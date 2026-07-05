import logging
import os

os.makedirs("logs", exist_ok=True)

def setup_logger():
    """Configures global logging to stream strictly to files, hiding console output."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    file_handler = logging.FileHandler("logs/bot.log", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    
    root_logger.addHandler(file_handler)