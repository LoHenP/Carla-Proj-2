from __future__ import print_function

# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================


import glob
import os
import sys
import time

from basic_agent import BasicAgent

# from reportlab.lib.colors import cyan, red, green, white, orange


try:
    sys.path.append(
        glob.glob(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/carla/dist/carla-*%d.%d-%s.egg' % (
            sys.version_info.major,
            sys.version_info.minor,
            'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

try:
    sys.path.append("/opt/carla-simulator/PythonAPI/carla")
except IndexError:
    pass

# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================


import carla

from carla import ColorConverter as cc

# from agents.navigation.basic_agent import BasicAgent
# from agents.navigation.behavior_agent import BehaviorAgent



# import PythonAPI
# import PythonAPI.util

# from carla import draw_waypoint_union, draw_transform
# from lane_explorer import draw_waypoint_union, draw_transform, cyan, red, green, white, orange
import argparse
import collections
import datetime
import logging
import math
import random
import re
import weakref

try:
    import pygame
    from pygame.locals import KMOD_CTRL
    from pygame.locals import KMOD_SHIFT
    from pygame.locals import K_0
    from pygame.locals import K_9
    from pygame.locals import K_BACKQUOTE
    from pygame.locals import K_BACKSPACE
    from pygame.locals import K_COMMA
    from pygame.locals import K_DOWN
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_F1
    from pygame.locals import K_LEFT
    from pygame.locals import K_PERIOD
    from pygame.locals import K_RIGHT
    from pygame.locals import K_SLASH
    from pygame.locals import K_SPACE
    from pygame.locals import K_TAB
    from pygame.locals import K_UP
    from pygame.locals import K_a
    from pygame.locals import K_b
    from pygame.locals import K_c
    from pygame.locals import K_d
    from pygame.locals import K_g
    from pygame.locals import K_h
    from pygame.locals import K_i
    from pygame.locals import K_l
    from pygame.locals import K_m
    from pygame.locals import K_n
    from pygame.locals import K_p
    from pygame.locals import K_k
    from pygame.locals import K_j
    from pygame.locals import K_q
    from pygame.locals import K_r
    from pygame.locals import K_s
    from pygame.locals import K_v
    from pygame.locals import K_w
    from pygame.locals import K_x
    from pygame.locals import K_z
    from pygame.locals import K_MINUS
    from pygame.locals import K_EQUALS
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')

red = carla.Color(255, 0, 0)
green = carla.Color(0, 255, 0)
blue = carla.Color(47, 210, 231)
cyan = carla.Color(0, 255, 255)
yellow = carla.Color(255, 255, 0)
orange = carla.Color(255, 162, 0)
white = carla.Color(255, 255, 255)

trail_life_time = 10
waypoint_separation = 10



# ==============================================================================
# -- transform ----------------------------------------------------------
# ==============================================================================

S1 = carla.Transform(carla.Location(x=154, y=12.75, z=2), carla.Rotation(pitch=0.0, yaw=90, roll=0))

T1 = carla.Transform(carla.Location(x=92.75, y=45, z=0), carla.Rotation(pitch=0, yaw=-90, roll=0))

# T2 = carla.Transform(carla.Location(x=93, y=12, z=0), carla.Rotation(pitch=0, yaw=-90, roll=0))
T3 = carla.Transform(carla.Location(x=103, y=2.25, z=0), carla.Rotation(pitch=0, yaw=0, roll=-0.000305))
# T4 = carla.Transform(carla.Location(x=143.083298, y=2.472215, z=-0.000568), carla.Rotation(pitch=-0.074954, yaw=0.611216, roll=0.000273))
T5 = carla.Transform(carla.Location(x=154, y=12.75, z=0), carla.Rotation(pitch=0.0, yaw=90, roll=-0.000031))
# T6 = carla.Transform(carla.Location(x=153.716843, y=45.599705, z=-0.001173), carla.Rotation(pitch=-0.032286, yaw=88.864830, roll=0.000117))
T7 = carla.Transform(carla.Location(x=143.75, y=55.25, z=0), carla.Rotation(pitch=0.047217, yaw=-180, roll=-0.000153))
# T8 = carla.Transform(carla.Location(x=102.361626, y=54.566963, z=0.001186), carla.Rotation(pitch=-0.198704, yaw=-178.541473, roll=0.000706))

P1 = carla.Transform(carla.Location(x=339, y=14.5, z=0), carla.Rotation(pitch=0, yaw=-90, roll=0))
P2 = carla.Transform(carla.Location(x=382, y=2.4, z=0), carla.Rotation(pitch=0, yaw=-90, roll=0))
P3 = carla.Transform(carla.Location(x=392, y=313, z=0), carla.Rotation(pitch=0, yaw=-90, roll=0))
P4 = carla.Transform(carla.Location(x=350, y=326.5, z=0), carla.Rotation(pitch=0, yaw=-90, roll=0))


L1 = carla.Location(x=98.164513, y=45.598881, z=0)
L3 = carla.Location(x=98.164513, y=2.502027, z=0)
L2 = carla.Location(x=148.005653, y=2.502027, z=0)
L4 = carla.Location(x=148.005653, y=45.598881, z=0)

# Auto_Points = [T1, T2, T3, T4, T5, T6, T7, T8]
Auto_Points = [T1, T3, T5, T7]
Two_Points = [P1, P2, P3, P4]

custom_waypoints = [Auto_Points, Two_Points]




# ==============================================================================
# -- Global functions ----------------------------------------------------------
# ==============================================================================

def calculate_distance(self_location, other_actor_location):
    p1 = (self_location.x, self_location.y, self_location.z)
    p2 = (other_actor_location.x, other_actor_location.y, other_actor_location.z)
    return math.sqrt((p1[0] - p2[0])**2 +
                     (p1[1] - p2[1])**2 +
                     (p1[2] - p2[2])**2)

def draw_transform(debug, trans, col=carla.Color(255, 0, 0), lt=-1):
    debug.draw_arrow(
        trans.location, trans.location + trans.get_forward_vector(),
        thickness=0.05, arrow_size=0.1, color=col, life_time=lt)


def draw_waypoint_union(debug, w0, w1, color=carla.Color(255, 0, 0), lt=5):
    debug.draw_line(
        w0.transform.location + carla.Location(z=0.25),
        w1.transform.location + carla.Location(z=0.25),
        thickness=0.1, color=color, life_time=lt, persistent_lines=False)
    debug.draw_point(w1.transform.location + carla.Location(z=0.25), 0.1, color, lt, False)


def draw_waypoint_info(debug, w, lt=5):
    w_loc = w.transform.location
    debug.draw_string(w_loc + carla.Location(z=0.5), "lane: " + str(w.lane_id), False, yellow, lt)
    debug.draw_string(w_loc + carla.Location(z=1.0), "road: " + str(w.road_id), False, blue, lt)
    debug.draw_string(w_loc + carla.Location(z=-.5), str(w.lane_change), False, red, lt)


def draw_junction(debug, junction, l_time=10):
    """Draws a junction bounding box and the initial and final waypoint of every lane."""
    # draw bounding box
    box = junction.bounding_box
    point1 = box.location + carla.Location(x=box.extent.x, y=box.extent.y, z=2)
    point2 = box.location + carla.Location(x=-box.extent.x, y=box.extent.y, z=2)
    point3 = box.location + carla.Location(x=-box.extent.x, y=-box.extent.y, z=2)
    point4 = box.location + carla.Location(x=box.extent.x, y=-box.extent.y, z=2)
    debug.draw_line(
        point1, point2,
        thickness=0.1, color=orange, life_time=l_time, persistent_lines=False)
    debug.draw_line(
        point2, point3,
        thickness=0.1, color=orange, life_time=l_time, persistent_lines=False)
    debug.draw_line(
        point3, point4,
        thickness=0.1, color=orange, life_time=l_time, persistent_lines=False)
    debug.draw_line(
        point4, point1,
        thickness=0.1, color=orange, life_time=l_time, persistent_lines=False)
    # draw junction pairs (begin-end) of every lane
    junction_w = junction.get_waypoints(carla.LaneType.Any)
    for pair_w in junction_w:
        draw_transform(debug, pair_w[0].transform, orange, l_time)
        debug.draw_point(
            pair_w[0].transform.location + carla.Location(z=0.75), 0.1, orange, l_time, False)
        draw_transform(debug, pair_w[1].transform, orange, l_time)
        debug.draw_point(
            pair_w[1].transform.location + carla.Location(z=0.75), 0.1, orange, l_time, False)
        debug.draw_line(
            pair_w[0].transform.location + carla.Location(z=0.75),
            pair_w[1].transform.location + carla.Location(z=0.75), 0.1, white, l_time, False)


def find_weather_presets():
    rgx = re.compile('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')
    name = lambda x: ' '.join(m.group(0) for m in rgx.finditer(x))
    presets = [x for x in dir(carla.WeatherParameters) if re.match('[A-Z].+', x)]
    return [(getattr(carla.WeatherParameters, x), name(x)) for x in presets]


def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name


# ==============================================================================
# -- World ---------------------------------------------------------------------
# ==============================================================================


class World(object):
    def __init__(self, carla_world, hud, args):
        self.world = carla_world
        self.debug = carla.DebugHelper
        self.actor_role_name = args.rolename
        try:
            self.map = self.world.get_map()
        except RuntimeError as error:
            print('RuntimeError: {}'.format(error))
            print('  The server could not send the OpenDRIVE (.xodr) file:')
            print('  Make sure it exists, has the same name of your town, and is correct.')
            sys.exit(1)
        self.hud = hud
        self.player = None
        self.collision_sensor = None

        self.front_sensor = None
        self.back_sensor = None

        self.front_right_sensor = None
        self.front_left_sensor = None

        self.right_sensor = None
        self.left_sensor = None

        self.back_right_sensor = None
        self.back_left_sensor = None

        self.lane_invasion_sensor = None
        self.gnss_sensor = None
        self.imu_sensor = None
        self.radar_sensor = None
        self.camera_manager = None
        self._weather_presets = find_weather_presets()
        self._weather_index = 0
        self._actor_filter = args.filter
        self._gamma = args.gamma
        self.restart()
        self.world.on_tick(hud.on_world_tick)
        self.recording_enabled = False
        self.recording_start = 0
        self.constant_velocity_enabled = False
        self.current_map_layer = 0
        self.map_layer_names = [
            carla.MapLayer.NONE,
            carla.MapLayer.Buildings,
            carla.MapLayer.Decals,
            carla.MapLayer.Foliage,
            carla.MapLayer.Ground,
            carla.MapLayer.ParkedVehicles,
            carla.MapLayer.Particles,
            carla.MapLayer.Props,
            carla.MapLayer.StreetLights,
            carla.MapLayer.Walls,
            carla.MapLayer.All
        ]

        self.checker = None
        self.emergency_stop = False

        self.is_auto_pilot = False
        self.agent = None

        self.is_turning_right = False
        self.is_turning_left = False

    def restart(self):
        self.player_max_speed = 1.589
        self.player_max_speed_fast = 3.713
        # Keep same camera config if the camera manager exists.
        cam_index = self.camera_manager.index if self.camera_manager is not None else 0
        cam_pos_index = self.camera_manager.transform_index if self.camera_manager is not None else 0
        # Get a random blueprint.

        vehicle_blueprints = self.world.get_blueprint_library().filter('vehicle.carlamotors.carlacola')

        blueprint = vehicle_blueprints[0]

        # blueprint = random.choice(self.world.get_blueprint_library().filter(self._actor_filter))
        # blueprint.set_attribute('role_name', self.actor_role_name)
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        if blueprint.has_attribute('driver_id'):
            driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
            blueprint.set_attribute('driver_id', driver_id)
        if blueprint.has_attribute('is_invincible'):
            blueprint.set_attribute('is_invincible', 'true')
        # set the max speed
        if blueprint.has_attribute('speed'):
            self.player_max_speed = float(blueprint.get_attribute('speed').recommended_values[1])
            self.player_max_speed_fast = float(blueprint.get_attribute('speed').recommended_values[2])
        else:
            print("No recommended values for 'speed' attribute")
        # Spawn the player.
        if self.player is not None:
            spawn_point = self.player.get_transform()
            spawn_point.location.z += 2.0
            spawn_point.rotation.roll = 0.0
            spawn_point.rotation.pitch = 0.0
            self.destroy()
            spawn_points = self.map.get_spawn_points()
            spawn_point = random.choice(spawn_points) if spawn_points else carla.Transform()
            print(spawn_point)
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
            # self.agent = BehaviorAgent(self.player, behavior='cautious')
        while self.player is None:
            if not self.map.get_spawn_points():
                print('There are no spawn points available in your map/town.')
                print('Please add some Vehicle Spawn Point to your UE4 scene.')
                sys.exit(1)

            spawn_points = self.map.get_spawn_points()
            spawn_point = random.choice(spawn_points) if spawn_points else carla.Transform()
            # spawn_point = S1
            print(spawn_point)
            # self.player = self.world.try_spawn_actor(blueprint, T1)
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
            # self.agent = BehaviorAgent(self.player, behavior='cautious')
            # self.agent = BehaviorAgent(self.player, behavior='cautious')
            # destination = S1
            # self.agent.set_destination(start_location=spawn_point, end_location=destination)



        # Set up the sensors.
        self.collision_sensor = CollisionSensor(self.player, self.hud)

        self.front_sensor = FrontSensor(self, self.player, self.hud)
        # self.front_left_sensor = FrontLeftSensor(self, self.player, self.hud)
        # self.front_right_sensor = FrontRightSensor(self, self.player, self.hud)
        # self.back_sensor = BackSensor(self, self.player, self.hud)
        # self.back_left_sensor = BackLeftSensor(self, self.player, self.hud)
        # self.back_right_sensor = BackRightSensor(self, self.player, self.hud)
        # self.right_sensor = RightSensor(self, self.player, self.hud)
        self.left_sensor = LeftSensor(self, self.player, self.hud)
        # self.checker = Checker(self.player)
        # self.front_sensor = ObstacleSensor(self.player, self.hud)
        self.lane_invasion_sensor = LaneInvasionSensor(self.player, self.hud)
        self.gnss_sensor = GnssSensor(self.player)
        self.imu_sensor = IMUSensor(self.player)
        self.camera_manager = CameraManager(self.player, self.hud, self._gamma)
        self.camera_manager.transform_index = cam_pos_index
        self.camera_manager.set_sensor(cam_index, notify=False)
        actor_type = get_actor_display_name(self.player)
        self.hud.notification(actor_type)

    def next_weather(self, reverse=False):
        self._weather_index += -1 if reverse else 1
        self._weather_index %= len(self._weather_presets)
        preset = self._weather_presets[self._weather_index]
        self.hud.notification('Weather: %s' % preset[1])
        self.player.get_world().set_weather(preset[0])

    def next_map_layer(self, reverse=False):
        self.current_map_layer += -1 if reverse else 1
        self.current_map_layer %= len(self.map_layer_names)
        selected = self.map_layer_names[self.current_map_layer]
        self.hud.notification('LayerMap selected: %s' % selected)

    def load_map_layer(self, unload=False):
        selected = self.map_layer_names[self.current_map_layer]
        if unload:
            self.hud.notification('Unloading map layer: %s' % selected)
            self.world.unload_map_layer(selected)
        else:
            self.hud.notification('Loading map layer: %s' % selected)
            self.world.load_map_layer(selected)

    def toggle_radar(self):
        if self.radar_sensor is None:
            self.radar_sensor = RadarSensor(self.player)
        elif self.radar_sensor.sensor is not None:
            self.radar_sensor.sensor.destroy()
            self.radar_sensor = None

    def cast_ray(self, initial_location, final_location):
        return self.world.cast_ray(initial_location, final_location)

    def tick(self, clock):
        self.hud.tick(self, clock)

    def render(self, display):
        self.camera_manager.render(display)
        self.hud.render(display)

    def destroy_sensors(self):
        self.camera_manager.sensor.destroy()
        self.camera_manager.sensor = None
        self.camera_manager.index = None

    def destroy(self):
        if self.radar_sensor is not None:
            self.toggle_radar()
        if self.checker is not None:
            self.checker.remove_checker()
            self.checker = None
        sensors = [
            self.camera_manager.sensor,
            self.collision_sensor.sensor,

            self.front_sensor.sensor,
            # self.back_sensor.sensor,

            # self.right_sensor.sensor,
            self.left_sensor.sensor,

            # self.front_right_sensor.sensor,
            # self.front_left_sensor.sensor,

            # self.back_left_sensor.sensor,
            # self.back_right_sensor.sensor,

            self.lane_invasion_sensor.sensor,
            self.gnss_sensor.sensor,
            self.imu_sensor.sensor,
        ]
        for sensor in sensors:
            if sensor is not None:
                sensor.stop()
                sensor.destroy()
        if self.player is not None:
            self.player.destroy()
            # self.agent.destroy()


# ==============================================================================
# -- KeyboardControl -----------------------------------------------------------
# ==============================================================================


class KeyboardControl(object):
    """Class that handles keyboard input."""

    def __init__(self, world, start_in_autopilot):
        self._carsim_enabled = False
        self._carsim_road = False
        self._autopilot_enabled = start_in_autopilot
        self.world = world
        self.player = world.player

        self.current_arr = None
        self.route_count = 0
        self.is_route_end = False

        if isinstance(world.player, carla.Vehicle):
            self._control = carla.VehicleControl()
            self._lights = carla.VehicleLightState.NONE
            world.player.set_autopilot(self._autopilot_enabled)
            world.player.set_light_state(self._lights)
        elif isinstance(world.player, carla.Walker):
            self._control = carla.WalkerControl()
            self._autopilot_enabled = False
            self._rotation = world.player.get_transform().rotation
        else:
            raise NotImplementedError("Actor type not supported")
        self._steer_cache = 0.0
        world.hud.notification("Press 'H' or '?' for help.", seconds=4.0)

    def parse_events(self, client, world, clock):

        # if world.is_auto_pilot:
        #     return

        if isinstance(self._control, carla.VehicleControl):
            current_lights = self._lights
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYUP:
                if self._is_quit_shortcut(event.key):
                    return True
                elif event.key == K_BACKSPACE:
                    if self._autopilot_enabled:
                        world.player.set_autopilot(False)
                        world.restart()
                        world.player.set_autopilot(True)
                    else:
                        world.restart()
                elif event.key == K_F1:
                    world.hud.toggle_info()
                elif event.key == K_v and pygame.key.get_mods() & KMOD_SHIFT:
                    world.next_map_layer(reverse=True)
                elif event.key == K_v:
                    world.next_map_layer()
                elif event.key == K_b and pygame.key.get_mods() & KMOD_SHIFT:
                    world.load_map_layer(unload=True)
                elif event.key == K_b:
                    world.load_map_layer()
                elif event.key == K_h or (event.key == K_SLASH and pygame.key.get_mods() & KMOD_SHIFT):
                    world.hud.help.toggle()
                elif event.key == K_TAB:
                    world.camera_manager.toggle_camera()
                elif event.key == K_c and pygame.key.get_mods() & KMOD_SHIFT:
                    world.next_weather(reverse=True)
                elif event.key == K_c:
                    world.next_weather()
                elif event.key == K_g:
                    world.toggle_radar()
                elif event.key == K_BACKQUOTE:
                    world.camera_manager.next_sensor()
                elif event.key == K_n:
                    world.camera_manager.next_sensor()
                elif event.key == K_w and (pygame.key.get_mods() & KMOD_CTRL):
                    print(world.constant_velocity_enabled)
                    if world.constant_velocity_enabled:
                        world.player.disable_constant_velocity()
                        world.constant_velocity_enabled = False
                        world.hud.notification("Disabled Constant Velocity Mode")
                        print('60 off!!')
                    else:
                        world.player.enable_constant_velocity(carla.Vector3D(1.4, 0, 0))
                        world.constant_velocity_enabled = True
                        world.hud.notification("Enabled Constant Velocity Mode at 60 km/h")
                        print('60 on!!')
                elif event.key > K_0 and event.key <= K_9:
                    world.camera_manager.set_sensor(event.key - 1 - K_0)
                elif event.key == K_r and not (pygame.key.get_mods() & KMOD_CTRL):
                    world.camera_manager.toggle_recording()
                elif event.key == K_r and (pygame.key.get_mods() & KMOD_CTRL):
                    if (world.recording_enabled):
                        client.stop_recorder()
                        world.recording_enabled = False
                        world.hud.notification("Recorder is OFF")
                    else:
                        client.start_recorder("manual_recording.rec")
                        world.recording_enabled = True
                        world.hud.notification("Recorder is ON")
                elif event.key == K_p and (pygame.key.get_mods() & KMOD_CTRL):
                    # stop recorder
                    client.stop_recorder()
                    world.recording_enabled = False
                    # work around to fix camera at start of replaying
                    current_index = world.camera_manager.index
                    world.destroy_sensors()
                    # disable autopilot
                    self._autopilot_enabled = False
                    world.player.set_autopilot(self._autopilot_enabled)
                    world.hud.notification("Replaying file 'manual_recording.rec'")
                    # replayer
                    client.replay_file("manual_recording.rec", world.recording_start, 0, 0)
                    world.camera_manager.set_sensor(current_index)
                elif event.key == K_k and (pygame.key.get_mods() & KMOD_CTRL):
                    print("k pressed")
                    world.player.enable_carsim("d:/CVC/carsim/DataUE4/ue4simfile.sim")
                elif event.key == K_j and (pygame.key.get_mods() & KMOD_CTRL):
                    self._carsim_road = not self._carsim_road
                    world.player.use_carsim_road(self._carsim_road)
                    print("j pressed, using carsim road =", self._carsim_road)
                # elif event.key == K_i and (pygame.key.get_mods() & KMOD_CTRL):
                #     print("i pressed")
                #     imp = carla.Location(z=50000)
                #     world.player.add_impulse(imp)
                elif event.key == K_MINUS and (pygame.key.get_mods() & KMOD_CTRL):
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        world.recording_start -= 10
                    else:
                        world.recording_start -= 1
                    world.hud.notification("Recording start time is %d" % (world.recording_start))
                elif event.key == K_EQUALS and (pygame.key.get_mods() & KMOD_CTRL):
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        world.recording_start += 10
                    else:
                        world.recording_start += 1
                    world.hud.notification("Recording start time is %d" % (world.recording_start))
                if isinstance(self._control, carla.VehicleControl):
                    if event.key == K_q:
                        self._control.gear = 1 if self._control.reverse else -1
                    elif event.key == K_m:
                        self._control.manual_gear_shift = not self._control.manual_gear_shift
                        self._control.gear = world.player.get_control().gear
                        world.hud.notification('%s Transmission' %
                                               ('Manual' if self._control.manual_gear_shift else 'Automatic'))
                    elif self._control.manual_gear_shift and event.key == K_COMMA:
                        self._control.gear = max(-1, self._control.gear - 1)
                    elif self._control.manual_gear_shift and event.key == K_PERIOD:
                        self._control.gear = self._control.gear + 1
                    elif event.key == K_p and not pygame.key.get_mods() & KMOD_CTRL:
                        self.world.is_auto_pilot = not self.world.is_auto_pilot
                        self._autopilot_enabled = not self._autopilot_enabled



                        # self._autopilot_enabled = not self._autopilot_enabled
                        # world.player.set_autopilot(self._autopilot_enabled)
                        # world.hud.notification(
                        #     'Autopilot %s' % ('On' if self._autopilot_enabled else 'Off'))
                        #
                        # # tm = client.get_trafficmanager(8000)
                        # # tm.vehicle_percentage_speed_difference(world.player, 85.0)
                        # # print(tm)
                    elif event.key == K_l and pygame.key.get_mods() & KMOD_CTRL:
                        current_lights ^= carla.VehicleLightState.Special1
                    elif event.key == K_l and pygame.key.get_mods() & KMOD_SHIFT:
                        current_lights ^= carla.VehicleLightState.HighBeam
                    elif event.key == K_l:
                        # Use 'L' key to switch between lights:
                        # closed -> position -> low beam -> fog
                        if not self._lights & carla.VehicleLightState.Position:
                            world.hud.notification("Position lights")
                            current_lights |= carla.VehicleLightState.Position
                        else:
                            world.hud.notification("Low beam lights")
                            current_lights |= carla.VehicleLightState.LowBeam
                        if self._lights & carla.VehicleLightState.LowBeam:
                            world.hud.notification("Fog lights")
                            current_lights |= carla.VehicleLightState.Fog
                        if self._lights & carla.VehicleLightState.Fog:
                            world.hud.notification("Lights off")
                            current_lights ^= carla.VehicleLightState.Position
                            current_lights ^= carla.VehicleLightState.LowBeam
                            current_lights ^= carla.VehicleLightState.Fog
                    elif event.key == K_i:
                        current_lights ^= carla.VehicleLightState.Interior
                    elif event.key == K_z:
                        current_lights ^= carla.VehicleLightState.LeftBlinker
                    elif event.key == K_x:
                        current_lights ^= carla.VehicleLightState.RightBlinker

        if not self._autopilot_enabled:
            if isinstance(self._control, carla.VehicleControl):
                self._parse_vehicle_keys(pygame.key.get_pressed(), clock.get_time())
                self._control.reverse = self._control.gear < 0
                # Set automatic control-related vehicle lights
                if self._control.brake:
                    current_lights |= carla.VehicleLightState.Brake
                else:  # Remove the Brake flag
                    current_lights &= ~carla.VehicleLightState.Brake
                if self._control.reverse:
                    current_lights |= carla.VehicleLightState.Reverse
                else:  # Remove the Reverse flag
                    current_lights &= ~carla.VehicleLightState.Reverse
                if current_lights != self._lights:  # Change the light state only if necessary
                    self._lights = current_lights
                    world.player.set_light_state(carla.VehicleLightState(self._lights))
            elif isinstance(self._control, carla.WalkerControl):
                self._parse_walker_keys(pygame.key.get_pressed(), clock.get_time(), world)
            world.player.apply_control(self._control)



        if world.emergency_stop:
            # print('emergency_stop!!!!')
            self._control.throttle = 0.0
            # self._control.brake = min(self._control.brake + 0.2, 1)
            self._control.brake = 1
            self._control.steer = 0
            self._control.hand_brake = 1
            world.player.apply_control(self._control)

        else:
            if not world.agent.done():
                self._control = world.agent.run_step()
                world.player.apply_control(self._control)
            else:
                current_location = world.player.get_location()
                near_point = None
                T_index = 0

                for arr in custom_waypoints:
                    if self.current_arr == None:
                        self.current_arr = arr
                    elif self.current_arr != arr:
                        continue

                    for i, T in enumerate(arr):
                        if near_point is None:
                            near_point = T
                            T_index = i
                            continue

                        if current_location.distance(near_point.location) >= current_location.distance(T.location):
                            near_point = T
                            T_index = i

                        else:
                            continue

                    if T_index == len(Auto_Points) - 1:
                        T_index = -1

                    if self.route_count == 5:
                        print("route end")
                        self.is_route_end = True
                        near_point = None
                        T_index = 0
                        self.current_arr = None
                        self.route_count = 0
                        continue


                    next_point = arr[T_index+1]
                    world.agent.set_destination((
                        next_point.location.x,
                        next_point.location.y,
                        next_point.location.z
                    ), self.is_route_end)
                    self.is_route_end = False
                    self.route_count += 1

    def _parse_vehicle_keys(self, keys, milliseconds):
        if keys[K_UP] or keys[K_w]:
            self._control.throttle = min(self._control.throttle + 0.01, 1)
        else:
            self._control.throttle = 0.0

        if keys[K_DOWN] or keys[K_s]:
            self._control.brake = min(self._control.brake + 0.2, 1)
        else:
            self._control.brake = 0

        steer_increment = 5e-4 * milliseconds
        if keys[K_LEFT] or keys[K_a]:
            if self._steer_cache > 0:
                self._steer_cache = 0
            else:
                self._steer_cache -= steer_increment
        elif keys[K_RIGHT] or keys[K_d]:
            if self._steer_cache < 0:
                self._steer_cache = 0
            else:
                self._steer_cache += steer_increment
        else:
            self._steer_cache = 0.0
        self._steer_cache = min(0.7, max(-0.7, self._steer_cache))
        self._control.steer = round(self._steer_cache, 1)
        self._control.hand_brake = keys[K_SPACE]

    def _parse_walker_keys(self, keys, milliseconds, world):
        self._control.speed = 0.0
        if keys[K_DOWN] or keys[K_s]:
            self._control.speed = 0.0
        if keys[K_LEFT] or keys[K_a]:
            self._control.speed = .01
            self._rotation.yaw -= 0.08 * milliseconds
        if keys[K_RIGHT] or keys[K_d]:
            self._control.speed = .01
            self._rotation.yaw += 0.08 * milliseconds
        if keys[K_UP] or keys[K_w]:
            self._control.speed = world.player_max_speed_fast if pygame.key.get_mods() & KMOD_SHIFT else world.player_max_speed
        self._control.jump = keys[K_SPACE]
        self._rotation.yaw = round(self._rotation.yaw, 1)
        self._control.direction = self._rotation.get_forward_vector()

    @staticmethod
    def _is_quit_shortcut(key):
        return (key == K_ESCAPE) or (key == K_q and pygame.key.get_mods() & KMOD_CTRL)


# ==============================================================================
# -- HUD -----------------------------------------------------------------------
# ==============================================================================


class HUD(object):
    def __init__(self, width, height):
        self.dim = (width, height)
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        font_name = 'courier' if os.name == 'nt' else 'mono'
        fonts = [x for x in pygame.font.get_fonts() if font_name in x]
        default_font = 'ubuntumono'
        mono = default_font if default_font in fonts else fonts[0]
        mono = pygame.font.match_font(mono)
        self._font_mono = pygame.font.Font(mono, 12 if os.name == 'nt' else 14)
        self._notifications = FadingText(font, (width, 40), (0, height - 40))
        # self.help = HelpText(pygame.font.Font(mono, 16), width, height)
        self.server_fps = 0
        self.frame = 0
        self.simulation_time = 0
        self._show_info = True
        self._info_text = []
        self._server_clock = pygame.time.Clock()

    def on_world_tick(self, timestamp):
        self._server_clock.tick()
        self.server_fps = self._server_clock.get_fps()
        self.frame = timestamp.frame
        self.simulation_time = timestamp.elapsed_seconds

    def tick(self, world, clock):
        self._notifications.tick(world, clock)
        if not self._show_info:
            return
        t = world.player.get_transform()
        v = world.player.get_velocity()
        c = world.player.get_control()
        compass = world.imu_sensor.compass
        heading = 'N' if compass > 270.5 or compass < 89.5 else ''
        heading += 'S' if 90.5 < compass < 269.5 else ''
        heading += 'E' if 0.5 < compass < 179.5 else ''
        heading += 'W' if 180.5 < compass < 359.5 else ''
        colhist = world.collision_sensor.get_collision_history()
        collision = [colhist[x + self.frame - 200] for x in range(0, 200)]
        max_col = max(1.0, max(collision))
        collision = [x / max_col for x in collision]
        vehicles = world.world.get_actors().filter('vehicle.*')
        self._info_text = [
            'Server:  % 16.0f FPS' % self.server_fps,
            'Client:  % 16.0f FPS' % clock.get_fps(),
            '',
            'Vehicle: % 20s' % get_actor_display_name(world.player, truncate=20),
            'Map:     % 20s' % world.map.name.split('/')[-1],
            'Simulation time: % 12s' % datetime.timedelta(seconds=int(self.simulation_time)),
            '',
            'Speed:   % 15.0f km/h' % (3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)),
            u'Compass:% 17.0f\N{DEGREE SIGN} % 2s' % (compass, heading),
            'Accelero: (%5.1f,%5.1f,%5.1f)' % (world.imu_sensor.accelerometer),
            'Gyroscop: (%5.1f,%5.1f,%5.1f)' % (world.imu_sensor.gyroscope),
            'Location:% 20s' % ('(% 5.1f, % 5.1f)' % (t.location.x, t.location.y)),
            'GNSS:% 24s' % ('(% 2.6f, % 3.6f)' % (world.gnss_sensor.lat, world.gnss_sensor.lon)),
            'Height:  % 18.0f m' % t.location.z,
            '']
        if isinstance(c, carla.VehicleControl):
            self._info_text += [
                ('Throttle:', c.throttle, 0.0, 1.0),
                ('Steer:', c.steer, -1.0, 1.0),
                ('Brake:', c.brake, 0.0, 1.0),
                ('Reverse:', c.reverse),
                ('Hand brake:', c.hand_brake),
                ('Manual:', c.manual_gear_shift),
                'Gear:        %s' % {-1: 'R', 0: 'N'}.get(c.gear, c.gear)]
        elif isinstance(c, carla.WalkerControl):
            self._info_text += [
                ('Speed:', c.speed, 0.0, 5.556),
                ('Jump:', c.jump)]
        self._info_text += [
            '',
            'Collision:',
            collision,
            '',
            'Number of vehicles: % 8d' % len(vehicles)]
        if len(vehicles) > 1:
            self._info_text += ['Nearby vehicles:']
            distance = lambda l: math.sqrt(
                (l.x - t.location.x) ** 2 + (l.y - t.location.y) ** 2 + (l.z - t.location.z) ** 2)
            vehicles = [(distance(x.get_location()), x) for x in vehicles if x.id != world.player.id]
            for d, vehicle in sorted(vehicles, key=lambda vehicles: vehicles[0]):
                if d > 200.0:
                    break
                vehicle_type = get_actor_display_name(vehicle, truncate=22)
                self._info_text.append('% 4dm %s' % (d, vehicle_type))

    def toggle_info(self):
        self._show_info = not self._show_info

    def notification(self, text, seconds=2.0):
        self._notifications.set_text(text, seconds=seconds)

    def error(self, text):
        self._notifications.set_text('Error: %s' % text, (255, 0, 0))

    def render(self, display):
        if self._show_info:
            info_surface = pygame.Surface((220, self.dim[1]))
            info_surface.set_alpha(100)
            display.blit(info_surface, (0, 0))
            v_offset = 4
            bar_h_offset = 100
            bar_width = 106
            for item in self._info_text:
                if v_offset + 18 > self.dim[1]:
                    break
                if isinstance(item, list):
                    if len(item) > 1:
                        points = [(x + 8, v_offset + 8 + (1.0 - y) * 30) for x, y in enumerate(item)]
                        pygame.draw.lines(display, (255, 136, 0), False, points, 2)
                    item = None
                    v_offset += 18
                elif isinstance(item, tuple):
                    if isinstance(item[1], bool):
                        rect = pygame.Rect((bar_h_offset, v_offset + 8), (6, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect, 0 if item[1] else 1)
                    else:
                        rect_border = pygame.Rect((bar_h_offset, v_offset + 8), (bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect_border, 1)
                        f = (item[1] - item[2]) / (item[3] - item[2])
                        if item[2] < 0.0:
                            rect = pygame.Rect((bar_h_offset + f * (bar_width - 6), v_offset + 8), (6, 6))
                        else:
                            rect = pygame.Rect((bar_h_offset, v_offset + 8), (f * bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect)
                    item = item[0]
                if item:  # At this point has to be a str.
                    surface = self._font_mono.render(item, True, (255, 255, 255))
                    display.blit(surface, (8, v_offset))
                v_offset += 18
        self._notifications.render(display)
        # self.help.render(display)


# ==============================================================================
# -- FadingText ----------------------------------------------------------------
# ==============================================================================


class FadingText(object):
    def __init__(self, font, dim, pos):
        self.font = font
        self.dim = dim
        self.pos = pos
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)

    def set_text(self, text, color=(255, 255, 255), seconds=2.0):
        text_texture = self.font.render(text, True, color)
        self.surface = pygame.Surface(self.dim)
        self.seconds_left = seconds
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(text_texture, (10, 11))

    def tick(self, _, clock):
        delta_seconds = 1e-3 * clock.get_time()
        self.seconds_left = max(0.0, self.seconds_left - delta_seconds)
        self.surface.set_alpha(500.0 * self.seconds_left)

    def render(self, display):
        display.blit(self.surface, self.pos)


# ==============================================================================
# -- HelpText ------------------------------------------------------------------
# ==============================================================================


class HelpText(object):
    """Helper class to handle text output using pygame"""

    def __init__(self, font, width, height):
        lines = __doc__.split('\n')
        self.font = font
        self.line_space = 18
        self.dim = (780, len(lines) * self.line_space + 12)
        self.pos = (0.5 * width - 0.5 * self.dim[0], 0.5 * height - 0.5 * self.dim[1])
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)
        self.surface.fill((0, 0, 0, 0))
        for n, line in enumerate(lines):
            text_texture = self.font.render(line, True, (255, 255, 255))
            self.surface.blit(text_texture, (22, n * self.line_space))
            self._render = False
        self.surface.set_alpha(220)

    def toggle(self):
        self._render = not self._render

    def render(self, display):
        if self._render:
            display.blit(self.surface, self.pos)


# ==============================================================================
# -- CollisionSensor -----------------------------------------------------------
# ==============================================================================


class CollisionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self.history = []
        self._parent = parent_actor
        self.hud = hud
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.collision')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
        print('######################################################')
        print(self.sensor.get_transform())
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: CollisionSensor._on_collision(weak_self, event))

    def get_collision_history(self):
        history = collections.defaultdict(int)
        for frame, intensity in self.history:
            history[frame] += intensity
        return history

    @staticmethod
    def _on_collision(weak_self, event):
        self = weak_self()
        if not self:
            return
        actor_type = get_actor_display_name(event.other_actor)
        self.hud.notification('Collision with %r' % actor_type)
        impulse = event.normal_impulse
        intensity = math.sqrt(impulse.x ** 2 + impulse.y ** 2 + impulse.z ** 2)
        self.history.append((event.frame, intensity))
        if len(self.history) > 4000:
            self.history.pop(0)


# front  : x 2.4
# back   : x -2.7
# left   : y -1
# right  : y 1
# z      : 1.7
# FR     : yaw = -45
# R      : yaw = 0
# BR     : yaw = 45
# FL     : yaw = -135
# L      : yaw = 180
# BL     : yaw = 135


class FrontSensor(object):
    def __init__(self, t_world, parent_actor, hud):
        self.sensor = None
        self._history = []
        self._parent = parent_actor
        self._hud = hud
        self._world = t_world
        self.sensor_transform = carla.Transform(carla.Location(x=2.4, z=1.7),
                                                carla.Rotation(yaw=0))  # Put this sensor on the windshield of the car.
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.obstacle')
        bp.set_attribute('distance', '50')
        bp.set_attribute('hit_radius', '1')
        bp.set_attribute('only_dynamics', 'true')
        # bp.set_attribute('debug_linetrace', 'true')
        bp.set_attribute('sensor_tick', '0.5')
        self.sensor = world.spawn_actor(bp, self.sensor_transform, attach_to=self._parent)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: FrontSensor._on_LOS(weak_self, event))

    @staticmethod
    def _on_LOS(weak_self, event):
        self = weak_self()
        if not self:
            return
        if 'traffic' in event.other_actor.type_id or 'static' in event.other_actor.type_id:
            return

        if event.other_actor.type_id.startswith('vehicle.') or event.other_actor.type_id.startswith('walker.'):
            if event.distance <= 2:
                v = event.other_actor.get_velocity()
                a = event.other_actor.get_acceleration()
                if (self._world.is_turning_right or self._world.is_turning_left) and (3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)) < 1:
                    return
                # print('=========================================')
                # print(v)
                # print((3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)))
                # print(a)
                # print(3.6 * math.sqrt(a.x ** 2 + a.y ** 2 + a.z ** 2))

                # print('too close to obstacle!!!')
                # self._parent.set_autopilot(False)
                # self._parent.get_control().throttle = 0
                # self._parent.get_control().brake = min(self._parent.get_control().brake + 0.2, 1)
                self._world.emergency_stop = True

            # print(event.other_actor)
            ##print ("LOS with %s at distance %u" % (event.other_actor.type_id, event.distance))
            self._hud.notification('Front obstacle is %r' % event.other_actor.type_id)


class FrontRightSensor(object):
    def __init__(self, t_world, parent_actor, hud):
        self.sensor = None
        self._history = []
        self._parent = parent_actor
        self._hud = hud
        self._world = t_world
        self.sensor_transform = carla.Transform(carla.Location(x=2.4, y=1.0, z=1.7),
                                                carla.Rotation(yaw=45))  # Put this sensor on the windshield of the car.
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.obstacle')
        bp.set_attribute('distance', '50')
        bp.set_attribute('hit_radius', '1')
        bp.set_attribute('only_dynamics', 'true')
        # bp.set_attribute('debug_linetrace', 'true')
        bp.set_attribute('sensor_tick', '0.5')
        self.sensor = world.spawn_actor(bp, self.sensor_transform, attach_to=self._parent)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: FrontRightSensor._on_FRS(weak_self, event))

    @staticmethod
    def _on_FRS(weak_self, event):
        self = weak_self()
        if not self:
            return
        #
        if event.other_actor.type_id.startswith('vehicle.') or event.other_actor.type_id.startswith('walker.'):
            # if event.distance <= 20:
            #     #print('too close to obstacle!!!')
            #     self._parent.set_autopilot(False)
            #     #self._parent.get_control().throttle = 0
            #     #self._parent.get_control().brake = min(self._parent.get_control().brake + 0.2, 1)
            #     self._world.emergency_stop = True
            # ##print ("FRS with %s at distance %u" % (event.other_actor.type_id, event.distance))
            self._hud.notification('Front Right obstacle is %r' % event.other_actor.type_id)


class FrontLeftSensor(object):
    def __init__(self, t_world, parent_actor, hud):
        self.sensor = None
        self._history = []
        self._parent = parent_actor
        self._hud = hud
        self._world = t_world
        self.sensor_transform = carla.Transform(carla.Location(x=2.4, y=-1.0, z=1.7), carla.Rotation(
            yaw=-45))  # Put this sensor on the windshield of the car.
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.obstacle')
        bp.set_attribute('distance', '50')
        bp.set_attribute('hit_radius', '1')
        bp.set_attribute('only_dynamics', 'true')
        # bp.set_attribute('debug_linetrace', 'true')
        bp.set_attribute('sensor_tick', '0.5')
        self.sensor = world.spawn_actor(bp, self.sensor_transform, attach_to=self._parent)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: FrontLeftSensor._on_FLS(weak_self, event))

    @staticmethod
    def _on_FLS(weak_self, event):
        self = weak_self()
        if not self:
            return
        #
        if event.other_actor.type_id.startswith('vehicle.') or event.other_actor.type_id.startswith('walker.'):
            # if event.distance <= 20:
            #     #print('too close to obstacle!!!')
            #     self._parent.set_autopilot(False)
            #     #self._parent.get_control().throttle = 0
            #     #self._parent.get_control().brake = min(self._parent.get_control().brake + 0.2, 1)
            #     self._world.emergency_stop = True

            ##print ("FLS with %s at distance %u" % (event.other_actor.type_id, event.distance))
            self._hud.notification('Front Left obstacle is %r' % event.other_actor.type_id)


class RightSensor(object):
    def __init__(self, t_world, parent_actor, hud):
        self.sensor = None
        self._history = []
        self._parent = parent_actor
        self._hud = hud
        self._world = t_world
        self.sensor_transform = carla.Transform(carla.Location(x=0, y=1, z=1.7), carla.Rotation(yaw=90))
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.obstacle')
        bp.set_attribute('distance', '50')
        bp.set_attribute('hit_radius', '5')
        bp.set_attribute('only_dynamics', 'true')
        # bp.set_attribute('debug_linetrace', 'true')
        bp.set_attribute('sensor_tick', '0.5')
        self.sensor = world.spawn_actor(bp, self.sensor_transform, attach_to=self._parent)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: RightSensor._on_RS(weak_self, event))

    @staticmethod
    def _on_RS(weak_self, event):
        self = weak_self()
        if not self:
            return

        if event.other_actor.type_id.startswith('vehicle.') or event.other_actor.type_id.startswith('walker.'):
            # if event.distance <= 20:
            #     #print('too close to obstacle!!!')
            #     self._parent.set_autopilot(False)
            #     #self._parent.get_control().throttle = 0
            #     #self._parent.get_control().brake = min(self._parent.get_control().brake + 0.2, 1)
            #     self._world.emergency_stop = True
            # print ("Right with %s at distance %u" % (event.other_actor.type_id, event.distance))
            self._hud.notification('Right obstacle is %r' % event.other_actor.type_id)


class LeftSensor(object):
    def __init__(self, t_world, parent_actor, hud):
        self.sensor = None
        self._history = []
        self._parent = parent_actor
        self._hud = hud
        self._world = t_world
        self.sensor_transform = carla.Transform(carla.Location(x=0, y=-1, z=1.7), carla.Rotation(yaw=-90))
        self.other_actor_id = None
        self.before_distance = 0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.obstacle')
        bp.set_attribute('distance', '5')
        bp.set_attribute('hit_radius', '2')
        bp.set_attribute('only_dynamics', 'true')
        bp.set_attribute('debug_linetrace', 'true')
        bp.set_attribute('sensor_tick', '0.5')
        self.sensor = world.spawn_actor(bp, self.sensor_transform, attach_to=self._parent)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: LeftSensor._on_LS(weak_self, event))

    @staticmethod
    def _on_LS(weak_self, event):
        self = weak_self()
        if not self:
            return

        if not self._world.is_turning_right:
            return

        if event.other_actor.type_id.startswith('vehicle.'):
            v = event.other_actor.get_velocity()
            # print((3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)))

            if self.other_actor_id == None:
                self.other_actor_id = event.other_actor.id
            elif self.other_actor_id != event.other_actor.id:
                self.other_actor_id = event.other_actor.id
                self.before_distance = 0
            else:
                v = event.other_actor.get_velocity()
                if (3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)) < 5:
                    return

                distance = calculate_distance(self._parent.get_location(), event.other_actor.get_location())
                # print(distance)

                if distance <= self.before_distance:
                    self._world.emergency_stop = True
                else:
                    self.other_actor_id = None

                self.before_distance = distance

                # if event.other_actor
            # if event.distance <= 5:
            #
            #     print('too close to obstacle!!!')
            #
            #     self._world.emergency_stop = True
            # print ("Left with %s at distance %u" % (
            # event.other_actor.type_id, event.distance))
        self._hud.notification('Left obstacle is %r' % event.other_actor.type_id)


class BackSensor(object):
    def __init__(self, t_world, parent_actor, hud):
        self.sensor = None
        self._history = []
        self._parent = parent_actor
        self._hud = hud
        self._world = t_world
        self.sensor_transform = carla.Transform(carla.Location(x=-2.7, y=0, z=1.7), carla.Rotation(yaw=180))
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.obstacle')
        bp.set_attribute('distance', '5')
        bp.set_attribute('hit_radius', '2')
        bp.set_attribute('only_dynamics', 'true')
        # bp.set_attribute('debug_linetrace', 'true')
        bp.set_attribute('sensor_tick', '0.5')
        self.sensor = world.spawn_actor(bp, self.sensor_transform, attach_to=self._parent)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: BackSensor._on_BS(weak_self, event))

    @staticmethod
    def _on_BS(weak_self, event):
        self = weak_self()
        if not self:
            return

        if event.other_actor.type_id.startswith('vehicle.') or event.other_actor.type_id.startswith('walker.'):
            # if event.distance <= 20:
            #     #print('too close to obstacle!!!')
            #     self._parent.set_autopilot(False)
            #     #self._parent.get_control().throttle = 0
            #     #self._parent.get_control().brake = min(self._parent.get_control().brake + 0.2, 1)
            #     self._world.emergency_stop = True
            # print ("Back with %s at distance %u" % (
            # event.other_actor.type_id, event.distance))
            self._hud.notification('Back obstacle is %r' % event.other_actor.type_id)


class BackRightSensor(object):
    def __init__(self, t_world, parent_actor, hud):
        self.sensor = None
        self._history = []
        self._parent = parent_actor
        self._hud = hud
        self._world = t_world
        self.sensor_transform = carla.Transform(carla.Location(x=-2.7, y=1, z=1.7), carla.Rotation(yaw=135))
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.obstacle')
        bp.set_attribute('distance', '7')
        bp.set_attribute('hit_radius', '1')
        bp.set_attribute('only_dynamics', 'true')
        # bp.set_attribute('debug_linetrace', 'true')
        bp.set_attribute('sensor_tick', '0.5')
        self.sensor = world.spawn_actor(bp, self.sensor_transform, attach_to=self._parent)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: BackRightSensor._on_BRS(weak_self, event))

    @staticmethod
    def _on_BRS(weak_self, event):
        self = weak_self()
        if not self:
            return

        if event.other_actor.type_id.startswith('vehicle.') or event.other_actor.type_id.startswith('walker.'):
            # if event.distance <= 20:
            #     #print('too close to obstacle!!!')
            #     self._parent.set_autopilot(False)
            #     #self._parent.get_control().throttle = 0
            #     #self._parent.get_control().brake = min(self._parent.get_control().brake + 0.2, 1)
            #     self._world.emergency_stop = True
            # print ("BRS with %s at distance %u" % (event.other_actor.type_id, event.distance))
            self._hud.notification('Back Right obstacle is %r' % event.other_actor.type_id)


class BackLeftSensor(object):
    def __init__(self, t_world, parent_actor, hud):
        self.sensor = None
        self._history = []
        self._parent = parent_actor
        self._hud = hud
        self._world = t_world

        self.sensor_transform = carla.Transform(carla.Location(x=-2.7, y=-1, z=1.7), carla.Rotation(yaw=-135))
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.obstacle')
        bp.set_attribute('distance', '7')
        bp.set_attribute('hit_radius', '1')
        bp.set_attribute('only_dynamics', 'true')
        # bp.set_attribute('debug_linetrace', 'true')
        bp.set_attribute('sensor_tick', '0.5')
        self.sensor = world.spawn_actor(bp, self.sensor_transform, attach_to=self._parent)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: BackLeftSensor._on_BLS(weak_self, event))

    @staticmethod
    def _on_BLS(weak_self, event):
        self = weak_self()
        if not self:
            return

        if event.other_actor.type_id.startswith('vehicle.') or event.other_actor.type_id.startswith('walker.'):
            if event.distance < 5:
                v = event.other_actor.get_velocity()
                if (3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)) < 1:
                    return
            # if event.distance <= 20:
            #     #print('too close to obstacle!!!')
            #     self._parent.set_autopilot(False)
            #     #self._parent.get_control().throttle = 0
            #     #self._parent.get_control().brake = min(self._parent.get_control().brake + 0.2, 1)
            #     self._world.emergency_stop = True
            # print ("BLS with %s at distance %u" % (event.other_actor.type_id, event.distance))
                self._hud.notification('Back Left obstacle is %r' % event.other_actor.type_id)


class Checker(object):
    def __init__(self, parent_actor):
        self._parent = parent_actor
        self.sensor_transform = carla.Transform(carla.Location(x=0, y=1, z=1.7), carla.Rotation(yaw=0))
        world = self._parent.get_world()
        self.bp = world.get_blueprint_library().find('static.prop.bike helmet')
        print(self.bp)
        self.sensor = world.spawn_actor(self.bp, self.sensor_transform, attach_to=self._parent)

    def remove_checker(self):
        self.bp.destroy()


# ==============================================================================
# -- LaneInvasionSensor --------------------------------------------------------
# ==============================================================================


class LaneInvasionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self._parent = parent_actor
        self.hud = hud
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.lane_invasion')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: LaneInvasionSensor._on_invasion(weak_self, event))

    @staticmethod
    def _on_invasion(weak_self, event):
        self = weak_self()
        if not self:
            return
        lane_types = set(x.type for x in event.crossed_lane_markings)
        text = ['%r' % str(x).split()[-1] for x in lane_types]
        self.hud.notification('Crossed line %s' % ' and '.join(text))


# ==============================================================================
# -- GnssSensor ----------------------------------------------------------------
# ==============================================================================


class GnssSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.lat = 0.0
        self.lon = 0.0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.gnss')
        self.sensor = world.spawn_actor(bp, carla.Transform(carla.Location(x=1.0, z=2.8)), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: GnssSensor._on_gnss_event(weak_self, event))

    @staticmethod
    def _on_gnss_event(weak_self, event):
        self = weak_self()
        if not self:
            return
        self.lat = event.latitude
        self.lon = event.longitude


# ==============================================================================
# -- IMUSensor -----------------------------------------------------------------
# ==============================================================================


class IMUSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.accelerometer = (0.0, 0.0, 0.0)
        self.gyroscope = (0.0, 0.0, 0.0)
        self.compass = 0.0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.imu')
        self.sensor = world.spawn_actor(
            bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(
            lambda sensor_data: IMUSensor._IMU_callback(weak_self, sensor_data))

    @staticmethod
    def _IMU_callback(weak_self, sensor_data):
        self = weak_self()
        if not self:
            return
        limits = (-99.9, 99.9)
        self.accelerometer = (
            max(limits[0], min(limits[1], sensor_data.accelerometer.x)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.y)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.z)))
        self.gyroscope = (
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.x))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.y))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.z))))
        self.compass = math.degrees(sensor_data.compass)


# ==============================================================================
# -- RadarSensor ---------------------------------------------------------------
# ==============================================================================


class RadarSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.velocity_range = 7.5  # m/s
        world = self._parent.get_world()
        self.debug = world.debug
        bp = world.get_blueprint_library().find('sensor.other.radar')
        bp.set_attribute('horizontal_fov', str(35))
        bp.set_attribute('vertical_fov', str(20))
        self.sensor = world.spawn_actor(
            bp,
            carla.Transform(
                carla.Location(x=2.8, z=1.0),
                carla.Rotation(pitch=5)),
            attach_to=self._parent)
        # We need a weak reference to self to avoid circular reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(
            lambda radar_data: RadarSensor._Radar_callback(weak_self, radar_data))

    @staticmethod
    def _Radar_callback(weak_self, radar_data):
        self = weak_self()
        if not self:
            return
        # To get a numpy [[vel, altitude, azimuth, depth],...[,,,]]:
        # points = np.frombuffer(radar_data.raw_data, dtype=np.dtype('f4'))
        # points = np.reshape(points, (len(radar_data), 4))

        current_rot = radar_data.transform.rotation
        for detect in radar_data:
            azi = math.degrees(detect.azimuth)
            alt = math.degrees(detect.altitude)
            # The 0.25 adjusts a bit the distance so the dots can
            # be properly seen
            fw_vec = carla.Vector3D(x=detect.depth - 0.25)
            carla.Transform(
                carla.Location(),
                carla.Rotation(
                    pitch=current_rot.pitch + alt,
                    yaw=current_rot.yaw + azi,
                    roll=current_rot.roll)).transform(fw_vec)

            def clamp(min_v, max_v, value):
                return max(min_v, min(value, max_v))

            norm_velocity = detect.velocity / self.velocity_range  # range [-1, 1]
            r = int(clamp(0.0, 1.0, 1.0 - norm_velocity) * 255.0)
            g = int(clamp(0.0, 1.0, 1.0 - abs(norm_velocity)) * 255.0)
            b = int(abs(clamp(- 1.0, 0.0, - 1.0 - norm_velocity)) * 255.0)
            self.debug.draw_point(
                radar_data.transform.location + fw_vec,
                size=0.075,
                life_time=0.06,
                persistent_lines=False,
                color=carla.Color(r, g, b))


# ==============================================================================
# -- CameraManager -------------------------------------------------------------
# ==============================================================================


class CameraManager(object):
    def __init__(self, parent_actor, hud, gamma_correction):
        self.sensor = None
        self.surface = None
        self._parent = parent_actor
        self.hud = hud
        self.recording = False
        bound_y = 0.5 + self._parent.bounding_box.extent.y
        Attachment = carla.AttachmentType
        self._camera_transforms = [
            (carla.Transform(carla.Location(x=-10, z=5.5), carla.Rotation(pitch=-20.0)), Attachment.Rigid),
            (carla.Transform(carla.Location(x=1.6, z=1.7)), Attachment.Rigid),
            (carla.Transform(carla.Location(x=5.5, y=1.5, z=1.5)), Attachment.Rigid),
            (carla.Transform(carla.Location(x=-8.0, z=6.0), carla.Rotation(pitch=6.0)), Attachment.Rigid),
            (carla.Transform(carla.Location(x=-1, y=-bound_y, z=0.5)), Attachment.Rigid)]
        self.transform_index = 1
        self.sensors = [
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB', {}],
            ['sensor.camera.depth', cc.Raw, 'Camera Depth (Raw)', {}],
            ['sensor.camera.depth', cc.Depth, 'Camera Depth (Gray Scale)', {}],
            ['sensor.camera.depth', cc.LogarithmicDepth, 'Camera Depth (Logarithmic Gray Scale)', {}],
            ['sensor.camera.semantic_segmentation', cc.Raw, 'Camera Semantic Segmentation (Raw)', {}],
            ['sensor.camera.semantic_segmentation', cc.CityScapesPalette,
             'Camera Semantic Segmentation (CityScapes Palette)', {}],
            ['sensor.lidar.ray_cast', None, 'Lidar (Ray-Cast)', {'range': '50'}],
            ['sensor.camera.dvs', cc.Raw, 'Dynamic Vision Sensor', {}],
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB Distorted',
             {'lens_circle_multiplier': '3.0',
              'lens_circle_falloff': '3.0',
              'chromatic_aberration_intensity': '0.5',
              'chromatic_aberration_offset': '0'}]]
        world = self._parent.get_world()
        bp_library = world.get_blueprint_library()
        for item in self.sensors:
            bp = bp_library.find(item[0])
            if item[0].startswith('sensor.camera'):
                bp.set_attribute('image_size_x', str(hud.dim[0]))
                bp.set_attribute('image_size_y', str(hud.dim[1]))
                if bp.has_attribute('gamma'):
                    bp.set_attribute('gamma', str(gamma_correction))
                for attr_name, attr_value in item[3].items():
                    bp.set_attribute(attr_name, attr_value)
            elif item[0].startswith('sensor.lidar'):
                self.lidar_range = 50

                for attr_name, attr_value in item[3].items():
                    bp.set_attribute(attr_name, attr_value)
                    if attr_name == 'range':
                        self.lidar_range = float(attr_value)
                print(bp)

            item.append(bp)
        self.index = None

    def toggle_camera(self):
        self.transform_index = (self.transform_index + 1) % len(self._camera_transforms)
        self.set_sensor(self.index, notify=False, force_respawn=True)

    def set_sensor(self, index, notify=True, force_respawn=False):
        index = index % len(self.sensors)
        needs_respawn = True if self.index is None else \
            (force_respawn or (self.sensors[index][2] != self.sensors[self.index][2]))
        if needs_respawn:
            if self.sensor is not None:
                self.sensor.destroy()
                self.surface = None
            self.sensor = self._parent.get_world().spawn_actor(
                self.sensors[index][-1],
                self._camera_transforms[self.transform_index][0],
                attach_to=self._parent,
                attachment_type=self._camera_transforms[self.transform_index][1])
            # We need to pass the lambda a weak reference to self to avoid
            # circular reference.
            weak_self = weakref.ref(self)
            self.sensor.listen(lambda image: CameraManager._parse_image(weak_self, image))
        if notify:
            self.hud.notification(self.sensors[index][2])
        self.index = index

    def next_sensor(self):
        self.set_sensor(self.index + 1)

    def toggle_recording(self):
        self.recording = not self.recording
        self.hud.notification('Recording %s' % ('On' if self.recording else 'Off'))

    def render(self, display):
        if self.surface is not None:
            display.blit(self.surface, (0, 0))

    @staticmethod
    def _parse_image(weak_self, image):
        self = weak_self()
        if not self:
            return
        if self.sensors[self.index][0].startswith('sensor.lidar'):
            points = np.frombuffer(image.raw_data, dtype=np.dtype('f4'))
            points = np.reshape(points, (int(points.shape[0] / 4), 4))
            lidar_data = np.array(points[:, :2])
            lidar_data *= min(self.hud.dim) / (2.0 * self.lidar_range)
            lidar_data += (0.5 * self.hud.dim[0], 0.5 * self.hud.dim[1])
            lidar_data = np.fabs(lidar_data)  # pylint: disable=E1111
            lidar_data = lidar_data.astype(np.int32)
            lidar_data = np.reshape(lidar_data, (-1, 2))
            lidar_img_size = (self.hud.dim[0], self.hud.dim[1], 3)
            lidar_img = np.zeros((lidar_img_size), dtype=np.uint8)
            lidar_img[tuple(lidar_data.T)] = (155, 155, 5)
            self.surface = pygame.surfarray.make_surface(lidar_img)
        elif self.sensors[self.index][0].startswith('sensor.camera.dvs'):
            # Example of converting the raw_data from a carla.DVSEventArray
            # sensor into a NumPy array and using it as an image
            dvs_events = np.frombuffer(image.raw_data, dtype=np.dtype([
                ('x', np.uint16), ('y', np.uint16), ('t', np.int64), ('pol', np.bool)]))
            dvs_img = np.zeros((image.height, image.width, 3), dtype=np.uint8)
            # Blue is positive, red is negative
            dvs_img[dvs_events[:]['y'], dvs_events[:]['x'], dvs_events[:]['pol'] * 2] = 255
            self.surface = pygame.surfarray.make_surface(dvs_img.swapaxes(0, 1))
        else:
            image.convert(self.sensors[self.index][1])
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        if self.recording:
            image.save_to_disk('_out/%08d' % image.frame)


# ==============================================================================
# -- game_loop() ---------------------------------------------------------------
# ==============================================================================
def calculate_waypoints(start_location, end_location, world):
    # Connect to Carla server
    # client = carla.Client('localhost', 2000)
    # client.set_timeout(2.0)
    #
    # # Load the map
    # world = client.get_world()
    world_map = world.map

    # Find the closest waypoints to start and end locations
    start_waypoint = world_map.get_waypoint(start_location)
    end_waypoint = world_map.get_waypoint(end_location)

    # Calculate the route using A* algorithm
    route = world_map.get_random_route(start_waypoint.transform.location, 1000.0)

    # Extract waypoints from the route
    waypoints = [start_waypoint] + [world_map.get_waypoint(x[0].transform.location) for x in route]

    return waypoints




# Example usage

def game_loop(args):
    pygame.init()
    pygame.font.init()
    world = None

    before_time = time.time()
    reset_time = time.time()
    before_w = None
    current_w = None

    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(2.0)

        display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF)

        hud = HUD(args.width, args.height)
        world = World(client.get_world(), hud, args)
        debug = client.get_world().debug
        controller = KeyboardControl(world, False)

        clock = pygame.time.Clock()

        map = world.world.get_map()
        vehicle = world.player

        tm = client.get_trafficmanager(8000)
        # tm.vehicle_percentage_speed_difference(world.player, 85.0)
        tm.distance_to_leading_vehicle(world.player, 10)

        current_w = map.get_waypoint(vehicle.get_location())
        before_w = current_w
        current_w = map.get_waypoint(vehicle.get_location())

        world.agent = BasicAgent(vehicle, 20)
        destination = S1.location
        # world.agent.set_destination((120, 2, 2), True)
        world.agent.set_destination((
            T1.location.x, T1.location.y, T1.location.z
        ), True)

        while True:
            clock.tick_busy_loop(60)
            if controller.parse_events(client, world, clock):
                return
            world.tick(clock)
            world.render(display)
            T_index = 0


            if time.time() - reset_time > 3:
                world.emergency_stop = False
                reset_time = time.time()

            if vehicle.is_alive:
                # world.cast_ray(vehicle.get_location(), vehicle.get_location() + vehicle.get_location())

                # print('location :', vehicle.get_location())

                if controller._control.steer > 0.2:
                    world.hud.notification('Right Turning')
                    # print(time.time())
                    # print('Right Turning')
                    world.is_turning_right = True
                else:
                    world.is_turning_right = False

                if controller._control.steer < -0.2:
                    world.hud.notification('Left Turning')
                    world.is_turning_left = True
                else:
                    world.is_turning_left = False


                next_w = map.get_waypoint(vehicle.get_location(),
                                          lane_type=carla.LaneType.Driving | carla.LaneType.Shoulder | carla.LaneType.Sidewalk)



                if next_w.id != current_w.id:
                    # print('waypoint id', next_w.id)
                    vector = vehicle.get_velocity()

                    if time.time() - before_time >= 6:

                        if current_w.lane_type == carla.LaneType.Sidewalk:

                            draw_waypoint_union(debug, before_w, current_w, cyan if current_w.is_junction else red, 60)
                            # draw_waypoint_union(debug, current_w, next_w, red if current_w.is_junction else red, 60)

                        else:

                            draw_waypoint_union(debug, before_w, current_w, cyan if current_w.is_junction else green,
                                                60)
                            # draw_waypoint_union(debug, current_w, next_w, red if current_w.is_junction else red, 60)

                        # print(time.time())
                        # print(next_w.next(waypoint_separation))
                        debug.draw_string(current_w.transform.location, str('%15.0f km/h' % (
                                3.6 * math.sqrt(vector.x ** 2 + vector.y ** 2 + vector.z ** 2))), False, orange, 60)
                        draw_transform(debug, current_w.transform, white, 60)

                        before_time = time.time()
                        before_w = current_w

                # Update the current waypoint and sleep for some time
                current_w = next_w
            pygame.display.flip()


    finally:

        if (world and world.recording_enabled):
            client.stop_recorder()

        if world is not None:
            world.destroy()

        pygame.quit()


# def game_loop(args):
#     pygame.init()
#     pygame.font.init()
#     world = None
#
#     try:
#         client = carla.Client(args.host, args.port)
#         client.set_timeout(2.0)
#
#         display = pygame.display.set_mode(
#             (args.width, args.height),
#             pygame.HWSURFACE | pygame.DOUBLEBUF)
#
#         hud = HUD(args.width, args.height)
#         world = World(client.get_world(), hud, args)
#         controller = KeyboardControl(world, args.autopilot)
#
#         clock = pygame.time.Clock()
#         while True:
#             clock.tick_busy_loop(60)
#             if controller.parse_events(client, world, clock):
#                 return
#             world.tick(clock)
#             world.render(display)
#             pygame.display.flip()
#
#     finally:
#
#         if (world and world.recording_enabled):
#             client.stop_recorder()
#
#         if world is not None:
#             world.destroy()
#
#         pygame.quit()


# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================


def main():
    argparser = argparse.ArgumentParser(
        description='CARLA Manual Control Client')
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-a', '--autopilot',
        action='store_true',
        help='enable autopilot')
    argparser.add_argument(
        '--res',
        metavar='WIDTHxHEIGHT',
        default='1280x720',
        help='window resolution (default: 1280x720)')
    argparser.add_argument(
        '--filter',
        metavar='PATTERN',
        default='vehicle.*',
        help='actor filter (default: "vehicle.*")')
    argparser.add_argument(
        '--rolename',
        metavar='NAME',
        default='hero',
        help='actor role name (default: "hero")')
    argparser.add_argument(
        '--gamma',
        default=2.2,
        type=float,
        help='Gamma correction of the camera (default: 2.2)')
    argparser.add_argument(
        '-i', '--info',
        action='store_true',
        help='Show text information')
    args = argparser.parse_args()

    args.width, args.height = [int(x) for x in args.res.split('x')]

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)

    print(__doc__)

    try:

        game_loop(args)

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':
    main()
