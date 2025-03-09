"""
src/trapMemFn.py

Trapezoidal Membership Function
"""

from typing import List
from utils.line import Point, Line

class TrapMemFn:
    def __init__(self, label: str, x_coordinates: List[int]):
        assert len(x_coordinates) == 4
        
        # Ensure trapezoidal property in clockwise order
        for i in range(len(x_coordinates)-1):
            assert x_coordinates[i] <= x_coordinates[i+1]

        self.label = label
        self.x_coordinates = x_coordinates
        self.points_length = len(self.x_coordinates)
        self.points: List[Point] = []
        self.lines: List[Line] = []
        self._createBoundary()
    
    def _createBoundary(self):
        pt1 = Point(self.x_coordinates[0], 0)
        pt2 = Point(self.x_coordinates[1], 1)
        pt3 = Point(self.x_coordinates[2], 1)
        pt4 = Point(self.x_coordinates[3], 0)

        self.points.append(pt1)
        self.points.append(pt2)
        self.points.append(pt3)
        self.points.append(pt4)

        line1 = Line(pt1,pt2)
        line2 = Line(pt2,pt3)
        line3 = Line(pt3,pt4)
        
        self.lines.append(line1)
        self.lines.append(line2)
        self.lines.append(line3)
    
    def calculateMembershipDegree(self, x: float) -> float:
        if (x<self.x_coordinates[0]) or (x>self.x_coordinates[self.points_length-1]):
            return 0

        target_line: Line

        for i in range(self.points_length-1):
            if (x>=self.x_coordinates[i]) and (x<=self.x_coordinates[i+1]):
                target_line = self.lines[i]
                
        return target_line.calculateY(x)
    
    def generatePortionPoints(self, fraction: float) -> List[Point]:
        if fraction == 1.0:
            return self.points
        
        portionPoints: List[Point] = []
        portionPoints.append(self.points[0])

        for i in range(self.points_length-1):
            x = self.lines[i].calculateX(fraction)
            if x is not None:
                portionPoints.append(Point(x, fraction))

        portionPoints.append(self.points[self.points_length-1])
        return portionPoints
    

