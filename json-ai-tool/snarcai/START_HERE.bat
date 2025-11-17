@echo off
REM SnarcAI Quick Start
REM Tum adimlari gosterir

color 0A

echo.
echo ========================================
echo   SnarcAI Fine-Tuning Wizard
echo   Burak Kumuk'un Dijital Ikizi
echo ========================================
echo.
echo Model: Qwen 2.5 7B Instruct
echo Dataset: 50 Turkce ornek
echo GPU: RTX 5080 16GB
echo.
echo ========================================
echo   ADIMLAR
echo ========================================
echo.
echo 1. Setup      - Gerekli paketleri yukle
echo 2. Train      - Model'i fine-tune et (30-60 dk)
echo 3. Test       - Fine-tuned modeli test et
echo.
echo Q. Cikis
echo.
echo ========================================

set /p CHOICE="Seciminiz (1/2/3/Q): "

if "%CHOICE%"=="1" goto SETUP
if "%CHOICE%"=="2" goto TRAIN
if "%CHOICE%"=="3" goto TEST
if /i "%CHOICE%"=="Q" goto END

echo Gecersiz secim!
pause
goto START

:SETUP
echo.
echo ========================================
echo SETUP BASLIYOR...
echo ========================================
echo.
call 1_setup.bat
goto END

:TRAIN
echo.
echo ========================================
echo TRAINING BASLIYOR...
echo ========================================
echo.
call 2_train.bat
goto END

:TEST
echo.
echo ========================================
echo TEST BASLIYOR...
echo ========================================
echo.
call 3_test.bat
goto END

:END
echo.
echo Programdan cikiliyor...
echo.
pause
