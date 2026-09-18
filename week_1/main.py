import pygame
import numpy as np
import random

# Configuration

WIDTH = 800
HEIGHT = 800

BOWL_CENTER = np.array([WIDTH / 2, HEIGHT / 2], dtype=float)
BOWL_RADIUS = 300

# Start with 1 ball, then 2. Many at once is the bonus.
NUM_PARTICLES = 50
PARTICLE_RADIUS = 12
PARTICLE_SPEED = 150.0

# Pixels per second squared, not m/s^2. Note that +y points DOWN on screen.
GRAVITYVAL = 900.0

# How much speed survives a bounce. 1.0 loses nothing, below 1.0 is weaker.
WALL_RESTITUTION = 1.0
RESTITUTION = 1.0

FPS = 60

positions = []
velocities = []
gravity = np.array([0, GRAVITYVAL])

for i in range(NUM_PARTICLES):

    # A random spot inside the bowl, with the whole ball fitting.
    angle = random.uniform(0, 2 * np.pi)
    distance = random.uniform(0, BOWL_RADIUS - PARTICLE_RADIUS)

    positions.append(BOWL_CENTER + distance * np.array([
        np.cos(angle),
        np.sin(angle)
    ]))

    # A random direction, at roughly PARTICLE_SPEED.
    # Swap for np.array([0.0, 0.0]) to drop the ball from rest.
    angle = random.uniform(0, 2 * np.pi)

    velocities.append(PARTICLE_SPEED * np.array([
        np.cos(angle),
        np.sin(angle)
    ]))

# Pygame setup

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle Simulation")

clock = pygame.time.Clock()

running = True

# Main loop

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # Seconds since the last frame. This is your timestep.
    dt = clock.tick(FPS) / 1000.0

    ###########################################################################
    # TODO: Make every ball fall, and bounce it off the wall of the bowl.     #
    #                                                                         #
    # Two things happen here, in an order that matters.                       #
    #                                                                         #
    # First, it falls. Gravity is an acceleration, so ask yourself what it    #
    # changes directly: the position, or the velocity? And once that has      #
    # changed, what does the ball's new position depend on?                   #
    #                                                                         #
    # Second, it has to stay in the bowl. Work out how you would even         #
    # tell that it has escaped, given that you know where the centre of       #
    # the bowl is, how wide the bowl is, and how wide the ball is.            #
    # Careful: the ball is drawn with a radius of its own, so its edge        #
    # reaches the wall before its centre would.                               #
    #                                                                         #
    # Once you know it has escaped, two things need fixing. Where should      #
    # the ball actually be, and what should its velocity become? For the      #
    # velocity, only the part heading into the wall should change. The        #
    # part sliding along the wall carries on untouched. WALL_RESTITUTION      #
    # decides how much of the incoming speed comes back out.                  #
    ###########################################################################
    
    # CODE STARTS HERE.

    for i in range(NUM_PARTICLES):  
        velocities[i] = velocities[i] + gravity * dt
        positions[i] = positions[i] + velocities[i] * dt
    
    
    #positions[0] += velocities[0] * dt + (1/2) * gravity * dt * dt
    #velocities[0] += gravity * dt
    # felt like this made more sense but i was wrong

        rel_pos = np.array(positions[i] - BOWL_CENTER)
        distance = np.linalg.norm(rel_pos)
        arena =  BOWL_RADIUS - PARTICLE_RADIUS
        if(distance >= arena):
            n =  -rel_pos / distance
            Vnormal = np.dot(velocities[i], n)
            velocities[i] = velocities[i] - ((1+WALL_RESTITUTION)  * Vnormal) * n
            positions[i] = BOWL_CENTER - n * (BOWL_RADIUS - PARTICLE_RADIUS)

        
        for j in range(i+1, NUM_PARTICLES):
            
            dist = np.array(positions[i] - positions[j])
            distMgn = np.linalg.norm(dist)
            collisionNormal =  dist / distMgn

            relative_vel_norm = np.dot((velocities[i] - velocities[j]), collisionNormal)
            if(distMgn <= 2 * PARTICLE_RADIUS):
                if(relative_vel_norm <=0):
                    delta = distMgn - 2*PARTICLE_RADIUS
                    positions[i] += delta/2 * collisionNormal
                    positions[j] -= delta/2 * collisionNormal
                    velocities[i] = velocities[i] - 0.5 * (1 + RESTITUTION) * relative_vel_norm * collisionNormal
                    velocities[j] = velocities[j] + 0.5 * (1 + RESTITUTION) * relative_vel_norm * collisionNormal

                



        

    pass

    ###########################################################################
    #                            END OF YOUR CODE                             #
    ###########################################################################

    ###########################################################################
    # TODO: Make the balls bounce off each other.                             #
    #                                                                         #
    # Start with the condition. Given two balls, what has to be true          #
    # about where they are for them to be touching? Every ball has the        #
    # same radius, which makes this simpler than it sounds.                   #
    #                                                                         #
    # Then the response. A collision changes velocities, not positions.       #
    # Which direction does the change act along, and how would you get        #
    # that direction from the two positions you have? Only the motion         #
    # along that direction matters, the rest is unaffected.                   #
    #                                                                         #
    # One trap worth thinking about: two balls that are overlapping but       #
    # already moving apart should be left alone. If you bounce them again     #
    # they will get stuck together. How would you tell "approaching"          #
    # from "separating"?                                                      #
    #                                                                         #
    # Finally, this has to happen for every pair of balls, not just one.      #
    ###########################################################################

    # CODE STARTS HERE.

    pass

    ###########################################################################
    #                            END OF YOUR CODE                             #
    ###########################################################################

    # Render

    screen.fill((20, 20, 25))

    pygame.draw.circle(
        screen,
        (180, 180, 180),
        BOWL_CENTER.astype(int),
        BOWL_RADIUS,
        width=3
    )

    for position in positions:
        pygame.draw.circle(
            screen,
            (220, 220, 220),
            position.astype(int),
            PARTICLE_RADIUS
        )

    pygame.display.flip()

    


pygame.quit()
