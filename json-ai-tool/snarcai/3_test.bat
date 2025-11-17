@echo off
REM SnarcAI Test Script
REM Fine-tuned modeli test eder

echo ========================================
echo SnarcAI Chat - Test
echo ========================================
echo.

echo Fine-tuned model yukleniyor...
echo.

echo Test sorulari:
echo   - WC blok 40g icin maliyet hesapla
echo   - Maliyet 25TL, hedef %%30 marj. Satis fiyati?
echo   - Stok 3000, kritik esik 5000. Ne yapmaliyim?
echo.

echo Cikmak icin 'q' veya 'cik' yazin
echo.
echo ========================================
echo.

REM Chat baslat
python snarcai_chat.py

echo.
pause
