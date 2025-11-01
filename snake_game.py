#!/usr/bin/env python3
"""
Enhanced Snake Game - A beautiful Snake game with scoring, high scores, power-ups, mini-games, and music
Controls: Arrow keys to move, R to reset, SPACE to start, ESC to quit, 1-4 for power-ups
"""

import pygame
import random
import sys
import json
import os
import math
from typing import List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime

# Initialize Pygame
pygame.init()

# Initialize mixer with error handling for environments without audio
try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except pygame.error:
    AUDIO_AVAILABLE = False
    print("Warning: Audio not available. Game will run without music.")

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 30  # Larger cells for better visibility and precision
GRID_WIDTH = 20  # Standard snake game width (20x20 grid)
GRID_HEIGHT = 20  # Standard snake game height
GAME_AREA_WIDTH = GRID_WIDTH * GRID_SIZE  # 600 pixels
GAME_AREA_HEIGHT = GRID_HEIGHT * GRID_SIZE  # 600 pixels (square game area)
SIDEBAR_WIDTH = WINDOW_WIDTH - GAME_AREA_WIDTH  # 200 pixels

# Colors - Enhanced modern palette
DARK_BG = (10, 10, 20)
DARKER_BG = (5, 5, 15)
GRID_COLOR = (25, 25, 35)
SNAKE_HEAD = (120, 255, 120)
SNAKE_BODY = (60, 220, 60)
FOOD_COLOR = (255, 90, 90)
SPECIAL_FOOD_COLOR = (255, 220, 0)
COIN_COLOR = (200, 150, 255)
POWERUP_COLOR = (100, 200, 255)
TEXT_PRIMARY = (255, 255, 255)
TEXT_SECONDARY = (180, 180, 180)
TEXT_HIGHLIGHT = (120, 255, 120)
ACCENT_COLOR = (120, 170, 255)
SHIELD_COLOR = (100, 200, 255)

# Power-up colors
TIME_SLOW_COLOR = (255, 200, 100)
ZOOM_COLOR = (200, 100, 255)
SPEED_BOOST_COLOR = (100, 255, 200)
SHIELD_COLOR_POWER = (150, 150, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Score file and music file
SCORE_FILE = "high_scores.json"
MUSIC_FILE = "Dreamin'.mp3"

# Game states
class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    MINI_GAME = "mini_game"


class PowerUpType(Enum):
    TIME_SLOW = "time_slow"
    ZOOM = "zoom"
    SPEED_BOOST = "speed_boost"
    SHIELD = "shield"


@dataclass
class ScoreEntry:
    score: int
    timestamp: str
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class Particle:
    """Particle effect for visual feedback"""
    
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 25
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(1, self.size - 0.3)
        self.vx *= 0.95
        self.vy *= 0.95
        
    def is_alive(self) -> bool:
        return self.life > 0
    
    def draw(self, screen):
        alpha = int(255 * (self.life / 25))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))


class PowerUp:
    """Power-up item"""
    
    def __init__(self, power_type: PowerUpType, position: Tuple[int, int], duration: int = 300):
        self.type = power_type
        self.position = position
        self.duration = duration
        self.timer = 0
        self.active = False
        self.animation_timer = 0
        
    def update(self):
        self.animation_timer += 1
        
    def draw(self, screen):
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE
        
        # Animated pulsing effect
        pulse = abs(math.sin(self.animation_timer * 0.2)) * 4 + 2
        
        color_map = {
            PowerUpType.TIME_SLOW: TIME_SLOW_COLOR,
            PowerUpType.ZOOM: ZOOM_COLOR,
            PowerUpType.SPEED_BOOST: SPEED_BOOST_COLOR,
            PowerUpType.SHIELD: SHIELD_COLOR_POWER
        }
        
        color = color_map.get(self.type, POWERUP_COLOR)
        
        # Draw power-up icon
        center_x = x + GRID_SIZE // 2
        center_y = y + GRID_SIZE // 2
        
        # Draw glowing circle
        for i in range(3):
            alpha = 100 - i * 30
            radius = GRID_SIZE // 2 + int(pulse) - i * 2
            pygame.draw.circle(screen, color, (center_x, center_y), radius)
        
        # Draw icon based on type
        if self.type == PowerUpType.TIME_SLOW:
            # Clock icon
            pygame.draw.circle(screen, TEXT_PRIMARY, (center_x, center_y), 4)
        elif self.type == PowerUpType.ZOOM:
            # Eye icon
            pygame.draw.circle(screen, TEXT_PRIMARY, (center_x, center_y), 5, 2)
        elif self.type == PowerUpType.SPEED_BOOST:
            # Lightning bolt
            points = [(center_x, center_y - 5), (center_x + 3, center_y), (center_x, center_y), (center_x - 3, center_y + 5)]
            pygame.draw.polygon(screen, TEXT_PRIMARY, points)
        elif self.type == PowerUpType.SHIELD:
            # Shield icon
            pygame.draw.circle(screen, TEXT_PRIMARY, (center_x, center_y), 5, 2)


class Coin:
    """Coin that triggers mini-games"""
    
    def __init__(self, position: Tuple[int, int]):
        self.position = position
        self.animation_timer = 0
        self.collected = False
        
    def update(self):
        self.animation_timer += 1
        
    def draw(self, screen):
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE
        
        # Rotating coin effect
        rotation = self.animation_timer * 0.3
        pulse = abs(math.sin(self.animation_timer * 0.25)) * 3
        
        center_x = x + GRID_SIZE // 2
        center_y = y + GRID_SIZE // 2
        
        # Draw coin with glow
        radius = GRID_SIZE // 2 + int(pulse)
        pygame.draw.circle(screen, COIN_COLOR, (center_x, center_y), radius)
        pygame.draw.circle(screen, (255, 220, 100), (center_x, center_y), radius - 2)
        
        # Draw $ symbol
        coin_text = pygame.font.Font(None, 20).render("$", True, DARK_BG)
        coin_rect = coin_text.get_rect(center=(center_x, center_y))
        screen.blit(coin_text, coin_rect)


class MiniGame:
    """Mini-game system"""
    
    def __init__(self, game_type: str = "speed_challenge"):
        self.type = game_type
        self.active = False
        self.timer = 0
        self.duration = 180  # 3 seconds at 60 FPS
        self.score = 0
        self.target_score = 50
        
    def start(self):
        self.active = True
        self.timer = 0
        self.score = 0
        
    def update(self) -> bool:
        """Returns True if mini-game is still active"""
        if not self.active:
            return False
            
        self.timer += 1
        if self.timer >= self.duration:
            self.active = False
            return False
        return True
    
    def draw(self, screen, game):
        if not self.active:
            return
            
        # Draw mini-game overlay
        overlay = pygame.Surface((GAME_AREA_WIDTH, GAME_AREA_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 50))
        screen.blit(overlay, (0, 0))
        
        # Mini-game instructions
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 32)
        
        title = font_large.render("MINI-GAME!", True, TEXT_HIGHLIGHT)
        title_rect = title.get_rect(center=(GAME_AREA_WIDTH // 2, GAME_AREA_HEIGHT // 2 - 100))
        screen.blit(title, title_rect)
        
        instruction = font_medium.render("Collect food quickly! +50 bonus!", True, TEXT_PRIMARY)
        inst_rect = instruction.get_rect(center=(GAME_AREA_WIDTH // 2, GAME_AREA_HEIGHT // 2 - 40))
        screen.blit(instruction, inst_rect)
        
        time_left = self.duration - self.timer
        timer_text = font_medium.render(f"Time: {time_left // 60:.1f}s", True, ACCENT_COLOR)
        timer_rect = timer_text.get_rect(center=(GAME_AREA_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 20))
        screen.blit(timer_text, timer_rect)


class Snake:
    """Snake class to handle snake movement and growth"""
    
    def __init__(self, start_pos: Tuple[int, int]):
        self.body: List[Tuple[int, int]] = [start_pos]
        self.direction = RIGHT
        self.grow = False
        
    def move(self) -> bool:
        """Move the snake and check for collisions"""
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            return False
        
        # Check self collision
        if new_head in self.body:
            return False
        
        self.body.insert(0, new_head)
        
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
            
        return True
    
    def change_direction(self, new_direction: Tuple[int, int]):
        """Change snake direction if valid"""
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
    
    def eat_food(self):
        """Mark snake to grow on next move"""
        self.grow = True
    
    def get_head(self) -> Tuple[int, int]:
        """Get the head position"""
        return self.body[0]


class Food:
    """Food class to handle food placement"""
    
    def __init__(self):
        self.position = self.generate_position()
        self.is_special = False
        self.special_timer = 0
        
    def generate_position(self) -> Tuple[int, int]:
        """Generate a random food position"""
        return (random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1))
    
    def respawn(self, snake_body: List[Tuple[int, int]], make_special: bool = False):
        """Respawn food at a new location not on snake"""
        while True:
            self.position = self.generate_position()
            if self.position not in snake_body:
                break
        self.is_special = make_special or random.random() < 0.15
        self.special_timer = 0
    
    def update(self):
        """Update food animation"""
        if self.is_special:
            self.special_timer += 1


class ScoreManager:
    """Manages high scores persistence"""
    
    def __init__(self, filename: str = SCORE_FILE):
        self.filename = filename
        self.scores: List[ScoreEntry] = []
        self.load_scores()
    
    def load_scores(self):
        """Load scores from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.scores = [ScoreEntry.from_dict(entry) for entry in data]
                    self.scores.sort(key=lambda x: x.score, reverse=True)
            except:
                self.scores = []
        else:
            self.scores = []
    
    def save_scores(self):
        """Save scores to file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump([s.to_dict() for s in self.scores], f, indent=2)
        except Exception as e:
            print(f"Error saving scores: {e}")
    
    def add_score(self, score: int) -> bool:
        """Add a new score and return True if it's a new high score"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = ScoreEntry(score=score, timestamp=timestamp)
        
        self.scores.append(new_entry)
        self.scores.sort(key=lambda x: x.score, reverse=True)
        self.scores = self.scores[:10]
        self.save_scores()
        
        return len(self.scores) > 0 and self.scores[0].score == score
    
    def get_high_score(self) -> int:
        """Get the current high score"""
        return self.scores[0].score if self.scores else 0
    
    def get_latest_score(self) -> Optional[int]:
        """Get the latest score"""
        return self.scores[-1].score if self.scores else None


class Game:
    """Main game class"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - Ultimate Edition")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        # Initialize music
        self.music_loaded = False
        self.load_music()
        
        self.score_manager = ScoreManager()
        self.state = GameState.MENU
        self.particles: List[Particle] = []
        self.base_speed = 3  # Much slower for better control
        self.current_speed = self.base_speed
        
        # Power-up system
        self.active_powerups: dict = {}  # Currently active power-ups
        self.collected_powerups: dict = {}  # Power-ups collected but not yet activated
        self.powerups: List[PowerUp] = []  # Power-ups on the field
        self.powerup_spawn_timer = 0
        self.powerup_spawn_interval = 600  # Spawn every 10 seconds
        
        # Coin system
        self.coins: List[Coin] = []
        self.coin_spawn_timer = 0
        self.coin_spawn_interval = 900  # Spawn every 15 seconds
        
        # Mini-game system
        self.mini_game = MiniGame()
        self.mini_game_triggered = False
        
        # Zoom effect
        self.zoom_level = 1.0
        self.target_zoom = 1.0
        
        # Time slow effect
        self.time_slow_factor = 1.0
        
        self.reset_game()
    
    def load_music(self):
        """Load and play background music"""
        if not AUDIO_AVAILABLE:
            self.music_loaded = False
            print("Audio not available - game will run without music")
            return
            
        try:
            music_path = MUSIC_FILE
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)  # Loop forever
                self.music_loaded = True
                print(f"Music loaded successfully: {music_path}")
            else:
                print(f"Music file '{MUSIC_FILE}' not found in current directory.")
                print(f"Current directory: {os.getcwd()}")
                print(f"Game will run without music.")
                self.music_loaded = False
        except Exception as e:
            print(f"Error loading music: {e}")
            self.music_loaded = False
    
    def reset_game(self):
        """Reset the game to initial state"""
        start_pos = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.snake = Snake(start_pos)
        self.food = Food()
        self.food.respawn(self.snake.body)
        self.score = 0
        self.game_over = False
        self.running = True
        self.particles.clear()
        self.current_speed = self.base_speed
        self.new_high_score = False
        self.previous_high_score = self.score_manager.get_high_score()
        self.active_powerups.clear()
        self.collected_powerups.clear()
        self.powerups.clear()
        self.powerup_spawn_timer = 0
        self.coins.clear()
        self.coin_spawn_timer = 0
        self.mini_game.active = False
        self.mini_game_triggered = False
        self.zoom_level = 1.0
        self.target_zoom = 1.0
        self.time_slow_factor = 1.0
    
    def update_title(self):
        """Update the window title with current score"""
        pygame.display.set_caption(
            f"Snake Game - Score: {self.score} | High: {self.score_manager.get_high_score()} | ESC to Quit"
        )
    
    def activate_powerup(self, power_type: PowerUpType):
        """Activate a power-up"""
        duration = 300  # 5 seconds at 60 FPS
        
        if power_type == PowerUpType.TIME_SLOW:
            self.time_slow_factor = 0.5  # Slow down FPS by 50% (makes everything slower)
            self.active_powerups[PowerUpType.TIME_SLOW] = duration
            print("Time Slow activated! Movement slowed down.")
        elif power_type == PowerUpType.ZOOM:
            self.target_zoom = 1.3  # Zoom in slightly
            self.active_powerups[PowerUpType.ZOOM] = duration
            print("Zoom activated!")  # Debug
        elif power_type == PowerUpType.SPEED_BOOST:
            self.current_speed = min(self.current_speed + 2, 8)  # Less aggressive boost, max 8
            self.active_powerups[PowerUpType.SPEED_BOOST] = duration
            print("Speed Boost activated!")  # Debug
        elif power_type == PowerUpType.SHIELD:
            self.active_powerups[PowerUpType.SHIELD] = duration
            print("Shield activated!")  # Debug
    
    def update_powerups(self):
        """Update active power-ups"""
        for power_type in list(self.active_powerups.keys()):
            self.active_powerups[power_type] -= 1
            if self.active_powerups[power_type] <= 0:
                # Deactivate power-up
                if power_type == PowerUpType.TIME_SLOW:
                    self.time_slow_factor = 1.0
                elif power_type == PowerUpType.ZOOM:
                    self.target_zoom = 1.0
                elif power_type == PowerUpType.SPEED_BOOST:
                    # Reset speed gradually
                    self.current_speed = max(self.base_speed, self.current_speed - 2)
                del self.active_powerups[power_type]
        
        # Smooth zoom transition
        self.zoom_level += (self.target_zoom - self.zoom_level) * 0.1
    
    def handle_events(self):
        """Handle keyboard and window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.MENU:
                        self.running = False
                    else:
                        self.state = GameState.MENU
                        self.reset_game()
                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.MENU:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.GAME_OVER:
                        self.state = GameState.MENU
                        self.reset_game()
                elif event.key == pygame.K_r:
                    if self.state == GameState.PLAYING:
                        self.reset_game()
                    elif self.state == GameState.GAME_OVER:
                        self.state = GameState.PLAYING
                        self.reset_game()
                elif self.state == GameState.PLAYING and not self.game_over:
                    # Power-up keys - activate if collected
                    if event.key == pygame.K_1 and PowerUpType.TIME_SLOW in self.collected_powerups:
                        self.activate_powerup(PowerUpType.TIME_SLOW)
                        del self.collected_powerups[PowerUpType.TIME_SLOW]
                    elif event.key == pygame.K_2 and PowerUpType.ZOOM in self.collected_powerups:
                        self.activate_powerup(PowerUpType.ZOOM)
                        del self.collected_powerups[PowerUpType.ZOOM]
                    elif event.key == pygame.K_3 and PowerUpType.SPEED_BOOST in self.collected_powerups:
                        self.activate_powerup(PowerUpType.SPEED_BOOST)
                        del self.collected_powerups[PowerUpType.SPEED_BOOST]
                    elif event.key == pygame.K_4 and PowerUpType.SHIELD in self.collected_powerups:
                        self.activate_powerup(PowerUpType.SHIELD)
                        del self.collected_powerups[PowerUpType.SHIELD]
                    # Movement
                    elif event.key == pygame.K_UP:
                        self.snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(RIGHT)
    
    def update(self):
        """Update game state"""
        if self.state == GameState.PLAYING and not self.game_over:
            # Update power-ups
            self.update_powerups()
            
            # Spawn power-ups
            self.powerup_spawn_timer += 1
            if self.powerup_spawn_timer >= self.powerup_spawn_interval and len(self.powerups) < 2:
                self.powerup_spawn_timer = 0
                power_type = random.choice(list(PowerUpType))
                pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                # Don't spawn on snake, food, coins, or existing power-ups
                valid_pos = True
                if pos in self.snake.body or pos == self.food.position:
                    valid_pos = False
                for coin in self.coins:
                    if pos == coin.position:
                        valid_pos = False
                        break
                for pu in self.powerups:
                    if pos == pu.position:
                        valid_pos = False
                        break
                if valid_pos:
                    self.powerups.append(PowerUp(power_type, pos))
                    print(f"Power-up spawned: {power_type.value} at {pos}")
            
            # Update and check power-up collection
            for powerup in self.powerups[:]:
                powerup.update()
                if self.snake.get_head() == powerup.position:
                    # Collect power-up
                    self.powerups.remove(powerup)
                    self.collected_powerups[powerup.type] = True
                    print(f"Power-up collected: {powerup.type.value} - Press {['1','2','3','4'][[PowerUpType.TIME_SLOW, PowerUpType.ZOOM, PowerUpType.SPEED_BOOST, PowerUpType.SHIELD].index(powerup.type)]} to activate!")
                    # Particle effect
                    pu_x = powerup.position[0] * GRID_SIZE + GRID_SIZE // 2
                    pu_y = powerup.position[1] * GRID_SIZE + GRID_SIZE // 2
                    color_map = {
                        PowerUpType.TIME_SLOW: TIME_SLOW_COLOR,
                        PowerUpType.ZOOM: ZOOM_COLOR,
                        PowerUpType.SPEED_BOOST: SPEED_BOOST_COLOR,
                        PowerUpType.SHIELD: SHIELD_COLOR_POWER
                    }
                    color = color_map.get(powerup.type, POWERUP_COLOR)
                    for _ in range(15):
                        self.particles.append(Particle(pu_x, pu_y, color))
            
            # Spawn coins
            self.coin_spawn_timer += 1
            if self.coin_spawn_timer >= self.coin_spawn_interval:
                self.coin_spawn_timer = 0
                pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                if pos not in self.snake.body and pos != self.food.position:
                    self.coins.append(Coin(pos))
            
            # Update coins
            for coin in self.coins[:]:
                coin.update()
                if self.snake.get_head() == coin.position:
                    self.coins.remove(coin)
                    # Trigger mini-game
                    self.mini_game.start()
                    self.mini_game_triggered = True
            
            # Update mini-game
            if self.mini_game.update():
                # Mini-game is active
                pass
            
            # Move snake (FPS controls speed now)
            if not self.snake.move():
                # Check if shield is active
                if PowerUpType.SHIELD not in self.active_powerups:
                    self.game_over = True
                    self.state = GameState.GAME_OVER
                    if self.score > 0:
                        self.new_high_score = self.score_manager.add_score(self.score)
            
            # Check if snake ate food
            if self.snake.get_head() == self.food.position:
                self.snake.eat_food()
                
                points = 25 if self.food.is_special else 10
                
                # Bonus points during mini-game
                if self.mini_game.active:
                    points *= 2
                    self.mini_game.score += points
                
                self.score += points
                
                # Create particles
                food_x = self.food.position[0] * GRID_SIZE + GRID_SIZE // 2
                food_y = self.food.position[1] * GRID_SIZE + GRID_SIZE // 2
                color = SPECIAL_FOOD_COLOR if self.food.is_special else FOOD_COLOR
                for _ in range(12):
                    self.particles.append(Particle(food_x, food_y, color))
                
                # Increase speed gradually (less aggressive)
                if self.score % 50 == 0:
                    self.current_speed = min(self.base_speed + (self.score // 50), 6)  # Max speed capped at 6
                
                self.update_title()
                self.food.respawn(self.snake.body)
            
            # Check mini-game completion
            if self.mini_game_triggered and not self.mini_game.active:
                if self.mini_game.score >= self.mini_game.target_score:
                    self.score += 50  # Bonus!
                    self.mini_game_triggered = False
        
        # Update particles
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
        
        # Update food animation
        if self.state == GameState.PLAYING:
            self.food.update()
    
    def draw_gradient_background(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]):
        """Draw a gradient background"""
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))
    
    def draw_rounded_rect(self, surface, color, rect, radius):
        """Draw a rounded rectangle"""
        x, y, w, h = rect
        pygame.draw.rect(surface, color, (x + radius, y, w - 2*radius, h))
        pygame.draw.rect(surface, color, (x, y + radius, w, h - 2*radius))
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)
    
    def draw_grid(self):
        """Draw a subtle grid background"""
        for x in range(0, GAME_AREA_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, GAME_AREA_WIDTH), 1)
        for y in range(0, GAME_AREA_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (GAME_AREA_WIDTH, y), 1)
    
    def draw_game(self):
        """Draw the game screen"""
        # Draw game area background with animated gradient
        bg_offset = int(pygame.time.get_ticks() * 0.01) % 100
        for y in range(0, GAME_AREA_WIDTH, 5):
            ratio = ((y + bg_offset) % 200) / 200
            color = (
                int(DARK_BG[0] + ratio * 5),
                int(DARK_BG[1] + ratio * 5),
                int(DARK_BG[2] + ratio * 10)
            )
            pygame.draw.rect(self.screen, color, (0, y, GAME_AREA_WIDTH, 5))
        
        self.draw_grid()
        
        # Draw food with enhanced effects
        food_x = self.food.position[0] * GRID_SIZE
        food_y = self.food.position[1] * GRID_SIZE
        food_color = SPECIAL_FOOD_COLOR if self.food.is_special else FOOD_COLOR
        
        if self.food.is_special:
            pulse = abs(math.sin(self.food.special_timer * 0.3)) * 4
            glow_radius = GRID_SIZE // 2 + int(pulse)
            # Multiple glow layers
            for i in range(3):
                alpha_radius = glow_radius + i * 2
                pygame.draw.circle(
                    self.screen, food_color,
                    (food_x + GRID_SIZE // 2, food_y + GRID_SIZE // 2),
                    alpha_radius
                )
        else:
            food_rect = pygame.Rect(food_x + 2, food_y + 2, GRID_SIZE - 4, GRID_SIZE - 4)
            self.draw_rounded_rect(self.screen, food_color, food_rect, 4)
            pygame.draw.rect(self.screen, DARKER_BG, food_rect, 2)
        
        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)
        
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # Draw snake with enhanced visuals
        for i, segment in enumerate(self.snake.body):
            segment_x = segment[0] * GRID_SIZE
            segment_y = segment[1] * GRID_SIZE
            
            # Gradient effect on body
            if i == 0:
                color = SNAKE_HEAD
            else:
                # Fade from head to tail
                fade = max(0.5, 1.0 - (i / len(self.snake.body)) * 0.5)
                color = (
                    int(SNAKE_BODY[0] * fade),
                    int(SNAKE_BODY[1] * fade),
                    int(SNAKE_BODY[2] * fade)
                )
            
            self.draw_rounded_rect(
                self.screen, color,
                (segment_x + 1, segment_y + 1, GRID_SIZE - 2, GRID_SIZE - 2),
                4
            )
            
            # Head highlight
            if i == 0:
                pygame.draw.circle(
                    self.screen, TEXT_HIGHLIGHT,
                    (segment_x + GRID_SIZE // 2, segment_y + GRID_SIZE // 2),
                    4
                )
                # Eyes
                eye_offset = 3
                if self.snake.direction == RIGHT:
                    pygame.draw.circle(self.screen, DARK_BG, (segment_x + GRID_SIZE - 6, segment_y + 6), 2)
                    pygame.draw.circle(self.screen, DARK_BG, (segment_x + GRID_SIZE - 6, segment_y + GRID_SIZE - 6), 2)
                elif self.snake.direction == LEFT:
                    pygame.draw.circle(self.screen, DARK_BG, (segment_x + 6, segment_y + 6), 2)
                    pygame.draw.circle(self.screen, DARK_BG, (segment_x + 6, segment_y + GRID_SIZE - 6), 2)
                elif self.snake.direction == UP:
                    pygame.draw.circle(self.screen, DARK_BG, (segment_x + 6, segment_y + 6), 2)
                    pygame.draw.circle(self.screen, DARK_BG, (segment_x + GRID_SIZE - 6, segment_y + 6), 2)
                elif self.snake.direction == DOWN:
                    pygame.draw.circle(self.screen, DARK_BG, (segment_x + 6, segment_y + GRID_SIZE - 6), 2)
                    pygame.draw.circle(self.screen, DARK_BG, (segment_x + GRID_SIZE - 6, segment_y + GRID_SIZE - 6), 2)
        
        # Draw shield effect
        if PowerUpType.SHIELD in self.active_powerups:
            head = self.snake.get_head()
            shield_x = head[0] * GRID_SIZE + GRID_SIZE // 2
            shield_y = head[1] * GRID_SIZE + GRID_SIZE // 2
            shield_radius = GRID_SIZE + int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 5)
            pygame.draw.circle(self.screen, SHIELD_COLOR, (shield_x, shield_y), shield_radius, 2)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw sidebar with enhanced design
        sidebar_x = GAME_AREA_WIDTH
        # Gradient sidebar
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            color = (
                int(DARKER_BG[0] + ratio * 3),
                int(DARKER_BG[1] + ratio * 3),
                int(DARKER_BG[2] + ratio * 5)
            )
            pygame.draw.line(self.screen, color, (sidebar_x, y), (WINDOW_WIDTH, y))
        
        # Divider line
        pygame.draw.line(self.screen, GRID_COLOR, (sidebar_x, 0), (sidebar_x, WINDOW_HEIGHT), 2)
        
        # Draw score with glow effect
        y_offset = 30
        score_text = self.font_medium.render("Score", True, TEXT_PRIMARY)
        self.screen.blit(score_text, (sidebar_x + 20, y_offset))
        
        score_value = self.font_large.render(f"{self.score}", True, TEXT_HIGHLIGHT)
        self.screen.blit(score_value, (sidebar_x + 20, y_offset + 35))
        
        # High score
        y_offset += 110
        high_score_text = self.font_medium.render("High Score", True, TEXT_PRIMARY)
        self.screen.blit(high_score_text, (sidebar_x + 20, y_offset))
        
        high_score_value = self.font_large.render(
            f"{self.score_manager.get_high_score()}", True, ACCENT_COLOR
        )
        self.screen.blit(high_score_value, (sidebar_x + 20, y_offset + 35))
        
        # Speed indicator
        y_offset += 110
        speed_text = self.font_small.render("Speed", True, TEXT_SECONDARY)
        self.screen.blit(speed_text, (sidebar_x + 20, y_offset))
        
        speed_bar_width = 100
        speed_bar_height = 12
        speed_fill = int((self.current_speed - self.base_speed) / 12 * speed_bar_width)
        pygame.draw.rect(
            self.screen, GRID_COLOR,
            (sidebar_x + 20, y_offset + 25, speed_bar_width, speed_bar_height), 2
        )
        if speed_fill > 0:
            pygame.draw.rect(
                self.screen, ACCENT_COLOR,
                (sidebar_x + 20, y_offset + 25, speed_fill, speed_bar_height)
            )
        
        # Active power-ups
        y_offset += 80
        powerup_text = self.font_small.render("Power-Ups", True, TEXT_PRIMARY)
        self.screen.blit(powerup_text, (sidebar_x + 20, y_offset))
        
        y_offset += 30
        powerup_keys = ["1", "2", "3", "4"]
        powerup_names = ["Slow Time", "Zoom", "Speed", "Shield"]
        powerup_types = [PowerUpType.TIME_SLOW, PowerUpType.ZOOM, PowerUpType.SPEED_BOOST, PowerUpType.SHIELD]
        for i, (key, name, pu_type) in enumerate(zip(powerup_keys, powerup_names, powerup_types)):
            color = TEXT_SECONDARY
            if pu_type in self.active_powerups:
                # Active power-up (currently in use)
                if i == 0:
                    color = TIME_SLOW_COLOR
                elif i == 1:
                    color = ZOOM_COLOR
                elif i == 2:
                    color = SPEED_BOOST_COLOR
                elif i == 3:
                    color = SHIELD_COLOR_POWER
                # Show timer
                timer = self.active_powerups[pu_type] // 60
                name = f"{name} ({timer}s)"
            elif pu_type in self.collected_powerups:
                # Collected but not activated
                color = TEXT_HIGHLIGHT
            
            pu_text = self.font_tiny.render(f"{key}: {name}", True, color)
            self.screen.blit(pu_text, (sidebar_x + 20, y_offset + i * 20))
        
        # Controls
        y_offset = WINDOW_HEIGHT - 120
        controls = [
            "Controls:",
            "Arrow Keys: Move",
            "R: Reset",
            "ESC: Menu"
        ]
        for i, control in enumerate(controls):
            color = TEXT_PRIMARY if i == 0 else TEXT_SECONDARY
            font = self.font_small if i == 0 else self.font_tiny
            self.screen.blit(font.render(control, True, color), (sidebar_x + 20, y_offset + i * 20))
        
        # Draw mini-game overlay
        if self.mini_game.active:
            self.mini_game.draw(self.screen, self)
        
        # Draw game over overlay
        if self.game_over:
            overlay = pygame.Surface((GAME_AREA_WIDTH, GAME_AREA_HEIGHT))
            overlay.set_alpha(220)
            overlay.fill((20, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font_large.render("GAME OVER!", True, FOOD_COLOR)
            game_over_rect = game_over_text.get_rect(
                center=(GAME_AREA_WIDTH // 2, GAME_AREA_HEIGHT // 2 - 80)
            )
            self.screen.blit(game_over_text, game_over_rect)
            
            final_score_text = self.font_medium.render(
                f"Final Score: {self.score}", True, TEXT_PRIMARY
            )
            final_score_rect = final_score_text.get_rect(
                center=(GAME_AREA_WIDTH // 2, GAME_AREA_HEIGHT // 2 - 20)
            )
            self.screen.blit(final_score_text, final_score_rect)
            
            if self.new_high_score:
                new_high_text = self.font_medium.render(
                    "NEW HIGH SCORE!", True, TEXT_HIGHLIGHT
                )
                new_high_rect = new_high_text.get_rect(
                    center=(GAME_AREA_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 20)
                )
                self.screen.blit(new_high_text, new_high_rect)
            
            restart_text = self.font_small.render(
                "Press SPACE for Menu | R to Restart", True, TEXT_SECONDARY
            )
            restart_rect = restart_text.get_rect(
                center=(GAME_AREA_WIDTH // 2, GAME_AREA_HEIGHT // 2 + 80)
            )
            self.screen.blit(restart_text, restart_rect)
    
    def draw_menu(self):
        """Draw the start menu with enhanced design"""
        # Animated gradient background
        offset = int(pygame.time.get_ticks() * 0.02) % 400
        for y in range(WINDOW_HEIGHT):
            ratio = ((y + offset) % 400) / 400
            color1 = DARK_BG
            color2 = DARKER_BG
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))
        
        # Title with glow effect
        glow_offset = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 5
        title_text = self.font_large.render("SNAKE GAME", True, TEXT_HIGHLIGHT)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100 + glow_offset))
        
        # Draw glow
        for i in range(3):
            glow_surf = self.font_large.render("SNAKE GAME", True, (
                TEXT_HIGHLIGHT[0] // (i + 1),
                TEXT_HIGHLIGHT[1] // (i + 1),
                TEXT_HIGHLIGHT[2] // (i + 1)
            ))
            glow_rect = glow_surf.get_rect(center=(WINDOW_WIDTH // 2 + i, 100 + glow_offset + i))
            self.screen.blit(glow_surf, glow_rect)
        
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.font_small.render("Ultimate Edition", True, TEXT_SECONDARY)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # High scores section
        y_start = 220
        scores_title = self.font_medium.render("HIGH SCORES", True, TEXT_PRIMARY)
        scores_title_rect = scores_title.get_rect(center=(WINDOW_WIDTH // 2, y_start))
        self.screen.blit(scores_title, scores_title_rect)
        
        # Draw top 5 scores with enhanced styling
        y_offset = y_start + 50
        for i, score_entry in enumerate(self.score_manager.scores[:5]):
            score_text = f"{i+1}. {score_entry.score}"
            date_text = score_entry.timestamp.split()[0]
            
            color = TEXT_HIGHLIGHT if i == 0 else TEXT_PRIMARY
            score_surface = self.font_small.render(score_text, True, color)
            date_surface = self.font_tiny.render(date_text, True, TEXT_SECONDARY)
            
            score_rect = score_surface.get_rect(center=(WINDOW_WIDTH // 2 - 60, y_offset))
            date_rect = date_surface.get_rect(center=(WINDOW_WIDTH // 2 + 60, y_offset))
            
            self.screen.blit(score_surface, score_rect)
            self.screen.blit(date_surface, date_rect)
            
            y_offset += 35
        
        # Latest score
        latest_score = self.score_manager.get_latest_score()
        if latest_score is not None:
            y_offset += 20
            latest_label = self.font_tiny.render("Latest Score:", True, TEXT_SECONDARY)
            latest_label_rect = latest_label.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(latest_label, latest_label_rect)
            
            latest_value = self.font_small.render(f"{latest_score}", True, ACCENT_COLOR)
            latest_value_rect = latest_value.get_rect(center=(WINDOW_WIDTH // 2, y_offset + 20))
            self.screen.blit(latest_value, latest_value_rect)
        
        # Instructions
        y_offset = WINDOW_HEIGHT - 150
        instructions = [
            "Press SPACE to Start",
            "Collect coins for mini-games!",
            "Use power-ups: 1-4 keys",
            "ESC to Quit"
        ]
        for i, instruction in enumerate(instructions):
            inst_text = self.font_small.render(instruction, True, TEXT_SECONDARY)
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, y_offset + i * 28))
            self.screen.blit(inst_text, inst_rect)
    
    def draw(self):
        """Draw all game elements"""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
            # Adjust FPS based on speed
            # Time slow reduces overall FPS to make everything slower
            if self.state == GameState.PLAYING:
                fps = self.current_speed  # Base FPS
                # Apply time slow factor - lower factor = slower (lower FPS)
                if self.time_slow_factor < 1.0:
                    fps = int(fps * self.time_slow_factor)
            else:
                fps = 60  # Menu runs at 60 FPS
            fps = max(15, fps)  # Minimum FPS (reduced for slower gameplay)
            self.clock.tick(fps)
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
