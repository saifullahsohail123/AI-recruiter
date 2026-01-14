#Streamlit web application
import streamlit as st
import asyncio
import os
from datetime import datetime
from pathlib import Pathlib
from streamlit_option_menu import option_menu
from agents.orchestrator import OrchestratorAgent
from utils.logger import setup_logger
from utils.exception import ResumeProcessingError

# Configure Streamlit page
st.set_page_config(
    page_title = "AI Recruiter Agency",
    page_icon = "🤖",
    layout = "wide"
    initial_sidebar_state = "expanded"
)

# Initialize logger
logger = setup_logger()


