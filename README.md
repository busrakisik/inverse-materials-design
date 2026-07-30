# 🧪 Inverse Materials Design Studio

An enterprise-grade, LLM-powered Inverse Materials Design platform deployed on Google Colab with 4-bit NF4 quantization and real-time Pymatgen structural validation.

---

## 🌟 Overview

**Inverse Materials Design Studio** generates 3D crystallographic structures (CIF format) directly from chemical formulas and optional space groups using fine-tuned open-source LLMs. The platform bridges Generative AI with Material Science by providing real-time physical validation, lattice parameter extraction, and interactive 3D visualizations.

---

## 🚀 Key Features

* **LLM Core:** Powered by `Qwen2.5-7B-Instruct` quantized using `bitsandbytes` 4-bit NF4 for fast VRAM-efficient generation on Tesla T4 GPUs.
* **Physical Validation Engine:** Integrated with `Pymatgen` to verify atomic distances, detect physical overlapping (< 0.8 Å), and parse crystallographic properties.
* **Real-time Metrics:** Automatic calculation of unit cell volume (V), density (ρ), lattice parameters (a, b, c, α, β, γ), and formula atom counts.
* **Interactive 3D View:** WebGL-based dynamic unit cell rendering using `py3Dmol`.
* **Zero-Setup Tunneling:** Publicly accessible UI exposed securely via Cloudflare Tunnels.

---

## 🛠️ Tech Stack

* **Language Model:** HuggingFace `transformers`, `bitsandbytes`, `accelerate`
* **Validation & Domain Logic:** `pymatgen`, `numpy`
* **UI & Rendering:** `streamlit`, `py3Dmol`
* **Deployment & Networking:** Google Colab (Tesla T4), Cloudflare Tunnel (`cloudflared`)

---

## 📁 Repository Structure

```text
├── crystal_gen/
│   ├── __init__.py
│   └── generator.py     # Qwen2.5-7B Singleton model loader & CIF generator
├── app.py               # Streamlit UI & Pymatgen validation logic
├── requirements.txt     # System dependencies
└── README.md            # Project documentation

## 🔮 Limitations & Future Roadmap

This project is currently a **Proof of Concept (PoC)** focused on software engineering and pipeline integration. To evolve into a full-scale research framework, the following steps are planned:

- [ ] **Surrogate Relaxation & Energy Prediction:** Integrate MLIPs (CHGNet / M3GNet) for structural relaxation and formation energy evaluation instead of pure rule-based validation.
- [ ] **Property-Conditioned Generation:** Allow users to input target properties (e.g., `Band Gap = 2.0 eV`, `Density < 4 g/cm³`) alongside chemical formulas.
- [ ] **Closed-Loop Feedback:** Implement active learning / reinforcement learning loops between validation metrics and the generative model.
- [ ] **Benchmarking:** Comprehensive evaluation of LLM success rates, structural novelty, and diversity against domain baselines (e.g., MatterGen, MatGen).
