# HeartAI 🫀

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/ahmetxhero/heartai)

**heartai** is a Python library designed to process ECG/EKG (electrocardiogram) signals and provide AI-powered predictions for potential arrhythmia risks. It is aimed at researchers, healthcare data scientists, and developers who want to experiment with biosignal processing and lightweight machine learning models in the medical domain.

## 🛠 Features

### 📊 ECG Signal Processing
- Load ECG data from `.csv`, `.txt`, or standard formats
- Apply noise filtering (Butterworth, band-pass, etc.)
- Normalize and segment signals for analysis

### 🤖 AI/ML Prediction
- Pre-trained lightweight ML model for arrhythmia detection
- Binary classification: Normal rhythm vs Potential arrhythmia
- Option to train on custom datasets

### 📈 Visualization Tools
- Plot ECG waveforms (P-QRS-T cycles)
- Highlight detected anomalies

### 🔌 Extensible
- Easy integration with healthcare IoT devices and research pipelines
- Modular design for custom ML models

## 🚀 Quick Start

### Installation

```bash
pip install heartai
```

### Command Line Usage

```bash
# Predict arrhythmia risk from ECG data
heartai predict ecg_data.csv
```

### Python API Usage

```python
from heartai import ECGAnalyzer

# Load and analyze ECG data
analyzer = ECGAnalyzer("ecg_data.csv")
analyzer.preprocess()
prediction = analyzer.predict()

print("Prediction:", prediction)
```

**Output example:**
```
Prediction: Potential arrhythmia detected (confidence: 87%)
```

## 📋 Requirements

- Python 3.8+
- NumPy, SciPy, Pandas
- Scikit-learn
- Matplotlib, Seaborn

## 🎯 Roadmap (2025 Vision)

- [ ] Support for real-time ECG streaming
- [ ] Integration with wearable devices (Apple Watch, Fitbit, etc.)
- [ ] Deep learning models for multi-class arrhythmia classification
- [ ] REST API & FastAPI microservice deployment

## Documentation

For detailed documentation, examples, and API reference, visit our [GitHub repository](https://github.com/ahmetxhero/AhmetX-HeartAi).

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This library is for research and educational purposes only. It is not intended for clinical diagnosis or medical decision-making. Always consult with qualified healthcare professionals for medical advice.

## 📧 Contact

- GitHub: [AhmetX-HeartAi](https://github.com/ahmetxhero/AhmetX-HeartAi)
- Email: ahmetxhero@gmail.com

---

Made with ❤️ for the healthcare research community
