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
    translation_matrix,
    shearing_matrix_homogeneous,
    scaling_matrix_homogeneous,
    orthographic_projection_matrix_homogeneous,
    perspective_projection_matrix,
)

def main():
    pr.init_window(1000, 900, "Cube central tournant avec cubes orbitaux")
    pr.set_target_fps(60)

    # Charger l'objet central
    mesh_file = "../cube.ply"  # Remplacez par le chemin réel vers votre fichier PLY
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
    scale_factor_ptr = pr.ffi.new('float *', 1.0)
    orbit_count_ptr = pr.ffi.new('float *', 5)
    orbit_radius_ptr = pr.ffi.new('float *', 5)
    projection_type_ptr = pr.ffi.new('float *', 0.0)
    distance_ptr = pr.ffi.new('float *', 1.0)

    # Créer une liste de cubes orbitaux avec toutes les clés nécessaires
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
            "clockwise": np.random.choice([True, False]),
            "scale": np.random.uniform(0.5, 1.5),
            "radius": np.random.uniform(orbit_radius_ptr[0] * 0.5, orbit_radius_ptr[0] * 1.5)
        })

    camera = initialize_camera()

    while not pr.window_should_close():
        update_camera_position(camera, movement_speed=0.1)
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)

        pr.begin_mode_3d(camera)

        # Transformation du cube central
        tx = translate_x_ptr[0]
        ty = translate_y_ptr[0]
        tz = translate_z_ptr[0]
        angle_central = np.radians(rotation_angle_ptr[0])
        central_translation = translation_matrix(tx, ty, tz)
        rotation_axis = Vector3(axis_x_ptr[0], axis_y_ptr[0], axis_z_ptr[0])
        rotation_centrale = rotation_matrix_homogeneous(rotation_axis, angle_central)
        scale_central = scaling_matrix_homogeneous(Vector3(1, 1, 1), scale_factor_ptr[0])

        central_transform = central_translation @ rotation_centrale @ scale_central

        if projection_type_ptr[0] == 0:
            projection_mat = orthographic_projection_matrix_homogeneous(Vector3(0, 0, 1))
        else:
            projection_mat = perspective_projection_matrix(distance_ptr[0])

        # Dessiner le cube central
        apply_transformations_homogeneous(mesh, central_transform, np.eye(4), np.eye(4), projection_mat)
        draw_mesh(mesh)

        # Dessiner les cubes orbitaux
        for i in range(round(orbit_count_ptr[0])):
            orbit = orbit_cubes[i]
            angle = pr.get_time() * (1 if orbit["clockwise"] else -1) + orbit["angle_offset"]
            orbit_rotation = rotation_matrix_homogeneous(orbit["rotation_axis"], angle)
            rayon_orbite = orbit["radius"]
            orbit_x = rayon_orbite * np.cos(angle)
            orbit_y = rayon_orbite * np.tan(orbit["inclination"])
            orbit_z = rayon_orbite * np.sin(angle)
            orbit_translation = translation_matrix(orbit_x, orbit_y, orbit_z)
            scale = np.eye(4)
            scale[0, 0] = orbit["scale"]
            scale[1, 1] = orbit["scale"]
            scale[2, 2] = orbit["scale"]

            orbit_transform = central_transform @ orbit_translation @ orbit_rotation @ scale
            apply_transformations_homogeneous(mesh, orbit_transform, np.eye(4), np.eye(4), np.eye(4))
            draw_mesh(mesh)

        # --- Ajout du plan sous le cube central ---
        # On dessine une grille sur le plan y = -5 pour visualiser la projection
        for x in range(-10, 11):
            start = Vector3(x, -5, -10)
            end = Vector3(x, -5, 10)
            pr.draw_line_3d(start, end, pr.DARKGRAY)
        for z in range(-10, 11):
            start = Vector3(-10, -5, z)
            end = Vector3(10, -5, z)
            pr.draw_line_3d(start, end, pr.DARKGRAY)
        # --- Fin ajout du plan ---

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
        pr.draw_text("Scale Central:", 10, 380, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 400, 200, 20), "0.5", "3.0", scale_factor_ptr, 0.5, 3.0)
        pr.draw_text("Cubes Orbitaux:", 10, 420, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 440, 200, 20), "0", "50", orbit_count_ptr, 0, max_orbits)
        pr.draw_text("Rayon d'Orbite:", 10, 460, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 480, 200, 20), "0", "10", orbit_radius_ptr, 0, 10)
        pr.draw_text("Mode de Projection (0: Orthographique, 1: Perspective):", 10, 500, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(10, 520, 200, 20), "0", "1", projection_type_ptr, 0, 1)
        if projection_type_ptr[0] == 1:
            pr.draw_text("Distance de Projection:", 10, 540, 20, pr.BLACK)
            pr.gui_slider_bar(pr.Rectangle(10, 560, 200, 20), "1.0", "8.0", distance_ptr, 1.0, 8.0)
        pr.end_drawing()

    pr.close_window()

if __name__ == "__main__":
    main()
