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
        return input(text)
    else:
        return raw_input(text)

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
        self.state = State('Start', gridSize, 1, (1, 1), False, False, None, 1, None)
        self.count = 0
        self.move = 0
        self.isLearning = True
        self.exitPath = []


    def think( self, percept ):
        """
        Returns the best action regarding the current state of the game.
        Available actions are ['left', 'right', 'forward', 'shoot', 'grab', 'climb'].
        """

        from utils import PriorityQueue
        
        next_actions = []
        action = None 

        self.state.update_state_from_percepts(percept)
        
        # Grab gold
        if percept.glitter:
            action = 'grab'

        # Exit the cave
        elif self.state.goldIsGrabbed and self.state.cell == (1,1):
            action = 'climb'

        # Kill the Wumpus 
        elif self.state.wumpusLocation != None:
            list = self.solve('kill', self.state)
            for i in list:
                next_actions.append(i.action)

        # Get the shortest path to exit (computed once)
        elif self.state.goldIsGrabbed and self.state.wumpusIsKilled and self.isLearning:
            list = self.solve('get_out', self.state)
            self.isLearning = False
            for i in list:
                self.exitPath.append(i.action)
                
        # Get the shortest path to a SAFE cell 
        elif not self.state.isMapSafelyExplored() and self.isLearning:
            list = self.solve('explo', self.state)
            for i in list:
                next_actions.append(i.action)

        # If no more options, get the shortest path to try a non SAFE cell
        elif self.isLearning:
            list = self.solve('risk', self.state)
            for i in list:
                next_actions.append(i.action)

        self.move += 1

        #For debug purpose 
        #self.state.print_world()
        #pause("HIT")

        if action:
            self.updateStateFromAction(action)
            # Display score
            if(action == 'climb'):
                score = self.state.wumpusIsKilled*1000 + 1000 - self.move
                print("========================\n Score : ", score)
                print("Nb etat explorés : ",self.count)
            return action

        if self.exitPath:
            action = self.exitPath.pop(0)
            self.updateStateFromAction(action)
            return action

        if next_actions:
            self.updateStateFromAction(next_actions[1])
            return next_actions[1]
    
    def solve(self, goal, initial_state):
        """
        Return the ordered list of actions to achieve goal
        """        
        from utils import PriorityQueue
        # Open list initialisation
        open_list = PriorityQueue()
        open_list.push([initial_state], self.heuristic(initial_state, goal)+self.move)
        # Already visited states
        closed_list = {initial_state}
        # Searching loop
        while not open_list.isEmpty():
            # Explored state counter
            self.count += 1
            # Get the lower cost state
            current_path, cost  = open_list.pop()
            current_state = current_path[-1]
            current_state.set_cell(current_state.cell, VISITED)
            # Verify if goal is achieved 
            if goal == 'kill' and current_state.wumpusIsKilled:
                return current_path
            if goal == 'explo' and self.state.isSafe(current_state.cell):#current_state.isMapSafelyExplored():
                return current_path
            if goal == 'get_out' and current_state.getPos() == (1,1):
                return current_path
            if goal == 'risk' and not self.state.isSure(current_state.cell):
                if (self.heuristic(current_state, goal) < 29):
                    return current_path
            else:
                # New states generation
                for next_state in self.generate_next_states(current_state, goal):
                    if (next_state not in closed_list):
                        # Compute new state cost 
                        next_cost = len(current_path) + self.heuristic(next_state, goal) + cost
                        closed_list = {next_state}
                        # Add new state to open list 
                        open_list.push((current_path + [next_state]), next_cost)
        print("No Solution found")
        return [] # No solution


    def generate_next_states(self, state, goal):
        """
        Return the list of all valid adjacent and non redondant states
        """
        next_states = []

        # Move forward
        nextCell = state.get_forward_position(state.cell, state.direction)
        if self.state.is_valid_move(nextCell):
            if goal == 'get_out' or goal == 'explo':
                if state.isSure(nextCell):
                    next_state = State('forward', state.size, state.direction, nextCell, state.wumpusIsKilled, state.goldIsGrabbed, state.wumpusLocation, state.arrowInventory, state)
                    next_states.append(next_state)
            elif state.isRisky(nextCell):
                next_state = State('forward', state.size, state.direction, nextCell, state.wumpusIsKilled, state.goldIsGrabbed, state.wumpusLocation, state.arrowInventory, state)
                next_states.append(next_state)

        # Turn left
        if(state.action != 'right'):
            if(state.previousState and state.previousState.action != 'left') or state.action != 'left':
                next_direction = rotate(state.direction, 'left')
                next_state = State('left', state.size, next_direction, state.cell, state.wumpusIsKilled, state.goldIsGrabbed, state.wumpusLocation, state.arrowInventory, state)
                next_states.append(next_state)

        # Turn right
        if(state.action != 'left'):
            if(state.previousState and state.previousState.action != 'right') or state.action != 'right':
                next_direction = rotate(state.direction, 'right')
                next_state = State('right', state.size, next_direction, state.cell, state.wumpusIsKilled, state.goldIsGrabbed, state.wumpusLocation, state.arrowInventory, state)
                next_states.append(next_state)

        # Shoot
        if (not state.wumpusIsKilled and state.wumpusLocation and distMan(state.cell, state.wumpusLocation) == 1):
            if (state.direction == self.state.targetDirection((state.wumpusLocation))):
                next_state = State('shoot', state.size, state.direction, state.cell, True, state.goldIsGrabbed, state.wumpusLocation, False, state)
                next_states.append(next_state)

        # Grab the gold
        if (not state.goldIsGrabbed and state.get_cell(state.cell) == GOLD):
            next_state = State('grab', state.size, state.direction, state.cell, state.wumpusIsKilled, True, state.wumpusLocation, state.arrowInventory, state)
            next_states.append(next_state)

        # Get out the cave 
        if (state.goldIsGrabbed and state.wumpusIsKilled and state.getPos() == (1,1)):
            next_state = State('climb', state.size, state.direction, state.cell, state.wumpusIsKilled, True, state.wumpusLocation, state.arrowInventory, state)
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
            cell = self.state.get_forward_position(self.state.cell, self.state.direction)
            if self.state.get_cell(cell) != WALL:
                self.state.cell = cell

    def heuristic(self, state, goal):
        """
        Estimate the value of a state
        """
        cost = 1

        if(state.wumpusIsKilled and state.action == 'kill'):
            cost -= 50 

        if(state.goldIsGrabbed and state.action == 'grab'):
            cost -= 50 

        if(state.goldIsGrabbed and state.action == 'climb'):
            cost -= 50

        if(self.state.isSafe(state.cell)):
            cost -= 1

        elif(self.state.isRisky(state.cell)):
            for cell in state.get_cell_neighbors(state.cell):
                if(cell in breezePositions or (cell in stenchPositions and not state.wumpusIsKilled)):
                    if(goal == 'risk'):
                        cost += 15
                    else:
                        cost += 200
            

        if(goal == 'get_out'):
            cost += distMan(state.cell, (1,1))
            if(state.action == 'forward'):
                cost -= 10

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
breezePositions = []



class State():
    def __init__( self, action, gridSize, direction, cell, wumpusIsKilled, goldIsGrabbed, wumpusLocation, arrowInventory, previousState ):
        self.size = gridSize
        self.action = action
        if previousState == None:
            self.worldmap = [[((y in [0, gridSize - 1] or  x in [0, gridSize - 1]) and WALL) or UNKNOWN
                          for x in range(gridSize) ] for y in range(gridSize)]
        else:
            self.worldmap = copy.deepcopy(previousState.worldmap)
        self.direction = direction
        self.cell = cell
        self.wumpusIsKilled = wumpusIsKilled
        self.goldIsGrabbed = goldIsGrabbed
        self.wumpusLocation = wumpusLocation
        self.arrowInventory = arrowInventory
        self.previousState = previousState

    def print_world( self ):
        """
        For debugging purpose.
        """
        for y in range(self.size):
            for x in range(self.size):
                print(self.get_cell((x, y)) + " ", end=' ')
            print()

    def get_cell( self, cell ):
        return self.worldmap[cell[0]][cell[1]]

    def set_cell( self, cell, value ):
        self.worldmap[cell[0]][cell[1]] = value

    def get_cell_neighbors( self, cell ):
        return [(cell[0] + dx, cell[1] + dy) for (dx,dy) in DIRECTIONTABLE]
    
    def get_forward_position( self, cell, direction ):
        (dx, dy) = DIRECTIONTABLE[direction]
        return (cell[0] + dx, cell[1] + dy)

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
        """
        Return the direction (int) of the given cell if aligned or -1
        """
        delta = (self.cell[0] - position[0], self.cell[1] - position[1])
        if(delta[0] == 0):
            if(delta[1] < 0):
                return 2
            else:
                return 0
        elif(delta[1] == 0):
            if(delta[0] < 0):
                return 1
            else:
                return 3
        return -1

    def update_state_from_percepts( self, percept ):
        """
        Updates the current environment with regards to the percept information.
        """
        self.set_cell(self.cell, VISITED)

        #Pit perceived
        if percept.breeze:
            if self.cell not in breezePositions:
                breezePositions.append(self.cell)
            for cell in self.get_cell_neighbors(self.cell):
                if(self.get_cell(cell) == UNKNOWN):
                    self.set_cell(cell, PITP)
                elif (self.get_cell(cell) == WUMPUSP):
                    self.set_cell(cell, WUMPUSPITP)
                    
        #Wumpus perceived
        if percept.stench and self.getPos() not in stenchPositions:
            if(self.wumpusLocation == None):
                for cell in self.get_cell_neighbors(self.cell):
                    if(self.get_cell(cell) == UNKNOWN):
                        self.set_cell(cell,WUMPUSP)
                    elif (self.get_cell(cell) == PITP):
                        self.set_cell(cell,WUMPUSPITP)
                self.updateWumpusConsistency()

        #Gold perceived
        if percept.glitter:
            self.set_cell(self.cell, GOLD) 
            self.goldIsGrabbed = True

        #Wumpus dead
        if percept.scream:
            self.wumpusIsKilled = True
            self.set_cell(self.wumpusLocation, SAFE)
            self.wumpusLocation = None

        #No detection -> SAFE 
        if not percept.stench and not percept.breeze and not percept.glitter:
            for cell in self.get_cell_neighbors(self.cell):
                if (self.get_cell(cell) != VISITED and self.get_cell(cell) != WALL):
                    self.set_cell(cell, SAFE)
        
        self.updatePitConsistency()

    def updatePitConsistency(self):
        """
        Try to locate pit based on breeze detections and remove unconsistent pit locations
        """
        
        for breeze in breezePositions:
            safeSpot = 0
            for cell in self.get_cell_neighbors(breeze):
                if self.isSure(cell) or self.get_cell(cell) == WALL:
                    safeSpot += 1
            if safeSpot == 3:
                for cell in self.get_cell_neighbors(breeze):
                    if self.isRisky(cell):
                        self.set_cell(cell, PIT)

    def updateWumpusConsistency(self):
        """
        Try to locate Wumpus based on Stench detections and remove unconsistent Wumpus locations
        """
        wumpusP = []

        #Wumpus triangulation 
        if(self.cell not in stenchPositions and self.wumpusLocation == None and not self.wumpusIsKilled):
            stenchPositions.append(self.cell)
            if(len(stenchPositions) > 1):
                for neighborA in self.get_cell_neighbors(stenchPositions[0]):
                    for neighborB in self.get_cell_neighbors(stenchPositions[1]):
                        if(neighborA == neighborB):
                            if(not self.isSure(neighborA)):
                                wumpusP.append(neighborA)
                if(len(wumpusP)==1):
                    self.set_cell(wumpusP[0], WUMPUS)
                    self.wumpusLocation = (wumpusP[0])
                elif(len(stenchPositions) == 3):
                    for neighborC in self.get_cell_neighbors(stenchPositions[2]):        
                        if(neighborC in wumpusP):
                            self.set_cell(neighborC, WUMPUS)
                            self.wumpusLocation = (neighborC)

        #Remove unconsistent positions
        if(self.wumpusLocation != None or self.wumpusIsKilled):
            for i in range (self.size):
                for j in range (self.size):
                    if(self.get_cell((i,j)) == WUMPUSPITP):
                        self.set_cell((i,j),PITP)
                    elif(self.get_cell((i,j)) == WUMPUSP):
                        self.set_cell((i,j),SAFE)
        
    def isSure(self, cell):
        return self.get_cell(cell) == SAFE or self.get_cell(cell) == VISITED or self.get_cell(cell) == GOLD

    def isSafe(self, cell):
        return self.get_cell(cell) == SAFE
    
    def isRisky(self, cell):
        return self.get_cell(cell) == WUMPUSP or self.get_cell(cell) == PITP

    def getPos(self):
        return (self.cell)

    def is_valid_move(self, cell):
        return self.get_cell(cell) != WALL

    def isMapSafelyExplored(self):
        """
        True if there's no more SAFE cell to explore
        """
        explored = True
        for i in range (self.size):
            for j in range (self.size):
                if self.get_cell((i,j)) == SAFE:
                    explored = False
        return explored

    def isNeighborsSafelyExplored(self, dist):
        """
        True if there's no more SAFE cell to explore
        """
        explored = True
        for i in range (self.size):
            for j in range (self.size):
                if(distMan(self.cell, (i,j)) < dist):
                    if self.get_cell((i,j)) == SAFE:
                        explored = False
        return explored


def rotate(baseDirection, goalDirection):
    if goalDirection == 'left':
        return (baseDirection + 3) % 4
    elif goalDirection == 'right':
        return (baseDirection + 1) % 4

def distMan(cellA, cellB):
    """
    Return Manhattan distance between cell A and cell B
    """
    return abs(cellA[0] - cellB[0]) + abs(cellA[1] - cellB[1]) 

