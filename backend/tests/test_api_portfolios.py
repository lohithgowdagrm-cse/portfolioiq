"""Integration tests for PortfolioIQ REST API endpoints and IDOR authorization."""
import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.portfolios.models import Portfolio
from apps.instruments.models import Instrument, Sector


@pytest.mark.django_db
class TestPortfolioAndAuthAPI:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.client = APIClient()
        # User A
        self.user_a = User.objects.create_user(
            email="alice@portfolioiq.io",
            password="SecurePassword123!",
            first_name="Alice",
            last_name="Quant",
        )
        # User B
        self.user_b = User.objects.create_user(
            email="bob@portfolioiq.io",
            password="SecurePassword123!",
            first_name="Bob",
            last_name="Trader",
        )
        self.sector = Sector.objects.create(name="Tech", code="TECH")
        self.tcs = Instrument.objects.create(
            symbol="TCS",
            name="Tata Consultancy Services Ltd.",
            sector=self.sector,
            exchange="NSE",
            currency="INR",
        )
        # Portfolio for User A
        self.portfolio_a = Portfolio.objects.create(
            user=self.user_a,
            name="Alice Alpha Fund",
            cash_balance=Decimal("500000.0000"),
            base_currency="INR",
            is_default=True,
        )
        # Portfolio for User B
        self.portfolio_b = Portfolio.objects.create(
            user=self.user_b,
            name="Bob Value Fund",
            cash_balance=Decimal("300000.0000"),
            base_currency="INR",
            is_default=True,
        )

    def test_user_login_and_jwt(self):
        response = self.client.post("/api/v1/auth/login/", {
            "email": "alice@portfolioiq.io",
            "password": "SecurePassword123!",
        })
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == "alice@portfolioiq.io"

    def test_user_can_list_only_their_own_portfolios(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/api/v1/portfolios/")
        assert response.status_code == 200
        # Results should contain portfolio A and NOT portfolio B
        results = response.data.get("results", response.data)
        ids = [p["id"] for p in results]
        assert str(self.portfolio_a.id) in ids
        assert str(self.portfolio_b.id) not in ids

    def test_idor_protection_user_cannot_access_other_users_portfolio(self):
        # Alice tries to access Bob's portfolio
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(f"/api/v1/portfolios/{self.portfolio_b.id}/")
        assert response.status_code == 404  # 404 prevents leaking existence of other users' IDs

    def test_create_portfolio_and_summary(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.post("/api/v1/portfolios/", {
            "name": "New Venture Fund",
            "description": "Seed early tech bets",
            "base_currency": "INR",
            "cash_balance": "100000.0000",
        })
        assert response.status_code == 201
        p_id = response.data["id"]

        # Check summary endpoint
        summary_resp = self.client.get(f"/api/v1/portfolios/{p_id}/summary/")
        assert summary_resp.status_code == 200
        assert summary_resp.data["portfolio_name"] == "New Venture Fund"
        assert Decimal(str(summary_resp.data["cash_balance"])) == Decimal("100000.00")

    def test_record_transaction_and_positions_endpoint(self):
        self.client.force_authenticate(user=self.user_a)
        tx_resp = self.client.post("/api/v1/transactions/", {
            "portfolio": str(self.portfolio_a.id),
            "instrument": str(self.tcs.id),
            "transaction_type": "BUY",
            "quantity": "25.0000",
            "price": "4000.0000",
            "fees": "50.0000",
            "taxes": "25.0000",
            "notes": "API test buy",
        })
        assert tx_resp.status_code == 201
        assert tx_resp.data["symbol"] == "TCS"

        # Check positions
        pos_resp = self.client.get(f"/api/v1/portfolios/{self.portfolio_a.id}/positions/")
        assert pos_resp.status_code == 200
        positions = pos_resp.data["positions"]
        assert len(positions) == 1
        assert positions[0]["symbol"] == "TCS"
        assert Decimal(str(positions[0]["quantity"])) == Decimal("25.0000")

    def test_stress_test_endpoint(self):
        self.client.force_authenticate(user=self.user_a)
        stress_resp = self.client.post("/api/v1/risk/stress-test/", {
            "portfolio_id": str(self.portfolio_a.id),
            "market_shock_pct": -10.0,
        })
        assert stress_resp.status_code == 200
        assert "current_equity" in stress_resp.data
        assert "projected_equity" in stress_resp.data
        assert "total_percentage_change" in stress_resp.data
