@echo off
REM Simple script to compile core.c into a shared library

REM Get the directory where the script resides
SET DIR=%~dp0
SET OUTPUT_NAME=core.dll REM Use .so for Linux/macOS

echo Compiling core.c into %OUTPUT_NAME%...

REM Compile using gcc with standard C99, creating a position-independent shared object
gcc -shared -o "%DIR%\%OUTPUT_NAME%" -Wl,--out-implib,%DIR%\libcore.a -fPIC "%DIR%\core.c" -std=c99

IF %ERRORLEVEL% EQU 0 (
  echo Compilation successful: %OUTPUT_NAME% created in %DIR%
) ELSE (
  echo Compilation failed.
  exit /b 1
)

exit /b 0