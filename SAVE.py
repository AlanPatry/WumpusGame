# -*- coding: utf-8; mode: python -*-

# ENSICAEN
# École Nationale Supérieure d'Ingénieurs de Caen
# 6 Boulevard Maréchal Juin
# F-14050 Caen Cedex France
#
# Artificial Intelligence 2I1AE1

#
# @file agents.py
#
# @author Régis Clouard.
#

from __future__ import print_function
import queue
import random
import copy
import sys
import utils

class Agent:
    """
    The base class for various flavors of the agent.
    This an implementation of the Strategy design pattern.
    """
    def init( self, gridSize ):
        raise Exception("Invalid Agent class, init() not implemented")

    def think( self, percept, isTraining = False ):
        raise Exception("Invalid Agent class, think() not implemented")

def pause( text):
    if sys.version_info.major >= 3:
        input(text)
    else:
        raw_input(text)

class DummyAgent( Agent ):
    """
    An example of simple Wumpus hunter brain: acts randomly...
    """
    isLearningAgent = False

    def init( self, gridSize ):
        pass

    def think( self, percept ):
        return random.choice(['shoot', 'grab', 'left', 'right', 'forward', 'forward'])


#######
####### Exercise: Rational Agent
#######
class RationalAgent( Agent ):
    """
    Your smartest Wumpus hunter brain.
    """
    isLearningAgent = False
    
    def init( self, gridSize ):
        self.state = State('Start', gridSize, 1, 1, 1, False, False, None, 1, None)
        self.count = 0
        self.move = 0
        self.isLearning = True
        self.exitPath = []

        " *** YOUR CODE HERE ***"

    def think( self, percept ):
        """
        Returns the best action regarding the current state of the game.
        Available actions are ['left', 'right', 'forward', 'shoot', 'grab', 'climb'].
        """

        " *** YOUR CODE HERE ***"
        from utils import PriorityQueue
        
        next_actions = []
        

        self.state.update_state_from_percepts(percept)
        
        action = None
        if percept.glitter:
            action = 'grab'
        elif self.state.goldIsGrabbed and self.state.posx == 1 and self.state.posy == 1:
            action = 'climb'
        elif self.state.wumpusLocation != None:
            list = self.solve('kill', self.state)
            for i in list:
                next_actions.append(i.action)
        elif self.state.goldIsGrabbed and self.isLearning:
            list = self.solve('get_out', self.state)
            self.isLearning = False
            for i in list:
                self.exitPath.append(i.action)
        elif not self.state.isMapSafelyExplored() and self.isLearning:
            list = self.solve('explo', self.state)
            for i in list:
                next_actions.append(i.action)
        elif self.isLearning:
            list = self.solve('risk', self.state)
            for i in list:
                next_actions.append(i.action)
         #next_actions = solve(self.state.posx,self.state.posy,self.state.wumpusIsKilled,self.state.goldIsGrabbed)

        #next_actions[0] = 'forward'
        self.state.print_world()
        self.move += 1
        #pause("HIT")

        if action:
            self.updateStateFromAction(action)
            return action

        if self.exitPath:
            action = self.exitPath.pop(0)
            self.updateStateFromAction(action)
            return action

        if next_actions:
            if next_actions[0] != 'Start':
                self.updateStateFromAction(next_actions[0])
                return next_actions[0]
            elif next_actions[1]: 
                self.updateStateFromAction(next_actions[1])
                return next_actions[1]
    
    def solve(self, goal, initial_state):
        from utils import PriorityQueue
        self.count += 1
        # Création de la liste des états à explorer
        open_list = PriorityQueue()
        # Ajout de l'état initial à la liste
        open_list.push([initial_state], self.heuristic(initial_state, goal)+self.count)
        # Création de la liste des états visités
        closed_list = {initial_state:self.heuristic(initial_state, goal)}
        # Boucle de résolution
        while not open_list.isEmpty():
            # Récupération de l'état avec le coût le plus faible
            current_path, cost  = open_list.pop()
            current_state = current_path[-1]
            current_state.set_cell(current_state.posx, current_state.posy, VISITED)
            # Si l'état courant est l'état final (trésor ramassé et retour à la case de départ), renvoi du chemin
            if goal == 'kill' and current_state.wumpusIsKilled:
                return current_path
            elif goal == 'explo' and self.state.worldmap[current_state.posx][current_state.posy] == SAFE:#current_state.isMapSafelyExplored():
                return current_path
            elif goal == 'get_out' and current_state.posx == 1 and current_state.posy == 1:
                return current_path
            elif goal == 'risk' and not self.state.isSure(current_state.posx, current_state.posy):
                return current_path
            else:
                # Génération des états suivants
                for next_state in self.generate_next_states(current_state):
                    if (next_state not in closed_list and next_state not in current_path):
                        
                        # Calcul du coût de l'état suivant
                        next_cost = len(current_path) + self.heuristic(next_state, goal) + cost
                        closed_list = {next_state:next_cost}
                        """if self.move > 10:
                            for i in range(0,len(current_path)):
                                print(current_path[i].action, end=" ")
                            print(next_state.action,end =" ")
                            print(next_cost)"""
                        # Ajout de l'état suivant à la liste des états à explorer
                        open_list.push((current_path + [next_state]), next_cost)
                    else:
                        next_cost = closed_list[next_state]
                        open_list.push((current_path + [next_state]), next_cost)
                #(current_state.action)
            
        return []

    # Fonction de génération des états suivants
    def generate_next_states(self, state):
        next_states = []
        next_x = 0
        next_y = 0
        # Déplacement vers l'avant
        if state.direction == 2:
            next_x, next_y = state.posx, state.posy + 1
        elif state.direction == 1:
            next_x, next_y = state.posx + 1, state.posy
        elif state.direction == 0:
            next_x, next_y = state.posx, state.posy - 1
        elif state.direction == 3:
            next_x, next_y = state.posx - 1, state.posy
        if self.state.is_valid_move(next_x, next_y):
            next_state = State('forward', state.size, state.direction, next_x, next_y, state.wumpusIsKilled, state.goldIsGrabbed, state.wumpusLocation, state.arrowInventory, state)
            next_state.previousCell = (state.posx, state.posy)
            next_states.append(next_state)
        # Rotation à gauche
        if(state.action != 'right'):
            next_direction = rotate(state.direction, 'left')
            next_state = State('left', state.size, next_direction, state.posx, state.posy, state.wumpusIsKilled, state.goldIsGrabbed, state.wumpusLocation, state.arrowInventory, state)
            next_states.append(next_state)
        # Rotation à droite
        if(state.action != 'left'):
            next_direction = rotate(state.direction, 'right')
            next_state = State('right', state.size, next_direction, state.posx, state.posy, state.wumpusIsKilled, state.goldIsGrabbed, state.wumpusLocation, state.arrowInventory, state)
            next_states.append(next_state)
        # Tir
        if (not state.wumpusIsKilled and state.wumpusLocation and distMan(state.posx, state.posy, state.wumpusLocation[0], state.wumpusLocation[1]) == 1):
            if (state.direction == self.state.targetDirection((state.wumpusLocation[0],state.wumpusLocation[1]))):
                next_state = State('shoot', state.size, state.direction, state.posx, state.posy, True, state.goldIsGrabbed, state.wumpusLocation, False, state)
                next_states.append(next_state)
        # Ramassage de l'or
        if (not state.goldIsGrabbed and state.worldmap[state.posx][state.posy] == 'G'):
            next_state = State('grab', state.size, state.direction, state.posx, state.posy, state.wumpusIsKilled, True, state.wumpusLocation, state.arrowInventory, state)
            next_states.append(next_state)
        # Sortir de la grotte
        if (state.goldIsGrabbed and state.posx == 1 and state.posy == 1):
            next_state = State('climb', state.size, state.direction, state.posx, state.posy, state.wumpusIsKilled, True, state.wumpusLocation, state.arrowInventory, state)
            next_states.append(next_state)
        return next_states

    def updateStateFromAction(self, action):
        if action == 'forward':
            self.state.direction = self.state.direction
        elif action == 'right':
            self.state.direction = (self.state.direction+1)%4
        elif action == 'left':
            self.state.direction = (self.state.direction+3)%4

        if action == 'forward':
            cell = self.state.get_forward_position(self.state.posx,self.state.posy,self.state.direction)
            if self.state.worldmap[cell[0]][cell[1]] != WALL:
                self.state.previousCell = (self.state.posx, self.state.posy)
                self.state.posx = cell[0]
                self.state.posy = cell[1]

    def heuristic(self, state, goal):
        cost = 1
        if(state.wumpusIsKilled and state.action == 'kill'):# and not state.previousState.wumpusIsKilled):
            cost -= 50 
        if(state.goldIsGrabbed and state.action == 'grab'):# and not state.previousState.goldIsGrabbed):
            cost -= 50 
        if(state.worldmap[state.posx][state.posy]==SAFE):
            cost -= 3
        elif (not state.isSure(state.posx,state.posy)):
            if(goal == 'risk'):
                cost += 10
            else:
                cost += 100
        if(state.goldIsGrabbed and state.action == 'climb'):
            cost -= 100
        if(goal == 'get_out' and state.action == 'forward'):
            cost -= 7
        return cost
            
    
    


WALL='#'
UNKNOWN='?'
WUMPUSP='w'
WUMPUS='W'
PITP='p'
PIT='P'
WUMPUSPITP='x'
SAFE=' '
VISITED='.'
GOLD='G'

RIGHT  ='right'
LEFT = 'left'
FORWARD = 'forward'
CLIMB = 'climb'
SHOOT = 'shoot'
GRAB = 'grab'

DIRECTIONTABLE = [(0, -1), (1, 0), (0, 1), (-1, 0)] # North, East, South, West

stenchPositions = []


class State():
    def __init__( self, action, gridSize, direction, posx, posy, wumpusIsKilled, goldIsGrabbed, wumpusLocation, arrowInventory, previousState ):
        self.size = gridSize
        self.action = action
        if previousState == None:
            self.worldmap = [[((y in [0, gridSize - 1] or  x in [0, gridSize - 1]) and WALL) or UNKNOWN
                          for x in range(gridSize) ] for y in range(gridSize)]
        else:
            self.worldmap = copy.deepcopy(previousState.worldmap)
        self.direction = direction
        self.posx = posx
        self.posy = posy
        self.wumpusIsKilled = wumpusIsKilled
        self.goldIsGrabbed = goldIsGrabbed
        self.wumpusLocation = wumpusLocation
        self.arrowInventory = arrowInventory
        self.previousCell = (1,1)
        self.domains = [[((y in [0, gridSize - 1] or  x in [0, gridSize - 1]) and WALL) or UNKNOWN
                          for x in range(gridSize) ] for y in range(gridSize)]
        self.previousState = previousState

    def print_world( self ):
        """
        For debugging purpose.
        """
        for y in range(self.size):
            for x in range(self.size):
                print(self.get_cell(x, y) + " ", end=' ')
            print()

    def get_cell( self, x, y ):
        return self.worldmap[x][y]

    def set_cell( self, x, y, value ):
        self.worldmap[x][y] = value

    def get_cell_neighbors( self, x, y ):
        return [(x + dx, y + dy) for (dx,dy) in DIRECTIONTABLE]
    
    def get_forward_position( self, x, y, direction ):
        (dx, dy) = DIRECTIONTABLE[direction]
        return (x + dx, y + dy)

    def from_direction_to_action( self, direction ):
        if direction == self.direction:
            return FORWARD
        elif direction == (self.direction + 1) % 4:
            return RIGHT
        elif direction == (self.direction + 2) % 4:
            return RIGHT
        else:
            return LEFT
        

    def targetDirection(self, position):
        delta = (self.posx - position[0], self.posy - position[1])
        if(delta[0] == 0):
            if(delta[1] < 0):
                return 2
            else:
                return 0
        elif(delta[1] == 0):
            if(delta[1] < 0):
                return 3
            else:
                return 1
        return -1

    def update_state_from_percepts( self, percept ):
        """
        Updates the current environment with regards to the percept information.
        """
        " *** YOUR CODE HERE ***"
        
        self.set_cell(self.posx,self.posy,VISITED)
        if percept.breeze:
            for cell in self.get_cell_neighbors(self.posx,self.posy):
                if(self.worldmap[cell[0]][cell[1]] == UNKNOWN):
                    self.set_cell(cell[0] ,cell[1],PITP)
                elif (self.worldmap[cell[0]][cell[1]] == WUMPUSP):
                    self.set_cell(cell[0] ,cell[1],WUMPUSPITP)
                    
        if percept.stench:
            for cell in self.get_cell_neighbors(self.posx,self.posy):
                if(self.worldmap[cell[0]][cell[1]] == UNKNOWN):
                    if(self.wumpusLocation == None):
                        self.set_cell(cell[0] ,cell[1],WUMPUSP)
                elif (self.worldmap[cell[0]][cell[1]] == PITP):
                    if(self.wumpusLocation == None):
                        self.set_cell(cell[0] ,cell[1],WUMPUSPITP)
                if((self.posx,self.posy) not in stenchPositions):
                    self.updateWumpusConsistency()
        if percept.glitter:
            self.set_cell(self.posx, self.posy, GOLD) 
            self.goldIsGrabbed = True

        if percept.scream:
            self.wumpusIsKilled = True
            self.set_cell(self.wumpusLocation[0],self.wumpusLocation[1], SAFE)
            self.wumpusLocation = None

        if not percept.stench and not percept.breeze and not percept.glitter and not percept.scream:
            for cell in self.get_cell_neighbors(self.posx,self.posy):
                if (self.worldmap[cell[0]][cell[1]] != VISITED and self.worldmap[cell[0]][cell[1]] != WALL):
                    self.set_cell(cell[0], cell[1], SAFE)



    def updateWumpusConsistency(self):
        wumpusP = []
        if(self.wumpusLocation == None and not self.wumpusIsKilled):
            stenchPositions.append((self.posx,self.posy))
            if(len(stenchPositions)>1):
                for neighborA in self.get_cell_neighbors(stenchPositions[0][0], stenchPositions[0][1]):
                    for neighborB in self.get_cell_neighbors(stenchPositions[1][0], stenchPositions[1][1]):
                        if(neighborA == neighborB):
                            if(not self.isSure(neighborA[0], neighborA[1])):
                                wumpusP.append(neighborA)
                if(len(wumpusP)==1):
                    self.set_cell(wumpusP[0][0], wumpusP[0][1], WUMPUS)
                    self.wumpusLocation = (wumpusP[0][0],wumpusP[0][1])
                elif(len(stenchPositions)==3):
                    for neighborC in self.get_cell_neighbors(stenchPositions[2][0], stenchPositions[2][1]):        
                        if(neighborC in wumpusP):
                            self.set_cell(neighborC[0], neighborC[1], WUMPUS)
                            self.wumpusLocation = (neighborC[0], neighborC[1])
        if(self.wumpusLocation != None or self.wumpusIsKilled):
            for i in range (self.size):
                for j in range (self.size):
                    if(self.worldmap[i][j] == WUMPUSPITP):
                        self.set_cell(i,j,PITP)
                    elif(self.worldmap[i][j] == WUMPUSP):
                        self.set_cell(i,j,SAFE)
        
    def isSure(self, x, y):
        return self.worldmap[x][y] == SAFE or self.worldmap[x][y] == VISITED or self.worldmap[x][y] == GOLD 

    def isGoal(self, position):
        if not self.goldIsGrabbed:
            return self.worldmap[position[0]][position[1]]=='G'
        else:
            return position[0] == 1 and position[1] == 1

    # Fonction de vérification de la validité d'un déplacement
    def is_valid_move(self, x, y):
        return x >= 1 and y >= 1 and x < self.size and y < self.size

    def isMapSafelyExplored(self):
        explored = True
        #self.print_world()
        for i in range (self.size):
            for j in range (self.size):
                #if distMan(i,j,self.posx,self.posy) < 6:
                    if self.worldmap[i][j] == SAFE:
                        explored = False
        return explored


def rotate(baseDirection, goalDirection):
    if goalDirection == 'left':
        return (baseDirection + 3) % 4
    elif goalDirection == 'right':
        return (baseDirection + 1) % 4

def distMan(Ax, Ay, Bx, By):
    return abs(Ax - Bx) + abs(Ay - By) 

