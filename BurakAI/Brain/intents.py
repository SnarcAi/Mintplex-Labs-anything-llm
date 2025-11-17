#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BurakAI - Intent Detection System
═════════════════════════════════════════════════════════
NEXUS'tan esinlendi - basitleştirilmiş:
- ML model yerine → Rule-based pattern matching
- Embedding search yerine → Regex patterns
- Real-time learning yerine → Manual pattern updates

But still SMART:
- Multi-intent detection
- Context-aware classification
- Priority scoring
- Profile auto-selection
═════════════════════════════════════════════════════════
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """Intent categories"""
    # Finance intents
    MARGIN_CALC = "margin_calc"
    BREAKEVEN = "breakeven"
    PROFITABILITY = "profitability"
    CURRENCY_CONVERT = "currency_convert"
    INVOICE_CHECK = "invoice_check"
    QUOTE_GENERATE = "quote_generate"

    # Compliance intents
    ADR_CHECK = "adr_check"
    HS_CODE_LOOKUP = "hs_code_lookup"
    ZEEMAN_VALIDATE = "zeeman_validate"
    MSDS_VERIFY = "msds_verify"
    COMPLIANCE_CHECKLIST = "compliance_checklist"

    # Operations intents
    EMAIL_COMPOSE = "email_compose"
    LINKEDIN_POST = "linkedin_post"
    CUSTOMER_COMMUNICATION = "customer_communication"
    PRODUCT_LIST = "product_list"
    REPORT_GENERATE = "report_generate"

    # Risk assessment
    RISK_ASSESSMENT = "risk_assessment"
    CUSTOMER_EVALUATION = "customer_evaluation"

    # General
    QUESTION = "question"
    COMMAND = "command"
    UNKNOWN = "unknown"


class ProfileType(Enum):
    """AI profile types"""
    FINANCE = "finance"
    COMPLIANCE = "compliance"
    OPERATIONS = "operations"
    AUTO = "auto"  # Auto-detect


@dataclass
class Intent:
    """Detected intent with metadata"""
    type: IntentType
    confidence: float  # 0.0-1.0
    profile: ProfileType
    entities: Dict[str, any]  # Extracted entities (amounts, dates, names, etc.)
    sub_intents: List['Intent']  # Multi-intent support
    priority: int  # 1=highest, 5=lowest

    def __repr__(self):
        return f"Intent({self.type.value}, conf={self.confidence:.2f}, profile={self.profile.value})"


# ═════════════════════════════════════════════════════════
# INTENT PATTERNS (rule-based)
# ═════════════════════════════════════════════════════════
INTENT_PATTERNS = {
    # ─────────────────────────────────────────────────────
    # FINANCE INTENTS
    # ─────────────────────────────────────────────────────
    IntentType.MARGIN_CALC: {
        "patterns": [
            r"\b(marj|margin)\b",
            r"\b(kâr|kar|profit)\b",
            r"\bnet\s+(marj|kar|profit)\b",
            r"\bgross\s+margin\b",
            r"\bkarlılık\b",
        ],
        "profile": ProfileType.FINANCE,
        "priority": 1,
        "entities": {
            "amount": r"(\d+[\d\.,]*)\s*(tl|try|usd|\$|€|eur|gbp)",
            "quantity": r"(\d+[\d\.,]*)\s*(adet|pcs|unit)",
            "percentage": r"(\d+[\d\.,]*)\s*%",
        }
    },

    IntentType.INVOICE_CHECK: {
        "patterns": [
            r"\bfatura\b.*\b(kontrol|check|doğrula|verify)\b",
            r"\binvoice\b.*\b(check|verify|validate)\b",
            r"\bkontrol\s+et\b.*\bfatura\b",
        ],
        "profile": ProfileType.FINANCE,
        "priority": 1,
        "entities": {
            "customer": r"(?:için|from|of)\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)*)",
            "amount": r"(\d+[\d\.,]*)\s*(tl|try|usd|\$|€|eur)",
        }
    },

    IntentType.BREAKEVEN: {
        "patterns": [
            r"\bbreakeven\b",
            r"\bbaş.?a.?baş\b",
            r"\b(başabaş|basabas)\s+(nokta|point)\b",
        ],
        "profile": ProfileType.FINANCE,
        "priority": 2,
        "entities": {
            "fixed_cost": r"sabit.*?(\d+[\d\.,]*)",
            "unit_price": r"birim.*?(\d+[\d\.,]*)",
        }
    },

    IntentType.CURRENCY_CONVERT: {
        "patterns": [
            r"\b(kur|exchange\s+rate|fx)\b",
            r"\b(dolar|usd|euro|eur|sterlin|gbp)\b.*\b(tl|try|lira)\b",
            r"\bçevir\b.*\b(usd|eur|gbp)\b",
        ],
        "profile": ProfileType.FINANCE,
        "priority": 2,
        "entities": {
            "amount": r"(\d+[\d\.,]*)",
            "from_currency": r"\b(usd|eur|gbp|try)\b",
            "to_currency": r"\b(usd|eur|gbp|try)\b",
        }
    },

    IntentType.QUOTE_GENERATE: {
        "patterns": [
            r"\bteklif\b.*(ver|hazırla|oluştur|yap)",
            r"\b(quote|offer)\b.*(generate|create|prepare)",
            r"\bfiyat\s+ver\b",
        ],
        "profile": ProfileType.FINANCE,
        "priority": 2,
        "entities": {
            "customer": r"(?:için|to|for)\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)*)",
            "product": r"(?:ürün|product)[:\s]+([^\n]+)",
        }
    },

    # ─────────────────────────────────────────────────────
    # COMPLIANCE INTENTS
    # ─────────────────────────────────────────────────────
    IntentType.ADR_CHECK: {
        "patterns": [
            r"\badr\b",
            r"\bun\s*\d{4}\b",
            r"\btehlikeli\s+(madde|malzeme)\b",
            r"\bdangerous\s+goods\b",
            r"\bhazard(ous)?\s+(class|material)\b",
        ],
        "profile": ProfileType.COMPLIANCE,
        "priority": 1,
        "entities": {
            "un_number": r"\b(un\s*)?(\d{4})\b",
            "product": r"(?:ürün|product)[:\s]+([^\n]+)",
        }
    },

    IntentType.HS_CODE_LOOKUP: {
        "patterns": [
            r"\b(hs\s*code|gtip|tariff)\b",
            r"\bgümrük\s+kodu\b",
            r"\b\d{4}\.\d{2}\.\d{2}\b",  # HS code pattern
        ],
        "profile": ProfileType.COMPLIANCE,
        "priority": 2,
        "entities": {
            "hs_code": r"\b(\d{4}\.\d{2}\.?\d{0,2})\b",
            "product": r"(?:ürün|product)[:\s]+([^\n]+)",
        }
    },

    IntentType.ZEEMAN_VALIDATE: {
        "patterns": [
            r"\bzeeman\b",
            r"\betiket\s+(kontrol|check|validate)\b",
            r"\bpaket\s+(standart|requirement)\b",
        ],
        "profile": ProfileType.COMPLIANCE,
        "priority": 2,
        "entities": {}
    },

    IntentType.MSDS_VERIFY: {
        "patterns": [
            r"\bmsds\b",
            r"\bsds\b",
            r"\bgüvenlik\s+bilgi\s+formu\b",
            r"\bsafety\s+data\s+sheet\b",
        ],
        "profile": ProfileType.COMPLIANCE,
        "priority": 2,
        "entities": {
            "product": r"(?:ürün|product|için|for)[:\s]+([^\n]+)",
        }
    },

    # ─────────────────────────────────────────────────────
    # OPERATIONS INTENTS
    # ─────────────────────────────────────────────────────
    IntentType.EMAIL_COMPOSE: {
        "patterns": [
            r"\b(e-?mail|e.?posta)\b.*(yaz|oluştur|hazırla|draft)",
            r"\b(compose|write|draft)\b.*\b(email|mail)\b",
            r"\bmüşteri.*(yanıt|cevap|reply)",
        ],
        "profile": ProfileType.OPERATIONS,
        "priority": 2,
        "entities": {
            "recipient": r"(?:için|to|for)\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)*)",
            "subject": r"(?:konu|subject)[:\s]+([^\n]+)",
        }
    },

    IntentType.LINKEDIN_POST: {
        "patterns": [
            r"\blinkedin\b.*(post|paylaş|share)",
            r"\bsosyal\s+medya\b",
            r"\b(post|içerik)\s+(yaz|oluştur)\b",
        ],
        "profile": ProfileType.OPERATIONS,
        "priority": 3,
        "entities": {
            "topic": r"(?:konu|topic|hakkında|about)[:\s]+([^\n]+)",
        }
    },

    IntentType.CUSTOMER_COMMUNICATION: {
        "patterns": [
            r"\bmüşteri\b.*(iletişim|communication|contact)",
            r"\bcustomer\b.*(communication|contact|message)",
        ],
        "profile": ProfileType.OPERATIONS,
        "priority": 2,
        "entities": {
            "customer": r"(?:müşteri|customer)[:\s]+([A-ZÇĞİÖŞÜ][^\n]+)",
        }
    },

    # ─────────────────────────────────────────────────────
    # RISK INTENTS
    # ─────────────────────────────────────────────────────
    IntentType.RISK_ASSESSMENT: {
        "patterns": [
            r"\brisk\b.*(değerlendir|assess|analiz)",
            r"\bgüvenli\s+mi\b",
            r"\bonayl[ıi]y[ıi]m\s+m[ıi]\b",
            r"\btehlikeli\s+mi\b",
        ],
        "profile": ProfileType.FINANCE,  # Risk often finance-related
        "priority": 1,
        "entities": {
            "customer": r"([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)*)",
        }
    },
}


# ═════════════════════════════════════════════════════════
# INTENT DETECTOR
# ═════════════════════════════════════════════════════════
class IntentDetector:
    """
    Rule-based intent detector with multi-intent support
    """

    def __init__(self, context: Optional[Dict] = None):
        """
        Initialize detector

        Args:
            context: Optional context dict (from context.yaml)
        """
        self.context = context or {}
        self.patterns = INTENT_PATTERNS

    def detect(self, query: str, top_k: int = 3) -> List[Intent]:
        """
        Detect intents from query

        Args:
            query: User query
            top_k: Maximum number of intents to return

        Returns:
            List of detected intents, sorted by confidence
        """
        query_lower = query.lower()
        detected = []

        for intent_type, config in self.patterns.items():
            # Check if any pattern matches
            matches = []
            for pattern in config["patterns"]:
                if re.search(pattern, query_lower):
                    matches.append(pattern)

            if matches:
                # Calculate confidence (simple: ratio of matched patterns)
                confidence = len(matches) / len(config["patterns"])

                # Boost confidence if context matches
                confidence = self._apply_context_boost(confidence, intent_type, query_lower)

                # Extract entities
                entities = self._extract_entities(query, config.get("entities", {}))

                # Create intent
                intent = Intent(
                    type=intent_type,
                    confidence=confidence,
                    profile=config["profile"],
                    entities=entities,
                    sub_intents=[],
                    priority=config["priority"]
                )

                detected.append(intent)

        # Sort by confidence * priority (higher confidence, lower priority number = better)
        detected.sort(key=lambda x: (x.confidence, -x.priority), reverse=True)

        # Return top K
        return detected[:top_k]

    def _apply_context_boost(self, base_confidence: float, intent_type: IntentType, query: str) -> float:
        """
        Boost confidence based on context

        Examples:
        - If customer name is in query and we know that customer → boost risk-related intents
        - If time is Friday afternoon → boost decision-related intents
        """
        confidence = base_confidence

        # Customer context boost
        if self.context and "customers" in self.context:
            for customer_name in self.context["customers"].keys():
                if customer_name.lower() in query:
                    # Customer mentioned → boost risk assessment
                    if intent_type == IntentType.RISK_ASSESSMENT:
                        confidence *= 1.3
                    # Customer mentioned + invoice → boost invoice check
                    if intent_type == IntentType.INVOICE_CHECK and "fatura" in query:
                        confidence *= 1.2

        # Product context boost
        if self.context and "products" in self.context:
            for product_info in self.context["products"].values():
                if isinstance(product_info, dict):
                    product_name = product_info.get("name", "").lower()
                    if product_name and product_name in query:
                        # Hazardous product → boost ADR check
                        if product_info.get("un_number") and intent_type == IntentType.ADR_CHECK:
                            confidence *= 1.5

        # Cap at 1.0
        return min(confidence, 1.0)

    def _extract_entities(self, query: str, entity_patterns: Dict[str, str]) -> Dict[str, any]:
        """
        Extract entities from query using regex patterns

        Args:
            query: User query
            entity_patterns: Dict of entity_name -> regex_pattern

        Returns:
            Dict of extracted entities
        """
        entities = {}

        for entity_name, pattern in entity_patterns.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                # Extract first group if exists, otherwise full match
                entities[entity_name] = match.group(1) if match.groups() else match.group(0)

        return entities

    def get_primary_profile(self, intents: List[Intent]) -> ProfileType:
        """
        Determine primary profile from detected intents

        Args:
            intents: List of detected intents

        Returns:
            Primary profile type
        """
        if not intents:
            return ProfileType.OPERATIONS  # Default

        # Return profile of highest confidence intent
        return intents[0].profile


# ═════════════════════════════════════════════════════════
# SENSITIVE DATA DETECTION
# ═════════════════════════════════════════════════════════
SENSITIVE_PATTERNS = [
    r"\bşifre\b",
    r"\bpassword\b",
    r"\btoken\b",
    r"\bapi[_-]?key\b",
    r"\bsecret\b",
    r"\bcredential\b",
    r"\bprivate[_-]?key\b",
]


def is_sensitive_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Check if query contains sensitive data request

    Args:
        query: User query

    Returns:
        (is_sensitive, matched_pattern)
    """
    query_lower = query.lower()

    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, query_lower):
            return True, pattern

    return False, None


# ═════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Example context (normally loaded from context.yaml)
    example_context = {
        "customers": {
            "ABC_Lojistik": {"risk_score": 7}
        },
        "products": {
            "bioethanol_5L": {"un_number": "UN1170"}
        }
    }

    detector = IntentDetector(context=example_context)

    # Test queries
    test_queries = [
        "ABC'nin faturasını kontrol et",
        "5000 adet, $4.5, komisyon %7, net marj?",
        "Bioethanol için ADR kontrolü yap",
        "Müşteriye e-posta yaz",
        "LinkedIn post hazırla e-ticaret hakkında",
        "ABC güvenli mi?",
    ]

    print("=" * 60)
    print("INTENT DETECTION TEST")
    print("=" * 60)

    for query in test_queries:
        print(f"\nQuery: {query}")

        # Check if sensitive
        is_sens, pattern = is_sensitive_query(query)
        if is_sens:
            print(f"  ⚠️  SENSITIVE: {pattern}")
            continue

        # Detect intents
        intents = detector.detect(query, top_k=2)

        if intents:
            print(f"  Primary: {intents[0]}")
            if len(intents) > 1:
                print(f"  Secondary: {intents[1]}")

            # Show entities
            if intents[0].entities:
                print(f"  Entities: {intents[0].entities}")
        else:
            print("  ❌ No intent detected")
