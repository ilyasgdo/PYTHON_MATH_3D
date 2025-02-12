import pyray as pr
import math
from pyray import Vector3
import exo4 as exo4

def cross_product(A, B):
    newx=A.y*B.z -A.z*B.y
    newy=A.z*B.x -A.x* B.z
    newz=A.x*B.y -A.y *B.x

    return Vector3(newx, newy, newz)

def dot_product(A, B):
    return A.x*B.x+A.y*B.y+A.z * B.z

def vector_length(vector):
    return math.sqrt(dot_product(vector, vector))

def vector_normalize(vector):

    if vector_length(vector) == 0:
        return 0
    length = vector_length(vector)
    return Vector3(vector.x /length, vector.y /length, vector.z /length)



def aire(vec1, vec2):
    X = cross_product(vec1, vec2)
    return vector_length(X)

def draw_parallelogram(centre, vec1, vec2):
    
    point_a = centre
    point_b=Vector3(centre.x+vec1.x,centre.y+vec1.y,centre.z+ vec1.z)
    point_c= Vector3(point_a.x+vec2.x,point_a.y+vec2.y,point_a.z + vec2.z)
    point_d= Vector3(point_b.x+vec2.x,point_b.y+vec2.y,point_b.z+ vec2.z)

    pr.draw_line_3d(point_a,point_b, pr.YELLOW)
    pr.draw_line_3d(point_b,point_d,pr.YELLOW)
    pr.draw_line_3d(point_d, point_c,pr.YELLOW)
    pr.draw_line_3d(point_c,point_a, pr.YELLOW)

    pr.draw_line_3d(point_a,point_d,pr.RED)
    pr.draw_line_3d(point_b,point_c,pr.RED)

def main():
    pr.init_window(800, 600, "Parallélogramme 3D et surface")
    camera = pr.Camera3D(
        Vector3(10, 10, 10),  # Position
        Vector3(0, 0, 0),     # Cible
        Vector3(0, 1, 0),     # Haut
        45,                   # Champ de vision
        pr.CAMERA_PERSPECTIVE
    )
    pr.set_target_fps(120)

    centre = Vector3(0, 0, 0)
    vector1 = Vector3(3, 0, 0)
    vector2 = Vector3(0, 2, 4)

    aireP = aire(vector1, vector2)

    while not pr.window_should_close():
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)

        pr.begin_mode_3d(camera)
        pr.draw_grid(10, 1)  # Grille de référence

        # Dessine le parallélogramme
        draw_parallelogram(centre, vector1, vector2)

        pr.end_mode_3d()

        # Afficher la surface à l'écran
        pr.draw_text(f"aire: {aireP:.2f}", 10, 10, 20, pr.BLACK)

        pr.end_drawing()

    pr.close_window()

# Lancer le programme principal
if __name__ == "__main__":
    main()
