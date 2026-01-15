import logging
from datetime import datetime
import os

def setup_logger():
    """Setup applicaiton logging"""
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    log_file = os.path.join(
        logs_dir, f"recruitment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler() 
            ]
        )
    return logging.getLogger("AI_Recruiter")