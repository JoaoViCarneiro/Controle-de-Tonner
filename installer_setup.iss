; ============================================================
; installer_setup.iss
; Instalador profissional - Controle de tonner v3.0
; Cliente: World Print
; Usa onedir para abertura instantanea
; ============================================================

#define AppName "Controle de tonner"
#define AppVersion "3.0"
#define AppPublisher "World Print"
#define AppExeName "Controletonner.exe"
#define AppId "{{B7F3A1C2-D4E5-4890-BCDE-FA2345678901}"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
AppCopyright=Copyright (C) 2025 {#AppPublisher}

DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes

MinVersion=6.1.7601

Compression=lzma2/ultra64
SolidCompression=yes
DiskSpanning=no

WizardStyle=modern
WizardSizePercent=120
WizardResizable=no

SetupIconFile=icone.ico

OutputDir=instalador_final
OutputBaseFilename=Controletonner_WorldPrint_v{#AppVersion}_Setup

PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=commandline

DisableReadyPage=yes
DisableDirPage=no
DisableProgramGroupPage=yes
ShowTasksTreeLines=yes

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[CustomMessages]
brazilianportuguese.WelcomeLabel1=Bem-vindo ao instalador do [name]
brazilianportuguese.WelcomeLabel2=Este assistente vai instalar o [name/ver] no seu computador.%n%nFornecido por World Print.%n%nClique em Instalar para continuar.
brazilianportuguese.FinishedHeadingLabel=Instalacao concluida!
brazilianportuguese.FinishedLabelNoIcons=O [name] foi instalado com sucesso no seu computador.
brazilianportuguese.FinishedLabel=O [name] foi instalado com sucesso.%nClique em Concluir para fechar este assistente.

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Area de Trabalho"; GroupDescription: "Atalhos adicionais:"; Flags: checkedonce

[Files]
; Todos os arquivos da pasta onedir gerada pelo PyInstaller
Source: "dist\Controletonner\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Icone separado para atalhos
Source: "icone.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Dirs]
; Cria a pasta db com permissao total para todos os usuarios (necessario para rede)
Name: "{app}\db"; Permissions: everyone-full

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\icone.ico"; Comment: "Controle de tonner - World Print"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\icone.ico"; Comment: "Controle de tonner - World Print"; Tasks: desktopicon
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Iniciar o Controle de tonner agora"; Flags: nowait postinstall skipifsilent unchecked

[UninstallDelete]
; Preserva a pasta db (dados) ao desinstalar
Type: dirifempty; Name: "{app}"

[Code]
function InitializeSetup(): Boolean;
var
  OldVersion: string;
  Msg: string;
begin
  Result := True;

  if RegQueryStringValue(HKLM,
    'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppId}_is1',
    'DisplayVersion', OldVersion) then
  begin
    Msg := 'O Controle de tonner versao ' + OldVersion + ' ja esta instalado.';
    Msg := Msg + #13#10 + #13#10;
    Msg := Msg + 'Deseja atualizar para a versao {#AppVersion}?';
    Msg := Msg + #13#10;
    Msg := Msg + 'Seus dados serao preservados.';
    if MsgBox(Msg, mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;

procedure InitializeWizard();
begin
  WizardForm.Caption := 'Controle de tonner v{#AppVersion} - World Print';
  WizardForm.NextButton.Caption := 'Instalar';
  WizardForm.BackButton.Visible := False;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpWelcome then
  begin
    WizardForm.NextButton.Caption := 'Instalar';
    WizardForm.BackButton.Visible := False;
  end;

  if CurPageID = wpInstalling then
    WizardForm.NextButton.Enabled := False;

  if CurPageID = wpFinished then
    WizardForm.NextButton.Caption := 'Concluir';
end;
