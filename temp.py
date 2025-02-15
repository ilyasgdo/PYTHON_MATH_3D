import pyray as pr
import numpy as np
from pyray import Vector3
import math

UPPER_ARM_LENGTH = 3
FOREARM_LENGTH = 1.5
FINGER_LENGTH = 1


def initialize_camera():
    camera = pr.Camera3D(
        Vector3(0, 10, 10),
        Vector3(0, 0, 0),
        Vector3(0, 1, 0),
        45,
        pr.CAMERA_PERSPECTIVE
    )
    return camera


def update_camera_position(camera, movement_speed):
    if pr.is_key_down(pr.KEY_W): camera.position.z -= movement_speed
    if pr.is_key_down(pr.KEY_S): camera.position.z += movement_speed
    if pr.is_key_down(pr.KEY_A): camera.position.x -= movement_speed
    if pr.is_key_down(pr.KEY_D): camera.position.x += movement_speed
    if pr.is_key_down(pr.KEY_Q): camera.position.y += movement_speed
    if pr.is_key_down(pr.KEY_E): camera.position.y -= movement_speed


def rotation_matrix_yaw_pitch_roll(yaw, pitch, roll):
    yaw = math.radians(yaw)
    pitch = math.radians(pitch)
    roll = math.radians(roll)

    cos_z, sin_z = math.cos(yaw), math.sin(yaw)
    cos_y, sin_y = math.cos(pitch), math.sin(pitch)
    cos_x, sin_x = math.cos(roll), math.sin(roll)

    Rz = np.array([
        [cos_z, -sin_z, 0, 0],
        [sin_z, cos_z, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    Ry = np.array([
        [cos_y, 0, sin_y, 0],
        [0, 1, 0, 0],
        [-sin_y, 0, cos_y, 0],
        [0, 0, 0, 1]
    ])

    Rx = np.array([
        [1, 0, 0, 0],
        [0, cos_x, -sin_x, 0],
        [0, sin_x, cos_x, 0],
        [0, 0, 0, 1]
    ])

    return Rz @ Ry @ Rx


def apply_rotation(point, matrix):
    point_homogeneous = np.array([point.x, point.y, point.z, 1])
    rotated = matrix @ point_homogeneous
    return Vector3(rotated[0], rotated[1], rotated[2])


def dot_product(A, B):
    return A.x * B.x + A.y * B.y + A.z * B.z


def vector_length(vector):
    return math.sqrt(dot_product(vector, vector))


def vector_add(v1, v2):
    return Vector3(v1.x + v2.x, v1.y + v2.y, v1.z + v2.z)


def vector_subtract(v1, v2):
    return Vector3(v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)


def vector_multiply_scalar(v, scalar):
    return Vector3(v.x * scalar, v.y * scalar, v.z * scalar)


def apply_transformation_to_segment(position, rotation_matrix, reference_position, parent_transformation):
    # Translation vers l'origine
    T_to_origin = np.array([
        [1, 0, 0, -reference_position.x],
        [0, 1, 0, -reference_position.y],
        [0, 0, 1, -reference_position.z],
        [0, 0, 0, 1]
    ])

    # Translation inverse
    T_from_origin = np.array([
        [1, 0, 0, reference_position.x],
        [0, 1, 0, reference_position.y],
        [0, 0, 1, reference_position.z],
        [0, 0, 0, 1]
    ])

    transformation_matrix = parent_transformation @ T_from_origin @ rotation_matrix @ T_to_origin
    pos_homogeneous = np.array([position.x, position.y, position.z, 1])
    new_pos = transformation_matrix @ pos_homogeneous

    return Vector3(new_pos[0], new_pos[1], new_pos[2]), transformation_matrix


def calculate_fingers_positions(wrist, wrist_rotation, FINGER_LENGTH):
    finger_positions = []
    for i in range(-1, 2):
        # Positions locales des doigts
        finger_base = Vector3(i * 0.3, -0.4, 0)
        finger_tip = Vector3(i * 0.3, -0.4 - FINGER_LENGTH, 0)

        # Application de la rotation
        rotated_base = apply_rotation(finger_base, wrist_rotation)
        rotated_tip = apply_rotation(finger_tip, wrist_rotation)

        # Positions globales
        global_base = vector_add(wrist, rotated_base)
        global_tip = vector_add(wrist, rotated_tip)

        finger_positions.append((global_base, global_tip))
    return finger_positions


def draw_human_arm(shoulder, elbow, wrist, fingers):
    # Dessin du bras
    pr.draw_sphere(shoulder, 0.6, pr.RED)
    pr.draw_cylinder_ex(shoulder, elbow, 0.25, 0.25, 8, pr.BLUE)
    pr.draw_sphere(elbow, 0.5, pr.RED)
    pr.draw_cylinder_ex(elbow, wrist, 0.2, 0.2, 8, pr.BLUE)
    pr.draw_sphere(wrist, 0.4, pr.RED)

    # Dessin des doigts
    for base, tip in fingers:
        pr.draw_sphere(base, 0.1, pr.GREEN)
        pr.draw_cylinder_ex(base, tip, 0.05, 0.05, 8, pr.YELLOW)


def draw_slider_with_label(label, x_label, x_slider, y, ptr, min_val, max_val):
    pr.draw_text(label, x_label, y + 4, 20, pr.BLACK)
    pr.gui_slider_bar(pr.Rectangle(x_slider, y, 200, 20), str(min_val), str(max_val), ptr, min_val, max_val)


def draw_sliders(base_x_label, base_x_slider, base_y, spacing, yaw, pitch, roll):
    draw_slider_with_label("Yaw", base_x_label, base_x_slider, base_y, yaw, -180, 180)
    draw_slider_with_label("Pitch", base_x_label, base_x_slider, base_y + spacing, pitch, -180, 180)
    draw_slider_with_label("Roll", base_x_label, base_x_slider, base_y + 2 * spacing, roll, -180, 180)


def main():
    pr.init_window(1200, 800, "Bras Humain 3D avec Contrôles")
    camera = initialize_camera()
    pr.set_target_fps(60)

    # Initialisation des curseurs
    shoulder_yaw = pr.ffi.new('float *', 0.0)
    shoulder_pitch = pr.ffi.new('float *', 0.0)
    shoulder_roll = pr.ffi.new('float *', 0.0)

    elbow_yaw = pr.ffi.new('float *', 0.0)
    elbow_pitch = pr.ffi.new('float *', 0.0)
    elbow_roll = pr.ffi.new('float *', 0.0)

    wrist_yaw = pr.ffi.new('float *', 0.0)
    wrist_pitch = pr.ffi.new('float *', 0.0)
    wrist_roll = pr.ffi.new('float *', 0.0)

    while not pr.window_should_close():
        update_camera_position(camera, 0.2)

        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)
        pr.begin_mode_3d(camera)

        # Positions initiales
        shoulder = Vector3(0, 3, 0)
        elbow = vector_add(shoulder, Vector3(0, -UPPER_ARM_LENGTH, 0))
        wrist = vector_add(elbow, Vector3(0, -FOREARM_LENGTH, 0))

        # Calcul des rotations
        shoulder_rot = rotation_matrix_yaw_pitch_roll(shoulder_yaw[0], shoulder_pitch[0], shoulder_roll[0])
        elbow_rot = rotation_matrix_yaw_pitch_roll(elbow_yaw[0], elbow_pitch[0], elbow_roll[0])
        wrist_rot = rotation_matrix_yaw_pitch_roll(wrist_yaw[0], wrist_pitch[0], wrist_roll[0])

        # Application des transformations
        parent = np.eye(4)
        new_elbow, elbow_transform = apply_transformation_to_segment(elbow, shoulder_rot, shoulder, parent)
        new_wrist, wrist_transform = apply_transformation_to_segment(wrist, elbow_rot, new_elbow, elbow_transform)

        # Vérification des longueurs
        assert abs(vector_length(vector_subtract(new_elbow, shoulder)) - UPPER_ARM_LENGTH) < 0.01
        assert abs(vector_length(vector_subtract(new_wrist, new_elbow)) - FOREARM_LENGTH) < 0.01

        # Calcul des doigts
        fingers = calculate_fingers_positions(new_wrist, wrist_rot, FINGER_LENGTH)

        # Dessin
        draw_human_arm(shoulder, new_elbow, new_wrist, fingers)
        pr.end_mode_3d()

        # Interface
        slider_x = 1200 - 250
        pr.draw_text("ÉPAULE", slider_x - 100, 20, 20, pr.BLACK)
        draw_sliders(slider_x - 100, slider_x, 40, 40, shoulder_yaw, shoulder_pitch, shoulder_roll)

        pr.draw_text("COUDE", slider_x - 100, 180, 20, pr.BLACK)
        draw_sliders(slider_x - 100, slider_x, 200, 40, elbow_yaw, elbow_pitch, elbow_roll)

        pr.draw_text("POIGNET", slider_x - 100, 340, 20, pr.BLACK)
        draw_sliders(slider_x - 100, slider_x, 360, 40, wrist_yaw, wrist_pitch, wrist_roll)

        pr.end_drawing()

    pr.close_window()


if __name__ == "__main__":
    main()