; ==============================================================================
; برنامج التثبيت الرسمي لتطبيق: Universal Video Downloader Pro
; إعداد وتطوير: المهندس مجد ياسر الأعرج (Eng. Majd Alaaraj)
; خبير ذكاء اصطناعي ومهندس حواسيب - سورية، اللاذقية (+963988008243)
; الإصدار: 1.0
; ==============================================================================

#define MyAppName "Universal Video Downloader Pro"
#define MyAppVersion "1.0"
#define MyAppPublisher "Eng. Majd Yasser Alaaraj"
#define MyAppContact "+963988008243"
#define MyAppExeName "UniversalDownloader.exe"
#define MyAppIcon "app_icon.ico"

[Setup]
; الهوية الرقمية الفريدة للبرنامج
AppId={{E58C3A41-8B39-44F7-9C1D-8F2B5915D71C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL="tel:{#MyAppContact}"
AppSupportPhone={#MyAppContact}
AppComments="تطوير وبرمجة المهندس مجد ياسر الأعرج - خبير ذكاء اصطناعي ومهندس حواسيب"

; مسارات التثبيت وإعدادات الحزمة
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=.
OutputBaseFilename=VideoDownloader_Setup_v1.0
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\{#MyAppIcon}

; الضغط ونمط المعالج
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; الملف التنفيذي الأساسي
Source: "{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; أدوات المعالجة المرئية والصوتية (FFmpeg)
Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ffprobe.exe"; DestDir: "{app}"; Flags: ignoreversion

; موارد الواجهة
Source: "{#MyAppIcon}"; DestDir: "{app}"; Flags: ignoreversion
Source: "developer.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; اختصارات قائمة Start وسطح المكتب مع الأيقونة المخصصة
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcon}"
Name: "{group}\إلغاء التثبيت"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcon}"; Tasks: desktopicon

[Run]
; تشغيل البرنامج تلقائياً بعد اكتمال التنصيب
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent