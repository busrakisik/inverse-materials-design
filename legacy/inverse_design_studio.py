# Historical Qwen-based inverse materials design prototype.
# Kept separate from the BHS Streamlit research demonstration.
# Generated CIFs require independent scientific validation.

import streamlit as st
import streamlit.components.v1 as components
import py3Dmol
from pymatgen.core import Structure
import numpy as np
from crystal_gen.generator import CrystalGenerator

st.set_page_config(page_title="Inverse Materials Design", layout="wide")
st.title("🧪 Inverse Materials Design Studio")
st.warning("LEGACY RESEARCH PROTOTYPE: A parsed CIF and basic distance check are not proof of thermodynamic stability, synthesizability, or experimental validation.")
st.caption("Qwen2.5-7B-Instruct & Pymatgen Physical Validation Engine")

def validate_cif_with_pymatgen(cif_str: str):
    """CIF içeriğini Pymatgen ile analiz eder ve fiziksel metrikleri döndürür."""
    try:
        struct = Structure.from_str(cif_str, fmt="cif")
        
        # Lattice parametreleri
        a, b, c = struct.lattice.a, struct.lattice.b, struct.lattice.c
        alpha, beta, gamma = struct.lattice.alpha, struct.lattice.beta, struct.lattice.gamma
        volume = struct.lattice.volume
        density = struct.density
        
        # Atomlar arası en kısa mesafeleri kontrol et (Atomic Clashing Check)
        min_dist = float('inf')
        num_sites = len(struct)
        for i in range(num_sites):
            for j in range(i + 1, num_sites):
                dist = struct.get_distance(i, j)
                if dist < min_dist:
                    min_dist = dist
        
        # Fiziksel geçerlilik kriteri (Örn: 0.8 Å altında atom çakışması uyarısı)
        is_valid = min_dist >= 0.8 if min_dist != float('inf') else True
        
        metrics = {
            "valid": True,
            "is_physically_sound": is_valid,
            "num_atoms": num_sites,
            "a": round(a, 3), "b": round(b, 3), "c": round(c, 3),
            "alpha": round(alpha, 2), "beta": round(beta, 2), "gamma": round(gamma, 2),
            "volume": round(volume, 2),
            "density": round(density, 2),
            "min_distance": round(min_dist, 3) if min_dist != float('inf') else "N/A"
        }
        return struct, metrics
    except Exception as e:
        return None, {"valid": False, "error": str(e)}

# Sol ve Sağ Kolonlar
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📌 Yapı Parametreleri")
    
    # Hazır Şablonlar (Presets)
    preset = st.selectbox("🎯 Hazır Şablon Seç (Opsiyonel)", ["Özel (Custom)", "NaCl (Rock-salt)", "SrTiO3 (Perovskite)", "C (Diamond)", "TiO2 (Rutile)"])
    
    default_formula = "NaCl"
    default_sg = "Fm-3m"
    if preset == "SrTiO3 (Perovskite)":
        default_formula, default_sg = "SrTiO3", "Pm-3m"
    elif preset == "C (Diamond)":
        default_formula, default_sg = "C", "Fd-3m"
    elif preset == "TiO2 (Rutile)":
        default_formula, default_sg = "TiO2", "P42/mnm"
        
    formula = st.text_input("Kimyasal Formül", value=default_formula)
    spacegroup = st.text_input("Uzay Grubu (Opsiyonel)", value=default_sg)
    generate_btn = st.button("🚀 Kristal Yapısı Üret & Doğrula", type="primary")

if generate_btn:
    with st.spinner("Qwen2.5-7B modeli CIF üretiyor ve Pymatgen analiz ediyor..."):
        try:
            generator = CrystalGenerator.get_instance()
            cif_data = generator.generate_cif(formula, spacegroup)
            st.session_state['cif_data'] = cif_data
            
            # Pymatgen Doğrulaması
            _, metrics = validate_cif_with_pymatgen(cif_data)
            st.session_state['metrics'] = metrics
            
            st.success("CIF üretim denemesi tamamlandı. Bilimsel doğrulama ayrıca gereklidir.")
        except Exception as e:
            st.error(f"Hata oluştu: {str(e)}")

with col2:
    st.subheader("🧊 3D Görselleştirme & Fiziksel Analiz")
    if 'cif_data' in st.session_state:
        cif_str = st.session_state['cif_data']
        metrics = st.session_state.get('metrics', {})
        
        # 1. Kalite ve Doğrulama Rozeti
        if metrics.get("valid"):
            if metrics.get("is_physically_sound"):
                st.info("🟡 **BASIC GEOMETRY CHECK PASSED:** Seçilen eşik altında atom mesafesi tespit edilmedi. Bu sonuç yapısal kararlılığı kanıtlamaz.")
            else:
                st.warning(f"⚠️ **POTENTIAL OVERLAP:** Atomlar arası mesafe çok yakın ({metrics.get('min_distance')} Å).")
            
            # 2. Metrik Kartları
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Formül Atom Sayısı", metrics.get("num_atoms"))
            m_col2.metric("Hacım (Å³)", metrics.get("volume"))
            m_col3.metric("Yoğunluk (g/cm³)", metrics.get("density"))
            m_col4.metric("Min Atom Mesafesi", f"{metrics.get('min_distance')} Å")
            
            with st.expander("📐 Lattice (Örgü) Parametreleri"):
                st.write(f"**a:** {metrics['a']} Å | **b:** {metrics['b']} Å | **c:** {metrics['c']} Å")
                st.write(f"**α:** {metrics['alpha']}° | **β:** {metrics['beta']}° | **γ:** {metrics['gamma']}°")
        else:
            st.error(f"❌ **CIF PARSE ERROR:** Pymatgen CIF dosyasını işleyemedi. Hata: {metrics.get('error')}")

        # 3D Görselleştirme
        if metrics.get("valid"):
            xyz_view = py3Dmol.view(width=500, height=380)
            xyz_view.addModel(cif_str, "cif")
            xyz_view.setStyle({'sphere': {'scale': 0.25}, 'stick': {'radius': 0.15}})
            xyz_view.addUnitCell()
            xyz_view.zoomTo()
            components.html(xyz_view._make_html(), height=390)
        
        st.download_button("💾 CIF Dosyasını İndir", cif_str, file_name=f"{formula}_generated.cif", mime="text/plain")
        with st.expander("📄 Ham CIF İçeriğini Göster"):
            st.code(cif_str, language="text")
