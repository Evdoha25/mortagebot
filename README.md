# Mortgage Calculator Telegram Bot (Russia 2026)

A minimal Telegram bot that calculates monthly mortgage payments using a simple step-by-step conversation. Built for the Russian market with RUB currency support.

## Features

- **Simple linear flow**: One question at a time
- **Session-only storage**: All data cleared when conversation ends (no database required)
- **Text-only interface**: No complex buttons, just text input
- **Basic validation**: Input validation with helpful error messages
- **Privacy-focused**: No data persistence, everything in RAM only

## User Flow

```
User: /start
Bot: "Welcome! Enter the loan amount you want (in RUB):"
User: 5000000
Bot: "Enter your down payment/savings (in RUB):"
User: 1000000
Bot: "Enter loan term in years (1-30):"
User: 15
Bot: "Enter annual interest rate % (e.g., 12.5):"
User: 12
Bot: [shows calculation results]
```

## Bot Commands

- `/start` - Begin new calculation (clears any existing session data)
- `/cancel` - Cancel current calculation and clear all data
- `/help` - Show brief help message

## Calculation Formula

The bot uses the standard annuity mortgage payment formula:

```
Monthly Payment = P * (r * (1 + r)^n) / ((1 + r)^n - 1)

Where:
- P = Principal (loan amount - down payment)
- r = Monthly interest rate (annual rate / 12 / 100)
- n = Total number of months (years * 12)
```

## Setup

### Prerequisites

- Python 3.9 or higher
- A Telegram Bot Token (get one from [@BotFather](https://t.me/BotFather))

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mortgagebot
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your bot token:
   ```bash
   cp .env.example .env
   # Edit .env and add your TELEGRAM_BOT_TOKEN
   ```

5. Run the bot:
   ```bash
   python bot.py
   ```

## Configuration

Environment variables (set in `.env` file):

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram Bot API token | Yes |

Validation limits (configured in `config.py`):

| Parameter | Min | Max |
|-----------|-----|-----|
| Loan Term (years) | 1 | 30 |
| Interest Rate (%) | 0.1 | 30 |

## Project Structure

```
.
├── bot.py              # Main bot implementation
├── config.py           # Configuration and constants
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment file
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Validation Rules

| Input | Validation | Error Handling |
|-------|------------|----------------|
| Loan Amount | Positive number | Shows error message, asks again |
| Down Payment | Positive number ≤ Loan Amount | Shows error with amounts, asks again |
| Loan Term | 1-30 years | Shows valid range, asks again |
| Interest Rate | 0.1-30% | Shows valid range, asks again |

## Example Output

```
📊 CALCULATION RESULTS:

• Loan Amount: 5 000 000 RUB
• Down Payment: 1 000 000 RUB
• Loan Principal: 4 000 000 RUB
• Loan Term: 15 years (180 months)
• Interest Rate: 12.0% per year

💸 Monthly Payment: ~48 007 RUB
💰 Total Payment: ~8 641 214 RUB
💎 Total Interest: ~4 641 214 RUB

⚠️ Note: This is an estimate. Actual terms may vary.
All your data has been deleted from memory.
```

## Deployment

The bot can be deployed to any platform that supports Python:

- **Heroku**: Use a `Procfile` with `worker: python bot.py`
- **PythonAnywhere**: Upload files and run as a scheduled task
- **VPS/Cloud VM**: Run with systemd or supervisor
- **Docker**: Create a simple Dockerfile

No database setup required - all data is stored in RAM during conversations only.

## Limitations (MVP)

- No calculation history
- No save/export functionality
- No special mortgage programs (e.g., family mortgage, government subsidies)
- No currency conversion
- No PDF/printable results
- Maximum 30-year term (standard for Russia)

## License

MIT License
