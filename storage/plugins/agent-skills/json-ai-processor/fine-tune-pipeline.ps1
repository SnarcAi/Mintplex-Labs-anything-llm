# JSON AI Assistant - Fine-Tuning Pipeline (Windows PowerShell)
# Automates the process of fine-tuning a local LLM for JSON tasks

$ErrorActionPreference = "Stop"

# Configuration
$BASE_MODEL = "deepseek-coder:6.7b"  # or llama3:8b, codellama:7b
$DATASET_PATH = ".\json_training_5k.jsonl"
$OUTPUT_MODEL = "json-ai-assistant"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "JSON AI Assistant Fine-Tuning" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Base Model: $BASE_MODEL"
Write-Host "Dataset: $DATASET_PATH"
Write-Host "Output Model: $OUTPUT_MODEL"
Write-Host ""

# Step 1: Generate training dataset
Write-Host "[1/6] Generating training dataset..." -ForegroundColor Yellow
if (-Not (Test-Path $DATASET_PATH)) {
    node training-dataset-generator.js
    Write-Host "✓ Dataset generated: $DATASET_PATH" -ForegroundColor Green
} else {
    Write-Host "✓ Dataset already exists: $DATASET_PATH" -ForegroundColor Green
}

# Step 2: Validate dataset
Write-Host ""
Write-Host "[2/6] Validating dataset..." -ForegroundColor Yellow
$LINE_COUNT = (Get-Content $DATASET_PATH | Measure-Object -Line).Lines
Write-Host "✓ Dataset contains $LINE_COUNT examples" -ForegroundColor Green

# Step 3: Create Modelfile for fine-tuning
Write-Host ""
Write-Host "[3/6] Creating Modelfile..." -ForegroundColor Yellow

$ModelfileContent = @"
FROM $BASE_MODEL

# System prompt optimized for JSON tasks
SYSTEM """You are a specialized JSON AI assistant. You excel at:
- Validating and analyzing JSON/JSONL data
- Detecting and fixing syntax errors
- Inferring and validating JSON Schemas
- Generating realistic synthetic JSON data
- Transforming and optimizing JSON structures
- Processing large JSON datasets efficiently

Always provide precise, accurate responses. When fixing JSON, explain what was wrong.
When generating data, ensure it's realistic and follows best practices."""

# Parameters optimized for JSON processing
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096
PARAMETER repeat_penalty 1.1
PARAMETER num_gpu 99

# Templates
TEMPLATE """{{ if .System }}<|system|>
{{ .System }}<|end|>
{{ end }}{{ if .Prompt }}<|user|>
{{ .Prompt }}<|end|>
{{ end }}<|assistant|>
{{ .Response }}<|end|>
"""
"@

Set-Content -Path "Modelfile" -Value $ModelfileContent
Write-Host "✓ Modelfile created" -ForegroundColor Green

# Step 4: Pull base model if needed
Write-Host ""
Write-Host "[4/6] Checking base model..." -ForegroundColor Yellow
$models = ollama list
if ($models -notmatch $BASE_MODEL) {
    Write-Host "Pulling base model: $BASE_MODEL" -ForegroundColor Yellow
    ollama pull $BASE_MODEL
} else {
    Write-Host "✓ Base model already available" -ForegroundColor Green
}

# Step 5: Create custom model
Write-Host ""
Write-Host "[5/6] Creating optimized model..." -ForegroundColor Yellow
ollama create $OUTPUT_MODEL -f Modelfile
Write-Host "✓ Model created: $OUTPUT_MODEL" -ForegroundColor Green

# Step 6: Test the model
Write-Host ""
Write-Host "[6/6] Testing the model..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Test Query: Validate this JSON: {`"key`": `"value`",}" -ForegroundColor Cyan
Write-Host ""
Write-Host "Response:" -ForegroundColor Cyan
$testInput = 'Validate the following JSON and fix any errors: {"key": "value",}'
ollama run $OUTPUT_MODEL $testInput

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "✓ Fine-tuning pipeline completed!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your JSON AI assistant is ready!" -ForegroundColor Cyan
Write-Host "Model name: $OUTPUT_MODEL" -ForegroundColor Yellow
Write-Host ""
Write-Host "To use it:" -ForegroundColor Cyan
Write-Host "  ollama run $OUTPUT_MODEL" -ForegroundColor White
Write-Host ""
Write-Host "To integrate with AnythingLLM:" -ForegroundColor Cyan
Write-Host "  1. Go to Settings > LLM Preference" -ForegroundColor White
Write-Host "  2. Select 'Ollama' as provider" -ForegroundColor White
Write-Host "  3. Set model to: $OUTPUT_MODEL" -ForegroundColor White
Write-Host ""
