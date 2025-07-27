# RickyMama - Data Entry System Documentation

## Project Overview

RickyMama is a Python-based local data entry application designed for personal use with cross-platform compatibility (Mac/Windows). The system manages customer data, multiple bazars, and complex numeric input patterns with automatic calculations and data persistence.

### Key Features
- **Customer Management**: Unique ID system with name-ID bidirectional mapping
- **Multi-Bazar Support**: 9 default bazars (T.O, T.K, M.O, M.K, K.O, NMO, NMK, B.O, B.K) with extensibility
- **Complex Input Parsing**: 5 different input pattern types with intelligent parsing
- **Real-time Preview**: Input validation and preview before submission
- **Multiple Data Tables**: Pana, Type, Time, Universal, and Summary tables
- **Data Backup**: CSV/Excel export functionality
- **Fast GUI**: Dear PyGui for responsive user interface

## System Requirements

### Platform Support
- **macOS**: 10.14+ (Mojave or newer)
- **Windows**: 10/11 (64-bit)

### Dependencies
- Python 3.8+
- Dear PyGui (GUI framework)
- pandas (data manipulation)
- openpyxl (Excel support)
- sqlite3 (database - built-in)

## Application Architecture

### Core Components

1. **Main Entry Form** - Primary user interface
2. **Data Parser** - Input pattern recognition and processing
3. **Database Manager** - SQLite data persistence
4. **Table Viewer** - Tabbed interface for data tables
5. **Export Manager** - CSV/Excel backup functionality

### Data Flow
```
User Input → Parser → Validator → Database → Tables → Export
```

## Input Pattern Types

### Type 1: Pana Table Entries
**Format**: `128/129/120 = 100`
**Supported Separators**: `/`, `+`, ` `, `,`, `*`
**Processing**: 
- Validates numbers against pana table
- Distributes value to each number
- Updates pana table per bazar/date
- Logs to universal table

### Type 2: Type Table Queries
**Format**: `1SP=100`, `5DP=200`, `15CP=300`
**Tables**: SP (columns 1-10), DP (columns 1-10), CP (columns 11-99, 0)
**Processing**:
- Fetches all numbers from specified column
- Applies value to each number
- Updates universal table

### Type 3: Time Table Direct
**Format**: `1=100`, `0 1 3 5 = 900`
**Processing**:
- Updates time table columns for customer
- Supports multiple column selection

### Type 4: Time Table Multiplication
**Format**: `38x700`, `83x700`
**Processing**:
- Extracts tens digit as column identifier
- Adds value to customer's time table column

### Type 5: Mixed Input
**Processing**: Intelligently detects and processes multiple pattern types in single input

## Database Schema

### Tables Structure

#### customers
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT UNIQUE)
- `created_at` (TIMESTAMP)

#### bazars
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT UNIQUE)
- `created_at` (TIMESTAMP)

#### universal_log
- `id` (INTEGER PRIMARY KEY)
- `customer_id` (INTEGER)
- `customer_name` (TEXT)
- `date` (DATE)
- `bazar` (TEXT)
- `number` (INTEGER)
- `value` (INTEGER)
- `created_at` (TIMESTAMP)

#### pana_table
- `id` (INTEGER PRIMARY KEY)
- `bazar` (TEXT)
- `date` (DATE)
- `number` (INTEGER)
- `value` (INTEGER)
- `updated_at` (TIMESTAMP)

#### time_table
- `id` (INTEGER PRIMARY KEY)
- `customer_name` (TEXT)
- `bazar` (TEXT)
- `date` (DATE)
- `col_1` through `col_0` (INTEGER)
- `total` (INTEGER)
- `updated_at` (TIMESTAMP)

#### total_summary
- `id` (INTEGER PRIMARY KEY)
- `customer_name` (TEXT)
- `date` (DATE)
- `TO_value`, `TK_value`, `MO_value`, `MK_value`, `KO_value`, `KK_value`, `NMO_value`, `NMK_value`, `BO_value`, `BK_value` (INTEGER)
- `total` (INTEGER)
- `updated_at` (TIMESTAMP)

## Business Logic

### Calculation Rules

#### Total Calculation Logic
1. **Pattern Type 1** (Space-separated): `count × value`
   - `6 8 9 0 = 3300` → `4 × 3300 = 13,200`

2. **Pattern Type 1** (Multi-line): `line_count × value`
   - 20 numbers = 260 → `20 × 260 = 5,200`

3. **Direct Assignment**: Sum of individual values
   - `124=400, 147=250` → `400 + 250 = 650`

4. **Multiplication Pattern**: Sum of all values
   - `38x700, 83x700` → `700 + 700 = 1,400`

### Value Extraction
- Supports currency indicators: `Rs`, `R`, `Rs.`, `Rs..`
- Extracts numeric value after `=` sign
- Handles whitespace variations

## GUI Design Specifications

### Main Window Layout
```
┌─────────────────────────────────────────────────────────┐
│ RickyMama Data Entry System                             │
├─────────────────────────────────────────────────────────┤
│ Customer: [Dropdown ▼] | ID: [Text Field]              │
│ Date: [DD-MM-YYYY] | Bazar: [Dropdown ▼]               │
│                                                         │
│ Input Field: [Multi-line Text Area]                    │
│                                                         │
│ Preview: [Read-only Text Area]                         │
│                                                         │
│ Total: [Calculated Value]                              │
│                                                         │
│ [Preview] [Submit] [Clear]                             │
├─────────────────────────────────────────────────────────┤
│ Tabs: [Customers][Universal][Pana][Time][Total][Export] │
└─────────────────────────────────────────────────────────┘
```

### Table Views
- **Responsive Design**: Auto-fit to window size
- **Sortable Columns**: Click headers to sort
- **Filter Options**: Date range, customer, bazar filters
- **Export Integration**: Direct export from table views

## Error Handling

### Input Validation
- **Number Validation**: Check against pana table for valid entries
- **Format Validation**: Regex patterns for each input type
- **Value Validation**: Positive integers only
- **Date Validation**: Valid date format and range

### Error Recovery
- **Parse Errors**: Highlight problematic lines
- **Database Errors**: Transaction rollback
- **GUI Errors**: User-friendly error messages
- **File Errors**: Backup creation failure handling

## Data Backup Strategy

### Export Formats
- **CSV**: Universal compatibility
- **Excel**: Advanced formatting and formulas
- **SQLite**: Complete database backup

### Backup Schedule
- **Manual**: User-initiated export
- **Automatic**: Daily backup (optional)
- **Version Control**: Timestamped backups

## Security Considerations

### Data Protection
- **Local Storage**: No network transmission
- **File Permissions**: Restricted database access
- **Input Sanitization**: SQL injection prevention
- **Data Validation**: Type checking and bounds validation

## Performance Optimization

### GUI Responsiveness
- **Async Operations**: Non-blocking database operations
- **Lazy Loading**: Load tables on demand
- **Efficient Rendering**: Dear PyGui optimization
- **Memory Management**: Regular cleanup of large datasets

### Database Performance
- **Indexing**: Key columns indexed
- **Query Optimization**: Prepared statements
- **Transaction Management**: Batch operations
- **Connection Pooling**: Efficient database connections

## Testing Strategy

### Unit Tests
- Input parser validation
- Calculation logic verification
- Database operations testing
- Export functionality testing

### Integration Tests
- End-to-end workflow testing
- GUI interaction testing
- Cross-platform compatibility testing
- Data integrity verification

### User Acceptance Testing
- Non-technical user workflow testing
- Error scenario handling
- Performance benchmarking
- Usability assessment

## Deployment Guide

### Installation Steps
1. Install Python 3.8+
2. Install required packages: `pip install dearpygui pandas openpyxl`
3. Initialize database schema
4. Configure default bazars and customers
5. Launch application

### Configuration
- Database location: `./data/rickymama.db`
- Export directory: `./exports/`
- Log files: `./logs/`
- Configuration file: `./config/settings.json`

## Maintenance

### Regular Tasks
- Database backup verification
- Log file rotation
- Performance monitoring
- User feedback collection

### Updates
- Bug fixes and patches
- Feature enhancements
- Compatibility updates
- Security updates

## Support Documentation

### User Manual
- Getting started guide
- Feature tutorials
- Troubleshooting guide
- FAQ section

### Technical Documentation
- API reference
- Database schema
- Code structure
- Development setup

---

*This documentation serves as the complete specification for the RickyMama data entry system implementation.*