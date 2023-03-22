import random
import numpy as np
import matplotlib.pyplot as plt
from deap import algorithms, base, creator, tools

creator.create("FitnessMax", base.Fitness, weights=(1.0,))

creator.create("Individual", list, fitness=creator.FitnessMax)

IND_SIZE = 10
toolbox = base.Toolbox()

toolbox.register("attr_float", random.uniform, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_float, n=IND_SIZE)

toolbox.register("population", tools.initRepeat, list, toolbox.individual)
pop = toolbox.population(n=IND_SIZE)
print(pop)
surface = 0.5
top = 2
lakes = 2
flooding = 20
steep_slope = 0.2


def evaluate(individual):
    fitness = 0
    count_top = 0
    count_lakes = 0
    count_flooding = 0
    count_steep_slope = 0

    # считаем количество гор, если гор не ровно нужному количеству, то непригодно
    for i in range(0, len(individual) - 1):
        if individual[i] > individual[i - 1] and individual[i] > individual[i + 1]:
            count_top += 1
    if count_top == top:
        fitness += 1
    else:
        fitness -= 1

    # считаем количество озер, если озер не ровно нужному количеству, то непригодно
    for i in range(0, len(individual) - 1):
        if individual[i] < surface:
            if individual[i] < individual[i - 1] and individual[i] < individual[i + 1]:
                count_lakes += 1
    if count_lakes == lakes:
        fitness += 1
    else:
        fitness -= 1

    #  проверяем процент затопленности, если не ровно, то непригодно
    for i in range(0, len(individual) - 1):
        if individual[i] < surface:
            count_flooding += 1
    new_flooding = count_flooding * 100 / len(individual)
    if flooding - 5 <= new_flooding <= flooding + 5:
        fitness += 1
    else:
        fitness -= 1

    for i in range(0, len(individual) - 1):
        if abs(individual[i] - individual[i - 1]) > steep_slope or abs(
                individual[i] - individual[i + 1]) > steep_slope:
            count_steep_slope += 1
    if count_steep_slope > 0:
        fitness -= 1
    else:
        fitness += 1

    return fitness,


toolbox.register("evaluate", evaluate)

toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", tools.mutUniformInt, low=0, up=1, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

NGEN = 1000
CXPB = 0.9
MUTPB = 0.5

s = tools.Statistics(key=lambda ind: ind.fitness.values)
s.register("mean", np.mean)
s.register("max", np.max)

hof = tools.HallOfFame(1)  # pamatuje si 1 nejlepšího jedince za historii evoluce (i když zanikne)

finalpop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN, stats=s, halloffame=hof)

mean, maximum = logbook.select("mean", "max")

print(hof)

fig, ax = plt.subplots()

ax.plot(range(1, len(hof[0]) + 1), hof[0], color='green', alpha=0.5)

ax.axhline(y=surface, color='blue', linestyle='-')

# Закрашиваем область под линией до максимального значения
ax.fill_between(range(1, len(hof[0]) + 1), hof[0], 0, color='green', alpha=0.5)
ax.fill_between(range(1, len(hof[0]) + 1), 0, surface, color='blue', alpha=0.2)

ax.set_xlim(1, len(hof[0]))
ax.set_ylim(0, 1)
ax.legend()
plt.show()
