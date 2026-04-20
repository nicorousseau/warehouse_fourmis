import numpy as np
import random
from cost import calculate_cost
from warehouse import get_real_distance

def run_aco(G, points, start_loc={'type': 'node', 'id': '0,0'}, n_ants=10, n_iter=50, alpha=1.0, beta=2.0, rho=0.5):
    locations = [start_loc] + [p['loc'] for p in points]
    poids_produits = [0] + [p['poids'] for p in points]
    info_nodes = [{'id_produit': 'Dépôt (Départ)', 'loc': start_loc}] + points
    
    n_nodes = len(locations)
    pheromones = np.ones((n_nodes, n_nodes))
    best_path_global = None
    best_cost_global = float('inf')
    history = []

    for iteration in range(n_iter):
        paths = []
        path_costs = []
        
        for _ in range(n_ants):
            unvisited = list(range(1, n_nodes))
            current = 0
            path = [current]
            cart_weight = 0
            total_cost = 0
            
            # 1. Ramassage des produits
            while unvisited:
                probabilities = []
                for j in unvisited:
                    dist = get_real_distance(G, locations[current], locations[j])
                    cost = calculate_cost(dist, cart_weight + poids_produits[j])
                    
                    if cost == float('inf'):
                        prob = 0
                    else:
                        eta = 1.0 / cost if cost > 0 else 1e10
                        prob = (pheromones[current][j] ** alpha) * (eta ** beta)
                    probabilities.append(prob)
                
                sum_prob = sum(probabilities)
                if sum_prob == 0: break
                
                next_node = np.random.choice(unvisited, p=np.array(probabilities)/sum_prob)
                
                dist = get_real_distance(G, locations[current], locations[next_node])
                cart_weight += poids_produits[next_node]
                total_cost += calculate_cost(dist, cart_weight)
                
                path.append(next_node)
                unvisited.remove(next_node)
                current = next_node
            
            # 2. Retour au dépôt (Retour à l'index 0)
            dist_retour = get_real_distance(G, locations[current], locations[0])
            # Le coût du retour inclut le poids total de la commande collectée
            total_cost += calculate_cost(dist_retour, cart_weight)
            path.append(0) 
            
            paths.append(path)
            path_costs.append(total_cost)
            
            if total_cost < best_cost_global:
                best_cost_global = total_cost
                best_path_global = path

        # Mise à jour des phéromones
        pheromones *= (1 - rho)
        for p, cost in zip(paths, path_costs):
            if cost < float('inf'):
                for i in range(len(p) - 1):
                    pheromones[p[i]][p[i+1]] += 1.0 / cost

        history.append({
            'iteration': iteration,
            'best_cost': float(min(path_costs)) if path_costs else float('inf'),
            'best_path': [int(x) for x in best_path_global] if best_path_global else []
        })

    # Construction de la séquence finale avec l'objet "Dépôt (Arrivée)" à la fin
    info_nodes_final = info_nodes + [{'id_produit': 'Dépôt (Arrivée)', 'loc': start_loc}]
    # On ajuste le dernier index du path car on a ajouté un élément à info_nodes_final
    sequence_indices = best_path_global[:-1] + [n_nodes] 
    sequence_finale = [info_nodes_final[i] for i in sequence_indices]
    
    return sequence_finale, history