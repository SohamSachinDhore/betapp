"""RickyMama Application Core - Main application orchestrator"""

from typing import Optional
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config.config_manager import ConfigManager
from database.db_manager import DatabaseManager
from utils.logger import LoggerSetup
from utils.error_handler import ErrorHandler, get_error_handler

class RickyMamaApp:
    """Main application orchestrator"""
    
    def __init__(self, config_path: Optional[str] = None):
        # Initialize configuration
        self.config = ConfigManager(config_path or "./config/settings.json")
        
        # Validate configuration
        if not self.config.validate_config():
            raise RuntimeError("Invalid configuration")
        
        # Setup logging
        logging_config = self.config.get_logging_config()
        self.logger = LoggerSetup.setup_logger(__name__, logging_config)
        
        # Initialize error handler
        self.error_handler = ErrorHandler(self.logger)
        
        # Initialize database (without auto-initialization)
        db_config = self.config.get_database_config()
        self.db_manager = DatabaseManager(db_config['path'])
        
        # Initialize other components (will be added later)
        self.input_parser = None
        self.gui_manager = None
        self.export_manager = None
        
        self.logger.info("RickyMama application initialized successfully")
    
    def initialize_components(self):
        """Initialize all application components"""
        try:
            # Initialize database
            self.db_manager.initialize_database()
            self.logger.info("Database initialized")
            
            # Load pana reference data for validation
            pana_numbers = self._load_pana_numbers()
            self.logger.info(f"Loaded {len(pana_numbers)} pana reference numbers")
            
            # TODO: Initialize other components when ready
            # self.input_parser = InputParser(pana_numbers)
            # self.gui_manager = GUIManager(self)
            # self.export_manager = ExportManager(self.db_manager)
            
            return True
            
        except Exception as e:
            self.error_handler.handle_database_error("initialize_components", e)
            return False
    
    def _load_pana_numbers(self) -> set:
        """Load pana reference numbers from database"""
        try:
            query = "SELECT number FROM pana_numbers"
            results = self.db_manager.execute_query(query)
            return {row['number'] for row in results}
        except Exception as e:
            self.logger.warning(f"Failed to load pana numbers: {e}")
            return set()
    
    def run(self):
        """Main application entry point"""
        try:
            self.logger.info("Starting RickyMama application")
            
            # Initialize all components
            if not self.initialize_components():
                self.logger.error("Failed to initialize components")
                return False
            
            # TODO: Start GUI when ready
            # self.gui_manager.run_gui()
            
            self.logger.info("RickyMama application started successfully")
            print("RickyMama application core initialized successfully!")
            print("Database connection:", "OK" if self.db_manager else "FAILED")
            print("Configuration loaded:", "OK" if self.config else "FAILED")
            
            return True
            
        except Exception as e:
            self.error_handler.show_user_error(
                "Failed to start application",
                str(e),
                "Startup Error"
            )
            return False
    
    def shutdown(self):
        """Cleanup application resources"""
        try:
            self.logger.info("Shutting down RickyMama application")
            
            # Close database connections
            if self.db_manager:
                self.db_manager.close()
            
            # Shutdown logging
            LoggerSetup.shutdown()
            
            self.logger.info("Application shutdown complete")
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()


def create_app(config_path: Optional[str] = None) -> RickyMamaApp:
    """Factory function to create application instance"""
    return RickyMamaApp(config_path)


if __name__ == "__main__":
    # Test the core application
    with create_app() as app:
        success = app.run()
        if not success:
            sys.exit(1)