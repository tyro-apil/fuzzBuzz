"""
utils/polygon.py

Utilities involving polygons
"""
from .line import Point, Line, calculateIntersection_unextended
from typing import List

class Polygon:
    def __init__(self, points: List[Point]):
        self.noOfPoints = len(points)
        for i in range(self.noOfPoints-1):
            assert points[i].x <= points[i+1].x
        self.points = points

        self._createLines()
        self._calculateLimits()
    
    def _createLines(self):
        self.lines: List[Line] = []
        for i in range(self.noOfPoints-1):
            self.lines.append(Line(self.points[i], self.points[i+1]))
    
    def _calculateLimits(self):
        self.xmin = self.points[0].x
        self.xmax = self.points[self.noOfPoints-1].x

        self.ymin = 0
        self.ymax = self.points[0].y
        for i in range(self.noOfPoints):
            if self.points[i].y > self.ymax:
                self.ymax = self.points[i].y
    
    def displayPoints(self):
        for pt in self.points:
            print(f"[{pt.x} {pt.y}]")
    


def combinePolygons(poly1: Polygon, poly2: Polygon) -> Polygon:
    combined_points: List[Point] = []

    # Ensure first polygon is always left
    if poly1.xmin > poly2.xmin:
        poly1, poly2 = poly2, poly1
    

    # Find intersections inside the region bounded by min and max
    intersection_points: List[Point] = []
    for i, linePoly1 in enumerate(poly1.lines):
        for j, linePoly2 in enumerate(poly2.lines):
            intersectPoint = calculateIntersection_unextended(linePoly1, linePoly2)
            if intersectPoint is not None:
                intersection_points.append(intersectPoint)
    
    # Sort the intersection points
    intersection_points: List[Point] = sorted(intersection_points, key=lambda point: (point.x, point.y))
    intersection_xmax = intersection_points[len(intersection_points)-1].x
    intersection_points_y_reverse: List[Point] = sorted(intersection_points, key=lambda point: (point.y), reverse=True)
    intersection_ymax = intersection_points_y_reverse[0].y

    # Find points for combined polygon
    for point in poly1.points:
        if (point.x <= intersection_points[0].x) or (point.y > intersection_ymax):
            combined_points.append(point)
    for point in poly2.points:
        if point.x >= intersection_xmax:
            combined_points.append(point)
    combined_points += intersection_points

    combined_points = sorted(combined_points, key=lambda point: (point.x, point.y))
    combined_polygon = Polygon(combined_points)
    return combined_polygon