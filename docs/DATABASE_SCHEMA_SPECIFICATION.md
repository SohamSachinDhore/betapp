# RickyMama - Database Schema Specification

## Database Design Overview

The RickyMama system uses SQLite for local data persistence with a normalized schema design optimized for fast queries and data integrity. The database supports concurrent access, transaction safety, and efficient backup operations.

## Schema Architecture

### Database Configuration
```sql
-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Set synchronous mode for data safety
PRAGMA synchronous = NORMAL;

-- Enable WAL mode for better concurrency
PRAGMA journal_mode = WAL;

-- Set cache size (in KB)
PRAGMA cache_size = 10240;
```

## Core Tables

### 1. Customer Management

#### customers
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    
    -- Constraints
    CONSTRAINT customers_name_length CHECK (length(name) BETWEEN 1 AND 100)
);

-- Indexes
CREATE INDEX idx_customers_name ON customers(name);
CREATE INDEX idx_customers_active ON customers(is_active) WHERE is_active = 1;
```

#### Triggers for customers
```sql
-- Auto-update timestamp on modification
CREATE TRIGGER customers_updated_at 
AFTER UPDATE ON customers
FOR EACH ROW
BEGIN
    UPDATE customers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

### 2. Bazar Management

#### bazars
```sql
CREATE TABLE bazars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    display_name TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    
    -- Constraints
    CONSTRAINT bazars_name_length CHECK (length(name) BETWEEN 1 AND 10),
    CONSTRAINT bazars_display_name_length CHECK (length(display_name) BETWEEN 1 AND 50)
);

-- Indexes
CREATE INDEX idx_bazars_name ON bazars(name);
CREATE INDEX idx_bazars_sort_order ON bazars(sort_order);
CREATE INDEX idx_bazars_active ON bazars(is_active) WHERE is_active = 1;

-- Insert default bazars
INSERT INTO bazars (name, display_name, sort_order) VALUES
('T.O', 'T.O', 1),
('T.K', 'T.K', 2),
('M.O', 'M.O', 3),
('M.K', 'M.K', 4),
('K.O', 'K.O', 5),
('NMO', 'NMO', 6),
('NMK', 'NMK', 7),
('B.O', 'B.O', 8),
('B.K', 'B.K', 9);
```

### 3. Universal Transaction Log

#### universal_log
```sql
CREATE TABLE universal_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL, -- Denormalized for performance
    entry_date DATE NOT NULL,
    bazar TEXT NOT NULL,
    number INTEGER NOT NULL,
    value INTEGER NOT NULL,
    entry_type TEXT NOT NULL, -- 'PANA', 'TYPE', 'TIME_DIRECT', 'TIME_MULTI'
    source_line TEXT, -- Original input line for audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT universal_log_number_range CHECK (number >= 0 AND number <= 999),
    CONSTRAINT universal_log_value_positive CHECK (value >= 0),
    CONSTRAINT universal_log_entry_type_valid CHECK (
        entry_type IN ('PANA', 'TYPE', 'TIME_DIRECT', 'TIME_MULTI')
    )
);

-- Indexes for performance
CREATE INDEX idx_universal_log_customer_date ON universal_log(customer_id, entry_date);
CREATE INDEX idx_universal_log_bazar_date ON universal_log(bazar, entry_date);
CREATE INDEX idx_universal_log_number ON universal_log(number);
CREATE INDEX idx_universal_log_created_at ON universal_log(created_at);
CREATE INDEX idx_universal_log_composite ON universal_log(customer_id, bazar, entry_date);
```

### 4. Pana Table Data

#### pana_table
```sql
CREATE TABLE pana_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bazar TEXT NOT NULL,
    entry_date DATE NOT NULL,
    number INTEGER NOT NULL,
    value INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT pana_table_number_range CHECK (number >= 100 AND number <= 999),
    CONSTRAINT pana_table_value_positive CHECK (value >= 0),
    
    -- Unique constraint for bazar + date + number
    UNIQUE(bazar, entry_date, number)
);

-- Indexes
CREATE INDEX idx_pana_table_bazar_date ON pana_table(bazar, entry_date);
CREATE INDEX idx_pana_table_number ON pana_table(number);
CREATE INDEX idx_pana_table_value ON pana_table(value) WHERE value > 0;
```

#### Triggers for pana_table
```sql
-- Auto-update timestamp on modification
CREATE TRIGGER pana_table_updated_at 
AFTER UPDATE ON pana_table
FOR EACH ROW
BEGIN
    UPDATE pana_table SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

### 5. Time Table Data

#### time_table
```sql
CREATE TABLE time_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL, -- Denormalized for performance
    bazar TEXT NOT NULL,
    entry_date DATE NOT NULL,
    
    -- Digit columns (0-9)
    col_0 INTEGER DEFAULT 0,
    col_1 INTEGER DEFAULT 0,
    col_2 INTEGER DEFAULT 0,
    col_3 INTEGER DEFAULT 0,
    col_4 INTEGER DEFAULT 0,
    col_5 INTEGER DEFAULT 0,
    col_6 INTEGER DEFAULT 0,
    col_7 INTEGER DEFAULT 0,
    col_8 INTEGER DEFAULT 0,
    col_9 INTEGER DEFAULT 0,
    
    -- Calculated total
    total INTEGER GENERATED ALWAYS AS (
        col_0 + col_1 + col_2 + col_3 + col_4 + 
        col_5 + col_6 + col_7 + col_8 + col_9
    ) STORED,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT time_table_columns_positive CHECK (
        col_0 >= 0 AND col_1 >= 0 AND col_2 >= 0 AND col_3 >= 0 AND col_4 >= 0 AND
        col_5 >= 0 AND col_6 >= 0 AND col_7 >= 0 AND col_8 >= 0 AND col_9 >= 0
    ),
    
    -- Unique constraint for customer + bazar + date
    UNIQUE(customer_id, bazar, entry_date)
);

-- Indexes
CREATE INDEX idx_time_table_customer_date ON time_table(customer_id, entry_date);
CREATE INDEX idx_time_table_bazar_date ON time_table(bazar, entry_date);
CREATE INDEX idx_time_table_total ON time_table(total) WHERE total > 0;
```

#### Triggers for time_table
```sql
-- Auto-update timestamp on modification
CREATE TRIGGER time_table_updated_at 
AFTER UPDATE ON time_table
FOR EACH ROW
BEGIN
    UPDATE time_table SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

### 6. Customer Summary by Bazar

#### customer_bazar_summary
```sql
CREATE TABLE customer_bazar_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL, -- Denormalized for performance
    entry_date DATE NOT NULL,
    
    -- Bazar totals
    to_total INTEGER DEFAULT 0,     -- T.O
    tk_total INTEGER DEFAULT 0,     -- T.K
    mo_total INTEGER DEFAULT 0,     -- M.O
    mk_total INTEGER DEFAULT 0,     -- M.K
    ko_total INTEGER DEFAULT 0,     -- K.O
    kk_total INTEGER DEFAULT 0,     -- K.K (assuming this was meant instead of NMK)
    nmo_total INTEGER DEFAULT 0,    -- NMO
    nmk_total INTEGER DEFAULT 0,    -- NMK
    bo_total INTEGER DEFAULT 0,     -- B.O
    bk_total INTEGER DEFAULT 0,     -- B.K
    
    -- Calculated grand total
    grand_total INTEGER GENERATED ALWAYS AS (
        to_total + tk_total + mo_total + mk_total + ko_total + 
        kk_total + nmo_total + nmk_total + bo_total + bk_total
    ) STORED,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT customer_bazar_summary_totals_positive CHECK (
        to_total >= 0 AND tk_total >= 0 AND mo_total >= 0 AND mk_total >= 0 AND
        ko_total >= 0 AND kk_total >= 0 AND nmo_total >= 0 AND nmk_total >= 0 AND
        bo_total >= 0 AND bk_total >= 0
    ),
    
    -- Unique constraint for customer + date
    UNIQUE(customer_id, entry_date)
);

-- Indexes
CREATE INDEX idx_customer_bazar_summary_customer_date ON customer_bazar_summary(customer_id, entry_date);
CREATE INDEX idx_customer_bazar_summary_date ON customer_bazar_summary(entry_date);
CREATE INDEX idx_customer_bazar_summary_grand_total ON customer_bazar_summary(grand_total) WHERE grand_total > 0;
```

## Reference Tables (Read-Only)

### 7. Pana Reference Table

#### pana_numbers
```sql
CREATE TABLE pana_numbers (
    number INTEGER PRIMARY KEY,
    section INTEGER NOT NULL, -- 1 for upper section, 2 for lower section
    row_position INTEGER NOT NULL,
    col_position INTEGER NOT NULL,
    
    -- Constraints
    CONSTRAINT pana_numbers_range CHECK (number >= 100 AND number <= 999),
    CONSTRAINT pana_numbers_section CHECK (section IN (1, 2))
);

-- Insert pana numbers from specification
-- Upper section (section 1)
INSERT INTO pana_numbers (number, section, row_position, col_position) VALUES
-- Row 1
(128, 1, 1, 1), (129, 1, 1, 3), (120, 1, 1, 5), (130, 1, 1, 7), (140, 1, 1, 9),
(123, 1, 1, 11), (124, 1, 1, 13), (125, 1, 1, 15), (126, 1, 1, 17), (127, 1, 1, 19),
-- ... (continue with all pana numbers from specification)

-- Create index for fast lookups
CREATE INDEX idx_pana_numbers_section ON pana_numbers(section);
```

### 8. Type Table Reference

#### type_table_sp
```sql
CREATE TABLE type_table_sp (
    column_number INTEGER NOT NULL,
    row_number INTEGER NOT NULL,
    number INTEGER NOT NULL,
    
    PRIMARY KEY (column_number, row_number),
    CONSTRAINT type_table_sp_column_range CHECK (column_number BETWEEN 1 AND 10),
    CONSTRAINT type_table_sp_number_range CHECK (number >= 100 AND number <= 999)
);

-- Insert SP table data from specification
-- ... (insert all SP table values)
```

#### type_table_dp
```sql
CREATE TABLE type_table_dp (
    column_number INTEGER NOT NULL,
    row_number INTEGER NOT NULL,
    number INTEGER NOT NULL,
    
    PRIMARY KEY (column_number, row_number),
    CONSTRAINT type_table_dp_column_range CHECK (column_number BETWEEN 1 AND 10),
    CONSTRAINT type_table_dp_number_range CHECK (number >= 0 AND number <= 999)
);

-- Insert DP table data from specification
-- ... (insert all DP table values)
```

#### type_table_cp
```sql
CREATE TABLE type_table_cp (
    column_number INTEGER NOT NULL,
    row_number INTEGER NOT NULL,
    number INTEGER NOT NULL,
    
    PRIMARY KEY (column_number, row_number),
    CONSTRAINT type_table_cp_column_valid CHECK (
        (column_number BETWEEN 11 AND 99) OR column_number = 0
    ),
    CONSTRAINT type_table_cp_number_range CHECK (number >= 0 AND number <= 999)
);

-- Insert CP table data from specification (complete the partial data logically)
-- ... (insert all CP table values)
```

## Views for Simplified Queries

### 1. Customer Summary View
```sql
CREATE VIEW v_customer_summary AS
SELECT 
    c.id,
    c.name,
    c.created_at,
    COUNT(DISTINCT ul.entry_date) as active_days,
    SUM(ul.value) as total_value,
    MAX(ul.created_at) as last_activity
FROM customers c
LEFT JOIN universal_log ul ON c.id = ul.customer_id
WHERE c.is_active = 1
GROUP BY c.id, c.name, c.created_at;
```

### 2. Daily Pana Summary View
```sql
CREATE VIEW v_daily_pana_summary AS
SELECT 
    bazar,
    entry_date,
    COUNT(*) as total_entries,
    SUM(value) as total_value,
    COUNT(DISTINCT number) as unique_numbers
FROM pana_table
WHERE value > 0
GROUP BY bazar, entry_date
ORDER BY entry_date DESC, bazar;
```

### 3. Customer Time Table Summary View
```sql
CREATE VIEW v_customer_time_summary AS
SELECT 
    customer_name,
    bazar,
    entry_date,
    total,
    (col_0 + col_1 + col_2 + col_3 + col_4) as first_half_total,
    (col_5 + col_6 + col_7 + col_8 + col_9) as second_half_total
FROM time_table
WHERE total > 0
ORDER BY entry_date DESC, customer_name, bazar;
```

## Database Functions and Procedures

### 1. Pana Table Update Function
```sql
-- Function to update or insert pana table entry
CREATE TRIGGER tr_update_pana_table
AFTER INSERT ON universal_log
FOR EACH ROW
WHEN NEW.entry_type = 'PANA'
BEGIN
    INSERT INTO pana_table (bazar, entry_date, number, value)
    VALUES (NEW.bazar, NEW.entry_date, NEW.number, NEW.value)
    ON CONFLICT(bazar, entry_date, number) DO UPDATE SET 
        value = value + excluded.value,
        updated_at = CURRENT_TIMESTAMP;
END;
```

### 2. Time Table Update Function
```sql
-- Function to update time table entries
CREATE TRIGGER tr_update_time_table_direct
AFTER INSERT ON universal_log
FOR EACH ROW
WHEN NEW.entry_type = 'TIME_DIRECT'
BEGIN
    INSERT INTO time_table (
        customer_id, customer_name, bazar, entry_date,
        col_0, col_1, col_2, col_3, col_4, col_5, col_6, col_7, col_8, col_9
    )
    VALUES (
        NEW.customer_id, NEW.customer_name, NEW.bazar, NEW.entry_date,
        CASE WHEN NEW.number = 0 THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.number = 1 THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.number = 2 THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.number = 3 THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.number = 4 THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.number = 5 THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.number = 6 THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.number = 7 THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.number = 8 THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.number = 9 THEN NEW.value ELSE 0 END
    )
    ON CONFLICT(customer_id, bazar, entry_date) DO UPDATE SET
        col_0 = col_0 + (CASE WHEN NEW.number = 0 THEN NEW.value ELSE 0 END),
        col_1 = col_1 + (CASE WHEN NEW.number = 1 THEN NEW.value ELSE 0 END),
        col_2 = col_2 + (CASE WHEN NEW.number = 2 THEN NEW.value ELSE 0 END),
        col_3 = col_3 + (CASE WHEN NEW.number = 3 THEN NEW.value ELSE 0 END),
        col_4 = col_4 + (CASE WHEN NEW.number = 4 THEN NEW.value ELSE 0 END),
        col_5 = col_5 + (CASE WHEN NEW.number = 5 THEN NEW.value ELSE 0 END),
        col_6 = col_6 + (CASE WHEN NEW.number = 6 THEN NEW.value ELSE 0 END),
        col_7 = col_7 + (CASE WHEN NEW.number = 7 THEN NEW.value ELSE 0 END),
        col_8 = col_8 + (CASE WHEN NEW.number = 8 THEN NEW.value ELSE 0 END),
        col_9 = col_9 + (CASE WHEN NEW.number = 9 THEN NEW.value ELSE 0 END),
        updated_at = CURRENT_TIMESTAMP;
END;
```

### 3. Customer Summary Update Function
```sql
-- Function to update customer summary
CREATE TRIGGER tr_update_customer_summary
AFTER INSERT ON universal_log
FOR EACH ROW
BEGIN
    INSERT INTO customer_bazar_summary (
        customer_id, customer_name, entry_date,
        to_total, tk_total, mo_total, mk_total, ko_total,
        kk_total, nmo_total, nmk_total, bo_total, bk_total
    )
    VALUES (
        NEW.customer_id, NEW.customer_name, NEW.entry_date,
        CASE WHEN NEW.bazar = 'T.O' THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.bazar = 'T.K' THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.bazar = 'M.O' THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.bazar = 'M.K' THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.bazar = 'K.O' THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.bazar = 'K.K' THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.bazar = 'NMO' THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.bazar = 'NMK' THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.bazar = 'B.O' THEN NEW.value ELSE 0 END,
        CASE WHEN NEW.bazar = 'B.K' THEN NEW.value ELSE 0 END
    )
    ON CONFLICT(customer_id, entry_date) DO UPDATE SET
        to_total = to_total + (CASE WHEN NEW.bazar = 'T.O' THEN NEW.value ELSE 0 END),
        tk_total = tk_total + (CASE WHEN NEW.bazar = 'T.K' THEN NEW.value ELSE 0 END),
        mo_total = mo_total + (CASE WHEN NEW.bazar = 'M.O' THEN NEW.value ELSE 0 END),
        mk_total = mk_total + (CASE WHEN NEW.bazar = 'M.K' THEN NEW.value ELSE 0 END),
        ko_total = ko_total + (CASE WHEN NEW.bazar = 'K.O' THEN NEW.value ELSE 0 END),
        kk_total = kk_total + (CASE WHEN NEW.bazar = 'K.K' THEN NEW.value ELSE 0 END),
        nmo_total = nmo_total + (CASE WHEN NEW.bazar = 'NMO' THEN NEW.value ELSE 0 END),
        nmk_total = nmk_total + (CASE WHEN NEW.bazar = 'NMK' THEN NEW.value ELSE 0 END),
        bo_total = bo_total + (CASE WHEN NEW.bazar = 'B.O' THEN NEW.value ELSE 0 END),
        bk_total = bk_total + (CASE WHEN NEW.bazar = 'B.K' THEN NEW.value ELSE 0 END),
        updated_at = CURRENT_TIMESTAMP;
END;
```

## Database Maintenance

### 1. Cleanup Procedures
```sql
-- Clean up old log entries (older than 2 years)
CREATE VIEW v_cleanup_old_logs AS
SELECT COUNT(*) as records_to_delete
FROM universal_log 
WHERE created_at < date('now', '-2 years');

-- Vacuum and analyze for performance
-- VACUUM; -- Reclaim space
-- ANALYZE; -- Update statistics
```

### 2. Backup Procedures
```sql
-- Export data for backup
.mode csv
.headers on
.output customers_backup.csv
SELECT * FROM customers;

.output universal_log_backup.csv
SELECT * FROM universal_log;

.output pana_table_backup.csv
SELECT * FROM pana_table;

.output time_table_backup.csv
SELECT * FROM time_table;

.output customer_bazar_summary_backup.csv
SELECT * FROM customer_bazar_summary;
```

## Performance Optimization

### 1. Query Optimization
- Use appropriate indexes for frequent queries
- Implement query result caching for table views
- Use EXPLAIN QUERY PLAN for complex queries
- Optimize JOIN operations with proper indexing

### 2. Connection Management
- Use connection pooling for concurrent access
- Implement transaction batching for bulk operations
- Set appropriate timeout values
- Use WAL mode for better concurrency

### 3. Data Archival Strategy
- Archive old universal_log entries annually
- Maintain summary tables for historical analysis
- Implement sliding window for active data
- Regular VACUUM operations for space reclamation

This database schema provides a robust foundation for the RickyMama system with proper normalization, referential integrity, performance optimization, and automated data maintenance through triggers and views.