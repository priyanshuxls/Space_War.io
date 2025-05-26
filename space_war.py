import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space War - 3D UFO Edition")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Create a starfield background
def create_starfield_background():
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(BLACK)
    
    # Add some nebula-like clouds for depth
    for _ in range(5):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        radius = random.randint(50, 150)
        color_value = random.randint(20, 60)
        color = (color_value//2, color_value//3, color_value)
        
        # Create a surface for the nebula with alpha
        nebula_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        for i in range(20):
            alpha = 150 - i * 7
            if alpha <= 0:
                break
            pygame.draw.circle(nebula_surf, (*color, alpha), 
                              (radius, radius), radius - i*2)
        
        background.blit(nebula_surf, (x-radius, y-radius), special_flags=pygame.BLEND_ADD)
    
    return background

# Player ship
class PlayerShip:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.width = 50
        self.height = 30
        self.speed = 5
        self.health = 100
        self.cooldown = 0
        self.cooldown_max = 15
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.glow_size = 0
        self.glow_direction = 1

    def draw(self):
        # UFO body - main saucer (3D effect with multiple ellipses)
        # Bottom shadow (darker)
        pygame.draw.ellipse(screen, (0, 100, 0), (self.x - 25, self.y + 5, 50, 15))
        
        # Middle section (main body)
        pygame.draw.ellipse(screen, GREEN, (self.x - 25, self.y, 50, 15))
        
        # Top dome (3D effect)
        pygame.draw.ellipse(screen, (100, 255, 100), (self.x - 15, self.y - 10, 30, 20))
        
        # Cockpit window
        pygame.draw.ellipse(screen, (150, 255, 255), (self.x - 10, self.y - 5, 20, 10))
        
        # Animated glow underneath (pulsing)
        self.glow_size += 0.1 * self.glow_direction
        if self.glow_size > 3 or self.glow_size < 0:
            self.glow_direction *= -1
            
        glow_radius = 5 + self.glow_size
        pygame.draw.circle(screen, (100, 255, 200), (self.x - 10, self.y + 10), glow_radius)
        pygame.draw.circle(screen, (100, 255, 200), (self.x + 10, self.y + 10), glow_radius)
        
        # Draw health bar
        pygame.draw.rect(screen, RED, (self.x - 25, self.y + 25, 50, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 25, self.y + 25, 50 * (self.health / 100), 5))

    def move(self, direction):
        if direction == "left" and self.x > 20:
            self.x -= self.speed
        if direction == "right" and self.x < WIDTH - 20:
            self.x += self.speed

    def shoot(self):
        if self.cooldown <= 0:
            self.cooldown = self.cooldown_max
            return Bullet(self.x, self.y - 20, -10, True)
        return None

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

# AI ship
class AIShip:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = 50
        self.width = 50
        self.height = 30
        self.speed = 3
        self.health = 100
        self.cooldown = 0
        self.cooldown_max = 30
        self.direction = random.choice([-1, 1])
        self.decision_timer = 0
        self.hover_offset = 0
        self.hover_direction = 1
        self.rotation = 0

    def draw(self):
        # Alien UFO with 3D effect
        # Hovering animation
        self.hover_offset += 0.05 * self.hover_direction
        if abs(self.hover_offset) > 2:
            self.hover_direction *= -1
            
        # Rotation effect for the saucer
        self.rotation = (self.rotation + 2) % 360
        
        # Bottom saucer (main body)
        pygame.draw.ellipse(screen, (150, 0, 0), (self.x - 25, self.y + self.hover_offset, 50, 15))
        
        # Top dome
        pygame.draw.ellipse(screen, RED, (self.x - 15, self.y - 10 + self.hover_offset, 30, 20))
        
        # Alien cockpit (darker center)
        pygame.draw.ellipse(screen, (50, 0, 0), (self.x - 10, self.y - 5 + self.hover_offset, 20, 10))
        
        # Rotating lights (3 lights that appear to rotate)
        for i in range(3):
            angle = self.rotation + (i * 120)
            light_x = self.x + 15 * math.cos(math.radians(angle))
            light_y = self.y + 5 * math.sin(math.radians(angle)) + self.hover_offset
            pygame.draw.circle(screen, (255, 200, 0), (int(light_x), int(light_y)), 3)
        
        # Draw health bar
        pygame.draw.rect(screen, RED, (self.x - 25, self.y - 25 + self.hover_offset, 50, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 25, self.y - 25 + self.hover_offset, 50 * (self.health / 100), 5))

    def update(self, player_x):
        # AI decision making
        if self.decision_timer <= 0:
            # Randomly decide to change direction or follow player
            if random.random() < 0.3:
                self.direction = random.choice([-1, 1])
            else:
                # Follow player with some randomness
                self.direction = 1 if player_x > self.x else -1
                if random.random() < 0.2:  # Sometimes do the opposite to be unpredictable
                    self.direction *= -1
            
            self.decision_timer = random.randint(20, 60)
        else:
            self.decision_timer -= 1
        
        # Move
        self.x += self.speed * self.direction
        
        # Boundary check
        if self.x < 30:
            self.x = 30
            self.direction = 1
        elif self.x > WIDTH - 30:
            self.x = WIDTH - 30
            self.direction = -1
            
        # Cooldown for shooting
        if self.cooldown > 0:
            self.cooldown -= 1

    def shoot(self):
        if self.cooldown <= 0 and random.random() < 0.05:  # Random chance to shoot
            self.cooldown = self.cooldown_max
            return Bullet(self.x, self.y + 20, 8, False)
        return None

# Bullet class
class Bullet:
    def __init__(self, x, y, speed, is_player=True):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = 5
        self.active = True
        self.is_player = is_player
        self.trail = []
        self.max_trail = 5
        self.glow_size = random.randint(5, 10)
        self.color = (0, 255, 200) if is_player else (255, 100, 0)

    def update(self):
        # Add current position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
            
        # Move bullet
        self.y += self.speed
        
        # Check if bullet is off screen
        if self.y < 0 or self.y > HEIGHT:
            self.active = False

    def draw(self):
        # Draw trail (3D effect)
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            trail_color = (min(self.color[0], alpha), 
                          min(self.color[1], alpha), 
                          min(self.color[2], alpha))
            trail_radius = self.radius * (i / len(self.trail))
            pygame.draw.circle(screen, trail_color, (int(trail_x), int(trail_y)), int(trail_radius))
        
        # Draw bullet with glow effect
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius)
        
        # Outer glow
        glow_surf = pygame.Surface((self.glow_size*2, self.glow_size*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, 100), (self.glow_size, self.glow_size), self.glow_size)
        screen.blit(glow_surf, (self.x - self.glow_size, self.y - self.glow_size), special_flags=pygame.BLEND_ADD)

# Explosion effect
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.active = True
        self.particles = []
        self.create_particles()
        self.alpha = 255
        
    def create_particles(self):
        # Create 3D particle explosion
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            size = random.uniform(2, 6)
            color = (random.randint(200, 255), 
                    random.randint(100, 200), 
                    random.randint(0, 50))
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'color': color,
                'alpha': 255
            })

    def update(self):
        self.radius += 2
        self.alpha -= 10
        
        # Update particles
        for p in self.particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['alpha'] -= random.randint(5, 15)
            p['size'] *= 0.95
        
        # Remove faded particles
        self.particles = [p for p in self.particles if p['alpha'] > 0 and p['size'] > 0.5]
        
        if self.radius >= self.max_radius and not self.particles:
            self.active = False

    def draw(self):
        # Draw expanding ring
        if self.alpha > 0:
            ring_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (255, 165, 0, self.alpha), 
                              (self.radius, self.radius), self.radius, 2)
            screen.blit(ring_surf, (self.x - self.radius, self.y - self.radius))
        
        # Draw particles
        for p in self.particles:
            particle_surf = pygame.Surface((int(p['size']*2), int(p['size']*2)), pygame.SRCALPHA)
            color_with_alpha = (*p['color'], p['alpha'])
            pygame.draw.circle(particle_surf, color_with_alpha, 
                              (int(p['size']), int(p['size'])), int(p['size']))
            screen.blit(particle_surf, (p['x'] - p['size'], p['y'] - p['size']))

# Star background
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(0.5, 3)
        self.speed = self.size * 0.8  # Larger stars move faster (parallax effect)
        self.brightness = random.randint(150, 255)
        self.twinkle_speed = random.uniform(0.02, 0.1)
        self.twinkle_offset = random.uniform(0, math.pi * 2)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
            
        # Twinkle effect
        self.twinkle_offset += self.twinkle_speed
        self.brightness = 150 + int(50 * math.sin(self.twinkle_offset))

    def draw(self):
        # Draw star with glow effect for larger stars
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))
        
        # Add glow to larger stars
        if self.size > 2:
            glow_size = int(self.size * 3)
            glow_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
            glow_color = (*color, 50)  # Semi-transparent
            pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), glow_size)
            screen.blit(glow_surf, (int(self.x - glow_size), int(self.y - glow_size)), 
                       special_flags=pygame.BLEND_ADD)

# Game state
class GameState:
    def __init__(self):
        self.player = PlayerShip()
        self.ai = AIShip()
        self.player_bullets = []
        self.ai_bullets = []
        self.explosions = []
        self.stars = [Star() for _ in range(100)]
        self.game_over = False
        self.winner = None
        self.font = pygame.font.SysFont(None, 36)
        self.background = create_starfield_background()
        self.shake_amount = 0
        self.camera_offset_x = 0
        self.camera_offset_y = 0

    def update(self):
        if self.game_over:
            return

        # Update player
        self.player.update()
        
        # Update AI
        self.ai.update(self.player.x)
        
        # AI shooting
        ai_bullet = self.ai.shoot()
        if ai_bullet:
            self.ai_bullets.append(ai_bullet)
        
        # Update bullets
        for bullet in self.player_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.player_bullets.remove(bullet)
            elif self.check_collision(bullet, self.ai):
                self.ai.health -= 10
                self.explosions.append(Explosion(bullet.x, bullet.y))
                self.player_bullets.remove(bullet)
                self.shake_amount = 5  # Add screen shake
                if self.ai.health <= 0:
                    self.game_over = True
                    self.winner = "Player"
                    self.explosions.append(Explosion(self.ai.x, self.ai.y))
                    self.shake_amount = 10  # More intense shake
        
        for bullet in self.ai_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.ai_bullets.remove(bullet)
            elif self.check_collision(bullet, self.player):
                self.player.health -= 10
                self.explosions.append(Explosion(bullet.x, bullet.y))
                self.ai_bullets.remove(bullet)
                self.shake_amount = 5  # Add screen shake
                if self.player.health <= 0:
                    self.game_over = True
                    self.winner = "AI"
                    self.explosions.append(Explosion(self.player.x, self.player.y))
                    self.shake_amount = 10  # More intense shake
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if not explosion.active:
                self.explosions.remove(explosion)
        
        # Update stars
        for star in self.stars:
            star.update()
            
        # Update camera shake
        if self.shake_amount > 0:
            self.camera_offset_x = random.randint(-int(self.shake_amount), int(self.shake_amount))
            self.camera_offset_y = random.randint(-int(self.shake_amount), int(self.shake_amount))
            self.shake_amount -= 0.5
        else:
            self.camera_offset_x = 0
            self.camera_offset_y = 0

    def check_collision(self, bullet, ship):
        # Simple circle-rectangle collision
        dx = abs(bullet.x - ship.x)
        dy = abs(bullet.y - ship.y)
        
        if dx > ship.width // 2 + bullet.radius:
            return False
        if dy > ship.height // 2 + bullet.radius:
            return False
            
        return True

    def draw(self):
        # Draw background
        screen.blit(self.background, (0, 0))
        
        # Apply camera shake
        shake_surface = pygame.Surface((WIDTH, HEIGHT))
        shake_surface.blit(screen, (-self.camera_offset_x, -self.camera_offset_y))
        screen.blit(shake_surface, (0, 0))
        
        # Draw stars
        for star in self.stars:
            star.draw()
        
        # Draw ships
        self.player.draw()
        self.ai.draw()
        
        # Draw bullets
        for bullet in self.player_bullets:
            bullet.draw()
        for bullet in self.ai_bullets:
            bullet.draw()
        
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw()
        
        # Draw game over message
        if self.game_over:
            text = self.font.render(f"Game Over! {self.winner} wins!", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(text, text_rect)
            
            restart_text = self.font.render("Press R to restart or Q to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            screen.blit(restart_text, restart_rect)

# Main game function
def main():
    clock = pygame.time.Clock()
    game = GameState()
    running = True
    
    # Create a surface for post-processing effects
    post_process = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r and game.game_over:
                    game = GameState()
                elif event.key == pygame.K_SPACE and not game.game_over:
                    bullet = game.player.shoot()
                    if bullet:
                        game.player_bullets.append(bullet)
        
        # Movement controls
        if not game.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                game.player.move("left")
            if keys[pygame.K_RIGHT]:
                game.player.move("right")
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw()
        
        # Add post-processing effects
        post_process.fill((0, 0, 0, 0))  # Clear with transparent
        
        # Add simple glow effect for explosions
        if len(game.explosions) > 0 or game.shake_amount > 0:
            # Create a simple glow effect without gaussian blur
            for explosion in game.explosions:
                glow_radius = explosion.radius * 2
                glow_surf = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 165, 0, 100), 
                                  (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surf, (explosion.x - glow_radius, explosion.y - glow_radius), 
                           special_flags=pygame.BLEND_ADD)
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
