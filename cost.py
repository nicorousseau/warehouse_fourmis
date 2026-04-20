def calculate_cost(distance, current_cart_weight):
    """
    Fonction de coût : pénalise la distance en fonction du poids transporté.
    Plus le chariot est lourd, plus le coût kilométrique augmente.
    """
    if distance == float('inf'):
        return float('inf')
        
    # Facteur de pénalité : par exemple, +1% de coût par kg
    weight_penalty = 1 + (current_cart_weight * 0.01)
    
    return distance * weight_penalty