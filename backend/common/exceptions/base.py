"""Domain-specific financial exceptions for PortfolioIQ."""
from rest_framework.exceptions import APIException
from rest_framework import status


class FinancialValidationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "INVALID_FINANCIAL_OPERATION"
    default_detail = "Invalid financial operation or validation failed."

    def __init__(self, message=None, code=None, details=None):
        self.code = code or self.default_code
        self.message = message or self.default_detail
        self.details = details or {}
        super().__init__(detail=self.message, code=self.code)


class InsufficientPositionException(FinancialValidationException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "INSUFFICIENT_POSITION"
    default_detail = "Cannot sell more quantity than currently held in position."


class InvalidPriceException(FinancialValidationException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "INVALID_PRICE"
    default_detail = "Price must be strictly positive."


class UnauthorizedPortfolioAccessException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "UNAUTHORIZED_PORTFOLIO_ACCESS"
    default_detail = "You do not have permission to access or modify this portfolio."
