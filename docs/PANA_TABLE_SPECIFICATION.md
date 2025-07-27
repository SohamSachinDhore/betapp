# RickyMama - Pana Table Layout Specification

## Pana Table Structure

The pana table must follow this exact layout with 10 Number|Value column pairs (20 columns total) and specific row organization with a gap separator between upper and lower sections.

### Table Format
| Number | Value | Number | Value | Number | Value | Number | Value | Number | Value | Number | Value | Number | Value | Number | Value | Number | Value | Number | Value |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 128 | 0 | 129 | 0 | 120 | 0 | 130 | 0 | 140 | 0 | 123 | 0 | 124 | 0 | 125 | 0 | 126 | 0 | 127 | 0 |
| 137 | 0 | 138 | 0 | 139 | 0 | 149 | 0 | 159 | 0 | 150 | 0 | 160 | 0 | 134 | 0 | 135 | 0 | 136 | 0 |
| 146 | 0 | 147 | 0 | 148 | 0 | 158 | 0 | 168 | 0 | 169 | 0 | 179 | 0 | 170 | 0 | 180 | 0 | 145 | 0 |
| 236 | 0 | 156 | 0 | 157 | 0 | 167 | 0 | 230 | 0 | 178 | 0 | 250 | 0 | 189 | 0 | 234 | 0 | 190 | 0 |
| 245 | 0 | 237 | 0 | 238 | 0 | 239 | 0 | 249 | 0 | 240 | 0 | 269 | 0 | 260 | 0 | 270 | 0 | 235 | 0 |
| 290 | 0 | 246 | 0 | 247 | 0 | 248 | 0 | 258 | 0 | 259 | 0 | 278 | 0 | 279 | 0 | 289 | 0 | 280 | 0 |
| 380 | 0 | 345 | 0 | 256 | 0 | 257 | 0 | 267 | 0 | 268 | 0 | 340 | 0 | 350 | 0 | 360 | 0 | 370 | 0 |
| 470 | 0 | 390 | 0 | 346 | 0 | 347 | 0 | 348 | 0 | 349 | 0 | 359 | 0 | 369 | 0 | 379 | 0 | 389 | 0 |
| 489 | 0 | 480 | 0 | 490 | 0 | 356 | 0 | 357 | 0 | 358 | 0 | 368 | 0 | 378 | 0 | 450 | 0 | 460 | 0 |
| 560 | 0 | 570 | 0 | 580 | 0 | 590 | 0 | 456 | 0 | 367 | 0 | 458 | 0 | 459 | 0 | 478 | 0 | 479 | 0 |
| 579 | 0 | 589 | 0 | 670 | 0 | 680 | 0 | 690 | 0 | 457 | 0 | 467 | 0 | 468 | 0 | 469 | 0 | 569 | 0 |
| 678 | 0 | 679 | 0 | 689 | 0 | 789 | 0 | 780 | 0 | 790 | 0 | 890 | 0 | 567 | 0 | 568 | 0 | 578 | 0 |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| 100 | 0 | 110 | 0 | 166 | 0 | 112 | 0 | 113 | 0 | 114 | 0 | 115 | 0 | 116 | 0 | 117 | 0 | 118 | 0 |
| 119 | 0 | 200 | 0 | 229 | 0 | 220 | 0 | 122 | 0 | 277 | 0 | 133 | 0 | 224 | 0 | 144 | 0 | 226 | 0 |
| 155 | 0 | 228 | 0 | 300 | 0 | 266 | 0 | 177 | 0 | 330 | 0 | 188 | 0 | 233 | 0 | 199 | 0 | 244 | 0 |
| 227 | 0 | 255 | 0 | 337 | 0 | 338 | 0 | 339 | 0 | 448 | 0 | 223 | 0 | 288 | 0 | 225 | 0 | 299 | 0 |
| 335 | 0 | 336 | 0 | 355 | 0 | 400 | 0 | 366 | 0 | 466 | 0 | 377 | 0 | 440 | 0 | 388 | 0 | 334 | 0 |
| 344 | 0 | 499 | 0 | 445 | 0 | 446 | 0 | 447 | 0 | 556 | 0 | 449 | 0 | 477 | 0 | 559 | 0 | 488 | 0 |
| 399 | 0 | 660 | 0 | 599 | 0 | 455 | 0 | 500 | 0 | 880 | 0 | 557 | 0 | 558 | 0 | 577 | 0 | 550 | 0 |
| 588 | 0 | 688 | 0 | 779 | 0 | 699 | 0 | 799 | 0 | 899 | 0 | 566 | 0 | 800 | 0 | 667 | 0 | 668 | 0 |
| 669 | 0 | 778 | 0 | 788 | 0 | 770 | 0 | 889 | 0 | 600 | 0 | 700 | 0 | 990 | 0 | 900 | 0 | 677 | 0 |
| 777 | 0 | 444 | 0 | 111 | 0 | 888 | 0 | 555 | 0 | 222 | 0 | 999 | 0 | 666 | 0 | 333 | 0 | 0 | 0 |

## Data Structure Requirements

### Layout Specifications
1. **Column Structure**: Exactly 20 columns alternating Number|Value pairs
2. **Row Count**: 21 rows total (12 upper section + 1 separator + 8 lower section)
3. **Section Separator**: Empty row (row 13) with all cells empty
4. **Upper Section**: Rows 1-12 containing first set of pana numbers
5. **Lower Section**: Rows 14-21 containing second set of pana numbers

### Value Logic Implementation

#### Database Schema for Pana Table
```sql
CREATE TABLE pana_table_display (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bazar TEXT NOT NULL,
    entry_date DATE NOT NULL,
    row_number INTEGER NOT NULL,
    col_pair INTEGER NOT NULL, -- 1 to 10 for the 10 Number|Value pairs
    number INTEGER NOT NULL,
    value INTEGER NOT NULL DEFAULT 0,
    section INTEGER NOT NULL, -- 1 for upper, 2 for lower
    
    UNIQUE(bazar, entry_date, row_number, col_pair),
    CONSTRAINT pana_display_number_range CHECK (number >= 0 AND number <= 999),
    CONSTRAINT pana_display_value_positive CHECK (value >= 0),
    CONSTRAINT pana_display_section CHECK (section IN (1, 2)),
    CONSTRAINT pana_display_row_range CHECK (row_number BETWEEN 1 AND 12),
    CONSTRAINT pana_display_col_range CHECK (col_pair BETWEEN 1 AND 10)
);
```

#### Pana Number Layout Array
```python
class PanaTableLayout:
    """Exact pana table layout as specified"""
    
    # Upper section (rows 1-12)
    UPPER_SECTION = [
        [128, 129, 120, 130, 140, 123, 124, 125, 126, 127],  # Row 1
        [137, 138, 139, 149, 159, 150, 160, 134, 135, 136],  # Row 2
        [146, 147, 148, 158, 168, 169, 179, 170, 180, 145],  # Row 3
        [236, 156, 157, 167, 230, 178, 250, 189, 234, 190],  # Row 4
        [245, 237, 238, 239, 249, 240, 269, 260, 270, 235],  # Row 5
        [290, 246, 247, 248, 258, 259, 278, 279, 289, 280],  # Row 6
        [380, 345, 256, 257, 267, 268, 340, 350, 360, 370],  # Row 7
        [470, 390, 346, 347, 348, 349, 359, 369, 379, 389],  # Row 8
        [489, 480, 490, 356, 357, 358, 368, 378, 450, 460],  # Row 9
        [560, 570, 580, 590, 456, 367, 458, 459, 478, 479],  # Row 10
        [579, 589, 670, 680, 690, 457, 467, 468, 469, 569],  # Row 11
        [678, 679, 689, 789, 780, 790, 890, 567, 568, 578],  # Row 12
    ]
    
    # Lower section (rows 14-21, after separator row 13)
    LOWER_SECTION = [
        [100, 110, 166, 112, 113, 114, 115, 116, 117, 118],  # Row 14
        [119, 200, 229, 220, 122, 277, 133, 224, 144, 226],  # Row 15
        [155, 228, 300, 266, 177, 330, 188, 233, 199, 244],  # Row 16
        [227, 255, 337, 338, 339, 448, 223, 288, 225, 299],  # Row 17
        [335, 336, 355, 400, 366, 466, 377, 440, 388, 334],  # Row 18
        [344, 499, 445, 446, 447, 556, 449, 477, 559, 488],  # Row 19
        [399, 660, 599, 455, 500, 880, 557, 558, 577, 550],  # Row 20
        [588, 688, 779, 699, 799, 899, 566, 800, 667, 668],  # Row 21
        [669, 778, 788, 770, 889, 600, 700, 990, 900, 677],  # Row 22
        [777, 444, 111, 888, 555, 222, 999, 666, 333, 0],    # Row 23
    ]
    
    @classmethod
    def get_complete_layout(cls):
        """Get complete pana table layout with separator"""
        complete_layout = []
        
        # Add upper section
        for row in cls.UPPER_SECTION:
            complete_layout.append(row)
        
        # Add separator row (empty)
        complete_layout.append([None] * 10)
        
        # Add lower section  
        for row in cls.LOWER_SECTION:
            complete_layout.append(row)
            
        return complete_layout
    
    @classmethod
    def get_all_pana_numbers(cls):
        """Get set of all valid pana numbers"""
        numbers = set()
        for row in cls.UPPER_SECTION + cls.LOWER_SECTION:
            for num in row:
                if num is not None and num != 0:
                    numbers.add(num)
        numbers.add(0)  # Special case for 0
        return numbers
```

#### Value Update Logic
```python
class PanaTableManager:
    """Manages pana table value updates and display"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.layout = PanaTableLayout()
    
    def update_pana_value(self, bazar: str, date: date, number: int, value: int):
        """Update value for specific pana number"""
        # Find position of number in layout
        position = self.find_number_position(number)
        if not position:
            raise ValueError(f"Number {number} not found in pana table layout")
        
        row_num, col_pair, section = position
        
        # Update database
        with self.db_manager.transaction() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO pana_table_display 
                (bazar, entry_date, row_number, col_pair, number, value, section)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(bazar, entry_date, row_number, col_pair) DO UPDATE SET
                    value = value + excluded.value
            """, (bazar, date, row_num, col_pair, number, value, section))
    
    def find_number_position(self, number: int) -> tuple:
        """Find position of number in layout (row, column_pair, section)"""
        # Search upper section
        for row_idx, row in enumerate(self.layout.UPPER_SECTION):
            for col_idx, num in enumerate(row):
                if num == number:
                    return (row_idx + 1, col_idx + 1, 1)  # 1-based indexing, section 1
        
        # Search lower section
        for row_idx, row in enumerate(self.layout.LOWER_SECTION):
            for col_idx, num in enumerate(row):
                if num == number:
                    return (row_idx + 1, col_idx + 1, 2)  # 1-based indexing, section 2
        
        return None
    
    def get_pana_display_data(self, bazar: str, date: date) -> list:
        """Get complete pana table data for display"""
        # Get values from database
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT row_number, col_pair, number, value, section
                FROM pana_table_display 
                WHERE bazar = ? AND entry_date = ?
                ORDER BY section, row_number, col_pair
            """, (bazar, date))
            
            db_values = {}
            for row in cursor.fetchall():
                key = (row[4], row[0], row[1])  # (section, row_number, col_pair)
                db_values[key] = {'number': row[2], 'value': row[3]}
        
        # Build display data using layout
        display_data = []
        complete_layout = self.layout.get_complete_layout()
        
        for layout_row_idx, layout_row in enumerate(complete_layout):
            display_row = []
            
            if layout_row[0] is None:  # Separator row
                display_row = [{'number': '', 'value': ''}] * 10
            else:
                section = 1 if layout_row_idx < 12 else 2
                db_row_num = (layout_row_idx + 1) if section == 1 else (layout_row_idx - 12)
                
                for col_idx, number in enumerate(layout_row):
                    key = (section, db_row_num, col_idx + 1)
                    
                    if key in db_values:
                        cell_data = db_values[key]
                    else:
                        cell_data = {'number': number, 'value': 0}
                    
                    display_row.append(cell_data)
            
            display_data.append(display_row)
        
        return display_data
```

#### GUI Implementation for Pana Table
```python
class PanaTableViewer:
    """GUI component for pana table display"""
    
    def create_pana_table_layout(self):
        """Create pana table with exact 10 Number|Value column layout"""
        
        # Create table with 20 columns (10 Number|Value pairs)
        with dpg.table(
            header_row=True,
            resizable=True,
            borders_innerH=True,
            borders_innerV=True,
            borders_outerH=True,
            borders_outerV=True,
            tag="pana_display_table",
            scrollY=True,
            height=600
        ) as table:
            
            # Create 20 column headers (Number|Value repeated 10 times)
            for i in range(10):
                dpg.add_table_column(label="Number", width=60)
                dpg.add_table_column(label="Value", width=60)
        
        self.load_pana_table_data()
    
    def load_pana_table_data(self):
        """Load and display pana table data"""
        bazar = dpg.get_value("pana_bazar_filter")
        date = self.get_selected_date("pana_date_filter") 
        
        if not bazar or not date:
            return
        
        # Clear existing rows
        dpg.delete_item("pana_display_table", children_only=True, slot=1)
        
        # Get display data
        display_data = self.pana_manager.get_pana_display_data(bazar, date)
        
        # Create rows
        for row_data in display_data:
            with dpg.table_row(parent="pana_display_table"):
                for cell in row_data:
                    if cell['number'] == '':  # Separator row
                        dpg.add_text("")  # Empty number cell
                        dpg.add_text("")  # Empty value cell
                    else:
                        # Number cell
                        dpg.add_text(str(cell['number']))
                        
                        # Value cell with conditional formatting
                        value = cell['value']
                        if value > 0:
                            dpg.add_text(
                                str(value),
                                color=(39, 174, 96, 255)  # Green for non-zero values
                            )
                        else:
                            dpg.add_text(
                                "0",
                                color=(108, 117, 125, 255)  # Gray for zero values
                            )
```

## Value Population Logic

### Entry Processing for Pana Table
When pana table entries are submitted:

1. **Parse Input**: Extract number-value pairs from input (e.g., "128/129/120 = 100")
2. **Find Positions**: Locate each number's position in the 10×21 grid layout
3. **Update Values**: Add new values to existing values in the Value columns
4. **Refresh Display**: Update GUI table to show new values

### Example Value Update Flow
```
Input: "128/129/120 = 100"
Processing:
- 128 found at Row 1, Column Pair 1, Section 1 → Add 100 to existing value
- 129 found at Row 1, Column Pair 2, Section 1 → Add 100 to existing value  
- 120 found at Row 1, Column Pair 3, Section 1 → Add 100 to existing value

Result: Value columns for these positions increment by 100
```

This specification ensures the pana table maintains the exact structure and value update logic as required, with proper 10 Number|Value column pairs and accurate positioning of all pana numbers.