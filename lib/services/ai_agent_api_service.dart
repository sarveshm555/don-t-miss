import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import '../models/ai_reminder_draft.dart';
import '../models/priority.dart';
import '../models/recurrence.dart';
import 'ai_reminder_service.dart';

/// Service that delegates natural-language reminder parsing to the
/// local FastAPI Strands Agents SDK backend at `POST http://127.0.0.1:8000/agent/reminder`.
class StrandsAgentApiService implements AiReminderService {
  final String? baseUrl;
  final Duration timeout;
  final AiReminderService? fallbackService;
  final HttpClient Function()? clientFactory;

  const StrandsAgentApiService({
    this.baseUrl,
    this.timeout = const Duration(seconds: 180),
    this.fallbackService,
    this.clientFactory,
  });

  /// Base URL configured at build/run time via `--dart-define=AGENT_BASE_URL=...`.
  static const String environmentBaseUrl =
      String.fromEnvironment('AGENT_BASE_URL', defaultValue: '');

  /// Default API base URL: resolves from --dart-define=AGENT_BASE_URL if supplied,
  /// otherwise 10.0.2.2:8000 for Android emulator and 127.0.0.1:8000 for other platforms.
  static String get defaultBaseUrl {
    if (environmentBaseUrl.isNotEmpty) {
      return environmentBaseUrl;
    }
    if (!kIsWeb && Platform.isAndroid) {
      return 'http://10.0.2.2:8000';
    }
    return 'http://127.0.0.1:8000';
  }

  /// The active base URL resolving configured URL or platform default.
  String get effectiveBaseUrl => baseUrl ?? defaultBaseUrl;

  @override
  Future<AiReminderDraft> parsePrompt(
    String prompt, {
    DateTime? referenceTime,
  }) async {
    final cleanPrompt = prompt.trim();
    if (cleanPrompt.isEmpty) {
      throw const AiParsingException('Please enter a reminder request.');
    }

    final now = referenceTime ?? DateTime.now();
    final currentDate =
        '${now.year.toString().padLeft(4, '0')}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}';
    final currentTime =
        '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';

    final payload = {
      'prompt': cleanPrompt,
      'current_date': currentDate,
      'current_time': currentTime,
    };

    final uri = Uri.parse('$effectiveBaseUrl/agent/reminder');
    HttpClient? client;

    try {
      client = clientFactory != null ? clientFactory!() : HttpClient();
      client.connectionTimeout = const Duration(seconds: 15);

      final request = await client.postUrl(uri);
      request.headers.set('content-type', 'application/json');
      request.write(jsonEncode(payload));

      final response = await request.close().timeout(timeout);
      final responseBody = await response.transform(utf8.decoder).join();

      if (response.statusCode != 200) {
        throw AiParsingException(
          'AI Agent service returned status code ${response.statusCode}: $responseBody',
        );
      }

      final Map<String, dynamic> data =
          jsonDecode(responseBody) as Map<String, dynamic>;
      final success = data['success'] as bool? ?? false;

      if (!success) {
        final error = data['error'] as String? ??
            data['message'] as String? ??
            'AI Agent could not propose a reminder.';
        throw AiParsingException(error);
      }

      final proposal = data['proposal'] as Map<String, dynamic>?;
      if (proposal == null) {
        throw const AiParsingException('No reminder proposal received from AI Agent.');
      }

      final draftMap = proposal['draft'] as Map<String, dynamic>?;
      if (draftMap == null) {
        throw const AiParsingException('Proposal missing reminder draft data.');
      }

      final title = draftMap['title'] as String? ?? 'Untitled Reminder';
      final description = draftMap['description'] as String? ?? '';
      final dueDateStr = draftMap['dueDate'] as String?;
      DateTime dueDate;
      if (dueDateStr != null && dueDateStr.isNotEmpty) {
        dueDate = DateTime.tryParse(dueDateStr) ?? now;
      } else {
        dueDate = now;
      }
      final dueHour = draftMap['dueHour'] as int? ?? 9;
      final dueMinute = draftMap['dueMinute'] as int? ?? 0;
      final priority = Priority.fromString(draftMap['priority'] as String?);
      final recurrence = Recurrence.fromString(draftMap['recurrence'] as String?);
      final url = draftMap['url'] as String?;
      final reasoning = draftMap['reasoning'] as String? ??
          proposal['message'] as String? ??
          data['message'] as String?;
      final rawPrompt = proposal['raw_prompt'] as String? ?? cleanPrompt;

      return AiReminderDraft(
        title: title,
        description: description,
        dueDate: dueDate,
        dueHour: dueHour,
        dueMinute: dueMinute,
        priority: priority,
        recurrence: recurrence,
        url: url,
        reasoning: reasoning,
        rawPrompt: rawPrompt,
      );
    } on SocketException catch (e) {
      if (fallbackService != null) {
        debugPrint(
          'StrandsAgentApiService: Connection to $effectiveBaseUrl failed ($e). Delegating to fallback service.',
        );
        return fallbackService!.parsePrompt(prompt, referenceTime: referenceTime);
      }
      throw AiParsingException(
        'Could not connect to AI backend at $effectiveBaseUrl. Ensure the Strands agent service is running.',
      );
    } catch (e) {
      if (e is AiParsingException) {
        rethrow;
      }
      if (fallbackService != null && (e is HttpException || e is IOException)) {
        debugPrint(
          'StrandsAgentApiService: Network error ($e). Delegating to fallback service.',
        );
        return fallbackService!.parsePrompt(prompt, referenceTime: referenceTime);
      }
      throw AiParsingException('Error communicating with AI Agent: $e');
    } finally {
      client?.close();
    }
  }
}
