"""
src/linguisticVariable.py

Represents a linguistic variable with multiple membership functions
"""
from typing import Dict

class LinguisticVariable:
    def __init__(self, name: str):
        self.name = name
        self.membership_functions: Dict[str, object] = {}
        self.range = [0, 0]  # [min, max]
    
    def add_membership_function(self, mem_fn):
        self.membership_functions[mem_fn.label] = mem_fn
        # Update range
        self.range[0] = min(self.range[0], mem_fn.x_coordinates[0])
        self.range[1] = max(self.range[1], mem_fn.x_coordinates[-1])
    
    def get_membership_degree(self, value: float, label: str) -> float:
        """Get membership degree for a specific label at given value"""
        if label not in self.membership_functions:
            raise ValueError(f"Label '{label}' not found in linguistic variable '{self.name}'")
        return self.membership_functions[label].calculateMembershipDegree(value)

