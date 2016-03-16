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
    food_value = 3

    def __init__(self):
        self.spawn_time = Ocean.spawn_rate

    def __str__(self):
        return 'O'

    def tick(self):
        """Modify unit state after single time unit"""
        self.spawn_time -= 1


class Predator:
    """A predator class.

    Attributes:
        vitality     The amount of time before newborn predator dies without food.
        energy       The amount of time before concrete predator dies without food.
        spawn_time   The amount of time before predator tries to reproduce offspring.
    """
    vitality = 5

    def __init__(self):
        self.energy = Predator.vitality
        self.spawn_time = Ocean.spawn_rate

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
    """
    spawn_rate = 7

    def __init__(self, h=10, w=10, pred_vitality=5, prey_food_value=5, spawn_rate=7):
        self.h = h
        self.w = w
        self.grid = [[Cell() for _ in range(w)] for _ in range(h)]
        Predator.vitality = pred_vitality
        Prey.food_value = prey_food_value

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

    def try_spawn(self, i, j):
        """Try to spawn new-born unit near given ancestor coordinates"""

        for dir_ in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
            i_ = i + dir_[0]
            j_ = j + dir_[1]
            if 0 <= i_ < self.h and 0 <= j_ < self.w and \
               self.grid[i_][j_].obj is None:
                if isinstance(self.grid[i][j].obj, Prey):
                    self.grid[i_][j_].obj = Prey()
                elif isinstance(self.grid[i][j].obj, Predator):
                    self.grid[i_][j_].obj = Predator()
                return i_, j_

    def tick(self):
        """Modify ocean state after single time unit"""

        grid_ = [[0 for _ in range(self.w)] for _ in range(self.h)]
        for i in range(self.h):
            for j in range(self.w):
                if grid_[i][j] == 0 and isinstance(self.grid[i][j].obj, Predator):
                    dir_ = random.choice([[-1, 0], [1, 0], [0, -1], [0, 1]])
                    i_ = i + dir_[0]
                    j_ = j + dir_[1]
                    if 0 <= i_ < self.h and 0 <= j_ < self.w and \
                            not isinstance(self.grid[i_][j_].obj, Predator) and \
                            not isinstance(self.grid[i_][j_].obj, Obstacle):

                        if isinstance(self.grid[i_][j_].obj, Prey):
                            self.grid[i][j].obj.energy += Prey.food_value

                        self.grid[i_][j_].obj = self.grid[i][j].obj
                        self.grid[i][j].obj = None
                        grid_[i_][j_] = 1
                    else:
                        i_ = i
                        j_ = j

                    self.grid[i_][j_].obj.tick()

                    if self.grid[i_][j_].obj.spawn_time == 0:
                        self.grid[i_][j_].obj.spawn_time = Ocean.spawn_rate
                        cords = self.try_spawn(i_, j_)
                        if cords is not None:
                            grid_[cords[0]][cords[1]] = 1

                    if self.grid[i_][j_].obj.energy == 0:
                        self.grid[i_][j_].obj = None

                elif grid_[i][j] == 0 and isinstance(self.grid[i][j].obj, Prey):
                    dir_ = random.choice([[-1, 0], [1, 0], [0, -1], [0, 1]])
                    i_ = i + dir_[0]
                    j_ = j + dir_[1]
                    if 0 <= i_ < self.h and 0 <= j_ < self.w and \
                       self.grid[i_][j_].obj is None:
                        self.grid[i_][j_].obj = self.grid[i][j].obj
                        self.grid[i][j].obj = None
                        grid_[i_][j_] = 1
                    else:
                        i_ = i
                        j_ = j

                    self.grid[i_][j_].obj.tick()

                    if self.grid[i_][j_].obj.spawn_time == 0:
                        self.grid[i_][j_].obj.spawn_time = Ocean.spawn_rate
                        cords = self.try_spawn(i_, j_)
                        if cords is not None:
                            grid_[cords[0]][cords[1]] = 1

    def get_animals_count(self):
        """Get count of prey and predators in ocean"""

        prey_count, pred_count = 0, 0
        for i in range(self.h):
            for j in range(self.w):
                if isinstance(self.grid[i][j].obj, Prey):
                    prey_count += 1
                elif isinstance(self.grid[i][j].obj, Predator):
                    pred_count += 1
        return prey_count, pred_count


def init_ocean(h, w, pred_vitality, prey_food_value, spawn_rate):
    """Init ocean with predators in the middle and prey on the borders"""
    random.seed(2)

    # Create new empty Ocean
    ocean = Ocean(h, w,
                  pred_vitality=pred_vitality,
                  prey_food_value=prey_food_value,
                  spawn_rate=spawn_rate)

    # Put predators in the middle
    for i in range(6):
        for j in range(6):
            ocean[(ocean.h // 2 - 2 + i, ocean.w // 2 - 2 + j)] = Predator()

    # Put prey on the borders
    for i in range(9):
        ocean[(0, i)] = Prey()
        ocean[(i, 0)] = Prey()
        ocean[(1, i)] = Prey()
        ocean[(i, 1)] = Prey()
        ocean[(7, i)] = Prey()
        ocean[(i, 7)] = Prey()
        ocean[(8, i)] = Prey()
        ocean[(i, 8)] = Prey()

    # Put one obstacle in the middle
    ocean[(4, 4)] = Obstacle()

    return ocean


# Configurations that did well on test phase
good_configurations = [
    (2, 2, 5), (2, 3, 7), (2, 6, 5), (6, 2, 7)
]

for config in good_configurations:
    ocean = init_ocean(9, 9,
                       pred_vitality=config[0],
                       prey_food_value=config[1],
                       spawn_rate=config[2])
    prey_counts, pred_counts = [], []
    ocean_history = []
    for _ in range(500):
        cnt = ocean.get_animals_count()
        prey_counts.append(cnt[0])
        pred_counts.append(cnt[1])
        ocean_history.append(str(ocean))
        ocean.tick()

    config_desc = "predactor_vitality = {:d}, prey_food_value = {:d}, spawn_rate = {:d}".format(
            config[2], config[1], config[2])

    # Display plot with individuals count
    plt.title(config_desc)
    plt.plot(list(range(500)), prey_counts, label='Prey')
    plt.plot(list(range(500)), pred_counts, label='Predators')
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
