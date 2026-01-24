# Setting Up On-Premise AI Models for GNSS Log Analysis

This guide helps you set up on-premise, open-source AI models for the GNSS Log Analyzer. All models run locally on your machine, ensuring **data privacy and IP protection** for company R&D projects.

## Why On-Premise Models?

- **Data Privacy**: Your GNSS logs never leave your infrastructure
- **IP Protection**: No third-party API calls, no data sent to external services
- **Cost**: No per-token API fees
- **Compliance**: Meets corporate security and compliance requirements
- **Offline**: Works without internet connectivity

## Option 1: Ollama (RECOMMENDED)

Ollama is the easiest way to run open-source LLMs locally.

### Installation

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### macOS
```bash
# Download from https://ollama.ai/download
# Or use Homebrew:
brew install ollama
```

#### Windows
Download the installer from: https://ollama.ai/download

### Starting Ollama

```bash
# Start Ollama server (runs in background)
ollama serve
```

### Pulling Models

```bash
# Recommended: Mistral 7B (best balance of speed and accuracy)
ollama pull mistral:7b

# Alternative models:
ollama pull llama2:7b        # LLaMA 2 7B
ollama pull llama2:13b       # LLaMA 2 13B (more accurate, slower)
ollama pull codellama:7b     # Code-focused LLaMA
ollama pull mixtral:8x7b     # Mixtral 8x7B (most capable, needs GPU)
ollama pull llama3:8b        # LLaMA 3 8B (newer, better)
ollama pull phi3:3.8b        # Phi-3 3.8B (smaller, faster)
```

### Testing

```bash
# Test that Ollama is working
ollama run mistral:7b "Explain GNSS position jumps"
```

### Using with GNSS Analyzer

```bash
# Default (uses mistral:7b)
python analyze_gnss_logs.py sample_data/gnss_log_with_issues.txt --ai

# With different model
python analyze_gnss_logs.py log.txt --ai --model llama2:13b

# With custom Ollama host
python analyze_gnss_logs.py log.txt --ai --api-url http://192.168.1.100:11434
```

### Model Comparison

| Model | Size | RAM Required | Speed | Accuracy | Best For |
|-------|------|--------------|-------|----------|----------|
| `mistral:7b` | 4.1 GB | 8 GB | Fast | Good | **Recommended default** |
| `llama2:7b` | 3.8 GB | 8 GB | Fast | Good | General purpose |
| `llama2:13b` | 7.3 GB | 16 GB | Medium | Better | More accuracy needed |
| `llama3:8b` | 4.7 GB | 10 GB | Fast | Better | Newer, improved |
| `codellama:7b` | 3.8 GB | 8 GB | Fast | Good | Technical analysis |
| `mixtral:8x7b` | 26 GB | 32 GB | Slow | Best | Maximum accuracy |
| `phi3:3.8b` | 2.3 GB | 4 GB | Very fast | Decent | Resource constrained |

## Option 2: HuggingFace Transformers

For more control and customization, you can load models directly with HuggingFace Transformers.

### Installation

```bash
pip install transformers torch accelerate
```

### GPU Support (Optional but Recommended)

```bash
# For NVIDIA GPUs
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For AMD GPUs (ROCm)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6
```

### Usage

```bash
# Use HuggingFace backend
python analyze_gnss_logs.py log.txt --ai \
  --backend huggingface \
  --model meta-llama/Llama-2-7b-chat-hf

# Other models:
python analyze_gnss_logs.py log.txt --ai \
  --backend huggingface \
  --model mistralai/Mistral-7B-Instruct-v0.2
```

### Recommended HuggingFace Models

```bash
# Mistral 7B Instruct
mistralai/Mistral-7B-Instruct-v0.2

# LLaMA 2 7B Chat (requires HuggingFace approval)
meta-llama/Llama-2-7b-chat-hf

# LLaMA 2 13B Chat (requires HuggingFace approval)
meta-llama/Llama-2-13b-chat-hf

# Falcon 7B Instruct
tiiuae/falcon-7b-instruct

# MPT 7B Instruct
mosaicml/mpt-7b-instruct

# Vicuna 7B
lmsys/vicuna-7b-v1.5
```

### Getting Access to Gated Models

Some models (like LLaMA 2) require approval:

1. Create HuggingFace account: https://huggingface.co/join
2. Request access to model page (e.g., https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)
3. Get your token: https://huggingface.co/settings/tokens
4. Set environment variable:
   ```bash
   export HF_TOKEN='hf_your_token_here'
   ```

## Option 3: Custom API Endpoint

If you have your own model serving infrastructure (e.g., vLLM, TGI, FastChat).

### Usage

```bash
python analyze_gnss_logs.py log.txt --ai \
  --backend api \
  --api-url http://your-server:8080 \
  --model your-model-name
```

### Compatible Servers

- **vLLM**: High-performance inference server
- **Text Generation Inference (TGI)**: HuggingFace's inference server
- **FastChat**: Chatbot training and deployment platform
- **LocalAI**: OpenAI-compatible API for local models
- **LM Studio**: Desktop app for running local models

## Programmatic Usage

### Example: Using Ollama

```python
from gnss_analyzer.parsers import GNSSLogParser
from gnss_analyzer.analyzers import PositionAnalyzer, AIAnalyzer

# Parse logs
parser = GNSSLogParser()
points = parser.parse_file('gnss_log.txt')

# Detect anomalies
analyzer = PositionAnalyzer()
anomalies = analyzer.analyze_all(points)

# AI analysis with on-premise model
ai = AIAnalyzer(
    model='mistral:7b',
    backend='ollama',
    api_url='http://localhost:11434'  # default
)

# Analyze anomalies
for anomaly in anomalies:
    analysis = ai.analyze_anomaly(anomaly)
    print(f"Root cause: {analysis['root_causes']}")
```

### Example: Using HuggingFace

```python
ai = AIAnalyzer(
    model='mistralai/Mistral-7B-Instruct-v0.2',
    backend='huggingface',
    hf_token='hf_your_token'  # optional
)

analysis = ai.analyze_multiple_anomalies(anomalies)
print(analysis['primary_root_cause'])
```

## Performance Tips

### CPU-Only Systems

If you don't have a GPU:
- Use smaller models: `mistral:7b`, `llama2:7b`, `phi3:3.8b`
- Expect slower inference (10-30 seconds per analysis)
- Consider using quantized models for better performance

### GPU Systems

- Use larger models for better accuracy: `llama2:13b`, `mixtral:8x7b`
- Enable GPU acceleration in HuggingFace:
  ```python
  ai = AIAnalyzer(
      model='mistralai/Mistral-7B-Instruct-v0.2',
      backend='huggingface'
  )  # Automatically uses GPU if available
  ```

### Memory Considerations

- 8GB RAM: `phi3:3.8b`, `mistral:7b`, `llama2:7b`
- 16GB RAM: `llama2:13b`, `codellama:13b`
- 32GB+ RAM: `mixtral:8x7b`, `llama2:70b`

## Troubleshooting

### Ollama Connection Failed

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### Model Not Found

```bash
# List installed models
ollama list

# Pull the model
ollama pull mistral:7b
```

### Out of Memory

Try a smaller model:
```bash
ollama pull phi3:3.8b
python analyze_gnss_logs.py log.txt --ai --model phi3:3.8b
```

### Slow Performance

- Use GPU if available
- Try quantized models (automatically used by Ollama)
- Reduce model size (use 7B instead of 13B)

### HuggingFace Model Access Denied

Some models require approval:
1. Go to model page (e.g., https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)
2. Click "Request Access"
3. Wait for approval (usually instant to 24 hours)

## Comparison: Ollama vs HuggingFace vs Custom API

| Feature | Ollama | HuggingFace | Custom API |
|---------|--------|-------------|------------|
| Ease of Setup | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Performance | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Flexibility | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Model Selection | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Best For | Quick start | Customization | Production |

## Recommended Setup for Company R&D

For corporate environments where IP protection is critical:

### Step 1: Install Ollama

```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from: https://ollama.ai/download
```

### Step 2: Pull Recommended Model

```bash
ollama pull mistral:7b
```

### Step 3: Test

```bash
python analyze_gnss_logs.py sample_data/gnss_log_with_issues.txt --ai
```

### Step 4: Deploy to Internal Infrastructure

For team use:
1. Set up Ollama on a dedicated server
2. Use `--api-url` to point to internal server:
   ```bash
   python analyze_gnss_logs.py log.txt --ai --api-url http://ai-server.company.local:11434
   ```

## Security Notes

- All models run locally - no data sent to external services
- No API keys required (unlike OpenAI, Anthropic, etc.)
- Logs and analysis stay within your infrastructure
- Suitable for sensitive GNSS data from field testing
- Compliant with corporate data governance policies

## Further Reading

- Ollama Documentation: https://github.com/ollama/ollama
- HuggingFace Model Hub: https://huggingface.co/models
- vLLM (High-performance serving): https://github.com/vllm-project/vllm
- Text Generation Inference: https://github.com/huggingface/text-generation-inference

## Support

If you encounter issues:
1. Check model is pulled: `ollama list`
2. Verify Ollama is running: `curl http://localhost:11434/api/tags`
3. Try fallback analysis without `--ai` flag
4. Check system resources (RAM, disk space)
