#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BurakAI - System Validation
═════════════════════════════════════════════════════════
Comprehensive system test to validate all components
═════════════════════════════════════════════════════════
"""

import sys
from pathlib import Path

# Test results
tests_passed = 0
tests_failed = 0
errors = []


def test(name: str, func):
    """Run a test"""
    global tests_passed, tests_failed, errors

    try:
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"{'='*60}")

        func()

        print(f"✅ PASSED: {name}")
        tests_passed += 1

    except Exception as e:
        print(f"❌ FAILED: {name}")
        print(f"   Error: {e}")
        errors.append((name, str(e)))
        tests_failed += 1


def test_file_structure():
    """Test 1: Verify directory structure"""
    required_files = [
        "Core/config.yaml",
        "Brain/context.yaml",
        "Brain/intents.py",
        "Brain/tools.py",
        "Brain/memory.py",
        "Brain/cache.py",
        "Brain/engine.py",
        "Tools/referee_margin.py",
        "App/cli.py",
        "README.md",
        "Factory/tasks/daily.yaml",
    ]

    root = Path("BurakAI")
    missing = []

    for file in required_files:
        if not (root / file).exists():
            missing.append(file)

    if missing:
        raise AssertionError(f"Missing files: {missing}")

    print(f"✓ All {len(required_files)} required files exist")


def test_config_loading():
    """Test 2: Load configuration files"""
    import yaml

    # Load config.yaml
    with open("BurakAI/Core/config.yaml") as f:
        config = yaml.safe_load(f)

    assert "system" in config, "Missing 'system' in config"
    assert "models" in config, "Missing 'models' in config"
    assert "brain" in config, "Missing 'brain' in config"

    print(f"✓ config.yaml loaded successfully")

    # Load context.yaml
    with open("BurakAI/Brain/context.yaml") as f:
        context = yaml.safe_load(f)

    assert "personal" in context, "Missing 'personal' in context"
    assert "business" in context, "Missing 'business' in context"
    assert "customers" in context, "Missing 'customers' in context"

    print(f"✓ context.yaml loaded successfully")


def test_intent_detection():
    """Test 3: Intent detection"""
    sys.path.insert(0, "BurakAI")

    from Brain.intents import IntentDetector, IntentType
    import yaml

    # Load context
    with open("BurakAI/Brain/context.yaml") as f:
        context = yaml.safe_load(f)

    detector = IntentDetector(context=context)

    # Test margin calculation intent
    intents = detector.detect("5000 adet, $4.5, komisyon %7, net marj?")
    assert len(intents) > 0, "No intents detected"
    assert intents[0].type == IntentType.MARGIN_CALC, f"Wrong intent: {intents[0].type}"
    print(f"✓ Margin calc intent detected: {intents[0]}")

    # Test risk assessment intent
    intents = detector.detect("ABC Lojistik güvenli mi?")
    assert len(intents) > 0, "No intents detected"
    assert intents[0].type == IntentType.RISK_ASSESSMENT, f"Wrong intent: {intents[0].type}"
    print(f"✓ Risk assessment intent detected: {intents[0]}")

    # Test ADR check intent
    intents = detector.detect("UN1170 için ADR kontrolü")
    assert len(intents) > 0, "No intents detected"
    assert intents[0].type == IntentType.ADR_CHECK, f"Wrong intent: {intents[0].type}"
    print(f"✓ ADR check intent detected: {intents[0]}")


def test_margin_calculator():
    """Test 4: Margin calculator"""
    sys.path.insert(0, "BurakAI")

    from Tools.referee_margin import RefereeMargin

    calc = RefereeMargin()

    # Test calculation
    result = calc.calculate(
        quantity=5000,
        price=4.5,
        cost=118,
        price_currency="USD",
        commission_percent=7,
        shipping_cost=600,
        return_rate_percent=1.2,
        fx_rate=34.10
    )

    assert result.quantity == 5000, "Wrong quantity"
    assert result.net_margin_percent > 0, "Net margin should be positive"
    assert result.net_margin_percent < 100, "Net margin should be < 100%"

    print(f"✓ Margin calculation: {result.net_margin_percent:.2f}%")

    # Test query parsing
    success, params, error = calc.parse_query(
        "5000 adet, $4.5, komisyon %7, kargo 600 TL, maliyet 118 TL"
    )

    assert success, f"Parse failed: {error}"
    assert params["quantity"] == 5000, "Wrong quantity parsed"
    assert params["price"] == 4.5, "Wrong price parsed"

    print(f"✓ Query parsing successful")


def test_tools_orchestrator():
    """Test 5: Tool orchestrator"""
    sys.path.insert(0, "BurakAI")

    from Brain.tools import ToolOrchestrator
    import yaml

    # Load context
    with open("BurakAI/Brain/context.yaml") as f:
        context = yaml.safe_load(f)

    orchestrator = ToolOrchestrator(context=context)

    # Test margin calc tool
    result = orchestrator.execute_tool(
        "margin_calc",
        cost=118,
        price=164,
        quantity=5000,
        commission_percent=7,
        shipping_cost=600
    )

    assert result.success, f"Tool execution failed: {result.error}"
    assert "net_margin_percent" in result.data, "Missing net_margin_percent"

    print(f"✓ Margin calc tool: {result.data['net_margin_percent']:.2f}%")

    # Test risk score tool
    result = orchestrator.execute_tool(
        "risk_score",
        customer="ABC_Lojistik"
    )

    assert result.success, f"Tool execution failed: {result.error}"
    assert result.data["risk_score"] == 7, "Wrong risk score"

    print(f"✓ Risk score tool: {result.data['risk_level']}")


def test_memory_system():
    """Test 6: Memory system"""
    sys.path.insert(0, "BurakAI")

    from Brain.memory import MemorySystem
    from pathlib import Path
    import tempfile

    # Create temp memory file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        memory_file = Path(f.name)

    try:
        mem = MemorySystem(memory_file, max_entries=100)

        # Log some events
        mem.log_query("test query", "margin_calc", "finance", {})
        mem.log_result("test query", "test result", 1.5, False, ["tool1"])
        mem.log_value_generated("test_task", 1000, 0.5)

        # Get stats
        stats = mem.get_stats(days=1)

        assert stats["total_entries"] == 3, f"Wrong entry count: {stats['total_entries']}"
        assert stats["total_value_try"] == 1000, f"Wrong value: {stats['total_value_try']}"

        print(f"✓ Memory system: {stats['total_entries']} entries logged")

    finally:
        # Cleanup
        memory_file.unlink(missing_ok=True)


def test_cache_system():
    """Test 7: Cache system"""
    sys.path.insert(0, "BurakAI")

    from Brain.cache import CacheSystem
    from pathlib import Path
    import tempfile

    # Create temp cache dir
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = CacheSystem(Path(tmpdir), max_size_mb=1, enable_disk=True)

        # Test set/get
        cache.set("test_key", "test_value", ttl=60)
        value = cache.get("test_key")

        assert value == "test_value", f"Wrong value: {value}"

        # Test query cache
        cache.set_query_cache("test query", "finance", "test result", ttl=60)
        cached = cache.get_query_cache("test query", "finance")

        assert cached == "test result", f"Wrong cached result: {cached}"

        # Test stats
        stats = cache.get_stats()
        assert stats["hits"] >= 2, f"Wrong hit count: {stats['hits']}"

        print(f"✓ Cache system: {stats['hits']} hits, {stats['hit_rate']:.2%} hit rate")


def test_engine_initialization():
    """Test 8: Engine initialization"""
    sys.path.insert(0, "BurakAI")

    from Brain.engine import BurakAIEngine
    from pathlib import Path

    # Initialize engine
    engine = BurakAIEngine(
        config_path=Path("BurakAI/Core/config.yaml"),
        context_path=Path("BurakAI/Brain/context.yaml")
    )

    assert engine is not None, "Engine failed to initialize"
    assert engine.config is not None, "Config not loaded"
    assert engine.context is not None, "Context not loaded"

    print(f"✓ Engine initialized successfully")


def test_end_to_end():
    """Test 9: End-to-end query processing"""
    sys.path.insert(0, "BurakAI")

    from Brain.engine import BurakAIEngine
    from pathlib import Path

    # Initialize engine
    engine = BurakAIEngine(
        config_path=Path("BurakAI/Core/config.yaml"),
        context_path=Path("BurakAI/Brain/context.yaml")
    )

    # Test query
    query = "5000 adet, $4.5, komisyon %7, kargo 600 TL, maliyet 118 TL net marj?"

    response = engine.process_query(query)

    assert response.success, f"Query failed: {response.response}"
    assert response.latency_sec < 5.0, f"Too slow: {response.latency_sec}s"
    assert len(response.response) > 0, "Empty response"

    print(f"✓ End-to-end test successful")
    print(f"  Latency: {response.latency_sec:.3f}s")
    print(f"  Profile: {response.profile}")
    print(f"  Tools used: {response.tools_used}")
    print(f"\nResponse preview:")
    print(response.response[:200] + "...")


def main():
    """Run all tests"""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "BurakAI System Validation" + " " * 23 + "║")
    print("╚" + "═" * 58 + "╝\n")

    # Run tests
    test("File Structure", test_file_structure)
    test("Configuration Loading", test_config_loading)
    test("Intent Detection", test_intent_detection)
    test("Margin Calculator", test_margin_calculator)
    test("Tool Orchestrator", test_tools_orchestrator)
    test("Memory System", test_memory_system)
    test("Cache System", test_cache_system)
    test("Engine Initialization", test_engine_initialization)
    test("End-to-End Query", test_end_to_end)

    # Summary
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 20 + "SUMMARY" + " " * 31 + "║")
    print("╠" + "═" * 58 + "╣")
    print(f"║  Tests Passed: {tests_passed:2d}" + " " * 42 + "║")
    print(f"║  Tests Failed: {tests_failed:2d}" + " " * 42 + "║")
    print("╚" + "═" * 58 + "╝\n")

    if tests_failed > 0:
        print("❌ FAILED TESTS:")
        for name, error in errors:
            print(f"   - {name}: {error}")
        sys.exit(1)
    else:
        print("✅ ALL TESTS PASSED!")
        print("\n🚀 BurakAI is ready to use!")
        print("\nNext steps:")
        print("  1. cd BurakAI")
        print("  2. python App/cli.py")
        print("  3. Try: '5000 adet, $4.5, komisyon %7, net marj?'")
        sys.exit(0)


if __name__ == "__main__":
    main()
