import numpy as np
import numpy.random as nprand
import time


class DifferentialEvolution:
    """Class implementing the Differential Evolution metaheuristic search algorithm (DE/rand/1/bin)
    R. Storn and K. Price (1997). "Differential evolution - a simple and efficient heuristic
    for global optimization over continuous spaces", Journal of Global Optimization, 11, pp.341–359.

    More at: https://doi.org/10.1023/A:1008202821328
    """

    def __init__(self, optimization_problem, population_size, mutation_factor, crossover_probability):

        self.dimension = optimization_problem.dimension
        self.lower_bounds = np.array(optimization_problem.lower_bounds)
        self.upper_bounds = np.array(optimization_problem.upper_bounds)

        self.population_size = population_size
        self.mutation_factor = mutation_factor
        self.crossover_probability = crossover_probability

        # Initial checks
        assert len(self.lower_bounds) == len(self.upper_bounds), \
            'Lower- and upper-bounds must be the same length'
        assert self.population_size >= 5, \
            'Population size must be greater or equal to 5'
        assert np.all(self.upper_bounds > self.lower_bounds), \
            'All upper-bound values must be greater than lower-bound values'

        self.objective = lambda x: optimization_problem.fitness(x)
        self.constraints = lambda x: optimization_problem.constraints(x)

        self.MAX_FUNCTION_EVALUATIONS = self.dimension * 4000  # Default value of maximum function evaluations
        self.PENALTY_FACTOR = 10 ** 15  # Default value of penalty factor
        self.verbose = True  # Default value for print

        self.__individuals = np.zeros(shape=(self.population_size, self.dimension))
        self.__fitness = np.zeros(self.population_size)
        self.__bound_range = self.upper_bounds - self.lower_bounds

        self.__trial = None
        self.__donor = None
        self.__best = None
        self.__fitness_min = None

    @property
    def function_evaluations(self):
        return self.__function_evaluations

    @property
    def best(self):
        return self.__best

    @property
    def fitness_min(self):
        return self.__fitness_min

    def __initialize(self):
        # Generate initial population
        self.__function_evaluations = 0
        np.random.seed()

        for parent in range(self.population_size):
            self.__individuals[parent, :] = self.lower_bounds + self.__bound_range * nprand.rand(self.dimension)
            self.__fitness[parent] = self.__evaluate(self.__individuals[parent, :])

        # Find the current best
        bestID = np.argmin(self.__fitness)
        self.__fitness_min = self.__fitness[bestID]
        self.__best = self.__individuals[bestID, :]

        # Update function evaluations
        self.__function_evaluations += self.population_size

    def __mutation(self):
        # DE/rand/1/bin mutation scheme
        r1 = nprand.permutation(self.population_size)
        r2 = nprand.permutation(self.population_size)
        r3 = nprand.permutation(self.population_size)

        # Create the donor vector
        self.__donor = self.__individuals[r1, :] + \
                       self.mutation_factor * (self.__individuals[r2, :] - self.__individuals[r3, :])

    def __crossover(self):
        k = nprand.rand(self.population_size, self.dimension) < self.crossover_probability
        self.__trial = self.__individuals * (1 - k) + self.__donor * k

    def __check_bounds(self):
        for i in range(self.population_size):
            for dim in range(self.dimension):
                if self.__trial[i, dim] < self.lower_bounds[dim] or self.__trial[i, dim] > self.upper_bounds[dim]:
                    self.__trial[i, dim] = self.lower_bounds[dim] + self.__bound_range[dim] * nprand.rand()

    def __selection(self):
        for i in range(self.population_size):
            fitness_trial = self.__evaluate(self.__trial[i, :])

            if fitness_trial <= self.__fitness[i]:
                self.__individuals[i, :] = self.__trial[i, :]
                self.__fitness[i] = fitness_trial

            if fitness_trial <= self.__fitness_min:
                self.__best = self.__trial[i, :]
                self.__fitness_min = fitness_trial

        self.__function_evaluations += self.population_size

    def __evaluate(self, x):
        f = self.objective(x)

        return f + self.__penalty(self.constraints(x))

    def __penalty(self, g):
        z = 0

        for k in range(len(g)):
            if g[k] > 0:
                z = z + self.PENALTY_FACTOR * g[k] ** 2

        return z

    def solve(self):
        self.__initialize()

        tic = time.clock()
        while self.__function_evaluations < self.MAX_FUNCTION_EVALUATIONS:
            self.__mutation()
            self.__crossover()
            self.__check_bounds()
            self.__selection()

            if self.verbose:
                toc = time.clock()
                time_elapsed = toc - tic

                x = self.__best
                for i in range(len(x)):
                    x[i] = np.round(x[i], decimals=2)

                # print('FES: %4i | Fit: %12.4e' % (self.__function_evaluations, self.__fitness_min) + \
                #       ' | CurBest:', ' '.join(map(str, self.__best))) + ' | Duration: %0.0f seconds' % time_elapsed

                print('FES: %4i | Fit: %12.4e' % (self.__function_evaluations, self.__fitness_min) + \
                      ' | CurBest: %s' % x + ' | Duration: %0.0f seconds' % time_elapsed)
