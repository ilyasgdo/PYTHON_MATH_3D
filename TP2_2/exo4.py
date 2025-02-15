import pyray as pr
import numpy as np
from pyray import Vector3
import math

from  exo1 import ( cross_product,
                   dot_product,
                   vector_length,
                   vector_normalize)
"""
Bras humain rotatable avec contrôle de caméra

Ce script visualise un bras humain dans un espace 3D, permettant d'ajuster
les angles des articulations (épaule, coude, poignet) à l'aide de curseurs. 
Le bras conserve des contraintes réalistes sur les longueurs des segments 
et permet le contrôle de la caméra pour la navigation.

Modules utilisés :
- pyray (pr) : Pour le rendu et l'interaction
- numpy (np) : Pour les calculs matriciels
- math : Pour les opérations trigonométriques

"""

UPPER_ARM_LENGTH = 3  # Longueur du bras supérieur (de l'épaule au coude)
FOREARM_LENGTH = 1.5    # Longueur de l'avant-bras (du coude au poignet)
FINGER_LENGTH = 1           # Longueur des doigts


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

def rotation_matrix_yaw_pitch_roll(yaw, pitch, roll):
    """Generate a rotation matrix from yaw, pitch, and roll."""
    # Convert degrees to radians
    yaw = math.radians(yaw)  # Rotation around Z-axis
    pitch = math.radians(pitch)  # Rotation around Y-axis
    roll = math.radians(roll)  # Rotation around X-axis

    # Precompute sin and cos values
    cos_yaw, sin_yaw = math.cos(yaw), math.sin(yaw)
    cos_pitch, sin_pitch = math.cos(pitch), math.sin(pitch)
    cos_roll, sin_roll = math.cos(roll), math.sin(roll)

    Rz = np.array([
        [cos_yaw, -sin_yaw, 0, 0],
        [sin_yaw, cos_yaw, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    Ry = np.array([
        [cos_pitch, 0, sin_pitch, 0],
        [0, 1, 0, 0],
        [-sin_pitch, 0, cos_pitch, 0],
        [0, 0, 0, 1]
    ])

    Rx = np.array([
        [1, 0, 0, 0],
        [0, cos_roll, -sin_roll, 0],
        [0, sin_roll, cos_roll, 0],
        [0, 0, 0, 1]
    ])
    
    # Combine the rotations in order: Rz * Ry * Rx
    return Rz @ Ry @ Rx

def apply_rotation(point, matrix):
    """
    Applique une matrice de rotation à un point 3D.

    Paramètres :
    - point (Vector3) : Le point 3D à faire pivoter.
    - matrix (np.ndarray) : Une matrice de rotation 4x4.

    Retourne :
    - Vector3 : Le point 3D après la rotation.
    """
    # Convertir le point en coordonnées homogènes
    point_homogeneous = np.array([point.x, point.y, point.z, 1])
    # Appliquer la matrice de rotation avec une multiplication matricielle
    rotated_point_homogeneous = matrix @ point_homogeneous
    # Convertir le point tourné en un Vector3
    rotated_point = Vector3(rotated_point_homogeneous[0], rotated_point_homogeneous[1], rotated_point_homogeneous[2])
    return rotated_point





def vector_add(v1, v2):
    """
    Retourne la somme de deux vecteurs.

    Paramètres :
    - v1 (Vector3) : Le premier vecteur.
    - v2 (Vector3) : Le second vecteur.

    Retourne :
    - Vector3 : Un nouveau vecteur représentant la somme de v1 et v2.
    """
    return Vector3(v1.x+v2.x,v1.y+v2.y,v1.z+v2.z)

def vector_subtract(v1, v2):
    """
    Retourne la différence entre deux vecteurs.

    Paramètres :
    - v1 (Vector3) : Le premier vecteur.
    - v2 (Vector3) : Le second vecteur.

    Retourne :
    - Vector3 : Un nouveau vecteur représentant la différence entre v1 et v2.
    """
    return Vector3(v1.x-v2.x,v1.y-v2.y,v1.z-v2.z)

def vector_multiply_scalar(v, scalar):
    """
    Multiplie un vecteur par un scalaire.

    Paramètres :
    - v (Vector3) : Le vecteur à multiplier.
    - scalar (float) : Le scalaire par lequel multiplier.

    Retourne :
    - Vector3 : Un nouveau vecteur représentant le produit du vecteur v et du scalaire.
    """
    return Vector3(1, 1, 1)


def apply_transformation_to_segment(position, rotation_matrix, reference_position, parent_transformation):
    """
    Applique une rotation et une translation à un segment à l'aide de matrices 4x4, tout en conservant la distance (longueur du segment).

    Paramètres :
    - position (Vector3) : La position actuelle du segment à transformer.
    - rotation_matrix (np.ndarray) : Une matrice 4x4 représentant la rotation à appliquer.
    - reference_position (Vector3) : La position de référence utilisée pour l'origine de la transformation.
    - parent_transformation (np.ndarray) : La matrice de transformation cumulative du segment parent.

    Étapes du processus :
    1. Création des matrices de translation pour déplacer le point de référence à l'origine et revenir à sa position initiale.
    2. Combinaison des transformations (parent, rotation, translation) en une matrice unique.
    3. Conversion de la position en coordonnées homogènes (ajout d'une composante "w" pour les calculs matriciels).
    4. Application de la transformation à la position.
    5. Conversion de la position transformée en un nouvel objet Vector3.

    Retourne :
    - Vector3 : La nouvelle position du segment après transformation.
    - np.ndarray : La matrice de transformation complète appliquée au segment.
    """
    
    # Étape 1 : Créer les matrices de translation pour déplacer la référence à l'origine
    T_to_origin = np.array([
        [1, 0, 0, -reference_position.x],
        [0, 1, 0, -reference_position.y],
        [0, 0, 1, -reference_position.z],
        [0, 0, 0, 1]
    ])

    # Étape 2 : Matrice de translation inverse pour revenir de l'origine
    T_from_origin = np.array([
        [1, 0, 0, reference_position.x],
        [0, 1, 0, reference_position.y],
        [0, 0, 1, reference_position.z],
        [0, 0, 0, 1]
    ])
    # Étape 3 : Combiner les transformations en une seule matrice
    transformation_matrix = parent_transformation @ T_from_origin @ rotation_matrix @ T_to_origin

    # Étape 4 : Convertir la position en coordonnées homogènes
    position_homogeneous = np.array([position.x, position.y, position.z, 1])

    # Étape 5 : Appliquer la transformation
    new_position_homogeneous = transformation_matrix @ position_homogeneous

    # Étape 6 : Convertir en Vector3
    new_position = Vector3(
        new_position_homogeneous[0],
        new_position_homogeneous[1],
        new_position_homogeneous[2]
    )

    return new_position, transformation_matrix


def calculate_fingers_positions(wrist, wrist_rotation, FINGER_LENGTH):
    """
    Calcule les positions des doigts par rapport au poignet.

    Paramètres :
    - wrist (Vector3) : La position globale du poignet.
    - wrist_rotation (np.ndarray) : Une matrice 4x4 représentant la rotation appliquée au poignet.
    - FINGER_LENGTH (float) : La longueur de chaque doigt.

    Étapes :
    1. Détermine les positions locales de la base et de l'extrémité de chaque doigt par rapport au poignet.
    2. Applique la rotation locale pour aligner les doigts avec l'orientation actuelle du poignet.
    3. Convertit les positions locales en positions globales par addition avec la position globale du poignet.
    4. Stocke les paires (base du doigt, extrémité du doigt) dans une liste.

    Retourne :
    - list of tuple(Vector3, Vector3) : Une liste de paires (position globale de la base, position globale de l'extrémité) pour chaque doigt.
    """
    finger_positions = []
    for i in range(-1, 2):  # Index pour le décalage des doigts
        finger_base_local = Vector3(i * 0.2, -0.4, 0)  # Position locale de la base par rapport au poignet
        finger_tip_local = Vector3(i * 0.2, -0.4 - FINGER_LENGTH, 0)  # Position locale de l'extrémité par rapport au poignet

        # Rotation des positions locales pour s'aligner avec le poignet
        rotated_finger_base = apply_rotation(finger_base_local, wrist_rotation)
        rotated_finger_tip = apply_rotation(finger_tip_local, wrist_rotation)

        # Conversion des positions locales en positions globales
        finger_base_global = vector_add(wrist, rotated_finger_base)
        finger_tip_global = vector_add(wrist, rotated_finger_tip)

        finger_positions.append((finger_base_global, finger_tip_global))

    return finger_positions

def draw_human_arm(shoulder, elbow, wrist, finger_positions):
    """
    Dessine un bras humain réaliste avec des positions transformées.

    Paramètres :
    - shoulder (Vector3) : La position de l'épaule.
    - elbow (Vector3) : La position du coude.
    - wrist (Vector3) : La position du poignet.
    - finger_positions (list of tuple(Vector3, Vector3)) : Les positions globales des doigts, 
      définies par des paires (base, extrémité) pour chaque doigt.

    Description :
    1. Dessine l'épaule, le coude, l'avant-bras et le poignet à l'aide de sphères et de cylindres.
    2. Dessine chaque doigt à l'aide des positions globales fournies.
    """
    pr.draw_sphere(shoulder, 0.6, pr.RED)  # Épaule
    pr.draw_cylinder_ex(shoulder, elbow, 0.25, 0.25, 8, pr.BLUE)  # Bras supérieur
    pr.draw_sphere(elbow, 0.5, pr.RED)  # Coude
    pr.draw_cylinder_ex(elbow, wrist, 0.2, 0.2, 8, pr.BLUE)  # Avant-bras
    pr.draw_sphere(wrist, 0.4, pr.RED)  # Poignet

    # Dessiner les doigts
    for finger_base_global, finger_tip_global in finger_positions:
        pr.draw_sphere(finger_base_global, 0.1, pr.GREEN)  # Base du doigt
        pr.draw_cylinder_ex(finger_base_global, finger_tip_global, 0.05, 0.05, 8, pr.YELLOW)  # Segment du doigt


def draw_slider_with_label(label, x_label, x_slider, y, ptr, min_val, max_val, padding=10):
    """
    Dessine un curseur avec une étiquette à sa gauche, avec un espacement horizontal configurable.

    Paramètres :
    - label (str) : Le texte de l'étiquette à dessiner (par exemple, "Yaw").
    - x_label (int) : La position X de l'étiquette.
    - x_slider (int) : La position X du curseur.
    - y (int) : La position Y commune pour l'étiquette et le curseur.
    - ptr (float *) : Pointeur vers la valeur contrôlée par le curseur.
    - min_val (float) : Valeur minimale du curseur.
    - max_val (float) : Valeur maximale du curseur.
    - padding (int, optionnel) : Espacement horizontal entre l'étiquette et le curseur (par défaut : 10).

    Description :
    - Dessine une étiquette alignée verticalement avec le curseur.
    - Positionne le curseur à côté de l'étiquette, en tenant compte de l'espacement.

    """
    pr.draw_text(label, x_label, y + 4, 20, pr.BLACK)  # Ajustement pour l'alignement du texte
    pr.gui_slider_bar(pr.Rectangle(x_slider + padding, y, 200, 20), str(min_val), str(max_val), ptr, min_val, max_val)


def draw_sliders_with_labels(base_x_label, base_x_slider, base_y, spacing, yaw_ptr, pitch_ptr, roll_ptr):
    """
    Dessine des curseurs pour les angles de lacet, tangage et roulis, avec des étiquettes et un espacement configurables.

    Paramètres :
    - base_x_label (int) : Position X des étiquettes.
    - base_x_slider (int) : Position X des curseurs.
    - base_y (int) : Position Y de départ pour le premier curseur.
    - spacing (int) : Espacement vertical entre les curseurs.
    - yaw_ptr (float *) : Pointeur vers la valeur du lacet.
    - pitch_ptr (float *) : Pointeur vers la valeur du tangage.
    - roll_ptr (float *) : Pointeur vers la valeur du roulis.

    Description :
    - Dessine trois curseurs verticaux avec des étiquettes correspondant aux angles de rotation.
    - Utilise la fonction `draw_slider_with_label` pour placer chaque curseur avec une étiquette et un espacement.

    Notes :
    - Les curseurs permettent de contrôler les valeurs dans la plage [-180, 180].
    - L'espacement entre les curseurs peut être ajusté en modifiant le paramètre `spacing`.
    """
    padding = 15  # Vous pouvez ajuster cet espacement si nécessaire
    draw_slider_with_label("Yaw", base_x_label, base_x_slider, base_y, yaw_ptr, -180, 180, padding)
    draw_slider_with_label("Pitch", base_x_label, base_x_slider, base_y + spacing, pitch_ptr, -180, 180, padding)
    draw_slider_with_label("Roll", base_x_label, base_x_slider, base_y + 2 * spacing, roll_ptr, -180, 180, padding)


def main():
    """
    Fonction principale pour visualiser un bras humain rotatable avec contrôle de caméra et curseurs.

    Description :
    - Initialise une fenêtre graphique et une caméra 3D.
    - Définit des curseurs pour ajuster les angles de rotation des articulations (épaule, coude, poignet).
    - Met à jour la position de la caméra et applique les transformations aux segments du bras.
    - Dessine le bras humain dans un espace 3D avec des positions transformées.

    Notes :
    - La longueur des segments est vérifiée à chaque étape pour garantir leur cohérence.
    - Les curseurs permettent de modifier les angles de rotation dans la plage [-180, 180].

    Aucune entrée.
    Aucune sortie.
    """
    
    # Largeur de la fenêtre
    window_width = 1200
    slider_width = 200
    margin = 20
    
    pr.init_window(1200, 800, "Bras Humain Rotatable avec Caméra")  # Initialisation de la fenêtre
    camera = initialize_camera()  # Initialisation de la caméra
    pr.set_target_fps(60)  # Fixe le nombre d'images par seconde à 60

    # Curseurs pour les angles de rotation (lacet, tangage, roulis) de chaque articulation
    shoulder_yaw_ptr = pr.ffi.new('float *', 0.0)  # Épaule (lacet)
    shoulder_pitch_ptr = pr.ffi.new('float *', 0.0)  # Épaule (tangage)
    shoulder_roll_ptr = pr.ffi.new('float *', 0.0)  # Épaule (roulis)

    elbow_yaw_ptr = pr.ffi.new('float *', 0.0)  # Coude (lacet)
    elbow_pitch_ptr = pr.ffi.new('float *', 0.0)  # Coude (tangage)
    elbow_roll_ptr = pr.ffi.new('float *', 0.0)  # Coude (roulis)

    wrist_yaw_ptr = pr.ffi.new('float *', 0.0)  # Poignet (lacet)
    wrist_pitch_ptr = pr.ffi.new('float *', 0.0)  # Poignet (tangage)
    wrist_roll_ptr = pr.ffi.new('float *', 0.0)  # Poignet (roulis)

    while not pr.window_should_close():  # Boucle principale
        # Mise à jour de la position de la caméra
        update_camera_position(camera, 0.2)

        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)  # Nettoie l'écran avec une couleur blanche
        pr.begin_mode_3d(camera)  # Active le mode 3D

        # Positions initiales des articulations
        shoulder = Vector3(0, 3, 0)  # Position de l'épaule
        elbow = vector_add(shoulder, Vector3(0, -UPPER_ARM_LENGTH, 0))  # Position du coude
        wrist = vector_add(elbow, Vector3(0, -FOREARM_LENGTH, 0))  # Position du poignet

        # Calcul des rotations pour chaque articulation
        shoulder_rotation = rotation_matrix_yaw_pitch_roll(
            shoulder_yaw_ptr[0], shoulder_pitch_ptr[0], shoulder_roll_ptr[0]
        )
        elbow_rotation = rotation_matrix_yaw_pitch_roll(
            elbow_yaw_ptr[0], elbow_pitch_ptr[0], elbow_roll_ptr[0]
        )
        wrist_rotation = rotation_matrix_yaw_pitch_roll(
            wrist_yaw_ptr[0], wrist_pitch_ptr[0], wrist_roll_ptr[0]
        )

        # Appliquer les rotations pour déterminer les nouvelles positions des articulations
        parent_transformation = np.eye(4)  # Transformation initiale
        elbow_rotated, elbow_transformation = apply_transformation_to_segment(
            elbow, shoulder_rotation, shoulder, parent_transformation)
        
        wrist_rotated, wrist_transformation = apply_transformation_to_segment(
            wrist, elbow_rotation, elbow, elbow_transformation)

        # Vérifications de la longueur des segments
        
        
        shoulder_to_elbow_length = vector_length(vector_subtract(elbow_rotated, shoulder))
        assert abs(shoulder_to_elbow_length - UPPER_ARM_LENGTH) < 1e-6, \
            f"Longueur attendue entre l'épaule et le coude : {UPPER_ARM_LENGTH}, obtenu : {shoulder_to_elbow_length}"
        
        elbow_to_wrist_length = vector_length(vector_subtract(wrist_rotated, elbow_rotated))
        assert abs(elbow_to_wrist_length - FOREARM_LENGTH) < 1e-6, \
            f"Longueur attendue entre le coude et le poignet : {FOREARM_LENGTH}, obtenu : {elbow_to_wrist_length}"

        # Calcul des positions des doigts
        finger_positions = calculate_fingers_positions(wrist_rotated, wrist_rotation, FINGER_LENGTH)

        # Dessin du bras humain
        draw_human_arm(shoulder, elbow_rotated, wrist_rotated, finger_positions)

        pr.end_mode_3d()

        # Dessiner les curseurs pour contrôler les rotations des articulations

        # Calculer les positions
        base_x_label = window_width - slider_width - margin - 50  # 50 représente la largeur estimée de l'étiquette
        base_x_slider = window_width - slider_width - margin

        # Mettre à jour les appels de fonctions
        pr.draw_text("Rotation de l'épaule :", base_x_label, 80, 20, pr.BLACK)
        draw_sliders_with_labels(base_x_label, base_x_slider, 110, 30, shoulder_yaw_ptr, shoulder_pitch_ptr, shoulder_roll_ptr)

        pr.draw_text("Rotation du coude :", base_x_label, 200, 20, pr.BLACK)
        draw_sliders_with_labels(base_x_label, base_x_slider, 230, 30, elbow_yaw_ptr, elbow_pitch_ptr, elbow_roll_ptr)

        pr.draw_text("Rotation du poignet :", base_x_label, 320, 20, pr.BLACK)
        draw_sliders_with_labels(base_x_label, base_x_slider, 350, 30, wrist_yaw_ptr, wrist_pitch_ptr, wrist_roll_ptr)

        pr.end_drawing()

    pr.close_window()  # Ferme la fenêtre graphique



if __name__ == "__main__":
    main()