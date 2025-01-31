import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import time

class TrafficSimulation:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.traffic_light_state = "green"
        self.light_timer = 0
        self.light_change_interval = 900
        self.vehicle_speed = 0.8
        self.pedestrian_speed = 0.3
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
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, width, 0, height)
        glMatrixMode(GL_MODELVIEW)

    def draw_road(self):
        # Road
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(0, 200)
        glVertex2f(self.width, 200)
        glVertex2f(self.width, 400)
        glVertex2f(0, 400)
        glEnd()

        # Zebra crossing
        glColor3f(1, 1, 1)
        for x in range(350, 450, 20):
            glBegin(GL_QUADS)
            glVertex2f(x, 200)
            glVertex2f(x + 10, 200)
            glVertex2f(x + 10, 400)
            glVertex2f(x, 400)
            glEnd()

    def draw_traffic_light(self):
        # Light post
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(300, 400)
        glVertex2f(320, 400)
        glVertex2f(320, 500)
        glVertex2f(300, 500)
        glEnd()

        # Light housing
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(290, 480)
        glVertex2f(330, 480)
        glVertex2f(330, 550)
        glVertex2f(290, 550)
        glEnd()

        # Light
        if self.traffic_light_state == "red":
            glColor3f(1, 0, 0)
        else:
            glColor3f(0, 1, 0)
        
        glBegin(GL_QUADS)
        glVertex2f(300, 500)
        glVertex2f(320, 500)
        glVertex2f(320, 530)
        glVertex2f(300, 530)
        glEnd()

    def draw_vehicles(self):
        for vehicle in self.vehicles[:]:
            glColor3f(*vehicle['color'])
            glBegin(GL_QUADS)
            glVertex2f(vehicle['x'], vehicle['y'])
            glVertex2f(vehicle['x'] + 60, vehicle['y'])
            glVertex2f(vehicle['x'] + 60, vehicle['y'] + 30)
            glVertex2f(vehicle['x'], vehicle['y'] + 30)
            glEnd()

            if self.traffic_light_state == "green":
                vehicle['x'] += vehicle['speed']
            
            if vehicle['x'] > self.width:
                self.vehicles.remove(vehicle)

    def draw_pedestrians(self):
        for ped in self.pedestrians[:]:
            glColor3f(1, 0.8, 0)
            glBegin(GL_QUADS)
            glVertex2f(ped['x'], ped['y'])
            glVertex2f(ped['x'] + 15, ped['y'])
            glVertex2f(ped['x'] + 15, ped['y'] + 30)
            glVertex2f(ped['x'], ped['y'] + 30)
            glEnd()

            if self.traffic_light_state == "red" and self.pedestrian_crossing_enabled:
                ped['y'] += ped['speed']

            if ped['y'] > 400:
                self.pedestrians.remove(ped)

    def key_callback(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            if key == glfw.KEY_L:
                self.auto_traffic_light = not self.auto_traffic_light
                if not self.auto_traffic_light:
                    self.traffic_light_state = "red" if self.traffic_light_state == "green" else "green"
            elif key == glfw.KEY_P:
                self.pedestrian_crossing_enabled = True
                if self.traffic_light_state == "red":
                    self.spawn_pedestrians()
            elif key == glfw.KEY_V:
                self.spawn_vehicle()
            elif key == glfw.KEY_R:
                self.reset_simulation()

    def spawn_vehicle(self):
        new_vehicle = {
            'x': -60,
            'y': random.randint(250, 350),
            'speed': self.vehicle_speed,
            'color': (random.random(), random.random(), random.random())
        }
        self.vehicles.append(new_vehicle)

    def spawn_pedestrians(self):
        if self.traffic_light_state == "red" and self.pedestrian_crossing_enabled:
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
            
            self.update_traffic_light()
            self.check_collision()
            
            self.draw_road()
            self.draw_traffic_light()
            self.draw_vehicles()
            self.draw_pedestrians()
            
            if self.accident_occurred:
                glColor3f(1, 0, 0)
                self.reset_simulation()
            
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        
        glfw.terminate()

def main():
    sim = TrafficSimulation()
    sim.run()

if __name__ == "__main__":
    main()