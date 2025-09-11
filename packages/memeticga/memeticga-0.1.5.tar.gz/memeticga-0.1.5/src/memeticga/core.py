from __future__ import annotations

import logging
import multiprocessing
import random
from functools import partial
from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np
from deap import base, creator, tools
from tqdm import tqdm
try:
    import cloudpickle  # type: ignore
except Exception:  # cloudpickle is optional; only required for pickling non-top-level fitness funcs
    cloudpickle = None  # type: ignore


# ----------------------------- Helpers / Evaluators -----------------------------

def evaluate_individual(individual: Sequence[int], fitness_func: Callable[[np.ndarray, Optional[np.ndarray]], float], X: Optional[np.ndarray]) -> Tuple[float]:
    """Evaluate a single individual.

    Returns a single-element tuple as required by DEAP fitness values.
    """
    arr = np.array(individual, dtype=np.int64)
    return (float(fitness_func(arr, X)),)


def evaluate_batch_deap(ind_list: List[tools._Toolbox], fitness_func_batch: Callable[[np.ndarray, Optional[np.ndarray]], np.ndarray], X: Optional[np.ndarray], perm_len: int) -> np.ndarray:
    """Batch evaluate a list of DEAP individuals in-place and return the values array.

    The function sets ``ind.fitness.values`` for each individual in ``ind_list``.
    """
    n = len(ind_list)
    if n == 0:
        return np.empty(0, dtype=np.float64)
    arr = np.empty((n, perm_len), dtype=np.int64)
    for i, ind in enumerate(ind_list):
        arr[i, :] = np.array(ind, dtype=np.int64)
    vals = fitness_func_batch(arr, X)
    for idx, ind in enumerate(ind_list):
        ind.fitness.values = (float(vals[idx]),)
    return vals


def _build_default_batch_from_single(single_func: Callable[[np.ndarray, Optional[np.ndarray]], float]) -> Callable[[np.ndarray, Optional[np.ndarray]], np.ndarray]:
    """Wrap a single-evaluation fitness function into a simple Python batch function.

    This is not vectorized but avoids requiring users to provide a batch API.
    """
    def batch_fn(inds2d: np.ndarray, X_data: Optional[np.ndarray]) -> np.ndarray:
        n_inds = inds2d.shape[0]
        out = np.empty(n_inds, dtype=np.float64)
        for r in range(n_inds):
            out[r] = float(single_func(inds2d[r], X_data))
        return out

    return batch_fn


# ----------------------------- Variation Operators -----------------------------


def create_individual(perm_len: int, start_node: Optional[int] = None):
    """Create a permutation (DEAP Individual).
    
    If start_node is provided, places it at index 0 (for problems requiring fixed start).
    If start_node is None, creates a completely random permutation.
    """
    p = random.sample(range(perm_len), perm_len)
    if start_node is not None:
        # Place the specified start_node at position 0
        start_idx = p.index(start_node)
        p[0], p[start_idx] = p[start_idx], p[0]
    return creator.Individual(p)


def mut_permutation_fixed(individual: list, indpb: float, fixed_start: bool = True):
    """Swap mutation that optionally respects a fixed index 0 (start node).

    Returns a 1-tuple (DEAP convention) containing the mutated individual.
    """
    size = len(individual)
    start_idx = 1 if fixed_start else 0
    for i in range(start_idx, size):
        if random.random() < indpb:
            j = random.randint(start_idx, size - 1)
            if i != j:
                individual[i], individual[j] = individual[j], individual[i]
    return (individual,)


def cxEdgeRecombination_fixed(ind1: Sequence[int], ind2: Sequence[int], fixed_start: bool = True) -> Tuple[creator.Individual, creator.Individual]:
    """Edge Recombination Crossover (ERX) returning two offspring - matches original implementation.

    This implementation builds two children: starting from each parent.
    """
    size = len(ind1)
    
    def build_child(p1: List[int], p2: List[int]) -> List[int]:
        """Build one child using ERX, starting from p1[0] with adjacency map from both parents."""
        adj_map = {k: set() for k in p1}
        for i in range(size):
            adj_map[p1[i]].add(p1[i-1])
            adj_map[p1[i]].add(p1[(i+1) % size])
            adj_map[p2[i]].add(p2[i-1])
            adj_map[p2[i]].add(p2[(i+1) % size])
        
        child = []
        current = p1[0] if fixed_start else random.choice(p1)
        remaining = set(p1)
        
        while len(child) < size:
            child.append(current)
            remaining.remove(current)
            if not remaining:
                break
            # Remove current from adjacency lists
            for k in adj_map:
                adj_map[k].discard(current)
            
            neigh = adj_map[current]
            if not neigh:
                current = random.choice(list(remaining))
            else:
                # Select neighbor with fewest adjacencies
                current = min(neigh, key=lambda n: len(adj_map[n]))
        
        return child
    
    p1 = list(ind1)
    p2 = list(ind2)
    c1 = build_child(p1, p2)
    c2 = build_child(p2, p1)
    return creator.Individual(c1), creator.Individual(c2)


# ----------------------------- Local Search (VNS) -----------------------------


def vns(toolbox: base.Toolbox, individual: list, max_iters: int, fixed_start: bool = True):
    """Simple Variable Neighborhood Search (VNS) using swap, insertion, and inversion.

    This version follows the original algorithm's behavior more closely by
    attempting each neighborhood in sequence on every iteration (subject to
    trivial size checks to avoid sampling errors) which keeps stronger local
    search pressure.
    """
    best = toolbox.clone(individual)
    if not best.fitness.valid:
        best.fitness.values = toolbox.evaluate(best)
    size = len(best)
    start_idx = 1 if fixed_start else 0
    for _ in range(max_iters):
        # swap (if possible)
        trial = toolbox.clone(best)
        if size > (3 if fixed_start else 1):  # Need at least two mutable positions
            i, j = random.sample(range(start_idx, size), 2) if size - start_idx >= 2 else (start_idx, start_idx)
            if i != j:
                trial[i], trial[j] = trial[j], trial[i]
                trial.fitness.values = toolbox.evaluate(trial)
                if trial.fitness.values[0] < best.fitness.values[0]:
                    best = trial
                    continue
        # insertion (if possible)
        trial = toolbox.clone(best)
        if size > (2 if fixed_start else 1):  # Need at least one mutable position to move
            i, j = random.sample(range(start_idx, size), 2) if size - start_idx >= 2 else (start_idx, start_idx)
            if i != j:
                elem = trial.pop(i)
                trial.insert(j, elem)
                trial.fitness.values = toolbox.evaluate(trial)
                if trial.fitness.values[0] < best.fitness.values[0]:
                    best = trial
                    continue
        # inversion (if possible)
        trial = toolbox.clone(best)
        if size > (3 if fixed_start else 2):
            i, j = sorted(random.sample(range(start_idx, size), 2)) if size - start_idx >= 2 else (start_idx, start_idx)
            if j > i:
                trial[i:j] = list(reversed(trial[i:j]))
                trial.fitness.values = toolbox.evaluate(trial)
                if trial.fitness.values[0] < best.fitness.values[0]:
                    best = trial
    return best


# ----------------------------- Island Worker -----------------------------


def island_evolution_worker(params: dict, island_data: Tuple[int, List[Tuple[List[int], float]], int, int]):
    """Worker that evolves one island for `MIGRATION_INTERVAL` generations.

    Returns (new_pop_data, new_stagnation_counter) where new_pop_data is a list of
    (perm_list, fitness_float).
    """
    # Unpack and seed random
    island_idx, pop_data, seed_val, island_stagnation_counter = island_data
    random.seed(seed_val)
    np.random.seed(seed_val)

    # Ensure DEAP creator types exist in worker process
    if not hasattr(creator, 'FitnessMin'):
        creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
    if not hasattr(creator, 'Individual'):
        creator.create('Individual', list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    # Reconstruct fitness functions if they were cloudpickled
    local_fitness_func = params.get('fitness_func')
    local_fitness_func_batch = params.get('fitness_func_batch')
    if params.get('USE_CLOUDPICKLE') and cloudpickle is not None:
        if params.get('fitness_func_pickled') is not None:
            local_fitness_func = cloudpickle.loads(params['fitness_func_pickled'])
        if params.get('fitness_func_batch_pickled') is not None:
            local_fitness_func_batch = cloudpickle.loads(params['fitness_func_batch_pickled'])
    toolbox.register('evaluate', partial(evaluate_individual, fitness_func=local_fitness_func, X=params['X']))
    toolbox.register('mate', partial(cxEdgeRecombination_fixed, fixed_start=bool(params['START_CANDIDATES'])))
    toolbox.register('mutate', partial(mut_permutation_fixed, indpb=params['MUT_PROB_GENE'], fixed_start=bool(params['START_CANDIDATES'])))
    toolbox.register('select', tools.selTournament, tournsize=params['TOURNAMENT_SIZE'])
    if params.get('START_CANDIDATES'):
        def _make_individual_worker():
            return create_individual(params['PERM_LEN'], start_node=random.choice(params['START_CANDIDATES']))
        toolbox.register('individual', _make_individual_worker)
    else:
        toolbox.register('individual', partial(create_individual, perm_len=params['PERM_LEN'], start_node=None))
    toolbox.register('population', tools.initRepeat, list, toolbox.individual)

    # Local batch evaluator (avoid pickling closures unexpectedly)
    local_batch_eval = local_fitness_func_batch or _build_default_batch_from_single(local_fitness_func)

    # Reconstruct island population from provided data
    island_pop: List[creator.Individual] = []
    for perm, fit in pop_data:
        ind = creator.Individual(list(perm))
        ind.fitness.values = (fit,)
        island_pop.append(ind)

    # Re-evaluate invalid individuals for safety
    invalid = [ind for ind in island_pop if not ind.fitness.valid]
    if invalid:
        evaluate_batch_deap(invalid, local_batch_eval, params['X'], params['PERM_LEN'])

    # Extinction event if stagnant (critical diversity mechanism)
    if island_stagnation_counter >= params['ISLAND_STAGNATION_LIMIT']:
        elites = tools.selBest(island_pop, params['ELITE_SIZE'])
        new_pop = toolbox.population(n=params['ISLAND_POP_SIZE'] - params['ELITE_SIZE'])
        island_pop[:] = [toolbox.clone(e) for e in elites] + new_pop
        invalid = [ind for ind in island_pop if not ind.fitness.valid]
        if invalid:
            evaluate_batch_deap(invalid, local_batch_eval, params['X'], params['PERM_LEN'])
        island_stagnation_counter = 0

    last_best = tools.selBest(island_pop, 1)[0].fitness.values[0]

        # Evolutionary loop for this island (MIGRATION_INTERVAL generations)
    for _ in range(params['MIGRATION_INTERVAL']):
        # Selection and variation - Match original logic exactly
        parents = [toolbox.clone(ind) for ind in toolbox.select(island_pop, len(island_pop))]
        offspring = []
        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                if random.random() < params['CX_PRPB']:
                    c1, c2 = toolbox.mate(parents[i], parents[i + 1])
                    # Clear fitness values after crossover
                    if hasattr(c1.fitness, 'values'):
                        del c1.fitness.values
                    if hasattr(c2.fitness, 'values'):
                        del c2.fitness.values
                    # Apply mutation only if crossover occurred
                    if random.random() < params['MUT_PROB']:
                        toolbox.mutate(c1)
                    if random.random() < params['MUT_PROB']:
                        toolbox.mutate(c2)
                    offspring.extend([c1, c2])
                else:
                    # No crossover: pass parents unchanged (no mutation)
                    offspring.extend([parents[i], parents[i + 1]])
            else:
                # Handle odd length: clone and append the last parent (V2 fix)
                offspring.append(toolbox.clone(parents[i]))

        if not offspring:
            continue

        # Evaluate offspring in batch
        invalid_off = [ind for ind in offspring if not ind.fitness.valid]
        if invalid_off:
            evaluate_batch_deap(invalid_off, local_batch_eval, params['X'], params['PERM_LEN'])

        # FIXED: Apply memetic local search like original - to offspring after evaluation
        n_apply = max(0, int(len(offspring) * params['VNS_APPLY_FRACTION']))
        if n_apply > 0:
            # choose top fraction by fitness (like original)
            candidates = sorted(offspring, key=lambda ind: ind.fitness.values[0])[:n_apply]
            for indv in candidates:
                refined = vns(toolbox, indv, params['VNS_ITER_SHORT'], params['FIXED_START'])
                if refined.fitness.values[0] < indv.fitness.values[0]:
                    indv[:] = refined[:]
                    indv.fitness.values = refined.fitness.values

        # Environmental selection
        island_pop[:] = tools.selBest(island_pop + offspring, params['ISLAND_POP_SIZE'])

    # Update stagnation counter with original logic
    current_best = tools.selBest(island_pop, 1)[0].fitness.values[0]
    if current_best >= last_best:
        island_stagnation_counter += params['MIGRATION_INTERVAL']
    else:
        island_stagnation_counter = 0

    # Deep VNS on island champion
    best_ind = tools.selBest(island_pop, 1)[0]
    refined_best = vns(toolbox, best_ind, params['VNS_ITER_DEEP'], params['FIXED_START'])
    if refined_best.fitness.values[0] < best_ind.fitness.values[0]:
        # Replace the worst individual
        island_pop.sort(key=lambda ind: ind.fitness.values[0], reverse=True)
        island_pop[0] = refined_best

    # Pack pop data for return
    new_pop_data = [(list(ind), ind.fitness.values[0]) for ind in island_pop]
    return new_pop_data, island_stagnation_counter


# ----------------------------- MGA Class -----------------------------


class MGA:
    """Memetic Genetic Algorithm with island model for permutation problems.

    Important: users must provide a `fitness_func` that accepts a 1D int np.array
    (permutation) and an optional data array ``X`` and returns a scalar float.

    Optionally, users can provide a `fitness_func_batch` that accepts a 2D int
    np.array (n_individuals x perm_len) and X and returns a 1D float array.
    """

    def __init__(
        self,
        problem: str = 'permutation',
        fitness_func: Optional[Callable[[np.ndarray, Optional[np.ndarray]], float]] = None,
        fitness_func_batch: Optional[Callable[[np.ndarray, Optional[np.ndarray]], np.ndarray]] = None,
        population: int = 200,
        ngen: int = 1000,
        verbosity: int = 1,
        log_file: Optional[str] = None,
        n_islands: int = 10,
        migration_interval: int = 25,
        migration_rate: int = 2,
        elite_size: int = 1,
        island_stagnation_limit: int = 50,
        tournament_size: int = 3,
        cx_prpb: float = 0.9,
        mut_prob: float = 0.8,
        mut_prob_gene: float = 0.12,
        vns_apply_fraction: float = 0.3,
        vns_iter_short: int = 15,
        vns_iter_deep: int = 250,
        start_candidates: Optional[Sequence[int]] = None,
        num_workers: Optional[int] = None,
        seed: int = 42,
        X: Optional[np.ndarray] = None,
        perm_len: Optional[int] = None,
        pickle_fitness_with_cloudpickle: bool = True,
    ) -> None:
        if problem != 'permutation':
            raise ValueError('Only permutation problem is currently supported.')
        if fitness_func is None:
            raise ValueError('fitness_func is required')

        self.problem = problem
        self.fitness_func = fitness_func
        self.fitness_func_batch = fitness_func_batch
        self.population = int(population)
        self.ngen = int(ngen)
        self.verbosity = int(verbosity)
        self.log_file = log_file
        self.n_islands = int(n_islands)
        self.migration_interval = int(migration_interval)
        self.migration_rate = int(migration_rate)
        self.elite_size = int(elite_size)
        self.island_stagnation_limit = int(island_stagnation_limit)
        self.cx_prpb = float(cx_prpb)
        self.mut_prob = float(mut_prob)
        self.mut_prob_gene = float(mut_prob_gene)
        self.vns_apply_fraction = float(vns_apply_fraction)
        self.vns_iter_short = int(vns_iter_short)
        self.vns_iter_deep = int(vns_iter_deep)
        self.start_candidates = list(start_candidates) if start_candidates else []
        # default number of workers: user-specified or CPU count - 1 (at least 1)
        if num_workers is None:
            self.num_workers = max(1, multiprocessing.cpu_count() - 1)
        else:
            self.num_workers = int(num_workers)
        self.seed = int(seed)
        self.X = X
        # Determine permutation length
        if self.X is not None:
            self.perm_len = int(self.X.shape[1])
        else:
            if perm_len is None:
                raise ValueError('perm_len is required when X is None')
            if int(perm_len) <= 0:
                raise ValueError('perm_len must be a positive integer')
            self.perm_len = int(perm_len)
        self.tournament_size = int(tournament_size)
        self.island_pop_size = max(2, self.population // max(1, self.n_islands))
        self.pickle_fitness_with_cloudpickle = bool(pickle_fitness_with_cloudpickle)

        # Validate start candidates if provided
        if self.start_candidates:
            for node in self.start_candidates:
                if node < 0 or node >= self.perm_len:
                    raise ValueError(f'start candidate {node} out of range for perm_len {self.perm_len}')

        # Setup logging
        if self.log_file:
            logging.basicConfig(filename=self.log_file, level=logging.INFO)
        else:
            logging.basicConfig(level=logging.WARNING)

        # Create DEAP classes in main process
        if not hasattr(creator, 'FitnessMin'):
            creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
        if not hasattr(creator, 'Individual'):
            creator.create('Individual', list, fitness=creator.FitnessMin)

        # Setup toolbox for main process
        self.toolbox = base.Toolbox()
        self.fixed_start = bool(self.start_candidates)
        self.toolbox.register('evaluate', partial(evaluate_individual, fitness_func=self.fitness_func, X=self.X))
        self.toolbox.register('mate', partial(cxEdgeRecombination_fixed, fixed_start=self.fixed_start))
        self.toolbox.register('mutate', partial(mut_permutation_fixed, indpb=self.mut_prob_gene, fixed_start=self.fixed_start))
        self.toolbox.register('select', tools.selTournament, tournsize=self.tournament_size)
        if self.start_candidates:
            def _make_individual_main():
                return create_individual(self.perm_len, start_node=random.choice(self.start_candidates))
            self.toolbox.register('individual', _make_individual_main)
        else:
            self.toolbox.register('individual', partial(create_individual, perm_len=self.perm_len, start_node=None))
        self.toolbox.register('population', tools.initRepeat, list, self.toolbox.individual)

    def optimize(self, num_workers: Optional[int] = None, hall_of_fame_size: int = 1):
        """Run the MGA. Returns a DEAP HallOfFame instance containing top solutions."""
        if num_workers is None:
            num_workers = self.num_workers
        random.seed(self.seed)
        np.random.seed(self.seed)

        # Prepare params dict to send to workers (must be picklable)
        params = {
            'fitness_func': self.fitness_func,
            'fitness_func_batch': self.fitness_func_batch,
            'X': self.X,
            'PERM_LEN': self.perm_len,
            'CX_PRPB': self.cx_prpb,
            'MUT_PROB': self.mut_prob,
            'MUT_PROB_GENE': self.mut_prob_gene,
            'VNS_APPLY_FRACTION': self.vns_apply_fraction,
            'VNS_ITER_SHORT': self.vns_iter_short,
            'VNS_ITER_DEEP': self.vns_iter_deep,
            'START_CANDIDATES': self.start_candidates,
            'TOURNAMENT_SIZE': self.tournament_size,
            'ISLAND_POP_SIZE': self.island_pop_size,
            'MIGRATION_INTERVAL': self.migration_interval,
            'ELITE_SIZE': self.elite_size,
            'ISLAND_STAGNATION_LIMIT': self.island_stagnation_limit,
            'FIXED_START': self.fixed_start,
            'USE_CLOUDPICKLE': self.pickle_fitness_with_cloudpickle,
        }

        # If running with workers and asked to cloudpickle, serialize fitness funcs to support non-top-level callables
        should_pickle = (num_workers and num_workers > 1 and self.pickle_fitness_with_cloudpickle)
        if should_pickle:
            if cloudpickle is None:
                raise RuntimeError('cloudpickle is required to pickle fitness functions when using multiple workers. Install with: pip install cloudpickle')
            params['fitness_func_pickled'] = cloudpickle.dumps(self.fitness_func) if self.fitness_func is not None else None
            params['fitness_func_batch_pickled'] = cloudpickle.dumps(self.fitness_func_batch) if self.fitness_func_batch is not None else None
            # Avoid sending unpicklable references
            params['fitness_func'] = None
            params['fitness_func_batch'] = None

        # Initialize islands
        islands = [self.toolbox.population(n=self.island_pop_size) for _ in range(self.n_islands)]
        island_stagnation_counters = [0] * self.n_islands

        # Initial batch evaluation
        all_inds = [ind for isl in islands for ind in isl]
        initial_batch = self.fitness_func_batch or _build_default_batch_from_single(self.fitness_func)
        evaluate_batch_deap(all_inds, initial_batch, self.X, self.perm_len)

        hof_size = max(1, min(hall_of_fame_size, len(all_inds)))
        halloffame = tools.HallOfFame(hof_size)
        halloffame.update(all_inds)

        # number of epochs equals how many migration cycles we will perform
        num_epochs = max(0, self.ngen // max(1, self.migration_interval))
        progress = tqdm(range(num_epochs), desc='Evolving Islands', disable=self.verbosity < 1)

        for epoch in progress:
            # Prepare island data for workers
            island_datas = []
            for i in range(self.n_islands):
                seed_val = self.seed + epoch * self.n_islands + i
                pop_data = [(list(ind), ind.fitness.values[0]) for ind in islands[i]]
                island_datas.append((i, pop_data, seed_val, island_stagnation_counters[i]))

            # Evolve islands in parallel or sequentially
            if num_workers and num_workers > 1:
                with multiprocessing.Pool(num_workers) as pool:
                    worker = partial(island_evolution_worker, params)
                    results = pool.map(worker, island_datas)
            else:
                results = [island_evolution_worker(params, data) for data in island_datas]

            # Reconstruct islands from results
            islands = []
            for j, res in enumerate(results):
                new_pop_data, new_stag = res
                pop = [creator.Individual(perm) for perm, _ in new_pop_data]
                for k, ind in enumerate(pop):
                    ind.fitness.values = (new_pop_data[k][1],)
                islands.append(pop)
                island_stagnation_counters[j] = new_stag

            # Perform migration (ring topology)
            islands = self.migrate_islands(islands)

            # Update hall of fame and progress
            all_inds = [ind for isl in islands for ind in isl]
            halloffame.update(all_inds)
            best = halloffame[0]
            progress.set_postfix({'best_fitness': f'{best.fitness.values[0]:.6f}'})
            if self.verbosity >= 1:
                logging.info(f'[Epoch {epoch + 1}/{num_epochs}] best_fitness={best.fitness.values[0]:.6f} best_perm={list(best)}')

        # Final log
        best = halloffame[0]
        logging.info(f'Final best solution: fitness={best.fitness.values[0]:.6f}, permutation={list(best)}')

        return halloffame

    def migrate_islands(self, islands: List[List[creator.Individual]]) -> List[List[creator.Individual]]:
        """Perform ring migration: send best individuals from each island to the next.

        Migrants replace random individuals in the destination island.
        """
        migrants = [tools.selBest(island, self.migration_rate) for island in islands]
        for i in range(self.n_islands):
            dest_idx = (i + 1) % self.n_islands
            for migrant in migrants[i]:
                replace_idx = random.randint(0, self.island_pop_size - 1)
                islands[dest_idx][replace_idx] = self.toolbox.clone(migrant)
        return islands