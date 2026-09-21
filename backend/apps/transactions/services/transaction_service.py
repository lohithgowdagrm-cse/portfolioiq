"""Transaction management service orchestrating atomic ledger creation and auditing."""
import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from apps.transactions.models import Transaction
from apps.portfolios.models import Portfolio
from apps.instruments.models import Instrument
from apps.options.models import OptionContract
from apps.portfolios.services.accounting import PortfolioCalculationService
from apps.audit.services import record_audit_log
from common.exceptions.base import FinancialValidationException

logger = logging.getLogger(__name__)


class TransactionService:
    """
    Coordinates transaction creation, deletion, validation, and audit recording.
    """

    @classmethod
    @transaction.atomic
    def record_transaction(
        cls,
        portfolio: Portfolio,
        instrument: Instrument,
        tx_type: str,
        quantity: Decimal,
        price: Decimal,
        fees: Decimal = Decimal("0.0000"),
        taxes: Decimal = Decimal("0.0000"),
        executed_at=None,
        notes: str = "",
        option_contract: OptionContract = None,
        user=None,
    ) -> Transaction:
        """
        Creates a transaction record, updates position cost basis, adjusts cash balance,
        and logs to the audit trail atomically.
        """
        if executed_at is None:
            executed_at = timezone.now()

        # Step 1: Create transaction record (runs model clean() validations)
        tx = Transaction(
            portfolio=portfolio,
            instrument=instrument,
            option_contract=option_contract,
            transaction_type=tx_type,
            quantity=quantity,
            price=price,
            fees=fees,
            taxes=taxes,
            executed_at=executed_at,
            notes=notes,
        )
        tx.save()

        # Step 2: Apply transaction to position state
        PortfolioCalculationService.apply_transaction_to_position(
            portfolio=portfolio,
            instrument=instrument,
            tx_type=tx_type,
            quantity=quantity,
            price=price,
            fees=fees,
            taxes=taxes,
            option_contract=option_contract,
        )

        # Step 3: Update portfolio cash balance if applicable
        if tx_type == "BUY":
            portfolio.cash_balance -= tx.total_amount
            portfolio.save(update_fields=["cash_balance", "updated_at"])
        elif tx_type == "SELL":
            portfolio.cash_balance += tx.total_amount
            portfolio.save(update_fields=["cash_balance", "updated_at"])
        elif tx_type == "DIVIDEND":
            portfolio.cash_balance += tx.total_amount
            portfolio.save(update_fields=["cash_balance", "updated_at"])

        # Step 4: Record audit log
        record_audit_log(
            action="RECORD_TRANSACTION",
            entity_type="Transaction",
            entity_id=str(tx.id),
            user=user or portfolio.user,
            metadata={
                "portfolio_id": str(portfolio.id),
                "symbol": instrument.symbol,
                "type": tx_type,
                "qty": str(quantity),
                "price": str(price),
                "total": str(tx.total_amount),
            },
        )

        return tx

    @classmethod
    @transaction.atomic
    def delete_transaction(cls, tx: Transaction, user=None) -> None:
        """
        Deletes a transaction and triggers a full chronological ledger replay
        to ensure mathematical integrity.
        """
        portfolio = tx.portfolio
        tx_id = str(tx.id)
        tx_meta = {
            "portfolio_id": str(portfolio.id),
            "symbol": tx.instrument.symbol,
            "type": tx.transaction_type,
            "quantity": str(tx.quantity),
            "price": str(tx.price),
        }

        # Reverse cash impact
        if tx.transaction_type == "BUY":
            portfolio.cash_balance += tx.total_amount
        elif tx.transaction_type in ("SELL", "DIVIDEND"):
            portfolio.cash_balance -= tx.total_amount
        portfolio.save(update_fields=["cash_balance", "updated_at"])

        # Delete transaction
        tx.delete()

        # Reconcile all positions from remaining transactions
        PortfolioCalculationService.recalculate_portfolio_from_ledger(portfolio)

        # Audit log
        record_audit_log(
            action="DELETE_TRANSACTION",
            entity_type="Transaction",
            entity_id=tx_id,
            user=user or portfolio.user,
            metadata=tx_meta,
        )
