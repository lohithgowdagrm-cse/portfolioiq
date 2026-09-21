"""Custom DRF exception handler standardizing JSON error envelope."""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .base import FinancialValidationException

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Standardizes error responses to:
    {
      "error": {
        "code": "ERROR_CODE",
        "message": "Human readable explanation",
        "details": {}
      }
    }
    """
    response = exception_handler(exc, context)

    # Custom domain exceptions
    if isinstance(exc, FinancialValidationException):
        return Response(
            {
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
            status=exc.status_code,
        )

    if response is not None:
        error_code = getattr(exc, "default_code", "API_ERROR").upper()
        details = {}
        message = "An error occurred while processing your request."

        if isinstance(response.data, dict):
            if "detail" in response.data:
                message = str(response.data["detail"])
                details = {k: v for k, v in response.data.items() if k != "detail"}
            else:
                message = "Validation failed for one or more fields."
                details = response.data
        elif isinstance(response.data, list):
            message = response.data[0] if response.data else message
            details = {"errors": response.data}

        response.data = {
            "error": {
                "code": error_code,
                "message": message,
                "details": details,
            }
        }
        return response

    # Unhandled 500 exceptions
    logger.exception("Unhandled server exception: %s", exc)
    return Response(
        {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please try again later.",
                "details": {},
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
