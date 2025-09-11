import numpy as np
import pytest
from memeticga.core import MGA

@pytest.mark.parametrize("num_workers", [1, 2])
def test_mga(num_workers):
    rng = np.random.default_rng(42)
    N = 50
    D = rng.integers(1, 100, size=(N, N)).astype(float)
    np.fill_diagonal(D, 0)
    
    def tour_length(perm, X=D):
        total = sum(X[perm[i], perm[i+1]] for i in range(len(perm)-1))
        total += X[perm[-1], perm[0]]
        return float(total)
    
    mga = MGA(
        problem="permutation",
        fitness_func=tour_length,
        population=20,
        ngen=100,
        n_islands=10,
        migration_interval=25,
        migration_rate=2,
        elite_size=1,
        X=D,
        seed=42,
        num_workers=num_workers,
        start_candidates=[0]
    )
    hof = mga.optimize(hall_of_fame_size=3)
    best = hof[0]
    
    assert best.fitness.values[0] >= 0
    assert np.allclose(tour_length(best, D), best.fitness.values[0])
    assert set(best) == set(range(N))
    assert best[0] == 0