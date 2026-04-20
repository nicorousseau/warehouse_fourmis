import json
from warehouse import build_warehouse
from orders import generate_orders
from aco import run_aco
from visualize import plot_warehouse_path

def main():
    G = build_warehouse()
    points_a_visiter = generate_orders(n_items=20, G=G)
    
    point_depart = {'type': 'node', 'id': '0,0'}
    
    # Paramètres augmentés pour la nouvelle taille de l'entrepôt
    meilleur_chemin, historique = run_aco(
        G=G, 
        points=points_a_visiter, 
        start_loc=point_depart, 
        n_ants=40,
        n_iter=5
    )
    
    print("--- Séquence de ramassage complète (Boucle) ---")
    for i, etape in enumerate(meilleur_chemin):
        loc = etape['loc']
        p_id = etape['id_produit']
        
        if loc['type'] == 'node':
            print(f"Étape {i:2d} | [ {str(p_id):<15} ] | Noeud {loc['id']}")
        else:
            print(f"Étape {i:2d} | [ Produit {p_id:2d} ] | Couloir {loc['u']}->{loc['v']} (pos: {loc['pos']:.2f})")

    # Sauvegarde
    with open('aco_history.json', 'w') as f:
        json.dump(historique, f, indent=4)
    
    plot_warehouse_path(G, meilleur_chemin)

if __name__ == "__main__":
    main()