# RickyMama - Implementation Guide & Technical Specifications

## Implementation Overview

This guide provides step-by-step instructions for implementing the RickyMama data entry system, including development environment setup, coding standards, testing procedures, and deployment instructions.

## Development Environment Setup

### Prerequisites
```bash
# Python 3.8+ required
python --version  # Should be 3.8 or higher

# Operating System Requirements
# Windows: 10/11 (64-bit)
# macOS: 10.14+ (Mojave or newer)
```

### Installation Steps

#### 1. Project Setup
```bash
# Create project directory
mkdir RickyMama
cd RickyMama

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Create project structure
mkdir -p {src,tests,data,exports,logs,config,docs}
mkdir -p src/{database,parsing,business,gui,export,utils}
mkdir -p src/gui/table_viewers
mkdir -p tests/{unit,integration,fixtures}
```

#### 2. Dependencies Installation
```bash
# Install required packages
pip install dearpygui==1.10.1
pip install pandas==2.1.4
pip install openpyxl==3.1.2
pip install pytest==7.4.3
pip install pytest-cov==4.1.0
pip install black==23.12.0
pip install flake8==6.1.0

# Create requirements.txt
pip freeze > requirements.txt
```

#### 3. Configuration Files

**requirements.txt**
```
dearpygui==1.10.1
pandas==2.1.4
openpyxl==3.1.2
pytest==7.4.3
pytest-cov==4.1.0
black==23.12.0
flake8==6.1.0
```

**config/settings.json**
```json
{
  "database": {
    "path": "./data/rickymama.db",
    "backup_interval": 86400,
    "max_connections": 5
  },
  "gui": {
    "window_width": 1200,
    "window_height": 800,
    "theme": "default",
    "auto_save_interval": 300
  },
  "export": {
    "default_path": "./exports/",
    "auto_backup": true,
    "max_export_rows": 100000
  },
  "validation": {
    "strict_pana_validation": true,
    "max_input_lines": 1000,
    "timeout_seconds": 30
  },
  "logging": {
    "level": "INFO",
    "file_path": "./logs/rickymama.log",
    "max_file_size": "10MB",
    "backup_count": 5
  }
}
```

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)

#### 1.1 Database Layer Implementation
```python
# src/database/db_manager.py
import sqlite3
import threading
from contextlib import contextmanager
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, date

class DatabaseManager:
    """Centralized database operations with connection pooling"""
    
    def __init__(self, db_path: str = "./data/rickymama.db"):
        self.db_path = db_path
        self.local = threading.local()
        self.lock = threading.Lock()
        self.initialize_database()
    
    def get_connection(self):
        """Thread-safe connection management"""
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self.local.connection.execute("PRAGMA foreign_keys = ON")
            self.local.connection.execute("PRAGMA journal_mode = WAL")
        return self.local.connection
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def initialize_database(self):
        """Create all tables and initial data"""
        with open('src/database/schema.sql', 'r') as f:
            schema_sql = f.read()
        
        with self.transaction() as conn:
            conn.executescript(schema_sql)
```

#### 1.2 Configuration Management
```python
# src/config/config_manager.py
import json
import os
from typing import Dict, Any

class ConfigManager:
    """Application configuration management"""
    
    def __init__(self, config_path: str = "./config/settings.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "database": {"path": "./data/rickymama.db"},
            "gui": {"window_width": 1200, "window_height": 800},
            "export": {"default_path": "./exports/"},
            "validation": {"strict_pana_validation": True}
        }
    
    def get(self, key: str, default=None):
        """Get configuration value with dot notation support"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
```

#### 1.3 Logging System
```python
# src/utils/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler

class LoggerSetup:
    """Centralized logging configuration"""
    
    @staticmethod
    def setup_logger(name: str, config: dict) -> logging.Logger:
        """Setup logger with file and console handlers"""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.get('level', 'INFO')))
        
        # Ensure log directory exists
        log_file = config.get('file_path', './logs/rickymama.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
```

### Phase 2: Input Parsing System (Week 2-3)

#### 2.1 Pattern Detection Engine
```python
# src/parsing/pattern_detector.py
import re
from enum import Enum
from typing import List, Tuple

class PatternType(Enum):
    PANA_TABLE = "pana_table"
    TYPE_TABLE = "type_table"
    TIME_DIRECT = "time_direct"
    TIME_MULTIPLY = "time_multiply"
    MIXED = "mixed"
    UNKNOWN = "unknown"

class PatternDetector:
    """Intelligent pattern recognition for input classification"""
    
    PATTERNS = {
        PatternType.TYPE_TABLE: r'(\d+)(SP|DP|CP)\s*=\s*\d+',
        PatternType.TIME_MULTIPLY: r'(\d{2})x(\d+)',
        PatternType.PANA_TABLE: r'(\d{3}[\/\+\s\,\*]+.*=.*\d+)',
        PatternType.TIME_DIRECT: r'^([\d\s]+)\s*=\s*\d+$',
    }
    
    def detect_pattern_type(self, line: str) -> PatternType:
        """
        Detect pattern type with priority ordering
        1. TYPE_TABLE (highest specificity)
        2. TIME_MULTIPLY (specific format)
        3. PANA_TABLE (complex separators)
        4. TIME_DIRECT (simple format)
        """
        line = line.strip()
        
        for pattern_type, regex in self.PATTERNS.items():
            if re.search(regex, line, re.IGNORECASE):
                return pattern_type
        
        return PatternType.UNKNOWN
    
    def analyze_input(self, input_text: str) -> Tuple[PatternType, List[PatternType]]:
        """Analyze entire input and return overall type and line types"""
        lines = [line.strip() for line in input_text.strip().split('\n') if line.strip()]
        line_types = []
        
        for line in lines:
            line_type = self.detect_pattern_type(line)
            line_types.append(line_type)
        
        # Determine overall pattern type
        unique_types = set(line_types)
        unique_types.discard(PatternType.UNKNOWN)
        
        if len(unique_types) == 0:
            return PatternType.UNKNOWN, line_types
        elif len(unique_types) == 1:
            return list(unique_types)[0], line_types
        else:
            return PatternType.MIXED, line_types
```

#### 2.2 Master Input Parser
```python
# src/parsing/input_parser.py
from typing import List, Dict, Any
from dataclasses import dataclass, field
from .pattern_detector import PatternDetector, PatternType
from .pattern_parsers import PanaTableParser, TypeTableParser, TimeTableParser, MultiplicationParser

@dataclass
class ParsedInputResult:
    """Result of input parsing operation"""
    pana_entries: List[Any] = field(default_factory=list)
    type_entries: List[Any] = field(default_factory=list)
    time_entries: List[Any] = field(default_factory=list)
    multi_entries: List[Any] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class InputParser:
    """Master input parser with pattern recognition"""
    
    def __init__(self, reference_data: Dict[str, Any]):
        self.pattern_detector = PatternDetector()
        self.pana_parser = PanaTableParser(reference_data['pana_numbers'])
        self.type_parser = TypeTableParser(reference_data['type_tables'])
        self.time_parser = TimeTableParser()
        self.multi_parser = MultiplicationParser()
    
    def parse(self, input_text: str) -> ParsedInputResult:
        """Main parsing entry point"""
        if not input_text.strip():
            raise ValueError("Input cannot be empty")
        
        result = ParsedInputResult()
        
        # Detect overall pattern
        overall_type, line_types = self.pattern_detector.analyze_input(input_text)
        
        if overall_type == PatternType.MIXED:
            return self._parse_mixed_input(input_text, result)
        else:
            return self._parse_single_type_input(input_text, overall_type, result)
    
    def _parse_mixed_input(self, input_text: str, result: ParsedInputResult) -> ParsedInputResult:
        """Parse input containing multiple pattern types"""
        lines = [line.strip() for line in input_text.strip().split('\n') if line.strip()]
        
        for line in lines:
            try:
                pattern_type = self.pattern_detector.detect_pattern_type(line)
                
                if pattern_type == PatternType.PANA_TABLE:
                    entries = self.pana_parser.parse(line)
                    result.pana_entries.extend(entries)
                    
                elif pattern_type == PatternType.TYPE_TABLE:
                    entry = self.type_parser.parse(line)
                    result.type_entries.append(entry)
                    
                elif pattern_type == PatternType.TIME_DIRECT:
                    entry = self.time_parser.parse(line)
                    result.time_entries.append(entry)
                    
                elif pattern_type == PatternType.TIME_MULTIPLY:
                    entry = self.multi_parser.parse(line)
                    result.multi_entries.append(entry)
                    
                else:
                    result.errors.append({
                        'line': line,
                        'error': f'Unknown pattern type: {pattern_type}'
                    })
                    
            except Exception as e:
                result.errors.append({
                    'line': line,
                    'error': str(e)
                })
        
        return result
```

### Phase 3: Business Logic Implementation (Week 3-4)

#### 3.1 Calculation Engine
```python
# src/business/calculation_engine.py
from typing import List, Dict, Any
from dataclasses import dataclass
from ..parsing.input_parser import ParsedInputResult

@dataclass
class CalculationResult:
    """Result of calculation operations"""
    pana_total: int = 0
    type_total: int = 0
    time_total: int = 0
    multi_total: int = 0
    grand_total: int = 0
    calculation_details: Dict[str, Any] = None

class CalculationEngine:
    """Master calculation engine for all input types"""
    
    def calculate_total(self, parsed_result: ParsedInputResult) -> CalculationResult:
        """Calculate total from parsed input"""
        result = CalculationResult()
        
        # Calculate each type
        result.pana_total = self._calculate_pana_total(parsed_result.pana_entries)
        result.type_total = self._calculate_type_total(parsed_result.type_entries)
        result.time_total = self._calculate_time_total(parsed_result.time_entries)
        result.multi_total = self._calculate_multi_total(parsed_result.multi_entries)
        
        # Calculate grand total
        result.grand_total = (
            result.pana_total + 
            result.type_total + 
            result.time_total + 
            result.multi_total
        )
        
        # Store calculation details
        result.calculation_details = {
            'pana_count': len(parsed_result.pana_entries),
            'type_count': len(parsed_result.type_entries),
            'time_count': len(parsed_result.time_entries),
            'multi_count': len(parsed_result.multi_entries)
        }
        
        return result
    
    def _calculate_pana_total(self, entries: List[Any]) -> int:
        """Calculate pana table total (count × value logic)"""
        if not entries:
            return 0
        
        # Group by value for correct calculation
        value_groups = {}
        for entry in entries:
            value = entry.value
            if value not in value_groups:
                value_groups[value] = 0
            value_groups[value] += 1
        
        total = 0
        for value, count in value_groups.items():
            total += count * value
        
        return total
    
    def _calculate_type_total(self, entries: List[Any]) -> int:
        """Calculate type table total (expansion logic)"""
        total = 0
        for entry in entries:
            # Each number in column gets the value
            numbers_count = len(entry.numbers)
            total += numbers_count * entry.value
        return total
    
    def _calculate_time_total(self, entries: List[Any]) -> int:
        """Calculate time table total (direct sum)"""
        return sum(entry.value for entry in entries)
    
    def _calculate_multi_total(self, entries: List[Any]) -> int:
        """Calculate multiplication total (direct sum)"""
        return sum(entry.value for entry in entries)
```

#### 3.2 Data Processing Pipeline
```python
# src/business/data_processor.py
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, date
from ..database.db_manager import DatabaseManager
from .calculation_engine import CalculationEngine, CalculationResult

@dataclass
class EntrySubmission:
    """Data submission structure"""
    customer_id: int
    customer_name: str
    bazar: str
    date: date
    input_text: str
    expected_total: int
    parsed_result: Any = None
    calc_result: CalculationResult = None

@dataclass
class ProcessingResult:
    """Result of data processing"""
    success: bool
    total: int = 0
    error: str = None
    warnings: List[str] = None

class DataProcessor:
    """Master data processing orchestrator"""
    
    def __init__(self, db_manager: DatabaseManager, calc_engine: CalculationEngine):
        self.db_manager = db_manager
        self.calc_engine = calc_engine
    
    def process_submission(self, submission: EntrySubmission) -> ProcessingResult:
        """Main data processing pipeline"""
        try:
            # Validate submission
            validation_result = self._validate_submission(submission)
            if not validation_result.success:
                return validation_result
            
            # Process with database transaction
            with self.db_manager.transaction() as conn:
                # Insert universal log entries
                self._insert_universal_log_entries(submission, conn)
                
                # Update specific tables
                self._update_pana_table(submission, conn)
                self._update_time_table(submission, conn)
                self._update_customer_summary(submission, conn)
            
            return ProcessingResult(
                success=True,
                total=submission.calc_result.grand_total
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error=str(e)
            )
    
    def _validate_submission(self, submission: EntrySubmission) -> ProcessingResult:
        """Validate submission data"""
        # Check if calculated total matches expected
        if submission.calc_result.grand_total != submission.expected_total:
            return ProcessingResult(
                success=False,
                error=f"Calculated total {submission.calc_result.grand_total} "
                      f"doesn't match expected {submission.expected_total}"
            )
        
        # Validate customer exists
        if not self._customer_exists(submission.customer_id):
            return ProcessingResult(
                success=False,
                error=f"Customer ID {submission.customer_id} not found"
            )
        
        return ProcessingResult(success=True)
    
    def _insert_universal_log_entries(self, submission: EntrySubmission, conn):
        """Insert entries into universal log"""
        # Implementation for universal log insertion
        pass
    
    def _update_pana_table(self, submission: EntrySubmission, conn):
        """Update pana table with new entries"""
        # Implementation for pana table updates
        pass
    
    def _update_time_table(self, submission: EntrySubmission, conn):
        """Update time table with new entries"""
        # Implementation for time table updates
        pass
    
    def _update_customer_summary(self, submission: EntrySubmission, conn):
        """Update customer summary table"""
        # Implementation for summary updates
        pass
```

### Phase 4: GUI Implementation (Week 4-6)

#### 4.1 Main Application Setup
```python
# src/main.py
import dearpygui.dearpygui as dpg
from src.config.config_manager import ConfigManager
from src.database.db_manager import DatabaseManager
from src.gui.gui_manager import GUIManager
from src.utils.logger import LoggerSetup
import sys
import os

class RickyMamaApp:
    """Main application class"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.logger = LoggerSetup.setup_logger('RickyMama', self.config.get('logging', {}))
        
        # Initialize core components
        self.db_manager = DatabaseManager(self.config.get('database.path'))
        self.gui_manager = GUIManager(self)
        
        self.logger.info("RickyMama application initialized")
    
    def run(self):
        """Start the application"""
        try:
            self.logger.info("Starting RickyMama application")
            
            # Setup Dear PyGui
            dpg.create_context()
            
            # Initialize GUI
            self.gui_manager.initialize_gui()
            
            # Setup viewport
            dpg.create_viewport(
                title="RickyMama Data Entry System",
                width=self.config.get('gui.window_width', 1200),
                height=self.config.get('gui.window_height', 800),
                min_width=1000,
                min_height=600
            )
            
            dpg.setup_dearpygui()
            dpg.show_viewport()
            
            # Main loop
            while dpg.is_dearpygui_running():
                dpg.render_dearpygui_frame()
            
        except Exception as e:
            self.logger.error(f"Application error: {str(e)}")
            raise
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up application resources")
        dpg.destroy_context()

if __name__ == "__main__":
    app = RickyMamaApp()
    app.run()
```

#### 4.2 GUI Manager Implementation
```python
# src/gui/gui_manager.py
import dearpygui.dearpygui as dpg
from .main_window import MainWindow
from .table_viewers.table_view_manager import TableViewManager
from .dialogs.dialog_manager import DialogManager

class GUIManager:
    """Main GUI orchestrator"""
    
    def __init__(self, app):
        self.app = app
        self.main_window = None
        self.table_manager = None
        self.dialog_manager = None
    
    def initialize_gui(self):
        """Setup Dear PyGui interface"""
        # Setup theme
        self._setup_theme()
        
        # Create main window
        self.main_window = MainWindow(self)
        self.main_window.create_window()
        
        # Create table manager
        self.table_manager = TableViewManager(self)
        
        # Create dialog manager
        self.dialog_manager = DialogManager(self)
        
        # Set primary window
        dpg.set_primary_window("main_window", True)
    
    def _setup_theme(self):
        """Setup application theme"""
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 4)
                
                # Colors
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (248, 249, 250, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (41, 128, 185, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (52, 152, 219, 255))
        
        dpg.bind_theme(theme)
```

### Phase 5: Testing Implementation (Week 6-7)

#### 5.1 Unit Test Setup
```python
# tests/unit/test_calculation_engine.py
import pytest
from src.business.calculation_engine import CalculationEngine
from src.parsing.input_parser import ParsedInputResult
from tests.fixtures.test_data import TestDataFactory

class TestCalculationEngine:
    """Unit tests for calculation engine"""
    
    def setup_method(self):
        """Setup for each test"""
        self.calc_engine = CalculationEngine()
        self.test_data = TestDataFactory()
    
    def test_pana_calculation_single_value(self):
        """Test pana calculation with single value"""
        # Create test entries
        pana_entries = self.test_data.create_pana_entries([
            (128, 100), (129, 100), (120, 100)
        ])
        
        parsed_result = ParsedInputResult(pana_entries=pana_entries)
        result = self.calc_engine.calculate_total(parsed_result)
        
        # Should be 3 numbers × 100 = 300
        assert result.pana_total == 300
        assert result.grand_total == 300
    
    def test_mixed_input_calculation(self):
        """Test calculation with mixed input types"""
        # Create mixed entries
        parsed_result = ParsedInputResult(
            pana_entries=self.test_data.create_pana_entries([(128, 100)]),
            time_entries=self.test_data.create_time_entries([(1, 200)]),
            multi_entries=self.test_data.create_multi_entries([("38", 300)])
        )
        
        result = self.calc_engine.calculate_total(parsed_result)
        
        # Should be 100 + 200 + 300 = 600
        assert result.grand_total == 600
        assert result.pana_total == 100
        assert result.time_total == 200
        assert result.multi_total == 300

# tests/fixtures/test_data.py
class TestDataFactory:
    """Factory for creating test data"""
    
    def create_pana_entries(self, data):
        """Create pana entries from tuple list"""
        from src.parsing.pattern_parsers import PanaEntry
        return [PanaEntry(number=num, value=val) for num, val in data]
    
    def create_time_entries(self, data):
        """Create time entries from tuple list"""
        from src.parsing.pattern_parsers import TimeEntry
        return [TimeEntry(columns=[col], value=val) for col, val in data]
    
    def create_multi_entries(self, data):
        """Create multiplication entries from tuple list"""
        from src.parsing.pattern_parsers import MultiEntry
        entries = []
        for num_str, val in data:
            tens = int(num_str[0])
            units = int(num_str[1])
            entries.append(MultiEntry(
                number=int(num_str),
                tens_digit=tens,
                units_digit=units,
                value=val
            ))
        return entries
```

#### 5.2 Integration Tests
```python
# tests/integration/test_end_to_end_workflow.py
import pytest
import tempfile
import os
from src.database.db_manager import DatabaseManager
from src.business.data_processor import DataProcessor, EntrySubmission
from src.business.calculation_engine import CalculationEngine
from src.parsing.input_parser import InputParser

class TestEndToEndWorkflow:
    """Integration tests for complete workflow"""
    
    def setup_method(self):
        """Setup test database and components"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Initialize components
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.calc_engine = CalculationEngine()
        self.data_processor = DataProcessor(self.db_manager, self.calc_engine)
        
        # Setup test data
        self._setup_test_customers()
    
    def teardown_method(self):
        """Cleanup test database"""
        os.unlink(self.temp_db.name)
    
    def test_complete_pana_entry_workflow(self):
        """Test complete workflow for pana entry"""
        # Create submission
        submission = EntrySubmission(
            customer_id=1,
            customer_name="Test Customer",
            bazar="T.O",
            date=datetime.date.today(),
            input_text="128/129/120 = 100",
            expected_total=300
        )
        
        # Parse input
        reference_data = self._get_reference_data()
        parser = InputParser(reference_data)
        submission.parsed_result = parser.parse(submission.input_text)
        
        # Calculate total
        submission.calc_result = self.calc_engine.calculate_total(submission.parsed_result)
        
        # Process submission
        result = self.data_processor.process_submission(submission)
        
        assert result.success
        assert result.total == 300
        
        # Verify database state
        self._verify_database_state(submission)
```

### Phase 6: Deployment and Distribution (Week 7-8)

#### 6.1 Build Script
```python
# build.py
import os
import shutil
import subprocess
import sys
from pathlib import Path

class BuildManager:
    """Handles application building and packaging"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
    
    def clean_build(self):
        """Clean previous build artifacts"""
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
    
    def run_tests(self):
        """Run test suite"""
        print("Running tests...")
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", "-v", "--cov=src"
        ], cwd=self.project_root)
        
        if result.returncode != 0:
            raise RuntimeError("Tests failed")
    
    def build_executable(self):
        """Build standalone executable"""
        print("Building executable...")
        
        # Use PyInstaller for packaging
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", "RickyMama",
            "--add-data", "config;config",
            "--add-data", "src/database/schema.sql;database",
            "src/main.py"
        ], cwd=self.project_root, check=True)
    
    def create_installer(self):
        """Create installation package"""
        print("Creating installer...")
        
        # Create installer directory structure
        installer_dir = self.dist_dir / "installer"
        installer_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy executable
        shutil.copy2(
            self.dist_dir / "RickyMama.exe",
            installer_dir / "RickyMama.exe"
        )
        
        # Copy configuration files
        shutil.copytree(
            self.project_root / "config",
            installer_dir / "config"
        )
        
        # Create directories
        for dir_name in ["data", "exports", "logs"]:
            (installer_dir / dir_name).mkdir(exist_ok=True)
        
        # Create install script
        self._create_install_script(installer_dir)
    
    def _create_install_script(self, installer_dir):
        """Create installation script"""
        install_script = installer_dir / "install.bat"
        
        with open(install_script, 'w') as f:
            f.write("""
@echo off
echo Installing RickyMama Data Entry System...

REM Create application directory
if not exist "%USERPROFILE%\\RickyMama" mkdir "%USERPROFILE%\\RickyMama"

REM Copy files
xcopy /E /I /Y * "%USERPROFILE%\\RickyMama\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\RickyMama.lnk'); $Shortcut.TargetPath = '%USERPROFILE%\\RickyMama\\RickyMama.exe'; $Shortcut.Save()"

echo Installation complete!
echo You can now run RickyMama from your desktop or from %USERPROFILE%\\RickyMama\\
pause
            """)

if __name__ == "__main__":
    builder = BuildManager()
    
    try:
        builder.clean_build()
        builder.run_tests()
        builder.build_executable()
        builder.create_installer()
        print("Build completed successfully!")
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)
```

## Development Guidelines

### Code Style Standards
```python
# .flake8
[flake8]
max-line-length = 100
exclude = venv,build,dist,__pycache__
ignore = E203,W503

# pyproject.toml (for Black)
[tool.black]
line-length = 100
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  venv
  | build
  | dist
)/
'''
```

### Git Workflow
```bash
# .gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
venv/
env/

# Application specific
data/*.db
data/*.db-*
exports/*.csv
exports/*.xlsx
logs/*.log

# Build artifacts
build/
dist/
*.spec

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### Testing Strategy
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test category
pytest tests/unit/ -v
pytest tests/integration/ -v

# Run performance tests
pytest tests/performance/ -v --benchmark-only
```

## Deployment Instructions

### Local Development Deployment
```bash
# 1. Clone repository
git clone <repository-url>
cd RickyMama

# 2. Setup environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 3. Initialize database
python -c "from src.database.db_manager import DatabaseManager; DatabaseManager().initialize_database()"

# 4. Run application
python src/main.py
```

### Production Deployment
```bash
# 1. Run build script
python build.py

# 2. Test executable
./dist/RickyMama.exe

# 3. Create distribution package
cd dist/installer
zip -r RickyMama-v1.0.zip *

# 4. Distribute to users
# Users run install.bat from extracted zip
```

### User Installation Guide
```markdown
# RickyMama Installation Guide

## System Requirements
- Windows 10/11 (64-bit) OR macOS 10.14+
- 2GB free disk space
- 4GB RAM minimum

## Installation Steps
1. Download RickyMama-v1.0.zip
2. Extract to temporary folder
3. Run install.bat as Administrator (Windows) or install.sh (macOS)
4. Launch from desktop shortcut or start menu

## First Run Setup
1. Application will create initial database
2. Add your customers and bazars
3. Start entering data!

## Backup Recommendations
- Enable auto-backup in settings
- Export data weekly to CSV/Excel
- Keep database backups in separate location
```

This implementation guide provides a complete roadmap for developing the RickyMama system with proper architecture, testing, and deployment procedures.