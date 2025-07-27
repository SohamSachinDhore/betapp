# RickyMama - Data Entry System

A comprehensive data entry and management system for betting/lottery operations with advanced parsing capabilities and real-time calculations.

## 🚀 Features

### Core Functionality
- **Smart Input Parsing**: Supports multiple input formats (PANA, TYPE, TIME, MULTI, DIRECT)
- **Real-time Validation**: Live preview and validation of entered data
- **Automatic Calculations**: Intelligent calculation engine with type-specific logic
- **Database Integration**: SQLite database with automatic triggers and data integrity

### Input Pattern Types

#### 1. PANA Table Entries
- **Format**: `128/129/120 = 100`
- **Separators**: `/`, `+`, ` `, `,`, `*`
- **Description**: Direct number assignments to pana table

#### 2. TYPE Table Queries  
- **Format**: `1SP=100`, `5DP=200`, `15CP=300`
- **Tables**: SP (columns 1-10), DP (columns 1-10), CP (columns 11-99, 0)
- **Description**: Applies values to all numbers in specified table columns

#### 3. TIME Table Direct
- **Format**: `1=100`, `0 1 3 5 = 900`
- **Description**: Direct column assignments in time table

#### 4. Multiplication Entries
- **Format**: `38x700`, `83x500`
- **Description**: Applies values to tens and units digit positions

#### 5. Direct Number Assignment
- **Format**: `128=500`, `347=300`
- **Description**: Direct value assignment to specific numbers

### GUI Features
- **Live Preview**: Real-time parsing and calculation preview
- **Customer Management**: Add and manage customers
- **Bazar Selection**: Multiple bazar support
- **Date Selection**: Calendar-based date picker
- **Data Tables**: Comprehensive table views for all data
- **Export Functionality**: CSV and Excel export capabilities

## 📁 Project Structure

```
RickyMama/
├── src/
│   ├── business/           # Business logic and calculations
│   ├── database/          # Database management and models
│   ├── parsing/           # Input parsing engines
│   ├── utils/             # Utilities and helpers
│   └── export/            # Data export functionality
├── data/                  # Database files
├── config/                # Configuration files
├── docs/                  # Documentation
├── exports/               # Export output directory
├── logs/                  # Application logs
└── main_gui_working.py    # Main GUI application
```

## 🛠️ Technology Stack

- **Language**: Python 3.11+
- **GUI Framework**: Dear PyGui
- **Database**: SQLite 3.x
- **Architecture**: Modular, component-based design

## 📊 Database Schema

### Core Tables
- **customers**: Customer information
- **bazars**: Bazar/market definitions
- **universal_log**: All entry transactions
- **pana_table**: Aggregated pana values by date/bazar
- **time_table**: Time-based entries by customer
- **customer_bazar_summary**: Daily summaries by customer/bazar

### Reference Tables
- **type_table_sp/dp/cp**: Type table definitions
- **pana_numbers**: Valid pana number references

## 🚀 Getting Started

### Prerequisites
```bash
python 3.11+
pip install -r requirements.txt
```

### Installation
```bash
git clone https://github.com/SohamSachinDhore/betapp.git
cd betapp
pip install -r requirements.txt
```

### Running the Application
```bash
python main_gui_working.py
```

## 📖 Usage Examples

### Basic Input Examples
```
# PANA entries
128/129/120 = 100
138+347+230 = 400

# TYPE entries  
1SP=50
5DP=100
15CP=200

# TIME entries
1=100
0 1 3 5 = 900

# MULTI entries
38x700
83x500

# Mixed input
138+347+230 = 400
1SP=50
7=80
```

## 🧪 Testing

The project includes comprehensive test suites:

```bash
# Test type parsing
python test_type_parsing_flow.py

# Test complete flow
python test_complete_type_flow.py

# Debug type values
python debug_type_values.py
```

## 📈 Key Features

### Intelligent Parsing
- **Pattern Detection**: Automatically detects input pattern types
- **Mixed Input Support**: Handles multiple pattern types in single input
- **Error Handling**: Comprehensive validation and error reporting
- **Currency Support**: Handles Rs, Rs., R currency indicators

### Advanced Calculations
- **Type Expansion**: Expands TYPE entries to individual pana numbers
- **Accumulation Logic**: Automatic value accumulation for duplicate numbers
- **Business Rules**: Implements complex business logic for different entry types
- **Real-time Totals**: Live calculation updates

### Data Management
- **Transaction Safety**: ACID compliance with SQLite transactions
- **Automatic Triggers**: Database triggers for data consistency
- **Backup Support**: Built-in backup and restore functionality
- **Export Options**: Multiple export formats (CSV, Excel)

## 🔧 Configuration

Configuration is managed through `config/settings.json`:

```json
{
  "database": {
    "path": "./data/rickymama.db",
    "backup_interval": 86400
  },
  "gui": {
    "window_width": 1200,
    "window_height": 800
  }
}
```

## 📝 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **Technical Architecture**: System design and component interactions
- **Database Schema**: Complete database documentation
- **Input Parsing Specification**: Detailed parsing rules and examples
- **Business Logic Specification**: Business rules and calculations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For support and questions, please open an issue on GitHub.

---

**Built with ❤️ for efficient data management and business operations**
