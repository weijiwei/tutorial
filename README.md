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

### AI-Powered Analysis

For detailed root cause analysis using AI:

1. Set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

2. Run analysis with AI:
```bash
# Using GPT-3.5 (faster, cheaper)
python analyze_gnss_logs.py sample_data/gnss_log_with_issues.txt --ai

# Using GPT-4 (more accurate)
python analyze_gnss_logs.py sample_data/gnss_log_with_issues.txt --ai --model gpt-4
```

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
# GPT-3.5 Turbo (faster, cheaper)
python analyze_gnss_logs.py log.txt --ai --model gpt-3.5-turbo

# GPT-4 (more accurate, slower, more expensive)
python analyze_gnss_logs.py log.txt --ai --model gpt-4

# GPT-4 Turbo (good balance)
python analyze_gnss_logs.py log.txt --ai --model gpt-4-turbo
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

# AI analysis
ai = AIAnalyzer(model='gpt-4')
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

### OpenAI API Key Not Found

If you see "OpenAI API key not found":
1. Get API key from https://platform.openai.com/api-keys
2. Set environment variable: `export OPENAI_API_KEY='sk-...'`
3. Or pass directly in code: `AIAnalyzer(api_key='sk-...')`

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

## Note on AI Model Names

This tool uses OpenAI's actual available models:
- `gpt-3.5-turbo` - Fast and cost-effective
- `gpt-4` - Most capable (as of 2024)
- `gpt-4-turbo` - Faster GPT-4 variant

Note: There is no "GPT-OSS-20B" model. The tool defaults to `gpt-3.5-turbo` which provides excellent results for log analysis.

## License

MIT License - Feel free to use and modify for your projects.

## Support

For issues or questions, please open an issue in the repository.
