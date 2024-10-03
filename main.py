import pygame
import sys
import verlet
import time
import asyncio

pygame.init()


screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Moving Rectangle")

clock = pygame.time.Clock()

rect_x = 50
rect_y = 50
rect_width = 100
rect_height = 50
rect_color = (255, 0, 0)
rect_speed = 10
#
# TO ADJUST INITIAL CONDITIONS SEE BELOW:
# [initial position (x or y), initial velocity (x or y)]
#
initial_conditions_x = [200, 100]
initial_conditions_y = [300, 0]




pygame.draw.circle(screen, rect_color, (initial_conditions_x[0], initial_conditions_y[0]),10,10)
valsx = initial_conditions_x
valsy = initial_conditions_y

Flag = True
import pygame
import sys

pygame.init()

# Screen setup
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Electric field")

clock = pygame.time.Clock()

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
gray = (200, 200, 200)

charge_radius = 15
resize_margin = 10  # The margin within which resizing is triggered

# Lists to store charges and magnetic field rectangles
charges = []
magnetic_fields = []

# States for dragging and resizing
dragging = False
resizing = False
dragged_charge_index = None
dragged_rect_index = None
resize_dir = None  # Direction of resizing ('h', 'v', 'hv')

# Button setup
button_width, button_height = 120, 40
button_x = screen_width - button_width - 10
button_y = 10
button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
button_color = gray

trail = []
if(initial_conditions_x[1] == 0 and initial_conditions_y[1] == 0):
    sim = verlet.verlet(20,0.01)
else:
    sim = verlet.verlet(0.1,0.01)


# Main loop
def main_loop():
    global charges, magnetic_fields, trail, valsx, valsy, Flag
    global dragging, resizing
    while True:
        if(Flag):
            for event in pygame.event.get():
                
                if event.type == pygame.KEYDOWN:
                    mods = pygame.key.get_mods()
                    if event.key == pygame.K_RETURN and mods & pygame.KMOD_SHIFT:
                        Flag = False

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos

                    # Check if button is clicked
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        # Add a new magnetic field rectangle at the center of the screen
                        new_rect = pygame.Rect(screen_width // 2 - 50, screen_height // 2 - 25, 100, 50)
                        
                        magnetic_fields.append(new_rect)
                        dragging = True
                        dragged_rect_index = len(magnetic_fields) - 1

                    else:
                        # Check if any charge is clicked
                        for i, charge in enumerate(charges):
                            x, y, sign = charge
                            if (x - mouse_x) ** 2 + (y - mouse_y) ** 2 <= charge_radius ** 2:
                                dragging = True
                                dragged_charge_index = i
                                break

                        # Check if any magnetic field rectangle is clicked or to be resized
                        if not dragging:
                            for i, rect in enumerate(magnetic_fields):
                                if rect.collidepoint(mouse_x, mouse_y):
                                    # Check if near edges to resize
                                    if abs(rect.right - mouse_x) < resize_margin and abs(rect.bottom - mouse_y) < resize_margin:
                                        resizing = True
                                        resize_dir = 'hv'
                                        dragged_rect_index = i
                                        break
                                    elif abs(rect.right - mouse_x) < resize_margin:
                                        resizing = True
                                        resize_dir = 'h'
                                        dragged_rect_index = i
                                        break
                                    elif abs(rect.bottom - mouse_y) < resize_margin:
                                        resizing = True
                                        resize_dir = 'v'
                                        dragged_rect_index = i
                                        break
                                    else:
                                        dragging = True
                                        dragged_rect_index = i
                                        break

                        # If nothing is being dragged or resized, create a new charge
                        if not dragging and not resizing:
                            sign = 1 if event.button == 1 else -1
                            charges.append([mouse_x, mouse_y, sign])

                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging = False
                    resizing = False
                    dragged_charge_index = None
                    dragged_rect_index = None
                    resize_dir = None

                elif event.type == pygame.MOUSEMOTION:
                    if dragging:
                        mouse_x, mouse_y = event.pos
                        if dragged_charge_index is not None:
                            charges[dragged_charge_index][0] = mouse_x
                            charges[dragged_charge_index][1] = mouse_y
                        elif dragged_rect_index is not None:
                            magnetic_fields[dragged_rect_index].x = mouse_x - magnetic_fields[dragged_rect_index].width // 2
                            magnetic_fields[dragged_rect_index].y = mouse_y - magnetic_fields[dragged_rect_index].height // 2
                    elif resizing:
                        mouse_x, mouse_y = event.pos
                        if resize_dir == 'h' or resize_dir == 'hv':
                            magnetic_fields[dragged_rect_index].width = max(10, mouse_x - magnetic_fields[dragged_rect_index].x)
                        if resize_dir == 'v' or resize_dir == 'hv':
                            magnetic_fields[dragged_rect_index].height = max(10, mouse_y - magnetic_fields[dragged_rect_index].y)

            screen.fill(white)

            # Draw the button
            pygame.draw.rect(screen, button_color, button_rect)
            font = pygame.font.Font(None, 30)
            text = font.render("Magnetic Field", True, black)
            screen.blit(text, (button_x + 10, button_y + 10))

            # Draw charges
            for charge in charges:
                x, y, sign = charge
                color = red if sign == 1 else blue
                pygame.draw.circle(screen, color, (x, y), charge_radius)

            # Draw magnetic field rectangles
            for rect in magnetic_fields:
                pygame.draw.rect(screen, black, rect, 2)  # Draw rectangle with black outline

            pygame.display.flip()
            clock.tick(60)

            print(charges)
            print(magnetic_fields)

        else:
            is_in_bfield = False
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    mods = pygame.key.get_mods()
                    if event.key == pygame.K_RETURN and mods & pygame.KMOD_SHIFT:
                        # RESET!!!
                        charges = []
                        magnetic_fields = []
                        trail = []
                        valsx = initial_conditions_x
                        valsy = initial_conditions_y
                        Flag = True

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            for Bfield in magnetic_fields:
                if Bfield.collidepoint((valsx[0], valsy[0])):
                    is_in_bfield = True
                    sim.iscurrinbfield = True  # Set the flag in the verlet integrator
                    print("Particle entered magnetic field")
                    break
                else:
                    sim.iscurrinbfield = False  # Ensure it's false if not in any B-field
                



            if is_in_bfield:
                
                valsx = sim.ts_x_verlet(valsx, valsy, charges, True)
                valsy = sim.ts_y_verlet(valsx, valsy, charges)
            else:
                valsx = sim.ts_x_verlet(valsx, valsy, charges)
                valsy = sim.ts_y_verlet(valsx, valsy, charges)

            rect_x = int(valsx[0])
            rect_y = int(valsy[0])
            
            if(rect_x <= 0 or rect_x >= screen_width):
                valsx[1] = -1.01*valsx[1]

            if(rect_y <= 0 or rect_y >= screen_height):
                valsy[1] = -1.01*valsy[1]
            

            rect = pygame.Rect(100, 100, 150, 100)

            # Define a point
            point = (valsx[0], valsy[0])

            # Check if the point is inside the rectangle
            if rect.collidepoint(point):
                print("The point is inside the rectangle.")
            else:
                print("The point is outside the rectangle.")


            screen.fill((0, 0, 0))
            
            for Bfield in magnetic_fields:
                pygame.draw.rect(screen, (244,244,244), Bfield, 5) 

            for x in charges:
                #print("drew")
                if(x[2] == -1):
                    pygame.draw.circle(screen, (0,255,0), (x[0], x[1]),10,10)
                else:
                    pygame.draw.circle(screen, (0,0,255), (x[0], x[1]),10,10)
                
            for x in trail:
                    pygame.draw.circle(screen, (100,100,100), (x[0], x[1]),1)
            trail.append([rect_x, rect_y])

            pygame.draw.circle(screen, rect_color, (rect_x, rect_y),10,10)



            pygame.display.flip()
            # change this if u want stuff to run faster
            time.sleep(0.00001)

try:
    import asyncio
    asyncio.run(main_loop())
except RuntimeError:
    main_loop()