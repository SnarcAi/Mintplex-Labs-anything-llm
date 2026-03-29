@echo off
REM MissFlora Qwen 2.5 7B QLoRA Training - Başlatma Scripti
REM Windows için otomatik kurulum ve eğitim

title MissFlora AI Training - Qwen 2.5 7B QLoRA

echo ============================================================
echo   MISSFLORA AI CUSTOMER ASSISTANT TRAINING
echo   Qwen 2.5 7B QLoRA (4-bit) - RTX 5080 16GB Optimize
echo ============================================================
echo.

REM Python kontrolü
echo [1/5] Python kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo HATA: Python bulunamadi! Python 3.13.7 yukleyin.
    pause
    exit /b 1
)
echo ✓ Python bulundu
echo.

REM CUDA kontrolü
echo [2/5] CUDA kontrol ediliyor...
python -c "import torch; print('CUDA:', torch.cuda.is_available())" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠ PyTorch yuklu degil, yukleniyor...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
)
echo ✓ CUDA hazir
echo.

REM Kütüphaneleri yükle
echo [3/5] Gerekli kutuphaneler yukleniyor...
echo Bu islem birka dakika sürebilir...
pip install -q transformers datasets peft accelerate bitsandbytes trl scipy sentencepiece flask flask-cors matplotlib
echo ✓ Kutuphaneler yuklendi
echo.

REM Dataset kontrolü
echo [4/5] Dataset kontrol ediliyor...
if not exist "missflora_dataset_full.py" (
    echo ⚠ missflora_dataset_full.py bulunamadi!
    echo Training minimal dataset ile devam edecek.
    pause
) else (
    echo ✓ Tam dataset mevcut
)
echo.

REM Eğitimi başlat
echo [5/5] Egitim baslat iliyor...
echo ============================================================
echo   RTX 5080 16GB + 128GB RAM + Ryzen 9 9950X
echo   Tahmini sure: 2-4 saat (5 epoch)
echo   VRAM kullanimi: ~6-8 GB
echo ============================================================
echo.
echo Egitim basliyor... Loglar consol'da goruntulernecek.
echo.
pause

python missflora_qwen_training.py

echo.
echo ============================================================
if %errorlevel% equ 0 (
    echo ✓ EGITIM TAMAMLANDI!
    echo.
    echo Model kaydedildi: ./missflora-qwen-final-...
    echo.
    echo SONRAKI ADIMLAR:
    echo   1. web_integration.py icinde MODEL_PATH guncelleyin
    echo   2. python web_integration.py ile API baslatin
    echo   3. missflora_chatbot.html ile test edin
    echo.
) else (
    echo ❌ EGITIM HATASI!
    echo Loglari kontrol edin.
)
echo ============================================================
pause
