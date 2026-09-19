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

; UIDetect installer icon
; Make sure UIDetect.ico exists inside the installer folder.
SetupIconFile=UIDetect.ico


[Files]

; ==========================================================
; Include UIDetect Runtime Files
; ==========================================================

Source: "..\*"; \
    DestDir: "{app}"; \
    Flags: recursesubdirs createallsubdirs ignoreversion; \
    Excludes: "installer\UIDetect_Setup.exe;installer\*.tmp;installer\UIDetect_Setup.iss;installer\UIDetect.ico;.env;.git\*;.gitignore;__pycache__\*;backend\logs\*;backend_startup.log;UIDetect_Launcher.c;unins000.exe;unins000.dat"


; ==========================================================
; UIDetect Shortcut Icon
; ==========================================================

Source: "UIDetect.ico"; \
    DestDir: "{app}"; \
    Flags: ignoreversion


[Icons]

; ==========================================================
; Start Menu Shortcut
; ==========================================================

Name: "{group}\UIDetect"; \
    Filename: "{app}\UIDetect.exe"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\UIDetect.ico"


; ==========================================================
; Desktop Shortcut
; ==========================================================

Name: "{autodesktop}\UIDetect"; \
    Filename: "{app}\UIDetect.exe"; \
    WorkingDir: "{app}"; \
    IconFilename: "{app}\UIDetect.ico"


[Run]

; ==========================================================
; Start UIDetect after installation
; ==========================================================

Filename: "{app}\UIDetect.exe"; \
    WorkingDir: "{app}"; \
    Flags: nowait postinstall unchecked skipifsilent; \
    Check: ShouldLaunchUIDetect


[Code]

function GetTickCount64: Int64;
external 'GetTickCount64@kernel32.dll stdcall';

var
    InstructionPage: TWizardPage;
    InstructionLabel: TNewMemo;

    InstallProgressPage: TOutputProgressWizardPage;

    InstallFinished: Boolean;
    InstallError: Boolean;
    
    ProgressLabel: TNewStaticText;
    ElapsedLabel: TNewStaticText;

    InstallStartTime: Int64;  
    
    CancelButton: TNewButton;
    CancelRequested: Boolean;
    BackendProcessID: Integer;  
    
    
function ShouldLaunchUIDetect: Boolean;
begin

    Result :=
        not CancelRequested;

end;


{============================================================}
{ CREATE INSTRUCTION PAGE                                    }
{============================================================}

procedure CreateInstructionPage;
begin

    InstructionPage :=
        CreateCustomPage(
            wpSelectDir,
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
        'UIDetect uses a local unpacked browser extension.' + #13#10#13#10 +

        'After installation is complete:' + #13#10 +
        '1. Launch UIDetect using the option on the Finish page.' + #13#10 +
        '2. In the UIDetect Launcher, click "Open Chrome".' + #13#10 +
        '3. The Chrome Extensions page will open.' + #13#10 +
        '4. Turn ON "Developer mode".' + #13#10 +
        '5. Click "Load unpacked".' + #13#10 +
        '6. Select the main UIDetect installation folder.' + #13#10#13#10 +

        'IMPORTANT:' + #13#10 +
        'Choose the main UIDetect installation folder.' + #13#10 +
        'Do not select any of its subfolders.' + #13#10#13#10 +

        'After loading the extension:' + #13#10 +
        '- Confirm that UIDetect appears in Chrome.' + #13#10 +
        '- Keep the UIDetect Launcher running while using the extension.' + #13#10 +
        '- UIDetect is ready to perform website security assessments.' + #13#10#13#10 +

        'For complete setup instructions, scanning workflow, features and troubleshooting, refer to the UIDetect documentation on GitHub.' + #13#10 +
        'Open the UIDetect GitHub repository to access the latest user manual and documentation.';

end;


procedure CancelInstallClick(Sender: TObject);
var
    ResultCode: Integer;
begin

    if CancelRequested then
        Exit;

    if MsgBox(
        'Are you sure you want to cancel the UIDetect installation?' + #13#10#13#10 +
        'The installation process will be stopped.',
        mbConfirmation,
        MB_YESNO
    ) <> IDYES then
        Exit;

    CancelRequested := True;

    CancelButton.Enabled := False;
    CancelButton.Caption := 'Cancelling...';

    InstallProgressPage.SetText(
        'Cancelling UIDetect installation...',
        'Stopping the installation process...'
    );

    WizardForm.Update;

    if BackendProcessID <> 0 then
    begin

        Exec(
            ExpandConstant('{sys}\taskkill.exe'),
            '/PID ' +
            IntToStr(BackendProcessID) +
            ' /T /F',
            '',
            SW_HIDE,
            ewWaitUntilTerminated,
            ResultCode
        );

        BackendProcessID := 0;

    end;

end;


{============================================================}
{ CREATE INSTALLATION PROGRESS PAGE                          }
{============================================================}

procedure CreateInstallProgressPage;
begin

    InstallProgressPage :=
        CreateOutputProgressPage(
            'Installing UIDetect',
            'Installing required components...'
        );


    {--------------------------------------------------------}
    { Installation percentage                                }
    {--------------------------------------------------------}

    ProgressLabel :=
        TNewStaticText.Create(InstallProgressPage);

    ProgressLabel.Parent :=
        InstallProgressPage.Surface;

    ProgressLabel.Left :=
        ScaleX(20);

    ProgressLabel.Top :=
        ScaleY(125);

    ProgressLabel.Width :=
        InstallProgressPage.SurfaceWidth - ScaleX(40);

    ProgressLabel.Height :=
        ScaleY(20);

    ProgressLabel.Caption :=
        'Progress: 0%';




    {--------------------------------------------------------}
    { Elapsed time                                            }
    {--------------------------------------------------------}

    ElapsedLabel :=
        TNewStaticText.Create(InstallProgressPage);

    ElapsedLabel.Parent :=
        InstallProgressPage.Surface;

    ElapsedLabel.Left :=
        ScaleX(20);

    ElapsedLabel.Top :=
        ScaleY(150);

    ElapsedLabel.Width :=
        InstallProgressPage.SurfaceWidth - ScaleX(40);

    ElapsedLabel.Height :=
        ScaleY(20);

    ElapsedLabel.Caption :=
        'Elapsed time: 00:00:00';

    {--------------------------------------------------------}
    { Cancel installation button                             }
    {--------------------------------------------------------}

    CancelButton :=
        TNewButton.Create(InstallProgressPage);

    CancelButton.Parent :=
        InstallProgressPage.Surface;

    CancelButton.Left :=
        InstallProgressPage.SurfaceWidth - ScaleX(120);

    CancelButton.Top :=
        ScaleY(205);

    CancelButton.Width :=
        ScaleX(100);

    CancelButton.Height :=
        ScaleY(25);

    CancelButton.Caption :=
        'Cancel Installation';

    CancelButton.OnClick :=
        @CancelInstallClick;

end;


{============================================================}
{ INITIALIZE INSTALLER                                       }
{============================================================}

procedure InitializeWizard;
begin

    InstallFinished := False;
    InstallError := False;

    CancelRequested := False;
    BackendProcessID := 0;

    CreateInstructionPage;
    CreateInstallProgressPage;

end;


{============================================================}
{ GET STATUS FILE                                            }
{============================================================}

function GetStatusFile: String;
begin

    Result :=
        AddBackslash(GetEnv('TEMP')) +
        'UIDetectInstaller\install_status.txt';

end;


{============================================================}
{ READ INSTALLATION STATUS                                   }
{============================================================}

function ReadInstallStatus(
    var ProgressValue: Integer;
    var StatusText: String
): Boolean;
var
    StatusFile: String;
    Lines: TArrayOfString;
    Line: String;
    SeparatorPosition: Integer;
    NumberText: String;
begin

    Result := False;

    ProgressValue := 0;

    StatusText :=
        'Waiting for installation status...';

    StatusFile :=
        GetStatusFile;

    if not FileExists(StatusFile) then
        Exit;

    try

        if not LoadStringsFromFile(
            StatusFile,
            Lines
        ) then
            Exit;

    except

        Exit;

    end;

    if GetArrayLength(Lines) = 0 then
        Exit;

    Line :=
        Lines[
            GetArrayLength(Lines) - 1
        ];

    SeparatorPosition :=
        Pos('|', Line);

    if SeparatorPosition <= 0 then
        Exit;

    NumberText :=
        Copy(
            Line,
            1,
            SeparatorPosition - 1
        );

    StatusText :=
        Copy(
            Line,
            SeparatorPosition + 1,
            Length(Line)
        );

    ProgressValue :=
        StrToIntDef(
            NumberText,
            0
        );

    Result := True;

end;


{============================================================}
{ FORMAT TIME                                                }
{============================================================}

function TwoDigit(
    Value: Cardinal
): String;
begin

    if Value < 10 then
        Result := '0' + IntToStr(Value)
    else
        Result := IntToStr(Value);

end;


function FormatElapsedTime(
    Seconds: Cardinal
): String;
var
    Hours: Cardinal;
    Minutes: Cardinal;
    RemainingSeconds: Cardinal;
begin

    Hours :=
        Seconds div 3600;

    Minutes :=
        (Seconds mod 3600) div 60;

    RemainingSeconds :=
        Seconds mod 60;

    Result :=
        TwoDigit(Hours) +
        ':' +
        TwoDigit(Minutes) +
        ':' +
        TwoDigit(RemainingSeconds);

end;


{============================================================}
{ UPDATE INSTALLATION TIME INFORMATION                       }
{============================================================}

procedure UpdateInstallationTime(
    ProgressValue: Integer
);
var
    ElapsedSeconds: Cardinal;
begin

    {--------------------------------------------------------}
    { Calculate actual elapsed time                          }
    {--------------------------------------------------------}

    ElapsedSeconds :=
        Cardinal(
            (GetTickCount64 - InstallStartTime) div 1000
        );


    {--------------------------------------------------------}
    { Update elapsed time                                    }
    {--------------------------------------------------------}

    ElapsedLabel.Caption :=
        'Elapsed time: ' +
        FormatElapsedTime(
            ElapsedSeconds
        );


    {--------------------------------------------------------}
    { Update progress percentage                             }
    {--------------------------------------------------------}

    ProgressLabel.Caption :=
        'Progress: ' +
        IntToStr(ProgressValue) +
        '%';

end;

{============================================================}
{ START BACKEND INSTALLATION - DIAGNOSTIC VERSION            }
{============================================================}

function StartBackendInstallation: Boolean;
var
    ResultCode: Integer;
    BatFile: String;
    Params: String;
    DebugFile: String;
begin

    Result := False;

    BatFile :=
        ExpandConstant(
            '{app}\Install_UIDetect.bat'
        );

    DebugFile :=
        ExpandConstant(
            '{tmp}\UIDetectInstaller\frontend_launch_test.txt'
        );


    {--------------------------------------------------------}
    { Check BAT exists                                       }
    {--------------------------------------------------------}

    if not FileExists(BatFile) then
    begin

        Log('ERROR: BAT FILE NOT FOUND.');
        Log('BAT FILE: ' + BatFile);

        MsgBox(
            'Install_UIDetect.bat was not found:' + #13#10#13#10 +
            BatFile,
            mbError,
            MB_OK
        );

        Exit;

    end;


    {--------------------------------------------------------}
    { Create a diagnostic file BEFORE launching CMD          }
    {--------------------------------------------------------}

    ForceDirectories(
        ExpandConstant('{tmp}\UIDetectInstaller')
    );

    SaveStringToFile(
        DebugFile,
        'Inno reached StartBackendInstallation.' + #13#10 +
        'BAT=' + BatFile + #13#10 +
        'TIME=' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', '-', ':') + #13#10,
        False
    );


    {--------------------------------------------------------}
    { IMPORTANT                                              }
    { Use the standard CMD /C quoted-BAT pattern.           }
    { Do NOT use CALL for this test.                        }
    {--------------------------------------------------------}

    Params :=
        '/D /S /C ""' +
        BatFile +
        '" /INSTALLER"';


    Log('Starting backend using standard CMD /C pattern.');
    Log('BAT FILE: ' + BatFile);
    Log('CMD FILE: ' + ExpandConstant('{sys}\cmd.exe'));
    Log('CMD PARAMETERS: ' + Params);


    {--------------------------------------------------------}
    { Launch asynchronously                                 }
    {--------------------------------------------------------}

    if Exec(
        ExpandConstant('{sys}\cmd.exe'),
        Params,
        ExpandConstant('{app}'),
        SW_HIDE,
        ewNoWait,
        ResultCode
    ) then
    begin

        BackendProcessID := ResultCode;

        Log(
            'CMD PROCESS CREATED SUCCESSFULLY.'
        );

        Log(
            'CMD PROCESS ID: ' +
            IntToStr(BackendProcessID)
        );

        SaveStringToFile(
            DebugFile,
            'CMD process created successfully.' + #13#10 +
            'Process ID=' +
            IntToStr(BackendProcessID) + #13#10 +
            'Parameters=' + Params + #13#10 +
            'TIME=' +
            GetDateTimeString(
                'yyyy-mm-dd hh:nn:ss',
                '-',
                ':'
            ) + #13#10,
            True
        );

        Result := True;

    end
    else
    begin

        Log('ERROR: CMD PROCESS COULD NOT BE CREATED.');

        SaveStringToFile(
            DebugFile,
            'ERROR: CMD process could NOT be created.' + #13#10 +
            'TIME=' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', '-', ':') + #13#10,
            True
        );

        MsgBox(
            'Failed to start UIDetect backend installation.' + #13#10#13#10 +
            'BAT:' + #13#10 +
            BatFile,
            mbError,
            MB_OK
        );

    end;

end;


{============================================================}
{ RUN BACKEND INSTALLATION                                   }
{============================================================}

procedure RunBackendInstallation;
var
    ProgressValue: Integer;
    StatusText: String;

    LastProgressValue: Integer;
    LastStatusText: String;

    StatusFile: String;

    StatusFound: Boolean;
begin

    InstallFinished := False;
    InstallError := False;

    CancelRequested := False;
    BackendProcessID := 0;

    LastProgressValue := -1;
    LastStatusText := '';

    StatusFile :=
        GetStatusFile;


    {--------------------------------------------------------}
    { Remove old status file before starting a new install.  }
    {--------------------------------------------------------}

    DeleteFile(StatusFile);


    {--------------------------------------------------------}
    { Show frontend progress page.                           }
    {--------------------------------------------------------}

    InstallProgressPage.Show;

    InstallProgressPage.SetProgress(
        0,
        100
    );

    InstallProgressPage.SetText(
        'Starting UIDetect backend installation...',
        'Starting Install_UIDetect.bat...'
    );
    
    InstallStartTime :=
      GetTickCount64;

    UpdateInstallationTime(0);
  
    { Force the installer window to repaint. } 
    
    WizardForm.Update;

    {--------------------------------------------------------}
    { Start BAT asynchronously.                              }
    {--------------------------------------------------------}

    if not StartBackendInstallation then
    begin

        InstallError := True;

        InstallProgressPage.SetText(
            'Unable to start backend installation.',
            'Install_UIDetect.bat could not be started.'
        );

        Sleep(1000);

        InstallProgressPage.Hide;

        Exit;

    end;


    {--------------------------------------------------------}
    { Frontend now monitors backend status file.             }
    {--------------------------------------------------------}

    InstallProgressPage.SetText(
        'UIDetect backend installation started.',
        'Waiting for installation progress...'
    );

    WizardForm.Update;


    {--------------------------------------------------------}
    { POLLING LOOP                                            }
    {--------------------------------------------------------}

    while True do
    begin

        if CancelRequested then
            Break;

        StatusFound :=
            ReadInstallStatus(
                ProgressValue,
                StatusText
            );


        if StatusFound then
        begin

            {------------------------------------------------}
            { Update GUI when status changes.                }
            {------------------------------------------------}

            if (
                ProgressValue <> LastProgressValue
            ) or (
                StatusText <> LastStatusText
            ) then
            begin

                InstallProgressPage.SetProgress(
                    ProgressValue,
                    100
                );

                InstallProgressPage.SetText(
                    StatusText,
                    'UIDetect backend installation is running...'
                );

                LastProgressValue :=
                    ProgressValue;

                LastStatusText :=
                    StatusText;

                {--------------------------------------------}
                { IMPORTANT: force GUI repaint               }
                {--------------------------------------------}

                WizardForm.Update;

            end;


            {------------------------------------------------}
            { ERROR                                           }
            {------------------------------------------------}

            if Pos(
                'ERROR:',
                UpperCase(StatusText)
            ) > 0 then
            begin

                InstallError := True;

                WizardForm.Update;

                Break;

            end;


            {------------------------------------------------}
            { SUCCESS                                         }
            {------------------------------------------------}

            if (
                ProgressValue >= 100
            ) and (
                Pos(
                    'ERROR:',
                    UpperCase(StatusText)
                ) = 0
            ) then
            begin

                InstallFinished := True;

                WizardForm.Update;

                Break;

            end;

        end;


        {----------------------------------------------------}
        { IMPORTANT                                           }
        {----------------------------------------------------}
        { Allow the Inno Setup GUI to repaint between status  }
        { checks.                                             }
        {----------------------------------------------------}

        if StatusFound then
        begin

            UpdateInstallationTime(
                ProgressValue
            );

        end
        else if LastProgressValue >= 0 then
        begin

            UpdateInstallationTime(
                LastProgressValue
            );

        end
        else
        begin

            UpdateInstallationTime(
                0
            );

        end;

        WizardForm.Update;

        Sleep(500);
    end;
    
  {--------------------------------------------------------}
  { Installation cancelled                                }
  {--------------------------------------------------------}

  if CancelRequested then
  begin

      InstallError := True;

      InstallProgressPage.SetText(
          'UIDetect installation cancelled.',
          'The installation was cancelled by the user.'
      );

      WizardForm.Update;

      Sleep(1500);

  end
  else
  begin

      {----------------------------------------------------}
      { Installation finished / failed                     }
      {----------------------------------------------------}

      if InstallFinished then
      begin
      
          CancelButton.Enabled := False;

          InstallProgressPage.SetProgress(
              100,
              100
          );

          InstallProgressPage.SetText(
              'UIDetect installation completed.',
              'All required components have been installed successfully.'
          );

          WizardForm.Update;

          Sleep(1000);

      end
      else
      begin

          if InstallError then
          begin

              InstallProgressPage.SetText(
                  'UIDetect installation failed.',
                  'Please check the installation log for details.'
              );

              WizardForm.Update;

              Sleep(1500);

          end;

      end;

  end;


    {--------------------------------------------------------}
    { Hide custom progress page                              }
    {--------------------------------------------------------}

    InstallProgressPage.Hide;

end;


{============================================================}
{ AFTER FILE INSTALLATION                                    }
{============================================================}

procedure CurStepChanged(
    CurStep: TSetupStep
);
begin

    if CurStep = ssPostInstall then
    begin

        RunBackendInstallation;

    end;

end;