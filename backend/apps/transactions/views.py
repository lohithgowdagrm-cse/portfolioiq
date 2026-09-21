"""Views for recording, filtering, and deleting transactions."""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer
from apps.transactions.services.transaction_service import TransactionService
from apps.portfolios.models import Portfolio


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = Transaction.objects.filter(portfolio__user=user).select_related(
            "portfolio", "instrument", "option_contract"
        ).order_by("-executed_at", "-created_at")

        portfolio_id = self.request.query_params.get("portfolio_id")
        if portfolio_id:
            qs = qs.filter(portfolio_id=portfolio_id)

        symbol = self.request.query_params.get("symbol")
        if symbol:
            qs = qs.filter(instrument__symbol__iexact=symbol)

        tx_type = self.request.query_params.get("type")
        if tx_type:
            qs = qs.filter(transaction_type=tx_type.upper())

        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        tx = TransactionService.record_transaction(
            portfolio=data["portfolio"],
            instrument=data["instrument"],
            tx_type=data["transaction_type"],
            quantity=data["quantity"],
            price=data["price"],
            fees=data.get("fees", 0),
            taxes=data.get("taxes", 0),
            executed_at=data.get("executed_at"),
            notes=data.get("notes", ""),
            option_contract=data.get("option_contract"),
            user=request.user,
        )

        response_serializer = self.get_serializer(tx)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        TransactionService.delete_transaction(instance, user=request.user)
        return Response(
            {"message": "Transaction deleted and portfolio ledger reconciled successfully."},
            status=status.HTTP_200_OK,
        )
