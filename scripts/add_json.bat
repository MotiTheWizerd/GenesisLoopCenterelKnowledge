@echo off
echo 🚀 Ray Memory JSON Importer
echo ============================

if "%1"=="" (
    echo Usage: add_json.bat path\to\your\file.json
    echo Example: add_json.bat data\my_data.json
    pause
    exit /b 1
)

echo 📁 Processing: %1
python scripts\add_json_to_memory.py %1

echo.
echo ✅ Import complete!
echo 💡 Restart your dashboard to see the new memories
pause