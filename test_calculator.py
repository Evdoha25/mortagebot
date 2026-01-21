"""
Unit tests for the Mortgage Calculator Bot.
Tests the core calculation and validation functions.
"""

import unittest
from bot import (
    calculate_monthly_payment,
    parse_number,
    format_currency,
)


class TestMortgageCalculator(unittest.TestCase):
    """Test cases for mortgage calculation functions."""

    def test_calculate_monthly_payment_standard(self):
        """Test standard mortgage calculation."""
        result = calculate_monthly_payment(
            loan_amount=5_000_000,
            down_payment=1_000_000,
            years=15,
            annual_rate_percent=12.0,
        )
        
        # Principal should be loan amount minus down payment
        self.assertEqual(result["principal"], 4_000_000)
        
        # Months should be years * 12
        self.assertEqual(result["months"], 180)
        
        # Monthly payment should be approximately 48,007 RUB
        self.assertAlmostEqual(result["monthly_payment"], 48007, delta=1)
        
        # Total payment should be monthly * months
        self.assertAlmostEqual(
            result["total_payment"],
            result["monthly_payment"] * result["months"],
            delta=1,
        )
        
        # Total interest should be total payment minus principal
        self.assertAlmostEqual(
            result["total_interest"],
            result["total_payment"] - result["principal"],
            delta=1,
        )

    def test_calculate_monthly_payment_zero_interest(self):
        """Test mortgage calculation with zero interest rate."""
        result = calculate_monthly_payment(
            loan_amount=1_200_000,
            down_payment=0,
            years=10,
            annual_rate_percent=0,
        )
        
        # With zero interest, monthly payment = principal / months
        expected_monthly = 1_200_000 / 120
        self.assertEqual(result["monthly_payment"], expected_monthly)
        self.assertEqual(result["total_interest"], 0)

    def test_calculate_monthly_payment_no_down_payment(self):
        """Test mortgage calculation without down payment."""
        result = calculate_monthly_payment(
            loan_amount=3_000_000,
            down_payment=0,
            years=20,
            annual_rate_percent=10.0,
        )
        
        self.assertEqual(result["principal"], 3_000_000)
        self.assertGreater(result["monthly_payment"], 0)
        self.assertGreater(result["total_interest"], 0)

    def test_calculate_monthly_payment_short_term(self):
        """Test mortgage calculation with short term (1 year)."""
        result = calculate_monthly_payment(
            loan_amount=1_000_000,
            down_payment=500_000,
            years=1,
            annual_rate_percent=15.0,
        )
        
        self.assertEqual(result["principal"], 500_000)
        self.assertEqual(result["months"], 12)


class TestParseNumber(unittest.TestCase):
    """Test cases for number parsing function."""

    def test_parse_integer(self):
        """Test parsing integer input."""
        self.assertEqual(parse_number("5000000"), 5_000_000.0)

    def test_parse_float_with_dot(self):
        """Test parsing float with dot separator."""
        self.assertEqual(parse_number("12.5"), 12.5)

    def test_parse_float_with_comma(self):
        """Test parsing float with comma separator (Russian format)."""
        self.assertEqual(parse_number("12,5"), 12.5)

    def test_parse_number_with_spaces(self):
        """Test parsing number with spaces (thousand separators)."""
        self.assertEqual(parse_number("5 000 000"), 5_000_000.0)

    def test_parse_invalid_input(self):
        """Test parsing invalid input returns None."""
        self.assertIsNone(parse_number("abc"))
        self.assertIsNone(parse_number(""))
        self.assertIsNone(parse_number("12.5.5"))

    def test_parse_whitespace(self):
        """Test parsing number with leading/trailing whitespace."""
        self.assertEqual(parse_number("  5000  "), 5000.0)


class TestFormatCurrency(unittest.TestCase):
    """Test cases for currency formatting function."""

    def test_format_simple(self):
        """Test formatting simple number."""
        self.assertEqual(format_currency(5000), "5 000 RUB")

    def test_format_millions(self):
        """Test formatting millions."""
        self.assertEqual(format_currency(5000000), "5 000 000 RUB")

    def test_format_decimal(self):
        """Test formatting rounds to integer."""
        self.assertEqual(format_currency(48007.52), "48 008 RUB")

    def test_format_zero(self):
        """Test formatting zero."""
        self.assertEqual(format_currency(0), "0 RUB")


if __name__ == "__main__":
    unittest.main()
