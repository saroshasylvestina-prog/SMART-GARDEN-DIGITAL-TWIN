# Installation Guide - Plant Disease Detection

## Required Extensions/Packages

You need to install the following Python packages to use the Plant Disease Detection feature:

### 1. **Pillow** (Image Processing)
   - Required for image handling and processing
   - Command: `pip install Pillow==10.1.0`

### 2. **NumPy** (Numerical Operations)
   - Required for image analysis and calculations
   - Command: `pip install numpy==1.24.3`

### 3. **Flask** (Already installed)
   - Web framework (should already be installed)
   - Command: `pip install Flask==3.0.0`

## Quick Installation

Run this command to install all required packages:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install Pillow==10.1.0 numpy==1.24.3
```

## Optional: TensorFlow (Advanced ML)

TensorFlow is **NOT required** for basic functionality. The system works with rule-based detection.

If you want to use machine learning models in the future:
```bash
pip install tensorflow==2.15.0
```

## Verification

After installation, verify packages are installed:

```bash
pip list | findstr /i "pillow numpy flask"
```

You should see:
- Pillow
- numpy
- Flask

## Browser Requirements

**No browser extensions needed!** The system works with:
- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Any modern browser with JavaScript enabled

## System Requirements

- **Python 3.7+** (Python 3.8+ recommended)
- **Operating System**: Windows, Linux, or macOS
- **Disk Space**: ~100MB for packages
- **RAM**: 512MB minimum (1GB+ recommended)

## Installation Steps

1. **Open terminal/command prompt** in the project directory

2. **Install packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python -c "from PIL import Image; import numpy; print('All packages installed successfully!')"
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the scanner**:
   - Go to: `http://localhost:5000`
   - Find "Plant Health Scanner" section
   - Or visit: `http://localhost:5000/plant-scan`

## Troubleshooting

### If Pillow installation fails:
```bash
pip install --upgrade pip
pip install Pillow
```

### If NumPy installation fails:
```bash
pip install --upgrade pip
pip install numpy
```

### If you get import errors:
- Make sure you're in the correct directory
- Check Python version: `python --version` (should be 3.7+)
- Try: `pip install --upgrade Pillow numpy`

## What You DON'T Need

❌ **No browser extensions**
❌ **No additional software**
❌ **No special hardware**
❌ **No TensorFlow** (optional only)
❌ **No GPU** (works on CPU)

## Current Status Check

Run this to check what's installed:
```bash
python -c "try:
    from PIL import Image
    print('✅ Pillow: Installed')
except:
    print('❌ Pillow: Not installed')

try:
    import numpy
    print('✅ NumPy: Installed')
except:
    print('❌ NumPy: Not installed')

try:
    import flask
    print('✅ Flask: Installed')
except:
    print('❌ Flask: Not installed')"
```

