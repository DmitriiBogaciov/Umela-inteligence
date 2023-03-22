import random

import numpy as np

from deap import base, creator, tools, algorithms

STEPSNUM = 100


# vždy kooperuje
def always_cooperate(myhistory, otherhistory):
    return 0


# náhodná odpověď
def random_answer(myhistory, otherhistory):
    p = random.random()
    if p < 0.5:
        return 1

    return 0

def lookup_table_strategy(table, myhistory, otherhistory):
    if not myhistory or not otherhistory:
        return 0  # cooperate by default for the first move
    last_my_move, last_opponent_move = myhistory[-1], otherhistory[-1]
    return table.get((last_my_move, last_opponent_move), 0)  # cooperate by default if the key is not found in the table


def rozdej_skore(tah1, tah2):
    # 1 = zradi, 0 = nezradi

    skores = (0, 0)

    if (tah1 == 1) and (tah2 == 1):
        skores = (2, 2)

    if (tah1 == 1) and (tah2 == 0):
        skores = (0, 3)

    if (tah1 == 0) and (tah2 == 1):
        skores = (3, 0)

    if (tah1 == 0) and (tah2 == 0):
        skores = (1, 1)

    return skores


def play(f1, f2, stepsnum):
    skore1 = 0
    skore2 = 0

    historie1 = []
    historie2 = []

    for i in range(stepsnum):
        tah1 = f1(historie1, historie2)
        tah2 = f2(historie2, historie1)

        s1, s2 = rozdej_skore(tah1, tah2)
        skore1 += s1
        skore2 += s2

        historie1.append(tah1)
        historie2.append(tah2)

    return skore1, skore2


# seznam funkci o testování
ucastnici = [always_cooperate, random_answer]

def evaluate(individual):
    table = {(0, 0): individual[0], (0, 1): individual[1], (1, 0): individual[2], (1, 1): individual[3]}
    strategy = lambda myhistory, otherhistory: lookup_table_strategy(table, myhistory, otherhistory)
    total_score = 0
    for opponent in ucastnici:
        my_score, _ = play(strategy, opponent, STEPSNUM)
        total_score += my_score
    return total_score,


# Create a fitness maximizing strategy
creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("binary_gene", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.binary_gene, n=4)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", tools.mutUniformInt, low=0, up=1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)


# Example usage:
# Define a lookup table (feel free to modify it)
example_table = {
    (0, 0): 0,  # cooperate if both players cooperated last turn
    (0, 1): 1,  # betray if the agent cooperated and the opponent betrayed last turn
    (1, 0): 0,  # cooperate if the agent betrayed and the opponent cooperated last turn
    (1, 1): 1,  # betray if both players betrayed last turn
}

# Partially apply the lookup table to create a new strategy function
NGEN = 100
CXPB = 0.9
MUTPB = 0.3

s = tools.Statistics(key=lambda ind: ind.fitness.values)
s.register("mean", np.mean)
s.register("max", np.max)

hof = tools.HallOfFame(1)  # remembers the best individual throughout evolution history (even if it disappears)

pop = toolbox.population(n=100)
finalpop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN, stats=s, halloffame=hof)

mean, maximum = logbook.select("mean", "max")
print("Evolution results:")
print("Mean:", mean)
print("Max:", maximum)
print("Best individual:", hof)

best_individual = hof[0]
best_table = {(0, 0): best_individual[0], (0, 1): best_individual[1], (1, 0): best_individual[2],
              (1, 1): best_individual[3]}


def betray(my_history, opponent_history):
    return lookup_table_strategy(best_table, my_history, opponent_history)


# Add the new strategy to the list of participants


ucastnici.append(betray)

# funkce se mohou v seznamu i opakovat
# ucastnici = [always_cooperate, always_cooperate, random_answer, random_answer, random_answer]



l = len(ucastnici)
skores = [0 for i in range(l)]

print("=========================================")
print("Turnaj")
print("hra délky:", STEPSNUM)
print("-----------------------------------------")

for i in range(l):
    for j in range(i + 1, l):
        f1 = ucastnici[i]
        f2 = ucastnici[j]
        skore1, skore2 = play(f1, f2, STEPSNUM)
        print(f1.__name__, "x", f2.__name__, " ", skore1, ":", skore2)
        skores[i] += skore1
        skores[j] += skore2

print("=========================================")
print("= Výsledné pořadí")
print("-----------------------------------------")

# setrideni indexu vysledku
index = sorted(range(l), key=lambda k: skores[k])

poradi = 1
for i in index:
    f = ucastnici[i]
    print(poradi, ".", f.__name__, ":", skores[i])
    poradi += 1
