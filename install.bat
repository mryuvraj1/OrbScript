@echo off
echo Installing OrbScript...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.7 or later.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create installation directory
set INSTALL_DIR=%USERPROFILE%\orbscript
mkdir "%INSTALL_DIR%" 2>nul

REM Copy files
echo Copying files...
copy lexer.py "%INSTALL_DIR%\" >nul
copy parser.py "%INSTALL_DIR%\" >nul
copy ast.py "%INSTALL_DIR%\" >nul
copy compiler.py "%INSTALL_DIR%\" >nul
copy bytecode.py "%INSTALL_DIR%\" >nul
copy vm.py "%INSTALL_DIR%\" >nul
copy main.py "%INSTALL_DIR%\" >nul

REM Create batch wrapper
echo Creating orbscript command...
echo @echo off > "%INSTALL_DIR%\orbscript.bat"
echo python "%INSTALL_DIR%\main.py" %%* >> "%INSTALL_DIR%\orbscript.bat"

REM Add to PATH
echo Adding to PATH...
setx PATH "%PATH%;%INSTALL_DIR%" >nul

REM Create examples directory
mkdir "%INSTALL_DIR%\examples" 2>nul

echo.
echo OrbScript installed successfully!
echo You can now use the 'orbscript' command from anywhere.
echo.
echo Try: orbscript run -c 'say "Hello World"'
echo.
pause