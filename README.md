# Don't Miss - Modern Reminder Android App (MVP)

A clean, modern, and extensible Flutter reminder app designed for Android to capture, prioritize, and alert users of deadlines, tasks, and essential events so you never miss what matters most.

---

## 📱 Features (MVP)

- **Modern Material 3 Design:** Sleek cards, dark/light theme support, smooth typography, and priority color coding.
- **Task Management:** Create, view, edit, and delete reminders with swipe-to-delete support.
- **Task Completion:** Checkbox toggle with strike-through styling and auto-cancellation of scheduled alerts.
- **Detailed Fields:**
  - **Title:** Compulsory headline for the reminder.
  - **Description/Message:** Multiline note for extra context.
  - **Date & Time:** Date and Time pickers for exact scheduled deadlines.
  - **Priority:** Low (Green), Medium (Amber), High (Red) with icons and sorting weights.
  - **Optional URL:** Direct link launching in external browser via `url_launcher`.
  - **Notification ON/OFF:** Toggle to enable/disable alerts for individual tasks.
- **Local Persistence:** Zero-setup local persistence using `shared_preferences` with pure Dart JSON serialization, decoupled via `TaskRepository`.
- **Scheduled Local Notifications:** Powered by `flutter_local_notifications` and `timezone` for exact zoned alarms with Android 13+ permission support.

---

## 📂 Project Architecture & Structure

```
Don't Miss/
├── pubspec.yaml                        # Project metadata & dependencies
├── analysis_options.yaml               # Linter configuration
├── README.md                           # Documentation & build instructions
├── android/
│   └── app/
│       └── src/
│           └── main/
│               └── AndroidManifest.xml # Android permissions (notifications, exact alarm, boot)
└── lib/
    ├── main.dart                       # App entry point, initializes services & providers
    ├── core/
    │   ├── constants/
    │   │   ├── app_colors.dart         # Brand palette & priority colors
    │   │   └── app_theme.dart          # Light & Dark Material 3 theme configurations
    │   └── utils/
    │       └── date_time_utils.dart    # Human-readable date/time formatting & overdue logic
    ├── models/
    │   ├── priority.dart               # Priority enum (Low, Medium, High)
    │   └── task.dart                   # Immutable Task model with JSON serialization
    ├── services/
    │   ├── notification_service.dart   # Exact alarm scheduling & permission handling
    │   ├── storage_service.dart        # SharedPreferences persistence layer
    │   └── url_launcher_service.dart   # Safe external URL launcher
    ├── repositories/
    │   └── task_repository.dart        # TaskRepository contract & LocalTaskRepository
    ├── providers/
    │   └── task_provider.dart          # State management (ChangeNotifier), search & filter
    ├── widgets/
    │   ├── empty_state_view.dart       # Empty state illustration & message
    │   ├── priority_badge.dart         # Color-coded priority pill badge
    │   ├── task_card.dart              # Interactive reminder card with swipe actions
    │   └── task_stats_card.dart        # Dashboard banner summarizing tasks
    └── screens/
        ├── home_screen.dart            # Main dashboard with stats, search, & task list
        └── add_edit_task_screen.dart   # Full creation/edit form with pickers & switches
```

---

## 📦 Required Dependencies

All declared in `pubspec.yaml`:

| Package | Purpose |
| :--- | :--- |
| `provider: ^6.1.2` | Clean, boilerplate-free state management |
| `shared_preferences: ^2.2.2` | Fast, key-value local storage without codegen or native C build hurdles |
| `flutter_local_notifications: ^17.1.2` | Android alarm scheduling & local heads-up notifications |
| `timezone: ^0.9.3` | Time-zone database for exact `tz.TZDateTime` alarm schedules |
| `intl: ^0.19.0` | Date and time formatting (e.g. "18 September 2026", "9:00 PM") |
| `url_launcher: ^6.2.6` | Safely open web links in default Android browser |
| `uuid: ^4.3.3` | Generates robust unique IDs for tasks |

---

## 🛠️ What We Will Install Later to Build the Android APK

When you are ready to build and run the app, here is the exact checklist of what will be installed and configured on your computer:

### 1. Flutter SDK
- Download the official Flutter SDK from [flutter.dev](https://docs.flutter.dev/get-started/install/windows).
- Extract to a clean folder (e.g. `C:\src\flutter`).
- Add `C:\src\flutter\bin` to your Windows system `PATH` environment variable.

### 2. Android Studio & Android SDK
- Install **Android Studio** from [developer.android.com/studio](https://developer.android.com/studio).
- Open Android Studio $\rightarrow$ **SDK Manager** and install:
  - **Android SDK Platform** (API 34 or latest).
  - **Android SDK Command-line Tools (latest)**.
  - **Android SDK Build-Tools**.
- Configure `ANDROID_HOME` in Windows Environment Variables (pointing to `%LOCALAPPDATA%\Android\Sdk`).

### 3. Generate Android Build Wrappers & Run
Once Flutter is installed, open PowerShell in this directory (`c:\Users\sarvesh\OneDrive\Desktop\Don't Miss`) and run:

```powershell
# 1. Generate standard Android platform wrapper files (gradlew, build.gradle)
flutter create . --org com.example

# 2. Fetch all dependencies
flutter pub get

# 3. Verify toolchain readiness
flutter doctor

# 4. Run on a connected Android phone or emulator
flutter run

# 5. Or build a release APK directly
flutter build apk --release
```
The output APK will be generated at `build/app/outputs/flutter-apk/app-release.apk`.

---

## 🔮 Future Extension (TOMT Productivity Web App & MCP)

The architecture is deliberately organized to make future integrations painless:
- `TaskRepository` defines an abstract contract (`getAllTasks`, `saveAllTasks`).
- When ready to link **Don't Miss** with your **TOMT productivity web app** via Model Context Protocol (MCP) or a sync service, you will simply implement a `RemoteTaskRepository` or `McpTaskRepository` that adheres to `TaskRepository` without touching any UI screen, widget, or state manager.
