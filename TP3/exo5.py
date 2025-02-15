import trimesh

def euler_dot_carre(mesh):
   
    V = len(mesh.vertices)  # Nb de sommets 
    E = len(mesh.edges_unique)  # Nb aretes uniques
    F = len(mesh.faces)  # Nb faces
    return V - E + F

def genre(mesh):

    euler = euler_dot_carre(mesh)
    nb_connexes = len(mesh.split())  
    g = (2 - euler - 2 * nb_connexes) // 2

    return g

liste_maillage = ["dolphin.ply", "cube.ply"]

for maillage in liste_maillage:
    mesh = trimesh.load_mesh(maillage)
    print("\n\n")
    print(f"'Euler Point-Carre pour {maillage} : {euler_dot_carre(mesh)}")
    print(f"type de maillage pour {maillage} : {genre(mesh)}")



