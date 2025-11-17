@echo off
REM SnarcAI Training Script
REM Fine-tuning'i baslatir

echo ========================================
echo SnarcAI Fine-Tuning
echo ========================================
echo.

echo Model: Qwen 2.5 7B Instruct
echo Dataset: 50 ornek (Turkce)
echo GPU: RTX 5080 16GB
echo Tahmini sure: 30-60 dakika
echo.

echo Varsayilan parametreler:
echo   - Epochs: 5
echo   - Batch size: 2
echo   - LoRA rank: 64
echo   - Learning rate: 1e-4
echo.

set /p CONFIRM="Training'i baslatmak istiyor musunuz? (E/H): "
if /i not "%CONFIRM%"=="E" (
    echo Iptal edildi.
    pause
    exit /b 0
)

echo.
echo ========================================
echo TRAINING BASLIYOR...
echo ========================================
echo.

REM Training baslat
python finetune_snarcai.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo TRAINING BASARILI!
    echo ========================================
    echo.
    echo Model kaydedildi: snarcai-qwen-2.5-7b\final
    echo.
    echo Sonraki adim: 3_test.bat
) else (
    echo.
    echo ========================================
    echo TRAINING BASARISIZ!
    echo ========================================
    echo.
    echo Loglari kontrol edin.
)

echo.
pause
