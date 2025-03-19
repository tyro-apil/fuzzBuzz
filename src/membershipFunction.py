"""
src/membershipFunction.py

Factory for creating membership functions
"""
from typing import List
from src.trapMemFn import TrapMemFn
from src.triMemFn import TriMemFn

class MembershipFunctionFactory:
    @staticmethod
    def create_triangular(label: str, points: List[float]) -> TriMemFn:
        """Create a triangular membership function"""
        if len(points) != 3:
            raise ValueError("Triangular membership function requires 3 points")
        return TriMemFn(label, points)
    
    @staticmethod
    def create_trapezoidal(label: str, points: List[float]) -> TrapMemFn:
        """Create a trapezoidal membership function"""
        if len(points) != 4:
            raise ValueError("Trapezoidal membership function requires 4 points")
        return TrapMemFn(label, points)