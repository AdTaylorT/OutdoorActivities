@echo off
echo Building WeatherBike executable...
REM pyinstaller --clean weather.spec --log-level DEBUG
pyinstaller --clean weather.spec
if errorlevel 1 (
    echo Build failed! Check the output above for errors.
    pause
    exit /b 1
)
echo Build complete. Executable is in the dist/WeatherBike folder.
pause
