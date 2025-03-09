import matplotlib.pyplot as plt
import matplotlib.patches as patches
from .line import Point
from .polygon import Polygon

def plot_polygon_with_centroid(poly:Polygon, centroid: Point ):
    fig, ax = plt.subplots()
    polygon_vertices = [(point.x,point.y) for point in poly.points]
    point = (centroid.x,centroid.y)
    point_x, point_y = point[0],point[1]

    poly = patches.Polygon(polygon_vertices)
    ax.add_patch(poly)
    ax.scatter(point_x, point_y, color='red', label='Point')


    plt.xlim(0,10)
    plt.ylim(0,10)
    plt.grid()
    plt.show()