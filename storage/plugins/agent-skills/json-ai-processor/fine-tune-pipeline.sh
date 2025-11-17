#!/bin/bash

###############################################################################
# JSON AI Assistant - Fine-Tuning Pipeline
# Automates the process of fine-tuning a local LLM for JSON tasks
###############################################################################

set -e

# Configuration
BASE_MODEL="deepseek-coder:6.7b"  # or llama3:8b, codellama:7b
DATASET_PATH="./json_training_5k.jsonl"
OUTPUT_MODEL="json-ai-assistant"
LORA_RANK=32
LEARNING_RATE=2e-4
BATCH_SIZE=4
EPOCHS=3
MAX_SEQ_LENGTH=2048

echo "=================================="
echo "JSON AI Assistant Fine-Tuning"
echo "=================================="
echo ""
echo "Base Model: $BASE_MODEL"
echo "Dataset: $DATASET_PATH"
echo "Output Model: $OUTPUT_MODEL"
echo ""

# Step 1: Generate training dataset
echo "[1/6] Generating training dataset..."
if [ ! -f "$DATASET_PATH" ]; then
    node training-dataset-generator.js
    echo "✓ Dataset generated: $DATASET_PATH"
else
    echo "✓ Dataset already exists: $DATASET_PATH"
fi

# Step 2: Validate dataset
echo ""
echo "[2/6] Validating dataset..."
LINE_COUNT=$(wc -l < "$DATASET_PATH")
echo "✓ Dataset contains $LINE_COUNT examples"

# Step 3: Create Modelfile for fine-tuning
echo ""
echo "[3/6] Creating Modelfile..."
cat > Modelfile <<EOF
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

# Templates
TEMPLATE """{{ if .System }}<|system|>
{{ .System }}<|end|>
{{ end }}{{ if .Prompt }}<|user|>
{{ .Prompt }}<|end|>
{{ end }}<|assistant|>
{{ .Response }}<|end|>
"""
EOF

echo "✓ Modelfile created"

# Step 4: Pull base model if needed
echo ""
echo "[4/6] Checking base model..."
if ! ollama list | grep -q "$BASE_MODEL"; then
    echo "Pulling base model: $BASE_MODEL"
    ollama pull $BASE_MODEL
else
    echo "✓ Base model already available"
fi

# Step 5: Create custom model with optimized settings
echo ""
echo "[5/6] Creating optimized model..."
ollama create $OUTPUT_MODEL -f Modelfile
echo "✓ Model created: $OUTPUT_MODEL"

# Step 6: Test the model
echo ""
echo "[6/6] Testing the model..."
echo ""
echo "Test Query: Validate this JSON: {\"key\": \"value\",}"
echo ""
echo "Response:"
echo '{"instruction": "Validate this JSON", "input": "{\"key\": \"value\",}"}' | \
    ollama run $OUTPUT_MODEL "Validate the following JSON and fix any errors: {\"key\": \"value\",}"

echo ""
echo "=================================="
echo "✓ Fine-tuning pipeline completed!"
echo "=================================="
echo ""
echo "Your JSON AI assistant is ready!"
echo "Model name: $OUTPUT_MODEL"
echo ""
echo "To use it:"
echo "  ollama run $OUTPUT_MODEL"
echo ""
echo "To integrate with AnythingLLM:"
echo "  1. Go to Settings > LLM Preference"
echo "  2. Select 'Ollama' as provider"
echo "  3. Set model to: $OUTPUT_MODEL"
echo ""
