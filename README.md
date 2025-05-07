# Bumphunter Analyzer Engine

A Python-based tool for analyzing poker session data to detect potential bumphunting behavior.

## Features
- Detects suspicious table joins within configurable time threshold
- Profiles potential bumphunters and their targets
- Calculates bumphunter scores based on multiple factors:
  - Join frequency (40 points max)
  - Join percentage (30 points max)
  - Target consistency (30 points max)
- Generates interactive HTML report with data compression

## Requirements
- Python 3.8+
- pandas
- numpy

## Usage
```bash
# Place your CSV file in the project directory
python Analizer.py
```

The script will generate an HTML report in the `output` directory.

## Input CSV Format
Required columns:
- tableId
- tableName
- username
- startSession (datetime)
- endSession (datetime)
- gameType
- limitType
- smallBlind
- bigBlind