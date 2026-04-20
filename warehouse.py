import networkx as nx

def build_warehouse():
    G = nx.DiGraph()
    
    # 3 allées verticales espacées de 10m
    x_coords = [0, 10, 20]
    
    # 20 allées horizontales espacées de 2m (de y=0 à y=38)
    y_coords = [y * 2 for y in range(20)]
    
    # 1. Allées horizontales (Rayons de picking)
    # Sens de marche alterné une allée sur deux (serpentin)
    for i, y in enumerate(y_coords):
        if i % 2 == 0:
            # Sens Gauche -> Droite
            G.add_edge(f"0,{y}", f"10,{y}", weight=10)
            G.add_edge(f"10,{y}", f"20,{y}", weight=10)
        else:
            # Sens Droite -> Gauche
            G.add_edge(f"20,{y}", f"10,{y}", weight=10)
            G.add_edge(f"10,{y}", f"0,{y}", weight=10)
            
    # 2. Allées verticales (Allées de circulation)
    # Bidirectionnelles pour passer d'un rayon à l'autre
    for x in x_coords:
        for i in range(len(y_coords) - 1):
            y1 = y_coords[i]
            y2 = y_coords[i+1]
            # Bas vers le Haut
            G.add_edge(f"{x},{y1}", f"{x},{y2}", weight=2)
            # Haut vers le Bas
            G.add_edge(f"{x},{y2}", f"{x},{y1}", weight=2)
            
    return G

def get_real_distance(G, loc1, loc2):
    """
    Calcule la distance exacte sans découper les edges du graphe.
    """
    if loc1['type'] == 'edge' and loc2['type'] == 'edge':
        if loc1['u'] == loc2['u'] and loc1['v'] == loc2['v']:
            if loc1['pos'] <= loc2['pos']:
                return loc2['pos'] - loc1['pos']

    if loc1['type'] == 'node':
        sortie_loc1 = loc1['id']
        dist_sortie = 0
    else:
        sortie_loc1 = loc1['v']
        longueur = G.edges[loc1['u'], loc1['v']]['weight']
        dist_sortie = longueur - loc1['pos']

    if loc2['type'] == 'node':
        entree_loc2 = loc2['id']
        dist_entree = 0
    else:
        entree_loc2 = loc2['u']
        dist_entree = loc2['pos']

    try:
        dist_inter = nx.shortest_path_length(G, sortie_loc1, entree_loc2, weight='weight')
        return dist_sortie + dist_inter + dist_entree
    except nx.NetworkXNoPath:
        return float('inf')