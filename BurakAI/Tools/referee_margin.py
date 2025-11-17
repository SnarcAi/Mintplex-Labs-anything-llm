#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BurakAI - Referee Margin Calculator
═════════════════════════════════════════════════════════
Precision margin calculator for e-commerce

Features:
- Net margin calculation
- Multi-currency support
- Commission, shipping, returns handling
- Detailed breakdown
═════════════════════════════════════════════════════════
"""

import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class MarginCalculation:
    """Margin calculation result"""
    # Inputs
    quantity: int
    unit_price: float
    unit_cost: float
    currency: str

    # Costs
    commission_amount: float
    shipping_cost: float
    return_cost: float
    fx_cost: float

    # Totals
    total_revenue: float
    total_cost: float
    net_profit: float

    # Margins
    gross_margin: float
    gross_margin_percent: float
    net_margin_percent: float

    # Breakeven
    breakeven_quantity: int

    def to_dict(self) -> Dict:
        """Convert to dict"""
        return {
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "unit_cost": self.unit_cost,
            "currency": self.currency,
            "commission_amount": round(self.commission_amount, 2),
            "shipping_cost": round(self.shipping_cost, 2),
            "return_cost": round(self.return_cost, 2),
            "fx_cost": round(self.fx_cost, 2),
            "total_revenue": round(self.total_revenue, 2),
            "total_cost": round(self.total_cost, 2),
            "net_profit": round(self.net_profit, 2),
            "gross_margin": round(self.gross_margin, 2),
            "gross_margin_percent": round(self.gross_margin_percent, 2),
            "net_margin_percent": round(self.net_margin_percent, 2),
            "breakeven_quantity": self.breakeven_quantity,
        }

    def format_pretty(self) -> str:
        """Format as pretty text"""
        return f"""
╔═══════════════════════════════════════════════════╗
║  NET MARJ HESAPLAMA                               ║
╠═══════════════════════════════════════════════════╣
║  Miktar: {self.quantity:,} adet
║  Birim Fiyat: {self.unit_price:.2f} {self.currency}
║  Birim Maliyet: {self.unit_cost:.2f} TRY
║                                                   ║
║  📊 TOPLAM                                        ║
║  Ciro: {self.total_revenue:,.2f} {self.currency}
║  Maliyet: {self.total_cost:,.2f} TRY
║  Net Kâr: {self.net_profit:,.2f} TRY
║                                                   ║
║  📈 MARJLAR                                       ║
║  Brüt Marj: %{self.gross_margin_percent:.2f}
║  Net Marj: %{self.net_margin_percent:.2f}
║                                                   ║
║  💡 BAŞABAŞ                                       ║
║  {self.breakeven_quantity:,} adet
╚═══════════════════════════════════════════════════╝
""".strip()


class RefereeMargin:
    """
    Margin calculator with precision and validation
    """

    # Default FX rates (should be updated regularly)
    DEFAULT_FX_RATES = {
        "USD": 34.10,
        "EUR": 37.20,
        "GBP": 43.50,
        "TRY": 1.00,
    }

    def __init__(self, fx_rates: Dict[str, float] = None):
        """
        Initialize calculator

        Args:
            fx_rates: Custom FX rates (None = use defaults)
        """
        self.fx_rates = fx_rates or self.DEFAULT_FX_RATES

    def calculate(
        self,
        quantity: int,
        price: float,
        cost: float,
        price_currency: str = "USD",
        commission_percent: float = 0.0,
        shipping_cost: float = 0.0,
        return_rate_percent: float = 0.0,
        fx_rate: Optional[float] = None
    ) -> MarginCalculation:
        """
        Calculate margin

        Args:
            quantity: Number of units
            price: Selling price per unit
            cost: Cost per unit (in TRY)
            price_currency: Price currency (USD, EUR, GBP, TRY)
            commission_percent: Commission percentage
            shipping_cost: Total shipping cost (TRY)
            return_rate_percent: Return/refund rate percentage
            fx_rate: Custom FX rate (None = use default)

        Returns:
            MarginCalculation result
        """
        # Get FX rate
        if fx_rate is None:
            fx_rate = self.fx_rates.get(price_currency.upper(), 1.0)

        # Convert price to TRY
        price_try = price * fx_rate

        # Calculate revenue
        total_revenue = price_try * quantity

        # Calculate costs
        commission_amount = total_revenue * (commission_percent / 100)
        return_cost = total_revenue * (return_rate_percent / 100)
        fx_cost = 0  # Can add FX hedging cost here
        product_cost = cost * quantity

        total_cost = product_cost + commission_amount + shipping_cost + return_cost + fx_cost

        # Calculate profit
        net_profit = total_revenue - total_cost

        # Calculate margins
        gross_margin = total_revenue - product_cost
        gross_margin_percent = (gross_margin / total_revenue * 100) if total_revenue > 0 else 0
        net_margin_percent = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

        # Calculate breakeven
        # breakeven = fixed_costs / (price - variable_cost_per_unit)
        fixed_costs = shipping_cost
        variable_cost_per_unit = cost + (price_try * commission_percent / 100) + (price_try * return_rate_percent / 100)
        contribution_margin = price_try - variable_cost_per_unit

        if contribution_margin > 0:
            breakeven_qty = int(fixed_costs / contribution_margin) + 1
        else:
            breakeven_qty = -1  # Impossible to break even

        return MarginCalculation(
            quantity=quantity,
            unit_price=price,
            unit_cost=cost,
            currency=price_currency,
            commission_amount=commission_amount,
            shipping_cost=shipping_cost,
            return_cost=return_cost,
            fx_cost=fx_cost,
            total_revenue=total_revenue,
            total_cost=total_cost,
            net_profit=net_profit,
            gross_margin=gross_margin,
            gross_margin_percent=gross_margin_percent,
            net_margin_percent=net_margin_percent,
            breakeven_quantity=breakeven_qty,
        )

    def parse_query(self, query: str) -> Tuple[bool, Dict, Optional[str]]:
        """
        Parse natural language query

        Args:
            query: Natural language query
                   Example: "5000 adet, $4.5, komisyon %7, kargo 600 TL, iade %1.2, kur 34.10, maliyet 118 TL"

        Returns:
            (success, params_dict, error_message)
        """
        try:
            params = {}

            # Quantity
            qty_match = re.search(r'(\d+[\d,]*)\s*(adet|pcs|units?)', query, re.I)
            if qty_match:
                params['quantity'] = int(qty_match.group(1).replace(',', ''))

            # Price (with currency symbol)
            price_match = re.search(r'([$€£]|usd|eur|gbp)\s*(\d+(?:[.,]\d+)?)', query, re.I)
            if price_match:
                symbol = price_match.group(1).upper()
                price_val = float(price_match.group(2).replace(',', '.'))
                params['price'] = price_val

                # Detect currency
                currency_map = {'$': 'USD', 'USD': 'USD', '€': 'EUR', 'EUR': 'EUR', '£': 'GBP', 'GBP': 'GBP'}
                params['price_currency'] = currency_map.get(symbol, 'USD')
            else:
                # Try without symbol
                price_match2 = re.search(r'fiyat[:\s]+(\d+[\d.,]*)', query, re.I)
                if price_match2:
                    params['price'] = float(price_match2.group(1).replace(',', '.'))
                    params['price_currency'] = 'USD'  # Default

            # Cost
            cost_match = re.search(r'maliyet[:\s]+(\d+(?:[.,]\d+)?)', query, re.I)
            if cost_match:
                params['cost'] = float(cost_match.group(1).replace(',', '.'))

            # Commission
            comm_match = re.search(r'komisyon[:\s]+%?(\d+(?:[.,]\d+)?)', query, re.I)
            if comm_match:
                params['commission_percent'] = float(comm_match.group(1).replace(',', '.'))

            # Shipping
            ship_match = re.search(r'kargo[:\s]+(\d+(?:[.,]\d+)?)', query, re.I)
            if ship_match:
                params['shipping_cost'] = float(ship_match.group(1).replace(',', '.'))

            # Return rate
            return_match = re.search(r'iade[:\s]+%?(\d+(?:[.,]\d+)?)', query, re.I)
            if return_match:
                params['return_rate_percent'] = float(return_match.group(1).replace(',', '.'))

            # FX rate
            fx_match = re.search(r'kur[:\s]+(\d+(?:[.,]\d+)?)', query, re.I)
            if fx_match:
                params['fx_rate'] = float(fx_match.group(1).replace(',', '.'))

            # Validate required params
            required = ['quantity', 'price', 'cost']
            missing = [p for p in required if p not in params]
            if missing:
                return False, {}, f"Eksik parametreler: {', '.join(missing)}"

            return True, params, None

        except Exception as e:
            return False, {}, f"Parse hatası: {str(e)}"


def run(query: str, fx_rates: Dict[str, float] = None, pretty: bool = False) -> Dict:
    """
    Run margin calculation from query

    Args:
        query: Natural language query
        fx_rates: Custom FX rates
        pretty: Return pretty formatted text instead of dict

    Returns:
        Calculation result
    """
    referee = RefereeMargin(fx_rates=fx_rates)

    # Parse query
    success, params, error = referee.parse_query(query)
    if not success:
        return {"error": error}

    # Calculate
    result = referee.calculate(**params)

    if pretty:
        return {"result": result.format_pretty()}
    else:
        return result.to_dict()


# ═════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Test query
    query = "5000 adet, $4.5, komisyon %7, kargo 600 TL, iade %1.2, kur 34.10, maliyet 118 TL"

    print("=" * 60)
    print("REFEREE MARGIN CALCULATOR TEST")
    print("=" * 60)
    print(f"\nQuery: {query}\n")

    # Run calculation
    result = run(query, pretty=True)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(result["result"])
