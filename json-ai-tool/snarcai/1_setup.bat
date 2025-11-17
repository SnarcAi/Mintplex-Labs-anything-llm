@echo off
REM SnarcAI Setup Script
REM Gerekli paketleri yükler

echo ========================================
echo SnarcAI Setup
echo ========================================
echo.

echo [1/5] Python versiyonu kontrol ediliyor...
python --version
if %errorlevel% neq 0 (
    echo HATA: Python bulunamadi!
    pause
    exit /b 1
)
echo.

echo [2/5] CUDA kontrol ediliyor...
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'YOK')" 2>nul
if %errorlevel% neq 0 (
    echo UYARI: PyTorch yuklu degil, simdi yuklenecek...
    echo.
    echo [3/5] PyTorch yukleniyor (CUDA 12.1)...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
) else (
    echo PyTorch zaten yuklu
)
echo.

echo [4/5] Transformers ve PEFT yukleniyor...
pip install transformers>=4.36.0 peft>=0.7.0 datasets>=2.16.0 accelerate>=0.25.0
pip install sentencepiece protobuf tensorboard
echo.

echo [5/5] GPU test ediliyor...
python -c "import torch; assert torch.cuda.is_available(), 'CUDA yok!'; print(f'GPU: {torch.cuda.get_device_name(0)}'); print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')"
echo.

echo ========================================
echo Setup tamamlandi!
echo ========================================
echo.
echo Sonraki adim: 2_train.bat
pause
