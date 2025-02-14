import pyray as pr
import numpy as np
from pyray import Vector3

# Importer les fonctions et utilitaires existants
from tp3_exo1 import (
    initialize_camera,
    update_camera_position,
    load_ply_file,
    initialize_mesh_for_transforming,
    apply_transformations_homogeneous,
    draw_mesh,
    rotation_matrix_homogeneous,
    translation_matrix
)


def main():
    pr.init_window(1000, 900, "Cube central tournant avec cubes orbitaux")
    pr.set_target_fps(60)

    # Charger l'objet central
    mesh_file = "cube.ply"  # Remplacez par le chemin réel vers votre fichier PLY
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
    orbit_count_ptr = pr.ffi.new('float *', 5)
    orbit_radius_ptr = pr.ffi.new('float *', 5)
    cubes_per_turn_ptr = pr.ffi.new('float *', 5.0)  # 5 cubes par tour par défaut

    # Créer une liste de cubes orbitaux
    # TODO : expliquer tous les différents paramètres (e.g., inclination)
    max_orbits = 50
    orbit_cubes = []
    for _ in range(max_orbits):
        orbit_cubes.append({
            "transform": np.eye(4),
            "angle_offset": np.random.uniform(0, 2 * np.pi),
            "inclination": np.random.uniform(-np.pi / 4, np.pi / 4),
            "rotation_axis": Vector3(
                np.random.uniform(-1, 1),
                np.random.uniform(-1, 1),
                np.random.uniform(-1, 1)
            ),
            "clockwise": np.random.choice([True, False])  # Rotation aléatoire (horaire ou antihoraire)
        })

    camera = initialize_camera()

    while not pr.window_should_close():
        update_camera_position(camera, movement_speed=0.1)
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)

        pr.begin_mode_3d(camera)

        # Transformation du cube central
        # TODO : construit une matrice représentant la transformation du cube central
        central_translation = np.eye(4)
        rotation_axis = Vector3(0, 0, 0)
        central_rotation = np.eye(4)
        central_transform = np.eye(4)

        # Dessiner le cube central
        apply_transformations_homogeneous(mesh, central_transform, np.eye(4), np.eye(4), np.eye(4))
        draw_mesh(mesh)

        # Dessiner les cubes orbitaux
        for i in range(round(orbit_count_ptr[0])):
            orbit = orbit_cubes[i]
            # Calcul de l'angle avec espacement régulier basé sur le nombre de cubes par tour
            angle = pr.get_time() * (1 if orbit["clockwise"] else -1) + (i * 2 * np.pi / cubes_per_turn_ptr[0])

            # Rotation autour de l'axe du cube
            orbit_rotation = rotation_matrix_homogeneous(orbit["rotation_axis"], angle)

            # Transformation du cube orbital relative au cube central
            """ Le mouvement se déroule principalement dans le plan xz, tandis 
            que la coordonnée y introduit une inclinaison pour donner l'impression 
            que l'orbite est inclinée dans l'espace 3D."""
            # TODO
            orbit_x = 0 * orbit_radius_ptr[0]
            orbit_y = 0 * orbit_radius_ptr[0]
            orbit_z = 0 * orbit_radius_ptr[0]
            orbit_translation = np.eye(4)

            orbit_transform = np.eye(4)
            apply_transformations_homogeneous(mesh, orbit_transform, np.eye(4), np.eye(4), np.eye(4))
            draw_mesh(mesh)

        pr.end_mode_3d()

        # Contrôles GUI
        pr.draw_text("Contrôles du Cube Central", 10, 10, 20, pr.BLACK)
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
        pr.draw_text("Cubes Orbitaux:", 10, 400, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 420, 200, 20), "0", "50", orbit_count_ptr, 0, max_orbits)
        pr.draw_text("Rayon d'Orbite:", 10, 440, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 460, 200, 20), "0", "10", orbit_radius_ptr, 0, 10)
        pr.draw_text("Cubes par Tour:", 10, 480, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 500, 200, 20), "1", "20", cubes_per_turn_ptr, 1, 20)

        pr.end_drawing()

    pr.close_window()


if __name__ == "__main__":
    main()