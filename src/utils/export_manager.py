"""Export Manager for backing up data to CSV/Excel formats"""

import csv
import os
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

class ExportManager:
    """Handles data export to CSV and other formats for backup"""
    
    def __init__(self, export_dir: str = "./exports"):
        """
        Initialize export manager
        
        Args:
            export_dir: Directory to save export files
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str, 
                     include_timestamp: bool = True) -> str:
        """
        Export data to CSV file
        
        Args:
            data: List of dictionaries to export
            filename: Base filename (without extension)
            include_timestamp: Whether to add timestamp to filename
            
        Returns:
            Path to exported file
        """
        if not data:
            raise ValueError("No data to export")
        
        # Create filename with optional timestamp
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"{filename}_{timestamp}.csv"
        else:
            csv_filename = f"{filename}.csv"
        
        filepath = self.export_dir / csv_filename
        
        # Get all unique keys from data
        all_keys = set()
        for row in data:
            all_keys.update(row.keys())
        
        fieldnames = sorted(list(all_keys))
        
        # Write CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                # Convert date objects to strings
                processed_row = {}
                for key, value in row.items():
                    if isinstance(value, (date, datetime)):
                        processed_row[key] = value.isoformat()
                    elif value is None:
                        processed_row[key] = ''
                    else:
                        processed_row[key] = str(value)
                
                writer.writerow(processed_row)
        
        return str(filepath)
    
    def export_universal_log(self, db_manager, filters: Optional[Dict[str, Any]] = None) -> str:
        """Export universal log entries to CSV"""
        # Get data from database
        entries = db_manager.get_universal_log_entries(filters or {}, limit=100000)
        
        # Convert to list of dicts
        data = []
        for entry in entries:
            data.append({
                'ID': entry['id'],
                'Customer_ID': entry['customer_id'],
                'Customer_Name': entry['customer_name'],
                'Date': entry['entry_date'],
                'Bazar': entry['bazar'],
                'Number': entry['number'],
                'Value': entry['value'],
                'Entry_Type': entry['entry_type'],
                'Source_Line': entry['source_line'],
                'Created_At': entry['created_at']
            })
        
        return self.export_to_csv(data, 'universal_log')
    
    def export_pana_table(self, db_manager, bazar: str, entry_date: str) -> str:
        """Export pana table for specific bazar and date"""
        # Get data from database
        entries = db_manager.get_pana_table_values(bazar, entry_date)
        
        # Convert to list of dicts
        data = []
        for entry in entries:
            data.append({
                'Number': entry['number'],
                'Value': entry['value'],
                'Bazar': bazar,
                'Date': entry_date
            })
        
        filename = f"pana_table_{bazar}_{entry_date.replace('-', '')}"
        return self.export_to_csv(data, filename)
    
    def export_time_table(self, db_manager, bazar: str, entry_date: str) -> str:
        """Export time table for specific bazar and date"""
        # Get data from database
        entries = db_manager.get_time_table_by_bazar_date(bazar, entry_date)
        
        # Convert to list of dicts
        data = []
        for entry in entries:
            row_data = {
                'Customer_Name': entry['customer_name'],
                '1': entry['col_1'],
                '2': entry['col_2'],
                '3': entry['col_3'],
                '4': entry['col_4'],
                '5': entry['col_5'],
                '6': entry['col_6'],
                '7': entry['col_7'],
                '8': entry['col_8'],
                '9': entry['col_9'],
                '0': entry['col_0'],
                'Total': entry['total']
            }
            data.append(row_data)
        
        filename = f"time_table_{bazar}_{entry_date.replace('-', '')}"
        return self.export_to_csv(data, filename)
    
    def export_customer_summary(self, db_manager, entry_date: str) -> str:
        """Export customer bazar summary for specific date"""
        # Get data from database
        entries = db_manager.get_customer_bazar_summary_by_date(entry_date)
        
        # Convert to list of dicts
        data = []
        for entry in entries:
            row_data = {
                'Customer_Name': entry['customer_name'],
                'T.O': entry['to_total'],
                'T.K': entry['tk_total'],
                'M.O': entry['mo_total'],
                'M.K': entry['mk_total'],
                'K.O': entry['ko_total'],
                'K.K': entry['kk_total'],
                'NMO': entry['nmo_total'],
                'NMK': entry['nmk_total'],
                'B.O': entry['bo_total'],
                'B.K': entry['bk_total'],
                'TOTAL': entry['grand_total']
            }
            data.append(row_data)
        
        filename = f"customer_summary_{entry_date.replace('-', '')}"
        return self.export_to_csv(data, filename)
    
    def export_all_tables(self, db_manager, entry_date: str, bazar: Optional[str] = None) -> Dict[str, str]:
        """
        Export all tables for a specific date
        
        Returns:
            Dictionary with table names as keys and file paths as values
        """
        exported_files = {}
        
        # Export universal log for the date
        filters = {'start_date': entry_date, 'end_date': entry_date}
        if bazar:
            filters['bazar'] = bazar
        
        try:
            exported_files['universal_log'] = self.export_universal_log(db_manager, filters)
        except Exception as e:
            print(f"Failed to export universal log: {e}")
        
        # Export customer summary
        try:
            exported_files['customer_summary'] = self.export_customer_summary(db_manager, entry_date)
        except Exception as e:
            print(f"Failed to export customer summary: {e}")
        
        # Export pana and time tables for each bazar if specified
        if bazar:
            try:
                exported_files[f'pana_table_{bazar}'] = self.export_pana_table(db_manager, bazar, entry_date)
            except Exception as e:
                print(f"Failed to export pana table for {bazar}: {e}")
            
            try:
                exported_files[f'time_table_{bazar}'] = self.export_time_table(db_manager, bazar, entry_date)
            except Exception as e:
                print(f"Failed to export time table for {bazar}: {e}")
        else:
            # Export for all bazars
            bazars = db_manager.get_all_bazars()
            for bazar_row in bazars:
                bazar_name = bazar_row['name']
                try:
                    exported_files[f'pana_table_{bazar_name}'] = self.export_pana_table(
                        db_manager, bazar_name, entry_date
                    )
                except Exception as e:
                    print(f"Failed to export pana table for {bazar_name}: {e}")
                
                try:
                    exported_files[f'time_table_{bazar_name}'] = self.export_time_table(
                        db_manager, bazar_name, entry_date
                    )
                except Exception as e:
                    print(f"Failed to export time table for {bazar_name}: {e}")
        
        # Save export metadata
        metadata = {
            'export_date': datetime.now().isoformat(),
            'data_date': entry_date,
            'bazar': bazar or 'all',
            'files': exported_files
        }
        
        metadata_file = self.export_dir / f"export_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return exported_files
    
    def get_export_history(self) -> List[Dict[str, Any]]:
        """Get list of previous exports"""
        metadata_files = list(self.export_dir.glob("export_metadata_*.json"))
        history = []
        
        for metadata_file in sorted(metadata_files, reverse=True):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    history.append(metadata)
            except Exception as e:
                print(f"Failed to read metadata file {metadata_file}: {e}")
        
        return history