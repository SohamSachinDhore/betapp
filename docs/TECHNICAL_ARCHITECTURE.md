# RickyMama - Technical Architecture Specification

## System Architecture Overview

### Layered Architecture Design
```
┌─────────────────────────────────────────────────────────┐
│                  Presentation Layer                    │
│              (Dear PyGui Interface)                    │
├─────────────────────────────────────────────────────────┤
│                  Business Logic Layer                  │
│         (Input Parser + Calculation Engine)            │
├─────────────────────────────────────────────────────────┤
│                  Data Access Layer                     │
│            (Database Manager + ORM)                    │
├─────────────────────────────────────────────────────────┤
│                  Data Storage Layer                    │
│         (SQLite Database + File System)                │
└─────────────────────────────────────────────────────────┘
```

## Core Components Architecture

### 1. Application Core (`app_core.py`)
```python
class RickyMamaApp:
    """Main application orchestrator"""
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.input_parser = InputParser()
        self.gui_manager = GUIManager()
        self.export_manager = ExportManager()
    
    def run(self):
        """Main application entry point"""
        pass
```

### 2. Database Management Layer

#### DatabaseManager (`database/db_manager.py`)
```python
class DatabaseManager:
    """Centralized database operations"""
    
    def __init__(self, db_path="./data/rickymama.db"):
        self.db_path = db_path
        self.connection = None
        
    def initialize_db(self):
        """Create tables and default data"""
        pass
    
    def get_connection(self):
        """Thread-safe connection management"""
        pass
    
    def execute_transaction(self, operations):
        """Atomic transaction execution"""
        pass
```

#### Data Models (`database/models.py`)
```python
@dataclass
class Customer:
    id: int
    name: str
    created_at: datetime

@dataclass
class UniversalLogEntry:
    customer_id: int
    customer_name: str
    date: date
    bazar: str
    number: int
    value: int

@dataclass
class PanaTableEntry:
    bazar: str
    date: date
    number: int
    value: int

@dataclass
class TimeTableEntry:
    customer_name: str
    bazar: str
    date: date
    columns: Dict[int, int]  # column_number: value
    total: int
```

### 3. Input Processing Layer

#### InputParser (`parsing/input_parser.py`)
```python
class InputParser:
    """Master input parser with pattern recognition"""
    
    def __init__(self):
        self.pana_parser = PanaTableParser()
        self.type_parser = TypeTableParser()
        self.time_parser = TimeTableParser()
        self.multi_parser = MultiplicationParser()
        
    def parse_input(self, input_text: str) -> List[ParsedEntry]:
        """Main parsing entry point"""
        pass
    
    def detect_pattern_type(self, line: str) -> PatternType:
        """Pattern recognition algorithm"""
        pass
```

#### Pattern-Specific Parsers
```python
class PanaTableParser:
    """Type 1: Pana table entries (128/129/120 = 100)"""
    
    SEPARATORS = ["/", "+", " ", ",", "*"]
    
    def parse(self, line: str) -> List[PanaEntry]:
        pass
    
    def validate_numbers(self, numbers: List[int]) -> bool:
        pass

class TypeTableParser:
    """Type 2: Type table queries (1SP=100)"""
    
    def parse(self, line: str) -> TypeEntry:
        pass
    
    def get_column_numbers(self, table_type: str, column: int) -> List[int]:
        pass

class TimeTableParser:
    """Type 3: Time table direct (1=100)"""
    
    def parse(self, line: str) -> TimeEntry:
        pass

class MultiplicationParser:
    """Type 4: Multiplication format (38x700)"""
    
    def parse(self, line: str) -> MultiEntry:
        pass
```

### 4. Business Logic Layer

#### CalculationEngine (`business/calculation_engine.py`)
```python
class CalculationEngine:
    """Handles all calculation logic"""
    
    def calculate_total(self, parsed_entries: List[ParsedEntry]) -> int:
        """Master total calculation"""
        pass
    
    def calculate_type1_total(self, entries: List[PanaEntry]) -> int:
        """Pattern 1: count × value"""
        pass
    
    def calculate_type2_total(self, entries: List[TypeEntry]) -> int:
        """Pattern 2: Sum of individual values"""
        pass
    
    def calculate_multiplication_total(self, entries: List[MultiEntry]) -> int:
        """Pattern 4: Sum of multiplication values"""
        pass
```

#### DataProcessor (`business/data_processor.py`)
```python
class DataProcessor:
    """Processes parsed data and updates database"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
    def process_submission(self, customer_id: int, bazar: str, 
                          date: date, parsed_entries: List[ParsedEntry]):
        """Main data processing pipeline"""
        pass
    
    def update_pana_table(self, bazar: str, date: date, entries: List[PanaEntry]):
        pass
    
    def update_time_table(self, customer_name: str, bazar: str, 
                         date: date, entries: List[TimeEntry]):
        pass
    
    def update_universal_log(self, entries: List[UniversalLogEntry]):
        pass
    
    def update_total_summary(self, customer_name: str, date: date):
        pass
```

### 5. GUI Layer

#### GUIManager (`gui/gui_manager.py`)
```python
class GUIManager:
    """Main GUI orchestrator using Dear PyGui"""
    
    def __init__(self, app_core):
        self.app_core = app_core
        self.main_window = MainWindow(self)
        self.table_viewers = {}
        
    def initialize_gui(self):
        """Setup Dear PyGui context and windows"""
        pass
    
    def run_gui(self):
        """Start GUI event loop"""
        pass
```

#### MainWindow (`gui/main_window.py`)
```python
class MainWindow:
    """Primary data entry interface"""
    
    def __init__(self, gui_manager: GUIManager):
        self.gui_manager = gui_manager
        
    def create_layout(self):
        """Build main window layout"""
        pass
    
    def setup_callbacks(self):
        """Wire up event handlers"""
        pass
    
    def on_preview_clicked(self):
        """Preview button handler"""
        pass
    
    def on_submit_clicked(self):
        """Submit button handler"""
        pass
```

#### Table Viewers (`gui/table_viewers/`)
```python
class UniversalTableViewer:
    """Universal log table display"""
    pass

class PanaTableViewer:
    """Pana table display with bazar/date filtering"""
    pass

class TimeTableViewer:
    """Time table display with customer filtering"""
    pass

class TotalSummaryViewer:
    """Customer totals by bazar"""
    pass
```

### 6. Data Export Layer

#### ExportManager (`export/export_manager.py`)
```python
class ExportManager:
    """Handles data export to CSV/Excel"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
    def export_to_csv(self, table_name: str, filename: str, filters: Dict):
        pass
    
    def export_to_excel(self, tables: List[str], filename: str, filters: Dict):
        pass
    
    def create_backup(self, backup_path: str):
        pass
```

## Data Model Relationships

### Entity Relationship Diagram
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  customers  │    │   bazars    │    │universal_log│
│             │    │             │    │             │
│ id (PK)     │    │ id (PK)     │    │ id (PK)     │
│ name        │────┼─────────────┼───→│ customer_id │
│ created_at  │    │ name        │    │ customer_nm │
└─────────────┘    │ created_at  │    │ date        │
                   └─────────────┘    │ bazar       │
                                      │ number      │
┌─────────────┐                       │ value       │
│ pana_table  │                       │ created_at  │
│             │                       └─────────────┘
│ id (PK)     │    
│ bazar       │    ┌─────────────┐
│ date        │    │ time_table  │
│ number      │    │             │
│ value       │    │ id (PK)     │
│ updated_at  │    │ customer_nm │
└─────────────┘    │ bazar       │
                   │ date        │
┌─────────────┐    │ col_1..col_0│
│total_summary│    │ total       │
│             │    │ updated_at  │
│ id (PK)     │    └─────────────┘
│ customer_nm │    
│ date        │    
│ TO_value..  │    
│ BK_value    │    
│ total       │    
│ updated_at  │    
└─────────────┘    
```

## Configuration Management

### ConfigManager (`config/config_manager.py`)
```python
class ConfigManager:
    """Application configuration management"""
    
    DEFAULT_CONFIG = {
        "database": {
            "path": "./data/rickymama.db",
            "backup_interval": 86400  # 24 hours
        },
        "gui": {
            "window_width": 1200,
            "window_height": 800,
            "theme": "default"
        },
        "export": {
            "default_path": "./exports/",
            "auto_backup": True
        },
        "validation": {
            "strict_pana_validation": True,
            "max_input_lines": 1000
        }
    }
    
    def load_config(self) -> Dict:
        pass
    
    def save_config(self, config: Dict):
        pass
```

## Error Handling Architecture

### ErrorHandler (`utils/error_handler.py`)
```python
class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self):
        self.logger = self.setup_logger()
        
    def handle_parsing_error(self, line: str, error: Exception):
        pass
    
    def handle_database_error(self, operation: str, error: Exception):
        pass
    
    def handle_gui_error(self, component: str, error: Exception):
        pass
    
    def show_user_error(self, message: str, details: str = None):
        pass
```

### Validation Framework

#### InputValidator (`validation/input_validator.py`)
```python
class InputValidator:
    """Input validation and sanitization"""
    
    def validate_customer_name(self, name: str) -> bool:
        pass
    
    def validate_date(self, date_str: str) -> bool:
        pass
    
    def validate_bazar(self, bazar: str) -> bool:
        pass
    
    def validate_number_input(self, line: str) -> ValidationResult:
        pass
    
    def sanitize_input(self, input_text: str) -> str:
        pass
```

## Performance Optimization

### Caching Strategy
```python
class CacheManager:
    """In-memory caching for frequently accessed data"""
    
    def __init__(self):
        self.pana_cache = {}
        self.type_table_cache = {}
        self.customer_cache = {}
        
    def get_pana_numbers(self) -> Set[int]:
        pass
    
    def get_type_table_column(self, table_type: str, column: int) -> List[int]:
        pass
    
    def invalidate_cache(self, cache_type: str):
        pass
```

### Database Optimization
- **Connection Pooling**: Reuse database connections
- **Prepared Statements**: Pre-compiled SQL queries
- **Batch Operations**: Bulk inserts and updates
- **Indexing Strategy**: Optimized indices for common queries

### GUI Performance
- **Lazy Loading**: Load table data on demand
- **Virtual Scrolling**: Handle large datasets efficiently
- **Async Operations**: Non-blocking database calls
- **Update Batching**: Reduce GUI refresh frequency

## Testing Architecture

### Test Structure
```
tests/
├── unit/
│   ├── test_input_parser.py
│   ├── test_calculation_engine.py
│   ├── test_database_manager.py
│   └── test_data_processor.py
├── integration/
│   ├── test_end_to_end_workflow.py
│   ├── test_database_integration.py
│   └── test_gui_integration.py
└── fixtures/
    ├── sample_data.sql
    ├── test_inputs.txt
    └── expected_outputs.json
```

### Test Data Management
```python
class TestDataFactory:
    """Generate test data for various scenarios"""
    
    @staticmethod
    def create_sample_customers() -> List[Customer]:
        pass
    
    @staticmethod
    def create_sample_input_patterns() -> List[str]:
        pass
    
    @staticmethod
    def create_expected_calculations() -> Dict:
        pass
```

## Security Architecture

### Data Security
- **Input Sanitization**: Prevent SQL injection
- **File System Security**: Restricted database access
- **Data Validation**: Type checking and bounds validation
- **Error Handling**: Secure error messages

### Application Security
- **Local-Only Operation**: No network exposure
- **File Permissions**: Restricted access to data files
- **Backup Encryption**: Optional backup encryption
- **Audit Logging**: Security event logging

## Deployment Architecture

### Application Structure
```
RickyMama/
├── main.py                 # Application entry point
├── app_core.py            # Main application class
├── config/
│   ├── settings.json      # Configuration file
│   └── config_manager.py  # Configuration management
├── database/
│   ├── db_manager.py      # Database operations
│   ├── models.py          # Data models
│   └── schema.sql         # Database schema
├── parsing/
│   ├── input_parser.py    # Main parser
│   └── pattern_parsers.py # Specific parsers
├── business/
│   ├── calculation_engine.py
│   └── data_processor.py
├── gui/
│   ├── gui_manager.py
│   ├── main_window.py
│   └── table_viewers/
├── export/
│   └── export_manager.py
├── utils/
│   ├── error_handler.py
│   └── logger.py
├── data/                  # Database files
├── exports/              # Export outputs
├── logs/                 # Application logs
└── tests/               # Test suite
```

This technical architecture provides a robust, maintainable, and scalable foundation for the RickyMama data entry system while ensuring optimal performance and reliability.