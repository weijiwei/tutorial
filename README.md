# GNSS Log Analyzer

AI-powered analysis tool for GNSS/GPS logs to detect position anomalies and identify root causes.

## Features

- **Multi-format Support**: Parse NMEA GGA sentences and custom CSV formats
- **Anomaly Detection**: Automatically detect:
  - Position jumps (unrealistic speed/distance changes)
  - HDOP spikes (accuracy degradation)
  - Satellite signal loss
- **AI-Powered Analysis**: Use OpenAI GPT models to analyze root causes
- **Pattern Recognition**: Identify systemic issues across multiple anomalies
- **Rule-based Fallback**: Works without AI for basic analysis

## Quick Start

### Installation

1. Clone or navigate to the project directory:
```bash
cd /home/user/tutorial
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Basic Usage

Analyze a GNSS log file (without AI):
```bash
python analyze_gnss_logs.py sample_data/gnss_log_with_issues.txt
```

### AI-Powered Analysis (On-Premise)

For detailed root cause analysis using **on-premise open-source AI models**:

1. Install Ollama (easiest method):
```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from: https://ollama.ai/download
```

2. Pull an AI model:
```bash
# Recommended: Mistral 7B
ollama pull mistral:7b

# Or other models: llama2:7b, llama3:8b, codellama:7b, mixtral:8x7b
```

3. Run analysis with AI:
```bash
# Using Mistral 7B (default)
python analyze_gnss_logs.py sample_data/gnss_log_with_issues.txt --ai

# Using LLaMA 2 13B (more accurate)
python analyze_gnss_logs.py sample_data/gnss_log_with_issues.txt --ai --model llama2:13b

# Using Mixtral (most capable)
python analyze_gnss_logs.py sample_data/gnss_log_with_issues.txt --ai --model mixtral:8x7b
```

**Important**: All AI models run **locally on your machine**. No data is sent to external services. Perfect for company R&D projects where IP protection matters.

See [SETUP_AI_MODELS.md](SETUP_AI_MODELS.md) for detailed setup instructions.

## Sample Data

The project includes two sample log files:

- `sample_data/gnss_log_with_issues.txt` - Contains simulated position jumps and signal issues
- `sample_data/gnss_log_clean.txt` - Clean GNSS data in NMEA format

## Supported Log Formats

### NMEA GGA Format
```
$GPGGA,100000.00,3746.4957,N,12225.1651,W,1,08,1.2,50.0,M,0.0,M,,*6E
```

### Custom CSV Format
```
timestamp,latitude,longitude,altitude,satellites,hdop,quality
2024-01-22T10:00:00,37.774929,-122.419418,50.0,8,1.2,1
```

## Project Structure

```
tutorial/
├── gnss_analyzer/           # Main package
│   ├── parsers/             # Log file parsers
│   │   └── gnss_parser.py   # NMEA and CSV parser
│   ├── analyzers/           # Analysis modules
│   │   ├── position_analyzer.py  # Anomaly detection
│   │   └── ai_analyzer.py        # AI-powered root cause analysis
│   └── utils/               # Utility functions
├── sample_data/             # Sample GNSS logs
├── tests/                   # Unit tests
├── analyze_gnss_logs.py     # Main analysis script
└── requirements.txt         # Python dependencies
```

## How It Works

### 1. Log Parsing
The parser reads GNSS log files and extracts:
- Position data (latitude, longitude, altitude)
- Quality metrics (satellites, HDOP, fix quality)
- Timestamps

### 2. Anomaly Detection
The position analyzer detects:

**Position Jumps**: Calculates implied speed between consecutive points and flags jumps that exceed physical limits (default: 30 m/s or 108 km/h).

**HDOP Spikes**: Identifies sudden increases in HDOP (Horizontal Dilution of Precision), indicating poor satellite geometry.

**Satellite Loss**: Detects rapid loss of satellite signals.

### 3. Root Cause Analysis

#### Rule-based Analysis (Default)
- Correlates anomalies with satellite count, HDOP, and fix quality
- Provides basic recommendations

#### AI-Powered Analysis (--ai flag)
- Uses GPT models to analyze anomaly patterns
- Identifies systemic issues vs isolated incidents
- Provides detailed root cause analysis with confidence levels
- Suggests prioritized actions and diagnostic steps

## Common Issues and Solutions

### Issue 1: Position Jump Detected

**Symptoms**: Large distance change in short time

**Common Root Causes**:
- Satellite signal loss (check satellite count drop)
- HDOP degradation (poor satellite geometry)
- Multipath interference (signals bouncing off buildings)
- Signal obstruction (entering tunnel, urban canyon)

**Solutions**:
- Use DGPS/RTK corrections for better accuracy
- Improve antenna placement
- Enable multi-constellation GNSS (GPS + GLONASS + Galileo)

### Issue 2: HDOP Spike

**Symptoms**: Sudden increase in HDOP value

**Common Root Causes**:
- Poor satellite geometry
- Limited sky visibility
- Satellite constellation changes

**Solutions**:
- Wait for satellite constellation to improve
- Move to location with better sky visibility
- Use prediction data (almanac/ephemeris)

### Issue 3: Satellite Loss

**Symptoms**: Rapid decrease in tracked satellites

**Common Root Causes**:
- Physical obstruction (buildings, terrain)
- Electromagnetic interference
- Antenna issues
- Receiver configuration problems

**Solutions**:
- Check for physical obstructions
- Verify antenna connection and placement
- Review receiver sensitivity settings
- Check for interference sources

## Customization

### Adjust Detection Thresholds

Edit `analyze_gnss_logs.py`:

```python
# Change maximum expected speed (default: 30 m/s = 108 km/h)
position_analyzer = PositionAnalyzer(max_speed_mps=50.0)  # 180 km/h
```

### Use Different AI Models

```bash
# Mistral 7B (default - good balance)
python analyze_gnss_logs.py log.txt --ai --model mistral:7b

# LLaMA 2 13B (more accurate, needs 16GB RAM)
python analyze_gnss_logs.py log.txt --ai --model llama2:13b

# Mixtral 8x7B (most capable, needs GPU)
python analyze_gnss_logs.py log.txt --ai --model mixtral:8x7b

# Phi-3 3.8B (fastest, smallest)
python analyze_gnss_logs.py log.txt --ai --model phi3:3.8b
```

## API Usage

Use the analyzer programmatically:

```python
from gnss_analyzer.parsers import GNSSLogParser
from gnss_analyzer.analyzers import PositionAnalyzer, AIAnalyzer

# Parse log file
parser = GNSSLogParser()
points = parser.parse_file('my_gnss_log.txt')

# Detect anomalies
analyzer = PositionAnalyzer(max_speed_mps=30.0)
anomalies = analyzer.analyze_all(points)

# AI analysis with on-premise model
ai = AIAnalyzer(
    model='mistral:7b',
    backend='ollama'
)
for anomaly in anomalies:
    analysis = ai.analyze_anomaly(anomaly)
    print(f"Root cause: {analysis['root_causes']}")
```

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Parsers

Create a new parser in `gnss_analyzer/parsers/`:

```python
from .gnss_parser import GNSSPoint

class MyCustomParser:
    def parse_file(self, filepath: str) -> List[GNSSPoint]:
        # Your parsing logic here
        pass
```

## Troubleshooting

### AI Backend Not Available

If you see "ollama backend not available":
1. Install Ollama: https://ollama.ai/download
2. Start Ollama: `ollama serve`
3. Pull a model: `ollama pull mistral:7b`
4. Run analysis again with `--ai` flag

### No Anomalies Detected

If the tool doesn't detect expected anomalies:
- Check if thresholds are too permissive (increase `max_speed_mps`)
- Verify log file format is supported
- Ensure timestamps are consecutive

### Import Errors

If you get import errors:
```bash
# Make sure you're in the project directory
cd /home/user/tutorial

# Install dependencies
pip install -r requirements.txt

# Run from project root
python analyze_gnss_logs.py sample_data/gnss_log_with_issues.txt
```

## About GNSS Terminology

- **GNSS**: Global Navigation Satellite System (includes GPS, GLONASS, Galileo, BeiDou)
- **HDOP**: Horizontal Dilution of Precision (lower is better, <2 is excellent)
- **Fix Quality**: 0=invalid, 1=GPS fix, 2=DGPS fix, 3=PPS fix, etc.
- **Satellites**: Number of satellites used for position calculation (4+ needed for 3D fix)

## On-Premise AI Models

This tool uses **open-source models that run entirely on your infrastructure**:

### Recommended Models
- `mistral:7b` - Mistral 7B (default, excellent balance)
- `llama2:7b` / `llama2:13b` - Meta's LLaMA 2
- `llama3:8b` - Meta's LLaMA 3 (newer, better)
- `codellama:7b` - Code-focused LLaMA variant
- `mixtral:8x7b` - Mixtral (most capable)
- `phi3:3.8b` - Microsoft Phi-3 (smallest, fastest)

### Why On-Premise?
- **Data Privacy**: Your GNSS logs never leave your infrastructure
- **IP Protection**: No third-party API calls, critical for R&D projects
- **No Costs**: No per-token API fees
- **Compliance**: Meets corporate security requirements
- **Offline**: Works without internet

See [SETUP_AI_MODELS.md](SETUP_AI_MODELS.md) for complete setup guide.

## License

MIT License - Feel free to use and modify for your projects.

## Support

For issues or questions, please open an issue in the repository.
