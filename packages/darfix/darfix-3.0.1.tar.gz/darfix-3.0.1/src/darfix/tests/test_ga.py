import numpy
import pytest

from darfix.core.geneticShiftDetection import GeneticShiftDetection as GA


@pytest.fixture
def ga():
    data = numpy.array(
        [
            [
                [1, 2, 3, 4, 5],
                [2, 2, 3, 4, 5],
                [3, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
            [
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 3],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
            [
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [8, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
        ]
    )

    optimal_shift = numpy.array([[0, 0, 0], [0, 0, 0]])
    return GA(data, optimal_shift)


def test_zero_shift_ga(ga):
    """
    Tests the genetic algorithm with a given optimal_shift of 0 and no normal distribution.
    """

    ga.fit((0, 0), [0, 0], 10, 10)

    numpy.testing.assert_equal(ga.optimal_shift, numpy.array(ga.support_))


def test_initialize(ga):
    """
    Tests the initialize method.
    """
    ga.fit((0, 0), [0, 0], 10, 10)
    population = ga.initialize(10)

    assert len(population) == 10


def test_fitness(ga):
    """
    Tests the fitness method.
    """
    ga.fit((0, 0), [0, 0], 10, 10)
    population = numpy.random.random((3, 2, 3))
    scores, population = ga.fitness(population)

    assert len(scores) == 3
    assert len(population) == 3


def test_select(ga):
    """
    Tests the select method.
    """
    ga.fit((0, 0), [0, 0], 10, 10)
    population = numpy.random.random((3, 2, 3))
    scores = numpy.random.random(3)
    population = ga.select(population, scores)

    assert len(population) == 3


def test_crossover_odd(ga):
    """
    Tests the crossover method when the length of the population is odd.
    """
    ga.fit((0, 0), [0, 0], 10, 10)
    population = numpy.random.random((3, 2, 3))
    population = ga.crossover(population)

    assert len(population) == 2


def test_crossover_even(ga):
    """
    Tests the crossover method when the length of the population is even.
    """
    ga.fit((0, 0), [0, 0], 10, 10)
    population = numpy.random.random((4, 2, 3))
    population = ga.crossover(population)

    assert len(population) == 4


def test_mutate(ga):
    """
    Tests the mutate method.
    """
    ga.fit((0, 0), [0, 0], 10, 10)
    population = numpy.random.random((3, 2, 3))
    population = ga.mutate(population)

    assert len(population) == 3


def test_generate(ga):
    """
    Tests the generate method.
    """
    ga.fit((0, 0), [0, 0], 10, 10)
    population = numpy.random.random((3, 2, 3))
    population = ga.generate(population)

    assert len(population) == 2


def test_fit_best(ga):
    """
    Tests correct shape of the chromosomes after fit.
    """
    ga.fit((0, 0), [0, 0], 10, 10)

    assert len(ga.chromosomes_best) == 10
    assert ga.support_.shape == (2, 3)


def test_fit_scores(ga):
    """
    Tests the correct length of the score after fit.
    """
    ga.fit((0, 0), [0, 0], 10, 10)

    assert len(ga.scores_best) == 10
    assert len(ga.scores_avg) == 10
