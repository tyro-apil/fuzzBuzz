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

        # Initialize ymin and ymax with the first point's y value
        self.ymin = self.points[0].y
        self.ymax = self.points[0].y
        
        # Then find the actual min and max
        for i in range(self.noOfPoints):
            if self.points[i].y > self.ymax:
                self.ymax = self.points[i].y
            if self.points[i].y < self.ymin:
                self.ymin = self.points[i].y
    
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

    # Handle case where polygons don't intersect
    if len(intersection_points) == 0:
        # Return union of points if no intersection
        all_points = poly1.points + poly2.points
        sorted_points = sorted(all_points, key=lambda point: (point.x, point.y))
        return Polygon(sorted_points)
    
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

    ## Fix same x-coodinates problem
    for i in range(len(combined_points)-1):
        if combined_points[i].x == combined_points[i+1].x:
            if i!=0:
                if combined_points[i-1].y != combined_points[i].y:
                    combined_points[i],combined_points[i+1]=combined_points[i+1],combined_points[i]
    
    combined_polygon = Polygon(combined_points)
    return combined_polygon
