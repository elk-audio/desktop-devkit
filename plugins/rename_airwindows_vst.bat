@echo off

rem Rename airwindows Windows DLLs so that the names match MacOS, run this
rem inside the airwindows-win folder if plugins are updated.

setlocal enabledelayedexpansion

echo Renaming files from *64.dll to *.vst...
echo.

for %%f in (*64.dll) do (
    set "filename=%%~nf"
    set "newname=!filename:~0,-2!.vst"
    
    if exist "!newname!" (
        echo WARNING: !newname! already exists, skipping %%f
    ) else (
        echo Renaming: %%f --^> !newname!
        ren "%%f" "!newname!"
    )
)

echo.
echo Done!
pause
