import neat
import random
import pickle
import pandas as pd
from numba import jit
from functools import cache


tracked_dataframe = pd.DataFrame({'Generation': [], 'Average Fitness': [], 'Best Fitness (All Time)': [], 'Best Fitness (Generation)': [], 'Genome Count': []}).set_index("Generation")
best_fit = 0
generation = 0


@cache
@jit(nopython=True)
def findWinner(gameArray: tuple):
    for i in [-1, 1]:
        for j in range(3):
            if gameArray[j*3] == i and gameArray[j*3+1] == i and gameArray[j*3+2] == i:  # horizontal
                return i
            elif gameArray[j] == i and gameArray[j+3] == i and gameArray[j+6] == i:  # vertical
                return i
        if gameArray[0] == i and gameArray[4] == i and gameArray[8] == i:  # diagonal
            return i
        elif gameArray[2] == i and gameArray[4] == i and gameArray[6] == i:  # diagonal
            return i
    for i in range(9):
        if gameArray[i] == 0:
            return 0  # Game is not over
    return 3  # Game is a draw


def stage_neat():
    """" This manages the NEAT stuff:
    - Makes a config
    - Gives output like statistics
    - Trains the genomes
    - Develops the genomes
    - Et cetera
    """

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, "config-feedforward.txt")

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())
    winner = p.run(main, 10000)

    # Save the winner object
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
    print("Hit threshold maximum.")


def main(genomes: list, config):
    global best_fit, generation, tracked_dataframe

    emptyGameArray = [0] * 9
    playerNum = 1
    aiNum = -1
    gameArrayArray = {}
    netArray = {}
    movesArray = {}
    streakArray = {}
    generation += 1

    for gid, g in genomes:
        movesArray[gid] = 0
        streakArray[gid] = 0
        gameArrayArray[gid] = emptyGameArray.copy()
        netArray[gid] = neat.nn.FeedForwardNetwork.create(g, config)
        genomes[genomes.index((gid, g))][1].fitness = 0

    while len(gameArrayArray):
        print(len(gameArrayArray))
        for gid, g in genomes:
            if gid in gameArrayArray:
                gameArray = gameArrayArray[gid]
                randint = random.randint(0, 8)
                while gameArray[randint] != 0:
                    randint = random.randint(0, 8)
                gameArray[randint] = playerNum
                cell = round((netArray[gid].activate(gameArray)[0] + 1) / 2 * 8)
                if gameArray[cell] != 0:
                    g.fitness = 0
                    del gameArrayArray[gid]
                    continue

                gameArray[cell] = aiNum
                winner = findWinner(tuple(gameArray))
                if winner != 0:
                    if winner == aiNum:
                        streakArray[gid] += 1
                        print(f"genome {gid} won! ({streakArray[gid]}x)")
                        # (1 - movesArray[gid] / 5) *
                        g.fitness += 50 * streakArray[gid]
                    elif winner == 3:
                        g.fitness += 10
                    elif winner == playerNum:
                        del gameArrayArray[gid]
                        continue
                    gameArray = emptyGameArray.copy()
                    movesArray[gid] = -1
                gameArrayArray[gid] = gameArray
                movesArray[gid] += 1
    bfg = max(genomes, key=lambda x: x[1].fitness)[1]
    best_fit = max(bfg.fitness, best_fit)
    best_fit_gen = bfg.fitness

    with open("reinforced_tictactoe.pkl", "wb") as f:
        pickle.dump(max(genomes, key=lambda x: x[1].fitness)[1], f)

    tracked_dataframe = tracked_dataframe.append(pd.DataFrame({'Generation': [generation], 'Average Fitness': [round(sum([x[1].fitness for x in genomes])/len(genomes), 2)], 'Best Fitness (All Time)': [best_fit], 'Best Fitness (Generation)': [best_fit_gen], 'Genome Count': [len(genomes)]}).set_index('Generation'))
    tracked_dataframe.to_excel("reinforced_tictactoe_statistics.xlsx", index=["Generation"])


if __name__ == "__main__":
    stage_neat()