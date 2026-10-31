# app.py

import time
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pymatgen.core import Structure, Lattice

# Pipeline & Agent Imports
from src.imd_pipeline.validation.real_calculators import RealPhysicsEngine
from src.imd_pipeline.visualization.crystal_viewer import CrystalStructureViewer
from src.imd_pipeline.agents.consensus_engine import MultiModelConsensusEngine
from src.imd_pipeline.agents.synthesis_agent import ExperimentalSynthesisAgent
from src.imd_pipeline.agents.search_planner import AdaptiveBudgetPlanner
from src.imd_pipeline.agents.literature_agent import RealLiteraturePatentAgent
from src.imd_pipeline.agents.hypothesis_engine import HypothesisAndExplainabilityEngine
from src.imd_pipeline.agents.bayesian_reasoner import BayesianHypothesisSearchEngine

st.set_page_config(
    page_title="Autonomous Scientific Discovery Engine",
    page_icon="🧠",
    layout="wide"
)

st.warning("RESEARCH DEMONSTRATION: hypothesis likelihoods and some displayed properties are illustrative or provisional, not independently validated experimental results.")

st.markdown("""
<style>
    .main-title { font-size: 2.1rem; font-weight: 800; color: #F0F2F6; }
    .sub-title-badge { font-size: 0.95rem; font-weight: 600; color: #00CC96; margin-bottom: 0.4rem; }
    .pipeline-tagline { font-size: 0.88rem; color: #A0AABF; font-style: italic; margin-bottom: 1.2rem; }
    .stMetric { background-color: #1a1d24; padding: 10px; border-radius: 6px; border: 1px solid #2e3440; }
    .mcts-card { background-color: #11151c; border: 1px solid #2b3245; border-radius: 8px; padding: 12px; margin-bottom: 10px; }
    .bayes-step-box { background-color: #0d1117; border-left: 4px solid #00cc96; padding: 10px; margin-bottom: 8px; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_demo_structure():
    lattice = Lattice.from_parameters(a=10.33, b=6.01, c=4.69, alpha=90, beta=90, gamma=90)
    species = ["Li", "Fe", "P", "O", "O"]
    coords = [[0.0, 0.0, 0.0], [0.28, 0.25, 0.97], [0.09, 0.25, 0.42], [0.09, 0.25, 0.74], [0.16, 0.05, 0.28]]
    return Structure(lattice, species, coords)

with st.sidebar:
    st.header("🎯 Target Discovery Goals")
    selected_targets = st.multiselect(
        "Target Objectives",
        ["Fast Charging (>2C)", "High Volumetric Energy (>250 Wh/kg)", "No Cobalt / Low Cost", "Thermal Stability (>700°C)"],
        default=["Fast Charging (>2C)", "No Cobalt / Low Cost", "Thermal Stability (>700°C)"]
    )
    cost_target = st.slider("Target Raw Material Cost ($/kg)", 5, 50, 18)
    st.divider()
    st.subheader("⚙️ Core Search Algorithm")
    st.markdown("**Engine:** Bayesian Hypothesis Search (BHS)")
    st.markdown("**Tree Navigation:** Adaptive MCTS (PUCT)")
    st.markdown("**Evidence Logic:** Sequential Bayes Update")
    st.divider()
    run_btn = st.button("🧪 Run BHS Demonstration", type="primary", use_container_width=True)

st.markdown("<div class='main-title'>Autonomous Scientific Discovery Engine</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title-badge'>Bayesian Hypothesis Search (BHS) & Physics-Grounded Evidence Accumulation</div>", unsafe_allow_html=True)
st.markdown("<div class='pipeline-tagline'>\"Existing methods primarily optimize over atomic or latent structural representations, whereas our method explicitly reasons over competing scientific hypotheses before structural generation via sequential Bayesian evidence accumulation.\"</div>", unsafe_allow_html=True)

demo_struct = get_demo_structure()

if run_btn or 'engine_executed' not in st.session_state:
    bhs = BayesianHypothesisSearchEngine()
    
    with st.status("🧠 Executing Bayesian Hypothesis Search (BHS)...", expanded=True) as status:
        # Step 1: Research Question & Prior Initialization
        st.write("❓ **Step 1:** Formulating Explicit Research Question & Prior Distributions P(H)...")
        time.sleep(0.2)
        
        # Step 2: Wyckoff Likelihood
        st.write("📐 **Step 2:** Physics Evidence E_1 (Wyckoff Clash Likelihood)...")
        step1_res = bhs.accumulate_sequential_evidence("Wyckoff Steric Clash Check", {"H1_NASICON": 0.92, "H2_Spinel": 0.65, "H3_Olivine": 0.88})
        time.sleep(0.2)
        
        # Step 3: MLFF Likelihood
        st.write("🔬 **Step 3:** Physics Evidence E_2 (Multi-Model MLFF Consensus Likelihood)...")
        relaxed_struct, real_calc_res = RealPhysicsEngine.run_chgnet_relaxation(demo_struct)
        consensus_res = MultiModelConsensusEngine.evaluate_ensemble(real_calc_res)
        step2_res = bhs.accumulate_sequential_evidence("MLFF Ensemble Relaxation", {"H1_NASICON": 0.81, "H2_Spinel": 0.40, "H3_Olivine": 0.55})
        time.sleep(0.2)
        
        # Step 4: Patent & Lab Evidence
        st.write("📚 **Step 4:** Literature Novelty & Experimental Failure Evidence E_3...")
        lit_report = RealLiteraturePatentAgent.evaluate_novelty("LiFePO4", "fingerprint_xyz")
        step3_res = bhs.accumulate_sequential_evidence("Prior Art Clearance & Lab Memory", {"H1_NASICON": 0.78, "H2_Spinel": 0.30, "H3_Olivine": 0.50})
        time.sleep(0.2)
        
        status.update(label="🎉 Bayesian Hypothesis Search Completed!", state="complete", expanded=False)

    st.session_state['relaxed_struct'] = relaxed_struct
    st.session_state['consensus_res'] = consensus_res
    st.session_state['lit_report'] = lit_report
    st.session_state['bhs_history'] = bhs.history
    st.session_state['final_bhs_res'] = step3_res
    st.session_state['bhs_engine'] = bhs
    st.session_state['engine_executed'] = True

relaxed_struct = st.session_state['relaxed_struct']
consensus_res = st.session_state['consensus_res']
lit_report = st.session_state['lit_report']
bhs_history = st.session_state['bhs_history']
final_bhs_res = st.session_state['final_bhs_res']
bhs_engine = st.session_state['bhs_engine']

winning_h = final_bhs_res['winning_hypothesis']
winning_p = final_bhs_res['updated_posteriors'][winning_h]

st.info(f"🧪 **DEMO — TOP-RANKED HYPOTHESIS (NOT VALIDATED):** {winning_h} | ⚡ **Final Posterior P(H|E):** {winning_p*100:.2f}% | 💻 **Allocated Budget:** {final_bhs_res['allocated_budget']}")

st.caption("Caution: metrics below may mix demonstration inputs, proxy outputs, and calculations. Verify provenance before scientific use.")

# Top Metrics
mcol1, mcol2, mcol3, mcol4 = st.columns(4)
mcol1.metric("Prototype energy output", f"{consensus_res['mean_formation_energy']} eV/atom", delta=f"±{consensus_res['model_uncertainty_std']} eV", delta_color="off")
mcol2.metric("Posterior Confidence P(H|E)", f"{winning_p*100:.1f}%", delta="Updated via Bayes Rule")
mcol3.metric("Prototype novelty score", f"{lit_report['novelty_score']}", delta="Not verified patent clearance")
mcol4.metric("Illustrative bandgap", "1.82 eV", delta="Not calculated here")

st.divider()

# -----------------------------------------------------------------------------
# Tabs & Academic Core
# -----------------------------------------------------------------------------
tab_rq, tab_mcts, tab_bayes, tab_math, tab_pareto, tab_3d = st.tabs([
    "❓ Research Question & Hypotheses",
    "🌳 Adaptive MCTS Node Stats (UCT)",
    "🔄 Sequential Bayes Evidence Update",
    "📐 Formal Mathematical Model",
    "📊 Illustrative Candidate Comparison",
    "🧊 3D Crystal Structure"
])

# --- TAB 1: Research Question & Hypotheses ---
with tab_rq:
    st.subheader("❓ Explicit Research Question Formulation")
    st.info("🎯 **Formulated Scientific Research Question:**\n\n*\"Can a cobalt-free, 3D open-framework NASICON analogue satisfy fast-charging kinetics (>2C) while maintaining raw material cost below $20/kg and thermal stability above 700°C?\"*")
    
    st.markdown("##### 🔬 Competing Hypothesis Manifolds (Priors P(H))")
    hcol1, hcol2, hcol3 = st.columns(3)
    with hcol1:
        st.markdown(f"**H1: 3D NASICON Framework**\n* **Prior P(H):** 0.41\n* **Final Posterior P(H|E):** `{final_bhs_res['updated_posteriors']['H1_NASICON']*100:.1f}%`\n* **Status:** **CHOSEN ✅**")
    with hcol2:
        st.markdown(f"**H2: Disordered Spinel**\n* **Prior P(H):** 0.33\n* **Final Posterior P(H|E):** `{final_bhs_res['updated_posteriors']['H2_Spinel']*100:.1f}%`\n* **Status:** **PRUNED ❌**")
    with hcol3:
        st.markdown(f"**H3: 1D Channel Olivine**\n* **Prior P(H):** 0.26\n* **Final Posterior P(H|E):** `{final_bhs_res['updated_posteriors']['H3_Olivine']*100:.1f}%`\n* **Status:** **QUEUED ⏳**")

# --- TAB 2: MCTS Node Statistics (UCT) ---
with tab_mcts:
    st.subheader("🌳 Adaptive Monte Carlo Tree Search (MCTS) Nodes & UCT Scores")
    st.caption("Node selection governed by UCT = Q + c_puct * P * sqrt(N_parent) / (1 + N_node)")
    
    mcols = st.columns(3)
    for i, (node_id, data) in enumerate(bhs_engine.mcts_nodes.items()):
        uct = bhs_engine.compute_uct(node_id)
        with mcols[i]:
            st.markdown(f"""
            <div class='mcts-card'>
                <h4>Node: {node_id}</h4>
                <p><b>Prior P(H):</b> {data['P']:.4f}</p>
                <p><b>Physical Reward (Q):</b> {data['Q']:.2f}</p>
                <p><b>Visit Count (N):</b> {data['N']}</p>
                <h3 style='color: #00cc96; margin-top:5px;'>UCT Score: {uct}</h3>
            </div>
            """, unsafe_allow_html=True)

# --- TAB 3: Sequential Bayes Evidence Update ---
with tab_bayes:
    st.subheader("🔄 Sequential Likelihood Evidence Accumulation Timeline")
    st.caption("Showing step-by-step P(H_i | E_1:k) belief progression as physical evidence arrives.")
    
    for record in bhs_history:
        st.markdown(f"""
        <div class='bayes-step-box'>
            <b>[EVIDENCE EVENT]: {record['step_name']}</b><br>
            • Likelihoods L(E|H): NASICON={record['likelihoods'].get('H1_NASICON')}, Spinel={record['likelihoods'].get('H2_Spinel')}, Olivine={record['likelihoods'].get('H3_Olivine')}<br>
            • Updated Posteriors P(H|E): <span style='color:#00cc96;'>NASICON={record['posteriors']['H1_NASICON']*100:.1f}%</span> | Spinel={record['posteriors']['H2_Spinel']*100:.1f}% | Olivine={record['posteriors']['H3_Olivine']*100:.1f}%
        </div>
        """, unsafe_allow_html=True)

    st.markdown("##### 📈 Posterior Belief Evrim Graﬁği")
    steps = ["Prior P(H)", "E1: Wyckoff", "E2: MLFF", "E3: Patent/Lab"]
    nasicon_p = [0.41, bhs_history[0]['posteriors']['H1_NASICON'], bhs_history[1]['posteriors']['H1_NASICON'], bhs_history[2]['posteriors']['H1_NASICON']]
    spinel_p  = [0.33, bhs_history[0]['posteriors']['H2_Spinel'],  bhs_history[1]['posteriors']['H2_Spinel'],  bhs_history[2]['posteriors']['H2_Spinel']]
    olivine_p = [0.26, bhs_history[0]['posteriors']['H3_Olivine'], bhs_history[1]['posteriors']['H3_Olivine'], bhs_history[2]['posteriors']['H3_Olivine']]
    
    fig_ev = go.Figure()
    fig_ev.add_trace(go.Scatter(x=steps, y=nasicon_p, name="H1: NASICON", line=dict(color='#00cc96', width=3)))
    fig_ev.add_trace(go.Scatter(x=steps, y=spinel_p,  name="H2: Spinel (Pruned)", line=dict(color='#ff4b4b', dash='dash')))
    fig_ev.add_trace(go.Scatter(x=steps, y=olivine_p, name="H3: Olivine", line=dict(color='#e2a03f')))
    fig_ev.update_layout(template="plotly_dark", height=300, yaxis_title="Posterior Probability P(H_i | E_{1:k})")
    st.plotly_chart(fig_ev, use_container_width=True)

# --- TAB 4: Formal Mathematical Model ---
with tab_math:
    st.subheader("📐 Formal Mathematical Definition of the Framework")
    
    st.markdown("#### 1. Bayesian Posterior Formula")
    st.latex(r"""
    P(H_i \mid E_{1:k}) = \frac{P(E_k \mid H_i) \cdot P(H_i \mid E_{1:k-1})}{\sum_{j} P(E_k \mid H_j) \cdot P(H_j \mid E_{1:k-1})}
    """)
    
    st.markdown("#### 2. Upper Confidence Bound for Trees (PUCT)")
    st.latex(r"""
    \text{UCT}(n) = Q(n) + c_{\text{puct}} \cdot P(H_n) \cdot \frac{\sqrt{N_{\text{parent}}}}{1 + N_n}
    """)
    
    st.markdown("#### 3. Dynamic GPU Budget Allocation Function")
    st.latex(r"""
    \text{ComputeBudget}(H_i) = \text{BaseCompute} \times \left(1 + \gamma \cdot P(H_i \mid E)\right) \times \exp\left(\sigma_{\text{MLFF}}\right)
    """)

# --- TAB 5: Multi-Objective Pareto Front ---
with tab_pareto:
    st.subheader("📊 Illustrative Candidate Comparison")
    st.caption("These plotted costs, energies and stabilities are manually specified demonstration values, not experimentally measured or verified Pareto-optimal results.")
    costs = [12, 18, 25, 42, 15, 38, 22]
    energies = [210, 265, 290, 310, 220, 295, 275]
    stabilities = [0.005, 0.008, 0.025, 0.045, 0.012, 0.038, 0.015]
    names = ["Candidate C (Olivine)", "Candidate A (NASICON - Chosen)", "Candidate B (Spinel)", "High-Ni NCM", "LFP-Base", "Cobalt-Rich", "Li-Rich NASICON"]
    
    fig_pareto = px.scatter(
        x=costs, y=energies, color=stabilities, text=names,
        labels={"x": "Raw Material Cost ($/kg)", "y": "Volumetric Energy (Wh/kg)", "color": "E_above_hull (eV)"},
        color_continuous_scale="Viridis_r"
    )
    fig_pareto.update_traces(marker=dict(size=16), textposition='top center')
    fig_pareto.update_layout(template="plotly_dark", height=380)
    st.plotly_chart(fig_pareto, use_container_width=True)

# --- TAB 6: 3D Crystal Structure ---
with tab_3d:
    st.subheader("🧊 Demonstration Crystal Structure")
    st.caption("Visualization of a prototype structure; the plot alone does not demonstrate physical or experimental validity.")
    CrystalStructureViewer.render_structure_3d(relaxed_struct, style_mode="Ball & Stick", height=400, width=700)
