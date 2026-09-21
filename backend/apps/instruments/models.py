"""Sector and Instrument models for financial market universe."""
import uuid

from common.utilities.constants import AssetClass, BaseCurrency
from django.db import models


class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "sectors"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Instrument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=30, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    asset_class = models.CharField(
        max_length=20,
        choices=AssetClass.choices,
        default=AssetClass.EQUITY,
        db_index=True,
    )
    sector = models.ForeignKey(
        Sector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="instruments",
    )
    exchange = models.CharField(max_length=30, default="NSE")
    currency = models.CharField(
        max_length=3,
        choices=BaseCurrency.choices,
        default=BaseCurrency.INR,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "instruments"
        ordering = ["symbol"]
        indexes = [
            models.Index(fields=["symbol", "is_active"]),
            models.Index(fields=["asset_class", "is_active"]),
        ]

    def __str__(self):
        return f"{self.symbol} ({self.name})"
