#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from imd_pipeline.pipeline.orchestrator import MaterialsPipeline
from imd_pipeline.output.structure_analyzer import StructureAnalyzer


def main() -> int:
    parser = argparse.ArgumentParser(description="Inverse Materials Design — legacy illustrative prototype")
    parser.add_argument("--formula", required=True, help="Hedef kimyasal formül (örn. LiFePO4)")
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, default=Path("data/outputs"))
    args = parser.parse_args()

    pipeline = MaterialsPipeline(max_retries=args.max_retries, output_dir=args.output_dir)

    print(f"[START] formula={args.formula} max_retries={args.max_retries}")
    result = pipeline.run(args.formula)

    print(f"\n[{'PASS' if result.success else 'FAIL'}] {result.iterations_used}/{args.max_retries} iterasyonda sonuçlandı.")

    if result.success and result.cif_path:
        print(f"\n[OUTPUT] Geçerli CIF: {result.cif_path}")
        analyzer = StructureAnalyzer(result.cif_path)
        summary = analyzer.get_summary()
        print("\n--- 🔬 KRİSTAL YAPI VE BAĞ ANALİZİ ---")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    else:
        print("\n[OUTPUT] Geçerli yapı üretilemedi.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
