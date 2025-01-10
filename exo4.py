import pyray as pr
import math
from pyray import Vector3
import exo4 as exo4

def vector_cross_product(A, B):
    """Calcule le produit vectoriel de deux vecteurs 3D."""
    return Vector3(
        A.y * B.z - A.z * B.y,
        A.z * B.x - A.x * B.z,
        A.x * B.y - A.y * B.x
    )

def vector_length(vector):
    """Calcule la longueur d'un vecteur."""
    return math.sqrt(vector.x ** 2 + vector.y ** 2 + vector.z ** 2)

def calculate_parallelogram_area(vec1, vec2):
    """Calcule la surface d'un parallélogramme défini par deux vecteurs."""
    cross_product = vector_cross_product(vec1, vec2)
    return vector_length(cross_product)

def draw_parallelogram(origin, vec1, vec2):
    """
    Dessine un parallélogramme défini par deux vecteurs 3D.
    :param origin: Origine du parallélogramme (Vector3).
    :param vec1: Premier vecteur (Vector3).
    :param vec2: Deuxième vecteur (Vector3).
    """
    # Calcul des sommets du parallélogramme
    point_a = origin
    point_b = Vector3(origin.x + vec1.x, origin.y + vec1.y, origin.z + vec1.z)
    point_c = Vector3(point_a.x + vec2.x, point_a.y + vec2.y, point_a.z + vec2.z)
    point_d = Vector3(point_b.x + vec2.x, point_b.y + vec2.y, point_b.z + vec2.z)

    # Dessine les côtés du parallélogramme
    pr.draw_line_3d(point_a, point_b, pr.BLUE)
    pr.draw_line_3d(point_b, point_d, pr.BLUE)
    pr.draw_line_3d(point_d, point_c, pr.BLUE)
    pr.draw_line_3d(point_c, point_a, pr.BLUE)

    # Dessine les diagonales pour référence
    pr.draw_line_3d(point_a, point_d, pr.RED)
    pr.draw_line_3d(point_b, point_c, pr.RED)

def main():
    pr.init_window(800, 600, "Parallélogramme 3D et surface")
    camera = pr.Camera3D(
        Vector3(10, 10, 10),  # Position
        Vector3(0, 0, 0),     # Cible
        Vector3(0, 1, 0),     # Haut
        45,                   # Champ de vision
        pr.CAMERA_PERSPECTIVE
    )
    pr.set_target_fps(60)

    # Définir l'origine et les vecteurs
    origin = Vector3(0, 0, 0)
    vector1 = Vector3(3, 0, 0)  # Vecteur 1
    vector2 = Vector3(0, 2, 4)  # Vecteur 2

    # Calculer la surface du parallélogramme
    area = calculate_parallelogram_area(vector1, vector2)

    while not pr.window_should_close():
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)

        pr.begin_mode_3d(camera)
        pr.draw_grid(10, 1)  # Grille de référence

        # Dessine le parallélogramme
        draw_parallelogram(origin, vector1, vector2)

        pr.end_mode_3d()

        # Afficher la surface à l'écran
        pr.draw_text(f"Surface: {area:.2f}", 10, 10, 20, pr.BLACK)

        pr.end_drawing()

    pr.close_window()

# Lancer le programme principal
if __name__ == "__main__":
    main()
