import math

from matplotlib import pyplot as plt, colors
from matplotlib.animation import FuncAnimation
import random

rand = random.Random()
SIDEWALK_WIDTH = 10  # This is the y-dimension of the sidewalk
SIDEWALK_LENGTH = 200  # This is the x-dimension of the sidewalk
TRANSPROB = 0.1  # Probability of transmission of virus in 1 time step at distance 1
INFECTED_PROP = 0.1  # The proportion of people who enter the simulation already carrying the virus
INTERARRIVAL = 3  # Average number of time steps between arrivals (each side handled separately)
ARRIVAL = 1

# Setup for graphical display
colourmap = colors.ListedColormap(["lightgrey", "green", "red", "yellow", "purple"])
normalizer = colors.Normalize(vmin=0.0, vmax=4.0)


class Person:
    def __init__(self, id, sidewalk):
        self.id = id
        self.active = False
        self.sidewalk = sidewalk
        self.infected = True if rand.random() < INFECTED_PROP else False
        self.newlyinfected = False
        self.careful = rand.choice([True,False])

        if rand.choice([True, False]):
            self.startx = 0
            self.direction = 1
        else:
            self.startx = SIDEWALK_LENGTH - 1
            self.direction = -1
        self.starty = self.y = rand.randint(0, SIDEWALK_WIDTH - 1)

    def enter_sidewalk(self, x, y):
        if self.sidewalk.enter_sidewalk(self, x, y):
            self.active = True

    def step(self):
        # Simple random movement in one of four cardinal directions (written for clarity, not efficiency!)
        desiredx = self.x
        desiredy = self.y
        change = rand.choice([-1, 1])
        #careful = rand.choice([True,False])

        if self.careful:
            self.careful = True
            if self.startx == 0:

                if not (self.sidewalk.isoccupied(desiredx + 1, desiredy) and self.sidewalk.isoccupied(desiredx + 2,
                                                                                                      desiredy)):
                    desiredx = self.x + 1

                if self.sidewalk.isoccupied(desiredx, desiredy + 1):
                    desiredy = self.y - 1
                    desiredx = self.x

                if self.sidewalk.isoccupied(desiredx, desiredy - 1):
                    desiredy = self.y + 1
                    desiredx = self.x

                if self.sidewalk.isoccupied(desiredx, desiredy):
                    desiredx = self.x
                    desiredy = self.y + change

                if self.sidewalk.isoccupied(desiredx + 1, desiredy + 1):
                    desiredx = self.x
                    desiredy = self.y - 1

                if self.sidewalk.isoccupied(desiredx + 1, desiredy - 1):
                    desiredx = self.x
                    desiredy = self.y + 1

                if self.sidewalk.isoccupied(desiredx + 1, desiredy):
                    desiredx = self.x
                    desiredy = self.y + change


            else:
                if not (self.sidewalk.isoccupied(desiredx - 1, desiredy) and self.sidewalk.isoccupied(desiredx - 2,
                                                                                                      desiredy)):
                    desiredx = self.x - 1

                if self.sidewalk.isoccupied(desiredx, desiredy + 1):
                    desiredy = self.y - 1
                    desiredx = self.x

                if self.sidewalk.isoccupied(desiredx, desiredy - 1):
                    desiredy = self.y + 1
                    desiredx = self.x

                if self.sidewalk.isoccupied(desiredx - 1, desiredy + 1):
                    desiredx = self.x
                    desiredy = self.y - 1

                if self.sidewalk.isoccupied(desiredx - 1, desiredy - 1):
                    desiredx = self.x
                    desiredy = self.y + 1

                if self.sidewalk.isoccupied(desiredx, desiredy):
                    desiredx = self.x
                    desiredy = self.y + change

                if self.sidewalk.isoccupied(desiredx - 1, desiredy):
                    desiredx = self.x
                    desiredy = self.y + change
                    
        if not self.careful:
            
            self.careful = False
            
            if self.startx == 0:
                desiredx = self.x + 1
                if self.sidewalk.isoccupied(desiredx, desiredy):
                    desiredx = self.x
                    desiredy = self.y + change
            else:
                desiredx = self.x - 1
                if self.sidewalk.isoccupied(desiredx, desiredy):
                    desiredx = self.x
                    desiredy = self.y + change

        # Ensure x and y don't go off edge of sidewalk
        desiredx = max(min(desiredx, SIDEWALK_LENGTH - 1), 0)
        desiredy = max(min(desiredy, SIDEWALK_WIDTH - 1), 0)
        self.sidewalk.attemptmove(self, desiredx, desiredy)

        # Ensure x and y don't go off edge of sidewalk
        desiredx = max(min(desiredx, SIDEWALK_LENGTH - 1), 0)
        desiredy = max(min(desiredy, SIDEWALK_WIDTH - 1), 0)
        self.sidewalk.attemptmove(self, desiredx, desiredy)

    def __str__(self):
        return "id: %d  x: %d  y: %d" % (self.id, self.x, self.y)


# The class representing the sidewalk itself.  Agents must enter the sidewalk to be active in the simulation.
# The sidewalk controls agents' positions/movement.
class Sidewalk:

    def __init__(self):
        # Tracking of positions of agents
        self.storage = SWGrid()

        # Store arrival time step of next person
        self.arrival = 1

        # Sore ID to create a person
        self.ID = 1

        # Store all the list of people created and were once active
        self.people = []

        # Store the number of people who were newly infected
        self.newInfections = 0

        # Store the number of people infected till that time step
        self.Infected_till_then = 0
        # Bitmap is for graphical display
        self.bitmap = [[0.0 for i in range(SIDEWALK_LENGTH)] for j in range(SIDEWALK_WIDTH)]

    def enter_sidewalk(self, person, x, y):
        # New entrant to the sidewalk, must attempt to start at one end
        # if x!=0 and x!=SIDEWALK_LENGTH-1:
        #     print("Must start at an end!")
        #     return False

        # Only allow move if space not currently occupied
        if self.storage.isoccupied(x, y):
            print("Move rejected: occupied")
            return False
        self.storage.add_item(x, y, person)
        person.x = x
        person.y = y
        return True


    def leave_sidewalk(self, person):
        # Must attempt to leave at one end
        if person.x != 0 and person.x != SIDEWALK_LENGTH - 1:
            print("Must leave at an end!")
            return False

        self.storage.remove_item(person)

    def attemptmove(self, person, x, y):

        # Reject move of more than 1 square
        if (abs(person.x - x) + abs(person.y - y)) > 1:
            print("Attempt to move more than one square!")
            return False

        # Only allow move if space not currently occupied
        if self.storage.isoccupied(x, y):
            # print("Move rejected: occupied")
            return False
        person.x = x
        person.y = y
        self.storage.move_item(x, y, person)
        return True

    def spead_infection(self):
        for person in self.storage.get_list():
            currentx = person.x
            currenty = person.y
            if person.infected:
                # Find all agents within a square of 'radius' 2 of the infected agent
                for x in range(currentx - 2, currentx + 3):
                    for y in range(currenty - 2, currenty + 3):
                        target = self.storage.get_item(x, y)

                        # If target is not infected, infect with probability dependent on distance
                        if target is not None and not target.infected:
                            riskfactor = 1 / ((currentx - x) ** 2 + (currenty - y) ** 2)
                            tranmission_prob = TRANSPROB * riskfactor
                            if rand.random() < tranmission_prob:
                                target.infected = True
                                target.newlyinfected = True
                                print('New infection! %s' % target)

    # Updates the graphic for display
    def refresh_image(self):
        self.bitmap = [[0.0 for i in range(SIDEWALK_LENGTH)] for j in range(SIDEWALK_WIDTH)]
        for person in self.storage.get_list():
            x = person.x
            y = person.y
            colour = 1
            if person.newlyinfected:
                colour = 3
            elif person.infected:
                colour = 2
            elif person.careful:
                colour = 4
            self.bitmap[y][x] = colour

    def calculateArrivalTime(self, time_step):
        # Time of arrival for first person
        if time_step == 1:
            return self.arrival

        # Subsequent gap between arrival time
        elif time_step <= self.arrival:
            return self.arrival

        # Generate and return the time to create next person
        else:
            self.arrival += int(rand.expovariate(1 / INTERARRIVAL))
            return self.arrival


    def run_step(self, time_step):
        # store the arrival time for person to be created
        nextArrival = self.calculateArrivalTime(time_step)

        if time_step == nextArrival:

            # Create a new person
            P = Person(self.ID, sw)

            # enter them to the sidewalk
            P.enter_sidewalk(P.startx, P.starty)

            # Check if the person has entered the sidewalk
            if P.active == True:
                # store the person in a list
                self.people.append(P)

            # Increment ID of the person being created
            self.ID += 1

        # Accessing each person and making a move
        for person1 in self.storage.get_list():
            # check if person entering is initially infected
            if person1.active:
                # make a move
                person1.step()

                # leave the side walk if you reached the end
                if person1.direction == 1 and person1.x == 199:
                    self.leave_sidewalk(person1)
                if person1.direction == -1 and person1.x == 0:
                    self.leave_sidewalk(person1)

        self.spead_infection()
        self.refresh_image()

        self.Infected_till_then = 0
        self.newInfections = 0
        # Infection rate every 100th time step starting from 1
        if time_step == 1 or time_step % 100 == 0:
            # traverse the list of people
            for person in self.people:
                # check if person is infected
                if person.infected == True:
                    self.Infected_till_then += 1
                if person.newlyinfected == True:
                    self.newInfections += 1

            print("New Rate of infection at time step %d: %.3f %%" % (
            time_step, (self.Infected_till_then / len(self.people)) * 100))
            if time_step == 1000:
                print("--------------------------------------------------")
                print("Initial Rate of infection at time step %d: %.3f %%" % (
                time_step, ((self.Infected_till_then - self.newInfections) / len(self.people)) * 100))
                print("Total Rate of infection: %.3f %%" % (self.Infected_till_then / len(self.people) * 100))
                print("--------------------------------------------------")

    # Returns true if x,y is occupied by an agent, false otherwise.  This is the only information that an agent
    # has about other agents; it can't (e.g.) see if other agents are infected!
    def isoccupied(self, x, y):
        return self.storage.isoccupied(x, y)


# Used to provide storage, lookup of occupants of sidewalk
class SWGrid:
    def __init__(self):
        self.dic = dict()

    def isoccupied(self, x, y):
        # self.check_coordinates(x, y)
        return (x, y) in self.dic

    # Stores item at coordinates x, y.  Throws an exception if the coordinates are invalid.  Returns false if
    # unsuccessful (e.g., the square is occupied) or true if successful.
    def add_item(self, x, y, item):
        self.check_coordinates(x, y)
        if (x, y) in self.dic:
            return False
        self.dic[(x, y)] = item
        return True

    # Removes item from its current coordinates (which do not need to be provided) and stores it
    # at coordinates x, y.  Throws an exception if the coordinates are invalid or if the square is occupied.
    def move_item(self, x, y, item):
        self.check_coordinates(x, y)
        # if self.isoccupied(x, y):
        # raise Exception("Move to occupied square!")

        # Find and remove previous location.  Assumed state is valid (meaning only one entry per x,y key)
        oldloc = next(key for key, value in self.dic.items() if value == item)
        del self.dic[oldloc]
        self.add_item(x, y, item)

    # Removes item (coordinates do not need to be provided)
    # Throws an exception if the item doesn't exist.
    def remove_item(self, item):
        # Find and remove previous location.  Assumed state is valid (meaning only one entry per x,y key)
        oldloc = next(key for key, value in self.dic.items() if value == item)
        if oldloc is None:
            raise Exception('Attempt to remove non-existent item!')
        del self.dic[oldloc]

    def get_item(self, x, y):
        # self.check_coordinates(x, y)
        return self.dic.get((x, y), None)

    # Returns a list of all agents in the simulation.
    def get_list(self):
        return list(self.dic.values())

    def check_coordinates(self, x, y):
        if x < 0 or x >= SIDEWALK_LENGTH or y < 0 or y >= SIDEWALK_WIDTH:
            raise Exception("Illegal coordinates!")


#
# Run simulation
#

sw = Sidewalk()

# This is NOT how people should be added-- it is just to put agents in place to demonstrate random movement.
# Agents should be added by a random process in the run_step method.

# Set up graphical display
display = plt.figure(figsize=(15, 5))
image = plt.imshow(sw.bitmap, cmap=colourmap, norm=normalizer, animated=True)

# Track time step
t = 0


def updatefigure(*args):
    global t
    t += 1

    if t % 100 == 0:
        print("Time: %d" % t)
    sw.run_step(t)
    sw.refresh_image()
    image.set_array(sw.bitmap)
    return image,

anim = FuncAnimation(display, updatefigure, frames=1000, interval=100, blit=True, repeat=False)
plt.show()

print("Done!")
