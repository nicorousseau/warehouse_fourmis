import random

def is_horizontal(u, v):
    """Vérifie si le couloir est horizontal (même coordonnée Y)."""
    y_u = u.split(',')[1]
    y_v = v.split(',')[1]
    return y_u == y_v

def generate_orders(n_items, G):
    """
    Génère une liste d'articles situés uniquement dans les allées horizontales.
    """
    orders = []
    edges = list(G.edges(data=True))
    
    # Filtrage : on ne garde que les allées de picking
    picking_edges = [(u, v, data) for u, v, data in edges if is_horizontal(u, v)]
    
    if not picking_edges:
        raise ValueError("Aucune allée de picking (horizontale) trouvée dans le graphe.")

    for i in range(1, n_items + 1):
        u, v, data = random.choice(picking_edges)
        longueur_couloir = data['weight']
        
        item = {
            'id_produit': i,
            'loc': {
                'type': 'edge',
                'u': u,
                'v': v,
                'pos': random.uniform(0.1, longueur_couloir - 0.1)
            },
            'poids': random.uniform(1.0, 25.0)
        }
        orders.append(item)
    
    return orders