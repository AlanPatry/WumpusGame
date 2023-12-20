import heapq

# Classe représentant un état du jeu
class State:
    def __init__(self, x, y, direction, gold_collected, wumpus_killed, previous_state):
        self.x = x
        self.y = y
        self.direction = direction
        self.gold_collected = gold_collected
        self.wumpus_killed = wumpus_killed
        self.previous_state = previous_state

    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y and self.direction == other.direction and
                self.gold_collected == other.gold_collected and self.wumpus_killed == other.wumpus_killed)

    def __hash__(self):
        return hash((self.x, self.y, self.direction, self.gold_collected, self.wumpus_killed))

    # Fonction de calcul de l'heuristique
    def heuristic(state, wumpus_pos, pit_positions, gold_pos):
        # Calcul de la distance au Wumpus
        wumpus_distance = abs(state.x - wumpus_pos[0]) + abs(state.y - wumpus_pos[1])
        # Calcul de la distance aux pits
        pit_distances = [abs(state.x - pit[0]) + abs(state.y - pit[1]) for pit in pit_positions]
        # Sélection de la distance minimale
        pit_distance = min(pit_distances) if pit_distances else 0
        # Calcul de la distance à l'or
        gold_distance = abs(state.x - gold_pos[0]) + abs(state.y - gold_pos[1])
        # Calcul du coût total (distance au Wumpus + distance aux pits + distance à l'or)
        cost = wumpus_distance + pit_distance + gold_distance
        # Ajout d'un coût supplémentaire si le Wumpus n'a pas encore été tué
        if not state.wumpus_killed:
            cost += 1
        return cost

    # Fonction de résolution du jeu
    def solve_wumpus(start_x, start_y, wumpus_pos, pit_positions, gold_pos):
        # Création de la liste des états à explorer
        states = []
        # Ajout de l'état initial à la liste
        initial_state = State(start_x, start_y, 'right', False, False)
        heapq.heappush(states, (heuristic(initial_state, wumpus_pos, pit_positions, gold_pos), initial_state))
        # Création de la liste des états visités
        visited_states = set()

        # Boucle de résolution
        while states:
            # Récupération de l'état avec le coût le plus faible
            cost, current_state = heapq.heappop(states)
            # Vérification si l'état courant a déjà été visité
            if current_state in visited_states:
                continue
            # Ajout de l'état courant aux états visités
            visited_states.add(current_state)
            # Si l'état courant est l'état final (trésor ramassé et retour à la case de départ), renvoi du chemin
            if current_state.gold_collected and current_state.x == start_x and current_state.y == start_y:
                return path(current_state)

            # Génération des états suivants
            for next_state in generate_next_states(current_state, wumpus_pos, pit_positions, gold_pos):
                # Calcul du coût de l'état suivant
                next_cost = cost + 1 + heuristic(next_state, wumpus_pos, pit_positions, gold_pos)
                # Ajout de l'état suivant à la liste des états à explorer
                heapq.heappush(states, (next_cost, next_state))

    def think(self, percept):
        # Mise à jour de la position du Wumpus si un cri est perçu
        if percept.scream:
            self.wumpus_pos = None
        # Mise à jour de la carte de l'environnement
        self.update_map(percept)
        # Vérification de la présence de l'or
        if percept.glitter:
            return 'grab'
        # Vérification de la possibilité de sortir de la grotte
        if self.x == 1 and self.y == 1:
            return 'climb'
        # Résolution du jeu avec l'algorithme A*
        next_action = solve_wumpus(self.x, self.y, self.wumpus_pos, self.pit_positions, self.gold_pos)
        # Si aucune solution n'a été trouvée, l'agent reste sur place
        if not next_action:
            return 'forward'
        # Renvoi de l'action suivante
        return next_action[0]

    # Fonction de génération des états suivants
    def generate_next_states(state, wumpus_pos, pit_positions, gold_pos):
        next_states = []
        # Déplacement vers l'avant
        if state.direction == 'up':
            next_x, next_y = state.x, state.y + 1
        elif state.direction == 'right':
            next_x, next_y = state.x + 1, state.y
        elif state.direction == 'down':
            next_x, next_y = state.x, state.y - 1
        elif state.direction == 'left':
            next_x, next_y = state.x - 1, state.y
        if is_valid_move(next_x, next_y):
            next_state = State(next_x, next_y, state.direction, state.gold_collected, state.wumpus_killed, state)
            next_states.append(next_state)
        # Rotation à gauche
        next_direction = rotate_left(state.direction)
        next_state = State(state.x, state.y, next_direction, state.gold_collected, state.wumpus_killed, state)
        next_states.append(next_state)
        # Rotation à droite
        next_direction = rotate_right(state.direction)
        next_state = State(state.x, state.y, next_direction, state.gold_collected, state.wumpus_killed, state)
        next_states.append(next_state)
        # Tir
        if not state.wumpus_killed and distance(state, wumpus_pos) == 1:
            next_state = State(state.x, state.y, state.direction, state.gold_collected, True, state)
            next_states.append(next_state)
        # Ramassage de l'or
        if not state.gold_collected and (state.x, state.y) == gold_pos:
            next_state = State(state.x, state.y, state.direction, True, state.wumpus_killed, state)
            next_states.append(next_state)
        return next_states

    # Fonction de vérification de la validité d'un déplacement
    def is_valid_move(x, y):
        return x >= 0 and y >= 0 and x < grid_size and y < grid_size

    # Fonction de calcul de la distance entre deux points
    def distance(point1, point2):
        return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

    # Fonction de calcul du chemin parcouru pour atteindre un état
    def path(state):
        actions = []
        while state.previous_state is not None:
            actions.append(state.action)
            state = state.previous_state
        actions.reverse()
        return actions