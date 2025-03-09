"""
utils/line.py

Line class
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Point:
    x: float
    y: float 

class Line:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end

        self.isHorizontal: bool = False
        if start.y == end.y:
            self.isHorizontal = True
        
        self.isVertical: bool = False
        if start.x == end.x:
            self.isVertical = True
        
        self._slope = self._calculateSlope()
        self._yIntercept = self._calculateYIntercept()
    
    def _calculateSlope(self) -> Optional[float]:
        if self.isVertical:
            return None
        return round((self.end.y - self.start.y)/(self.end.x - self.start.x), 2) 
       
    def _calculateYIntercept(self) -> Optional[float]:
        if self.isVertical:
            return None
        return round(self.start.y - self._slope*self.start.x, 2)

    def calculateX(self, y: float) -> Optional[float]:
        if self.isHorizontal:
            return None
        if self.isVertical:
            return self.start.x
        
        return round(((y-self.start.y)*(self.end.x-self.start.x)/(self.end.y-self.start.y)) + self.start.x, 2)
    
    def calculateY(self, x: float) -> Optional[float]:
        if self.isVertical:
            return None
        if self.isHorizontal:
            return self.start.y
        
        return round(((x-self.start.x)*(self.end.y-self.start.y)/(self.end.x-self.start.x)) + self.start.y, 2)
    

def calculateIntersection(line1: Line, line2: Line) -> Optional[Point]:
    if (line1._slope == line2._slope) or (line1.isVertical and line2.isVertical):
        return None
    
    if line1.isVertical:
        x = line1.start.x
        y = line2.calculateY(x)
        assert y is not None
        return Point(x=x, y=y)
    
    if line2.isVertical:
        x = line2.start.x
        y = line1.calculateY(x=x)
        assert y is not None
        return Point(x=x, y=y)
    
    x = (line2._yIntercept - line1._yIntercept) / (line1._slope - line2._slope)
    y = line1._slope * x + line1._yIntercept
    return Point(x=round(x, 2), y=round(y, 2))

def calculateIntersection_unextended(line1: Line, line2: Line) -> Optional[Point]:
    intersection = calculateIntersection(line1=line1, line2=line2)
    if intersection is not None:
        if not ((max(line1.end.x, line1.start.x) >= intersection.x >= min(line1.end.x, line1.start.x)) and \
                (max(line2.end.x, line2.start.x) >= intersection.x >= min(line2.end.x, line2.start.x)) and \
                (max(line1.end.y, line1.start.y) >= intersection.y >= min(line1.end.y, line1.start.y)) and \
                (max(line2.end.y, line2.start.y) >= intersection.y >= min(line2.end.y, line2.start.y))\
                ):
            intersection = None
    return intersection