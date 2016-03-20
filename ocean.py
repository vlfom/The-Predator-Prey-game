import random
import matplotlib.pyplot as plt


class Obstacle:
    """An obstacle class."""

    def __init__(self):
        pass

    def __str__(self):
        return '#'


class Prey:
    """A prey class.
    Attributes:
        food_value   The amount energy that predator will earn after eating a single prey.
        spawn_time   The amount of time before prey tries to reproduce offspring.
    """

    def __init__(self, food_value=3, spawn_time=7):
        self.food_value = food_value
        self.spawn_time = spawn_time

    def __str__(self):
        return 'O'

    def tick(self):
        """Modify unit state after single time unit"""
        self.spawn_time -= 1


class Predator:
    """A predator class.
    Attributes:
        energy       The amount of time before concrete predator dies without food.
        spawn_time   The amount of time before predator tries to reproduce offspring.
    """

    def __init__(self, start_energy=5, spawn_time=7):
        self.energy = start_energy
        self.spawn_time = spawn_time

    def __str__(self):
        return 'X'

    def tick(self):
        """Modify unit state after single time unit"""
        self.energy -= 1
        self.spawn_time -= 1


class Cell:
    """Single grid cell wrapper."""

    def __init__(self, obj=None):
        self.obj = obj

    def __str__(self):
        if self.obj is None:
            return '.'
        return str(self.obj)


class Ocean:
    """A grid with predators and prey model.
    Attributes:
        h            Grid height
        w            Grid width
        spawn_rate   The amount of time before new generation is born.
        _dirs        Possible directions of prey and predators
        _grid        Array with markers of whether animal has been modified on current step
    """
    _dirs = [[-1, 0], [1, 0], [0, -1], [0, 1]]

    def __init__(self, h=10, w=10, pred_vitality=5, prey_food_value=5, spawn_rate=7, seed=1337):
        self.h = h
        self.w = w
        self.grid = [[Cell() for _ in range(w)] for _ in range(h)]
        self.pred_vitality = pred_vitality
        self.prey_food_value = prey_food_value
        self.spawn_rate = spawn_rate

        self._random = random.Random(seed)

    def __str__(self):
        s = ''
        for i in range(self.h):
            for j in range(self.w):
                s += str(self.grid[i][j])
            s += '\n'
        return s

    def __getitem__(self, index):
        return self.grid[index[0]][index[1]].obj

    def __setitem__(self, index, value):
        self.grid[index[0]][index[1]].obj = value

    def generate_prey(self):
        """Generate new instance of prey"""

        return Prey(self.prey_food_value, self.spawn_rate)

    def generate_predator(self):
        """Generate new instance of predator"""

        return Predator(self.pred_vitality, self.spawn_rate)

    def try_spawn(self, i, j):
        """Try to spawn new-born unit near given ancestor coordinates"""

        for dir_ in self._random.sample(self._dirs, len(self._dirs)):
            i_, j_ = i + dir_[0], j + dir_[1]
            if 0 <= i_ < self.h and 0 <= j_ < self.w and \
               self.grid[i_][j_].obj is None:
                self.grid[i_][j_].obj = type(self.grid[i][j].obj)()
                return i_, j_

    def tick(self):
        """Modify ocean state after single time unit"""

        self.grid_ = [[0] * self.w] * self.h
        for i in range(self.h):
            for j in range(self.w):
                if self.grid_[i][j] == 0 and \
                  (isinstance(self.grid[i][j].obj, Predator) or
                   isinstance(self.grid[i][j].obj, Prey)):
                    self.make_animal_turn(i, j)

    def make_animal_turn(self, i, j):
        """Process one turn for animal on cell with coordinates (i, j)"""

        dir_ = self._random.choice(self._dirs)

        i_, j_ = i + dir_[0], j + dir_[1]

        if 0 <= i_ < self.h and 0 <= j_ < self.w:
            if isinstance(self.grid[i][j].obj, Predator) and \
               isinstance(self.grid[i_][j_].obj, Prey):
                self.grid[i][j].obj.energy += self.grid[i_][j_].obj.food_value
                self.grid[i_][j_].obj = None

            if self.grid[i_][j_].obj is None:
                self.grid[i_][j_].obj = self.grid[i][j].obj
                self.grid[i][j].obj = None
                self.grid_[i_][j_] = 1
            else:
                i_, j_ = i, j

            self.grid[i_][j_].obj.tick()

            if self.grid[i_][j_].obj.spawn_time == 0:
                self.grid[i_][j_].obj.spawn_time = self.spawn_rate
                cords = self.try_spawn(i_, j_)
                if cords is not None:
                    self.grid_[cords[0]][cords[1]] = 1

            if isinstance(self.grid[i_][j_].obj, Predator) and \
               self.grid[i_][j_].obj.energy == 0:
                self.grid[i_][j_].obj = None

    def get_animals_count(self):
        """Get count of prey and predators in ocean"""

        objects_count = {
            'Prey': 0,
            'Predator': 0,
            'Obstacle': 0,
            'NoneType': 0
        }

        for i in range(self.h):
            for j in range(self.w):
                objects_count[type(self.grid[i][j].obj).__name__] += 1

        return objects_count['Prey'], objects_count['Predator']


def init_ocean(h, w, pred_vitality, prey_food_value, spawn_rate, seed):
    """Init ocean with predators in the middle and prey on the borders"""

    # Create new empty Ocean
    ocean = Ocean(h, w,
                  pred_vitality=pred_vitality,
                  prey_food_value=prey_food_value,
                  spawn_rate=spawn_rate,
                  seed=seed)

    # Put predators in the middle
    for i in range(6):
        for j in range(6):
            ocean[(ocean.h // 2 - 2 + i, ocean.w // 2 - 2 + j)] = ocean.generate_predator()

    # Put prey on the borders
    for i in range(9):
        ocean[(0, i)] = ocean.generate_prey()
        ocean[(i, 0)] = ocean.generate_prey()
        ocean[(1, i)] = ocean.generate_prey()
        ocean[(i, 1)] = ocean.generate_prey()
        ocean[(7, i)] = ocean.generate_prey()
        ocean[(i, 7)] = ocean.generate_prey()
        ocean[(8, i)] = ocean.generate_prey()
        ocean[(i, 8)] = ocean.generate_prey()

    # Put one obstacle in the middle
    ocean[(4, 4)] = Obstacle()

    return ocean


# Configurations that did well on test phase
good_configurations = [
    (4, 12, 13),
    (5, 3, 14),
    (5, 11, 12),
    (6, 3, 12),
    (6, 7, 8),
    (8, 5, 13),
    (8, 8, 12),
    (9, 2, 11),
    (10, 14, 12),
    (11, 8, 10),
    (13, 6, 11)
]

for config in good_configurations:
    ocean = init_ocean(9, 9,
                       pred_vitality=config[0],
                       prey_food_value=config[1],
                       spawn_rate=config[2],
                       seed=1337)

    prey_counts, pred_counts = [], []
    ocean_history = []
    for _ in range(2000):
        cnt = ocean.get_animals_count()
        prey_counts.append(cnt[0])
        pred_counts.append(cnt[1])
        ocean_history.append(str(ocean))
        ocean.tick()

    config_desc = "predactor_vitality = {:d}, prey_food_value = {:d}, spawn_rate = {:d}".format(
            config[0], config[1], config[2])

    # Display plot with individuals count
    plt.title(config_desc)
    plt.plot(list(range(2000)), prey_counts, label='Prey')
    plt.plot(list(range(2000)), pred_counts, label='Predators')
    plt.xlabel('Time')
    plt.ylabel('Individuals count')
    plt.legend()
    plt.show()

    # Display grid history
    print("Model parameters:", config_desc)
    print('Do you want to view the grid history? (y/n)')
    choice = input()
    if choice == 'y':
        for i in range(len(ocean_history)):
            print(ocean_history[i])
            print('Do you want to continue? (y/n)')
            choice = input()
            if choice == 'n':
                break