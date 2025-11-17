# JSON AI Assistant - Quick Start Script
# Bu script, JSON AI Assistant'ı hızlı bir şekilde kurar ve test eder

param(
    [switch]$SkipInstall,
    [switch]$SkipTest,
    [string]$Model = "deepseek-coder:6.7b"
)

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     JSON AI ASSISTANT - QUICK START SETUP         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Sistem Bilgilerini Göster
Write-Host "📊 Sistem Bilgileri:" -ForegroundColor Yellow
Write-Host "   OS: $(Get-WmiObject -Class Win32_OperatingSystem | Select-Object -ExpandProperty Caption)"
Write-Host "   CPU: $(Get-WmiObject -Class Win32_Processor | Select-Object -ExpandProperty Name)"
Write-Host "   RAM: $([math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory/1GB, 2)) GB"

# GPU Kontrolü
try {
    $gpuInfo = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>$null
    if ($gpuInfo) {
        Write-Host "   GPU: $gpuInfo" -ForegroundColor Green
    }
} catch {
    Write-Host "   GPU: NVIDIA GPU bulunamadı (CUDA gerekli)" -ForegroundColor Red
}

Write-Host ""

# 1. Ollama Kontrolü
Write-Host "🔍 [1/7] Ollama kontrolü..." -ForegroundColor Yellow

try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "   ✓ Ollama yüklü: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Ollama bulunamadı!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Ollama'yı şuradan indirin: https://ollama.ai/download/windows" -ForegroundColor Yellow
    Write-Host "veya PowerShell Admin ile çalıştırın: winget install Ollama.Ollama" -ForegroundColor Yellow
    exit 1
}

# 2. Ollama Servis Kontrolü
Write-Host ""
Write-Host "🔍 [2/7] Ollama servis kontrolü..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "   ✓ Ollama servisi çalışıyor" -ForegroundColor Green
} catch {
    Write-Host "   ! Ollama servisi başlatılıyor..." -ForegroundColor Yellow
    Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow
    Start-Sleep -Seconds 3
    Write-Host "   ✓ Ollama servisi başlatıldı" -ForegroundColor Green
}

# 3. Base Model İndirme
if (-not $SkipInstall) {
    Write-Host ""
    Write-Host "📥 [3/7] Base model indiriliyor: $Model..." -ForegroundColor Yellow

    $existingModels = ollama list
    if ($existingModels -match $Model) {
        Write-Host "   ✓ Model zaten mevcut: $Model" -ForegroundColor Green
    } else {
        Write-Host "   → Downloading... (bu biraz zaman alabilir)" -ForegroundColor Cyan
        ollama pull $Model
        Write-Host "   ✓ Model indirildi: $Model" -ForegroundColor Green
    }
} else {
    Write-Host ""
    Write-Host "⏭️  [3/7] Model indirme atlandı (--SkipInstall)" -ForegroundColor Gray
}

# 4. Training Dataset Oluşturma
Write-Host ""
Write-Host "📝 [4/7] Training dataset oluşturuluyor..." -ForegroundColor Yellow

if (Test-Path "json_training_5k.jsonl") {
    Write-Host "   ✓ Dataset zaten mevcut: json_training_5k.jsonl" -ForegroundColor Green
} else {
    node training-dataset-generator.js
    if (Test-Path "json_training_5k.jsonl") {
        $lineCount = (Get-Content "json_training_5k.jsonl" | Measure-Object -Line).Lines
        Write-Host "   ✓ Dataset oluşturuldu: $lineCount örnek" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Dataset oluşturulamadı!" -ForegroundColor Red
        exit 1
    }
}

# 5. Modelfile Oluşturma
Write-Host ""
Write-Host "⚙️  [5/7] Modelfile oluşturuluyor..." -ForegroundColor Yellow

$modelfileContent = @"
FROM $Model

SYSTEM """You are a specialized JSON AI assistant. You excel at:
- Validating and analyzing JSON/JSONL data
- Detecting and fixing syntax errors
- Inferring and validating JSON Schemas
- Generating realistic synthetic JSON data
- Transforming and optimizing JSON structures
- Processing large JSON datasets efficiently

Always provide precise, accurate responses. When fixing JSON, explain what was wrong.
When generating data, ensure it's realistic and follows best practices."""

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096
PARAMETER repeat_penalty 1.1
PARAMETER num_gpu 99
"@

Set-Content -Path "Modelfile" -Value $modelfileContent
Write-Host "   ✓ Modelfile oluşturuldu" -ForegroundColor Green

# 6. Custom Model Oluşturma
Write-Host ""
Write-Host "🎓 [6/7] JSON AI Assistant modeli oluşturuluyor..." -ForegroundColor Yellow

$customModel = "json-ai-assistant"
$existingModels = ollama list

if ($existingModels -match $customModel) {
    Write-Host "   ! Model zaten mevcut. Yeniden oluşturuluyor..." -ForegroundColor Yellow
    ollama rm $customModel 2>$null
}

ollama create $customModel -f Modelfile
Write-Host "   ✓ Model oluşturuldu: $customModel" -ForegroundColor Green

# 7. Test
if (-not $SkipTest) {
    Write-Host ""
    Write-Host "🧪 [7/7] Model test ediliyor..." -ForegroundColor Yellow
    Write-Host ""

    $tests = @(
        @{
            Name = "JSON Validation"
            Prompt = 'Validate this JSON: {"name": "test", "age": 25}'
        },
        @{
            Name = "JSON Fixing"
            Prompt = 'Fix this JSON: {"name": "test", "age": 25,}'
        },
        @{
            Name = "Data Generation"
            Prompt = 'Generate 3 user records with id, name, and email'
        }
    )

    foreach ($test in $tests) {
        Write-Host "   Test: $($test.Name)" -ForegroundColor Cyan
        Write-Host "   Query: $($test.Prompt)" -ForegroundColor Gray
        Write-Host "   Response:" -ForegroundColor Gray

        $response = ollama run $customModel $test.Prompt --verbose 2>&1
        $responseText = $response | Out-String
        $preview = $responseText.Substring(0, [Math]::Min(200, $responseText.Length))
        Write-Host "   $preview..." -ForegroundColor White
        Write-Host ""
    }

    Write-Host "   ✓ Tüm testler tamamlandı" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⏭️  [7/7] Test atlandı (--SkipTest)" -ForegroundColor Gray
}

# Özet
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              KURULUM TAMAMLANDI! 🎉                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Kurulum Özeti:" -ForegroundColor Cyan
Write-Host "   • Ollama: Çalışıyor" -ForegroundColor White
Write-Host "   • Base Model: $Model" -ForegroundColor White
Write-Host "   • Custom Model: $customModel" -ForegroundColor White
Write-Host "   • Training Dataset: json_training_5k.jsonl" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Kullanmaya Başlayın:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1. Komut satırından:" -ForegroundColor Yellow
Write-Host "      ollama run $customModel" -ForegroundColor White
Write-Host ""
Write-Host "   2. AnythingLLM'de:" -ForegroundColor Yellow
Write-Host "      • Settings → LLM Preference" -ForegroundColor White
Write-Host "      • Provider: Ollama" -ForegroundColor White
Write-Host "      • Model: $customModel" -ForegroundColor White
Write-Host ""
Write-Host "📖 Detaylı kullanım için:" -ForegroundColor Cyan
Write-Host "   .\KURULUM_KILAVUZU.md dosyasını okuyun" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Örnek Komutlar:" -ForegroundColor Cyan
Write-Host "   • 'Validate this JSON: {\"key\": \"value\"}'" -ForegroundColor White
Write-Host "   • 'Fix this JSON: {key: \"value\",}'" -ForegroundColor White
Write-Host "   • 'Generate 100 user records'" -ForegroundColor White
Write-Host "   • 'Infer schema from this data: {...}'" -ForegroundColor White
Write-Host ""

# GPU Performans Önerisi
try {
    $gpu = nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>$null
    if ($gpu -gt 10000) {
        Write-Host "💡 İpucu: GPU'nuz çok güçlü ($([math]::Round($gpu/1024, 1)) GB)!" -ForegroundColor Yellow
        Write-Host "   Daha büyük modelleri deneyebilirsiniz:" -ForegroundColor Yellow
        Write-Host "   • ollama pull deepseek-coder:33b-q4" -ForegroundColor White
        Write-Host "   • ollama pull llama3:70b-q4" -ForegroundColor White
        Write-Host ""
    }
} catch {
    # GPU info alınamazsa sessizce devam et
}

Write-Host "Keyifli Kullanımlar! 🎉" -ForegroundColor Green
Write-Host ""
