;=====================================================
; INSTALADOR OFICIAL SIGAFI v1.0
;=====================================================

[Setup]
AppName=SIGAFI
AppVersion=1.0
AppPublisher=Instituto Superior Especializado de Estudios Penitenciarios
AppCopyright=ISEEPENC
DefaultDirName={autopf}\SIGAFI
DefaultGroupName=SIGAFI
OutputDir=Instalador
OutputBaseFilename=SIGAFI_v1.0_Instalador
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=logo.ico

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el Escritorio"; GroupDescription: "Opciones adicionales:"

[Files]
Source: "dist\SIGAFI.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SIGAFI"; Filename: "{app}\SIGAFI.exe"

Name: "{autodesktop}\SIGAFI"; Filename: "{app}\SIGAFI.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SIGAFI.exe"; Description: "Ejecutar SIGAFI"; Flags: nowait postinstall skipifsilent