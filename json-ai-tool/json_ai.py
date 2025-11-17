#!/usr/bin/env python3
"""
JSON AI Tool - Standalone CLI
Qwen 2.5 7B ile offline JSON işlemleri
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import re

class JSONAITool:
    def __init__(self, model_path: str = None, use_ai: bool = True):
        """
        Args:
            model_path: Qwen model path (None ise auto-detect)
            use_ai: AI kullan (False ise sadece basic işlemler)
        """
        self.use_ai = use_ai
        self.model = None
        self.tokenizer = None

        if use_ai:
            self._load_model(model_path)

    def _load_model(self, model_path: str = None):
        """Qwen modelini yükle"""
        if model_path is None:
            # Auto-detect HF cache
            cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
            qwen_dirs = list(cache_dir.glob("models--Qwen--Qwen2.5-7B-Instruct"))

            if qwen_dirs:
                # En son snapshot'ı bul
                snapshots = list(qwen_dirs[0].glob("snapshots/*"))
                if snapshots:
                    model_path = str(snapshots[-1])
                    print(f"✓ Model bulundu: {model_path}")

        if not model_path or not Path(model_path).exists():
            print("❌ Model bulunamadı! Manuel path verin veya --no-ai kullanın")
            sys.exit(1)

        print("🔄 Model yükleniyor... (RTX 5080'de ~10 saniye)")

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="cuda",
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )

        print("✓ Model yüklendi (GPU)")

    def _generate(self, prompt: str, max_tokens: int = 2048) -> str:
        """AI ile text üret"""
        if not self.use_ai:
            return "AI devre dışı (--no-ai)"

        messages = [
            {"role": "system", "content": "You are a JSON expert assistant. Always respond with valid JSON when generating data."},
            {"role": "user", "content": prompt}
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer([text], return_tensors="pt").to("cuda")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.1,
                top_p=0.9,
                do_sample=True
            )

        response = self.tokenizer.decode(
            outputs[0][len(inputs.input_ids[0]):],
            skip_special_tokens=True
        )

        return response.strip()

    # ========== JSON İŞLEMLERİ ==========

    def validate(self, json_input: Union[str, dict]) -> Dict:
        """JSON'u validate et"""
        try:
            if isinstance(json_input, str):
                data = json.loads(json_input)
            else:
                data = json_input

            return {
                "valid": True,
                "data": data,
                "message": "✓ JSON geçerli",
                "stats": self._get_stats(data)
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": str(e),
                "line": e.lineno,
                "column": e.colno,
                "message": f"❌ Syntax hatası: {e.msg}"
            }

    def fix(self, broken_json: str) -> Dict:
        """JSON hatalarını düzelt"""
        fixes = []
        fixed = broken_json

        # 1. Trailing commas
        if re.search(r',(\s*[}\]])', fixed):
            fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
            fixes.append("Trailing comma silindi")

        # 2. Single quotes -> double quotes
        if "'" in fixed:
            fixed = fixed.replace("'", '"')
            fixes.append("Single quote -> double quote")

        # 3. Unquoted keys
        fixed = re.sub(r'(\{|,)\s*([a-zA-Z_]\w*)\s*:', r'\1"\2":', fixed)
        if len(fixes) == len(fixes):  # if changed
            fixes.append("Key'lere quote eklendi")

        # 4. Comments
        fixed = re.sub(r'//.*', '', fixed)
        fixed = re.sub(r'/\*[\s\S]*?\*/', '', fixed)

        # Test et
        try:
            data = json.loads(fixed)
            return {
                "success": True,
                "original": broken_json,
                "fixed": fixed,
                "data": data,
                "fixes": fixes,
                "message": f"✓ {len(fixes)} hata düzeltildi"
            }
        except json.JSONDecodeError as e:
            # AI ile dene
            if self.use_ai:
                return self._fix_with_ai(broken_json)
            else:
                return {
                    "success": False,
                    "error": str(e),
                    "fixes": fixes,
                    "message": "❌ Otomatik düzeltme başarısız (AI dene: --ai)"
                }

    def _fix_with_ai(self, broken_json: str) -> Dict:
        """AI ile JSON düzelt"""
        prompt = f"""Fix this broken JSON and return ONLY the valid JSON:

{broken_json}

Return only valid JSON, no explanations."""

        response = self._generate(prompt, max_tokens=4096)

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}|\[[\s\S]*\]', response)
        if json_match:
            try:
                fixed = json_match.group(0)
                data = json.loads(fixed)
                return {
                    "success": True,
                    "original": broken_json,
                    "fixed": fixed,
                    "data": data,
                    "method": "AI",
                    "message": "✓ AI ile düzeltildi"
                }
            except:
                pass

        return {
            "success": False,
            "message": "❌ AI de düzeltemedi",
            "ai_response": response
        }

    def analyze(self, json_input: Union[str, dict]) -> Dict:
        """JSON'u analiz et"""
        if isinstance(json_input, str):
            data = json.loads(json_input)
        else:
            data = json_input

        analysis = {
            "type": self._get_type(data),
            "stats": self._get_stats(data),
            "structure": self._analyze_structure(data),
            "schema": self._infer_schema(data),
        }

        return analysis

    def generate(self, count: int = 10, template: Dict = None, data_type: str = "generic") -> Dict:
        """JSON data üret"""

        if template:
            # Template-based
            results = []
            for i in range(count):
                record = self._apply_template(template, i)
                results.append(record)

            return {
                "success": True,
                "count": len(results),
                "data": results,
                "method": "template"
            }

        elif self.use_ai:
            # AI-based
            return self._generate_with_ai(count, data_type)

        else:
            # Basic generation
            return self._generate_basic(count, data_type)

    def _generate_with_ai(self, count: int, data_type: str) -> Dict:
        """AI ile veri üret"""
        prompt = f"""Generate {count} realistic {data_type} records in JSON format.

Requirements:
- Each record should have realistic values
- Use proper data types
- Include variety

Return ONLY a JSON array, no explanations."""

        response = self._generate(prompt, max_tokens=4096)

        # Extract JSON
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return {
                    "success": True,
                    "count": len(data),
                    "data": data,
                    "method": "AI"
                }
            except:
                pass

        return {
            "success": False,
            "message": "AI JSON üretemedi",
            "raw_response": response
        }

    def _generate_basic(self, count: int, data_type: str) -> Dict:
        """Basit veri üret (AI olmadan)"""
        import random
        import uuid
        from datetime import datetime

        results = []

        for i in range(count):
            if data_type == "user":
                record = {
                    "id": i + 1,
                    "username": f"user{i+1}",
                    "email": f"user{i+1}@example.com",
                    "age": random.randint(18, 80),
                    "active": random.choice([True, False]),
                    "created_at": datetime.now().isoformat()
                }
            elif data_type == "product":
                record = {
                    "id": i + 1,
                    "sku": f"SKU-{random.randint(1000, 9999)}",
                    "name": f"Product {i+1}",
                    "price": round(random.uniform(10, 1000), 2),
                    "in_stock": random.choice([True, False]),
                    "quantity": random.randint(0, 500)
                }
            else:  # generic
                record = {
                    "id": i + 1,
                    "uuid": str(uuid.uuid4()),
                    "value": random.randint(1, 1000),
                    "timestamp": datetime.now().isoformat()
                }

            results.append(record)

        return {
            "success": True,
            "count": len(results),
            "data": results,
            "method": "basic"
        }

    def _apply_template(self, template: dict, index: int) -> dict:
        """Template'e göre veri üret"""
        import uuid
        import random
        from datetime import datetime

        result = {}

        for key, value in template.items():
            if isinstance(value, str):
                # Replace placeholders
                result[key] = (value
                    .replace("{{index}}", str(index))
                    .replace("{{uuid}}", str(uuid.uuid4()))
                    .replace("{{timestamp}}", str(int(datetime.now().timestamp())))
                    .replace("{{random}}", str(random.randint(1, 1000)))
                )
            elif isinstance(value, dict):
                result[key] = self._apply_template(value, index)
            elif isinstance(value, list):
                result[key] = [self._apply_template(item, index) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value

        return result

    # ========== HELPER METHODS ==========

    def _get_type(self, data) -> str:
        if isinstance(data, list):
            return "array"
        elif isinstance(data, dict):
            return "object"
        else:
            return type(data).__name__

    def _get_stats(self, data) -> Dict:
        json_str = json.dumps(data)
        return {
            "size_bytes": len(json_str),
            "size_kb": round(len(json_str) / 1024, 2),
            "depth": self._compute_depth(data),
            "node_count": self._count_nodes(data)
        }

    def _compute_depth(self, data, current=0) -> int:
        if not isinstance(data, (dict, list)):
            return current

        if isinstance(data, list):
            if not data:
                return current
            return max(self._compute_depth(item, current + 1) for item in data)
        else:
            if not data:
                return current
            return max(self._compute_depth(val, current + 1) for val in data.values())

    def _count_nodes(self, data) -> int:
        if not isinstance(data, (dict, list)):
            return 1

        if isinstance(data, list):
            return 1 + sum(self._count_nodes(item) for item in data)
        else:
            return 1 + sum(self._count_nodes(val) for val in data.values())

    def _analyze_structure(self, data, max_depth=3, current_depth=0) -> Dict:
        if current_depth > max_depth:
            return {"truncated": True}

        if isinstance(data, list):
            return {
                "type": "array",
                "length": len(data),
                "item_types": list(set(type(item).__name__ for item in data)),
                "sample": self._analyze_structure(data[0], max_depth, current_depth + 1) if data else None
            }
        elif isinstance(data, dict):
            return {
                "type": "object",
                "keys": list(data.keys()),
                "key_count": len(data),
                "properties": {
                    k: self._analyze_structure(v, max_depth, current_depth + 1)
                    for k, v in list(data.items())[:10]  # İlk 10 key
                }
            }
        else:
            return {
                "type": type(data).__name__,
                "value": str(data)[:100] if isinstance(data, str) else data
            }

    def _infer_schema(self, data) -> Dict:
        """JSON Schema çıkar"""
        if isinstance(data, list):
            if not data:
                return {"type": "array", "items": {}}
            return {
                "type": "array",
                "items": self._infer_schema(data[0])
            }
        elif isinstance(data, dict):
            properties = {}
            required = []

            for key, value in data.items():
                properties[key] = self._infer_schema(value)
                required.append(key)

            return {
                "type": "object",
                "properties": properties,
                "required": required
            }
        elif isinstance(data, bool):
            return {"type": "boolean"}
        elif isinstance(data, int):
            return {"type": "integer"}
        elif isinstance(data, float):
            return {"type": "number"}
        elif isinstance(data, str):
            # Format detection
            if "@" in data and "." in data:
                return {"type": "string", "format": "email"}
            elif data.startswith("http"):
                return {"type": "string", "format": "uri"}
            else:
                return {"type": "string"}
        elif data is None:
            return {"type": "null"}
        else:
            return {"type": "string"}


def main():
    parser = argparse.ArgumentParser(
        description="JSON AI Tool - Qwen 2.5 7B ile offline JSON işlemleri",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  # Validate
  python json_ai.py validate data.json
  python json_ai.py validate '{"key": "value"}'

  # Fix
  python json_ai.py fix broken.json
  python json_ai.py fix '{"key": "value",}' --ai

  # Analyze
  python json_ai.py analyze data.json

  # Generate
  python json_ai.py generate --count 100 --type user
  python json_ai.py generate --count 1000 --type product --output data.json
  python json_ai.py generate --template template.json --count 500

  # AI kullanmadan (daha hızlı)
  python json_ai.py validate data.json --no-ai
        """
    )

    parser.add_argument('command', choices=['validate', 'fix', 'analyze', 'generate'],
                       help='İşlem türü')
    parser.add_argument('input', nargs='?', help='JSON string veya dosya yolu')
    parser.add_argument('--model', help='Model path (default: auto-detect)')
    parser.add_argument('--no-ai', action='store_true', help='AI kullanma (daha hızlı)')
    parser.add_argument('--ai', action='store_true', help='AI kullan (fix için)')
    parser.add_argument('--count', type=int, default=10, help='Üretilecek kayıt sayısı')
    parser.add_argument('--type', default='generic', help='Veri tipi: user, product, generic')
    parser.add_argument('--template', help='Template JSON dosyası')
    parser.add_argument('--output', '-o', help='Output dosyası')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON')

    args = parser.parse_args()

    # Tool oluştur
    use_ai = not args.no_ai or args.ai
    tool = JSONAITool(model_path=args.model, use_ai=use_ai)

    # Input oku
    input_data = None
    if args.input:
        if Path(args.input).exists():
            with open(args.input, 'r', encoding='utf-8') as f:
                input_data = f.read()
        else:
            input_data = args.input

    # İşlem yap
    result = None

    if args.command == 'validate':
        if not input_data:
            print("❌ Input gerekli")
            sys.exit(1)
        result = tool.validate(input_data)

    elif args.command == 'fix':
        if not input_data:
            print("❌ Input gerekli")
            sys.exit(1)
        result = tool.fix(input_data)

    elif args.command == 'analyze':
        if not input_data:
            print("❌ Input gerekli")
            sys.exit(1)
        result = tool.analyze(input_data)

    elif args.command == 'generate':
        template = None
        if args.template:
            with open(args.template, 'r', encoding='utf-8') as f:
                template = json.load(f)

        result = tool.generate(
            count=args.count,
            template=template,
            data_type=args.type
        )

    # Output
    indent = 2 if args.pretty else None
    output_json = json.dumps(result, indent=indent, ensure_ascii=False)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"✓ Sonuç kaydedildi: {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
