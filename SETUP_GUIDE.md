# 🚀 RickyMama Setup Guide

Complete setup instructions for running the RickyMama data entry system on any machine.

## 📋 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB available space
- **Display**: 1024x768 minimum resolution

### Recommended Requirements
- **Python**: Version 3.10 or higher
- **RAM**: 8GB or more
- **Storage**: 2GB available space (for data and exports)
- **Display**: 1920x1080 or higher

## 🔧 Installation Steps

### Step 1: Install Python

#### Windows:
1. Download Python from [python.org](https://www.python.org/downloads/)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation: Open Command Prompt and run:
   ```cmd
   python --version
   ```

#### macOS:
1. Install using Homebrew (recommended):
   ```bash
   brew install python
   ```
   Or download from [python.org](https://www.python.org/downloads/)

2. Verify installation:
   ```bash
   python3 --version
   ```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Step 2: Download and Extract Project

1. Download the project ZIP file
2. Extract to your desired location (e.g., `Documents/RickyMama/`)
3. Open terminal/command prompt in the project folder

### Step 3: Set Up Virtual Environment (Recommended)

#### Windows:
```cmd
python -m venv rickymama_env
rickymama_env\Scripts\activate
```

#### macOS/Linux:
```bash
python3 -m venv rickymama_env
source rickymama_env/bin/activate
```

You should see `(rickymama_env)` in your terminal prompt.

### Step 4: Install Dependencies

With your virtual environment activated:

```bash
pip install -r requirements.txt
```

If you encounter any errors, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Initialize Database (First Time Only)

Run the database initialization script:

#### Windows:
```cmd
python setup_database.py
```

#### macOS/Linux:
```bash
python3 setup_database.py
```

### Step 6: Run the Application

#### Windows:
```cmd
python main_gui_working.py
```

#### macOS/Linux:
```bash
python3 main_gui_working.py
```

## 🎯 Quick Start

Once the application is running:

1. **Add Customers**: Click "Add Customer" and select Commission/Non-Commission type
2. **Enter Data**: Use the main input area with supported formats:
   - Pana: `123=500`
   - Time: `1 2 3=900`
   - Multiplication: `25x400`
   - Jodi: `22-24-26=500`
3. **View Tables**: Click "Tables" to see all data organized by type
4. **Export Data**: Use the Export tab to generate CSV reports

## 🐛 Troubleshooting

### Common Issues and Solutions

#### "Python not found" or "python is not recognized"
- **Windows**: Reinstall Python with "Add to PATH" checked
- **macOS/Linux**: Use `python3` instead of `python`

#### "No module named 'dearpygui'"
```bash
pip install --upgrade pip
pip install dearpygui==1.11.1
```

#### Application window doesn't appear
- Check if it's minimized in taskbar
- Try running from different terminal
- Ensure your display scaling is not too high (>150%)

#### Database errors on startup
Run the database reset script:
```bash
python setup_database.py --reset
```

#### Permission denied errors (Linux/macOS)
```bash
chmod +x main_gui_working.py
chmod +x setup_database.py
```

### Getting Help

1. **Check the logs**: Look in `logs/rickymama.log` for error details
2. **Run diagnostic**: Execute `python test_gui_functionality.py`
3. **Reset everything**: Delete `data/` folder and run `setup_database.py`

## 📂 Project Structure

```
RickyMama/
├── main_gui_working.py     # Main application file
├── setup_database.py       # Database initialization
├── requirements.txt        # Python dependencies
├── SETUP_GUIDE.md         # This file
├── src/                   # Source code modules
├── data/                  # Database files
├── config/                # Configuration files
├── docs/                  # Documentation
├── exports/               # CSV export files
└── logs/                  # Application logs
```

## 🔒 Data Safety

- **Backup**: The `data/` folder contains your database
- **Exports**: All data can be exported to CSV format
- **Recovery**: Database includes automatic backup features

## ⚡ Performance Tips

- **Close unused tabs** in the Tables window for better performance
- **Regular exports** help keep the database optimized
- **Restart weekly** to clear memory and refresh connections

## 🆕 Updates

To update the application:
1. Download the new version
2. Replace all files EXCEPT the `data/` folder
3. Run `pip install -r requirements.txt` to update dependencies
4. Restart the application

## 📞 Support

If you encounter persistent issues:
1. Save your `logs/rickymama.log` file
2. Export your data using the Export feature
3. Note your operating system and Python version
4. Describe the exact steps that cause the problem

---

## 🎨 Features Overview

### ✨ Key Features
- **Customer Management** with Commission/Non-Commission types
- **Color-coded tables** (Blue: Commission, Orange: Non-Commission)
- **Multiple input formats** (Pana, Time, Multiplication, Jodi)
- **Real-time data validation** and preview
- **Comprehensive reporting** with CSV exports
- **Multi-table views** (Customers, Time, Pana, Jodi, Summary)
- **Date-based filtering** and customer-specific views

### 🎯 Business Functions
- **Pana Table**: Number-value pairs with validation
- **Time Table**: Column-based time entries with totals
- **Jodi Table**: 10x10 grid with customer-specific views
- **Type Tables**: SP/DP/CP classification system
- **Customer Summary**: Bazar-wise financial summaries

Ready to get started? Follow the installation steps above! 🚀