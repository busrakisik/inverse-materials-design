import py3Dmol
from stmol import showmol
from pymatgen.core import Structure
from pymatgen.io.cif import CifWriter

class CrystalStructureViewer:
    @staticmethod
    def render_structure_3d(structure: Structure, style_mode: str = "Ball & Stick", height: int = 400, width: int = 700):
        cif_writer = CifWriter(structure)
        cif_str = str(cif_writer)

        view = py3Dmol.view(width=width, height=height)
        view.addModel(cif_str, "cif")
        
        if style_mode == "Space-Filling (VDW)":
            view.setStyle({'sphere': {'scale': 0.85}})
        elif style_mode == "Wireframe":
            view.setStyle({'line': {'linewidth': 2.0}})
        elif style_mode == "Polyhedra":
            # Polyhedral representation
            view.setStyle({'polyhedron': {'color': 'byelement'}, 'sphere': {'scale': 0.2}})
        else:  # Ball & Stick
            view.setStyle({'sphere': {'scale': 0.25}, 'stick': {'radius': 0.15}})
        
        view.addUnitCell()
        view.zoomTo()
        view.spin(True)
        
        showmol(view, height=height, width=width)