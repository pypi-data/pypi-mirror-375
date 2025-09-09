from .utilss.classes.score_calculator import ScoreCalculator
from itertools import combinations

def get_explaination_score(dendrogram, class_names, normalize=True):
    """
    Get the score of the entire dendrogram based on pairwise LCA ancestor counts.

    Parameters:
    - dendrogram: The hierarchical clustering dendrogram
    - class_names: List of class names corresponding to model outputs

    Returns:
    - score: The explanation score of the dendrogram
    """
    score_calculator = ScoreCalculator(dendrogram.Z, class_names)
    
    total_count = 0
    num_classes = len(class_names)

    # Get all combinations of 2 labels from class_names
    for label1, label2 in combinations(class_names, 2):
        try:
            idx1 = class_names.index(label1)
            idx2 = class_names.index(label2)
            count, _ = score_calculator.count_ancestors_to_lca(idx1, idx2)
            total_count += count
        except ValueError as e:
            print(f"Error processing pair ({label1}, {label2}): {e}")
            continue

    total_combinations = len(list(combinations(class_names, 2)))
    print(f"Total combinations processed: {total_combinations}")
    print(f"Total ancestor count sum: {total_count}")
    
    if normalize:
        # Maximum ancestors = height of dendrogram tree
        max_ancestors_per_pair = num_classes - 1  # Maximum tree height
        theoretical_max = total_combinations * max_ancestors_per_pair
        
        if theoretical_max == 0:
            normalized_score = 0
        else:
            # Invert the score so higher ancestor counts = lower explanation quality
            # and normalize to 0-100%
            normalized_score = max(0, (1 - (total_count / theoretical_max)) * 100)
        
        print(f"Theoretical maximum: {theoretical_max}")
        print(f"Normalized score: {normalized_score:.2f}%")
        
        return normalized_score
    else:
        return total_count