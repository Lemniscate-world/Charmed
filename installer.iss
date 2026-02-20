; Inno Setup Script for Charmed
; This script creates a Windows installer with the following features:
; - Start Menu shortcuts
; - Desktop shortcut (optional)
; - Auto-start option (run on Windows startup)
; - Uninstaller
; - File associations (future use)

#define MyAppName "Charmed"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Charmed Team"
#define MyAppURL "https://github.com/yourusername/charmed"
#define MyAppExeName "Charmed.exe"
#define MyAppAssocName "Charmed Alarm File"
#define MyAppAssocExt ".alarm"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; Basic application information
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Default installation directory
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; Disable dir exists warning
DisableDirPage=auto
DisableProgramGroupPage=auto

; Output settings
OutputDir=Output
OutputBaseFilename=CharmedSetup-{#MyAppVersion}

; Compression settings
Compression=lzma2/max
SolidCompression=yes

; Modern UI
WizardStyle=modern

; Privileges - require admin to install in Program Files
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Architecture
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Installer icon and images
SetupIconFile=Logo First Draft.png
UninstallDisplayIcon={app}\{#MyAppExeName}

; License and info files
LicenseFile=LICENSE
InfoBeforeFile=README.md

; Code signing placeholder - uncomment and configure when certificate is available
; SignTool=mysigntool
; SignedUninstaller=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "autostart"; Description: "Run {#MyAppName} automatically when Windows starts"; GroupDescription: "Startup Options:"; Flags: unchecked

[Files]
; Main executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Additional files (README, LICENSE, etc.)
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut (if user selected)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick Launch shortcut (if user selected, for older Windows)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; Auto-start registry entry (if user selected)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletevalue; Tasks: autostart

; Application settings registry key
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; Flags: uninsdeletekeyifempty
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}\Settings"; Flags: uninsdeletekey

; File association for .alarm files (future use)
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".alarm"; ValueData: ""

[Run]
; Option to launch the application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up any files created by the application
Type: filesandordirs; Name: "{app}\*.log"
Type: filesandordirs; Name: "{app}\.cache"
Type: filesandordirs; Name: "{app}\.cache-*"

[Code]
// Custom Pascal Script code for advanced installer logic

// Check if the application is currently running
function IsAppRunning(): Boolean;
var
  FWMIService: Variant;
  FSWbemLocator: Variant;
  FWbemObjectSet: Variant;
begin
  Result := false;
  try
    FSWbemLocator := CreateOleObject('WbemScripting.SWbemLocator');
    FWMIService := FSWbemLocator.ConnectServer('', 'root\CIMV2', '', '');
    FWbemObjectSet := FWMIService.ExecQuery('SELECT * FROM Win32_Process Where Name="' + '{#MyAppExeName}' + '"');
    Result := (FWbemObjectSet.Count > 0);
  except
  end;
end;

// Check before installation
function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check if app is running
  if IsAppRunning() then
  begin
    if MsgBox('{#MyAppName} is currently running. Please close it before continuing.' + #13#10 + #13#10 + 
              'Do you want to continue anyway?', 
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;

// Check before uninstall
function InitializeUninstall(): Boolean;
begin
  Result := True;
  
  // Check if app is running
  if IsAppRunning() then
  begin
    if MsgBox('{#MyAppName} is currently running. It must be closed before uninstalling.' + #13#10 + #13#10 + 
              'Do you want to continue anyway?', 
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;

// Custom page for additional options (example)
var
  OptionsPage: TInputOptionWizardPage;

procedure InitializeWizard();
begin
  // Create custom options page
  OptionsPage := CreateInputOptionPage(wpSelectTasks,
    'Additional Options', 'Select additional configuration options',
    'You can customize how {#MyAppName} behaves on your system.',
    False, False);
  
  // Add option to create .env file for Spotify credentials
  OptionsPage.Add('Create configuration file for Spotify API credentials (recommended)');
  OptionsPage.Values[0] := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvFilePath: String;
  EnvContent: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Create .env file if user selected the option
    if OptionsPage.Values[0] then
    begin
      EnvFilePath := ExpandConstant('{app}\.env');
      EnvContent := '# Spotify API Credentials' + #13#10 +
                    '# Get your credentials from: https://developer.spotify.com/dashboard' + #13#10 +
                    '#SPOTIPY_CLIENT_ID=your_client_id_here' + #13#10 +
                    '#SPOTIPY_CLIENT_SECRET=your_client_secret_here' + #13#10 +
                    '#SPOTIPY_REDIRECT_URI=http://localhost:8888/callback' + #13#10;
      SaveStringToFile(EnvFilePath, EnvContent, False);
    end;
  end;
end;
