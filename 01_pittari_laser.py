import pyxel
import math
import random

PLAYER_X = 60
PLAYER_Y = 80
CIRCLE_RADIUS = 5
LASER_SPEED = 7
MAX_REFLECTIONS = 9

TARGET_RADIUS = 4
TARGET_COLOR_NORMAL = 7
TARGET_COLOR_HIT = 8

NUM_TARGETS_MIN = 1
NUM_TARGETS_MAX = 1

BOUNDARY_X_MIN = 10
BOUNDARY_X_MAX = 110
BOUNDARY_Y_MIN = 10
BOUNDARY_Y_MAX = 110

class Laser:
    def __init__(self, x, y, angle):
        self.positions = [(x, y)]  # Track positions for afterimage
        self.angle = angle
        self.dx = math.cos(angle) * LASER_SPEED
        self.dy = math.sin(angle) * LASER_SPEED
        self.reflections = 0
        self.is_active = True

    def update(self):
        if not self.is_active:
            return

        new_x = self.positions[-1][0] + self.dx
        new_y = self.positions[-1][1] + self.dy

        # Reflect off boundaries
        if new_x <= BOUNDARY_X_MIN or new_x >= BOUNDARY_X_MAX:
            self.dx *= -1
            self.reflections += 1
            new_x = max(BOUNDARY_X_MIN, min(new_x, BOUNDARY_X_MAX))
        if new_y <= BOUNDARY_Y_MIN or new_y >= BOUNDARY_Y_MAX:
            self.dy *= -1
            self.reflections += 1
            new_y = max(BOUNDARY_Y_MIN, min(new_y, BOUNDARY_Y_MAX))

        # Update position
        self.positions.append((new_x, new_y))

        if self.reflections > MAX_REFLECTIONS:
            self.is_active = False

    def draw(self):
        for pos in self.positions[-10:]:  # Draw last 10 positions as afterimage
            pyxel.pset(int(pos[0]), int(pos[1]), 10)

class Target:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = TARGET_COLOR_NORMAL
        self.hit_reflections = None

    def check_hit(self, laser):
        if (
            laser.positions[-1][0] >= self.x - TARGET_RADIUS - 1
            and laser.positions[-1][0] <= self.x + TARGET_RADIUS + 1
            and laser.positions[-1][1] >= self.y - TARGET_RADIUS - 1
            and laser.positions[-1][1] <= self.y + TARGET_RADIUS + 1
        ):
            self.color = TARGET_COLOR_HIT
            if self.hit_reflections is None:
                self.hit_reflections = laser.reflections  # Record reflections at hit
            laser.is_active = False  # End laser activity immediately

    def is_hit(self):
        return self.color == TARGET_COLOR_HIT

    def draw(self):
        pyxel.circ(self.x, self.y, TARGET_RADIUS, self.color)

class Game:
    def __init__(self):
        pyxel.init(120, 160, title="Click Laser Game")
        self.reset_game()
        self.show_title_screen = True
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.score = 0
        self.round_count = 0
        self.circle_speed = 5
        self.targets = []
        self.laser = None
        self.is_game_over = False
        self.display_player = True
        self.spawn_targets()
        self.circle_angle = 0

    def spawn_targets(self):
        self.targets = [
            Target(
                random.randint(BOUNDARY_X_MIN + TARGET_RADIUS, BOUNDARY_X_MAX - TARGET_RADIUS),
                random.randint(BOUNDARY_Y_MIN + TARGET_RADIUS, BOUNDARY_Y_MAX - TARGET_RADIUS),
            )
            for _ in range(random.randint(NUM_TARGETS_MIN, NUM_TARGETS_MAX))
        ]

    def update(self):
        
        if self.show_title_screen:
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                self.show_title_screen = False
            return

        if self.is_game_over:
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                self.reset_game()
            return

        if self.display_player:
            self.circle_angle = (self.circle_angle + self.circle_speed) % 360

        if  (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)) or (pyxel.btnp(pyxel.KEY_SPACE)) and self.laser is None:
            angle = math.radians(self.circle_angle)
            self.laser = Laser(
                PLAYER_X + math.cos(angle) * CIRCLE_RADIUS,
                PLAYER_Y + math.sin(angle) * CIRCLE_RADIUS,
                angle,
            )
            self.display_player = False

        if self.laser:
            self.laser.update()
            for target in self.targets:
                target.check_hit(self.laser)

            if not self.laser.is_active:
                if all(target.is_hit() for target in self.targets):
                    # Add hit reflections to score for each target
                    for target in self.targets:
                        if target.hit_reflections is not None:
                            self.score += target.hit_reflections + 1

                    self.round_count += 1
                    if self.round_count % 3 == 0:
                        self.circle_speed += 1
                    self.spawn_targets()
                else:
                    self.is_game_over = True

                self.laser = None
                self.display_player = True

    def draw(self):
        pyxel.cls(0)
        
        if self.show_title_screen:
            pyxel.text(35, 60, "PITTARI LASER", 8)
            pyxel.text(23, 100, "PRESS SPACE TO START", (pyxel.frame_count)//4 % 16)
            return
        
        if self.is_game_over:
            pyxel.text(40, 70, "GAME OVER", 8)
            pyxel.text(30, 90, "PRESS TO RESTART", 7)
            pyxel.text(40, 110, f"SCORE: {self.score}", 7)
            return

        pyxel.rectb(
            BOUNDARY_X_MIN, BOUNDARY_Y_MIN, BOUNDARY_X_MAX - BOUNDARY_X_MIN, BOUNDARY_Y_MAX - BOUNDARY_Y_MIN, 13
        )

        if self.display_player:
            pyxel.circ(PLAYER_X, PLAYER_Y, 3, 3)
            circle_x = PLAYER_X + math.cos(math.radians(self.circle_angle)) * CIRCLE_RADIUS
            circle_y = PLAYER_Y + math.sin(math.radians(self.circle_angle)) * CIRCLE_RADIUS
            pyxel.circ(circle_x, circle_y, 1, 10)

        if self.laser:
            self.laser.draw()

        for target in self.targets:
            target.draw()

        pyxel.text(5, 3, f"SCORE: {self.score}", 7)
        pyxel.rect(0, pyxel.height - 20, pyxel.width, 20, 6)
        pyxel.text(pyxel.width // 2 - 23, pyxel.height - 15, "PRESS SPACE", 7)

Game()
