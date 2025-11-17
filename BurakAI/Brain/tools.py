#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BurakAI - Tool Orchestra System
═════════════════════════════════════════════════════════
NEXUS'tan esinlendi - basitleştirilmiş:
- Parallel execution yerine → Sequential pipeline
- Complex orchestration yerine → Simple tool chaining
- ML tool selection yerine → Rule-based routing

But still POWERFUL:
- 10+ tools integrated
- Smart tool chaining
- Error handling & fallback
- Tool usage metrics
═════════════════════════════════════════════════════════
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum


class ToolCategory(Enum):
    """Tool categories"""
    EXTRACTION = "extraction"      # OCR, PDF parsing, etc.
    ANALYSIS = "analysis"           # Margin calc, risk scoring
    COMPLIANCE = "compliance"       # ADR, HS code, MSDS
    COMMUNICATION = "communication" # Email, LinkedIn
    CODE = "code"                   # Code review, doc gen
    STRATEGIC = "strategic"         # Scenario planning


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict = None

    def __repr__(self):
        status = "✓" if self.success else "✗"
        return f"ToolResult({status}, data={type(self.data).__name__})"


@dataclass
class Tool:
    """Tool definition"""
    name: str
    category: ToolCategory
    description: str
    function: Callable
    required_params: List[str]
    optional_params: List[str] = None

    def execute(self, **kwargs) -> ToolResult:
        """Execute tool with parameters"""
        # Validate required params
        missing = [p for p in self.required_params if p not in kwargs]
        if missing:
            return ToolResult(
                success=False,
                data=None,
                error=f"Missing required parameters: {missing}"
            )

        try:
            result = self.function(**kwargs)
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))


# ═════════════════════════════════════════════════════════
# TOOL IMPLEMENTATIONS
# ═════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────
# EXTRACTION TOOLS
# ─────────────────────────────────────────────────────────

def ocr_pdf_tool(file_path: str) -> str:
    """
    Extract text from PDF using OCR

    Args:
        file_path: Path to PDF file

    Returns:
        Extracted text
    """
    # TODO: Implement with Tesseract/PaddleOCR
    # For now, placeholder
    return f"[OCR] Extracted text from {file_path}"


def parse_excel_tool(file_path: str, sheet: str = None) -> Dict:
    """
    Parse Excel file

    Args:
        file_path: Path to Excel file
        sheet: Sheet name (optional)

    Returns:
        Parsed data
    """
    # TODO: Implement with openpyxl/pandas
    return {"status": "parsed", "file": file_path}


# ─────────────────────────────────────────────────────────
# ANALYSIS TOOLS
# ─────────────────────────────────────────────────────────

def margin_calculator_tool(
    cost: float,
    price: float,
    quantity: int = 1,
    commission_percent: float = 0,
    shipping_cost: float = 0,
    return_rate_percent: float = 0
) -> Dict[str, float]:
    """
    Calculate net margin

    Args:
        cost: Unit cost in TRY
        price: Selling price
        quantity: Quantity
        commission_percent: Commission %
        shipping_cost: Shipping cost (total)
        return_rate_percent: Return rate %

    Returns:
        Margin calculations
    """
    # Total revenue
    total_revenue = price * quantity

    # Commission
    commission = total_revenue * (commission_percent / 100)

    # Return cost
    return_cost = total_revenue * (return_rate_percent / 100)

    # Total cost
    total_cost = (cost * quantity) + commission + shipping_cost + return_cost

    # Net profit
    net_profit = total_revenue - total_cost

    # Margins
    net_margin_percent = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    gross_margin = total_revenue - (cost * quantity)
    gross_margin_percent = (gross_margin / total_revenue * 100) if total_revenue > 0 else 0

    return {
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "net_profit": round(net_profit, 2),
        "net_margin_percent": round(net_margin_percent, 2),
        "gross_margin": round(gross_margin, 2),
        "gross_margin_percent": round(gross_margin_percent, 2),
        "unit_cost": cost,
        "unit_price": price,
        "quantity": quantity,
    }


def risk_scorer_tool(
    customer: str,
    context: Dict = None
) -> Dict[str, Any]:
    """
    Calculate customer risk score

    Args:
        customer: Customer name
        context: Context data (from context.yaml)

    Returns:
        Risk assessment
    """
    if not context or "customers" not in context:
        return {"risk_score": 5, "risk_level": "UNKNOWN", "note": "No context data"}

    customer_data = context["customers"].get(customer)
    if not customer_data:
        return {"risk_score": 5, "risk_level": "UNKNOWN", "note": f"Customer {customer} not found"}

    risk_score = customer_data.get("risk_score", 5)
    risk_level = "LOW" if risk_score <= 3 else "MEDIUM" if risk_score <= 6 else "HIGH"

    return {
        "customer": customer,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "payment_avg_days": customer_data.get("payment_avg_days", 0),
        "past_issues": customer_data.get("past_issues", 0),
        "requires_deposit": customer_data.get("requires_deposit", False),
        "notes": customer_data.get("notes", ""),
    }


def breakeven_calculator_tool(
    fixed_cost: float,
    unit_cost: float,
    unit_price: float
) -> Dict[str, float]:
    """
    Calculate breakeven point

    Args:
        fixed_cost: Fixed costs
        unit_cost: Variable cost per unit
        unit_price: Selling price per unit

    Returns:
        Breakeven analysis
    """
    contribution_margin = unit_price - unit_cost

    if contribution_margin <= 0:
        return {
            "breakeven_units": float('inf'),
            "breakeven_revenue": float('inf'),
            "note": "Price must be higher than unit cost"
        }

    breakeven_units = fixed_cost / contribution_margin
    breakeven_revenue = breakeven_units * unit_price

    return {
        "breakeven_units": round(breakeven_units, 0),
        "breakeven_revenue": round(breakeven_revenue, 2),
        "contribution_margin": round(contribution_margin, 2),
        "contribution_margin_percent": round((contribution_margin / unit_price * 100), 2),
    }


# ─────────────────────────────────────────────────────────
# COMPLIANCE TOOLS
# ─────────────────────────────────────────────────────────

def adr_checker_tool(un_number: str, context: Dict = None) -> Dict[str, Any]:
    """
    Check ADR compliance for UN number

    Args:
        un_number: UN number (e.g., "1170" or "UN1170")
        context: Context data

    Returns:
        ADR compliance info
    """
    # Clean UN number
    un_clean = re.sub(r'[^0-9]', '', un_number)

    # Simple ADR database (in reality, load from file)
    adr_db = {
        "1170": {
            "name": "Ethanol / Bioethanol",
            "class": "3",
            "packing_group": "II",
            "hazard": "Flammable liquid",
            "label": "GHS02, GHS07",
            "limited_quantity": "1L",
            "special_provisions": "144",
        },
        "1263": {
            "name": "Paint",
            "class": "3",
            "packing_group": "III",
            "hazard": "Flammable liquid",
            "label": "GHS02",
            "limited_quantity": "5L",
        }
    }

    info = adr_db.get(un_clean)

    if not info:
        return {
            "un_number": un_number,
            "status": "NOT_FOUND",
            "note": f"UN{un_clean} not in database"
        }

    return {
        "un_number": f"UN{un_clean}",
        "status": "FOUND",
        "name": info["name"],
        "class": info["class"],
        "packing_group": info.get("packing_group"),
        "hazard": info["hazard"],
        "label": info["label"],
        "limited_quantity": info.get("limited_quantity"),
        "compliance": "OK" if info.get("limited_quantity") else "FULL_ADR_REQUIRED",
    }


def hs_code_lookup_tool(product: str, context: Dict = None) -> Dict[str, str]:
    """
    Lookup HS code for product

    Args:
        product: Product name or description
        context: Context data

    Returns:
        HS code info
    """
    # Simple HS code database (in reality, load from file)
    hs_db = {
        "bioethanol": {
            "hs_code": "2207.20.00",
            "description": "Ethyl alcohol, denatured",
            "duty_rate": "0%",
        },
        "pp container": {
            "hs_code": "3923.30.00",
            "description": "Carboys, bottles, flasks of plastics",
            "duty_rate": "6.5%",
        }
    }

    product_lower = product.lower()

    for key, info in hs_db.items():
        if key in product_lower:
            return {
                "product": product,
                "hs_code": info["hs_code"],
                "description": info["description"],
                "duty_rate": info.get("duty_rate", "Unknown"),
                "status": "FOUND"
            }

    return {
        "product": product,
        "hs_code": "NOT_FOUND",
        "status": "NOT_FOUND",
        "note": "Product not in database - manual lookup required"
    }


# ─────────────────────────────────────────────────────────
# COMMUNICATION TOOLS
# ─────────────────────────────────────────────────────────

def email_composer_tool(
    recipient: str,
    subject: str,
    context: str,
    tone: str = "professional"
) -> str:
    """
    Compose email draft

    Args:
        recipient: Recipient name
        subject: Email subject
        context: Email context/request
        tone: Email tone (professional, friendly, formal)

    Returns:
        Email draft
    """
    # Simple template (in reality, use LLM)
    template = f"""
Konu: {subject}

Sayın {recipient},

{context}

İyi çalışmalar,
Burak Kumuk
SnarcAI
"""
    return template.strip()


def linkedin_writer_tool(topic: str, length: str = "medium") -> str:
    """
    Write LinkedIn post

    Args:
        topic: Post topic
        length: short (100 words), medium (150), long (200)

    Returns:
        LinkedIn post draft
    """
    # Simple template (in reality, use LLM)
    post = f"""
🚀 {topic}

[AI-generated content would go here - connect to model for real post]

#eticaret #üretim #entrepreneurship
"""
    return post.strip()


# ═════════════════════════════════════════════════════════
# TOOL REGISTRY
# ═════════════════════════════════════════════════════════

TOOL_REGISTRY: Dict[str, Tool] = {
    # Extraction
    "ocr_pdf": Tool(
        name="ocr_pdf",
        category=ToolCategory.EXTRACTION,
        description="Extract text from PDF",
        function=ocr_pdf_tool,
        required_params=["file_path"]
    ),

    "parse_excel": Tool(
        name="parse_excel",
        category=ToolCategory.EXTRACTION,
        description="Parse Excel file",
        function=parse_excel_tool,
        required_params=["file_path"],
        optional_params=["sheet"]
    ),

    # Analysis
    "margin_calc": Tool(
        name="margin_calc",
        category=ToolCategory.ANALYSIS,
        description="Calculate net margin",
        function=margin_calculator_tool,
        required_params=["cost", "price"],
        optional_params=["quantity", "commission_percent", "shipping_cost", "return_rate_percent"]
    ),

    "risk_score": Tool(
        name="risk_score",
        category=ToolCategory.ANALYSIS,
        description="Calculate customer risk",
        function=risk_scorer_tool,
        required_params=["customer"],
        optional_params=["context"]
    ),

    "breakeven_calc": Tool(
        name="breakeven_calc",
        category=ToolCategory.ANALYSIS,
        description="Calculate breakeven point",
        function=breakeven_calculator_tool,
        required_params=["fixed_cost", "unit_cost", "unit_price"]
    ),

    # Compliance
    "adr_check": Tool(
        name="adr_check",
        category=ToolCategory.COMPLIANCE,
        description="Check ADR compliance",
        function=adr_checker_tool,
        required_params=["un_number"],
        optional_params=["context"]
    ),

    "hs_code_lookup": Tool(
        name="hs_code_lookup",
        category=ToolCategory.COMPLIANCE,
        description="Lookup HS code",
        function=hs_code_lookup_tool,
        required_params=["product"],
        optional_params=["context"]
    ),

    # Communication
    "email_compose": Tool(
        name="email_compose",
        category=ToolCategory.COMMUNICATION,
        description="Compose email",
        function=email_composer_tool,
        required_params=["recipient", "subject", "context"],
        optional_params=["tone"]
    ),

    "linkedin_write": Tool(
        name="linkedin_write",
        category=ToolCategory.COMMUNICATION,
        description="Write LinkedIn post",
        function=linkedin_writer_tool,
        required_params=["topic"],
        optional_params=["length"]
    ),
}


# ═════════════════════════════════════════════════════════
# TOOL ORCHESTRATOR
# ═════════════════════════════════════════════════════════

class ToolOrchestrator:
    """
    Orchestrate tool execution
    """

    def __init__(self, tools: Dict[str, Tool] = None, context: Dict = None):
        """
        Initialize orchestrator

        Args:
            tools: Tool registry (None = use default)
            context: Global context (from context.yaml)
        """
        self.tools = tools or TOOL_REGISTRY
        self.context = context or {}

    def execute_tool(self, tool_name: str, **params) -> ToolResult:
        """
        Execute a single tool

        Args:
            tool_name: Tool name
            **params: Tool parameters

        Returns:
            Tool result
        """
        tool = self.tools.get(tool_name)
        if not tool:
            return ToolResult(success=False, data=None, error=f"Tool {tool_name} not found")

        # Inject context if needed
        if "context" in tool.optional_params or "context" in tool.required_params:
            params["context"] = self.context

        return tool.execute(**params)

    def execute_pipeline(self, pipeline: List[Dict[str, Any]]) -> List[ToolResult]:
        """
        Execute a pipeline of tools

        Args:
            pipeline: List of tool configs: [{"tool": "name", "params": {...}}, ...]

        Returns:
            List of tool results
        """
        results = []

        for step in pipeline:
            tool_name = step.get("tool")
            params = step.get("params", {})

            # Execute tool
            result = self.execute_tool(tool_name, **params)
            results.append(result)

            # Stop if tool failed and no fallback
            if not result.success and not step.get("continue_on_error", False):
                break

        return results

    def get_tool_for_intent(self, intent: str) -> List[str]:
        """
        Get recommended tools for intent

        Args:
            intent: Intent type (from intents.py)

        Returns:
            List of tool names
        """
        # Intent -> Tool mapping
        intent_tools = {
            "margin_calc": ["margin_calc"],
            "invoice_check": ["ocr_pdf", "margin_calc", "risk_score"],
            "breakeven": ["breakeven_calc"],
            "risk_assessment": ["risk_score"],
            "adr_check": ["adr_check"],
            "hs_code_lookup": ["hs_code_lookup"],
            "email_compose": ["email_compose"],
            "linkedin_post": ["linkedin_write"],
        }

        return intent_tools.get(intent, [])


# ═════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═════════════════════════════════════════════════════════
if __name__ == "__main__":
    import json

    # Example context
    example_context = {
        "customers": {
            "ABC_Lojistik": {
                "risk_score": 7,
                "payment_avg_days": 45,
                "past_issues": 2,
                "requires_deposit": True,
                "notes": "Geçmişte ödeme gecikmeleri"
            }
        }
    }

    orchestrator = ToolOrchestrator(context=example_context)

    print("=" * 60)
    print("TOOL EXECUTION TESTS")
    print("=" * 60)

    # Test 1: Margin calculation
    print("\n1. Margin Calculation")
    result = orchestrator.execute_tool(
        "margin_calc",
        cost=118,
        price=164,
        quantity=5000,
        commission_percent=7,
        shipping_cost=600,
        return_rate_percent=1.2
    )
    print(f"Result: {result}")
    if result.success:
        print(json.dumps(result.data, indent=2))

    # Test 2: Risk assessment
    print("\n2. Risk Assessment")
    result = orchestrator.execute_tool(
        "risk_score",
        customer="ABC_Lojistik"
    )
    print(f"Result: {result}")
    if result.success:
        print(json.dumps(result.data, indent=2))

    # Test 3: ADR check
    print("\n3. ADR Check")
    result = orchestrator.execute_tool(
        "adr_check",
        un_number="UN1170"
    )
    print(f"Result: {result}")
    if result.success:
        print(json.dumps(result.data, indent=2))

    # Test 4: Pipeline execution
    print("\n4. Pipeline Execution (Invoice Check)")
    pipeline = [
        {"tool": "risk_score", "params": {"customer": "ABC_Lojistik"}},
        {"tool": "margin_calc", "params": {"cost": 118, "price": 164, "quantity": 5000}},
        {"tool": "adr_check", "params": {"un_number": "1170"}},
    ]
    results = orchestrator.execute_pipeline(pipeline)
    print(f"Pipeline completed: {len([r for r in results if r.success])}/{len(results)} successful")
