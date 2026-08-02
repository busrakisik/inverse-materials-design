import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.imd_pipeline.export.paper_generator import ResearchPaperGenerator

def main():
    print("📄 GENERATING ACADEMIC PAPER DRAFT")
    print("=================================")

    # Test verisi (Self-Correction çıktımızdan elde edilen kararlı aday)
    candidate_data = {
        "formula": "LiFePO4",
        "e_form": -2.3983,
        "synthesizability_score": 0.856,
        "band_gap_class": "Insulator",
        "estimated_gap_eV": 3.5,
        "ensemble_confidence": 0.856
    }

    generator = ResearchPaperGenerator()
    output_path = generator.generate_latex_paper(candidate_data, filename="LiFePO4_discovery_paper.tex")

    print(f"✅ Academic LaTeX paper draft generated successfully!")
    print(f"📂 Saved to: {output_path}")

if __name__ == "__main__":
    main()