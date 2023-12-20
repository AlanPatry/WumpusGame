#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-

# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1
#

#
# @file wumpus.py
#
# @author Régis Clouard
#

from __future__ import print_function
import sys
import random

if sys.version_info.major >= 3:
    import tkinter as Tkinter
else:
    import Tkinter

from wumpusworld import WumpusFrame

class Wumpus:
    def __init__( self, solver, function = None ):
        self.__solver = solver
        self.__heuristicFunction = function

def run_agents( agent, speed, width, timeout, seed, numGames, numTraining ):
    """ The real main. """
    global currentAgent
    global numberOfGames
    global numberOfTraining
    global animationSpeed
    global root
    global gameWidth
    global currentEpisode

    currentAgent = agent
    numberOfGames = numGames
    numberOfTraining = numTraining
    gameWidth = width
    if seed >= 0:
        random.seed(seed)
    if speed < 0:
        speed = 0
    if speed > 100:
        speed = 100
    animationSpeed = speed
    root = Tkinter.Tk()
    root.wm_title('Wumpus World')
    currentAgent.init(width)
    currentEpisode = 0
    next_episode()
    root.mainloop()

def next_episode():
    global currentAgent
    global currentFrame
    global numberOfGames
    global numberOfTraining
    global animationSpeed
    global rootFrame
    global gameWidth
    global currentEpisode

    if currentEpisode >= numberOfGames:
        rootFrame.quit()
        return
    if currentEpisode > 0:
        print("Score:", currentFrame.world.score)
    if numberOfGames > 1:
        print("episode", currentEpisode)
    isTraining = numberOfTraining > 0 and currentEpisode < numberOfTraining
    if isTraining:
        print("Learning... ")
        currentSpeed = 100
        currentQuiet = True
        root.withdraw()
    else:
        currentSpeed = animationSpeed
        currentQuiet = False
        root.update()
        root.deiconify()
    isLearningAgent = currentAgent.isLearningAgent
    currentAgent.init(gameWidth)
    rootFrame = Tkinter.Frame(root)
    currentFrame = WumpusFrame(rootFrame, gameWidth, currentSpeed, currentAgent, currentQuiet, currentEpisode, isTraining, isLearningAgent, next_episode)
    currentEpisode += 1

def default( str ):
    return str + ' [Default: %default]'

def read_command( argv ):
    """ Processes the command used to run Wumpus from the command line. """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python wumpus.py <options>
    EXAMPLES:   python wumpus.py --agent DummyAgent
                OR  python wumpus.py -a DummyAgent
                    - run wumpus with the dummy agent
    """
    parser = OptionParser(usageStr)
    
    parser.add_option('-a', '--agent', dest='agent',
                      help=default('the agent to use'),
                      metavar='TYPE', default='DummyAgent')
    parser.add_option('-w', '--width', dest='width', metavar='n',
                      help=default('World width'), default=4)
    parser.add_option('-s', '--speed', dest='speed', metavar='n',
                      help=default('Speed in percent of maximum speed'), default=70)
    parser.add_option('-t', '--timeout', dest='timeout', metavar='n',
                      help=default('Maximum search time'), default=2000)
    parser.add_option('-x', '--numTraining', dest='numTraining', type='int',
                      help='How many episodes are training (suppresses output)', default=0)
    parser.add_option('-g', '--debugging', dest='seed', metavar='n',
                      help='For debuging purpose, set the random seed to the same seed which generates the same world or the same sequence of worlds', default=-1)
    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    
    options, otherjunk = parser.parse_args(argv)

    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()

    if options.numGames <= 0:
        raise Exception('Bad number of games: ' + str(options.numGames))

    if options.numTraining >= options.numGames:
        raise Exception('Bad number of training: ' + str(options.numTraining) + ' since the number of games is lony ' + str(options.numGames))

    # Choose a Wumpus solver
    try:
        module = __import__('agent')
        if options.agent in dir(module):
            agent = getattr(module, options.agent)
            args['agent'] = agent()
        else:
            raise Exception('Unknown agent: ' + options.agent)
    except ImportError:
        raise Exception('No file agent.py')
    
    args['width'] = int(options.width) + 2 # Add the borders.
    args['speed'] = int(options.speed)
    args['timeout'] = int(options.timeout)
    args['seed'] = int(options.seed)
    args['numGames'] = options.numGames
    args['numTraining'] = options.numTraining
    return args

if __name__ == '__main__':
    """ The main function called when wumpus.py is run
    from the command line:

    > python wumpus.py

    See the usage string for more details.

    > python wumpus.py --help
    > python wumpus.py -h """
    args = read_command(sys.argv[1:]) # Get game components based on input
    print("\n-------------------------------------------------------")
    for arg in sys.argv:
        print(arg, end=' ')
    print("\n-------------------------------------------------------")
    run_agents(**args)
