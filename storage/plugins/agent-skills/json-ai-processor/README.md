# 🤖 JSON AI Assistant - Offline AI-Powered JSON Processor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AnythingLLM](https://img.shields.io/badge/AnythingLLM-Plugin-blue)](https://useanything.com)
[![Ollama](https://img.shields.io/badge/Ollama-Compatible-green)](https://ollama.ai)

**Fully offline, AI-powered JSON processor with validation, error fixing, schema inference, and intelligent data generation capabilities.**

---

## ✨ Features

### 🔍 Core Capabilities
- ✅ **JSON Validation** - Syntax checking and schema validation
- 🔧 **Automatic Error Fixing** - Intelligent error detection and repair
- 📊 **Deep Analysis** - Structure analysis, statistics, and insights
- 🧬 **Schema Inference** - Extract JSON Schema from data
- 🎲 **Smart Data Generation** - Generate realistic synthetic data (1000+ records)
- 📝 **JSONL Processing** - Handle JSON Lines format efficiently
- 🔄 **Data Transformation** - Transform and optimize JSON structures
- ⚡ **Batch Processing** - Handle large datasets with ease

### 🎯 Use Cases
- **API Development** - Validate and generate test data
- **Data Migration** - Fix and transform JSON structures
- **Testing** - Generate thousands of realistic test records
- **Schema Design** - Infer schemas from existing data
- **Data Quality** - Detect and fix JSON errors
- **ML Training** - Generate synthetic training data

---

## 🚀 Quick Start

### Prerequisites
- **Windows 11** (or Linux/macOS)
- **Python 3.13+**
- **Node.js 18+**
- **NVIDIA GPU** (optional but recommended)
- **16GB+ RAM** (32GB+ for large models)

### Installation (Windows)

**Option 1: Automated Setup (Recommended)**
```powershell
# Clone or navigate to your AnythingLLM directory
cd storage/plugins/agent-skills/json-ai-processor

# Run quick start script
.\quick-start.ps1
```

**Option 2: Manual Setup**
```powershell
# 1. Install Ollama
winget install Ollama.Ollama

# 2. Start Ollama
ollama serve

# 3. Pull base model
ollama pull deepseek-coder:6.7b

# 4. Run fine-tuning pipeline
.\fine-tune-pipeline.ps1

# 5. Test the model
ollama run json-ai-assistant "Validate this JSON: {\"key\": \"value\"}"
```

**For detailed Turkish instructions:** See [KURULUM_KILAVUZU.md](./KURULUM_KILAVUZU.md)

---

## 📖 Usage

### AnythingLLM Integration

1. **Enable Plugin:**
   - Go to **Settings** → **Agent Skills**
   - Enable `json-ai-processor` plugin

2. **Configure LLM:**
   - Go to **Settings** → **LLM Preference**
   - Provider: `Ollama`
   - Model: `json-ai-assistant`

3. **Create Workspace:**
   - Create new workspace
   - Enable Agent Mode
   - Select `json-ai-processor` skill

### Command Examples

#### 1. JSON Validation
```
Validate this JSON:
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```

#### 2. Error Fixing
```
Fix this broken JSON:
{
  "name": "test",
  "age": 25,
}
```

#### 3. Schema Inference
```
Infer JSON Schema from this data:
{
  "id": 1,
  "email": "user@example.com",
  "tags": ["premium", "active"]
}
```

#### 4. Data Generation
```
Generate 1000 realistic user records with:
- id (integer)
- name (string)
- email (valid email format)
- age (18-75)
- address (street, city, country)
```

#### 5. Template-based Generation
```
Generate 500 records using this template:
{
  "userId": "{{index}}",
  "email": "user{{index}}@example.com",
  "uuid": "{{uuid}}",
  "timestamp": "{{timestamp}}"
}
```

#### 6. JSONL Processing
```
Process this JSONL data:
{"id":1,"value":100}
{"id":2,"value":200}
{"id":3,"value":300}
```

### Programmatic Usage

```javascript
// Via AnythingLLM Agent API
const response = await agent.run({
  operation: "generate",
  options: JSON.stringify({
    count: 1000,
    dataType: "users",
    realism: "high"
  })
});
```

See [examples.json](./examples.json) for more examples.

---

## 🏗️ Architecture

```
json-ai-processor/
├── plugin.json                    # Plugin configuration
├── handler.js                     # Main plugin logic
├── advanced-generator.js          # ML-powered data generator
├── training-dataset-generator.js  # Training data creator
├── fine-tune-pipeline.ps1         # Windows fine-tuning script
├── fine-tune-pipeline.sh          # Linux/Mac fine-tuning script
├── quick-start.ps1                # Automated setup (Windows)
├── examples.json                  # Usage examples
├── KURULUM_KILAVUZU.md           # Turkish setup guide
└── README.md                      # This file
```

### Components

#### 1. **JSONAIProcessor** (handler.js)
- Core JSON processing engine
- Operations: validate, fix, analyze, generate, transform
- AJV-based schema validation
- Intelligent error detection

#### 2. **AdvancedJSONGenerator** (advanced-generator.js)
- ML-inspired data generation
- Realistic user, product, transaction, log data
- Pattern recognition and variability control
- Template-based generation

#### 3. **TrainingDatasetGenerator** (training-dataset-generator.js)
- Generates 5000+ training examples
- 12 different task types
- Multiple output formats (JSONL, Alpaca, ShareGPT)
- Fine-tuning ready datasets

---

## ⚙️ Configuration

### Model Options

| Model | Size | VRAM | Speed | Quality | Best For |
|-------|------|------|-------|---------|----------|
| `deepseek-coder:6.7b` | 6.7B | ~4GB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | JSON tasks (Recommended) |
| `deepseek-coder:33b-q4` | 33B | ~12GB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Complex analysis |
| `llama3:70b-q4` | 70B | ~14GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Maximum quality |
| `codellama:13b` | 13B | ~8GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | General coding |

### GPU Optimization (Ollama)

```powershell
# Set environment variables (PowerShell Admin)
[System.Environment]::SetEnvironmentVariable('OLLAMA_NUM_GPU', '99', 'Machine')
[System.Environment]::SetEnvironmentVariable('OLLAMA_FLASH_ATTENTION', '1', 'Machine')
```

### Modelfile Customization

```dockerfile
FROM deepseek-coder:6.7b

SYSTEM """Your custom system prompt here..."""

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER num_gpu 99
```

---

## 📊 Performance

### Benchmarks (RTX 5080 16GB)

| Operation | Records | Time | Throughput |
|-----------|---------|------|------------|
| Validation | 1,000 | ~2s | 500 rec/s |
| Error Fixing | 1,000 | ~5s | 200 rec/s |
| Data Generation | 10,000 | ~15s | 666 rec/s |
| Schema Inference | 1 | <1s | - |

### Token Generation Speed

| Model | Tokens/Second |
|-------|---------------|
| deepseek-coder:6.7b | 50-100 |
| deepseek-coder:33b-q4 | 20-40 |
| llama3:70b-q4 | 10-20 |

---

## 🛠️ Development

### Training Dataset Generation

```bash
# Generate 5000 training examples
node training-dataset-generator.js
```

Output: `json_training_5k.jsonl`

### Custom Fine-tuning

```powershell
# Edit fine-tune-pipeline.ps1 to customize:
$BASE_MODEL = "your-preferred-model"
$DATASET_PATH = "./your_dataset.jsonl"
$OUTPUT_MODEL = "your-model-name"

# Run pipeline
.\fine-tune-pipeline.ps1
```

### Plugin Development

```javascript
// handler.js - Add new operation
case 'my_operation':
  result = myCustomFunction(json_input, opts);
  break;
```

---

## 🐛 Troubleshooting

### Issue: "Ollama connection failed"
```powershell
# Restart Ollama service
Stop-Process -Name ollama -Force
ollama serve
```

### Issue: "GPU not being used"
```powershell
# Check CUDA
nvidia-smi

# Set GPU env var
$env:OLLAMA_NUM_GPU = "99"
ollama serve
```

### Issue: "Model too slow"
```powershell
# Use smaller model
ollama pull deepseek-coder:6.7b

# Or quantized version
ollama pull llama3:70b-q4_0
```

### Issue: "Out of memory"
```dockerfile
# Reduce context in Modelfile
PARAMETER num_ctx 2048  # Instead of 4096
```

---

## 📚 Documentation

- **[KURULUM_KILAVUZU.md](./KURULUM_KILAVUZU.md)** - Comprehensive Turkish setup guide
- **[examples.json](./examples.json)** - Usage examples and templates
- **[AnythingLLM Docs](https://docs.useanything.com)** - Official AnythingLLM documentation
- **[Ollama Docs](https://ollama.ai/docs)** - Ollama documentation

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **AnythingLLM** - Platform for AI assistants
- **Ollama** - Local LLM runtime
- **DeepSeek** - DeepSeek Coder models
- **AJV** - JSON Schema validator

---

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check [KURULUM_KILAVUZU.md](./KURULUM_KILAVUZU.md) for detailed setup
- Review [examples.json](./examples.json) for usage patterns

---

## 🎯 Roadmap

- [ ] Support for JSON5 format
- [ ] Advanced schema generation with examples
- [ ] Data masking and anonymization
- [ ] JSON diff and patch operations
- [ ] GraphQL to JSON conversion
- [ ] API endpoint testing integration
- [ ] Real-time JSON streaming support

---

**Built with ❤️ for the JSON community**

**Version:** 1.0.0
**Last Updated:** 2025-01-17
**Optimized for:** RTX 5080, AMD Ryzen 9 9950X, 128GB RAM
