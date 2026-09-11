#define MyAppName "UIDetect"
#define MyAppVersion "1.0"
#define MyAppPublisher "UIDetect"

[Setup]
AppId={{UIDetect-Setup}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\UIDetect
DefaultGroupName=UIDetect

OutputDir=.
OutputBaseFilename=UIDetect_Setup

Compression=lzma
SolidCompression=yes

PrivilegesRequired=admin

ArchitecturesInstallIn64BitMode=x64compatible

DisableDirPage=no
DisableProgramGroupPage=no


[Files]

; ==========================================================
; Include Entire UIDetect Project
; ==========================================================

Source: "..\*"; \
    DestDir: "{app}"; \
    Flags: recursesubdirs createallsubdirs ignoreversion; \
    Excludes: "installer\*;.env;.git\*;__pycache__\*"


[Icons]

; ==========================================================
; Start Menu Shortcut
; ==========================================================

Name: "{group}\UIDetect"; \
    Filename: "{app}\Start_UIDetect.bat"; \
    WorkingDir: "{app}"


; ==========================================================
; Desktop Shortcut
; ==========================================================

Name: "{autodesktop}\UIDetect"; \
    Filename: "{app}\Start_UIDetect.bat"; \
    WorkingDir: "{app}"


[Run]

; ==========================================================
; Install UIDetect Python Dependencies
; ==========================================================

Filename: "{app}\Install_UIDetect.bat"; \
    Parameters: "/INSTALLER"; \
    WorkingDir: "{app}"; \
    Flags: waituntilterminated

Filename: "{app}\Start_UIDetect.bat"; \
    WorkingDir: "{app}"; \
    Flags: nowait skipifsilent


[Code]

var
  BrowserPage: TWizardPage;
  InstructionPage: TWizardPage;

  ChromeRadio: TNewRadioButton;
  EdgeRadio: TNewRadioButton;

  BrowserInfoLabel: TNewStaticText;
  InstructionLabel: TNewMemo;

  ChromeInstalled: Boolean;
  EdgeInstalled: Boolean;
  
  NextStepsPage: TWizardPage;
  NextStepsMemo: TNewMemo;


{============================================================}
{ FORWARD DECLARATIONS                                       }
{============================================================}

procedure OpenBrowserSetup; forward;
procedure OpenUIDetectFolder; forward;


{============================================================}
{ BROWSER DETECTION                                          }
{============================================================}

function GetChromePath(): String;
begin

  Result := '';

  { Standard Program Files location }

  if FileExists(
    ExpandConstant('{autopf}\Google\Chrome\Application\chrome.exe')
  ) then
  begin

    Result :=
      ExpandConstant(
        '{autopf}\Google\Chrome\Application\chrome.exe'
      );

  end

  { User-local installation }

  else
  if FileExists(
    ExpandConstant('{localappdata}\Google\Chrome\Application\chrome.exe')
  ) then
  begin

    Result :=
      ExpandConstant(
        '{localappdata}\Google\Chrome\Application\chrome.exe'
      );

  end;

end;


function GetEdgePath(): String;
begin

  Result := '';

  { Standard Program Files location }

  if FileExists(
    ExpandConstant('{autopf}\Microsoft\Edge\Application\msedge.exe')
  ) then
  begin

    Result :=
      ExpandConstant(
        '{autopf}\Microsoft\Edge\Application\msedge.exe'
      );

  end

  { Program Files (x86) location }

  else
  if FileExists(
    ExpandConstant('{autopf32}\Microsoft\Edge\Application\msedge.exe')
  ) then
  begin

    Result :=
      ExpandConstant(
        '{autopf32}\Microsoft\Edge\Application\msedge.exe'
      );

  end

  { User-local installation }

  else
  if FileExists(
    ExpandConstant('{localappdata}\Microsoft\Edge\Application\msedge.exe'
    )
  ) then
  begin

    Result :=
      ExpandConstant(
        '{localappdata}\Microsoft\Edge\Application\msedge.exe'
      );

  end;

end;


{============================================================}
{ CREATE BROWSER SELECTION PAGE                              }
{============================================================}

procedure CreateBrowserPage;
begin

  {----------------------------------------------------------}
  { IMPORTANT                                                }
  { Create this page BEFORE wpReady                          }
  {----------------------------------------------------------}

  BrowserPage :=
    CreateCustomPage(
      wpSelectDir,
      'UIDetect Browser Setup',
      'Select the browser where you want to load the UIDetect extension.'
    );


  {----------------------------------------------------------}
  { Information text                                         }
  {----------------------------------------------------------}

  BrowserInfoLabel :=
    TNewStaticText.Create(BrowserPage);

  BrowserInfoLabel.Parent :=
    BrowserPage.Surface;

  BrowserInfoLabel.Left :=
    ScaleX(20);

  BrowserInfoLabel.Top :=
    ScaleY(20);

  BrowserInfoLabel.Width :=
    BrowserPage.SurfaceWidth - ScaleX(40);

  BrowserInfoLabel.Height :=
    ScaleY(80);

  BrowserInfoLabel.AutoSize :=
    False;

  BrowserInfoLabel.Caption :=
    'UIDetect uses a local unpacked browser extension.' + #13#10 +
    'Chrome and Microsoft Edge require Developer Mode to load it.' + #13#10 +
    'Please select the browser you want to use.';


  {----------------------------------------------------------}
  { Chrome                                                   }
  {----------------------------------------------------------}

  ChromeRadio :=
    TNewRadioButton.Create(BrowserPage);

  ChromeRadio.Parent :=
    BrowserPage.Surface;

  ChromeRadio.Left :=
    ScaleX(30);

  ChromeRadio.Top :=
    ScaleY(115);

  ChromeRadio.Width :=
    ScaleX(350);

  ChromeRadio.Height :=
    ScaleY(25);

  ChromeRadio.Caption :=
    'Google Chrome';

  ChromeRadio.Enabled :=
    ChromeInstalled;

  ChromeRadio.Checked :=
    False;


  {----------------------------------------------------------}
  { Edge                                                     }
  {----------------------------------------------------------}

  EdgeRadio :=
    TNewRadioButton.Create(BrowserPage);

  EdgeRadio.Parent :=
    BrowserPage.Surface;

  EdgeRadio.Left :=
    ScaleX(30);

  EdgeRadio.Top :=
    ScaleY(155);

  EdgeRadio.Width :=
    ScaleX(350);

  EdgeRadio.Height :=
    ScaleY(25);

  EdgeRadio.Caption :=
    'Microsoft Edge';

  EdgeRadio.Enabled :=
    EdgeInstalled;

  EdgeRadio.Checked :=
    False;


  {----------------------------------------------------------}
  { Automatically select available browser                   }
  {----------------------------------------------------------}

  if ChromeInstalled then
  begin

    ChromeRadio.Checked :=
      True;

  end
  else
  if EdgeInstalled then
  begin

    EdgeRadio.Checked :=
      True;

  end;

end;


{============================================================}
{ CREATE INSTRUCTION PAGE                                    }
{============================================================}

procedure CreateInstructionPage;
begin

  InstructionPage :=
    CreateCustomPage(
      BrowserPage.ID,
      'UIDetect Extension Setup',
      'Follow the steps below after the installation is complete.'
    );


  InstructionLabel :=
    TNewMemo.Create(InstructionPage);

  InstructionLabel.Parent :=
    InstructionPage.Surface;

  InstructionLabel.Left :=
    ScaleX(20);

  InstructionLabel.Top :=
    ScaleY(15);

  InstructionLabel.Width :=
    InstructionPage.SurfaceWidth - ScaleX(40);

  InstructionLabel.Height :=
    InstructionPage.SurfaceHeight - ScaleY(30);

  InstructionLabel.ReadOnly :=
    True;

  InstructionLabel.ScrollBars :=
    ssVertical;

  InstructionLabel.WordWrap :=
    True;

  InstructionLabel.TabStop :=
    False;

  InstructionLabel.Text :=
    'UIDetect has been prepared for your browser.' + #13#10#13#10 +

    'After clicking Finish:' + #13#10 +
    '1. UIDetect installation will complete.' + #13#10 +
    '2. Your selected browser extension page will open.' + #13#10 +
    '3. Your UIDetect installation folder will also open.' + #13#10#13#10 +

    'In the browser:' + #13#10 +
    '4. Turn ON "Developer mode".' + #13#10 +
    '5. Click "Load unpacked".' + #13#10 +
    '6. Select the UIDetect installation folder that opens automatically.' + #13#10#13#10 +

    'IMPORTANT:' + #13#10 +
    'Select the main UIDetect folder.' + #13#10 +
    'Do NOT select backend, popup, scripts, content, or icons.' + #13#10#13#10 +

    'The selected folder must contain:' + #13#10 +
    'manifest.json' + #13#10 +
    'icons\icon16.png' + #13#10 +
    'icons\icon48.png' + #13#10 +
    'icons\icon128.png' + #13#10#13#10 +

    'Installation location:' + #13#10 +
    'The UIDetect installation folder will be opened automatically after installation.' + #13#10#13#10 +

    'After the extension appears in the browser, UIDetect is ready to use.';

end;


{============================================================}
{ INITIALIZE INSTALLER                                       }
{============================================================}

procedure InitializeWizard;
begin

  {----------------------------------------------------------}
  { Detect browsers                                         }
  {----------------------------------------------------------}

  ChromeInstalled :=
    GetChromePath() <> '';

  EdgeInstalled :=
    GetEdgePath() <> '';


  {----------------------------------------------------------}
  { Create custom pages BEFORE wpReady                       }
  {----------------------------------------------------------}

  CreateBrowserPage;

  CreateInstructionPage;
  
    NextStepsPage := CreateCustomPage(
    InstructionPage.ID,
    'Important Next Step',
    'Complete the UIDetect setup before using the extension'
  );

  NextStepsMemo := TNewMemo.Create(WizardForm);
  NextStepsMemo.Parent := NextStepsPage.Surface;
  NextStepsMemo.Left := 0;
  NextStepsMemo.Top := 0;
  NextStepsMemo.Width := NextStepsPage.SurfaceWidth;
  NextStepsMemo.Height := NextStepsPage.SurfaceHeight;
  NextStepsMemo.ReadOnly := True;
  NextStepsMemo.ScrollBars := ssVertical;
  NextStepsMemo.WordWrap := True;

    NextStepsMemo.Lines.Add(
    'IMPORTANT: UIDetect must be manually loaded into the browser before you can use the extension.'
  );

  NextStepsMemo.Lines.Add('');
  NextStepsMemo.Lines.Add(
    'When you click Finish, the browser extension page and UIDetect installation folder will open automatically.'
  );

  NextStepsMemo.Lines.Add('');
  NextStepsMemo.Lines.Add(
    'Then complete these steps:'
  );

  NextStepsMemo.Lines.Add('');

  NextStepsMemo.Lines.Add(
    '1. Turn ON "Developer mode" in the browser extension page.'
  );

  NextStepsMemo.Lines.Add(
    '2. Click "Load unpacked".'
  );

  NextStepsMemo.Lines.Add(
    '3. Select the installed UIDetect folder that opens automatically.'
  );

  NextStepsMemo.Lines.Add(
    '4. Confirm that the UIDetect extension appears in the browser.'
  );

  NextStepsMemo.Lines.Add('');

  NextStepsMemo.Lines.Add(
    'After loading the extension:'
  );

  NextStepsMemo.Lines.Add('');

  NextStepsMemo.Lines.Add(
    '• Start using UIDetect from the browser.'
  );

  NextStepsMemo.Lines.Add(
    '• Keep the UIDetect backend running while using the extension.'
  );

  NextStepsMemo.Lines.Add(
    '• Read "UIDetect User Manual.html" for the complete setup, scanning workflow, features and troubleshooting steps.'
  );

  NextStepsMemo.Lines.Add('');

  NextStepsMemo.Lines.Add(
    'IMPORTANT: Loading the unpacked extension is a required manual step. The installer does not automatically install the extension into Chrome or Microsoft Edge.'
  );

end;


{============================================================}
{ VALIDATE BROWSER SELECTION                                 }
{============================================================}

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  {----------------------------------------------------------}
  { Validate browser selection                               }
  {----------------------------------------------------------}

  if CurPageID = BrowserPage.ID then
  begin
    if (not ChromeRadio.Checked) and
       (not EdgeRadio.Checked) then
    begin

      MsgBox(
        'Please select Google Chrome or Microsoft Edge before continuing.',
        mbError,
        MB_OK
      );

      Result := False;
      Exit;

    end;
  end;


  {----------------------------------------------------------}
  { Open browser extension page and UIDetect folder          }
  { after the user clicks Finish                             }
  {----------------------------------------------------------}

  if CurPageID = wpFinished then
  begin
    OpenBrowserSetup;
    OpenUIDetectFolder;
  end;

end;


{============================================================}
{ OPEN SELECTED BROWSER                                      }
{============================================================}

procedure OpenBrowserSetup;
var
  BrowserPath: String;
  ResultCode: Integer;
begin

  BrowserPath :=
    '';


  {----------------------------------------------------------}
  { Chrome                                                   }
  {----------------------------------------------------------}

  if ChromeRadio.Checked then
  begin

    BrowserPath :=
      GetChromePath();

    if BrowserPath <> '' then
    begin

      Exec(
        BrowserPath,
        '--new-window "chrome://extensions/"',
        '',
        SW_SHOWNORMAL,
        ewNoWait,
        ResultCode
      );

    end;

  end;


  {----------------------------------------------------------}
  { Edge                                                     }
  {----------------------------------------------------------}

  if EdgeRadio.Checked then
  begin

    BrowserPath :=
      GetEdgePath();

    if BrowserPath <> '' then
    begin

      Exec(
        BrowserPath,
        '--new-window "edge://extensions/"',
        '',
        SW_SHOWNORMAL,
        ewNoWait,
        ResultCode
      );

    end;

  end;

end;


{============================================================}
{ OPEN UIDETECT INSTALLATION FOLDER                          }
{============================================================}

procedure OpenUIDetectFolder;
var
  ResultCode: Integer;
begin

  ShellExec(
    '',
    ExpandConstant('{app}'),
    '',
    '',
    SW_SHOWNORMAL,
    ewNoWait,
    ResultCode
  );

end;



