
# HeartAI Installation Guide

## Method 1: Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv heartai_env
source heartai_env/bin/activate  # On macOS/Linux
# heartai_env\Scripts\activate  # On Windows

# Install dependencies
pip install numpy scipy pandas scikit-learn matplotlib seaborn click rich pydantic joblib

# Install HeartAI
pip install -e .

# Test installation
heartai info
```

## Method 2: User Installation
```bash
# Install dependencies for user only
pip install --user numpy scipy pandas scikit-learn matplotlib seaborn click rich pydantic joblib

# Install HeartAI for user only
pip install --user -e .
```

## Method 3: System Installation (if allowed)
```bash
# Install dependencies system-wide
pip install --break-system-packages numpy scipy pandas scikit-learn matplotlib seaborn click rich pydantic joblib

# Install HeartAI
pip install --break-system-packages -e .
```

## Verify Installation
```bash
python3 -c "import heartai; print('HeartAI installed successfully!')"
heartai info
python examples/basic_usage.py
```
