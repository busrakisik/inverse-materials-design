"""Adversarial, entirely manufactured V12.16 input-geometry contracts."""
import csv
import gzip
import io
import json
import unittest

from scripts import bhs_v1216_single_input_lineage as v


def make_structure(xyz=None, lattice=None, elements=None):
    xyz = xyz or [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]]
    lattice = lattice or [[3, 0, 0], [0, 3, 0], [0, 0, 5]]
    elements = elements or ["Fe", "He"]
    return {"lattice": {"matrix": lattice},
            "sites": [
                {"species": [{"element": element, "occu": 1.0}], "abc": coord}
                for element, coord in zip(elements, xyz)
            ]}


def poscar(xyz=None, lattice=None, elements=None):
    xyz = xyz or [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]]
    lattice = lattice or [[3, 0, 0], [0, 3, 0], [0, 0, 5]]
    elements = elements or ["Fe", "He"]
    if elements != ["Fe", "He"]:
        raise ValueError("test generator only")
    lines = ["fixture", "1.0"] + [" ".join(map(str, row)) for row in lattice]
    lines += ["Fe He", "1 1", "Direct"]
    lines += [" ".join(map(str, coord)) for coord in xyz]
    return ("\n".join(lines) + "\n").encode()


def csv_source(record):
    sio=io.StringIO(newline="")
    w=csv.DictWriter(sio,fieldnames=[
        "GB","element","site","structure_unrel","E_seg","structure",
    ])
    w.writeheader()
    w.writerow(record)
    return gzip.compress(sio.getvalue().encode(),mtime=0)


class GeometryLineageTests(unittest.TestCase):
    def test_identical_structure_is_geometrically_equal(self):
        out=v.match_input_geometry(v.parse_poscar(poscar()),
                                   v.parse_structure_repr(json.dumps(make_structure())))
        self.assertTrue(out["sample_geometry_match"])
        self.assertEqual(out["species_counts"],{"Fe":1,"He":1})
        self.assertLessEqual(out["max_species_matched_min_image_displacement_angstrom"],1e-9)

    def test_matching_allows_order_permutations(self):
        d=make_structure(xyz=[[0.25,0.25,0.25],[0.0,0.0,0.0]],
                         elements=["He","Fe"])
        self.assertTrue(v.match_input_geometry(
            v.parse_poscar(poscar()),v.parse_structure_repr(json.dumps(d)))
            ["sample_geometry_match"])

    def test_matching_allows_periodic_wrapping(self):
        d=make_structure(xyz=[[1,0,0],[0.25,-0.75,0.25]])
        self.assertTrue(v.match_input_geometry(
            v.parse_poscar(poscar()),v.parse_structure_repr(json.dumps(d)))
            ["sample_geometry_match"])

    def test_displacement_strictly_fails(self):
        d=make_structure(xyz=[[0.01,0,0],[0.25,0.25,0.25]])
        x=v.match_input_geometry(v.parse_poscar(poscar()),
                                 v.parse_structure_repr(json.dumps(d)))
        self.assertFalse(x["sample_geometry_match"])
        self.assertGreater(x["max_species_matched_min_image_displacement_angstrom"],0.001)

    def test_lattice_error_strictly_fails(self):
        d=make_structure(lattice=[[3.01,0,0],[0,3,0],[0,0,5]])
        self.assertFalse(v.match_input_geometry(
            v.parse_poscar(poscar()),v.parse_structure_repr(json.dumps(d)))
            ["sample_geometry_match"])

    def test_wrong_species_fails(self):
        d=make_structure(elements=["Fe","H"])
        with self.assertRaisesRegex(v.GeometryContractError,"SPECIES_MISMATCH"):
            v.match_input_geometry(v.parse_poscar(poscar()),
                                   v.parse_structure_repr(json.dumps(d)))

    def test_missing_atom_fails(self):
        d=make_structure()
        d["sites"].pop()
        with self.assertRaisesRegex(v.GeometryContractError,"ATOM_COUNT_MISMATCH"):
            v.match_input_geometry(v.parse_poscar(poscar()),
                                   v.parse_structure_repr(json.dumps(d)))

    def test_fractional_occ_rejected(self):
        d=make_structure()
        d["sites"][0]["species"][0]["occu"]=0.5
        with self.assertRaisesRegex(v.GeometryContractError,"NONUNIT_STRUCTURE_OCCUPANCY"):
            v.parse_structure_repr(json.dumps(d))

    def test_nonfinite_coordinate_rejected(self):
        d=make_structure()
        d["sites"][1]["abc"]=["nan",0.25,0.25]
        with self.assertRaisesRegex(v.GeometryContractError,"NONFINITE_COORDINATES"):
            v.parse_structure_repr(json.dumps(d))

    def test_untrusted_executable_serialization_rejected(self):
        with self.assertRaises(v.GeometryContractError):
            v.parse_structure_repr("__import__('os').system('echo wrong')")
        with self.assertRaises(v.GeometryContractError):
            v.parse_structure_repr("[]"*3)

    def test_valid_python_literal_dict_accepted(self):
        parsed=v.parse_structure_repr(repr(make_structure()))
        self.assertEqual(len(parsed["species"]),2)

    def test_malformed_poscar_rejected(self):
        with self.assertRaises(v.GeometryContractError):
            v.parse_poscar(b"x")

    def test_sample_identity_and_outcome_not_read(self):
        record={"GB":v.SAMPLE_GB,"element":"He","site":"19",
                "structure_unrel":repr(make_structure()),"E_seg":"SECRET-TARGET",
                "structure":"SECRET-RELAXED-STRUCTURE"}
        raw=csv_source(record)
        value=v.extract_one_structure(raw,verify=False)
        self.assertNotIn("SECRET-TARGET",value)
        self.assertNotIn("SECRET-RELAXED-STRUCTURE",value)
        self.assertEqual(v.parse_structure_repr(value)["species"],["Fe","He"])

    def test_sample_identity_wrong_site_blocked(self):
        rec={"GB":v.SAMPLE_GB,"element":"He","site":"18",
             "structure_unrel":"X","E_seg":"hidden","structure":"secret"}
        with self.assertRaisesRegex(v.GeometryContractError,"MISSING_DUPLICATED_OR_BLANK"):
            v.extract_one_structure(csv_source(rec),verify=False)

    def test_sample_duplicated_identity_blocked(self):
        x={"GB":v.SAMPLE_GB,"element":"He","site":"19",
           "structure_unrel":"X","E_seg":"hidden","structure":"secret"}
        sio=io.StringIO(newline="")
        w=csv.DictWriter(sio,fieldnames=list(x))
        w.writeheader()
        w.writerows([x,x])
        with self.assertRaisesRegex(v.GeometryContractError,"MISSING_DUPLICATED_OR_BLANK"):
            v.extract_one_structure(gzip.compress(sio.getvalue().encode()),verify=False)

    def test_source_input_bytes_must_match_fixed_hash(self):
        from scripts.bhs_v1213_source_intake import SourceContractError
        with self.assertRaisesRegex(SourceContractError,"SOURCE_SIZE_MISMATCH"):
            v.audit_first_sample(b"forbidden", b"not original", b"not original")

    def test_tolerance_frozen(self):
        self.assertEqual(v.FIXED_TOLERANCE_ANGSTROM,0.001)
        self.assertFalse(v.GATES["scored_validation_allowed"])
        self.assertFalse(v.GATES["policy_time_access_certified"])
        self.assertFalse(v.GATES["precalculation_geometry_certified"])
        self.assertFalse(v.GATES["real_cost_verified"])


if __name__=="__main__":
    unittest.main()
