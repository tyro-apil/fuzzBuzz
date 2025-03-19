
"""
utils/centroid.py

Utilities to find centroid
"""
from .line import Point
from .polygon import Polygon

def get_area(poly: Polygon) -> float:
    l = poly.noOfPoints
    area = 0.0
    assert(l > 2)
    for i in range(l-1):
        x1 = poly.points[i].x
        y1 = poly.points[i].y
        x2 = poly.points[i+1].x
        y2 = poly.points[i+1].y

        area+= (x1*y2 - x2* y1)
        
    x1 = poly.points[-1].x
    y1 = poly.points[-1].y
    x2 = poly.points[0].x
    y2 = poly.points[0].y

    area+= (x1*y2 - x2* y1)
    

    area =abs( 0.5 * area)
    
    return area

def get_centroid(poly: Polygon) -> Point:
    l = poly.noOfPoints
    c_x = 0.0
    c_y = 0.0
    assert(l > 2)
    area = get_area(poly)
    for i in range(l-1):
        x1 = poly.points[i].x
        y1 = poly.points[i].y
        x2 = poly.points[i+1].x
        y2 = poly.points[i+1].y

        c_x+= (x1*y2 - x2* y1) * (x1+x2)
        c_y+= (x1*y2 - x2* y1) * (y1+y2)

    x1 = poly.points[-1].x
    y1 = poly.points[-1].y
    x2 = poly.points[0].x
    y2 = poly.points[0].y

    c_x+= (x1*y2 - x2* y1) * (x1+x2)
    c_y+= (x1*y2 - x2* y1) * (y1+y2)

    c_x = abs(c_x) / (6 * area)
    c_y = abs(c_y) / (6 * area)

    return Point(abs(c_x),abs(c_y))



