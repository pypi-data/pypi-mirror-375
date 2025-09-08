# HeartAI Installation Guide

## Quick Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from Source

1. **Clone the repository:**
```bash
git clone https://github.com/ahmetxhero/AhmetX-HeartAi.git
cd AhmetX-HeartAi
```

2. **Install in development mode:**
```bash
pip install -e .
```

3. **Verify installation:**
```bash
heartai info
```

## Usage Examples

### Command Line Interface

```bash
# Generate sample ECG data
heartai generate --duration 10 --heart-rate 75 --output sample.csv --plot sample.png

# Predict arrhythmia from ECG file
heartai predict sample.csv --output results.json --plot prediction.png

# Comprehensive analysis
heartai analyze sample.csv --output ./analysis_results

# Create training dataset
heartai create-dataset --normal-samples 50 --arrhythmia-samples 50 --output-dir ./dataset
```

### Python API

```python
from heartai import ECGAnalyzer

# Load and analyze ECG data
analyzer = ECGAnalyzer("ecg_data.csv")
analyzer.preprocess()
prediction = analyzer.predict()

print("Prediction:", prediction)
```

## Running Examples

```bash
# Basic usage example
python examples/basic_usage.py

# Advanced analysis example
python examples/advanced_analysis.py

# CLI examples
python examples/cli_examples.py
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_analyzer.py -v
```

## Project Structure

```
AhmetX-HeartAi/
├── heartai/                 # Main package
│   ├── core/               # Core analysis modules
│   ├── utils/              # Utility functions
│   ├── visualization/      # Plotting tools
│   └── cli.py             # Command-line interface
├── examples/               # Usage examples
├── tests/                 # Unit tests
├── requirements.txt       # Dependencies
├── setup.py              # Package setup
└── README.md             # Project documentation
```

## Dependencies

The library requires the following Python packages:
- numpy >= 1.21.0
- scipy >= 1.7.0
- pandas >= 1.3.0
- scikit-learn >= 1.0.0
- matplotlib >= 3.5.0
- click >= 8.0.0

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you installed the package with `pip install -e .`
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Permission errors**: Use `--user` flag: `pip install --user -e .`

### Getting Help

- Check the [GitHub repository](https://github.com/ahmetxhero/AhmetX-HeartAi)
- Run `heartai --help` for CLI usage
- Use `heartai COMMAND --help` for specific command help
