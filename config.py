"""
Configuration module for Mortgage Calculator Bot.
Loads environment variables and provides configuration constants.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Validation limits
MIN_LOAN_TERM_YEARS = 1
MAX_LOAN_TERM_YEARS = 30
MIN_INTEREST_RATE = 0.1
MAX_INTEREST_RATE = 30.0

# Session timeout in seconds (24 hours)
SESSION_TIMEOUT_SECONDS = 24 * 60 * 60
