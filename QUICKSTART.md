# Quick Start Guide - GNSS Log Analyzer for Company R&D

## Overview

You now have a **complete GNSS log analysis prototype** that uses **on-premise AI models** to protect your company's intellectual property. All analysis happens locally on your infrastructure with no external API calls.

## What You Can Do

✅ **Detect Position Anomalies** - Automatically find position jumps in field testing data
✅ **Root Cause Analysis** - AI identifies WHY anomalies occurred (satellite loss, HDOP issues, etc.)
✅ **IP Protection** - All data stays on your infrastructure, no third-party services
✅ **Production Ready** - Works with real NMEA logs and custom formats

## Instant Demo (No Setup Required)

Test the prototype immediately with rule-based analysis:

```bash
cd /home/user/tutorial

# Analyze sample data with issues
python analyze_gnss_logs.py sample_data/gnss_log_with_issues.txt

# Analyze clean sample data
python analyze_gnss_logs.py sample_data/gnss_log_clean.txt
```

You'll see:
- 4 detected anomalies in the problematic log
- 0 anomalies in the clean log
- Position jumps correlated with satellite loss and HDOP spikes

## Enable AI Analysis (5-Minute Setup)

For AI-powered root cause analysis, set up Ollama:

### 1. Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**
```bash
brew install ollama
# Or download from: https://ollama.ai/download
```

**Windows:**
Download from: https://ollama.ai/download

### 2. Pull an AI Model

```bash
# Recommended: Mistral 7B (4GB download)
ollama pull mistral:7b

# Alternative: LLaMA 3 8B (newer)
ollama pull llama3:8b

# For better accuracy (7GB download, needs 16GB RAM)
ollama pull llama2:13b
```

### 3. Run AI Analysis

```bash
python analyze_gnss_logs.py sample_data/gnss_log_with_issues.txt --ai
```

You'll now get:
- **Pattern Analysis** - Identifies systemic issues vs isolated incidents
- **Root Cause Confidence** - 85-90% confidence scores for each diagnosis
- **Prioritized Actions** - What to fix first
- **Diagnostic Steps** - How to investigate further

## Using with Your Own Data

### Supported Formats

**NMEA GGA (standard GPS format):**
```
$GPGGA,100000.00,3746.4957,N,12225.1651,W,1,08,1.2,50.0,M,0.0,M,,*6E
```

**Custom CSV:**
```csv
timestamp,latitude,longitude,altitude,satellites,hdop,quality
2024-01-22T10:00:00,37.774929,-122.419418,50.0,8,1.2,1
```

### Analyze Your Logs

```bash
# Basic analysis
python analyze_gnss_logs.py your_log_file.txt

# With AI
python analyze_gnss_logs.py your_log_file.txt --ai

# Different model
python analyze_gnss_logs.py your_log_file.txt --ai --model llama3:8b
```

## Understanding the Output

### Example Output

```
Anomaly #1 [CRITICAL]
  Type: POSITION_JUMP
  Position jump detected: 113.4m in 1.0s (implied speed: 408.2 km/h)
  Satellites: 3, HDOP: 8.5
  Distance jump: 113.4m
```

**What This Means:**
- Position jumped 113 meters in 1 second
- This implies 408 km/h speed (physically impossible for your device)
- Satellite count dropped to 3 (minimum is 4 for good 3D fix)
- HDOP spiked to 8.5 (poor satellite geometry, >5 is bad)

**Root Cause (from AI):**
- Satellite signal loss (85% confidence)
- HDOP degradation indicating poor geometry (80% confidence)
- Evidence: Lost 5 satellites, HDOP increased by 7.3

### Severity Levels

- **CRITICAL**: Urgent issue, position completely unreliable
- **HIGH**: Significant issue, affects accuracy substantially
- **MEDIUM**: Moderate issue, investigate if persistent

## Programmatic Usage

Integrate into your testing pipeline:

```python
from gnss_analyzer.parsers import GNSSLogParser
from gnss_analyzer.analyzers import PositionAnalyzer, AIAnalyzer

# Parse your log
parser = GNSSLogParser()
points = parser.parse_file('field_test_log.txt')

# Detect anomalies
analyzer = PositionAnalyzer(max_speed_mps=30.0)  # Adjust for your use case
anomalies = analyzer.analyze_all(points)

# AI analysis (on-premise)
ai = AIAnalyzer(model='mistral:7b', backend='ollama')

if anomalies:
    # Get pattern analysis
    analysis = ai.analyze_multiple_anomalies(anomalies)
    print(f"Primary issue: {analysis['primary_root_cause']}")

    # Detailed analysis of critical anomalies
    for anomaly in anomalies:
        if anomaly.severity == "CRITICAL":
            detail = ai.analyze_anomaly(anomaly)
            print(f"Root cause: {detail['root_causes']}")
```

## Customization

### Adjust Detection Thresholds

Edit the analyzer parameters:

```python
analyzer = PositionAnalyzer(
    max_speed_mps=50.0,        # Max expected speed (default: 30 m/s = 108 km/h)
    max_hdop=6.0,              # HDOP threshold (default: 5.0)
    hdop_spike_threshold=3.0   # HDOP spike detection (default: 3.0)
)
```

### Use Different AI Models

```bash
# Fastest (small devices, limited RAM)
python analyze_gnss_logs.py log.txt --ai --model phi3:3.8b

# Balanced (recommended)
python analyze_gnss_logs.py log.txt --ai --model mistral:7b

# More accurate (needs 16GB RAM)
python analyze_gnss_logs.py log.txt --ai --model llama2:13b

# Most capable (needs GPU, 32GB RAM)
python analyze_gnss_logs.py log.txt --ai --model mixtral:8x7b
```

## Deployment for Team Use

### Option 1: Individual Setup
Each team member installs Ollama on their machine.

### Option 2: Shared Server
1. Install Ollama on a dedicated server
2. Configure to accept network connections:
   ```bash
   # On server
   OLLAMA_HOST=0.0.0.0:11434 ollama serve
   ```
3. Team members use `--api-url`:
   ```bash
   python analyze_gnss_logs.py log.txt --ai --api-url http://ai-server.company.local:11434
   ```

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve

# In another terminal
ollama pull mistral:7b
```

### "Model not found"
```bash
# List installed models
ollama list

# Pull the model you need
ollama pull mistral:7b
```

### Slow Performance
- Use smaller model: `phi3:3.8b`
- Enable GPU (automatic if available)
- Use quantized models (Ollama does this automatically)

### Out of Memory
Try a smaller model:
```bash
ollama pull phi3:3.8b
python analyze_gnss_logs.py log.txt --ai --model phi3:3.8b
```

## Files Overview

```
tutorial/
├── README.md                    # Complete documentation
├── QUICKSTART.md               # This file
├── SETUP_AI_MODELS.md          # Detailed AI setup guide
├── requirements.txt            # Python dependencies
├── analyze_gnss_logs.py        # Main CLI tool
├── example_usage.py            # Programmatic usage example
├── gnss_analyzer/              # Core package
│   ├── parsers/
│   │   └── gnss_parser.py      # NMEA and CSV parser
│   └── analyzers/
│       ├── position_analyzer.py # Anomaly detection
│       └── ai_analyzer.py       # AI root cause analysis
└── sample_data/
    ├── gnss_log_with_issues.txt  # Sample with anomalies
    └── gnss_log_clean.txt         # Sample clean log
```

## Next Steps

1. **Test with your real field data**
   ```bash
   python analyze_gnss_logs.py your_field_test_log.txt --ai
   ```

2. **Adjust thresholds for your use case**
   - Modify `max_speed_mps` based on your device (vehicle, drone, handheld)
   - Adjust HDOP thresholds based on your accuracy requirements

3. **Integrate into your testing pipeline**
   - Use programmatic API in your test automation
   - Generate reports automatically after field tests

4. **Deploy to team infrastructure**
   - Set up shared Ollama server
   - Add to CI/CD pipeline
   - Create custom dashboards

## Why This Approach?

✅ **IP Protection**: No data sent to OpenAI, Anthropic, or any external service
✅ **Cost Effective**: No per-token API fees, one-time setup
✅ **Compliance**: Meets corporate data governance requirements
✅ **Offline**: Works without internet connectivity
✅ **Customizable**: Full control over models and analysis logic

## Support

- **Setup Issues**: See SETUP_AI_MODELS.md
- **Model Selection**: See model comparison table in SETUP_AI_MODELS.md
- **API Usage**: See example_usage.py
- **Advanced Features**: See README.md

## Success! 🎉

You now have a production-ready GNSS log analyzer that:
- Detects position jumps and anomalies
- Uses AI to identify root causes
- Runs entirely on your infrastructure
- Protects your company's IP and data

Start analyzing your field test logs today:
```bash
python analyze_gnss_logs.py your_log.txt --ai
```
