@echo off
echo Cleaning up unnecessary files...

REM Delete setup.py (no longer needed)
if exist "setup.py" (
    del "setup.py"
    echo Deleted setup.py
)

REM Delete Python cache files in backend
echo Cleaning Python cache files...
for /d /r "backend" %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d"
        echo Deleted %%d
    )
)

REM Delete .pyc files in backend
for /r "backend" %%f in (*.pyc) do (
    if exist "%%f" (
        del "%%f"
        echo Deleted %%f
    )
)

REM Delete log files in node_modules
if exist "frontend\node_modules\nwsapi\dist\lint.log" (
    del "frontend\node_modules\nwsapi\dist\lint.log"
    echo Deleted lint.log
)

echo.
echo Cleanup complete!
echo.
echo The following files were safely removed:
echo - setup.py (development setup script)
echo - Python cache files (*.pyc and __pycache__ directories)
echo - Log files in node_modules
echo.
echo Your project structure is now cleaner and these files will be
echo automatically regenerated when needed.
pause
