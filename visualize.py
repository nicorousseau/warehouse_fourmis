import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import FancyArrowPatch
import networkx as nx
import math

def get_coords(node_str):
    """Convertit l'ID du noeud en tuple d'entiers."""
    return tuple(map(int, node_str.split(',')))

def get_exact_position(loc):
    """Calcule les coordonnées exactes (x, y) d'un point."""
    if loc['type'] == 'node':
        return get_coords(loc['id'])
    else:
        u_coords = get_coords(loc['u'])
        v_coords = get_coords(loc['v'])
        pos = loc['pos']
        
        L = math.hypot(v_coords[0] - u_coords[0], v_coords[1] - u_coords[1])
        ratio = pos / L if L > 0 else 0
        
        px = u_coords[0] + ratio * (v_coords[0] - u_coords[0])
        py = u_coords[1] + ratio * (v_coords[1] - u_coords[1])
        return (px, py)

def get_path_coordinates(G, loc1, loc2):
    """Récupère tous les points (x,y) du chemin physique entre loc1 et loc2."""
    coords = []
    coords.append(get_exact_position(loc1))

    if loc1['type'] == 'edge' and loc2['type'] == 'edge':
        if loc1['u'] == loc2['u'] and loc1['v'] == loc2['v']:
            if loc1['pos'] <= loc2['pos']:
                coords.append(get_exact_position(loc2))
                return coords

    if loc1['type'] == 'node':
        sortie_loc1 = loc1['id']
    else:
        sortie_loc1 = loc1['v']
        coords.append(get_coords(sortie_loc1)) 

    if loc2['type'] == 'node':
        entree_loc2 = loc2['id']
    else:
        entree_loc2 = loc2['u']

    try:
        if sortie_loc1 != entree_loc2:
            path_nodes = nx.shortest_path(G, source=sortie_loc1, target=entree_loc2, weight='weight')
            for node in path_nodes:
                coords.append(get_coords(node))
        else:
            coords.append(get_coords(sortie_loc1))
    except nx.NetworkXNoPath:
        pass 

    coords.append(get_exact_position(loc2))
    return coords

def plot_warehouse_path(G, sequence_finale):
    fig, ax = plt.subplots(figsize=(12, 9))
    
    # 1. Structure de l'entrepôt
    pos_nodes = {node: get_coords(node) for node in G.nodes()}
    nx.draw_networkx_edges(G, pos_nodes, ax=ax, edge_color='lightgray', arrows=True, arrowsize=15, width=2)
    nx.draw_networkx_nodes(G, pos_nodes, ax=ax, node_color='lightgray', node_size=50)
    
    # 2. Dessiner le chemin avec dégradé et flèches
    if sequence_finale and len(sequence_finale) > 1:
        n_etapes = len(sequence_finale) - 1
        cmap = cm.plasma # Choix du dégradé (plasma = violet -> rose -> jaune)
        
        for i in range(n_etapes):
            loc1 = sequence_finale[i]['loc']
            loc2 = sequence_finale[i+1]['loc']
            
            segment_coords = get_path_coordinates(G, loc1, loc2)
            # Calcul de la couleur en fonction de l'avancement
            color = cmap(i / max(1, n_etapes - 1)) 
            
            if len(segment_coords) > 1:
                # Tracer la ligne de l'étape en cours
                xs, ys = zip(*segment_coords)
                ax.plot(xs, ys, color=color, linestyle='-', linewidth=2.5, zorder=2)
                
                # Ajouter une flèche au milieu de chaque sous-segment
                for j in range(len(segment_coords) - 1):
                    x1, y1 = segment_coords[j]
                    x2, y2 = segment_coords[j+1]
                    
                    dx = x2 - x1
                    dy = y2 - y1
                    length = math.hypot(dx, dy)
                    
                    if length > 1.0: # Ignorer les tout petits ajustements
                        dir_x = dx / length
                        dir_y = dy / length
                        mid_x = x1 + dx / 2
                        mid_y = y1 + dy / 2
                        
                        arrow_len = 1.5 # Taille fixe pour la flèche
                        arrow = FancyArrowPatch((mid_x - dir_x*arrow_len, mid_y - dir_y*arrow_len), 
                                                (mid_x + dir_x*arrow_len, mid_y + dir_y*arrow_len), 
                                                arrowstyle='-|>', mutation_scale=20, 
                                                color=color, zorder=3)
                        ax.add_patch(arrow)

        # Ajouter une barre de couleur (légende du dégradé)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=n_etapes))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Évolution du parcours (Ordre des étapes)')

    # 3. Placer les marqueurs (Dépôt et Produits)
    if sequence_finale:
        points_coords = [get_exact_position(etape['loc']) for etape in sequence_finale]
        xs_p, ys_p = zip(*points_coords)
        
        ax.plot(xs_p[0], ys_p[0], marker='s', color='green', markersize=14, label='Dépôt', linestyle='None', zorder=5)
        
        for etape, (x, y) in zip(sequence_finale[1:], points_coords[1:]):
            prod_id = etape['id_produit']
            ax.plot(x, y, marker='*', color='red', markersize=12, linestyle='None', zorder=5)
            ax.annotate(f"P{prod_id}", (x, y), textcoords="offset points", xytext=(0, 10), 
                        ha='center', fontsize=10, color='darkred', fontweight='bold', zorder=6)

    ax.set_title("Visualisation du parcours de picking (ACO)")
    ax.set_xlabel("Coordonnée X")
    ax.set_ylabel("Coordonnée Y")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_aspect('equal', adjustable='box')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.show()