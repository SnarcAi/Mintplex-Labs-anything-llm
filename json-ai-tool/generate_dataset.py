#!/usr/bin/env python3
"""
JSON Training Dataset Generator
Fine-tuning için JSON task örnekleri üretir
"""

import json
import random
import argparse
from typing import List, Dict


class DatasetGenerator:
    def __init__(self):
        self.examples = []

    def generate_all(self, count_per_task: int = 500) -> List[Dict]:
        """Tüm task türleri için örnek üret"""

        tasks = [
            self.gen_validation,
            self.gen_validation_error,
            self.gen_fix,
            self.gen_schema_inference,
            self.gen_data_generation,
            self.gen_transformation,
            self.gen_jsonl,
            self.gen_analysis,
        ]

        for task in tasks:
            print(f"Generating {task.__name__}... ({count_per_task} examples)")
            for _ in range(count_per_task):
                example = task()
                self.examples.append(example)

        # Shuffle
        random.shuffle(self.examples)

        print(f"\n✓ Total: {len(self.examples)} examples")
        return self.examples

    def gen_validation(self) -> Dict:
        """JSON validation örnekleri"""
        data = self._random_json()
        return {
            "instruction": "Validate the following JSON and check for syntax errors.",
            "input": json.dumps(data, indent=2),
            "output": "The JSON is valid. No syntax errors found."
        }

    def gen_validation_error(self) -> Dict:
        """Hatalı JSON örnekleri"""
        broken = self._random_broken_json()
        return {
            "instruction": "Validate the following JSON and identify any syntax errors.",
            "input": broken,
            "output": "Syntax errors found: trailing comma, missing quotes, or invalid structure."
        }

    def gen_fix(self) -> Dict:
        """JSON düzeltme örnekleri"""
        data = self._random_json()
        broken = self._break_json(data)
        fixed = json.dumps(data, indent=2)

        return {
            "instruction": "Fix the syntax errors in the following JSON.",
            "input": broken,
            "output": f"Fixed JSON:\n{fixed}"
        }

    def gen_schema_inference(self) -> Dict:
        """Schema inference örnekleri"""
        data = self._random_json()
        schema = self._infer_simple_schema(data)

        return {
            "instruction": "Infer a JSON Schema from the following JSON data.",
            "input": json.dumps(data, indent=2),
            "output": f"Inferred JSON Schema:\n{json.dumps(schema, indent=2)}"
        }

    def gen_data_generation(self) -> Dict:
        """Veri üretme örnekleri"""
        types = ["user", "product", "transaction"]
        data_type = random.choice(types)
        count = random.choice([5, 10, 20])

        data = [self._generate_by_type(data_type, i) for i in range(count)]

        return {
            "instruction": f"Generate {count} {data_type} records in JSON format.",
            "input": f"Generate {count} {data_type} records",
            "output": json.dumps(data, indent=2)
        }

    def gen_transformation(self) -> Dict:
        """Veri dönüştürme örnekleri"""
        data = self._random_json()
        transformed = {k.upper(): v for k, v in data.items() if isinstance(data, dict)}

        return {
            "instruction": "Transform the JSON by converting all keys to uppercase.",
            "input": json.dumps(data, indent=2),
            "output": json.dumps(transformed, indent=2)
        }

    def gen_jsonl(self) -> Dict:
        """JSONL örnekleri"""
        records = [self._random_json() for _ in range(5)]
        jsonl = "\n".join(json.dumps(r) for r in records)

        return {
            "instruction": "Process the following JSONL data and provide a summary.",
            "input": jsonl,
            "output": f"Processed {len(records)} records successfully."
        }

    def gen_analysis(self) -> Dict:
        """JSON analiz örnekleri"""
        data = self._random_json()
        size = len(json.dumps(data))

        return {
            "instruction": "Analyze the structure and content of the following JSON.",
            "input": json.dumps(data, indent=2),
            "output": f"Analysis: {type(data).__name__} with size {size} bytes."
        }

    # ========== HELPER METHODS ==========

    def _random_json(self) -> Dict:
        """Random JSON üret"""
        types = ["user", "product", "config"]
        t = random.choice(types)
        return self._generate_by_type(t, random.randint(1, 100))

    def _generate_by_type(self, data_type: str, index: int) -> Dict:
        """Tipe göre veri üret"""
        if data_type == "user":
            return {
                "id": index,
                "name": f"User{index}",
                "email": f"user{index}@example.com",
                "age": random.randint(18, 80),
                "active": random.choice([True, False])
            }
        elif data_type == "product":
            return {
                "id": index,
                "sku": f"SKU-{random.randint(1000, 9999)}",
                "name": f"Product {index}",
                "price": round(random.uniform(10, 1000), 2),
                "in_stock": random.choice([True, False])
            }
        elif data_type == "transaction":
            return {
                "id": index,
                "user_id": random.randint(1, 1000),
                "amount": round(random.uniform(10, 500), 2),
                "status": random.choice(["pending", "completed", "failed"])
            }
        else:  # config
            return {
                "version": f"{random.randint(1, 5)}.{random.randint(0, 10)}.0",
                "enabled": random.choice([True, False]),
                "timeout": random.randint(1000, 10000)
            }

    def _break_json(self, data: Dict) -> str:
        """JSON'u boz"""
        json_str = json.dumps(data, indent=2)

        errors = [
            lambda s: s.replace("}", ",}"),  # trailing comma
            lambda s: s.replace('":', ':'),   # missing quote
            lambda s: s[:-1],                 # missing brace
        ]

        error = random.choice(errors)
        return error(json_str)

    def _random_broken_json(self) -> str:
        """Rastgele hatalı JSON"""
        broken = [
            '{"key": "value",}',
            '{key: "value"}',
            '{"key": "value"',
            '{"key": undefined}',
        ]
        return random.choice(broken)

    def _infer_simple_schema(self, data) -> Dict:
        """Basit schema çıkar"""
        if isinstance(data, dict):
            return {
                "type": "object",
                "properties": {
                    k: {"type": type(v).__name__}
                    for k, v in data.items()
                }
            }
        elif isinstance(data, list):
            return {
                "type": "array",
                "items": {"type": "object"}
            }
        else:
            return {"type": type(data).__name__}

    def save(self, output_path: str):
        """JSONL olarak kaydet"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in self.examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')

        print(f"✓ Dataset saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate JSON training dataset")
    parser.add_argument('--count', type=int, default=500, help='Examples per task type')
    parser.add_argument('--output', default='json_training_dataset.jsonl', help='Output file')

    args = parser.parse_args()

    print("🎲 Generating JSON training dataset...")
    print(f"   Count per task: {args.count}")
    print(f"   Output: {args.output}")
    print()

    generator = DatasetGenerator()
    generator.generate_all(count_per_task=args.count)
    generator.save(args.output)

    print(f"\n✓ Ready for fine-tuning!")
    print(f"   python finetune.py --dataset {args.output}")


if __name__ == "__main__":
    main()
