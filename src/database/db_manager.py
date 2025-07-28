"""Database Manager with SQLite connection pooling and transaction management"""

import sqlite3
import threading
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Tuple
import os
import logging

class DatabaseManager:
    """Centralized database operations with connection pooling"""
    
    def __init__(self, db_path: str = "./data/rickymama.db"):
        self.db_path = db_path
        self.local = threading.local()
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Ensure database directory exists (skip for in-memory DB)
        if self.db_path != ":memory:" and os.path.dirname(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Thread-safe connection management"""
        if not hasattr(self.local, 'connection') or self.local.connection is None:
            self.local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            # Enable foreign keys and optimizations
            self.local.connection.execute("PRAGMA foreign_keys = ON")
            self.local.connection.execute("PRAGMA journal_mode = WAL")
            self.local.connection.execute("PRAGMA synchronous = NORMAL")
            self.local.connection.execute("PRAGMA cache_size = 10240")
            
            # Set row factory for dict-like access
            self.local.connection.row_factory = sqlite3.Row
            
        return self.local.connection
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Transaction failed: {e}")
            raise
    
    def initialize_database(self):
        """Create all tables and initial data"""
        # Check if database already exists and has tables
        if self._database_exists():
            self.logger.info("Database already exists, skipping initialization")
            return
        
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        # Check if schema file exists
        if not os.path.exists(schema_path):
            self.logger.warning(f"Schema file not found at {schema_path}, creating basic schema")
            self.create_basic_schema()
            return
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        with self.transaction() as conn:
            conn.executescript(schema_sql)
            self.logger.info("Database initialized successfully")
    
    def _database_exists(self) -> bool:
        """Check if database exists and has tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
            result = cursor.fetchone()
            return result is not None
        except Exception:
            return False
    
    def create_basic_schema(self):
        """Create basic schema if schema.sql is not available"""
        basic_schema = """
        -- Create customers table
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        );
        
        -- Create bazars table
        CREATE TABLE IF NOT EXISTS bazars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            display_name TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        );
        
        -- Create universal_log table
        CREATE TABLE IF NOT EXISTS universal_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            entry_date DATE NOT NULL,
            bazar TEXT NOT NULL,
            number INTEGER NOT NULL,
            value INTEGER NOT NULL,
            entry_type TEXT NOT NULL,
            source_line TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);
        CREATE INDEX IF NOT EXISTS idx_universal_log_customer_date ON universal_log(customer_id, entry_date);
        CREATE INDEX IF NOT EXISTS idx_universal_log_bazar_date ON universal_log(bazar, entry_date);
        """
        
        with self.transaction() as conn:
            conn.executescript(basic_schema)
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        return cursor.fetchall()
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Execute multiple INSERT/UPDATE/DELETE queries"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def insert_and_get_id(self, query: str, params: Tuple) -> int:
        """Insert a record and return the last inserted ID"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid
    
    # Customer Operations
    def add_customer(self, name: str, commission_type: str = 'commission') -> int:
        """Add a new customer and return their ID"""
        query = "INSERT INTO customers (name, commission_type) VALUES (?, ?)"
        return self.insert_and_get_id(query, (name, commission_type))
    
    def get_customer_by_name(self, name: str) -> Optional[sqlite3.Row]:
        """Get customer by name"""
        query = "SELECT * FROM customers WHERE name = ? AND is_active = 1"
        results = self.execute_query(query, (name,))
        return results[0] if results else None
    
    def get_customer_by_id(self, customer_id: int) -> Optional[sqlite3.Row]:
        """Get customer by ID"""
        query = "SELECT * FROM customers WHERE id = ? AND is_active = 1"
        results = self.execute_query(query, (customer_id,))
        return results[0] if results else None
    
    def get_all_customers(self) -> List[sqlite3.Row]:
        """Get all active customers"""
        query = "SELECT * FROM customers WHERE is_active = 1 ORDER BY name"
        return self.execute_query(query)
    
    # Bazar Operations
    def get_all_bazars(self) -> List[sqlite3.Row]:
        """Get all active bazars"""
        query = "SELECT * FROM bazars WHERE is_active = 1 ORDER BY sort_order, name"
        return self.execute_query(query)
    
    def add_bazar(self, name: str, display_name: str = None) -> int:
        """Add a new bazar"""
        if display_name is None:
            display_name = name
        query = "INSERT INTO bazars (name, display_name) VALUES (?, ?)"
        return self.insert_and_get_id(query, (name, display_name))
    
    # Universal Log Operations
    def add_universal_log_entry(self, entry_data: Dict[str, Any]) -> int:
        """Add an entry to universal log"""
        query = """
        INSERT INTO universal_log 
        (customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            entry_data['customer_id'],
            entry_data['customer_name'],
            entry_data['entry_date'],
            entry_data['bazar'],
            entry_data['number'],
            entry_data['value'],
            entry_data['entry_type'],
            entry_data.get('source_line', '')
        )
        return self.insert_and_get_id(query, params)
    
    def add_universal_log_entries(self, entries: List[Dict[str, Any]]) -> int:
        """Add multiple entries to universal log"""
        query = """
        INSERT INTO universal_log 
        (customer_id, customer_name, entry_date, bazar, number, value, entry_type, source_line)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params_list = [
            (
                entry['customer_id'],
                entry['customer_name'],
                entry['entry_date'],
                entry['bazar'],
                entry['number'],
                entry['value'],
                entry['entry_type'],
                entry.get('source_line', '')
            )
            for entry in entries
        ]
        return self.execute_many(query, params_list)
    
    def get_universal_log_entries(self, filters: Optional[Dict[str, Any]] = None, 
                                 limit: int = 1000, offset: int = 0) -> List[sqlite3.Row]:
        """Get universal log entries with optional filters"""
        query = "SELECT * FROM universal_log WHERE 1=1"
        params = []
        
        if filters:
            if 'customer_id' in filters:
                query += " AND customer_id = ?"
                params.append(filters['customer_id'])
            
            if 'bazar' in filters:
                query += " AND bazar = ?"
                params.append(filters['bazar'])
            
            if 'start_date' in filters:
                query += " AND entry_date >= ?"
                params.append(filters['start_date'])
            
            if 'end_date' in filters:
                query += " AND entry_date <= ?"
                params.append(filters['end_date'])
            
            if 'entry_type' in filters:
                query += " AND entry_type = ?"
                params.append(filters['entry_type'])
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        return self.execute_query(query, tuple(params))
    
    # Pana Table Operations
    def update_pana_table_entry(self, bazar: str, entry_date: str, number: int, value_to_add: int) -> None:
        """Update or insert pana table entry by adding value"""
        # First, try to get existing entry
        check_query = """
        SELECT id, value FROM pana_table 
        WHERE bazar = ? AND entry_date = ? AND number = ?
        """
        existing = self.execute_query(check_query, (bazar, entry_date, number))
        
        if existing:
            # Update existing entry by adding value
            update_query = """
            UPDATE pana_table 
            SET value = value + ?, updated_at = CURRENT_TIMESTAMP
            WHERE bazar = ? AND entry_date = ? AND number = ?
            """
            self.execute_update(update_query, (value_to_add, bazar, entry_date, number))
        else:
            # Insert new entry
            insert_query = """
            INSERT INTO pana_table (bazar, entry_date, number, value)
            VALUES (?, ?, ?, ?)
            """
            self.execute_update(insert_query, (bazar, entry_date, number, value_to_add))
    
    def get_pana_table_values(self, bazar: str, entry_date: str) -> List[sqlite3.Row]:
        """Get all pana values for a specific bazar and date"""
        query = """
        SELECT number, value FROM pana_table
        WHERE bazar = ? AND entry_date = ?
        ORDER BY number
        """
        return self.execute_query(query, (bazar, entry_date))
    
    def get_pana_reference_numbers(self) -> set:
        """Get all valid pana reference numbers from pana_numbers table"""
        query = "SELECT DISTINCT number FROM pana_numbers"
        rows = self.execute_query(query)
        return {row['number'] for row in rows} if rows else set()
    
    # Jodi Table Operations
    def get_jodi_table_values(self, bazar: str, entry_date: str) -> List[sqlite3.Row]:
        """Get all jodi values for a specific bazar and date (aggregated for all customers)"""
        query = """
        SELECT jodi_number, value FROM jodi_table
        WHERE bazar = ? AND entry_date = ?
        ORDER BY jodi_number
        """
        return self.execute_query(query, (bazar, entry_date))
    
    def get_jodi_table_values_by_customer(self, customer_name: str, bazar: str, entry_date: str) -> List[sqlite3.Row]:
        """Get jodi values for a specific customer, bazar and date from universal_log"""
        query = """
        SELECT number as jodi_number, SUM(value) as value 
        FROM universal_log
        WHERE customer_name = ? AND bazar = ? AND entry_date = ? AND entry_type = 'JODI'
        GROUP BY number
        ORDER BY number
        """
        return self.execute_query(query, (customer_name, bazar, entry_date))
    
    # Time Table Operations
    def update_time_table_entry(self, customer_id: int, customer_name: str, 
                               bazar: str, entry_date: str, column_values: Dict[int, int]) -> None:
        """Update or insert time table entry"""
        # First, try to get existing entry
        check_query = """
        SELECT id FROM time_table 
        WHERE customer_id = ? AND bazar = ? AND entry_date = ?
        """
        existing = self.execute_query(check_query, (customer_id, bazar, entry_date))
        
        if existing:
            # Build dynamic update query for columns
            update_parts = []
            params = []
            
            for col_num, value in column_values.items():
                if 0 <= col_num <= 9:
                    update_parts.append(f"col_{col_num} = col_{col_num} + ?")
                    params.append(value)
            
            if update_parts:
                update_query = f"""
                UPDATE time_table 
                SET {', '.join(update_parts)}, updated_at = CURRENT_TIMESTAMP
                WHERE customer_id = ? AND bazar = ? AND entry_date = ?
                """
                params.extend([customer_id, bazar, entry_date])
                self.execute_update(update_query, tuple(params))
        else:
            # Insert new entry
            insert_query = """
            INSERT INTO time_table 
            (customer_id, customer_name, bazar, entry_date, 
             col_0, col_1, col_2, col_3, col_4, col_5, col_6, col_7, col_8, col_9)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            # Initialize all columns to 0, then set provided values
            col_values = [0] * 10
            for col_num, value in column_values.items():
                if 0 <= col_num <= 9:
                    col_values[col_num] = value
            
            params = [customer_id, customer_name, bazar, entry_date] + col_values
            self.execute_update(insert_query, tuple(params))
    
    def get_time_table_entry(self, customer_id: int, bazar: str, entry_date: str) -> Optional[sqlite3.Row]:
        """Get time table entry for a customer, bazar, and date"""
        query = """
        SELECT * FROM time_table
        WHERE customer_id = ? AND bazar = ? AND entry_date = ?
        """
        results = self.execute_query(query, (customer_id, bazar, entry_date))
        return results[0] if results else None
    
    def get_time_table_by_bazar_date(self, bazar: str, entry_date: str) -> List[sqlite3.Row]:
        """Get all time table entries for a specific bazar and date"""
        query = """
        SELECT * FROM time_table
        WHERE bazar = ? AND entry_date = ?
        ORDER BY customer_name
        """
        return self.execute_query(query, (bazar, entry_date))
    
    # Customer Bazar Summary Operations
    def update_customer_bazar_summary(self, customer_id: int, customer_name: str, 
                                     entry_date: str, bazar_totals: Dict[str, int]) -> None:
        """Update or insert customer bazar summary"""
        # Map bazar names to column names
        bazar_column_map = {
            'T.O': 'to_total',
            'T.K': 'tk_total',
            'M.O': 'mo_total',
            'M.K': 'mk_total',
            'K.O': 'ko_total',
            'K.K': 'kk_total',
            'NMO': 'nmo_total',
            'NMK': 'nmk_total',
            'B.O': 'bo_total',
            'B.K': 'bk_total'
        }
        
        # Check if entry exists
        check_query = """
        SELECT id FROM customer_bazar_summary
        WHERE customer_id = ? AND entry_date = ?
        """
        existing = self.execute_query(check_query, (customer_id, entry_date))
        
        if existing:
            # Build update query
            update_parts = []
            params = []
            
            for bazar, total in bazar_totals.items():
                if bazar in bazar_column_map:
                    column = bazar_column_map[bazar]
                    update_parts.append(f"{column} = {column} + ?")
                    params.append(total)
            
            if update_parts:
                update_query = f"""
                UPDATE customer_bazar_summary
                SET {', '.join(update_parts)}, updated_at = CURRENT_TIMESTAMP
                WHERE customer_id = ? AND entry_date = ?
                """
                params.extend([customer_id, entry_date])
                self.execute_update(update_query, tuple(params))
        else:
            # Insert new entry
            # Initialize all totals to 0
            totals = {col: 0 for col in bazar_column_map.values()}
            
            # Set provided totals
            for bazar, total in bazar_totals.items():
                if bazar in bazar_column_map:
                    totals[bazar_column_map[bazar]] = total
            
            insert_query = """
            INSERT INTO customer_bazar_summary
            (customer_id, customer_name, entry_date, 
             to_total, tk_total, mo_total, mk_total, ko_total, 
             kk_total, nmo_total, nmk_total, bo_total, bk_total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = [customer_id, customer_name, entry_date] + [
                totals['to_total'], totals['tk_total'], totals['mo_total'], 
                totals['mk_total'], totals['ko_total'], totals['kk_total'], 
                totals['nmo_total'], totals['nmk_total'], totals['bo_total'], 
                totals['bk_total']
            ]
            self.execute_update(insert_query, tuple(params))
    
    def get_customer_bazar_summary_by_date(self, entry_date: str) -> List[sqlite3.Row]:
        """Get all customer summaries for a specific date"""
        query = """
        SELECT * FROM customer_bazar_summary
        WHERE entry_date = ?
        ORDER BY customer_name
        """
        return self.execute_query(query, (entry_date,))
    
    def close(self):
        """Close database connection"""
        if hasattr(self.local, 'connection') and self.local.connection:
            self.local.connection.close()
            self.local.connection = None
            self.logger.info("Database connection closed")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.close()


def create_database_manager(db_path: str = "./data/rickymama.db") -> DatabaseManager:
    """Factory function to create database manager"""
    return DatabaseManager(db_path)