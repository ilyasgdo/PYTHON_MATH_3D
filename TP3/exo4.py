import pyray as pr
import numpy as np
from pyray import Vector3

from TP1.exo5 import (dot_product)
def barycentric_coordinates(p, a, b, c):
    """Calculer les coordonnées barycentriques du point p dans le triangle abc."""

    v0 = Vector3(b.x - a.x, b.y - a.y, b.z - a.z)
    v1 = Vector3(c.x - a.x, c.y - a.y, c.z - a.z)
    v2 = Vector3(p.x - a.x, p.y - a.y, p.z - a.z)

    p00 = dot_product(v0, v0)
    p01 = dot_product(v0, v1)
    p11 = dot_product(v1, v1)
    p20 = dot_product(v2, v0)
    p21 = dot_product(v2, v1)

    denom = p00 * p11 - p01 * p01
    if denom == 0:
        return -1, -1, -1

    v = (p11 * p20 - p01 * p21) / denom
    w = (p00 * p21 - p01 * p20) / denom

    u = 1 - v - w

    return u, v, w

def interpolate_color(u, v, w, color_a, color_b, color_c):
    """Interpoler la couleur à l'aide de coordonnées barycentriques."""
    r = u * color_a[0] + v * color_b[0] + w * color_c[0]
    g = u * color_a[1] + v * color_b[1] + w * color_c[1]
    b = u * color_a[2] + v * color_b[2] + w * color_c[2]
    return int(r), int(g), int(b)

def draw_colored_triangle(a, b, c, color_a, color_b, color_c, grid_size):
    """Dessinez un triangle avec des couleurs interpolées en utilisant des coordonnées barycentriques."""
    min_x = int(min(a.x, b.x, c.x))
    max_x = int(max(a.x, b.x, c.x))
    min_y = int(min(a.y, b.y, c.y))
    max_y = int(max(a.y, b.y, c.y))

    for y in range(min_y, max_y, grid_size):
        for x in range(min_x, max_x, grid_size):
            p = Vector3(x + grid_size / 2, y + grid_size / 2, 0)  # Utiliser le centre du carré de la grille
            u, v, w = barycentric_coordinates(p, a, b, c)

            if u >= 0 and v >= 0 and w >= 0:  # Le point est à l'intérieur du triangle
                color = interpolate_color(u, v, w, color_a, color_b, color_c)
                pr.draw_rectangle(x, y, grid_size, grid_size, pr.Color(*color, 255))

def main():
    pr.init_window(1000, 800, "Interpolation de couleurs triangulaires")
    pr.set_target_fps(60)

    window_width = pr.get_screen_width()
    window_height = pr.get_screen_height()

    a = Vector3(window_width / 2 - 200, window_height / 2 - 200, 0)
    b = Vector3(window_width / 2 + 200, window_height / 2 - 200, 0)
    c = Vector3(window_width / 2, window_height / 2 + 200, 0)

    color_a = (255, 0, 0)  # Rouge
    color_b = (0, 255, 0)  # Vert
    color_c = (0, 0, 255)  # Bleu

    grid_size = 10  # Taille de chaque carré, plus la valeur est basse, plus le carré est petit. Plus le programme est lent.

    while not pr.window_should_close():
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)

        draw_colored_triangle(a, b, c, color_a, color_b, color_c, grid_size)

        pr.end_drawing()

    pr.close_window()

if __name__ == "__main__":
    main()