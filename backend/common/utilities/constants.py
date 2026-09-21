"""Domain constants and choices for PortfolioIQ."""
from django.db import models


class AssetClass(models.TextChoices):
    EQUITY = "EQUITY", "Equity"
    ETF = "ETF", "Exchange Traded Fund"
    OPTION = "OPTION", "Options Contract"
    CRYPTO = "CRYPTO", "Cryptocurrency"
    CASH = "CASH", "Cash Equivalent"


class TransactionType(models.TextChoices):
    BUY = "BUY", "Buy"
    SELL = "SELL", "Sell"
    DIVIDEND = "DIVIDEND", "Dividend"
    BONUS = "BONUS", "Bonus Shares"
    SPLIT = "SPLIT", "Stock Split"


class OptionType(models.TextChoices):
    CALL = "CALL", "Call"
    PUT = "PUT", "Put"


class OptionStyle(models.TextChoices):
    AMERICAN = "AMERICAN", "American"
    EUROPEAN = "EUROPEAN", "European"


class AlertMetricType(models.TextChoices):
    DRAWDOWN = "DRAWDOWN", "Portfolio Drawdown"
    CONCENTRATION = "CONCENTRATION", "Position Weight Concentration"
    DAILY_LOSS = "DAILY_LOSS", "Daily Loss Breach"
    VOLATILITY = "VOLATILITY", "Volatility Threshold"
    OPTION_EXPIRY = "OPTION_EXPIRY", "Option Expiry Horizon"


class AlertComparator(models.TextChoices):
    GT = "GT", "Greater Than"
    LT = "LT", "Less Than"
    GTE = "GTE", "Greater Than or Equal"
    LTE = "LTE", "Less Than or Equal"


class BaseCurrency(models.TextChoices):
    INR = "INR", "Indian Rupee (₹)"
    USD = "USD", "US Dollar ($)"
    EUR = "EUR", "Euro (€)"
    GBP = "GBP", "British Pound (£)"
