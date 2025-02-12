import pyray as pr
import math
from pyray import Vector3


def initialize_camera():
    """Initialise la caméra 3D."""
    camera = pr.Camera3D(
        Vector3(0, 10, 10),  # position
        Vector3(0, 0, 0),    # cible
        Vector3(0, 1, 0),    # haut
        45,                  # fovy (champ de vision dans la direction y)
        pr.CAMERA_PERSPECTIVE
    )
    return camera

def update_camera_position(camera, movement_speed):
    """Met à jour la position de la caméra en fonction des touches pressées."""
    if pr.is_key_down(pr.KEY_W):
        camera.position.z -= movement_speed
    if pr.is_key_down(pr.KEY_S):
        camera.position.z += movement_speed
    if pr.is_key_down(pr.KEY_A):
        camera.position.x -= movement_speed
    if pr.is_key_down(pr.KEY_D):
        camera.position.x += movement_speed
    if pr.is_key_down(pr.KEY_Q):
        camera.position.y += movement_speed
    if pr.is_key_down(pr.KEY_E):
        camera.position.y -= movement_speed

def draw_fov_cone(point, direction, distance, angle_phi, color=pr.BLUE, segments=20):
    """Dessine un secteur circulaire représentant le champ de vision (FOV) 2D."""
    direction = vector_normalize(direction)
    half_angle_rad = math.radians(angle_phi / 2)
    angle_step = (2 * half_angle_rad) / segments
    points = []
    for i in range(segments + 1):
        rotation_angle = -half_angle_rad + i * angle_step
        rotated_direction = rotate_vector_y(direction, rotation_angle)
        arc_point = Vector3(
            point.x + rotated_direction.x * distance,
            point.y + rotated_direction.y * distance,
            point.z + rotated_direction.z * distance
        )
        points.append(arc_point)
    for i in range(len(points) - 1):
        pr.draw_line_3d(point, points[i], color)
        pr.draw_line_3d(points[i], points[i + 1], color)
    pr.draw_line_3d(point, points[-1], color)

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




def rotate_vector_y(vector, angle):
    """Fait tourner un vecteur autour de l'axe Y selon un angle donné en radians."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return Vector3(
        vector.x * cos_a - vector.z * sin_a,
        vector.y,
        vector.x * sin_a + vector.z * cos_a
    )

def is_point_in_fov(fov_position, fov_direction, fov_distance, fov_angle, point):
    """Vérifie si un point est dans le champ de vision défini par une position, une direction, une distance et un angle."""
    point = Vector3(point.x - fov_position.x, point.y - fov_position.y, point.z - fov_position.z)
    distance = vector_length(point)
    if distance > fov_distance:
        return False
    normalize_fov_direction = vector_normalize(fov_direction)
    normalize_point = vector_normalize(point)
    dot = dot_product(normalize_fov_direction, normalize_point)
    cos_moitier_fov = math.cos(math.radians(fov_angle) / 2)
    return dot >= cos_moitier_fov

def draw_points(points, fov_position, fov_direction, fov_distance, fov_angle):
    """Dessine les points, avec une couleur verte s'ils sont dans le champ de vision (FOV)."""
    for point in points:
        if is_point_in_fov(fov_position, fov_direction, fov_distance, fov_angle, point):
            pr.draw_sphere(point, 0.1, pr.GREEN)
        else:
            pr.draw_sphere(point, 0.1, pr.RED)

def main():
    pr.init_window(800, 600, "FOV")
    camera = initialize_camera()
    pr.set_target_fps(60)
    grid_size = 15
    movement_speed = 0.1
    
    fov_position = Vector3(0, 0, 0)
    fov_direction = Vector3(0, 0, 1)  # Vecteur directeur du cône
    point_a = Vector3(1.5, 0, 2)
    point_b = Vector3(2, 0, 4)
    point_c = Vector3(-5, 0, 4)
    point_d = Vector3(4, 0, 2)
    point_e = Vector3(2, 0, -10)
    point_f = Vector3(-7, 7, 4)
    fov_distance = 5
    fov_angle = 90

    while not pr.window_should_close():
        update_camera_position(camera, movement_speed)
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)
        pr.begin_mode_3d(camera)
        
        pr.draw_grid(grid_size, 1)  # Dessine une grille pour référence
        draw_points([point_a, point_b, point_c,point_d, point_e, point_f], fov_position, fov_direction, fov_distance, fov_angle)
        draw_fov_cone(fov_position, fov_direction, fov_distance, fov_angle)

        pr.end_mode_3d()
        pr.end_drawing()

    pr.close_window()

# Lancer le programme principal
if __name__ == "__main__":
    main()
