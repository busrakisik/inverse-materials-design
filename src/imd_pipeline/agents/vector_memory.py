from typing import List, Dict, Any

class ScientificFailureMemory:
    """
    Vector Memory module storing failed generation attempts to prevent 
    the LLM Agent from repeating physical or thermodynamic clashes.
    """
    def __init__(self):
        self.memory_db: List[Dict[str, Any]] = [
            {
                "id": "MEM-001",
                "composition": "LiFePO4",
                "failure_mode": "Steric clash at Wyckoff 4c site",
                "action_taken": "Expand cell volume by +1.5% and shift oxygen z-coordinate"
            },
            {
                "id": "MEM-002",
                "composition": "NaFePO4",
                "failure_mode": "Charge imbalance in octahedral layer",
                "action_taken": "Re-assign sodium site occupancies"
            }
        ]

    def query_similar_failures(self, formula: str) -> List[Dict[str, Any]]:
        return [m for m in self.memory_db if any(elem in formula for elem in ["Li", "Fe", "P"])]