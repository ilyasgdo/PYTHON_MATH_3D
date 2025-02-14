import pyray as pr
import numpy as np
from pyray import Vector3

# Importer les fonctions et utilitaires existants
from exo1 import (
    initialize_camera,
    update_camera_position,
    load_ply_file,
    initialize_mesh_for_transforming,
    apply_transformations_homogeneous,
    draw_mesh,
    rotation_matrix_homogeneous,
    translation_matrix
)

def trefle_noeud(t):
    x = np.sin(3*t)
    y = np.cos(2*t)
    z = np.sin(2*t)
    return x, y, z

def huit_noeud(t):
    x= (2+ np.cos(2*t)) * np.cos(3*t)
    y= (2+ np.cos(2*t)) * np.sin(3*t)
    z= np.sin(4*t)
    return x, y, z

def noeud_4_3(t):
    x= np.cos(2*t) * (2 + np.cos(3*t))
    y= np.sin(2*t) * (2 + np.cos(3*t))
    z= np.sin(5*t)
    return x, y, z

def solomon_noeud(t):
    x= (2+np.cos(5*t)) * np.cos(2*t)
    y= (2+np.cos(5*t)) * np.sin(2*t)
    z = np.sin(5*t)
    return x, y, z


def uniform_scaling_matrix_homogeneous(k):
    """Génère une matrice homogène de mise à l'échelle uniforme (4x4)."""
    return np.array([
           [k, 0, 0, 0],
           [0, k, 0, 0],
           [0, 0, k, 0],
           [0, 0, 0, 1]
       ])

def helix_curve(length, t, spacing, num_turns, scale_factor):
    """Définit une courbe hélicoïdale 3D mise à l'échelle pour s'adapter à la vue."""
    z_max = spacing * num_turns * (2 * np.pi)
    scale = scale_factor / z_max  # Ajuster l'échelle
    return (
        spacing * np.cos(t) * scale,   # Coordonnée x mise à l'échelle
        length * t / (2 * np.pi) * scale,  # Coordonnée y mise à l'échelle
        spacing * np.sin(t) * scale   # Coordonnée z mise à l'échelle
    )

def type_courbe_manager(t, curve_type, scale_factor=1.0):
    if curve_type == 0:
        x, y, z = trefle_noeud(t)
    elif curve_type == 1:
        x, y, z = huit_noeud(t)
    elif curve_type == 2:
        x, y, z = noeud_4_3(t)
    elif curve_type == 3:
        x, y, z = solomon_noeud(t)
    else:
        x, y, z = trefle_noeud(t) 
        
    return x * scale_factor, y * scale_factor, z * scale_factor

def main():
    pr.init_window(1000, 900, "Cubes tournants le long d'une hélice")
    pr.set_target_fps(180)

    # Charger l'objet central
    mesh_file = "cube.ply"
    mesh = load_ply_file(mesh_file)
    initialize_mesh_for_transforming(mesh)

    # Contrôles GUI
    translate_x_ptr = pr.ffi.new('float *', 0.0)
    translate_y_ptr = pr.ffi.new('float *', 0.0)
    translate_z_ptr = pr.ffi.new('float *', 0.0)
    rotation_angle_ptr = pr.ffi.new('float *', 0.0)
    axis_x_ptr = pr.ffi.new('float *', 1.0)
    axis_y_ptr = pr.ffi.new('float *', 0.0)
    axis_z_ptr = pr.ffi.new('float *', 0.0)
    cube_scale_ptr = pr.ffi.new('float *', 0.1)
    curve_length = 10  # Longueur totale de l'hélice
    num_turns_ptr = pr.ffi.new('float *', 5.0)  # Nombre de tours par défaut
    spacing_between_turns_ptr = pr.ffi.new('float *', 10.0)  # Espacement entre les tours
    nb_cubes_ptr = pr.ffi.new('float *', 20.0)  # Nombre de cubes par tour      
    courbe_type_ptr = pr.ffi.new('int *', 0)


    camera = initialize_camera()

    while not pr.window_should_close():
        update_camera_position(camera, movement_speed=0.5)
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)

        pr.begin_mode_3d(camera)
        
        # Calculer le centre de l'hélice et appliquer la transformation centrale
        num_turns = num_turns_ptr[0]
        spacing = spacing_between_turns_ptr[0]

        # Transformation du cube central
        central_translation = translation_matrix(translate_x_ptr[0], translate_y_ptr[0], translate_z_ptr[0])
        rotation_axis = Vector3(axis_x_ptr[0], axis_y_ptr[0], axis_z_ptr[0])
        central_rotation = rotation_matrix_homogeneous(rotation_axis, np.radians(rotation_angle_ptr[0]))
        central_transform = central_translation @ central_rotation

        # Dessiner les cubes le long de l'hélice
        num_turns = num_turns_ptr[0]
        num_cubes = int(num_turns * nb_cubes_ptr[0])
        scale_factor = 50.0
        spacing = spacing_between_turns_ptr[0]  # Récupérer la valeur dynamique de l'espacement


        for i in range(-num_cubes // 2, num_cubes // 2):
            t = i * (2 * np.pi * num_turns / num_cubes)
            x, y, z = type_courbe_manager(t, courbe_type_ptr[0], scale_factor=2)
            cube_translation = translation_matrix(x, y, z)

            # Rotation et mise à l'échelle
            time_angle = pr.get_time()
            angle_prog = time_angle+ t

            cube_rotation = rotation_matrix_homogeneous(Vector3(0, 1, 0), angle_prog)
            t_normal = (t + (num_turns * np.pi)) / (2 * num_turns * np.pi)
            prog_scale = cube_scale_ptr[0] * t_normal
            cube_scaling = uniform_scaling_matrix_homogeneous(prog_scale)

            # Combiner les transformations
            cube_transform = central_transform @ cube_translation @ cube_rotation @ cube_scaling
            apply_transformations_homogeneous(mesh, cube_transform, np.eye(4), np.eye(4), np.eye(4))
            draw_mesh(mesh)

        pr.end_mode_3d()

        # Contrôles GUI
        pr.draw_text("Translation X:", 10, 40, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 60, 200, 20), "-5.0", "5.0", translate_x_ptr, -5.0, 5.0)
        pr.draw_text("Translation Y:", 10, 90, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 110, 200, 20), "-5.0", "5.0", translate_y_ptr, -5.0, 5.0)
        pr.draw_text("Translation Z:", 10, 140, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 160, 200, 20), "-5.0", "5.0", translate_z_ptr, -5.0, 5.0)
        pr.draw_text("Axe de Rotation X:", 10, 190, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 210, 200, 20), "-1.0", "1.0", axis_x_ptr, -1.0, 1.0)
        pr.draw_text("Axe de Rotation Y:", 10, 240, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 260, 200, 20), "-1.0", "1.0", axis_y_ptr, -1.0, 1.0)
        pr.draw_text("Axe de Rotation Z:", 10, 290, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 310, 200, 20), "-1.0", "1.0", axis_z_ptr, -1.0, 1.0)
        pr.draw_text("Angle de Rotation:", 10, 340, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 360, 200, 20), "0", "360", rotation_angle_ptr, 0.0, 360.0)        
        pr.draw_text("Taille des Cubes:", 10, 460, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 480, 200, 20), "0.1", "3.0", cube_scale_ptr, 0.01, 1.0)
        pr.draw_text("Écartement des Tours:", 10, 520, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 540, 200, 20), "0.5", "5.0", spacing_between_turns_ptr, 0.5, 15.0)
        pr.draw_text("Nombre de cubes par tour:", 10, 560, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 580, 200, 20), "1", "50", nb_cubes_ptr, 1.0, 50.0)

        pr.draw_text("Type de Courbe:", 10, 620, 20, pr.BLACK)
        if pr.gui_button(pr.Rectangle(10, 650, 150, 30), "Noeud de Trèfle"):
            courbe_type_ptr[0] = 0
        if pr.gui_button(pr.Rectangle(170, 650, 150, 30), "Noeud en Huit"):
            courbe_type_ptr[0] = 1
        if pr.gui_button(pr.Rectangle(10, 690, 150, 30), "Noeud 4,3"):
            courbe_type_ptr[0] = 2
        if pr.gui_button(pr.Rectangle(170, 690, 150, 30), "Noeud Solomon"):
            courbe_type_ptr[0] = 3


        pr.end_drawing()

    pr.close_window()

if __name__ == "__main__":
    main()