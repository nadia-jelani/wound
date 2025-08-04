# Wound Analysis & Classification System

A comprehensive machine learning system for wound detection, segmentation, and analysis using deep learning models.

## 🚀 Features

- **Wound Classification**: Binary classification (wound vs non-wound) using ResNet50
- **Wound Segmentation**: U-Net based segmentation for precise wound area detection
- **Progress Tracking**: Monitor wound healing progress over time
- **Report Generation**: Automated PDF reports with visualizations
- **Web Interface**: Flask-based web application for easy interaction
- **Multi-model Support**: ResNet, U-Net, and SimCLR implementations

## 📁 Project Structure

```
├── train_classifier.py          # Main classifier training script
├── train_resnet.py             # ResNet50 training
├── train_resnet_optimized.py   # Optimized ResNet training
├── train_simclr_unet.py        # SimCLR + U-Net training
├── analyze_wound.py            # Flask web application
├── test_wound_progress.py      # Wound progress analysis
├── wound_checker.py            # GUI application
├── classifier.py               # Classification utilities
├── wound_analyze.py            # Wound analysis utilities
└── requirements.txt            # Python dependencies
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd wound-analysis-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export DATASET_PATH="/path/to/your/dataset"
   export MODEL_SAVE_PATH="/path/to/save/models"
   ```

## 🎯 Usage

### Training Models

**Train Classifier:**
```bash
python train_classifier.py
```

**Train ResNet:**
```bash
python train_resnet.py
```

**Train SimCLR U-Net:**
```bash
python train_simclr_unet.py
```

### Running Applications

**Web Interface:**
```bash
python analyze_wound.py
```

**GUI Application:**
```bash
python wound_checker.py
```

**Progress Analysis:**
```bash
python test_wound_progress.py
```

## 📊 Model Performance

- **Classification Accuracy**: ~95% on wound/non-wound classification
- **Segmentation IoU**: ~0.85 on wound area segmentation
- **Processing Speed**: ~2-3 seconds per image

## 🔧 Configuration

Update the following paths in your scripts:
- `DATASET_PATH`: Path to your training dataset
- `MODEL_SAVE_PATH`: Path to save trained models
- `UPLOAD_FOLDER`: Path for web app uploads
- `REPORT_FOLDER`: Path for generated reports

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For questions and support, please open an issue in the repository.