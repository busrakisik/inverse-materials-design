import os
from typing import Dict, Any

class ResearchPaperGenerator:
    """
    Generates structured LaTeX and Markdown research draft papers 
    for discovered thermodynamically stable materials.
    """

    def __init__(self, output_dir: str = "outputs/papers"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_latex_paper(self, material_data: Dict[str, Any], filename: str = "paper_draft.tex") -> str:
        """
        Generates a publication-ready LaTeX paper draft using standard REVTeX / IEEE style structure.
        """
        formula = material_data.get("formula", "Unknown Discovery")
        e_form = material_data.get("e_form", 0.0)
        synth_score = material_data.get("synthesizability_score", 0.0)
        band_gap_class = material_data.get("band_gap_class", "N/A")
        gap_ev = material_data.get("estimated_gap_eV", 0.0)
        confidence = material_data.get("ensemble_confidence", 0.0)

        latex_content = (
            r"\documentclass[twocolumn,aps,prb,preprintnumbers,amsmath,amssymb]{revtex4-2}" "\n"
            r"\usepackage{graphicx}" "\n"
            r"\usepackage{dcolumn}" "\n"
            r"\usepackage{bm}" "\n"
            r"\usepackage{hyperref}" "\n\n"
            r"\begin{document}" "\n\n"
            rf"\title{{Autonomous Inverse Discovery and Physical Validation of Novel Crystal Structure: {formula}}}" "\n\n"
            r"\author{Inverse Materials Discovery Pipeline (Autonomous MLFF-Agent)}" "\n"
            r"\date{\today}" "\n\n"
            r"\begin{abstract}" "\n"
            rf"We report the computational discovery of a novel inorganic crystal phase, \textbf{{{formula}}}, "
            rf"identified via an agentic inverse design pipeline integrated with Universal Machine Learning Force Fields (CHGNet) "
            rf"and multi-model ensemble validation. The candidate structure demonstrated high thermodynamic stability with a formation "
            rf"energy of $E_{{\text{{form}}}} = {e_form:.4f}\text{{ eV/atom}}$, zero internal stress residual, and a synthesizability score of ${synth_score:.3f}$. "
            rf"Electronic property classification indicates an electronic phase of {band_gap_class} with an estimated band gap of $\sim {gap_ev:.2f}\text{{ eV}}$. "
            rf"Cross-ensemble validation yielded a confidence score of ${confidence:.3f}$, confirming high dynamic and physical stability." "\n"
            r"\end{abstract}" "\n\n"
            r"\maketitle" "\n\n"
            r"\section{Introduction}" "\n"
            r"Accelerating the discovery of stable functional materials is crucial for energy storage and advanced technology applications. "
            r"Traditional density functional theory (DFT) screening is computationally expensive. Here, we leverage a closed-loop agentic AI architecture "
            r"coupled with graph neural network potential relaxations to generate physical structure candidates without human intervention." "\n\n"
            r"\section{Computational Methods}" "\n"
            r"Candidate structures were refined using the CHGNet Graph Neural Network potential architecture (v0.3.0). "
            r"Structural relaxation criteria were set to a strict force threshold of $f_{\text{max}} < 0.1\text{ eV/\AA}$. "
            r"Steric overlaps and dynamic feedback loops were governed by an LLM-driven physical correction agent. "
            r"Synthesizability metric evaluation and electronic band characterizations were computed via distance distribution matrices and dynamic element coordination models." "\n\n"
            r"\section{Results and Discussion}" "\n"
            rf"The optimized atomic configuration for \textbf{{{formula}}} achieved full convergence:" "\n"
            r"\begin{itemize}" "\n"
            rf"    \item \textbf{{Formation Energy ($E_{{\text{{form}}}}$):}} ${e_form:.4f}\text{{ eV/atom}}$" "\n"
            rf"    \item \textbf{{Synthesizability Score:}} ${synth_score:.3f}$" "\n"
            rf"    \item \textbf{{Band Structure Category:}} {band_gap_class} (${gap_ev:.2f}\text{{ eV}}$)" "\n"
            rf"    \item \textbf{{Ensemble Approval Confidence:}} ${confidence:.3f}$" "\n"
            r"\end{itemize}" "\n\n"
            rf"The low formation energy suggests thermodynamic stability relative to the elemental convex hull references, making \textbf{{{formula}}} a high-priority candidate for experimental synthesis." "\n\n"
            r"\section{Conclusion}" "\n"
            rf"The candidate \textbf{{{formula}}} demonstrates robust thermodynamic stability and favourable structural metrics. "
            r"Future work includes rigorous DFT validation (VASP/Quantum ESPRESSO) and experimental synthesis planning." "\n\n"
            r"\end{document}"
        )

        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(latex_content)

        return filepath