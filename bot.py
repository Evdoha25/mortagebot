"""
Mortgage Calculator Telegram Bot for Russia (2026)

A minimal Telegram bot that calculates monthly mortgage payments
using a simple step-by-step conversation.

Features:
- Simple linear flow: One question at a time
- Session-only storage: All data cleared when conversation ends
- Text-only interface: No complex buttons, just text input
- Basic validation: Only numbers accepted where required
"""

import logging
from typing import Dict, Any

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from config import (
    TELEGRAM_BOT_TOKEN,
    MIN_LOAN_TERM_YEARS,
    MAX_LOAN_TERM_YEARS,
    MIN_INTEREST_RATE,
    MAX_INTEREST_RATE,
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Conversation states
LOAN_AMOUNT, DOWN_PAYMENT, LOAN_TERM, INTEREST_RATE = range(4)

# In-memory session storage (per chat_id)
sessions: Dict[int, Dict[str, Any]] = {}


def format_currency(amount: float) -> str:
    """Format a number as Russian Rubles with thousand separators."""
    return f"{amount:,.0f}".replace(",", " ") + " RUB"


def parse_number(text: str) -> float | None:
    """
    Parse a number from user input.
    Handles both dot and comma as decimal separators.
    Returns None if parsing fails.
    """
    try:
        # Replace comma with dot for decimal separator
        cleaned = text.strip().replace(",", ".").replace(" ", "")
        return float(cleaned)
    except ValueError:
        return None


def calculate_monthly_payment(
    loan_amount: float,
    down_payment: float,
    years: int,
    annual_rate_percent: float,
) -> Dict[str, float]:
    """
    Calculate mortgage payment details using the annuity formula.
    
    Args:
        loan_amount: Total loan amount in RUB
        down_payment: Down payment amount in RUB
        years: Loan term in years
        annual_rate_percent: Annual interest rate as percentage (e.g., 12.5)
    
    Returns:
        Dictionary with calculation results:
        - principal: Actual borrowed amount
        - monthly_payment: Monthly payment amount
        - total_payment: Total amount to be paid
        - total_interest: Total interest to be paid
        - months: Total number of months
    """
    principal = loan_amount - down_payment
    months = years * 12
    
    if annual_rate_percent == 0:
        monthly_payment = principal / months
    else:
        monthly_rate = annual_rate_percent / 12 / 100
        monthly_payment = principal * (
            monthly_rate * (1 + monthly_rate) ** months
        ) / ((1 + monthly_rate) ** months - 1)
    
    total_payment = monthly_payment * months
    total_interest = total_payment - principal
    
    return {
        "principal": principal,
        "monthly_payment": monthly_payment,
        "total_payment": total_payment,
        "total_interest": total_interest,
        "months": months,
    }


def get_session(chat_id: int) -> Dict[str, Any]:
    """Get or create a session for the given chat_id."""
    if chat_id not in sessions:
        sessions[chat_id] = {
            "loan_amount": None,
            "down_payment": None,
            "loan_term": None,
            "interest_rate": None,
        }
    return sessions[chat_id]


def clear_session(chat_id: int) -> None:
    """Clear session data for the given chat_id."""
    if chat_id in sessions:
        del sessions[chat_id]
        logger.info(f"Session cleared for chat_id: {chat_id}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle /start command.
    Clears any existing session and begins new calculation.
    """
    chat_id = update.effective_chat.id
    
    # Clear any existing session
    clear_session(chat_id)
    
    # Create new session
    get_session(chat_id)
    
    welcome_message = (
        "🏠 *Mortgage Calculator 2026 (Russia)*\n\n"
        "I will help you calculate your monthly mortgage payment.\n"
        "All data is stored only during this session and will be deleted afterwards.\n\n"
        "*Step 1:* Enter the loan amount you want (in RUB):"
    )
    
    await update.message.reply_text(welcome_message, parse_mode="Markdown")
    return LOAN_AMOUNT


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = (
        "🏠 *Mortgage Calculator Bot*\n\n"
        "This bot helps you calculate monthly mortgage payments.\n\n"
        "*Commands:*\n"
        "/start - Begin new calculation\n"
        "/cancel - Cancel current calculation\n"
        "/help - Show this help message\n\n"
        "*How to use:*\n"
        "1. Send /start to begin\n"
        "2. Enter the loan amount\n"
        "3. Enter your down payment\n"
        "4. Enter loan term in years\n"
        "5. Enter interest rate\n"
        "6. Get your calculation results!\n\n"
        "⚠️ All data is deleted after calculation is complete."
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle /cancel command.
    Cancels current calculation and clears session data.
    """
    chat_id = update.effective_chat.id
    clear_session(chat_id)
    
    await update.message.reply_text(
        "❌ Calculation cancelled. All data has been deleted.\n\n"
        "Type /start to begin a new calculation."
    )
    
    return ConversationHandler.END


async def handle_loan_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle loan amount input."""
    chat_id = update.effective_chat.id
    text = update.message.text
    
    amount = parse_number(text)
    
    if amount is None or amount <= 0:
        await update.message.reply_text(
            "⚠️ Invalid input. Please enter a valid positive number.\n\n"
            "Example: 5000000"
        )
        return LOAN_AMOUNT
    
    session = get_session(chat_id)
    session["loan_amount"] = amount
    
    await update.message.reply_text(
        f"✅ Loan amount: {format_currency(amount)}\n\n"
        f"*Step 2:* Enter your down payment/savings (in RUB):",
        parse_mode="Markdown",
    )
    
    return DOWN_PAYMENT


async def handle_down_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle down payment input."""
    chat_id = update.effective_chat.id
    text = update.message.text
    
    amount = parse_number(text)
    session = get_session(chat_id)
    loan_amount = session.get("loan_amount", 0)
    
    if amount is None or amount < 0:
        await update.message.reply_text(
            "⚠️ Invalid input. Please enter a valid positive number (or 0 for no down payment).\n\n"
            "Example: 1000000"
        )
        return DOWN_PAYMENT
    
    if amount >= loan_amount:
        await update.message.reply_text(
            f"⚠️ Down payment ({format_currency(amount)}) cannot exceed or equal "
            f"loan amount ({format_currency(loan_amount)}).\n"
            "Please enter a smaller amount:"
        )
        return DOWN_PAYMENT
    
    session["down_payment"] = amount
    
    await update.message.reply_text(
        f"✅ Down payment: {format_currency(amount)}\n\n"
        f"*Step 3:* Enter loan term in years ({MIN_LOAN_TERM_YEARS}-{MAX_LOAN_TERM_YEARS}):",
        parse_mode="Markdown",
    )
    
    return LOAN_TERM


async def handle_loan_term(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle loan term input."""
    chat_id = update.effective_chat.id
    text = update.message.text
    
    years = parse_number(text)
    
    if years is None or not (MIN_LOAN_TERM_YEARS <= years <= MAX_LOAN_TERM_YEARS):
        await update.message.reply_text(
            f"⚠️ Please enter a number between {MIN_LOAN_TERM_YEARS} and {MAX_LOAN_TERM_YEARS} years.\n\n"
            "Example: 15"
        )
        return LOAN_TERM
    
    session = get_session(chat_id)
    session["loan_term"] = int(years)
    
    await update.message.reply_text(
        f"✅ Loan term: {int(years)} years\n\n"
        f"*Step 4:* Enter annual interest rate % "
        f"(e.g., 12.5):",
        parse_mode="Markdown",
    )
    
    return INTEREST_RATE


async def handle_interest_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle interest rate input and show calculation results."""
    chat_id = update.effective_chat.id
    text = update.message.text
    
    rate = parse_number(text)
    
    if rate is None or not (MIN_INTEREST_RATE <= rate <= MAX_INTEREST_RATE):
        await update.message.reply_text(
            f"⚠️ Please enter a rate between {MIN_INTEREST_RATE}% and {MAX_INTEREST_RATE}%.\n\n"
            "Example: 12.5"
        )
        return INTEREST_RATE
    
    session = get_session(chat_id)
    session["interest_rate"] = rate
    
    # Perform calculation
    result = calculate_monthly_payment(
        loan_amount=session["loan_amount"],
        down_payment=session["down_payment"],
        years=session["loan_term"],
        annual_rate_percent=rate,
    )
    
    # Format results
    results_message = (
        "📊 *CALCULATION RESULTS:*\n\n"
        f"• Loan Amount: {format_currency(session['loan_amount'])}\n"
        f"• Down Payment: {format_currency(session['down_payment'])}\n"
        f"• Loan Principal: {format_currency(result['principal'])}\n"
        f"• Loan Term: {session['loan_term']} years ({result['months']} months)\n"
        f"• Interest Rate: {rate:.1f}% per year\n\n"
        f"💸 *Monthly Payment:* ~{format_currency(result['monthly_payment'])}\n"
        f"💰 *Total Payment:* ~{format_currency(result['total_payment'])}\n"
        f"💎 *Total Interest:* ~{format_currency(result['total_interest'])}\n\n"
        "⚠️ _Note: This is an estimate. Actual terms may vary._\n"
        "_All your data has been deleted from memory._\n\n"
        "Type /start for new calculation."
    )
    
    # Clear session after showing results
    clear_session(chat_id)
    
    await update.message.reply_text(results_message, parse_mode="Markdown")
    
    return ConversationHandler.END


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown messages outside of conversation."""
    await update.message.reply_text(
        "👋 Hello! I'm a Mortgage Calculator Bot.\n\n"
        "Type /start to begin calculating your mortgage payment,\n"
        "or /help for more information."
    )


def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error(
            "TELEGRAM_BOT_TOKEN not found! "
            "Please set it in .env file or environment variables."
        )
        return
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LOAN_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_loan_amount)
            ],
            DOWN_PAYMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_down_payment)
            ],
            LOAN_TERM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_loan_term)
            ],
            INTEREST_RATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_interest_rate)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start),
        ],
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown))
    
    # Start polling
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
