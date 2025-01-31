import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import random
import time
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_TIMES_ROMAN_24

class TrafficSimulation:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.traffic_light_state = "green"
        self.light_timer = 0
        self.light_change_interval = 900
        self.vehicle_speed = 0.8
        self.pedestrian_speed = 0.4
        self.zebra_start = 350
        self.zebra_end = 450
        
        self.vehicles = []
        self.pedestrians = []
        self.accident_occurred = False
        self.auto_traffic_light = True
        self.pedestrian_crossing_enabled = False
        
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")
        
        self.window = glfw.create_window(width, height, "Traffic Simulation", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")
        
        glfw.make_context_current(self.window)
        glfw.set_key_callback(self.window, self.key_callback)
        glutInit()
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, width, 0, height)
        glMatrixMode(GL_MODELVIEW)
        
    def draw_game_over(self):
        # Dark overlay
        glColor4f(0, 0, 0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()

        # Game Over text
        glColor3f(1, 0, 0)
        glRasterPos2f(self.width/2 - 50, self.height/2 + 20)
        for c in "GAME OVER":
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(c))

        # Options
        glColor3f(1, 1, 1)
        glRasterPos2f(self.width/2 - 100, self.height/2 - 20)
        for c in "Press R to Reset or Q to Quit":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    def key_callback(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            if key == glfw.KEY_Q and self.accident_occurred:
                glfw.set_window_should_close(self.window, True)
            elif key == glfw.KEY_L and not self.accident_occurred:
                self.auto_traffic_light = not self.auto_traffic_light
                if not self.auto_traffic_light:
                    self.traffic_light_state = "red" if self.traffic_light_state == "green" else "green"
            elif key == glfw.KEY_P and not self.accident_occurred and self.traffic_light_state == "red":
                if not self.is_vehicle_in_zebra_crossing():
                    self.pedestrian_crossing_enabled = True
                    self.spawn_pedestrians()
            elif key == glfw.KEY_V and not self.accident_occurred:
                self.spawn_vehicle()
            elif key == glfw.KEY_R:
                self.reset_simulation()

    def draw_timer(self):
        time_left = (self.light_change_interval - self.light_timer) // 60
        glColor3f(1, 1, 1)
        glRasterPos2f(270, 540)
        for c in str(time_left):
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    def is_vehicle_in_zebra_crossing(self):
        for vehicle in self.vehicles:
            # Check if any part of vehicle overlaps with zebra crossing
            vehicle_end = vehicle['x'] + 60
            if ((vehicle['x'] >= self.zebra_start and vehicle['x'] <= self.zebra_end) or
                (vehicle_end >= self.zebra_start and vehicle_end <= self.zebra_end) or
                (vehicle['x'] <= self.zebra_start and vehicle_end >= self.zebra_end)):
                return True
        return False

    def spawn_vehicle(self):
        new_vehicle = {
            'x': -60,
            'y': random.randint(250, 350),
            'speed': self.vehicle_speed,
            'color': (random.random(), random.random(), random.random())
        }
        self.vehicles.append(new_vehicle)

    def spawn_pedestrians(self):
        # Only spawn if light is red and no vehicles in crossing
        if (self.traffic_light_state == "red" and 
            self.pedestrian_crossing_enabled and 
            not self.is_vehicle_in_zebra_crossing()):
            for _ in range(3):
                new_pedestrian = {
                    'x': random.randint(360, 440),
                    'y': 180,
                    'speed': self.pedestrian_speed
                }
                self.pedestrians.append(new_pedestrian)

    def update_traffic_light(self):
        if self.auto_traffic_light:
            self.light_timer += 1
            if self.light_timer >= self.light_change_interval:
                self.traffic_light_state = "red" if self.traffic_light_state == "green" else "green"
                self.light_timer = 0
                self.pedestrian_crossing_enabled = False
                self.pedestrians.clear()

    def check_collision(self):
        for vehicle in self.vehicles:
            for ped in self.pedestrians:
                if (abs(vehicle['x'] - ped['x']) < 40 and 
                    abs(vehicle['y'] - ped['y']) < 30):
                    self.accident_occurred = True
                    return

    def update_vehicles(self):
        for i, vehicle in enumerate(self.vehicles[:]):
            can_move = True
            
            # Check for vehicles in front
            for front_vehicle in self.vehicles[:i]:
                if (front_vehicle['x'] > vehicle['x'] and 
                    front_vehicle['x'] - (vehicle['x'] + 60) < 20):
                    can_move = False
                    break
            
            if can_move:
                if self.traffic_light_state == "red":
                    vehicle_end = vehicle['x'] + 60
                    # If vehicle is touching or within zebra crossing, allow movement
                    if (vehicle['x'] >= self.zebra_start or 
                        vehicle_end >= self.zebra_start):
                        vehicle['x'] += vehicle['speed']
                    # If vehicle is before zebra crossing, move until just before it
                    elif vehicle['x'] + vehicle['speed'] < self.zebra_start - 60:
                        vehicle['x'] += vehicle['speed']
                else:
                    vehicle['x'] += vehicle['speed']

            # Remove off-screen vehicles
            if vehicle['x'] > self.width:
                self.vehicles.remove(vehicle)

    def update_pedestrians(self):
        # Only update pedestrians if no vehicle is in crossing
        if not self.is_vehicle_in_zebra_crossing():
            for ped in self.pedestrians[:]:
                if self.traffic_light_state == "red" and self.pedestrian_crossing_enabled:
                    ped['y'] += ped['speed']
                if ped['y'] > 400:
                    self.pedestrians.remove(ped)

    def draw_road(self):
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(0, 200)
        glVertex2f(self.width, 200)
        glVertex2f(self.width, 400)
        glVertex2f(0, 400)
        glEnd()

        glColor3f(1, 1, 1)
        for x in range(self.zebra_start, self.zebra_end, 20):
            glBegin(GL_QUADS)
            glVertex2f(x, 200)
            glVertex2f(x + 10, 200)
            glVertex2f(x + 10, 400)
            glVertex2f(x, 400)
            glEnd()

    def draw_traffic_light(self):
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(300, 400)
        glVertex2f(320, 400)
        glVertex2f(320, 500)
        glVertex2f(300, 500)
        glEnd()

        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(290, 480)
        glVertex2f(330, 480)
        glVertex2f(330, 550)
        glVertex2f(290, 550)
        glEnd()

        glColor3f(1, 0, 0) if self.traffic_light_state == "red" else glColor3f(0, 1, 0)
        glBegin(GL_QUADS)
        glVertex2f(300, 500)
        glVertex2f(320, 500)
        glVertex2f(320, 530)
        glVertex2f(300, 530)
        glEnd()

    def draw_vehicles(self):
        for vehicle in self.vehicles:
            glColor3f(*vehicle['color'])
            glBegin(GL_QUADS)
            glVertex2f(vehicle['x'], vehicle['y'])
            glVertex2f(vehicle['x'] + 60, vehicle['y'])
            glVertex2f(vehicle['x'] + 60, vehicle['y'] + 30)
            glVertex2f(vehicle['x'], vehicle['y'] + 30)
            glEnd()

    def draw_pedestrians(self):
        for ped in self.pedestrians:
            glColor3f(1, 0.8, 0)
            glBegin(GL_QUADS)
            glVertex2f(ped['x'], ped['y'])
            glVertex2f(ped['x'] + 15, ped['y'])
            glVertex2f(ped['x'] + 15, ped['y'] + 30)
            glVertex2f(ped['x'], ped['y'] + 30)
            glEnd()

    def reset_simulation(self):
        self.vehicles.clear()
        self.pedestrians.clear()
        self.accident_occurred = False
        self.traffic_light_state = "green"
        self.auto_traffic_light = True
        self.pedestrian_crossing_enabled = False
        self.light_timer = 0

    def run(self):
        last_time = time.time()
        frame_delay = 1/60.0

        while not glfw.window_should_close(self.window):
            current_time = time.time()
            if current_time - last_time < frame_delay:
                time.sleep(frame_delay - (current_time - last_time))
            last_time = time.time()
            
            glClear(GL_COLOR_BUFFER_BIT)
            
            if not self.accident_occurred:
                self.update_traffic_light()
                self.check_collision()
                self.update_vehicles()
                self.update_pedestrians()
            
            self.draw_road()
            self.draw_traffic_light()
            self.draw_vehicles()
            self.draw_pedestrians()
            self.draw_timer()
            
            if self.accident_occurred:
                self.draw_game_over()
            
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        
        glfw.terminate()

def main():
    sim = TrafficSimulation()
    sim.run()

if __name__ == "__main__":
    main()