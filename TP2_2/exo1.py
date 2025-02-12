import pyray as pr
import numpy as np
import math
from pyray import Vector3
import trimesh
from TP1.exo1_2 import (
    initialize_camera,
    update_camera_position,
    dot_product,
    vector_length,
    cross_product,
    vector_normalize,

)


def draw_plane(axis, size=5, color=pr.GRAY):
    """Dessine un plan basé sur un vecteur normal et une taille."""
    axis = vector_normalize(axis)
    orthogonal_vector = Vector3(1, 0, 0) if abs(axis.x) < abs(axis.y) else Vector3(0, 1, 0)
    v1 = cross_product(axis, orthogonal_vector)
    v2 = cross_product(axis, v1)

    for i in range(-size, size + 1):
        start1 = Vector3(v1.x * -size + v2.x * i, v1.y * -size + v2.y * i, v1.z * -size + v2.z * i)
        end1 = Vector3(v1.x * size + v2.x * i, v1.y * size + v2.y * i, v1.z * size + v2.z * i)
        start2 = Vector3(v2.x * -size + v1.x * i, v2.y * -size + v1.y * i, v2.z * -size + v1.z * i)
        end2 = Vector3(v2.x * size + v1.x * i, v2.y * size + v1.y * i, v2.z * size + v1.z * i)
        
        pr.draw_line_3d(start1, end1, color)
        pr.draw_line_3d(start2, end2, color)

def draw_vector_3(start, end, color, thickness=0.05, head_size_factor=0.8):
    """Dessine un vecteur en utilisant un cylindre et un cône."""
    direction = Vector3(end.x - start.x, end.y - start.y, end.z - start.z)
    length = vector_length(direction)
    head_size = length * head_size_factor
    
    n_direction = vector_normalize(direction)
    
    arrow_start = Vector3(start.x + n_direction.x * head_size, 
                          start.y + n_direction.y * head_size, 
                          start.z + n_direction.z * head_size)
    
    pr.draw_cylinder_ex(start, end, thickness / 2, thickness / 2, 8, color)
    pr.draw_cylinder_ex(arrow_start, end, thickness * 2, thickness / 5, 8, color)

def draw_coordinate_axes(origin, scale=3):
    """Dessine les axes de coordonnées standard X, Y, Z à partir de l'origine."""
    # X-axis (Rouge)
    draw_vector_3(origin, Vector3(origin.x + scale, origin.y, origin.z), pr.RED, thickness=0.05)
    
    # Y-axis (Vert)
    draw_vector_3(origin, Vector3(origin.x, origin.y + scale, origin.z), pr.GREEN, thickness=0.05)
    
    # Z-axis (Bleu)
    draw_vector_3(origin, Vector3(origin.x, origin.y, origin.z + scale), pr.BLUE, thickness=0.05)

def draw_transformation_axis(origin, axis, scale=3):
    """Dessine l'axe de transformation personnalisé à partir de l'origine dans la direction de l'axe donné."""
    # Mettre à l'échelle le vecteur d'axe pour la visualisation
    scaled_axis = Vector3(origin.x + axis.x * scale, origin.y + axis.y * scale, origin.z + axis.z * scale)
    draw_vector_3(origin, scaled_axis, pr.PURPLE, thickness=0.05)

def draw_mesh(mesh):
    """Dessine le mesh complet avec sommets, arêtes et faces."""
    for face in mesh.faces:
        v0 = Vector3(*mesh.vertices[face[0]])
        v1 = Vector3(*mesh.vertices[face[1]])
        v2 = Vector3(*mesh.vertices[face[2]])
        pr.draw_triangle_3d(v0, v1, v2, pr.LIGHTGRAY)
    
    for edge in mesh.edges:
        v_start = Vector3(*mesh.vertices[edge[0]])
        v_end = Vector3(*mesh.vertices[edge[1]])
        pr.draw_line_3d(v_start, v_end, pr.BLACK)
    
    for vertex in mesh.vertices:
        pr.draw_sphere(Vector3(*vertex), 0.05, pr.RED)

def load_ply_file(file_path):
    """Charge un fichier PLY et retourne le mesh en tant que structure de données trimesh."""
    mesh = trimesh.load(file_path)
    return mesh



def shearing_matrix_homogeneous(axis, s, t):
    axis = vector_normalize(axis)
    return np.array([
        [1, 0, s,0],
        [0, 1, t,0],
        [0, 0, 1,0],
        [0, 0, 0, 1]
    ])



def rotation_matrix_homogeneous(axis, theta):
    """Génère une matrice homogène de rotation autour d'un axe arbitraire (4x4)."""
    axis = vector_normalize(axis)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    return np.array([
        [cos_t + axis.x ** 2 * (1 - cos_t), axis.x * axis.y * (1 - cos_t) - axis.z * sin_t,
         axis.x * axis.z * (1 - cos_t) + axis.y * sin_t, 0],
        [axis.y * axis.x * (1 - cos_t) + axis.z * sin_t, cos_t + axis.y ** 2 * (1 - cos_t),
         axis.y * axis.z * (1 - cos_t) - axis.x * sin_t, 0],
        [axis.z * axis.x * (1 - cos_t) - axis.y * sin_t, axis.z * axis.y * (1 - cos_t) + axis.x * sin_t,
         cos_t + axis.z ** 2 * (1 - cos_t), 0],
        [0, 0, 0, 1]
    ])

def scaling_matrix_homogeneous(axis, k):
    """Génère une matrice homogène de mise à l'échelle le long d'un axe arbitraire (4x4)."""
    axis = vector_normalize(axis)
    axis = vector_normalize(axis)
    return np.array([
        [1 + (k - 1) * axis.x ** 2, (k - 1) * axis.x * axis.y, (k - 1) * axis.x * axis.z, 0],
        [(k - 1) * axis.x * axis.y, 1 + (k - 1) * axis.y ** 2, (k - 1) * axis.y * axis.z, 0],
        [(k - 1) * axis.x * axis.z, (k - 1) * axis.y * axis.z, 1 + (k - 1) * axis.z ** 2, 0],
        [0, 0, 0, 1]
    ])

def orthographic_projection_matrix_homogeneous(axis):
    """Génère une matrice homogène de projection orthographique sur un plan normal à un axe donné (4x4)."""

    axis = vector_normalize(axis)
    return np.array([
        [1 - axis.x ** 2, -axis.x * axis.y, -axis.x * axis.z,0],
        [-axis.x * axis.y, 1 - axis.y ** 2, -axis.y * axis.z,0],
        [-axis.x * axis.z, -axis.y * axis.z, 1 - axis.z ** 2,0],
        [0, 0, 0, 1]
    ])


def translation_matrix(tx, ty, tz):
    """Génère une matrice homogène de translation (4x4)."""
    matrix = np.eye(4)
    matrix[0:3, 3] = [tx, ty, tz]
    print(matrix)
    return matrix

def shearing_matrix(axis,s,t):
    axis = vector_normalize(axis)
    return np.array([
        [1,0,s,0],
        [0,1,t,0],
        [0,0,1,0],
        [0, 0, 0, 1]
    ])


def perspective_projection_matrix(d):
    """Génère une matrice homogène de projection en perspective avec une distance focale d."""
    if d == 0:
        d = 1e-10 # pour enlever div by zero

    matrix = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 1/d, 0]
    ])

    return matrix

def apply_transformations_homogeneous(mesh, translation_mat, rotation_mat, scaling_mat, projection_mat):
    """Applique les transformations de rotation, de mise à l'échelle et de projection aux sommets du mesh en utilisant des matrices 4x4."""
    vertices_homogeneous = np.hstack((mesh.original_vertices, np.ones((mesh.original_vertices.shape[0], 1))))
    transformed_vertices = vertices_homogeneous @ translation_mat.T @ rotation_mat.T @ scaling_mat.T  @ projection_mat.T
    mesh.vertices = transformed_vertices[:, :3] / transformed_vertices[:, 3, np.newaxis]

def initialize_mesh_for_transforming(mesh):
    """Stocke les sommets originaux du mesh pour permettre un redimensionnement dynamique."""
    mesh.original_vertices = np.copy(mesh.vertices)

def main():
    pr.init_window(1000, 900, "Visionneuse 3D avec contrôle de rotation, de mise à l'échelle et de projection")
    pr.set_window_min_size(800, 600)
    camera = initialize_camera()
    pr.set_target_fps(120)
    movement_speed = 0.2

    # Chargement du mesh et initialisation des transformations
    ply_file_path = "../cube.ply"
    mesh = load_ply_file(ply_file_path)
    initialize_mesh_for_transforming(mesh)

    # Contrôles d'interface pour les transformations et translations
    scale_factor_ptr = pr.ffi.new('float *', 1.0)
    angle_ptr = pr.ffi.new('float *', 0.0)
    axis_x_ptr = pr.ffi.new('float *', 1.0)
    axis_y_ptr = pr.ffi.new('float *', 0.0)
    axis_z_ptr = pr.ffi.new('float *', 0.0)
    translate_x_ptr = pr.ffi.new('float *', 0.0)
    translate_y_ptr = pr.ffi.new('float *', 0.0)
    translate_z_ptr = pr.ffi.new('float *', 0.0)


    d_ptr = pr.ffi.new('float *', 1.0)       # Paramètre de distance pour la projection en perspective
    projection_type_ptr = pr.ffi.new('float *', -1)  # Valeur par défaut (aucune projection)

    while not pr.window_should_close():
        update_camera_position(camera, movement_speed)
        
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)
        pr.begin_mode_3d(camera)
        
        axis = Vector3(axis_x_ptr[0], axis_y_ptr[0], axis_z_ptr[0])
        angle = angle_ptr[0]

        scale_factor = scale_factor_ptr[0]


        rotation_mat = rotation_matrix_homogeneous(axis, np.radians(angle))
        scaling_mat = scaling_matrix_homogeneous(axis, scale_factor)

        # Choix de la projection
        projection_mat = np.eye(4)
        if projection_type_ptr[0] > -1 and projection_type_ptr[0] < 1:
            projection_mat = orthographic_projection_matrix_homogeneous(axis)
        elif projection_type_ptr[0] == 1:
            projection_mat = perspective_projection_matrix(d_ptr[0])
        
        # Dessin des axes et du mesh
        draw_coordinate_axes(Vector3(0, 0, 0), scale=3)
        draw_transformation_axis(Vector3(0, 0, 0), axis, scale=3)

        tx = translate_x_ptr[0]
        ty = translate_y_ptr[0]
        tz = translate_z_ptr[0]
        translation_mat = translation_matrix(tx, ty, tz)
        
        apply_transformations_homogeneous(mesh, translation_mat, rotation_mat, scaling_mat, projection_mat)
        
        draw_plane(axis, 10)
        draw_mesh(mesh)
        pr.end_mode_3d()

        # GUI de contrôle pour les transformations
        pr.draw_text("Échelle:", 750, 50, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 80, 200, 20), "0.5", "10", scale_factor_ptr, 0.4, 10.0)

        pr.draw_text("Angle (degrés):", 750, 110, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 140, 200, 20), "0", "360", angle_ptr, 0.0, 360.0)

        pr.draw_text("Axe X:", 750, 170, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 200, 200, 20), "-1.0", "1.0", axis_x_ptr, -1.0, 1.0)

        pr.draw_text("Axe Y:", 750, 230, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 260, 200, 20), "-1.0", "1.0", axis_y_ptr, -1.0, 1.0)

        pr.draw_text("Axe Z:", 750, 290, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 320, 200, 20), "-1.0", "1.0", axis_z_ptr, -1.0, 1.0)

        # Translations
        pr.draw_text("Translation X:", 750, 350, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 380, 200, 20), "-5.0", "5.0", translate_x_ptr, -5.0, 5.0)

        pr.draw_text("Translation Y:", 750, 410, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 440, 200, 20), "-5.0", "5.0", translate_y_ptr, -5.0, 5.0)

        pr.draw_text("Translation Z:", 750, 470, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 500, 200, 20), "-5.0", "5.0", translate_z_ptr, -5.0, 5.0)


        # Projection
        pr.draw_text("Type projection:", 750, 650, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 680, 200, 20), "-1", "1", projection_type_ptr, -1.0, 1.0)

        if projection_type_ptr[0] == 1:
            pr.draw_text("Distance projection:", 750, 710, 20, pr.BLACK)
            pr.gui_slider_bar(pr.Rectangle(750, 740, 200, 20), "1.0", "8.0", d_ptr, 1.0, 8.0)

        pr.end_drawing()

    pr.close_window()

if __name__ == "__main__":
    main()