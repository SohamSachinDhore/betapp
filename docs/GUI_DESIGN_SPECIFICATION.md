# RickyMama - GUI Design & User Interface Specification

## Overview

The RickyMama GUI is designed using Dear PyGui for fast, responsive performance with a user-friendly interface suitable for non-technical users. The design emphasizes clarity, efficiency, and error prevention.

## Design Principles

### 1. User Experience Guidelines
- **Simplicity First**: Clean, uncluttered interface with clear visual hierarchy
- **Non-Technical Friendly**: Intuitive controls with helpful labels and tooltips
- **Fast Data Entry**: Optimized workflow for rapid input with minimal clicks
- **Error Prevention**: Real-time validation and clear error messaging
- **Consistent Layout**: Standard patterns across all windows and dialogs

### 2. Performance Requirements
- **Responsive UI**: <100ms response time for all interactions
- **Smooth Scrolling**: Efficient table rendering for large datasets
- **Memory Efficient**: Lazy loading for data-heavy tables
- **Cross-Platform**: Consistent appearance on Mac and Windows

## Main Application Window

### Redesigned Window Layout Structure
```
┌─────────────────────────────────────────────────────────────────────────┐
│ RickyMama Data Entry System                                    [_ □ X] │
├─────────────────────────────────────────────────────────────────────────┤
│ Entry Form                                                              │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ Customer: [Dropdown ▼]     ID: [___________]          Auto-fill ✓   │ │
│ │ Date: [DD-MM-YYYY 📅]      Bazar: [Dropdown ▼]                       │ │
│ │                                                                     │ │
│ │ Input:                                                              │ │
│ │ ┌─────────────────────────────────────────────────────────────────┐ │ │
│ │ │ Multi-line text input area                                      │ │ │
│ │ │ (Supports all 5 input patterns)                                 │ │ │
│ │ │                                                                 │ │ │
│ │ │                                                                 │ │ │
│ │ └─────────────────────────────────────────────────────────────────┘ │ │
│ │                                                                     │ │
│ │ Preview:                                                            │ │
│ │ ┌─────────────────────────────────────────────────────────────────┐ │ │
│ │ │ Parsed output preview (read-only)                               │ │ │
│ │ │ Shows breakdown of calculations                                 │ │ │
│ │ └─────────────────────────────────────────────────────────────────┘ │ │
│ │                                                                     │ │
│ │ Total: [________] ₹         [Preview] [Submit] [Clear]              │ │
│ │                                                                     │ │
│ │ Quick Actions:  [View Tables] [Export Data]                         │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ Status: Ready | Last Entry: DD-MM-YYYY HH:MM                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### Separate Table Window Layout
```
┌─────────────────────────────────────────────────────────────────────────┐
│ RickyMama - Data Tables                                       [_ □ X] │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─[Customers]─[Universal]─[Pana]─[Time]─[Summary]─[Export]─────────────┐ │
│ │                                                                     │ │
│ │ Tab Content Area (Full Screen Table View)                          │ │
│ │                                                                     │ │
│ │ ┌─────────────────────────────────────────────────────────────────┐ │ │
│ │ │ Filters: [Date Range] [Customer] [Bazar] [Apply] [Clear]        │ │ │
│ │ ├─────────────────────────────────────────────────────────────────┤ │ │
│ │ │                                                                 │ │ │
│ │ │ Full-Screen Table with Enhanced Controls                        │ │ │
│ │ │ • Resizable/Sortable columns                                    │ │ │
│ │ │ • Pagination for large datasets                                 │ │ │
│ │ │ • Advanced filtering and search                                 │ │ │
│ │ │ • Export options per table                                      │ │ │
│ │ │                                                                 │ │ │
│ │ └─────────────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ Summary: X Records | Page Y of Z | Last Updated: DD-MM-YYYY HH:MM      │
└─────────────────────────────────────────────────────────────────────────┘
```

### Main Window Specifications
```python
class MainWindow:
    """Main application window design - Entry form only"""
    
    WINDOW_CONFIG = {
        'title': 'RickyMama Data Entry System',
        'width': 1000,
        'height': 700,
        'min_width': 800,
        'min_height': 600,
        'resizable': True,
        'pos': (100, 100)  # Center on screen
    }

class TableWindow:
    """Separate window for all data tables"""
    
    WINDOW_CONFIG = {
        'title': 'RickyMama - Data Tables',
        'width': 1400,
        'height': 900,
        'min_width': 1200,
        'min_height': 700,
        'resizable': True,
        'pos': (150, 150)  # Offset from main window
    }
    
    COLORS = {
        'primary': (41, 128, 185),      # Blue
        'success': (39, 174, 96),       # Green  
        'warning': (243, 156, 18),      # Orange
        'danger': (231, 76, 60),        # Red
        'background': (248, 249, 250),  # Light gray
        'text': (52, 58, 64),           # Dark gray
        'border': (206, 212, 218)       # Gray border
    }
```

## Entry Form Design

### Quick Actions Section
```python
class QuickActionsSection:
    """Quick action buttons for main operations"""
    
    def create_layout(self):
        with dpg.group(horizontal=True):
            # View Tables button
            dpg.add_button(
                label="View Tables",
                callback=self.open_table_window,
                tag="view_tables_btn",
                width=120,
                height=30
            )
            
            dpg.add_spacer(width=10)
            
            # Export Data button
            dpg.add_button(
                label="Export Data",
                callback=self.open_export_dialog,
                tag="export_data_btn",
                width=120,
                height=30
            )
            
            dpg.add_spacer(width=10)
            
            # Settings button
            dpg.add_button(
                label="Settings",
                callback=self.open_settings_dialog,
                tag="settings_btn",
                width=120,
                height=30
            )
    
    def open_table_window(self):
        """Open separate table window"""
        if not dpg.does_item_exist("table_window"):
            self.table_window = TableWindow(self.gui_manager)
            self.table_window.create_window()
        else:
            dpg.show_item("table_window")
            dpg.focus_item("table_window")

### Customer Selection Section
```python
class CustomerSection:
    """Customer and ID selection with bidirectional sync"""
    
    def create_layout(self):
        with dpg.group(horizontal=True):
            # Customer dropdown
            dpg.add_text("Customer:")
            dpg.add_combo(
                items=self.get_customer_names(),
                callback=self.on_customer_selected,
                tag="customer_combo",
                width=200,
                default_value="Select Customer..."
            )
            
            dpg.add_spacer(width=20)
            
            # Customer ID field
            dpg.add_text("ID:")
            dpg.add_input_text(
                callback=self.on_id_entered,
                tag="customer_id_input",
                width=100,
                hint="Auto-fill"
            )
            
            dpg.add_spacer(width=10)
            
            # Add new customer button
            dpg.add_button(
                label="+ New Customer",
                callback=self.show_new_customer_dialog,
                tag="new_customer_btn"
            )
    
    def on_customer_selected(self, sender, app_data, user_data):
        """Auto-fill ID when customer selected"""
        customer_name = app_data
        customer_id = self.get_customer_id(customer_name)
        dpg.set_value("customer_id_input", customer_id)
    
    def on_id_entered(self, sender, app_data, user_data):
        """Auto-fill name when ID entered"""
        customer_id = app_data
        customer_name = self.get_customer_name(customer_id)
        if customer_name:
            dpg.set_value("customer_combo", customer_name)
```

### Date and Bazar Selection
```python
class DateBazarSection:
    """Date and bazar selection with smart defaults"""
    
    def create_layout(self):
        with dpg.group(horizontal=True):
            # Date picker
            dpg.add_text("Date:")
            dpg.add_date_picker(
                callback=self.on_date_changed,
                tag="entry_date",
                default_value=self.get_today_dict()
            )
            
            dpg.add_spacer(width=20)
            
            # Bazar dropdown
            dpg.add_text("Bazar:")
            dpg.add_combo(
                items=self.get_active_bazars(),
                callback=self.on_bazar_selected,
                tag="bazar_combo",
                width=150,
                default_value="Select Bazar..."
            )
            
            dpg.add_spacer(width=10)
            
            # Add new bazar button
            dpg.add_button(
                label="+ New Bazar",
                callback=self.show_new_bazar_dialog,
                tag="new_bazar_btn"
            )
    
    def get_today_dict(self):
        """Get today's date in Dear PyGui format"""
        today = datetime.date.today()
        return {
            'month_day': today.day,
            'month': today.month - 1,  # 0-based months
            'year': today.year
        }
```

### Input Text Area
```python
class InputTextArea:
    """Multi-line input with real-time validation"""
    
    def create_layout(self):
        dpg.add_text("Input:")
        
        # Main input area
        dpg.add_input_text(
            multiline=True,
            callback=self.on_input_changed,
            tag="input_text_area",
            width=-1,  # Full width
            height=200,
            hint="Enter numbers and values (supports multiple formats)..."
        )
        
        # Input format help
        with dpg.collapsing_header(label="Input Format Help", default_open=False):
            dpg.add_text("Supported formats:")
            dpg.add_text("• Pana: 128/129/120 = 100 (or use +, space, comma, *)")
            dpg.add_text("• Type: 1SP=100, 5DP=200, 15CP=300")
            dpg.add_text("• Time: 1=100, 0 1 3 5 = 900")
            dpg.add_text("• Multiply: 38x700, 83x700")
            dpg.add_text("• Mixed: Combine multiple formats")
    
    def on_input_changed(self, sender, app_data, user_data):
        """Real-time input validation and preview update"""
        input_text = app_data
        
        # Validate input asynchronously
        self.validate_input_async(input_text)
        
        # Update preview if valid
        if self.is_valid_input(input_text):
            self.update_preview(input_text)
```

### Preview Area
```python
class PreviewArea:
    """Preview parsed input with calculation breakdown"""
    
    def create_layout(self):
        dpg.add_text("Preview:")
        
        # Preview text area (read-only)
        dpg.add_input_text(
            multiline=True,
            readonly=True,
            tag="preview_text_area",
            width=-1,
            height=150
        )
        
        # Calculation breakdown
        with dpg.group(horizontal=True):
            dpg.add_text("Total:")
            dpg.add_input_text(
                readonly=True,
                tag="calculated_total",
                width=150,
                default_value="0"
            )
            
            dpg.add_spacer(width=20)
            
            # Show breakdown button
            dpg.add_button(
                label="Show Breakdown",
                callback=self.show_calculation_breakdown,
                tag="breakdown_btn"
            )
    
    def update_preview(self, parsed_result: ParsedInputResult):
        """Update preview with parsed and calculated data"""
        preview_lines = []
        
        # Pana entries
        if parsed_result.pana_entries:
            preview_lines.append("=== Pana Table Entries ===")
            for entry in parsed_result.pana_entries:
                preview_lines.append(f"{entry.number} = {entry.value}")
            preview_lines.append("")
        
        # Type entries
        if parsed_result.type_entries:
            preview_lines.append("=== Type Table Entries ===")
            for entry in parsed_result.type_entries:
                preview_lines.append(f"Column {entry.column} ({entry.table_type}): {len(entry.numbers)} numbers × {entry.value}")
            preview_lines.append("")
        
        # Time entries
        if parsed_result.time_entries:
            preview_lines.append("=== Time Table Entries ===")
            for entry in parsed_result.time_entries:
                columns_str = ", ".join(map(str, entry.columns))
                preview_lines.append(f"Columns [{columns_str}] = {entry.value}")
            preview_lines.append("")
        
        # Multi entries
        if parsed_result.multi_entries:
            preview_lines.append("=== Multiplication Entries ===")
            for entry in parsed_result.multi_entries:
                preview_lines.append(f"{entry.number}x{entry.value} (Columns {entry.tens_digit}, {entry.units_digit})")
        
        preview_text = "\n".join(preview_lines)
        dpg.set_value("preview_text_area", preview_text)
```

### Action Buttons
```python
class ActionButtons:
    """Preview, Submit, Clear buttons with smart states"""
    
    def create_layout(self):
        with dpg.group(horizontal=True):
            # Preview button
            dpg.add_button(
                label="Preview",
                callback=self.on_preview_clicked,
                tag="preview_btn",
                width=100
            )
            
            dpg.add_spacer(width=10)
            
            # Submit button
            dpg.add_button(
                label="Submit",
                callback=self.on_submit_clicked,
                tag="submit_btn",
                width=100,
                enabled=False  # Enabled after successful preview
            )
            
            dpg.add_spacer(width=10)
            
            # Clear button
            dpg.add_button(
                label="Clear",
                callback=self.on_clear_clicked,
                tag="clear_btn",
                width=100
            )
    
    def on_preview_clicked(self, sender, app_data, user_data):
        """Generate preview and enable submit if valid"""
        try:
            input_text = dpg.get_value("input_text_area")
            parsed_result = self.input_parser.parse(input_text)
            calc_result = self.calculation_engine.calculate_total(parsed_result)
            
            # Update preview area
            self.preview_area.update_preview(parsed_result)
            dpg.set_value("calculated_total", f"₹{calc_result.grand_total:,}")
            
            # Enable submit button
            dpg.configure_item("submit_btn", enabled=True)
            
            # Store result for submission
            self.current_parsed_result = parsed_result
            self.current_calc_result = calc_result
            
        except Exception as e:
            self.show_error_dialog(f"Preview failed: {str(e)}")
    
    def on_submit_clicked(self, sender, app_data, user_data):
        """Submit data to database"""
        try:
            # Validate all required fields
            if not self.validate_submission_fields():
                return
            
            # Create submission object
            submission = self.create_submission()
            
            # Process submission
            result = self.data_processor.process_submission(submission)
            
            if result.success:
                self.show_success_dialog("Data submitted successfully!")
                self.clear_form()
                self.refresh_tables()
            else:
                self.show_error_dialog(f"Submission failed: {result.error}")
                
        except Exception as e:
            self.show_error_dialog(f"Submission error: {str(e)}")
```

## Separate Table Window System

### Table Window Implementation
```python
class TableWindow:
    """Separate window for all data tables with full-screen interface"""
    
    def __init__(self, gui_manager):
        self.gui_manager = gui_manager
        self.table_viewers = {}
        
    def create_window(self):
        """Create separate table window"""
        with dpg.window(
            label="RickyMama - Data Tables",
            tag="table_window",
            width=self.WINDOW_CONFIG['width'],
            height=self.WINDOW_CONFIG['height'],
            min_width=self.WINDOW_CONFIG['min_width'],
            min_height=self.WINDOW_CONFIG['min_height'],
            pos=self.WINDOW_CONFIG['pos'],
            on_close=self.on_window_close
        ):
            self.create_table_layout()
    
    def create_table_layout(self):
        """Create tabbed interface for tables"""
        with dpg.tab_bar(tag="main_table_tabs"):
            # Customers tab
            with dpg.tab(label="Customers", tag="customers_tab"):
                self.table_viewers['customers'] = CustomersTableViewer()
                self.table_viewers['customers'].create_layout()
            
            # Universal log tab
            with dpg.tab(label="Universal", tag="universal_tab"):
                self.table_viewers['universal'] = UniversalTableViewer()
                self.table_viewers['universal'].create_layout()
            
            # Pana table tab
            with dpg.tab(label="Pana", tag="pana_tab"):
                self.table_viewers['pana'] = PanaTableViewer()
                self.table_viewers['pana'].create_layout()
            
            # Time table tab
            with dpg.tab(label="Time", tag="time_tab"):
                self.table_viewers['time'] = TimeTableViewer()
                self.table_viewers['time'].create_layout()
            
            # Summary tab
            with dpg.tab(label="Summary", tag="summary_tab"):
                self.table_viewers['summary'] = TotalSummaryViewer()
                self.table_viewers['summary'].create_layout()
            
            # Export tab
            with dpg.tab(label="Export", tag="export_tab"):
                self.table_viewers['export'] = ExportManagerGUI()
                self.table_viewers['export'].create_layout()
    
    def on_window_close(self):
        """Handle window close event"""
        dpg.hide_item("table_window")
        
    def refresh_all_tables(self):
        """Refresh data in all table viewers"""
        for viewer in self.table_viewers.values():
            if hasattr(viewer, 'refresh_data'):
                viewer.refresh_data()

### Enhanced Table Interface Features
```python
class EnhancedTableViewer:
    """Base class for enhanced table viewers with full-screen capabilities"""
    
    def create_enhanced_controls(self):
        """Create enhanced control panel for table"""
        with dpg.group(horizontal=True):
            # Search box
            dpg.add_input_text(
                hint="Search...",
                tag=f"{self.table_name}_search",
                callback=self.on_search_changed,
                width=200
            )
            
            dpg.add_spacer(width=10)
            
            # Quick filters
            dpg.add_button(
                label="Today",
                callback=lambda: self.apply_date_filter('today'),
                width=60
            )
            
            dpg.add_button(
                label="This Week",
                callback=lambda: self.apply_date_filter('week'),
                width=80
            )
            
            dpg.add_button(
                label="This Month",
                callback=lambda: self.apply_date_filter('month'),
                width=80
            )
            
            dpg.add_spacer(width=20)
            
            # Export button
            dpg.add_button(
                label=f"Export {self.table_name.title()}",
                callback=self.export_table_data,
                width=100
            )
            
            dpg.add_spacer(width=10)
            
            # Refresh button
            dpg.add_button(
                label="Refresh",
                callback=self.refresh_data,
                width=80
            )
    
    def create_pagination_controls(self):
        """Create pagination controls for large datasets"""
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="<<",
                callback=lambda: self.goto_page(1),
                width=30
            )
            
            dpg.add_button(
                label="<",
                callback=self.previous_page,
                width=30
            )
            
            dpg.add_text("Page:")
            dpg.add_input_int(
                tag=f"{self.table_name}_page_input",
                default_value=1,
                min_value=1,
                max_value=1,
                width=60,
                callback=self.on_page_changed
            )
            
            dpg.add_text("of")
            dpg.add_text("1", tag=f"{self.table_name}_total_pages")
            
            dpg.add_button(
                label=">",
                callback=self.next_page,
                width=30
            )
            
            dpg.add_button(
                label=">>",
                callback=lambda: self.goto_page(self.total_pages),
                width=30
            )
            
            dpg.add_spacer(width=20)
            
            # Records per page
            dpg.add_text("Show:")
            dpg.add_combo(
                items=["25", "50", "100", "250", "500"],
                default_value="50",
                tag=f"{self.table_name}_page_size",
                callback=self.on_page_size_changed,
                width=60
            )
            dpg.add_text("records")
```

### Enhanced Universal Table Viewer
```python
class UniversalTableViewer(EnhancedTableViewer):
    """Universal log table with enhanced filtering, sorting, and full-screen view"""
    
    def __init__(self):
        self.table_name = "universal"
        self.current_page = 1
        self.page_size = 50
        self.total_records = 0
        self.total_pages = 1
    
    def create_layout(self):
        # Enhanced controls
        self.create_enhanced_controls()
        
        dpg.add_separator()
        
        # Advanced filters section
        with dpg.collapsing_header(label="Advanced Filters", default_open=False):
            with dpg.group(horizontal=True):
                # Date range filter
                dpg.add_date_picker(tag="universal_filter_start_date", label="From")
                dpg.add_date_picker(tag="universal_filter_end_date", label="To")
                
                dpg.add_spacer(width=20)
                
                # Customer filter
                dpg.add_combo(
                    items=["All Customers"] + self.get_customer_names(),
                    tag="universal_filter_customer",
                    label="Customer",
                    width=150
                )
                
                # Bazar filter
                dpg.add_combo(
                    items=["All Bazars"] + self.get_bazar_names(),
                    tag="universal_filter_bazar",
                    label="Bazar",
                    width=100
                )
                
                # Entry type filter
                dpg.add_combo(
                    items=["All Types", "PANA", "TYPE", "TIME_DIRECT", "TIME_MULTI"],
                    tag="universal_filter_type",
                    label="Type",
                    width=120
                )
            
            dpg.add_spacer(height=10)
            
            with dpg.group(horizontal=True):
                # Value range filters
                dpg.add_text("Value Range:")
                dpg.add_input_int(
                    tag="universal_filter_min_value",
                    label="Min",
                    default_value=0,
                    width=80
                )
                dpg.add_input_int(
                    tag="universal_filter_max_value",
                    label="Max",
                    default_value=999999,
                    width=80
                )
                
                dpg.add_spacer(width=20)
                
                # Apply and clear filter buttons
                dpg.add_button(
                    label="Apply Filters",
                    callback=self.apply_advanced_filters,
                    width=100
                )
                
                dpg.add_button(
                    label="Clear Filters",
                    callback=self.clear_all_filters,
                    width=100
                )
        
        dpg.add_separator()
        
        # Full-screen table with enhanced features
        with dpg.table(
            header_row=True,
            resizable=True,
            sortable=True,
            scrollY=True,
            scrollX=True,
            tag="universal_table",
            height=-50  # Leave space for pagination
        ):
            # Define columns with better widths
            dpg.add_table_column(label="ID", width=60, no_sort=False)
            dpg.add_table_column(label="Customer", width=150, no_sort=False)
            dpg.add_table_column(label="Date", width=100, no_sort=False)
            dpg.add_table_column(label="Bazar", width=80, no_sort=False)
            dpg.add_table_column(label="Number", width=80, no_sort=False)
            dpg.add_table_column(label="Value", width=100, no_sort=False)
            dpg.add_table_column(label="Type", width=120, no_sort=False)
            dpg.add_table_column(label="Created", width=140, no_sort=False)
            dpg.add_table_column(label="Actions", width=100, no_sort=True)
        
        dpg.add_separator()
        
        # Pagination controls
        self.create_pagination_controls()
        
        # Load initial data
        self.load_table_data()
    
    def load_table_data(self, filters=None):
        """Load and display table data with optional filters"""
        # Clear existing rows
        dpg.delete_item("universal_table", children_only=True, slot=1)
        
        # Get data from database
        data = self.db_manager.get_universal_log_entries(filters)
        
        # Add rows
        for row in data:
            with dpg.table_row(parent="universal_table"):
                dpg.add_text(str(row.id))
                dpg.add_text(row.customer_name)
                dpg.add_text(row.entry_date.strftime("%d-%m-%Y"))
                dpg.add_text(row.bazar)
                dpg.add_text(str(row.number))
                dpg.add_text(f"₹{row.value:,}")
                dpg.add_text(row.entry_type)
                dpg.add_text(row.created_at.strftime("%d-%m-%Y %H:%M"))
```

### Pana Table Viewer
```python
class PanaTableViewer:
    """Pana table with bazar and date filtering"""
    
    def create_layout(self):
        # Controls
        with dpg.group(horizontal=True):
            # Bazar selection
            dpg.add_combo(
                items=self.get_bazar_names(),
                tag="pana_bazar_filter",
                label="Bazar",
                callback=self.on_filter_changed
            )
            
            # Date selection
            dpg.add_date_picker(
                tag="pana_date_filter",
                label="Date",
                callback=self.on_filter_changed
            )
            
            # Reset to today button
            dpg.add_button(
                label="Today",
                callback=self.reset_to_today
            )
        
        dpg.add_separator()
        
        # Pana table grid (10 columns × 20 rows layout)
        with dpg.table(
            header_row=False,
            borders_innerH=True,
            borders_innerV=True,
            borders_outerH=True,
            borders_outerV=True,
            tag="pana_grid_table"
        ):
            # Create 20 columns (Number | Value pairs × 10)
            for i in range(20):
                column_label = "Num" if i % 2 == 0 else "Val"
                dpg.add_table_column(label=column_label, width=60)
        
        self.load_pana_data()
    
    def load_pana_data(self):
        """Load pana table data in grid format"""
        bazar = dpg.get_value("pana_bazar_filter")
        date = self.get_selected_date("pana_date_filter")
        
        if not bazar or not date:
            return
        
        # Get pana data for bazar and date
        pana_data = self.db_manager.get_pana_table_data(bazar, date)
        
        # Clear existing data
        dpg.delete_item("pana_grid_table", children_only=True, slot=1)
        
        # Create grid layout matching specification
        pana_layout = self.get_pana_layout()
        
        for row_nums in pana_layout:
            with dpg.table_row(parent="pana_grid_table"):
                for num in row_nums:
                    if num is None:
                        dpg.add_text("")  # Empty cell
                        dpg.add_text("")  # Empty value
                    else:
                        value = pana_data.get(num, 0)
                        
                        # Number cell
                        dpg.add_text(str(num))
                        
                        # Value cell with color coding
                        if value > 0:
                            dpg.add_text(
                                f"₹{value}",
                                color=self.COLORS['success']
                            )
                        else:
                            dpg.add_text("0", color=self.COLORS['text'])
```

## Dialog System

### New Customer Dialog
```python
class NewCustomerDialog:
    """Dialog for adding new customers"""
    
    def show(self):
        with dpg.window(
            label="Add New Customer",
            modal=True,
            width=400,
            height=200,
            tag="new_customer_dialog"
        ):
            dpg.add_text("Customer Name:")
            dpg.add_input_text(
                tag="new_customer_name",
                width=-1,
                hint="Enter customer name"
            )
            
            dpg.add_spacer(height=20)
            
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Add Customer",
                    callback=self.add_customer,
                    width=120
                )
                
                dpg.add_spacer(width=10)
                
                dpg.add_button(
                    label="Cancel",
                    callback=lambda: dpg.delete_item("new_customer_dialog"),
                    width=120
                )
    
    def add_customer(self):
        """Add new customer to database"""
        name = dpg.get_value("new_customer_name").strip()
        
        if not name:
            self.show_error("Customer name cannot be empty")
            return
        
        try:
            customer_id = self.db_manager.add_customer(name)
            self.show_success(f"Customer '{name}' added with ID: {customer_id}")
            
            # Refresh customer list
            self.refresh_customer_dropdown()
            
            # Close dialog
            dpg.delete_item("new_customer_dialog")
            
        except Exception as e:
            self.show_error(f"Failed to add customer: {str(e)}")
```

### Error and Success Dialogs
```python
class MessageDialogs:
    """Standard message dialogs"""
    
    def show_error(self, message: str, title: str = "Error"):
        """Show error dialog"""
        with dpg.window(
            label=title,
            modal=True,
            width=400,
            height=150,
            tag="error_dialog"
        ):
            dpg.add_text(message, color=self.COLORS['danger'])
            
            dpg.add_spacer(height=20)
            
            dpg.add_button(
                label="OK",
                callback=lambda: dpg.delete_item("error_dialog"),
                width=100
            )
    
    def show_success(self, message: str, title: str = "Success"):
        """Show success dialog"""
        with dpg.window(
            label=title,
            modal=True,
            width=400,
            height=150,
            tag="success_dialog"
        ):
            dpg.add_text(message, color=self.COLORS['success'])
            
            dpg.add_spacer(height=20)
            
            dpg.add_button(
                label="OK",
                callback=lambda: dpg.delete_item("success_dialog"),
                width=100
            )
```

## Export Interface

### Export Manager GUI
```python
class ExportManagerGUI:
    """GUI for data export functionality"""
    
    def create_layout(self):
        dpg.add_text("Export Data", style={'font_size': 18, 'bold': True})
        
        dpg.add_separator()
        
        # Table selection
        dpg.add_text("Select Tables to Export:")
        
        with dpg.group():
            dpg.add_checkbox(label="Customers", tag="export_customers", default_value=True)
            dpg.add_checkbox(label="Universal Log", tag="export_universal", default_value=True)
            dpg.add_checkbox(label="Pana Table", tag="export_pana", default_value=False)
            dpg.add_checkbox(label="Time Table", tag="export_time", default_value=False)
            dpg.add_checkbox(label="Customer Summary", tag="export_summary", default_value=True)
        
        dpg.add_spacer(height=20)
        
        # Date range selection
        dpg.add_text("Date Range (for log tables):")
        
        with dpg.group(horizontal=True):
            dpg.add_date_picker(tag="export_start_date", label="From")
            dpg.add_date_picker(tag="export_end_date", label="To")
        
        dpg.add_spacer(height=20)
        
        # Format selection
        dpg.add_text("Export Format:")
        dpg.add_radio_button(
            items=["CSV", "Excel"],
            tag="export_format",
            default_value="CSV",
            horizontal=True
        )
        
        dpg.add_spacer(height=20)
        
        # Export buttons
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Export Data",
                callback=self.export_data,
                width=120
            )
            
            dpg.add_spacer(width=20)
            
            dpg.add_button(
                label="Full Backup",
                callback=self.create_full_backup,
                width=120
            )
        
        dpg.add_spacer(height=20)
        
        # Progress bar
        dpg.add_progress_bar(
            tag="export_progress",
            width=-1,
            overlay="Ready to export..."
        )
```

## Theme and Styling

### Application Theme
```python
class RickyMamaTheme:
    """Custom theme for RickyMama application"""
    
    def setup_theme(self):
        with dpg.theme() as self.app_theme:
            with dpg.theme_component(dpg.mvAll):
                # Window styling
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 4)
                
                # Colors
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (248, 249, 250, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (255, 255, 255, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (41, 128, 185, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (52, 152, 219, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (22, 160, 133, 255))
                
                # Text
                dpg.add_theme_color(dpg.mvThemeCol_Text, (52, 58, 64, 255))
                
        # Apply theme globally
        dpg.bind_theme(self.app_theme)
```

## Multi-Window Application Architecture

### Window Management System
```python
class WindowManager:
    """Manages multiple application windows"""
    
    def __init__(self):
        self.main_window = None
        self.table_window = None
        self.active_windows = []
        
    def initialize_windows(self):
        """Initialize all application windows"""
        # Create main entry window
        self.main_window = MainWindow(self)
        self.main_window.create_window()
        
        # Table window is created on demand
        self.table_window = None
        
    def show_table_window(self):
        """Show or create table window"""
        if self.table_window is None:
            self.table_window = TableWindow(self)
            self.table_window.create_window()
            self.active_windows.append(self.table_window)
        else:
            dpg.show_item("table_window")
            dpg.focus_item("table_window")
    
    def close_table_window(self):
        """Close table window"""
        if self.table_window:
            dpg.hide_item("table_window")
    
    def refresh_table_data(self):
        """Refresh table data after entry submission"""
        if self.table_window:
            self.table_window.refresh_all_tables()

### Responsive Design for Separate Windows
```python
class ResponsiveLayout:
    """Handles responsive layout adjustments for both windows"""
    
    def __init__(self, window_manager):
        self.window_manager = window_manager
        dpg.set_viewport_resize_callback(self.on_main_window_resize)
        
    def on_main_window_resize(self, sender, app_data):
        """Adjust main window layout when resized"""
        width, height = app_data
        
        # Adjust input areas based on available space
        input_height = max(150, (height - 500) // 2)
        dpg.configure_item("input_text_area", height=input_height)
        dpg.configure_item("preview_text_area", height=input_height)
        
        # Adjust form width
        form_width = max(600, width - 100)
        if dpg.does_item_exist("entry_form_group"):
            dpg.configure_item("entry_form_group", width=form_width)
    
    def on_table_window_resize(self, sender, app_data):
        """Adjust table window layout when resized"""
        width, height = app_data
        
        # Calculate available height for tables (minus controls and pagination)
        table_height = max(400, height - 200)
        
        # Update all table heights in table window
        table_tags = ["universal_table", "pana_grid_table", "time_table", 
                     "customers_table", "summary_table"]
        
        for table_tag in table_tags:
            if dpg.does_item_exist(table_tag):
                dpg.configure_item(table_tag, height=table_height)

### Window Communication
```python
class WindowCommunication:
    """Handles communication between main and table windows"""
    
    def __init__(self, window_manager):
        self.window_manager = window_manager
        
    def on_data_submitted(self, submission_result):
        """Called when data is successfully submitted in main window"""
        if submission_result.success:
            # Refresh table window if open
            self.window_manager.refresh_table_data()
            
            # Show success notification
            self.show_success_notification("Data submitted successfully!")
            
            # Optionally switch focus to table window
            if dpg.does_item_exist("table_window"):
                self.window_manager.show_table_window()
    
    def on_table_action(self, action_type, data):
        """Handle actions from table window that affect main window"""
        if action_type == "edit_entry":
            # Pre-fill main window with selected entry data
            self.prefill_main_form(data)
            dpg.focus_item("main_window")
            
        elif action_type == "new_customer":
            # Refresh customer dropdown in main window
            self.refresh_customer_dropdown()
    
    def show_success_notification(self, message):
        """Show temporary success notification"""
        with dpg.window(
            label="Success",
            modal=False,
            width=300,
            height=100,
            tag="success_notification",
            pos=(200, 100),
            no_resize=True,
            no_move=True
        ):
            dpg.add_text(message, color=(39, 174, 96, 255))
            
        # Auto-close after 3 seconds
        def close_notification():
            if dpg.does_item_exist("success_notification"):
                dpg.delete_item("success_notification")
                
        # Schedule close (simplified - in real implementation use timer)
        dpg.split_frame(delay=3*60, callback=close_notification)  # 3 seconds at 60fps
```

## Key Benefits of Redesigned Architecture

### 1. **Enhanced User Experience**
- **Focused Data Entry**: Main window dedicated entirely to data entry without distractions
- **Full-Screen Tables**: Separate window provides maximum space for viewing and analyzing data
- **Improved Workflow**: Clear separation between data entry and data viewing tasks
- **Better Multitasking**: Users can keep both windows open simultaneously

### 2. **Technical Advantages**
- **Better Performance**: Tables load independently without affecting main form responsiveness
- **Memory Efficiency**: Table data only loaded when needed
- **Scalability**: Each window can be optimized for its specific purpose
- **Modularity**: Easier maintenance and feature additions

### 3. **Improved Table Features**
- **Enhanced Filtering**: Advanced filter options with more screen space
- **Better Pagination**: Full pagination controls for large datasets
- **Export Options**: Table-specific export functionality
- **Search Capabilities**: Global search across all table data
- **Sorting & Columns**: Enhanced column management and sorting options

### 4. **Window Management Benefits**
- **Independent Sizing**: Each window can be sized optimally for its content
- **Multi-Monitor Support**: Windows can be placed on different monitors
- **Context Switching**: Easy switching between data entry and data review
- **Background Operations**: Tables can update in background while entering data

This redesigned GUI specification provides a more professional, efficient interface that separates concerns and optimizes each window for its specific purpose, resulting in better user experience and improved workflow efficiency.