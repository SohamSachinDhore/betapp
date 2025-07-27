"""Data Processor for coordinating parsing, calculation, and database operations"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import date, datetime
from dataclasses import dataclass
from ..database.db_manager import DatabaseManager
from ..database.models import UniversalLogEntry, Customer, Bazar, EntryType
from ..business.calculation_engine import CalculationEngine, CalculationContext, BusinessCalculation
from ..parsing.mixed_input_parser import MixedInputParser
from ..parsing.type_table_parser import TypeTableLoader
from ..parsing.pana_parser import PanaValidator
from ..utils.logger import get_logger
from ..utils.error_handler import ProcessingError, DatabaseError
from ..utils.export_manager import ExportManager

@dataclass
class ProcessingResult:
    """Result of data processing operation"""
    success: bool
    calculation: Optional[BusinessCalculation] = None
    entries_saved: int = 0
    customer_id: int = 0
    customer_name: str = ""
    bazar: str = ""
    entry_date: Optional[date] = None
    error_message: str = ""
    processing_time_ms: int = 0
    universal_log_ids: List[int] = None
    
    def __post_init__(self):
        if self.universal_log_ids is None:
            self.universal_log_ids = []

@dataclass
class ProcessingContext:
    """Context for data processing operations"""
    customer_name: str
    bazar: str
    entry_date: date
    input_text: str
    validate_references: bool = True
    auto_create_customer: bool = True

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
    calc_result: Any = None

@dataclass
class MixedProcessingResult:
    """GUI-compatible result structure for mixed input processing"""
    success: bool
    pana_count: int = 0
    type_count: int = 0
    time_count: int = 0
    multi_count: int = 0
    direct_count: int = 0
    total_value: int = 0
    entries_saved: int = 0
    customer_id: int = 0
    customer_name: str = ""
    bazar: str = ""
    entry_date: Optional[date] = None
    error_message: str = ""
    processing_time_ms: int = 0
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []


class DataProcessor:
    """Main data processor for the RickyMama application"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize data processor with database manager
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.logger = get_logger(__name__)
        self.export_manager = ExportManager()
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize calculation engine and parsers with reference data"""
        try:
            # Load type table reference data
            type_loader = TypeTableLoader(self.db_manager)
            sp_table, dp_table, cp_table = type_loader.load_all_tables()
            
            # Load pana reference numbers
            pana_numbers = self._load_pana_numbers()
            
            # Initialize calculation engine
            self.calculation_engine = CalculationEngine(sp_table, dp_table, cp_table)
            
            # Initialize parsers with validators
            pana_validator = PanaValidator(pana_numbers) if pana_numbers else None
            type_validator = type_loader.create_validator()
            
            self.mixed_parser = MixedInputParser(
                pana_validator=pana_validator,
                type_validator=type_validator
            )
            
            self.logger.info("Data processor components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            # Initialize with minimal functionality
            self.calculation_engine = CalculationEngine()
            self.mixed_parser = MixedInputParser()
    
    def _load_pana_numbers(self) -> set:
        """Load pana reference numbers from database"""
        try:
            query = "SELECT number FROM pana_numbers"
            results = self.db_manager.execute_query(query)
            return {row['number'] for row in results}
        except Exception as e:
            self.logger.warning(f"Failed to load pana numbers: {e}")
            return set()
    
    def process_input(self, context: ProcessingContext) -> ProcessingResult:
        """
        Main processing entry point
        
        Coordinates parsing, calculation, and database storage
        
        Args:
            context: Processing context with customer, bazar, date, input data
            
        Returns:
            ProcessingResult with complete operation details
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Processing input for {context.customer_name} in {context.bazar}")
            
            # Step 1: Get or create customer
            customer = self._get_or_create_customer(context.customer_name, context.auto_create_customer)
            
            # Step 2: Validate bazar
            if not self._validate_bazar(context.bazar):
                return ProcessingResult(
                    success=False,
                    error_message=f"Invalid bazar: {context.bazar}"
                )
            
            # Step 3: Parse input
            parsed_result = self.mixed_parser.parse(context.input_text)
            
            if parsed_result.is_empty:
                return ProcessingResult(
                    success=False,
                    error_message="No valid entries found in input"
                )
            
            # Step 4: Calculate business logic
            calc_context = CalculationContext(
                customer_id=customer['id'],
                customer_name=customer['name'],
                entry_date=context.entry_date,
                bazar=context.bazar,
                source_data=parsed_result
            )
            
            calculation = self.calculation_engine.calculate(calc_context)
            
            # Step 5: Save to database
            universal_log_ids = self._save_universal_entries(calculation.universal_entries)
            
            # Step 6: Save to specific tables (pana_table, time_table, customer_bazar_summary)
            self._save_to_specific_tables(calculation.universal_entries)
            
            # Step 7: Export data for backup (optional, non-blocking)
            try:
                self.export_manager.export_all_tables(
                    self.db_manager, 
                    context.entry_date.isoformat(),
                    context.bazar
                )
                self.logger.info("Data exported successfully for backup")
            except Exception as e:
                self.logger.warning(f"Export failed (non-critical): {e}")
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Return success result
            return ProcessingResult(
                success=True,
                calculation=calculation,
                entries_saved=len(universal_log_ids),
                customer_id=customer['id'],
                customer_name=customer['name'],
                bazar=context.bazar,
                entry_date=context.entry_date,
                processing_time_ms=processing_time,
                universal_log_ids=universal_log_ids
            )
            
        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self.logger.error(f"Processing failed: {e}")
            
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time
            )
    
    def _get_or_create_customer(self, customer_name: str, auto_create: bool) -> Dict[str, Any]:
        """Get existing customer or create new one"""
        # Try to get existing customer
        customer = self.db_manager.get_customer_by_name(customer_name)
        
        if customer:
            return dict(customer)
        
        if not auto_create:
            raise ProcessingError(f"Customer '{customer_name}' not found and auto-creation disabled")
        
        # Create new customer
        try:
            customer_id = self.db_manager.add_customer(customer_name)
            self.logger.info(f"Created new customer: {customer_name} (ID: {customer_id})")
            
            # Return customer data
            return {
                'id': customer_id,
                'name': customer_name,
                'is_active': True,
                'created_at': datetime.now()
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to create customer '{customer_name}': {e}")
    
    def _validate_bazar(self, bazar: str) -> bool:
        """Validate that bazar exists and is active"""
        try:
            bazars = self.db_manager.get_all_bazars()
            valid_bazars = {bazar_row['name'] for bazar_row in bazars}
            return bazar in valid_bazars
        except Exception as e:
            self.logger.warning(f"Failed to validate bazar: {e}")
            # Allow processing to continue with warning
            return True
    
    def _save_universal_entries(self, entries: List[UniversalLogEntry]) -> List[int]:
        """Save universal log entries to database"""
        if not entries:
            return []
        
        try:
            # Convert entries to dictionaries for database insertion
            entry_dicts = []
            for entry in entries:
                entry_dict = {
                    'customer_id': entry.customer_id,
                    'customer_name': entry.customer_name,
                    'entry_date': entry.entry_date.isoformat() if isinstance(entry.entry_date, date) else entry.entry_date,
                    'bazar': entry.bazar,
                    'number': entry.number,
                    'value': entry.value,
                    'entry_type': entry.entry_type.value if hasattr(entry.entry_type, 'value') else str(entry.entry_type),
                    'source_line': entry.source_line
                }
                entry_dicts.append(entry_dict)
            
            # Save all entries
            self.db_manager.add_universal_log_entries(entry_dicts)
            
            self.logger.info(f"Saved {len(entries)} universal log entries")
            
            # Generate mock IDs (in a real implementation, you'd get these from the database)
            return list(range(1, len(entries) + 1))
            
        except Exception as e:
            raise DatabaseError(f"Failed to save universal entries: {e}")
    
    def _save_to_specific_tables(self, entries: List[UniversalLogEntry]) -> None:
        """Save entries to their specific tables based on entry type"""
        if not entries:
            return
        
        try:
            # Group entries by type for efficient processing
            pana_entries = []
            direct_entries = []
            time_entries_by_customer = {}  # {(customer_id, bazar, date): {column: value}}
            bazar_totals_by_customer = {}  # {(customer_id, date): {bazar: total}}
            type_entries = []  # TYPE entries need expansion to pana numbers
            
            for entry in entries:
                # Track totals for customer_bazar_summary
                key = (entry.customer_id, entry.customer_name, entry.entry_date)
                if key not in bazar_totals_by_customer:
                    bazar_totals_by_customer[key] = {}
                if entry.bazar not in bazar_totals_by_customer[key]:
                    bazar_totals_by_customer[key][entry.bazar] = 0
                bazar_totals_by_customer[key][entry.bazar] += entry.value
                
                # Process based on entry type
                if entry.entry_type == EntryType.PANA:
                    pana_entries.append(entry)
                elif entry.entry_type == EntryType.DIRECT:
                    direct_entries.append(entry)
                elif entry.entry_type == EntryType.TYPE:
                    type_entries.append(entry)
                elif entry.entry_type in [EntryType.TIME_DIRECT, EntryType.TIME_MULTI]:
                    # Time entries (both direct and multiplication)
                    time_key = (entry.customer_id, entry.customer_name, entry.bazar, entry.entry_date)
                    if time_key not in time_entries_by_customer:
                        time_entries_by_customer[time_key] = {}
                    
                    # entry.number is the column number (0-9)
                    if entry.number not in time_entries_by_customer[time_key]:
                        time_entries_by_customer[time_key][entry.number] = 0
                    time_entries_by_customer[time_key][entry.number] += entry.value
            
            # Save pana entries
            for entry in pana_entries:
                date_str = entry.entry_date.isoformat() if isinstance(entry.entry_date, date) else entry.entry_date
                self.db_manager.update_pana_table_entry(
                    entry.bazar, date_str, entry.number, entry.value
                )
            
            if pana_entries:
                self.logger.info(f"Updated {len(pana_entries)} pana table entries")
            
            # Save direct entries to pana table
            for entry in direct_entries:
                date_str = entry.entry_date.isoformat() if isinstance(entry.entry_date, date) else entry.entry_date
                self.db_manager.update_pana_table_entry(
                    entry.bazar, date_str, entry.number, entry.value
                )
            
            if direct_entries:
                self.logger.info(f"Updated {len(direct_entries)} direct entries to pana table")
            
            # TYPE entries are automatically handled by the database trigger tr_update_pana_table
            # No manual expansion needed - the calculation engine already created individual universal_log entries
            # and the trigger updates pana_table accordingly
            if type_entries:
                self.logger.info(f"Processed {len(type_entries)} TYPE entries via database trigger")
            
            # Save time table entries
            for (customer_id, customer_name, bazar, entry_date), column_values in time_entries_by_customer.items():
                date_str = entry_date.isoformat() if isinstance(entry_date, date) else entry_date
                self.db_manager.update_time_table_entry(
                    customer_id, customer_name, bazar, date_str, column_values
                )
            
            if time_entries_by_customer:
                self.logger.info(f"Updated {len(time_entries_by_customer)} time table entries")
            
            # Save customer bazar summaries
            for (customer_id, customer_name, entry_date), bazar_totals in bazar_totals_by_customer.items():
                date_str = entry_date.isoformat() if isinstance(entry_date, date) else entry_date
                self.db_manager.update_customer_bazar_summary(
                    customer_id, customer_name, date_str, bazar_totals
                )
            
            if bazar_totals_by_customer:
                self.logger.info(f"Updated {len(bazar_totals_by_customer)} customer bazar summaries")
            
        except Exception as e:
            self.logger.error(f"Failed to save to specific tables: {e}")
            # Don't raise here - universal log is already saved, these are supplementary
    
    def _expand_type_entry(self, entry: UniversalLogEntry) -> List[int]:
        """
        Expand TYPE table entry to constituent pana numbers
        For TYPE entries, entry.number contains the column and table type info
        """
        try:
            # Extract table type and column from source_line
            # Expected format: "1SP=100" where column=1, table_type=SP
            source_line = entry.source_line or ""
            import re
            
            # Parse the type entry format
            match = re.match(r'(\d+)(SP|DP|CP)\s*=\s*\d+', source_line, re.IGNORECASE)
            if not match:
                self.logger.warning(f"Could not parse TYPE entry: {source_line}")
                return []
            
            column = int(match.group(1))
            table_type = match.group(2).upper()
            
            # Get numbers from appropriate table
            if table_type == 'SP':
                numbers = self.calculation_engine.sp_table.get(column, set())
            elif table_type == 'DP':
                numbers = self.calculation_engine.dp_table.get(column, set())
            elif table_type == 'CP':
                numbers = self.calculation_engine.cp_table.get(column, set())
            else:
                self.logger.warning(f"Unknown table type: {table_type}")
                return []
            
            return list(numbers)
            
        except Exception as e:
            self.logger.error(f"Failed to expand TYPE entry: {e}")
            return []
    
    def get_customer_summary(self, customer_name: str, start_date: Optional[date] = None, 
                           end_date: Optional[date] = None) -> Dict[str, Any]:
        """Get summary data for a customer"""
        try:
            customer = self.db_manager.get_customer_by_name(customer_name)
            if not customer:
                return {'error': f"Customer '{customer_name}' not found"}
            
            # Build filters
            filters = {'customer_id': customer['id']}
            if start_date:
                filters['start_date'] = start_date.isoformat()
            if end_date:
                filters['end_date'] = end_date.isoformat()
            
            # Get universal log entries
            entries = self.db_manager.get_universal_log_entries(filters, limit=10000)
            
            # Calculate summary statistics
            total_value = sum(entry['value'] for entry in entries)
            bazar_totals = {}
            entry_type_totals = {}
            
            for entry in entries:
                # Bazar totals
                bazar = entry['bazar']
                bazar_totals[bazar] = bazar_totals.get(bazar, 0) + entry['value']
                
                # Entry type totals
                entry_type = entry['entry_type']
                entry_type_totals[entry_type] = entry_type_totals.get(entry_type, 0) + entry['value']
            
            return {
                'customer_id': customer['id'],
                'customer_name': customer['name'],
                'total_entries': len(entries),
                'total_value': total_value,
                'date_range': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None
                },
                'bazar_totals': bazar_totals,
                'entry_type_totals': entry_type_totals,
                'last_entry_date': max([entry['created_at'] for entry in entries]) if entries else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get customer summary: {e}")
            return {'error': str(e)}
    
    def get_bazar_summary(self, bazar: str, target_date: date) -> Dict[str, Any]:
        """Get summary data for a bazar on specific date"""
        try:
            # Build filters
            filters = {
                'bazar': bazar,
                'start_date': target_date.isoformat(),
                'end_date': target_date.isoformat()
            }
            
            # Get universal log entries
            entries = self.db_manager.get_universal_log_entries(filters, limit=10000)
            
            # Calculate summary statistics
            total_value = sum(entry['value'] for entry in entries)
            customer_totals = {}
            entry_type_totals = {}
            number_frequencies = {}
            
            for entry in entries:
                # Customer totals
                customer = entry['customer_name']
                customer_totals[customer] = customer_totals.get(customer, 0) + entry['value']
                
                # Entry type totals
                entry_type = entry['entry_type']
                entry_type_totals[entry_type] = entry_type_totals.get(entry_type, 0) + entry['value']
                
                # Number frequencies
                number = entry['number']
                if number not in number_frequencies:
                    number_frequencies[number] = {'count': 0, 'total_value': 0}
                number_frequencies[number]['count'] += 1
                number_frequencies[number]['total_value'] += entry['value']
            
            # Sort customer totals
            sorted_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'bazar': bazar,
                'date': target_date.isoformat(),
                'total_entries': len(entries),
                'total_value': total_value,
                'unique_customers': len(customer_totals),
                'customer_totals': dict(sorted_customers),
                'entry_type_totals': entry_type_totals,
                'top_numbers': sorted(
                    [(num, data['total_value']) for num, data in number_frequencies.items()],
                    key=lambda x: x[1], reverse=True
                )[:10]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get bazar summary: {e}")
            return {'error': str(e)}
    
    def get_available_bazars(self) -> List[Dict[str, Any]]:
        """Get list of available bazars"""
        try:
            bazars = self.db_manager.get_all_bazars()
            return [dict(bazar) for bazar in bazars]
        except Exception as e:
            self.logger.error(f"Failed to get bazars: {e}")
            return []
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get overall processing statistics"""
        try:
            # Get total counts from database
            customer_count_query = "SELECT COUNT(*) as count FROM customers WHERE is_active = 1"
            customer_count = self.db_manager.execute_query(customer_count_query)[0]['count']
            
            entry_count_query = "SELECT COUNT(*) as count FROM universal_log"
            entry_count = self.db_manager.execute_query(entry_count_query)[0]['count']
            
            # Get recent activity
            recent_query = """
                SELECT entry_date, COUNT(*) as daily_entries, SUM(value) as daily_total
                FROM universal_log 
                WHERE entry_date >= date('now', '-30 days')
                GROUP BY entry_date 
                ORDER BY entry_date DESC 
                LIMIT 30
            """
            recent_activity = self.db_manager.execute_query(recent_query)
            
            return {
                'total_customers': customer_count,
                'total_entries': entry_count,
                'recent_activity': [dict(row) for row in recent_activity],
                'parser_components': {
                    'mixed_parser': 'active',
                    'calculation_engine': 'active',
                    'type_table_references': bool(self.calculation_engine.sp_table or 
                                                 self.calculation_engine.dp_table or 
                                                 self.calculation_engine.cp_table)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get processing statistics: {e}")
            return {'error': str(e)}
    
    def process_mixed_input(self, context: ProcessingContext) -> 'MixedProcessingResult':
        """
        Process mixed input with GUI-compatible result structure
        
        Args:
            context: Processing context with customer, bazar, date, input data
            
        Returns:
            MixedProcessingResult with GUI-compatible attributes
        """
        # Use the main processing method
        result = self.process_input(context)
        
        # Convert to GUI-compatible result
        if result.success and result.calculation:
            # Parse the input again to get entry counts
            parsed_result = self.mixed_parser.parse(context.input_text)
            
            # Count entries by type
            pana_count = len(parsed_result.pana_entries)
            type_count = len(parsed_result.type_entries)
            time_count = len(parsed_result.time_entries)
            multi_count = len(parsed_result.multi_entries)
            direct_count = len(parsed_result.direct_entries)
            
            # Use calculation totals for total value
            total_value = result.calculation.grand_total
            
            return MixedProcessingResult(
                success=True,
                pana_count=pana_count,
                type_count=type_count,
                time_count=time_count,
                multi_count=multi_count,
                direct_count=direct_count,
                total_value=total_value,
                entries_saved=result.entries_saved,
                customer_id=result.customer_id,
                customer_name=result.customer_name,
                bazar=result.bazar,
                entry_date=result.entry_date,
                processing_time_ms=result.processing_time_ms,
                validation_errors=[]
            )
        else:
            return MixedProcessingResult(
                success=False,
                error_message=result.error_message,
                validation_errors=[result.error_message] if result.error_message else []
            )


class BusinessValidator:
    """Business rule validation per specification"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = get_logger(__name__)
    
    def validate_submission(self, submission: EntrySubmission) -> Dict[str, Any]:
        """Comprehensive business validation per specification"""
        errors = []
        warnings = []
        
        try:
            # Rule: Customer must exist
            customer = self.db_manager.get_customer_by_id(submission.customer_id)
            if not customer:
                errors.append(f"Customer ID {submission.customer_id} not found")
            
            # Rule: Bazar must be valid
            bazars = self.db_manager.get_all_bazars()
            valid_bazars = {bazar['name'] for bazar in bazars}
            if submission.bazar not in valid_bazars:
                errors.append(f"Bazar {submission.bazar} not found")
            
            # Rule: Date cannot be in future
            if submission.date > date.today():
                errors.append("Entry date cannot be in the future")
            
            # Rule: Total must be positive
            if submission.expected_total < 0:
                errors.append("Total value cannot be negative")
            
            # Rule: Check for potential duplicates (simplified)
            if submission.input_text.strip() == "":
                errors.append("Input text cannot be empty")
                
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def validate_input_format(self, input_text: str) -> Dict[str, Any]:
        """Additional input format validation per specification"""
        errors = []
        
        lines = input_text.strip().split('\n')
        for i, line in enumerate(lines, 1):
            if not line.strip():
                continue
                
            # Check if line matches any known format (simplified validation)
            if not self._is_valid_format(line):
                errors.append(f"Line {i}: Unrecognized format - {line}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': []
        }
    
    def _is_valid_format(self, line: str) -> bool:
        """Check if line matches any known format"""
        import re
        
        # Multiplication format: 38x700
        if re.match(r'^\d+x\d+$', line.strip()):
            return True
            
        # Type table format: 1SP=100
        if re.match(r'^\d+(SP|DP|CP)\s*=\s*.*\d+.*$', line.strip(), re.IGNORECASE):
            return True
            
        # Time direct format: 1=100 or 0 1 3 5 = 900
        if re.match(r'^[\d\s]+\s*=\s*.*\d+.*$', line.strip()) and not re.search(r'[a-zA-Z]', line):
            return True
            
        # Pana format: numbers with equals
        if re.match(r'^[\d\s/+,*]+\s*=\s*.*\d+.*$', line.strip()):
            return True
            
        # Multiline pana: just numbers
        if re.match(r'^[\d\s/+,*]+$', line.strip()):
            return True
            
        return False