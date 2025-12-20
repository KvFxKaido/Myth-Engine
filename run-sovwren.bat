@echo off
REM Sovwren IDE Launcher (repo root wrapper)
REM Calls the real launcher at Sovwren\run-sovwren.bat so shortcuts can live at repo root.

setlocal
pushd "%~dp0Sovwren" || exit /b 1
call run-sovwren.bat
popd
endlocal

