#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BurakAI - Command Line Interface
═════════════════════════════════════════════════════════
Quick CLI for power users

Usage:
  python cli.py                          # Interactive mode
  python cli.py "query here"             # Single query
  python cli.py --stats                  # Show stats
  python cli.py --analyze                # Analyze patterns
═════════════════════════════════════════════════════════
"""

import sys
import json
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Brain.engine import BurakAIEngine


def print_banner():
    """Print welcome banner"""
    banner = """
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   ██████╗ ██╗   ██╗██████╗  █████╗ ██╗  ██╗ █████╗ ██╗║
║   ██╔══██╗██║   ██║██╔══██╗██╔══██╗██║ ██╔╝██╔══██╗██║║
║   ██████╔╝██║   ██║██████╔╝███████║█████╔╝ ███████║██║║
║   ██╔══██╗██║   ██║██╔══██╗██╔══██║██╔═██╗ ██╔══██║██║║
║   ██████╔╝╚██████╔╝██║  ██║██║  ██║██║  ██╗██║  ██║██║║
║   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝║
║                                                       ║
║   Pragmatic NEXUS v1.0 - Context-Aware AI             ║
║   "Sen düşün, ben hallederim"                         ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
"""
    print(banner)


def print_help():
    """Print help message"""
    help_text = """
Komutlar:
  /help          - Bu yardım mesajı
  /stats         - İstatistikler
  /analyze       - Pattern analizi
  /clear         - Cache temizle
  /exit, /quit   - Çıkış

Örnekler:
  > 5000 adet, $4.5, komisyon %7, net marj?
  > ABC Lojistik güvenli mi?
  > UN1170 için ADR kontrolü
"""
    print(help_text)


def interactive_mode(engine: BurakAIEngine):
    """Interactive REPL mode"""
    print_banner()
    print("\n💡 Hazır. Sorularını sor veya /help yaz.\n")

    while True:
        try:
            # Get input
            query = input("\n[BurakAI] >> ").strip()

            if not query:
                continue

            # Commands
            if query.startswith("/"):
                cmd = query.lower()

                if cmd in ["/exit", "/quit", "/q"]:
                    print("\n👋 Görüşmek üzere!")
                    break

                elif cmd == "/help":
                    print_help()

                elif cmd == "/stats":
                    stats = engine.get_stats(days=7)
                    print("\n📊 İSTATİSTİKLER (Son 7 gün)")
                    print("─" * 50)
                    print(json.dumps(stats, indent=2, ensure_ascii=False))

                elif cmd == "/analyze":
                    patterns = engine.analyze_patterns(days=7)
                    print("\n🔍 PATTERN ANALİZİ (Son 7 gün)")
                    print("─" * 50)
                    print(json.dumps(patterns, indent=2, ensure_ascii=False))

                elif cmd == "/clear":
                    engine.cache.clear()
                    print("\n✓ Cache temizlendi")

                else:
                    print(f"❌ Bilinmeyen komut: {query}")
                    print("   /help yazarak komutları görebilirsin")

                continue

            # Process query
            print("\n⚙️  İşleniyor...")
            response = engine.process_query(query)

            # Print response
            print("\n" + "─" * 60)
            if response.success:
                print(response.response)
                print("\n" + "─" * 60)
                print(f"⚡ {response.latency_sec:.3f}s | 🎯 {response.profile} | 🛠️  {len(response.tools_used or [])} tool")
                if response.cache_hit:
                    print("💾 Cache hit!")
            else:
                print(f"❌ Hata: {response.response}")

        except KeyboardInterrupt:
            print("\n\n👋 (Ctrl+C) Çıkış...")
            break

        except Exception as e:
            print(f"\n❌ Beklenmeyen hata: {e}")


def single_query_mode(engine: BurakAIEngine, query: str):
    """Single query mode"""
    response = engine.process_query(query)

    if response.success:
        print(response.response)
        if "--verbose" in sys.argv:
            print(f"\n[Latency: {response.latency_sec:.3f}s, Profile: {response.profile}, Tools: {response.tools_used}]")
    else:
        print(f"Error: {response.response}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point"""
    # Find BurakAI root
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    config_path = root_dir / "Core" / "config.yaml"
    context_path = root_dir / "Brain" / "context.yaml"

    # Check files exist
    if not config_path.exists():
        print(f"Error: Config not found at {config_path}", file=sys.stderr)
        sys.exit(1)

    if not context_path.exists():
        print(f"Error: Context not found at {context_path}", file=sys.stderr)
        sys.exit(1)

    # Initialize engine
    try:
        engine = BurakAIEngine(config_path=config_path, context_path=context_path)
    except Exception as e:
        print(f"Error initializing engine: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse arguments
    args = sys.argv[1:]

    if "--stats" in args:
        stats = engine.get_stats(days=7)
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        sys.exit(0)

    elif "--analyze" in args:
        patterns = engine.analyze_patterns(days=7)
        print(json.dumps(patterns, indent=2, ensure_ascii=False))
        sys.exit(0)

    elif args and not args[0].startswith("--"):
        # Single query mode
        query = " ".join(arg for arg in args if not arg.startswith("--"))
        single_query_mode(engine, query)

    else:
        # Interactive mode
        interactive_mode(engine)


if __name__ == "__main__":
    main()
