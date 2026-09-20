# Don't Miss – AI-Powered Reminder Assistant

> Built for the **WeMakeDevs × AWS Bharat Builds Tour — First Commit 2026** Hackathon (Track: *Build It*).

---

## 1. Project Overview

**Don't Miss** is an AI-powered reminder and task management application that eliminates the hassle of configuring reminders through multi-step forms. 

Instead of opening forms, scrolling date pickers, adjusting time dials, and selecting dropdowns, users simply type or dictate what they need in natural language:

> *"Remind me tomorrow at 9 PM about my Amazon interview because I need to prepare interview questions."*

The built-in AI Assistant understands the intent, identifies the date and time, infers task priority, extracts context, and presents a structured draft for the user to review.

---

## 2. Problem

In conventional reminder apps, adding an actionable reminder requires high manual effort:
- Typing a title
- Picking a due date from a calendar dialog
- Selecting an exact hour and minute with a time picker
- Setting a priority level
- Configuring recurrence (daily, weekly, monthly)
- Adding extra notes or links

Because this process creates friction, users often postpone setting reminders or enter incomplete information, leading to forgotten tasks, missed interviews, and neglected deadlines.

---

## 3. Solution

**Don't Miss** solves this friction through an intelligent, natural-language reminder extraction pipeline coupled with a strict **human-in-the-loop** workflow:

1. **Natural-Language Input**: The user writes their reminder casually, just as they would tell a colleague or write in a notebook.
2. **Deterministic Information Extraction**: The backend AI agent extracts the title, calculates relative dates (`today`, `tomorrow`, `day after tomorrow`), determines exact 24-hour time, classifies priority (e.g., interviews and exams automatically receive `high` priority), and identifies recurrence and URLs.
3. **Structured Proposal Presentation**: Instead of blindly writing to the local database, the AI invokes a dedicated `create_reminder` tool that returns a structured reminder proposal.
4. **Human Confirmation**: The Flutter client renders a confirmation bottom sheet displaying the parsed title, scheduled time, priority badge, and notes. The user reviews the details, can make adjustments, and explicitly confirms before anything is saved or scheduled.

---

## 4. Features

- **Natural-Language AI Reminder Creation**: Input conversational prompts to extract all reminder metadata in one step.
- **Human-in-the-Loop Confirmation**: AI proposes; the user inspects and approves before reminders are saved.
- **Full Task Lifecycle Management**: Create, view, edit, complete, and delete reminders.
- **Search & Filtering**:
  - Live search across reminder titles and descriptions.
  - Quick filter chips: **All**, **Today**, **Overdue**, **High Priority**, and **Completed**.
- **Priority Classification**: Color-coded priority tiers (`High`, `Medium`, `Low`) with visual badges.
- **Recurrence Support**: Flexible recurring reminders with `Daily`, `Weekly`, and `Monthly` repeat intervals.
- **Exact Local Notifications**: Scheduled zoned notifications powered by `flutter_local_notifications` and `timezone` for Android exact alarms.
- **URL Attachment Support**: Save web links with reminders and launch them directly in an external browser.
- **Local Persistence**: Fast, reliable offline storage using `shared_preferences` with JSON serialization.
- **Cross-Platform Support**: Works on **Android** and **Web** (Chrome).

---

## 5. AI Agent Architecture

The AI subsystem follows an explicit tool-calling architecture where the model operates within strict boundaries:

```
┌─────────────────────────────────────────────────────────────┐
│                    Flutter Application                      │
│            (Android App / Flutter Web in Chrome)            │
└──────────────────────────────┬──────────────────────────────┘
                               │
                POST /agent/reminder (JSON)
                { "prompt", "current_date", "current_time" }
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend Server                    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Strands Agents SDK                        │
│               (ReminderAgent Orchestration)                 │
└───────────────┬─────────────────────────────▲───────────────┘
                │                             │
        Prompt + System Context       Tool Invocation
                │                             │
                ▼                             │
┌────────────────────────────────┐            │
│       Ollama Inference         │            │
│       Model: Qwen3 1.7B        │            │
└───────────────┬────────────────┘            │
                │                             │
                ▼                             │
┌─────────────────────────────────────────────┴───────────────┐
│               create_reminder Tool (@tool)                  │
│       Generates Structured Proposal (Does NOT Persist)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                  Returns Proposal JSON
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Flutter Human Confirmation Sheet                │
│       (User reviews, edits, and taps "Confirm")             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│       TaskProvider → TaskRepository (Local Storage)         │
│               NotificationService (Scheduled Alarm)         │
└─────────────────────────────────────────────────────────────┘
```

> **Architecture Note**: The repository does **not** use Amazon Bedrock, AWS Lambda, Amazon DynamoDB, Amazon S3, Amazon Cognito, or Amazon OpenSearch. All inference runs through Ollama and the open-source Strands Agents SDK.

---

## 6. AWS Usage

The application uses **Amazon Web Services (AWS)** for hosting its AI agent inference backend:

- **Amazon EC2**: The FastAPI and Ollama backend runs on an Amazon EC2 instance.
- **Amazon Linux 2023**: The EC2 virtual machine runs the official Amazon Linux 2023 AMI.
- **FastAPI Service**: Serves the REST API on port `8000` with CORS enabled for web clients.
- **Strands Agents SDK**: An open-source agent orchestration framework (developed by AWS) used inside Python to define the agent, system prompt, and function tools.
- **Ollama on EC2**: Hosts and executes the `qwen3:1.7b` quantized model locally on the EC2 instance CPU.
- **EC2 Instance Connect**: Used for secure, browser-based administrative terminal access to configure and monitor the instance.

---

## 7. Technology Stack

### Frontend (Mobile & Web)
| Technology | Role |
| :--- | :--- |
| **Flutter 3.x** | Cross-platform UI framework (Android & Web) |
| **Dart 3.x** | Core client language |
| **Provider** | Reactive state management (`ChangeNotifier`) |
| **shared_preferences** | Local device storage and persistence |
| **flutter_local_notifications** | Android exact alarm scheduling and notifications |
| **timezone** | Timezone-aware date calculations for notifications |
| **intl** | Date/time localization and formatting |
| **url_launcher** | External web link launching |

### Backend & AI
| Technology | Role |
| :--- | :--- |
| **FastAPI** | High-performance Python asynchronous API server |
| **Uvicorn** | ASGI web server implementation |
| **Strands Agents SDK** | Agent orchestration and tool calling |
| **Ollama** | Local LLM inference server |
| **Qwen3 1.7B** | Lightweight open LLM for structured tool calling |
| **Pydantic** | Request/response data validation |
| **pytest** | Backend test suite |

### Cloud Infrastructure
| Technology | Role |
| :--- | :--- |
| **Amazon EC2** | Compute instance hosting backend & Ollama |
| **Amazon Linux 2023** | Operating system for the cloud instance |
| **EC2 Instance Connect** | Secure administrative instance access |

---

## 8. Project Structure

```
Don't miss app/
├── agent/                               # Python AI Agent backend
│   ├── app.py                           # FastAPI application entry point & CORS
│   ├── reminder_agent.py                # Strands Agents SDK agent definition
│   ├── requirements.txt                 # Backend Python dependencies
│   ├── models/
│   │   └── reminder_schema.py           # Pydantic schemas (AgentRequest, AgentResponse, etc.)
│   ├── tools/
│   │   └── reminder_tools.py            # create_reminder tool and proposal tracker
│   └── tests/
│       └── test_agent.py                # Deterministic backend pytest tests
├── android/                             # Android native platform files & manifest
├── web/                                 # Flutter Web scaffolding (index.html, manifest.json)
├── lib/                                 # Flutter client application
│   ├── main.dart                        # App entry point, theme setup, service registration
│   ├── core/
│   │   ├── constants/                   # Colors and Material 3 theme configurations
│   │   └── utils/                       # Date formatting and overdue calculations
│   ├── models/
│   │   ├── ai_reminder_draft.dart       # Model for AI proposed reminder draft
│   │   ├── priority.dart                # Priority enum (low, medium, high)
│   │   ├── recurrence.dart              # Recurrence enum (none, daily, weekly, monthly)
│   │   └── task.dart                    # Immutable reminder task model
│   ├── providers/
│   │   └── task_provider.dart           # State management, filtering, search, and CRUD
│   ├── repositories/
│   │   └── task_repository.dart         # TaskRepository contract & SharedPreferences persistence
│   ├── services/
│   │   ├── agent_http_transport.dart    # Abstract HTTP transport & conditional import router
│   │   ├── agent_http_transport_html.dart # Browser-native HttpRequest for Flutter Web
│   │   ├── agent_http_transport_io.dart   # Native dart:io HttpClient for Android
│   │   ├── agent_http_transport_stub.dart # Platform fallback stub
│   │   ├── ai_agent_api_service.dart    # StrandsAgentApiService communicating with backend
│   │   ├── ai_reminder_service.dart     # AI service interface & LocalAiReminderService fallback
│   │   ├── notification_service.dart    # Local alarm scheduling & permission handling
│   │   ├── storage_service.dart         # Storage abstraction
│   │   └── url_launcher_service.dart    # External browser URL launcher
│   ├── screens/
│   │   ├── add_edit_task_screen.dart    # Manual reminder creation & editing form
│   │   └── home_screen.dart             # Main dashboard, reminder list, and filters
│   └── widgets/
│       ├── ai_confirmation_sheet.dart   # Human confirmation bottom sheet for AI drafts
│       ├── ai_reminder_sheet.dart       # Natural language input dialog with quick prompts
│       ├── priority_badge.dart          # Visual priority indicator chip
│       └── task_card.dart               # Interactive reminder card with swipe actions
└── test/                                # Flutter unit and widget tests
    ├── ai_agent_api_service_test.dart   # API client and transport tests
    ├── ai_reminder_test.dart            # Local fallback parser & confirmation widget tests
    ├── task_provider_test.dart          # Provider state management tests
    └── widget_test.dart                 # Smoke tests
```

---

## 9. Running the Project

### Prerequisites
- **Flutter SDK** (version $\ge$ 3.10)
- **Python** (version $\ge$ 3.10)
- **Ollama** installed with the `qwen3:1.7b` model pulled:
  ```bash
  ollama pull qwen3:1.7b
  ```

---

### Step 1: Start the AI Agent Backend

1. Navigate to the `agent` directory:
   ```bash
   cd agent
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn agent.app:app --host 0.0.0.0 --port 8000
   ```
5. Verify health:
   ```bash
   curl http://127.0.0.1:8000/health
   ```
   *Expected response:*
   ```json
   {
     "status": "healthy",
     "sdk": "strands-agents",
     "model_provider": "ollama",
     "model": "qwen3:1.7b",
     "host": "http://localhost:11434"
   }
   ```

---

### Step 2: Run the Flutter Client

1. From the repository root, install Flutter packages:
   ```bash
   flutter pub get
   ```

2. Run the test suite:
   ```bash
   flutter test test/ai_agent_api_service_test.dart test/ai_reminder_test.dart
   ```

3. **Run on Android Emulator / Physical Device**:
   ```bash
   # When using Android emulator and local backend (defaults to 10.0.2.2:8000):
   flutter run

   # Or when pointing to an EC2 instance:
   flutter run --dart-define=AGENT_BASE_URL=http://<EC2_IP>:8000
   ```

4. **Run on Flutter Web (Chrome)**:
   ```bash
   # When pointing to an EC2 instance:
   flutter run -d chrome --dart-define=AGENT_BASE_URL=http://<EC2_IP>:8000
   ```

---

## 10. Web AI Transport

Flutter compiles differently for native operating systems versus browser environments. The standard `dart:io` library (which provides `HttpClient`) is not supported in web browsers because browsers enforce sandbox security and cannot open raw TCP sockets.

To support both **Android** and **Flutter Web** without adding external third-party HTTP dependencies, the project uses **Dart conditional imports**:

- [`lib/services/agent_http_transport.dart`](file:///c:/Users/sarvesh/OneDrive/Desktop/Don't miss app/lib/services/agent_http_transport.dart): Defines the abstract `AgentHttpTransport` interface and routes imports at compile time.
- [`lib/services/agent_http_transport_io.dart`](file:///c:/Users/sarvesh/OneDrive/Desktop/Don't miss app/lib/services/agent_http_transport_io.dart): Used when `dart.library.io` is present (Android, Windows, macOS, Linux). Executes requests using `dart:io`'s `HttpClient`.
- [`lib/services/agent_http_transport_html.dart`](file:///c:/Users/sarvesh/OneDrive/Desktop/Don't miss app/lib/services/agent_http_transport_html.dart): Used when `dart.library.html` is present (Flutter Web / Chrome). Executes requests using browser-native `HttpRequest`.
- [`lib/services/agent_http_transport_stub.dart`](file:///c:/Users/sarvesh/OneDrive/Desktop/Don't miss app/lib/services/agent_http_transport_stub.dart): Fallback stub throwing `UnsupportedError` on unsupported platforms.

This keeps [`lib/services/ai_agent_api_service.dart`](file:///c:/Users/sarvesh/OneDrive/Desktop/Don't miss app/lib/services/ai_agent_api_service.dart) completely free of direct `dart:io` imports and guarantees zero runtime platform exceptions (`Platform._version`) on the web.

---

## 11. Safety & Human-in-the-Loop

AI agents should never make irreversible state modifications without explicit user approval. 

**Don't Miss** enforces safety through design:
1. **Separation of Proposal and Storage**: The `create_reminder` tool strictly produces an in-memory draft (`status: "PROPOSED"`, `requires_confirmation: true`). It does not write to disk or database.
2. **Interactive Confirmation Sheet**: The user is presented with the proposed title, calculated date, exact time, and assigned priority.
3. **Full User Editability**: The user can modify any field before confirming or open the full manual form pre-filled with the AI draft.
4. **Offline Fallback Guard**: If the AI backend is unreachable, the app automatically falls back to `LocalAiReminderService` (rule-based extraction), ensuring the user is never blocked from creating reminders.

---

## 12. Hackathon Details

- **Event**: WeMakeDevs × AWS Bharat Builds Tour
- **Hackathon**: First Commit 2026
- **Track**: Build It

---

## 13. Demo

Watch the project walk-through and live demonstration:

- [Demo Video](https://youtu.be/FXXYuxEAF8I)

---

## 14. Future Improvements

- **Enhanced Temporal Understanding**: Support complex relative dates like *"first Friday of next month"* or *"in two and a half hours"*.
- **Location-Based Reminders**: Trigger notifications when arriving at or leaving specific geographical coordinates.
- **Cloud Synchronization**: Optional multi-device sync with cloud data persistence.
- **User Authentication**: Secure multi-user login and account profiles.
- **Model Selection Flexibility**: Configurable model provider endpoints (e.g., larger reasoning models when higher accuracy is desired).

---

## 15. License

No explicit license is currently provided in this repository. All rights reserved by the author for the WeMakeDevs × AWS First Commit 2026 submission.
