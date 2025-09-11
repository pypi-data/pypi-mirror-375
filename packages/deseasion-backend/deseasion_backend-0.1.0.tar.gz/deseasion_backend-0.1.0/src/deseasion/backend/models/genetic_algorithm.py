import math
import random
from functools import partial

import numpy as np
import pyproj
from shapely.geometry import Polygon
from shapely.ops import transform
from shapely.strtree import STRtree


class GAContext:
    def __init__(self, df, features, geo_size, bounds=None, proj=""):
        self.df = df
        self.features = features
        self.geo_size = geo_size
        self.proj = proj
        if bounds is None:
            self.bounds = tuple(df.total_bounds)
        else:
            self.bounds = bounds

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, value):
        self._df = value
        geoms = []
        values = []
        for i, f in self._df.iterrows():
            values.append(f["value"])
            geoms.append(f.geometry)
        self._geometries = geoms
        self._geometries_tree = STRtree(geoms)
        self._values = values

    @property
    def values(self):
        return self._values

    @property
    def geometries(self):
        return self._geometries

    @property
    def geometries_tree(self):
        return self._geometries_tree


class Individual:
    def __init__(self, ctx, genes):
        self._ctx = ctx
        self.genes = genes

    @classmethod
    def random(cls, ctx):
        """Create a new random individual."""
        xmin, ymin, xmax, ymax = ctx.bounds
        dmin = 0.5 * math.sqrt(ctx.geo_size)
        dmax = 1.5 * math.sqrt(ctx.geo_size)
        alpha_min = 0.1

        x = random.uniform(xmin, xmax)
        y = random.uniform(ymin, ymax)
        alpha1 = random.uniform(alpha_min, math.pi / 2 - alpha_min)
        d1 = random.uniform(dmin, dmax)
        alpha2 = random.uniform(alpha_min, math.pi / 2 - alpha_min)
        d2 = random.uniform(dmin, dmax)
        alpha3 = random.uniform(alpha_min, math.pi / 2 - alpha_min)
        d3 = random.uniform(dmin, dmax)
        alpha4 = random.uniform(alpha_min, math.pi / 2 - alpha_min)
        d4 = random.uniform(dmin, dmax)
        return cls(ctx, (x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4))

    @property
    def genes(self):
        return self._genes

    @genes.setter
    def genes(self, genes):
        """Cut the genes to the limits and reset the fitness."""
        genes = self.check_and_repair_the_geo_size(*genes)
        self._genes = genes
        self._fitness = None
        self._inputs = []
        self._execution_artifact = {}

    @property
    def inputs(self):
        return self._inputs

    @property
    def execution_artifact(self):
        return self._execution_artifact

    @property
    def fitness(self):
        """Calculate the fitness.

        The fitness corresponds of the percentage of the evaluation map covered
        by the geometry.
        """
        if (
            self._fitness is None
        ):  # TODO: Check that the condition is still correct
            self._fitness = 0
            self._execution_artifact["features"] = []
            self._inputs = []
            geom = self.as_geometry()
            query = self._ctx.geometries_tree.query(geom)
            for other in query:
                other_g = self._ctx.geometries[other]
                try:
                    intersection = geom.intersection(other_g)
                except TypeError as e:
                    raise TypeError(f"{e} : {geom} : {other_g}")
                value = float(self._ctx.values[other])
                if not intersection.is_empty:
                    feature = self._ctx.features[other]
                    area = intersection.area
                    fitness = area * pow(value, 3) + 0.00001
                    self._execution_artifact["features"].append(
                        {
                            "feature": feature.id,
                            "area": area,
                            "fitness": fitness,
                        }
                    )
                    self._inputs.append(feature)
                    self._fitness += fitness
        return self._fitness

    def check_and_repair_the_geo_size(
        self, x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4
    ):
        geo_size = self._ctx.geo_size
        step = 0.01 * math.sqrt(geo_size)
        alpha_min = 0.1
        alpha_max = math.pi / 2 - alpha_min
        xmin, ymin, xmax, ymax = self._ctx.bounds

        if x < xmin:
            x = xmin
        elif x > xmax:
            x = xmax

        if y < ymin:
            y = ymin
        elif y > ymax:
            y = ymax

        if alpha1 < alpha_min:
            alpha1 = alpha_min
        elif alpha1 > alpha_max:
            alpha1 = alpha_max

        if alpha2 < alpha_min:
            alpha2 = alpha_min
        elif alpha2 > alpha_max:
            alpha2 = alpha_max

        if alpha3 < alpha_min:
            alpha3 = alpha_min
        elif alpha3 > alpha_max:
            alpha3 = alpha_max

        if alpha4 < alpha_min:
            alpha4 = alpha_min
        elif alpha4 > alpha_max:
            alpha4 = alpha_max

        # calculate the area
        def calculate_area(
            x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4
        ):
            D1 = math.sqrt(
                pow(d1, 2)
                + pow(d4, 2)
                - 2 * d1 * d4 * math.cos(math.pi / 2 + alpha1 - alpha4)
            )
            D2 = math.sqrt(
                pow(d1, 2)
                + pow(d2, 2)
                - 2 * d1 * d2 * math.cos(math.pi / 2 + alpha2 - alpha1)
            )
            D3 = math.sqrt(
                pow(d2, 2)
                + pow(d3, 2)
                - 2 * d2 * d3 * math.cos(math.pi / 2 + alpha3 - alpha2)
            )
            D4 = math.sqrt(
                pow(d3, 2)
                + pow(d4, 2)
                - 2 * d3 * d4 * math.cos(math.pi / 2 + alpha4 - alpha3)
            )
            P1 = (D1 + d1 + d4) / 2
            S1 = math.sqrt(P1 * (P1 - D1) * (P1 - d1) * (P1 - d4))
            P2 = (D2 + d1 + d2) / 2
            S2 = math.sqrt(P2 * (P2 - D2) * (P2 - d1) * (P2 - d2))
            P3 = (D3 + d2 + d3) / 2
            S3 = math.sqrt(P3 * (P3 - D3) * (P3 - d2) * (P3 - d3))
            P4 = (D4 + d3 + d4) / 2
            S4 = math.sqrt(P4 * (P4 - D4) * (P4 - d3) * (P4 - d4))
            S = S1 + S2 + S3 + S4
            return S

        S = calculate_area(
            x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4
        )
        d1 = d1 * math.sqrt(geo_size / S)
        d2 = d2 * math.sqrt(geo_size / S)
        d3 = d3 * math.sqrt(geo_size / S)
        d4 = d4 * math.sqrt(geo_size / S)

        if d1 < step:
            d1 = step
        if d2 < step:
            d2 = step
        if d3 < step:
            d3 = step
        if d4 < step:
            d4 = step

        return x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4

    def as_geometry(self, proj=None):
        """Return the geometry of the individual."""
        x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4 = self.genes
        geom = Polygon(
            [
                (x + d1 * math.cos(alpha1), y + d1 * math.sin(alpha1)),
                (x - d2 * math.sin(alpha2), y + d2 * math.cos(alpha2)),
                (x - d3 * math.cos(alpha3), y - d3 * math.sin(alpha3)),
                (x + d4 * math.sin(alpha4), y - d4 * math.cos(alpha4)),
            ]
        )
        if proj is not None and self._ctx.proj is not None:
            proj_in = pyproj.Proj(self._ctx.proj)
            proj_out = pyproj.Proj(proj)
            if not proj_in.is_exact_same(proj_out):
                project = partial(
                    pyproj.transform, proj_in, proj_out, always_xy=True
                )
                geom = transform(project, geom)
        return geom

    def crossover_1(self, other_parent):
        (
            x1,
            y1,
            alpha11,
            d11,
            alpha21,
            d21,
            alpha31,
            d31,
            alpha41,
            d41,
        ) = self.genes
        (
            x2,
            y2,
            alpha12,
            d12,
            alpha22,
            d22,
            alpha32,
            d32,
            alpha42,
            d42,
        ) = other_parent.genes
        (
            x,
            y,
            alpha1,
            d1,
            alpha2,
            d2,
            alpha3,
            d3,
            alpha4,
            d4,
        ) = self.check_and_repair_the_geo_size(
            x2, y2, alpha11, d11, alpha21, d21, alpha31, d31, alpha41, d41
        )
        offspring1 = (x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4)
        (
            x,
            y,
            alpha1,
            d1,
            alpha2,
            d2,
            alpha3,
            d3,
            alpha4,
            d4,
        ) = self.check_and_repair_the_geo_size(
            x1, y1, alpha12, d12, alpha22, d22, alpha32, d32, alpha42, d42
        )
        offspring2 = (x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4)
        return [
            Individual(self._ctx, genes=offspring1),
            Individual(self._ctx, genes=offspring2),
        ]

    def crossover_2(self, other_parent):
        (
            x1,
            y1,
            alpha11,
            d11,
            alpha21,
            d21,
            alpha31,
            d31,
            alpha41,
            d41,
        ) = self.genes
        (
            x2,
            y2,
            alpha12,
            d12,
            alpha22,
            d22,
            alpha32,
            d32,
            alpha42,
            d42,
        ) = other_parent.genes
        (
            x,
            y,
            alpha1,
            d1,
            alpha2,
            d2,
            alpha3,
            d3,
            alpha4,
            d4,
        ) = self.check_and_repair_the_geo_size(
            x1, y1, alpha11, d12, alpha21, d22, alpha31, d32, alpha41, d42
        )
        offspring1 = (x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4)
        (
            x,
            y,
            alpha1,
            d1,
            alpha2,
            d2,
            alpha3,
            d3,
            alpha4,
            d4,
        ) = self.check_and_repair_the_geo_size(
            x2, y2, alpha12, d11, alpha22, d21, alpha32, d31, alpha42, d41
        )
        offspring2 = (x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4)
        return [
            Individual(self._ctx, genes=offspring1),
            Individual(self._ctx, genes=offspring2),
        ]

    def crossover_3(self, other_parent):
        (
            x1,
            y1,
            alpha11,
            d11,
            alpha21,
            d21,
            alpha31,
            d31,
            alpha41,
            d41,
        ) = self.genes
        (
            x2,
            y2,
            alpha12,
            d12,
            alpha22,
            d22,
            alpha32,
            d32,
            alpha42,
            d42,
        ) = other_parent.genes
        (
            x,
            y,
            alpha1,
            d1,
            alpha2,
            d2,
            alpha3,
            d3,
            alpha4,
            d4,
        ) = self.check_and_repair_the_geo_size(
            x1, y1, alpha12, d11, alpha22, d21, alpha32, d31, alpha42, d41
        )
        offspring1 = (x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4)
        (
            x,
            y,
            alpha1,
            d1,
            alpha2,
            d2,
            alpha3,
            d3,
            alpha4,
            d4,
        ) = self.check_and_repair_the_geo_size(
            x2, y2, alpha11, d12, alpha21, d22, alpha31, d32, alpha41, d42
        )
        offspring2 = (x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4)
        return [
            Individual(self._ctx, genes=offspring1),
            Individual(self._ctx, genes=offspring2),
        ]

    def mutation_1(self, other_parent):
        """Mutate the position (x, y)."""
        (
            x1,
            y1,
            alpha11,
            d11,
            alpha21,
            d21,
            alpha31,
            d31,
            alpha41,
            d41,
        ) = self.genes
        (
            x2,
            y2,
            alpha12,
            d12,
            alpha22,
            d22,
            alpha32,
            d32,
            alpha42,
            d42,
        ) = other_parent.genes
        # select one value at random
        r = random.randint(0, 1)
        if r == 0:
            x1, x2 = x2, x1
        else:
            y1, y2 = y2, y1
        (
            x,
            y,
            alpha1,
            d1,
            alpha2,
            d2,
            alpha3,
            d3,
            alpha4,
            d4,
        ) = self.check_and_repair_the_geo_size(
            x1, y1, alpha11, d11, alpha21, d21, alpha31, d31, alpha41, d41
        )
        offspring1 = (x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4)
        (
            x,
            y,
            alpha1,
            d1,
            alpha2,
            d2,
            alpha3,
            d3,
            alpha4,
            d4,
        ) = self.check_and_repair_the_geo_size(
            x2, y2, alpha12, d12, alpha22, d22, alpha32, d32, alpha42, d42
        )
        offspring2 = (x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4)
        return [
            Individual(self._ctx, genes=offspring1),
            Individual(self._ctx, genes=offspring2),
        ]

    def mutation_2(self, other_parent):
        """Mutate the vertices (alpha, d)."""
        (
            x1,
            y1,
            alpha11,
            d11,
            alpha21,
            d21,
            alpha31,
            d31,
            alpha41,
            d41,
        ) = self.genes
        (
            x2,
            y2,
            alpha12,
            d12,
            alpha22,
            d22,
            alpha32,
            d32,
            alpha42,
            d42,
        ) = other_parent.genes
        # select one value at random
        r = random.randint(0, 7)
        if r == 0:
            alpha11, alpha12 = alpha12, alpha11
        elif r == 1:
            d11, d12 = d12, d11
        if r == 2:
            alpha21, alpha22 = alpha22, alpha21
        elif r == 3:
            d21, d22 = d22, d21
        if r == 4:
            alpha31, alpha32 = alpha32, alpha31
        elif r == 5:
            d31, d32 = d32, d31
        if r == 6:
            alpha41, alpha42 = alpha42, alpha41
        else:
            d41, d42 = d42, d41
        (
            x,
            y,
            alpha1,
            d1,
            alpha2,
            d2,
            alpha3,
            d3,
            alpha4,
            d4,
        ) = self.check_and_repair_the_geo_size(
            x1, y1, alpha11, d11, alpha21, d21, alpha31, d31, alpha41, d41
        )
        offspring1 = (x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4)
        (
            x,
            y,
            alpha1,
            d1,
            alpha2,
            d2,
            alpha3,
            d3,
            alpha4,
            d4,
        ) = self.check_and_repair_the_geo_size(
            x2, y2, alpha12, d12, alpha22, d22, alpha32, d32, alpha42, d42
        )
        offspring2 = (x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4)
        return [
            Individual(self._ctx, genes=offspring1),
            Individual(self._ctx, genes=offspring2),
        ]

    def local_search(self):
        # TODO: It doesn't seem to always improve the solution, looks more like
        # a mutation
        x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4 = self.genes
        xmin, ymin, xmax, ymax = self._ctx.bounds
        r = random.randint(0, 10)
        if r == 0:
            x += random.uniform(-(xmax - xmin) / 100, (xmax - xmin) / 100)
        elif r == 1:
            y += random.uniform(-(ymax - ymin) / 100, (ymax - ymin) / 100)
        elif r == 2:
            alpha1 += random.uniform(-math.pi / 8, math.pi / 8)
        elif r == 3:
            d1 += random.uniform(
                -(xmax - xmin + ymax - ymin) / 500,
                (xmax - xmin + ymax - ymin) / 500,
            )
        elif r == 4:
            alpha2 += random.uniform(-math.pi / 8, math.pi / 8)
        elif r == 5:
            d2 += random.uniform(
                -(xmax - xmin + ymax - ymin) / 500,
                (xmax - xmin + ymax - ymin) / 500,
            )
        elif r == 6:
            alpha3 += random.uniform(-math.pi / 8, math.pi / 8)
        elif r == 7:
            d3 += random.uniform(
                -(xmax - xmin + ymax - ymin) / 500,
                (xmax - xmin + ymax - ymin) / 500,
            )
        elif r == 8:
            alpha4 += random.uniform(-math.pi / 8, math.pi / 8)
        elif r == 9:
            d4 += random.uniform(
                -(xmax - xmin + ymax - ymin) / 500,
                (xmax - xmin + ymax - ymin) / 500,
            )
        else:
            rotation = random.uniform(-math.pi / 8, math.pi / 8)
            alpha1 += rotation
            alpha2 += rotation
            alpha3 += rotation
            alpha4 += rotation

        (
            x,
            y,
            alpha1,
            d1,
            alpha2,
            d2,
            alpha3,
            d3,
            alpha4,
            d4,
        ) = self.check_and_repair_the_geo_size(
            x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4
        )
        self.genes = (x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4)


class Population:
    def __init__(self, ctx, individuals):
        self._ctx = ctx
        self.individuals = individuals

    @classmethod
    def random(cls, ctx, size):
        """Initialize a population with random individuals.

        Args:
            size: the size of the population to generate
        """
        individuals = [Individual.random(ctx) for i in range(size)]
        return cls(ctx, individuals)

    def select_roulette(self, count, replace=False):
        """Select individuals in the population using the roulette wheel
        policy.

        The probability of selecting an individual depends on its fitness
        value.
        An invidiuals with a high fitness will have more chance to be selected
        than an individual with a low fitness.

        Args:
            count: the number of individuals to select
            replace: allow to select several times the same individual
                (default: False)

        Returns:
            A new population with selected individuals
        """
        fitness = [
            i.fitness if i.fitness != 0 else 0.00001 for i in self.individuals
        ]
        p = [f / sum(fitness) for f in fitness]
        selection = list(
            np.random.choice(
                self.individuals, size=count, replace=replace, p=p
            )
        )
        copies = [Individual(self._ctx, ind.genes) for ind in selection]
        return Population(self._ctx, copies)

    def combine(self, individuals):
        """Add offsptring to parent population."""
        for offspring in individuals:
            self.individuals.append(offspring)

    def create_children_from_crossover_1(self, count):
        children = []
        parents_1_pop = self.select_roulette(int(count / 2))
        for p1 in parents_1_pop.individuals:
            p2 = np.random.choice(self.individuals)
            children.extend(p1.crossover_1(p2))
        return Population(self._ctx, children)

    def create_children_from_crossover_2(self, count):
        children = []
        parents_1_pop = self.select_roulette(int(count / 2))
        for p1 in parents_1_pop.individuals:
            p2 = np.random.choice(self.individuals)
            children.extend(p1.crossover_2(p2))
        return Population(self._ctx, children)

    def create_children_from_crossover_3(self, count):
        children = []
        parents_1_pop = self.select_roulette(int(count / 2))
        for p1 in parents_1_pop.individuals:
            p2 = np.random.choice(self.individuals)
            children.extend(p1.crossover_3(p2))
        return Population(self._ctx, children)

    def create_children_from_mutation_1(self, count):
        children = []
        parents_1_pop = self.select_roulette(int(count / 2))
        for p1 in parents_1_pop.individuals:
            p2 = np.random.choice(self.individuals)
            children.extend(p1.mutation_1(p2))
        return Population(self._ctx, children)

    def create_children_from_mutation_2(self, count):
        children = []
        parents_1_pop = self.select_roulette(int(count / 2))
        for p1 in parents_1_pop.individuals:
            p2 = np.random.choice(self.individuals)
            children.extend(p1.mutation_2(p2))
        return Population(self._ctx, children)

    def create_children_from_local_search(self, count):
        """One parent and one offspring."""
        offspring = []
        parents = self.select_roulette(count)
        for p in parents.individuals:
            p.local_search()
            offspring.append(p)
        return Population(self._ctx, offspring)


class GeneticAlgorithm:
    """Genetic algorithm to find the best areas on the decision map.

    Attributes:
        population: The population of solution of the genetic algorithm.
        size (int): The size of the population.
        iteration (int): The current iteration of the algorithm.
    """

    def __init__(
        self, ctx, size, mutation=None, children=None, filter_clusters=True
    ):
        self._ctx = ctx
        self.size = size
        self.population = Population.random(ctx, size)
        self.iteration = 0
        self.crossover_1_rate = int(0.3 * size)
        self.crossover_2_rate = int(0.3 * size)
        self.crossover_3_rate = int(0.5 * size)
        self.mutation_1_rate = int(0.3 * size)
        self.mutation_2_rate = int(0.3 * size)
        self.local_search_rate = int(0.5 * size)
        self.filter_clusters = filter_clusters
        self.B = []
        self.all_solutions_found = []

    def filter_best(self):
        def search(Fscore_list, num=3):
            if num > len(set(Fscore_list)):
                num = len(set(Fscore_list))
            res = dict(
                [(v, []) for v in sorted(set(Fscore_list), reverse=True)[:num]]
            )
            for index, val in enumerate(Fscore_list):
                if val in res:
                    res[val].append(index)
            A = sorted(res.items(), key=lambda x: x[0], reverse=True)
            B = A[num - 1]
            return B[0]

        threshold = search(self._ctx.df.value, num=3)  # TODO: Modify that?
        A = []
        for H in self.all_solutions_found:
            check_fitness = H.fitness
            if check_fitness >= 0.9 * self._ctx.geo_size * pow(
                int(threshold), 3
            ):  # threshold of objective function
                A.append(H)
        R = []
        le = len(A)
        max_num = 1
        while le >= 1:
            S = sorted(A, key=lambda i: i.fitness, reverse=True)
            S0 = S[0]  # best solution
            (
                x0,
                y0,
                alpha01,
                d01,
                alpha02,
                d02,
                alpha03,
                d03,
                alpha04,
                d04,
            ) = S0.genes
            B = []
            for M in S:
                x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4 = M.genes
                if math.sqrt(
                    pow(x - x0, 2) + pow(y - y0, 2)
                ) > 0.8 * math.sqrt(
                    self._ctx.geo_size
                ):  # set the distance constraint
                    B.append(M)
            A = B
            R.append(S0)  # save the best solution
            le = len(B)
            max_num += 1
            if max_num >= 30:  # max number of solutions to be shown
                break
        return Population(self._ctx, R)

    def iterate(self):
        """Iterate the algorithm to the next generation."""
        children_from_crossover_1 = (
            self.population.create_children_from_crossover_1(
                self.crossover_1_rate
            )
        )
        children_from_crossover_2 = (
            self.population.create_children_from_crossover_2(
                self.crossover_2_rate
            )
        )
        children_from_crossover_3 = (
            self.population.create_children_from_crossover_3(
                self.crossover_3_rate
            )
        )
        children_from_mutation_1 = (
            self.population.create_children_from_mutation_1(
                self.mutation_1_rate
            )
        )
        children_from_mutation_2 = (
            self.population.create_children_from_mutation_2(
                self.mutation_2_rate
            )
        )
        children_from_local_search = (
            self.population.create_children_from_local_search(
                self.local_search_rate
            )
        )
        self.population.combine(
            children_from_crossover_1.individuals
        )  # add chirldren from crossover 1
        self.population.combine(children_from_crossover_2.individuals)
        self.population.combine(children_from_crossover_3.individuals)
        self.population.combine(children_from_mutation_1.individuals)
        self.population.combine(children_from_mutation_2.individuals)
        self.population.combine(children_from_local_search.individuals)

        best = max(self.population.individuals, key=lambda i: i.fitness)

        # adaptative restart process
        A = best.fitness
        self.B.append(A)
        B_length = len(self.B)
        if B_length > 3:
            if (
                self.B[B_length - 1] == self.B[B_length - 2]
                and self.B[B_length - 1] == self.B[B_length - 3]
                and self.B[B_length - 1] == self.B[B_length - 4]
            ):
                # reinitialize if the best doesn't improve
                self.population = Population.random(self._ctx, self.size - 1)
            else:
                self.population = self.population.select_roulette(
                    self.size - 1
                )
        else:
            self.population = self.population.select_roulette(self.size - 1)
        self.population.individuals.append(best)  # keep the best

        (
            x0,
            y0,
            alpha01,
            d01,
            alpha02,
            d02,
            alpha03,
            d03,
            alpha04,
            d04,
        ) = best.genes
        for i, K in enumerate(self.population.individuals):
            x, y, alpha1, d1, alpha2, d2, alpha3, d3, alpha4, d4 = K.genes
            if math.sqrt(pow(x - x0, 2) + pow(y - y0, 2)) > math.sqrt(
                self._ctx.geo_size
            ):
                self.all_solutions_found.append(K)  # keep all solutions

        self.all_solutions_found.append(best)
        self.iteration += 1
