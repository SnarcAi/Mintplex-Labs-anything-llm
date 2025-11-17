#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BurakAI - Main Engine
═════════════════════════════════════════════════════════
PRAGMATIC NEXUS Implementation

This is the heart of BurakAI - combining:
- Intent detection (What user wants)
- Context weaving (Understanding the situation)
- Tool orchestration (Getting things done)
- Memory (Learning over time)
- Cache (Speed optimization)

NEXUS vision, pragmatic implementation.
═════════════════════════════════════════════════════════
"""

import time
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Import Brain components
from Brain.intents import IntentDetector, is_sensitive_query, Intent, ProfileType
from Brain.tools import ToolOrchestrator, ToolResult
from Brain.memory import MemorySystem
from Brain.cache import CacheSystem, SmartInvalidator


@dataclass
class EngineResponse:
    """Response from engine"""
    success: bool
    response: str
    intent: Optional[Intent] = None
    profile: str = "operations"
    tools_used: List[str] = None
    latency_sec: float = 0.0
    cache_hit: bool = False
    metadata: Dict = None

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "response": self.response,
            "intent": str(self.intent) if self.intent else None,
            "profile": self.profile,
            "tools_used": self.tools_used or [],
            "latency_sec": round(self.latency_sec, 3),
            "cache_hit": self.cache_hit,
            "metadata": self.metadata or {}
        }


class BurakAIEngine:
    """
    Main BurakAI engine - Context-aware, tool-orchestrating, learning AI
    """

    def __init__(self, config_path: Path, context_path: Path):
        """
        Initialize engine

        Args:
            config_path: Path to config.yaml
            context_path: Path to context.yaml
        """
        self.config_path = Path(config_path)
        self.context_path = Path(context_path)

        # Load configurations
        self.config = self._load_yaml(config_path)
        self.context = self._load_yaml(context_path)

        # Get paths from config
        brain_dir = Path(self.config["system"]["brain_dir"])

        # Initialize components
        self.intent_detector = IntentDetector(context=self.context)
        self.tool_orchestrator = ToolOrchestrator(context=self.context)

        self.memory = MemorySystem(
            memory_file=brain_dir / "memory.jsonl",
            max_entries=self.config["brain"]["memory"].get("max_entries", 10000)
        )

        cache_config = self.config["brain"]["cache"]
        self.cache = CacheSystem(
            cache_dir=brain_dir / "cache",
            max_size_mb=cache_config.get("max_size_mb", 100),
            default_ttl=cache_config.get("ttl_seconds", 300),
            enable_disk=cache_config.get("enabled", True)
        )

        self.cache_invalidator = SmartInvalidator(self.cache)

        # Constitution (core rules)
        self.constitution = self.config.get("constitution", {})

        print(f"[BurakAI] Engine initialized")
        print(f"[BurakAI] Config: {config_path}")
        print(f"[BurakAI] Context: {context_path}")

    # ═════════════════════════════════════════════════════
    # MAIN QUERY PROCESSING
    # ═════════════════════════════════════════════════════

    def process_query(
        self,
        query: str,
        profile: Optional[str] = None,
        use_cache: bool = True
    ) -> EngineResponse:
        """
        Process user query with full NEXUS pipeline

        Args:
            query: User query
            profile: Force specific profile (None = auto-detect)
            use_cache: Use cache if available

        Returns:
            Engine response
        """
        start_time = time.time()

        try:
            # ─────────────────────────────────────────────
            # STEP 1: SECURITY CHECK
            # ─────────────────────────────────────────────
            is_sensitive, pattern = is_sensitive_query(query)
            if is_sensitive:
                response = self.constitution.get("rejection_policy", {}).get(
                    "on_sensitive_data",
                    "Üzgünüm, bu isteği yerine getirmem. (Gizli veri politikası)"
                )
                self.memory.log_query(query, "sensitive_blocked", "security", {})
                return EngineResponse(
                    success=False,
                    response=response,
                    latency_sec=time.time() - start_time,
                    metadata={"blocked_pattern": pattern}
                )

            # ─────────────────────────────────────────────
            # STEP 2: INTENT DETECTION (Cortex)
            # ─────────────────────────────────────────────
            intents = self.intent_detector.detect(query, top_k=2)

            if not intents:
                return EngineResponse(
                    success=False,
                    response="Üzgünüm, isteğinizi anlayamadım. Lütfen daha açık ifade edin.",
                    latency_sec=time.time() - start_time
                )

            primary_intent = intents[0]

            # Auto-detect profile if not specified
            if not profile:
                profile = primary_intent.profile.value

            # ─────────────────────────────────────────────
            # STEP 3: CACHE CHECK (Speed optimization)
            # ─────────────────────────────────────────────
            if use_cache:
                cached_result = self.cache.get_query_cache(query, profile)
                if cached_result:
                    self.memory.log_result(query, cached_result, time.time() - start_time, cache_hit=True)
                    return EngineResponse(
                        success=True,
                        response=cached_result,
                        intent=primary_intent,
                        profile=profile,
                        latency_sec=time.time() - start_time,
                        cache_hit=True
                    )

            # ─────────────────────────────────────────────
            # STEP 4: CONTEXT WEAVING (Understanding)
            # ─────────────────────────────────────────────
            context_info = self._weave_context(query, primary_intent)

            # ─────────────────────────────────────────────
            # STEP 5: STRATEGY SELECTION
            # ─────────────────────────────────────────────
            strategy = self._select_strategy(primary_intent, context_info)

            # ─────────────────────────────────────────────
            # STEP 6: TOOL EXECUTION (Cerebellum)
            # ─────────────────────────────────────────────
            response, tools_used = self._execute_tools(primary_intent, query, context_info)

            # ─────────────────────────────────────────────
            # STEP 7: RESPONSE FORMATTING
            # ─────────────────────────────────────────────
            formatted_response = self._format_response(response, profile, context_info)

            # ─────────────────────────────────────────────
            # STEP 8: MEMORY & CACHE
            # ─────────────────────────────────────────────
            latency = time.time() - start_time

            # Log to memory
            self.memory.log_query(
                query=query,
                intent=primary_intent.type.value,
                profile=profile,
                entities=primary_intent.entities
            )
            self.memory.log_result(
                query=query,
                result=formatted_response[:500],
                latency_sec=latency,
                cache_hit=False,
                tools_used=tools_used
            )

            # Cache result
            self.cache.set_query_cache(query, profile, formatted_response, ttl=300)

            return EngineResponse(
                success=True,
                response=formatted_response,
                intent=primary_intent,
                profile=profile,
                tools_used=tools_used,
                latency_sec=latency,
                cache_hit=False,
                metadata={"strategy": strategy, "context": context_info}
            )

        except Exception as e:
            return EngineResponse(
                success=False,
                response=f"Bir hata oluştu: {str(e)}",
                latency_sec=time.time() - start_time,
                metadata={"error": str(e)}
            )

    # ═════════════════════════════════════════════════════
    # CONTEXT WEAVING (NEXUS Core Feature)
    # ═════════════════════════════════════════════════════

    def _weave_context(self, query: str, intent: Intent) -> Dict[str, Any]:
        """
        Weave context from multiple sources

        This is the simplified version of NEXUS's "Context Fabric"

        Args:
            query: User query
            intent: Detected intent

        Returns:
            Context information
        """
        context_info = {
            "query_lowercase": query.lower(),
            "current_profile": intent.profile.value,
        }

        # Extract customer if mentioned
        if "customer" in intent.entities:
            customer_name = intent.entities["customer"]
            customer_data = self.context.get("customers", {}).get(customer_name)
            if customer_data:
                context_info["customer"] = customer_data
                context_info["customer_name"] = customer_name

        # Extract product if mentioned
        query_lower = query.lower()
        for product_id, product_data in self.context.get("products", {}).items():
            if product_id.startswith("_"):
                continue
            product_name = product_data.get("name", "").lower()
            if product_name and product_name in query_lower:
                context_info["product"] = product_data
                context_info["product_id"] = product_id
                break

        # Business context (cash status, focus areas)
        business_status = self.context.get("business", {}).get("status", {})
        context_info["business_status"] = business_status

        # Time context
        import datetime
        now = datetime.datetime.now()
        context_info["time"] = {
            "hour": now.hour,
            "weekday": now.strftime("%A").lower(),
            "is_friday_afternoon": now.weekday() == 4 and now.hour >= 16
        }

        return context_info

    # ═════════════════════════════════════════════════════
    # STRATEGY SELECTION (NEXUS Feature)
    # ═════════════════════════════════════════════════════

    def _select_strategy(self, intent: Intent, context: Dict) -> str:
        """
        Select execution strategy

        Simplified version of NEXUS's strategy selector

        Strategies:
        - INSTANT: Cache hit (already handled)
        - FAST: Single simple tool
        - SMART: Multiple tools, standard model
        - DEEP: Complex analysis (future)

        Args:
            intent: Detected intent
            context: Context information

        Returns:
            Strategy name
        """
        # High priority intents → SMART
        if intent.priority == 1:
            return "SMART"

        # Simple queries → FAST
        if len(intent.entities) <= 1:
            return "FAST"

        # Default
        return "SMART"

    # ═════════════════════════════════════════════════════
    # TOOL EXECUTION
    # ═════════════════════════════════════════════════════

    def _execute_tools(self, intent: Intent, query: str, context: Dict) -> Tuple[str, List[str]]:
        """
        Execute tools based on intent

        Args:
            intent: Detected intent
            query: User query
            context: Context information

        Returns:
            (response_text, tools_used_list)
        """
        from Brain.intents import IntentType

        tools_used = []

        # ─────────────────────────────────────────────
        # MARGIN CALCULATION
        # ─────────────────────────────────────────────
        if intent.type == IntentType.MARGIN_CALC:
            # Try to use Referee for margin calculation
            from Tools.referee_margin import run as referee_run

            result = referee_run(query, pretty=True)
            tools_used.append("referee_margin")

            if "error" in result:
                return f"❌ {result['error']}", tools_used
            else:
                return result["result"], tools_used

        # ─────────────────────────────────────────────
        # INVOICE CHECK
        # ─────────────────────────────────────────────
        elif intent.type == IntentType.INVOICE_CHECK:
            response_parts = []

            # 1. Risk assessment if customer known
            if "customer_name" in context:
                risk_result = self.tool_orchestrator.execute_tool(
                    "risk_score",
                    customer=context["customer_name"]
                )
                tools_used.append("risk_score")

                if risk_result.success:
                    risk_data = risk_result.data
                    response_parts.append(f"""
🔍 **Müşteri: {risk_data['customer']}**
- Risk: {risk_data['risk_level']} ({risk_data['risk_score']}/10)
- Ortalama Ödeme: {risk_data['payment_avg_days']} gün
- Geçmiş Sorunlar: {risk_data['past_issues']}
""")
                    if risk_data['requires_deposit']:
                        response_parts.append("⚠️ **BU MÜŞTERİ İÇİN KAPARO GEREKLİ**")

            # 2. Try margin calculation if numbers in query
            has_numbers = bool(re.search(r'\d+', query))
            if has_numbers:
                from Tools.referee_margin import run as referee_run
                margin_result = referee_run(query, pretty=False)
                tools_used.append("margin_calc")

                if "error" not in margin_result:
                    net_margin = margin_result['net_margin_percent']
                    target_margin = self.context.get("business", {}).get("targets", {}).get("net_margin_percent", 28)

                    response_parts.append(f"""
💰 **Marj Analizi**
- Net Marj: %{net_margin:.2f}
- Hedef: %{target_margin:.0f}
""")
                    if net_margin < target_margin:
                        diff = target_margin - net_margin
                        response_parts.append(f"⚠️ Marj hedefin {diff:.1f} puan altında!")

            # 3. Combine response
            if response_parts:
                return "\n".join(response_parts), tools_used
            else:
                return "Fatura kontrolü için daha fazla bilgi gerekli (müşteri adı, tutarlar).", tools_used

        # ─────────────────────────────────────────────
        # RISK ASSESSMENT
        # ─────────────────────────────────────────────
        elif intent.type == IntentType.RISK_ASSESSMENT:
            customer = intent.entities.get("customer")
            if not customer and "customer_name" in context:
                customer = context["customer_name"]

            if not customer:
                return "Risk değerlendirmesi için müşteri adı gerekli.", tools_used

            risk_result = self.tool_orchestrator.execute_tool("risk_score", customer=customer)
            tools_used.append("risk_score")

            if risk_result.success:
                data = risk_result.data
                return f"""
🎯 **{data['customer']} - Risk Değerlendirmesi**

Risk Seviyesi: **{data['risk_level']}** ({data['risk_score']}/10)

📊 Detaylar:
- Ortalama Ödeme Süresi: {data['payment_avg_days']} gün
- Geçmiş Sorunlar: {data['past_issues']}
- Kaparo Gerekli: {'Evet ✓' if data['requires_deposit'] else 'Hayır ✗'}

💡 Notlar:
{data['notes']}
""", tools_used
            else:
                return f"❌ {risk_result.error}", tools_used

        # ─────────────────────────────────────────────
        # ADR CHECK
        # ─────────────────────────────────────────────
        elif intent.type == IntentType.ADR_CHECK:
            un_number = intent.entities.get("un_number")

            if not un_number and "product" in context:
                un_number = context["product"].get("un_number")

            if not un_number:
                return "ADR kontrolü için UN numarası gerekli.", tools_used

            adr_result = self.tool_orchestrator.execute_tool("adr_check", un_number=un_number)
            tools_used.append("adr_check")

            if adr_result.success:
                data = adr_result.data
                if data["status"] == "FOUND":
                    return f"""
📦 **ADR Kontrolü: {data['un_number']}**

Ürün: {data['name']}
Sınıf: {data['class']} ({data['hazard']})
Paketleme Grubu: {data.get('packing_group', 'N/A')}

Etiketler: {data['label']}
Limited Quantity: {data.get('limited_quantity', 'N/A')}

Durum: **{data['compliance']}**
""", tools_used
                else:
                    return f"❌ {data['note']}", tools_used
            else:
                return f"❌ {adr_result.error}", tools_used

        # ─────────────────────────────────────────────
        # DEFAULT: Generic response
        # ─────────────────────────────────────────────
        else:
            return f"Bu istek türü ({intent.type.value}) henüz tam olarak desteklenmiyor. Geliştirme devam ediyor.", tools_used

    # ═════════════════════════════════════════════════════
    # RESPONSE FORMATTING
    # ═════════════════════════════════════════════════════

    def _format_response(self, response: str, profile: str, context: Dict) -> str:
        """
        Format response based on profile and context

        Args:
            response: Raw response
            profile: Active profile
            context: Context information

        Returns:
            Formatted response
        """
        # Profile-specific formatting
        profile_config = self.context.get("profiles", {}).get(profile, {})
        tone_config = profile_config.get("tone", {})

        # Add profile signature (subtle)
        if tone_config.get("focus") == "sayı_odaklı":
            # Finance profile - already has numbers, no need to change
            pass

        # Add time-aware note if Friday afternoon
        if context.get("time", {}).get("is_friday_afternoon"):
            response += "\n\n💡 Cuma öğleden sonra - hafta sonu öncesi karar zamanı!"

        # Add warnings if needed
        if "customer" in context:
            customer = context["customer"]
            if customer.get("risk_score", 0) >= 7:
                response += f"\n\n⚠️ Yüksek riskli müşteri - dikkatli ol!"

        return response.strip()

    # ═════════════════════════════════════════════════════
    # STATS & MONITORING
    # ═════════════════════════════════════════════════════

    def get_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get engine statistics"""
        memory_stats = self.memory.get_stats(days=days)
        cache_stats = self.cache.get_stats()

        return {
            "memory": memory_stats,
            "cache": cache_stats,
            "performance": {
                "avg_latency_sec": memory_stats.get("avg_latency", 0),
                "cache_hit_rate": cache_stats.get("hit_rate", 0),
            }
        }

    def analyze_patterns(self, days: int = 7) -> Dict[str, Any]:
        """Analyze learned patterns"""
        return self.memory.analyze_patterns(days=days)

    # ═════════════════════════════════════════════════════
    # UTILITIES
    # ═════════════════════════════════════════════════════

    def _load_yaml(self, path: Path) -> Dict:
        """Load YAML file"""
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)


# ═════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═════════════════════════════════════════════════════════
if __name__ == "__main__":
    import json

    # Initialize engine
    engine = BurakAIEngine(
        config_path=Path("../Core/config.yaml"),
        context_path=Path("context.yaml")
    )

    # Test queries
    test_queries = [
        "5000 adet, $4.5, komisyon %7, kargo 600 TL, iade %1.2, maliyet 118 TL net marj?",
        "ABC Lojistik güvenli mi?",
        "UN1170 için ADR kontrolü",
    ]

    print("\n" + "=" * 60)
    print("ENGINE TEST")
    print("=" * 60)

    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 60)

        response = engine.process_query(query)

        print(f"✓ Success: {response.success}")
        print(f"⚡ Latency: {response.latency_sec:.3f}s")
        print(f"🎯 Intent: {response.intent}")
        print(f"🛠️  Tools: {response.tools_used}")
        print(f"\n{response.response}")
        print()
