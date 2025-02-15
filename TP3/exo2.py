import pyray as pr
import numpy as np
import math
from pyray import Vector3
from TP1.exo1_2 import (cross_product,
                      vector_length,
                      vector_normalize,dot_product)
from TP1.exo5 import (initialize_camera,update_camera_position)

   

def generate_random_points_on_plane(point, normal, num_points=10, spread=5):
    """
    # Génère des points aléatoires situés sur un plan défini par un point et un vecteur normal.

    Args:
        point (Vector3): Un point sur le plan.
        normal (Vector3): Le vecteur normal définissant le plan.
        num_points (int): Le nombre de points à générer.
        spread (float): L'écart maximal des points par rapport au point de référence.

    Returns:
        list: Une liste de points Vector3 situés sur le plan.
    """

    normal = vector_normalize(normal)

    # Générer deux vecteurs orthogonaux dans le plan
    if abs(normal.x) > 1e-3 or abs(normal.z) > 1e-3:
        u = vector_normalize(Vector3(-normal.z, 0, normal.x))
    else:
        u = vector_normalize(Vector3(0, -normal.z, normal.y))
    v = vector_normalize(cross_product(normal, u))

    # Générer des points aléatoires dans le plan en utilisant la base orthogonale
    points = []
    for _ in range(num_points):
        r1 = np.random.uniform(-spread, spread)
        r2 = np.random.uniform(-spread, spread)
        p = Vector3(
            point.x + r1 * u.x + r2 * v.x,
            point.y + r1 * u.y + r2 * v.y,
            point.z + r1 * u.z + r2 * v.z
        )
        decalage = np.random.uniform(-5, 5)
        p = Vector3(p.x + decalage * normal.x, p.y + decalage * normal.y, p.z + decalage * normal.z)

        points.append(p)

    return points



def compute_normal(points):
    centre = Vector3(0, 0, 0)
    nb_points = len(points)
    for pt in points:
        centre.x += pt.x
        centre.y += pt.y
        centre.z += pt.z

    centre.x /= nb_points
    centre.y /= nb_points
    centre.z /= nb_points

    differences = []

    for pt in points:

        diff = Vector3(pt.x - centre.x, pt.y - centre.y, pt.z - centre.z)
        differences.append([diff.x, diff.y, diff.z])

    _, _, Vt = np.linalg.svd(differences)

    normale = Vt[-1]

    return Vector3(normale[0], normale[1], normale[2])

def compute_aabb(points):
    
    
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    
    zs = [p.z for p in points]

    pmin = Vector3(min(xs), min(ys), min(zs))
    pmax = Vector3(max(xs), max(ys), max(zs))

    return pmin, pmax


def draw_aabb(pmin, pmax, color=pr.BLUE):
   
    c1 = Vector3(pmin.x, pmin.y, pmin.z)
    c2 = Vector3(pmax.x, pmin.y, pmin.z)
    c3 = Vector3(pmax.x, pmax.y, pmin.z)
    c4 = Vector3(pmin.x, pmax.y, pmin.z)
    c5 = Vector3(pmin.x, pmin.y, pmax.z)
    c6 = Vector3(pmax.x, pmin.y, pmax.z)
    c7 = Vector3(pmax.x, pmax.y, pmax.z)
    c8 = Vector3(pmin.x, pmax.y, pmax.z)

    pr.draw_line_3d(c1, c2, color)
    pr.draw_line_3d(c2, c3, color)
    pr.draw_line_3d(c3, c4, color)
    pr.draw_line_3d(c4, c1, color)

    pr.draw_line_3d(c5, c6, color)
    pr.draw_line_3d(c6, c7, color)
    pr.draw_line_3d(c7, c8, color)
    pr.draw_line_3d(c8, c5, color)

    pr.draw_line_3d(c1, c5, color)
    pr.draw_line_3d(c2, c6, color)
    pr.draw_line_3d(c3, c7, color)
    pr.draw_line_3d(c4, c8, color)

    centroid = Vector3((pmin.x + pmax.x) / 2,
                       (pmin.y + pmax.y) / 2,
                       (pmin.z + pmax.z) / 2)
    pr.draw_sphere(centroid, 0.1, color)

def apply_transformation(point, matrix):
    
    v = np.array([point.x, point.y, point.z])
    vt = matrix @ v
    return Vector3(vt[0], vt[1], vt[2])


def transform_points(points, matrix):
    
    return [apply_transformation(p, matrix) for p in points]


def transform_aabb(matrix, pmin, pmax):
    
    centre = Vector3((pmin.x + pmax.x) / 2,
                     (pmin.y + pmax.y) / 2,
                     (pmin.z + pmax.z) / 2)
    
    extent = Vector3((pmax.x - pmin.x) / 2,
                     (pmax.y - pmin.y) / 2,
                     (pmax.z - pmin.z) / 2)

    nouveau_centre = apply_transformation(centre, matrix)

    m = matrix
    nouveau_extent_x = abs(m[0, 0]) * extent.x + abs(m[0, 1]) * extent.y + abs(m[0, 2]) * extent.z
    nouveau_extent_y = abs(m[1, 0]) * extent.x + abs(m[1, 1]) * extent.y + abs(m[1, 2]) * extent.z
    nouveau_extent_z = abs(m[2, 0]) * extent.x + abs(m[2, 1]) * extent.y + abs(m[2, 2]) * extent.z

    nouveau_pmin = Vector3(nouveau_centre.x - nouveau_extent_x,
                       nouveau_centre.y - nouveau_extent_y,
                       nouveau_centre.z - nouveau_extent_z)
    
    nouveau_pmax = Vector3(nouveau_centre.x + nouveau_extent_x,
                       nouveau_centre.y + nouveau_extent_y,
                       nouveau_centre.z + nouveau_extent_z)
    
    return nouveau_pmin, nouveau_pmax

def draw_points(points, size=0.1, color=pr.RED):
    """Dessiner le point 3Ds."""
    for point in points:
        pr.draw_sphere(point,size, color)  


def draw_plane(normal, point_on_plane, size=10, couleur=pr.RED):
    """Dessiner un plan étant donné sa normale et un point situé dessus."""
    ref = Vector3(0, 1, 0) if abs(normal.y) < 0.99 else Vector3(1, 0, 0)

    u = vector_normalize(cross_product(normal, ref))
    v = vector_normalize(cross_product(normal, u))

    coin1 = Vector3(point_on_plane.x + (u.x + v.x) * size,
                    point_on_plane.y + (u.y + v.y) * size,
                    point_on_plane.z + (u.z + v.z) * size)
    
    coin2 = Vector3(point_on_plane.x + (-u.x + v.x) * size,
                    point_on_plane.y + (-u.y + v.y) * size,
                    point_on_plane.z + (-u.z + v.z) * size)
    
    coin4 = Vector3(point_on_plane.x + (u.x - v.x) * size,
                    point_on_plane.y + (u.y - v.y) * size,
                    point_on_plane.z + (u.z - v.z) * size)
    coin3 = Vector3(point_on_plane.x + (-u.x - v.x) * size,
                    point_on_plane.y + (-u.y - v.y) * size,
                    point_on_plane.z + (-u.z - v.z) * size)
    
    pr.draw_line_3d(coin1, coin2, couleur)
    pr.draw_line_3d(coin2, coin3, couleur)
    pr.draw_line_3d(coin3, coin4, couleur)
    pr.draw_line_3d(coin4, coin1, couleur)

    fin_normal = Vector3(point_on_plane.x + normal.x * size,
                          point_on_plane.y + normal.y * size,
                          point_on_plane.z + normal.z * size)
    pr.draw_line_3d(point_on_plane, fin_normal, couleur)




def main():
    pr.init_window(1000, 800, "Visualisation de points et de plans en 3D")
    pr.set_target_fps(60)
    movement_speed = 0.1
    camera = initialize_camera()
    
    # Générer des points aléatoires situés sur le plan
    points = generate_random_points_on_plane(Vector3(0, 0, 0), Vector3(1, 1, 1), num_points=10, spread=5)
    
    orig_pmin, orig_pmax = compute_aabb(points)
    
    centre_estime = Vector3(0, 0, 0)

    for pt in points:
        centre_estime.x += pt.x
        centre_estime.y += pt.y
        centre_estime.z += pt.z

    centre_estime.x /= len(points)
    centre_estime.y /= len(points)
    centre_estime.z /= len(points)

    normale_reference = vector_normalize(Vector3(1, 1, 1))
    point_reference = Vector3(0, 0, 0)

    while not pr.window_should_close():
        update_camera_position(camera, 0.5)

        angle = pr.get_time() * 0.5 
        M = np.array([[math.cos(angle), 0, math.sin(angle)],
                      [0, 1, 0],
                      [-math.sin(angle), 0, math.cos(angle)]])


        transformed_points = transform_points(points, M)
        trans_pts_pmin, trans_pts_pmax = compute_aabb(transformed_points)
        trans_box_pmin, trans_box_pmax = transform_aabb(M, orig_pmin, orig_pmax)


        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)
        pr.begin_mode_3d(camera)


        draw_points(points, size=0.1, color=pr.RED)
        draw_aabb(orig_pmin, orig_pmax, color=pr.BLUE)

        draw_points(transformed_points, size=0.1, color=pr.GREEN)
        draw_aabb(trans_pts_pmin, trans_pts_pmax, color=pr.PURPLE)

        draw_aabb(trans_box_pmin, trans_box_pmax, color=pr.ORANGE)

       

        pr.end_mode_3d()

        pr.draw_text("WASD pour déplacer la caméra", 10, 10, 20, pr.DARKGRAY)
        pr.draw_text("Points originaux RED", 10, 40, 20, pr.RED)
        pr.draw_text("AABB originale BLUE", 10, 70, 20, pr.BLUE)
        pr.draw_text("Points transformés GREEN", 10, 100, 20, pr.GREEN)
        pr.draw_text("AABB points transformés PURPLE", 10, 130, 20, pr.PURPLE)
        pr.draw_text("AABB transformée de l'AABB ORANGE", 10, 160, 20, pr.ORANGE)
        pr.end_drawing()

    pr.close_window()
    
if __name__ == "__main__":
    main()
