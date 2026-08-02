# tests/test_physics.py

from pymatgen.core import Structure, Lattice
from bhs.physics.relaxer import PhysicsRelaxationEngine
from bhs.provenance.tags import DataProvenanceType

def test_physics_engine():
    lattice = Lattice.cubic(4.0)
    struct = Structure(lattice, ["Fe"], [[0, 0, 0]])
    
    relaxed_struct, metrics = PhysicsRelaxationEngine.run_chgnet_relaxation(struct)
    
    assert metrics["formation_energy"].provenance == DataProvenanceType.MEASURED
    assert isinstance(metrics["formation_energy"].value, float)
    print("\n✅ Physics Engine Provenance Test Passed Successfully!")

if __name__ == "__main__":
    test_physics_engine()