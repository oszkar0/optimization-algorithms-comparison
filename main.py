import random
import copy
import math
from PIL import Image, ImageDraw, ImageFont
import os


class Space:
    # VISUALIZATION CONSTANTS
    CELL_SIZE = 30
    BOUNDARY_WIDTH = 2
    BOTTOM_STRIPE_HEIGHT = 20

    def __init__(self, width, height, num_hospitals):
        self.width = width
        self.height = height
        self.num_hospitals = num_hospitals
        self.houses = set()
        self.hospitals = set()

    def add_house(self, x, y):
        """
        Function which adds coordinates x, y of new house to set of house coordinates
        """
        if 0 < x < self.width and 0 < y < self.height:
            self.houses.add((x, y))

    def gen_hospital_candidates(self):
        """
        Function which generates coordinates which are free (currently no house and no hospital)
        """
        candidates = set()

        # generate all coordinates in our space
        for x in range(self.width):
            for y in range(self.height):
                candidates.add((x, y))

        # remove coordinates where house or hospital is placed
        for house in self.houses:
            candidates.remove(house)
        for hospital in self.hospitals:
            candidates.remove(hospital)

        return candidates

    def get_neighbours(self, x, y):
        """
        Function to get all neighbour of x,y coordinate
        """
        directions = [1, 0, -1]
        neighbours = set()

        # generate neighbours of x,y in the space (remove coordinates, which are out of our space)
        for dx in directions:
            new_x = x + dx
            if new_x > self.width - 1 or new_x < 0:
                continue

            for dy in directions:
                new_y = y + dy
                if new_y > self.height - 1 or new_y < 0:
                    continue

                neighbours.add((new_x, new_y))

        # remove coordinates where already house or hospital is already placed
        neighbours = neighbours.difference(self.hospitals)
        neighbours = neighbours.difference(self.houses)

        return neighbours

    def get_cost(self, hospitals):
        """
        Function to get sum of distances house - closest hospital
        """
        cost = 0
        # for all houses
        for house in self.houses:
            costs = []
            # calculate distance to every hospital
            for hospital in hospitals:
                single_cost = abs(hospital[0] - house[0]) + abs(hospital[1] - house[1])
                costs.append(single_cost)
            # add distance to the closest hospital to the overall cost
            cost += min(costs)
        return cost

    def visualize(self, name, iteration, cost):
        width = self.width * Space.CELL_SIZE + (self.width - 1) * Space.BOUNDARY_WIDTH
        height = self.height * Space.CELL_SIZE + (self.height - 1) * Space.BOUNDARY_WIDTH + Space.BOTTOM_STRIPE_HEIGHT

        image = Image.new(mode="RGB", size=(width, height), color=(128, 128, 128))
        hospital_image = Image.open("icons/hospital.png")
        house_image = Image.open("icons/house.png")
        f = ImageFont.truetype("arial.ttf", 15)

        drawing = ImageDraw.Draw(image)

        # draw horizontal lines
        for i in range(self.height - 1):
            x_0 = 0
            y_0 = Space.CELL_SIZE + i * (Space.CELL_SIZE + Space.BOUNDARY_WIDTH)
            x_1 = width
            y_1 = y_0 + Space.BOUNDARY_WIDTH - 1
            drawing.rectangle([(x_0, y_0), (x_1, y_1)], fill="#333333")

        # draw vertical lines
        for i in range(self.width - 1):
            x_0 = Space.CELL_SIZE + i * (Space.CELL_SIZE + Space.BOUNDARY_WIDTH)
            y_0 = 0
            x_1 = x_0 + Space.BOUNDARY_WIDTH - 1
            y_1 = height - 10
            drawing.rectangle([(x_0, y_0), (x_1, y_1)], fill="#333333")

        # put hospitals on the image
        for hospital in self.hospitals:
            x = hospital[0] * (Space.CELL_SIZE + Space.BOUNDARY_WIDTH)
            y = hospital[1] * (Space.CELL_SIZE + Space.BOUNDARY_WIDTH)
            image.paste(hospital_image, (x, y))

        # put houses on the image
        for house in self.houses:
            x = house[0] * (Space.CELL_SIZE + Space.BOUNDARY_WIDTH)
            y = house[1] * (Space.CELL_SIZE + Space.BOUNDARY_WIDTH)
            image.paste(house_image, (x, y))

        # put cost on the photo
        drawing.rectangle([(0, height - Space.BOTTOM_STRIPE_HEIGHT), (width, height)], fill="#000000")
        drawing.text((0, height - Space.BOTTOM_STRIPE_HEIGHT), f"COST: {cost}", (255, 255, 255), font=f)

        # save image
        folder_name = f"{name}"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        file_name = f"{name}_{iteration}.png"
        image.save(os.path.join(folder_name, file_name))

    def hill_climb(self, maximum=None, log=False, image_name=None):
        """
        Function to get optimized placement of hospitals
        """
        count = 0
        self.hospitals = set()

        # draw random hospital coordinates
        for i in range(self.num_hospitals):
            self.hospitals.add(random.choice(list(self.gen_hospital_candidates())))

        while maximum is None or count < maximum:
            best_neighbours = []
            best_neighbour_cost = None

            # iterate over every hospital
            for hospital in self.hospitals:

                # iterate over every neighbour of hospital
                for new_loc in self.get_neighbours(*hospital):

                    # substitute an iterated hospital for one of neighbours and calculate cost
                    neighbour = self.hospitals.copy()
                    neighbour.remove(hospital)
                    neighbour.add(new_loc)

                    cost = self.get_cost(neighbour)

                    # if cost of new hospital placement is lower or there is no best cost
                    # we have new best placement, if it is equal we add neighbour to "equal in cost" neighbours
                    if best_neighbour_cost is None or cost < best_neighbour_cost:
                        best_neighbour_cost = cost
                        best_neighbours = [neighbour]
                    elif best_neighbour_cost == cost:
                        best_neighbours.append(neighbour)

            # if best cost in that iteration is greater or equal, we should stop iterating
            # otherwise we found betters set, and we can continue with next iteration
            if best_neighbour_cost >= self.get_cost(self.hospitals):
                return self.hospitals
            else:
                if log:
                    print(f"Found better solution with cost: {best_neighbour_cost}")
                    self.visualize(image_name, count, best_neighbour_cost)
                self.hospitals = random.choice(best_neighbours)

            count += 1

    def random_restart_hill_climb(self, maximum, log=False, image_name=None):
        best_hospital_placement_cost = None
        best_hospital_placement = None
        # perform hill climb algorithm maximum number of times
        for i in range(maximum):
            placement = self.hill_climb()
            cost = self.get_cost(placement)
            # if solution from latest hill climb is better than current then change, if not don't change
            if best_hospital_placement_cost is None or cost < best_hospital_placement_cost:
                best_hospital_placement = placement
                best_hospital_placement_cost = cost
                if log:
                    print(f"Found new best state with cost: {cost}")
                    if not image_name is None:
                        self.visualize(image_name, i, cost)
            else:
                if log:
                    print(f"New found state cost: {cost}")

        #  save the best solution
        self.hospitals = best_hospital_placement

    def simulated_annealing(self, max_temp, max_steps, log=False, image_name=None):
        self.hospitals = set()

        # draw random hospital coordinates
        for i in range(self.num_hospitals):
            self.hospitals.add(random.choice(list(self.gen_hospital_candidates())))

        for t in range(max_steps):
            # calculate new "temperature" of our system
            temp = max_temp / float(t + 1)

            # draw random neighbour of current solution
            random_hospital = random.choice(list(self.hospitals))
            neighbours = self.get_neighbours(*random_hospital)
            random_neighbour = random.choice(list(neighbours))

            new_placement = self.hospitals.copy()
            new_placement.remove(random_hospital)
            new_placement.add(random_neighbour)

            # calculate current delta cost
            new_cost = self.get_cost(new_placement)
            current_cost = self.get_cost(self.hospitals)
            delta_cost = current_cost - new_cost

            # if delta cost more than 0 change current state to better one
            # if delta_cost is less or equal 0 then choose it with  probability math.exp(-1 / temp) (higher temp
            # higher probability to choose worse solution)
            if delta_cost > 0:
                self.hospitals = new_placement
                if log:
                    print(f"Found and set better placement with cost: {new_cost}, delta cost is: {delta_cost}")
                    if not image_name is None:
                        self.visualize(image_name, t, new_cost)
            elif delta_cost <= 0 and random.random() < math.exp(-1 / temp):
                self.hospitals = new_placement
                if log:
                    print(f"Found and set worse placement with cost: {new_cost}, delta cost is: {delta_cost}")
                    if not image_name is None:
                        self.visualize(image_name, t, new_cost)
            else:
                if log:
                    print(f"Found worse placement with cost: {new_cost}, delta cost is: {delta_cost}, but didn't set")

        print(f"Final solution has cost: {self.get_cost(self.hospitals)}")


space0 = Space(20, 10, 3)
for i in range(15):
    space0.add_house(random.randint(0, 20), random.randint(0, 10))

space1 = copy.deepcopy(space0)
space2 = copy.deepcopy(space0)

print("1. HILL CLIMB\n")
space0.hill_climb(20, True, "hill_climb_normal")
print("2. HILL CLIMB RANDOM RESTART\n")
space1.random_restart_hill_climb(20, True, "hill_climb_rndrs")
print("3. SIMULATED ANNEALING\n")
space2.simulated_annealing(10, 100, True, "sim_annealing")
