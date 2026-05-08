@echo off
:: ============================================================
:: build.bat
:: Script para gerar o executavel do Controle de tonner
:: Usa --onedir para abertura instantanea (sem extracao temp)
:: ============================================================

echo ============================================================
echo  BUILD - CONTROLE DE tonner v3.0
echo ============================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Instale o Python 3.10+ em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version

pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] pip nao encontrado!
    pause
    exit /b 1
)

echo.
echo [1/4] Instalando dependencias...
echo.

pip install customtkinter --quiet
pip install fpdf2 --quiet
pip install openpyxl --quiet
pip install Pillow --quiet
pip install pyinstaller --quiet

echo [OK] Dependencias instaladas
echo.
echo [2/4] Limpando builds anteriores...

if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del /q *.spec

echo [OK] Limpeza concluida
echo.
echo [3/4] Gerando executavel com PyInstaller...
echo.

if exist "icone.ico" (
    set ICON_ARG=--icon=icone.ico
    echo [OK] Icone encontrado: icone.ico
) else (
    set ICON_ARG=
    echo [AVISO] icone.ico nao encontrado
)

:: --onedir: gera uma pasta com o exe e dependencias
:: Abre instantaneamente pois nao precisa extrair nada
python -m PyInstaller ^
    --onedir ^
    --windowed ^
    --name="Controletonner" ^
    %ICON_ARG% ^
    --add-data="database.py;." ^
    --add-data="database_operations.py;." ^
    --add-data="models.py;." ^
    --add-data="relatorios.py;." ^
    --add-data="calendar_widget.py;." ^
    --add-data="compatibilidade.py;." ^
    --add-data="limpar_dados.py;." ^
    --hidden-import=customtkinter ^
    --hidden-import=fpdf ^
    --hidden-import=openpyxl ^
    --hidden-import=PIL ^
    --hidden-import=sqlite3 ^
    --hidden-import=calendar ^
    --hidden-import=json ^
    --hidden-import=ctypes ^
    --collect-all=customtkinter ^
    --noconfirm ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao gerar o executavel!
    pause
    exit /b 1
)

echo.
echo [OK] Pasta gerada: dist\Controletonner\

if exist "icone.ico" copy "icone.ico" "dist\Controletonner\" >nul

echo.
echo [4/4] Build concluido com sucesso!
echo.
echo ============================================================
echo  PASTA GERADA EM: dist\Controletonner\
echo  Proximo passo: Compile o instalador com o Inno Setup
echo  Arquivo: installer_setup.iss
echo ============================================================
echo.
pause
