import pyray as pr
import numpy as np
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





def draw_points(points):
    """Dessiner le point 3Ds."""
    for point in points:
        pr.draw_sphere(point, 0.1, pr.RED)  


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
    
    normal = compute_normal(points)
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

        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)
        pr.begin_mode_3d(camera)
        draw_points(points)

        draw_plane(normal, centre_estime, size=5, couleur=pr.RED)
        draw_plane(normale_reference, point_reference, size=5, couleur=pr.GREEN)

        pr.end_mode_3d()
        pr.draw_text("Utilisez WASD pour déplacer la caméra", 10, 10, 20, pr.DARKGRAY)
        pr.end_drawing()

    pr.close_window()
    
if __name__ == "__main__":
    main()
