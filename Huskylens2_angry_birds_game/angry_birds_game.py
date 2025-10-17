import pygame
import math
import random

class Bird:
    def __init__(self, x, y):
        self.start_x = x  # Initial X
        self.start_y = y  # Initial Y
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 15
        self.color = (255, 0, 0)
        self.trail = []  # Trajectory points
        self.is_launched = False
        self.is_aiming = False  # Whether currently aiming
        self.gravity = 0.3
        
        # Try to load bird sprite
        self.image = None
        self.use_image = False
        try:
            # Attempt to load bird sprite file
            self.image = pygame.image.load("bird.png")
            self.image = pygame.transform.scale(self.image, (self.radius * 3, self.radius * 3))
            self.use_image = True
            print("✅ Loaded bird image: bird.png")
        except pygame.error as e:
            print(f"⚠️ Failed to load bird.png: {e}")
            print("💡 Hint: Place bird.png in the project directory")
            # Fallback to vector drawing when image is unavailable
            self.use_image = False
        
    def launch(self, power, angle):
        """Launch the bird"""
        # Launch from current aiming position
        self.vx = power * math.cos(angle) * 0.3
        self.vy = power * math.sin(angle) * 0.3
        self.is_launched = True
        self.is_aiming = False
        self.trail = []
    
    def set_aiming_position(self, power, angle):
        """Set bird position while aiming"""
        self.is_aiming = True
        # Place bird along sling vector based on power and angle
        pull_distance = min(power * 0.8, 80)  # Max pull distance 80 px
        self.x = self.start_x - pull_distance * math.cos(angle)
        self.y = self.start_y - pull_distance * math.sin(angle)
    
    def reset_position(self):
        """Reset to initial position"""
        self.is_aiming = False
        self.x = self.start_x
        self.y = self.start_y
        
    def update(self):
        """Update bird physics and position"""
        if self.is_launched:
            # Append trajectory point
            self.trail.append((self.x, self.y))
            if len(self.trail) > 20:
                self.trail.pop(0)
            
            # Integrate motion
            self.x += self.vx
            self.y += self.vy
            self.vy += self.gravity  # Gravity
            
            # Ground collision
            if self.y > 550:
                self.y = 550
                self.vy *= -0.3  # Bounce
                self.vx *= 0.8   # Friction
                
    def draw(self, screen):
        """Draw the bird"""
        # Enhanced trail rendering
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                current_pos = self.trail[i]
                next_pos = self.trail[i + 1]
                
                # Trail alpha and size gradient
                alpha = int((i / len(self.trail)) * 255)
                trail_size = max(1, int(self.radius * (i / len(self.trail)) * 0.8))
                
                # Trail color gradient (red→yellow→transparent)
                if i < len(self.trail) * 0.3:
                    color = (255, int(200 * (i / len(self.trail) * 3)), 0, alpha)
                elif i < len(self.trail) * 0.7:
                    color = (255, 255, int(100 * ((i - len(self.trail) * 0.3) / (len(self.trail) * 0.4))), alpha)
                else:
                    color = (int(255 * ((len(self.trail) - i) / (len(self.trail) * 0.3))), 100, 100, alpha)
                
                # Streamlined trail segments
                if i < len(self.trail) - 1:
                    trail_surface = pygame.Surface((trail_size * 4, trail_size * 4), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surface, color, (trail_size * 2, trail_size * 2), trail_size)
                    
                    # Outer glow
                    glow_surface = pygame.Surface((trail_size * 6, trail_size * 6), pygame.SRCALPHA)
                    glow_color = (*color[:3], alpha // 3)
                    pygame.draw.circle(glow_surface, glow_color, (trail_size * 3, trail_size * 3), trail_size * 2)
                    
                    screen.blit(glow_surface, (int(current_pos[0] - trail_size * 3), int(current_pos[1] - trail_size * 3)))
                    screen.blit(trail_surface, (int(current_pos[0] - trail_size * 2), int(current_pos[1] - trail_size * 2)))
        
        # Flight effects
        if self.is_launched and abs(self.vx) > 1:
            # Airflow streaks
            for i in range(3):
                wind_start_x = self.x - (20 + i * 10)
                wind_end_x = wind_start_x - 15
                wind_y = self.y + (i - 1) * 5
                
                wind_surface = pygame.Surface((25, 3), pygame.SRCALPHA)
                wind_alpha = 150 - i * 40
                pygame.draw.line(wind_surface, (200, 200, 255, wind_alpha), (0, 1), (25, 1), 2)
                screen.blit(wind_surface, (wind_start_x, wind_y))
        
        # Bird body
        if self.use_image and self.image:
            # Draw using sprite
            bird_rect = self.image.get_rect()
            bird_rect.center = (int(self.x), int(self.y))
            
            # Blit sprite
            screen.blit(self.image, bird_rect)
            
            # Aiming halo
            if self.is_aiming:
                for i in range(3):
                    ring_radius = self.radius + 5 + i * 3
                    ring_alpha = 100 - i * 30
                    ring_surface = pygame.Surface((ring_radius * 4, ring_radius * 4), pygame.SRCALPHA)
                    pygame.draw.circle(ring_surface, (255, 255, 0, ring_alpha), 
                                     (ring_radius * 2, ring_radius * 2), ring_radius, 2)
                    screen.blit(ring_surface, (int(self.x - ring_radius * 2), int(self.y - ring_radius * 2)))
        else:
            # Vector fallback rendering
            self.draw_detailed_bird(screen)
    
    def draw_detailed_bird(self, screen):
        """Draw a detailed bird (Angry Birds style)"""
        x, y = int(self.x), int(self.y)
        
        # Main circular body
        main_color = (220, 20, 20)  # Red
        pygame.draw.circle(screen, main_color, (x, y), self.radius)
        
        # Gradient highlight on top
        highlight_color = (255, 100, 100)
        for i in range(8):
            alpha = 255 - i * 30
            if alpha > 0:
                color = (min(255, highlight_color[0]), 
                        min(255, highlight_color[1]), 
                        min(255, highlight_color[2]))
                pygame.draw.circle(screen, color, (x, y - 3), self.radius - i)
        
        # Belly (light ellipse)
        belly_width = self.radius + 2
        belly_height = self.radius - 2
        belly_rect = pygame.Rect(x - belly_width//2, y - belly_height//2 + 2, 
                               belly_width, belly_height)
        pygame.draw.ellipse(screen, (255, 180, 180), belly_rect)
        
        # Beak with depth
        beak_base = (x + self.radius - 2, y + 2)
        beak_tip = (x + self.radius + 12, y + 2)
        beak_top = (x + self.radius + 8, y - 4)
        beak_bottom = (x + self.radius + 8, y + 8)
        
        # Beak polygons
        beak_points = [beak_base, beak_tip, beak_top]
        pygame.draw.polygon(screen, (255, 200, 0), beak_points)
        beak_points = [beak_base, beak_tip, beak_bottom]
        pygame.draw.polygon(screen, (255, 165, 0), beak_points)
        
        # Beak highlight
        pygame.draw.line(screen, (255, 255, 200), 
                        (beak_base[0] + 2, beak_base[1] - 1), 
                        (beak_tip[0] - 2, beak_tip[1] - 1), 2)
        
        # Eyes
        eye_size = 7
        eye_x = x - 2
        eye_y = y - 6
        
        # Sclera
        pygame.draw.circle(screen, (255, 255, 255), (eye_x, eye_y), eye_size)
        # Eye outline
        pygame.draw.circle(screen, (200, 200, 200), (eye_x, eye_y), eye_size, 1)
        
        # Pupil
        pupil_x = eye_x + 2
        pupil_y = eye_y + 1
        pygame.draw.circle(screen, (0, 0, 0), (pupil_x, pupil_y), 4)
        
        # Pupil highlights
        pygame.draw.circle(screen, (255, 255, 255), (pupil_x + 1, pupil_y - 1), 2)
        pygame.draw.circle(screen, (255, 255, 255), (pupil_x - 1, pupil_y - 2), 1)
        
        # Eyebrows
        eyebrow_color = (100, 50, 0)
        pygame.draw.line(screen, eyebrow_color, (x - 8, y - 12), (x + 6, y - 16), 4)
        # Eyebrow highlight
        pygame.draw.line(screen, (150, 80, 20), (x - 7, y - 13), (x + 5, y - 17), 2)
        
        # Crest feathers
        crest_points = [(x - 3, y - self.radius + 2), 
                       (x - 8, y - self.radius - 5),
                       (x, y - self.radius - 8),
                       (x + 8, y - self.radius - 5),
                       (x + 3, y - self.radius + 2)]
        pygame.draw.polygon(screen, (180, 15, 15), crest_points)
        # Feather highlight
        pygame.draw.polygon(screen, (220, 50, 50), 
                          [(x - 1, y - self.radius + 2), 
                           (x - 4, y - self.radius - 3),
                           (x + 2, y - self.radius - 6),
                           (x + 4, y - self.radius - 3),
                           (x + 1, y - self.radius + 2)])
        
        # Tail feathers
        tail_points = [(x - self.radius + 2, y + 2), 
                      (x - self.radius - 8, y - 6),
                      (x - self.radius - 12, y),
                      (x - self.radius - 8, y + 6)]
        pygame.draw.polygon(screen, (150, 10, 10), tail_points)
        # Tail highlight
        pygame.draw.polygon(screen, (200, 40, 40), 
                          [(x - self.radius + 2, y + 1), 
                           (x - self.radius - 6, y - 4),
                           (x - self.radius - 9, y),
                           (x - self.radius - 6, y + 4)])
        
        # Tail feather detail
        tail_points = [(x - self.radius, y), (x - self.radius - 6, y - 5), (x - self.radius - 6, y + 5)]
        pygame.draw.polygon(screen, (180, 15, 15), tail_points)
        
    def reset(self, x, y):
        """Reset bird state"""
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.is_launched = False
        self.is_aiming = False
        self.trail = []

class Pig:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.color = (0, 255, 0)
        self.health = 100
        self.is_alive = True
        
        # Try to load pig sprite
        self.image = None
        self.use_image = False
        try:
            # Attempt to load pig sprite file
            self.image = pygame.image.load("pig.png")
            self.image = pygame.transform.scale(self.image, (self.radius * 3, self.radius * 3))
            self.use_image = True
            print("✅ Successfully loaded pig image: pig.png")
        except pygame.error as e:
            print(f"⚠️ Failed to load pig.png: {e}")
            print("💡 Hint: Place pig.png in the project directory")
            # Fallback to vector drawing when image is unavailable
            self.use_image = False
        
    def take_damage(self, damage):
        """Take damage"""
        self.health -= damage
        if self.health <= 0:
            self.is_alive = False
            return True  # Return True if eliminated
        return False
        
    def draw(self, screen):
        """Draw the pig"""
        if self.is_alive:
            if self.use_image and self.image:
                # Draw pig using sprite
                pig_rect = self.image.get_rect()
                pig_rect.center = (int(self.x), int(self.y))
                screen.blit(self.image, pig_rect)
                
                # Add visual effects if pig is injured
                if self.health < 100:
                    # Draw health bar
                    bar_width = 30
                    bar_height = 4
                    bar_x = int(self.x - bar_width // 2)
                    bar_y = int(self.y - self.radius - 10)
                    
                    # Background bar
                    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                    # Health bar
                    health_width = int((self.health / 100) * bar_width)
                    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))
            else:
                # Use traditional drawing method
                self.draw_detailed_pig(screen)
    
    def draw_detailed_pig(self, screen):
        """Draw detailed pig (used when no image is available)"""
        x, y = int(self.x), int(self.y)
        
        # Pig body (circular, green)
        pygame.draw.circle(screen, (50, 200, 50), (x, y), self.radius)
        # Body border
        pygame.draw.circle(screen, (30, 150, 30), (x, y), self.radius, 2)
        
        # Pig ears
        ear_points1 = [(x - 12, y - 15), (x - 8, y - 20), (x - 4, y - 15)]
        ear_points2 = [(x + 4, y - 15), (x + 8, y - 20), (x + 12, y - 15)]
        pygame.draw.polygon(screen, (40, 180, 40), ear_points1)
        pygame.draw.polygon(screen, (40, 180, 40), ear_points2)
        
        # Eyes (white base)
        pygame.draw.circle(screen, (255, 255, 255), (x - 7, y - 7), 5)
        pygame.draw.circle(screen, (255, 255, 255), (x + 7, y - 7), 5)
        # Pupils
        pygame.draw.circle(screen, (0, 0, 0), (x - 7, y - 6), 3)
        pygame.draw.circle(screen, (0, 0, 0), (x + 7, y - 6), 3)
        # Highlights
        pygame.draw.circle(screen, (255, 255, 255), (x - 6, y - 7), 1)
        pygame.draw.circle(screen, (255, 255, 255), (x + 8, y - 7), 1)
        
        # Nose (oval)
        pygame.draw.ellipse(screen, (30, 120, 30), (x - 6, y + 2, 12, 8))
        # Nostrils
        pygame.draw.circle(screen, (0, 0, 0), (x - 3, y + 5), 1)
        pygame.draw.circle(screen, (0, 0, 0), (x + 3, y + 5), 1)
        
        # Mouth (smile or frown)
        if self.health > 50:
            # Smile
            pygame.draw.arc(screen, (0, 0, 0), (x - 8, y + 8, 16, 10), 0, 3.14159, 2)
        else:
            # Frown
            pygame.draw.arc(screen, (0, 0, 0), (x - 8, y + 15, 16, 10), 3.14159, 6.28318, 2)

class Block:
    def __init__(self, x, y, width, height, color=(139, 69, 19)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.original_color = color
        self.health = 50
        self.is_destroyed = False
        
        # Determine block type based on color
        if color == (160, 82, 45):  # Wood
            self.health = 30
            self.block_type = "wood"
        elif color == (128, 128, 128):  # Stone
            self.health = 80
            self.block_type = "stone"
        elif color == (173, 216, 230):  # Ice
            self.health = 20
            self.block_type = "ice"
        else:  # Default wood
            self.health = 50
            self.block_type = "wood"
            
        self.max_health = self.health
        
    def take_damage(self, damage):
        """Take damage"""
        self.health -= damage
        if self.health <= 0:
            self.is_destroyed = True
            return True
        return False
        
    def draw(self, screen):
        """Draw the block"""
        if not self.is_destroyed:
            # Change color based on health
            health_ratio = self.health / self.max_health
            color = (
                int(self.original_color[0] * health_ratio),
                int(self.original_color[1] * health_ratio),
                int(self.original_color[2] * health_ratio)
            )
            
            # Draw block body
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
            
            # Add texture effects based on type
            if self.block_type == "wood":
                # Wood grain effect
                for i in range(0, self.height, 8):
                    lighter_color = (min(255, color[0] + 30), min(255, color[1] + 20), color[2])
                    pygame.draw.line(screen, lighter_color, 
                                   (self.x + 2, self.y + i), 
                                   (self.x + self.width - 2, self.y + i), 1)
            elif self.block_type == "stone":
                # Stone texture
                for i in range(0, self.width, 10):
                    for j in range(0, self.height, 10):
                        darker_color = (max(0, color[0] - 20), max(0, color[1] - 20), max(0, color[2] - 20))
                        pygame.draw.rect(screen, darker_color, 
                                       (self.x + i, self.y + j, 2, 2))
            elif self.block_type == "ice":
                # Ice effect - transparency and highlights
                ice_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                ice_surface.fill((*color, 200))  # Semi-transparent
                screen.blit(ice_surface, (self.x, self.y))
                
                # Ice highlights
                pygame.draw.line(screen, (255, 255, 255), 
                               (self.x + 5, self.y + 5), 
                               (self.x + self.width - 5, self.y + 5), 2)
                pygame.draw.line(screen, (255, 255, 255), 
                               (self.x + 5, self.y + 5), 
                               (self.x + 5, self.y + self.height - 5), 2)
            
            # Draw border
            border_color = (max(0, color[0] - 50), max(0, color[1] - 50), max(0, color[2] - 50))
            pygame.draw.rect(screen, border_color, (self.x, self.y, self.width, self.height), 2)

class Slingshot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 90
        
    def draw(self, screen, bird_pos=None, aiming=False):
        """Draw a simple Y-shaped slingshot - only the slingshot body"""
        # Y-shaped fork design
        fork_start_y = self.y + 20  # Adjust Y-shaped slingshot starting position
        fork_height = 50
        fork_width = 35
        
        # Fork connection - simplified version
        connection_rect = pygame.Rect(self.x - 8, fork_start_y - 5, 16, 15)
        pygame.draw.rect(screen, (100, 65, 40), connection_rect, border_radius=8)
        pygame.draw.rect(screen, (140, 90, 55), connection_rect, width=2, border_radius=8)
        
        # Left fork
        left_start = (self.x - 5, fork_start_y)
        left_end = (self.x - fork_width, fork_start_y - fork_height)
        
        # Left fork body
        pygame.draw.line(screen, (120, 80, 45), left_start, left_end, 12)
        
        # Left fork highlight
        pygame.draw.line(screen, (160, 110, 65), 
                        (left_start[0] - 2, left_start[1] - 2),
                        (left_end[0] - 2, left_end[1] - 2), 4)
        
        # Right fork
        right_start = (self.x + 5, fork_start_y)
        right_end = (self.x + fork_width, fork_start_y - fork_height)
        
        # Right fork body
        pygame.draw.line(screen, (120, 80, 45), right_start, right_end, 12)
        
        # Right fork highlight
        pygame.draw.line(screen, (160, 110, 65), 
                        (right_start[0] - 2, right_start[1] - 2),
                        (right_end[0] - 2, right_end[1] - 2), 4)
        
        # Fork endpoint decorations
        # Left endpoint
        pygame.draw.circle(screen, (140, 90, 55), left_end, 8)  # Main body
        pygame.draw.circle(screen, (180, 120, 75), left_end, 8, 2)  # Border
        pygame.draw.circle(screen, (200, 140, 90), left_end, 4)  # Inner
        
        # Right endpoint
        pygame.draw.circle(screen, (140, 90, 55), right_end, 8)  # Main body
        pygame.draw.circle(screen, (180, 120, 75), right_end, 8, 2)  # Border
        pygame.draw.circle(screen, (200, 140, 90), right_end, 4)  # Inner
        
        # Rope connection points
        left_rope_point = left_end
        right_rope_point = right_end
        
        if bird_pos and aiming:
            # Elastic rope when aiming - more realistic effect
            rope_color = (101, 67, 33)
            rope_highlight = (140, 95, 60)
            
            # Main rope
            pygame.draw.line(screen, rope_color, left_rope_point, bird_pos, 4)
            pygame.draw.line(screen, rope_color, right_rope_point, bird_pos, 4)
            
            # Rope highlight
            pygame.draw.line(screen, rope_highlight, left_rope_point, bird_pos, 2)
            pygame.draw.line(screen, rope_highlight, right_rope_point, bird_pos, 2)
            
            # Rope texture
            pygame.draw.line(screen, (120, 80, 50), left_rope_point, bird_pos, 1)
            pygame.draw.line(screen, (120, 80, 50), right_rope_point, bird_pos, 1)
            
            # === Aiming assistance line (trajectory prediction) ===
            if bird_pos:
                # Calculate pull vector
                pull_vector_x = self.x - bird_pos[0]
                pull_vector_y = self.y - bird_pos[1]
                pull_distance = math.sqrt(pull_vector_x**2 + pull_vector_y**2)
                
                if pull_distance > 10:  # Only show when pull is sufficient
                    # Calculate trajectory prediction points
                    launch_power = min(pull_distance * 0.3, 30)  # Match game launch logic
                    launch_angle = math.atan2(pull_vector_y, pull_vector_x)
                    
                    # Draw trajectory prediction
                    trajectory_points = []
                    gravity = 0.3
                    time_step = 0.5
                    initial_vx = launch_power * math.cos(launch_angle) * 0.3
                    initial_vy = launch_power * math.sin(launch_angle) * 0.3
                    
                    for t in range(0, 40, 2):  # Predict 20 time steps
                        time = t * time_step
                        pred_x = bird_pos[0] + initial_vx * time
                        pred_y = bird_pos[1] + initial_vy * time + 0.5 * gravity * time * time
                        
                        if pred_y > 550:  # Ground height
                            break
                            
                        trajectory_points.append((int(pred_x), int(pred_y)))
                    
                    # Draw trajectory points (dashed line effect)
                    for i, point in enumerate(trajectory_points):
                        if i % 3 == 0 and i < len(trajectory_points):  # Draw every 3rd point for dashed effect
                            point_alpha = max(50, 255 - int((i / max(1, len(trajectory_points))) * 200))
                            point_size = max(1, 4 - int((i / max(1, len(trajectory_points))) * 2))
                            
                            # Create semi-transparent circle
                            trajectory_surface = pygame.Surface((point_size * 4, point_size * 4), pygame.SRCALPHA)
                            trajectory_color = (255, 255, 100, point_alpha)
                            pygame.draw.circle(trajectory_surface, trajectory_color, 
                                             (point_size * 2, point_size * 2), point_size)
                            
                            # Add outer glow
                            glow_surface = pygame.Surface((point_size * 6, point_size * 6), pygame.SRCALPHA)
                            glow_color = (255, 200, 0, max(20, point_alpha // 3))
                            pygame.draw.circle(glow_surface, glow_color, 
                                             (point_size * 3, point_size * 3), point_size * 2)
                            
                            screen.blit(glow_surface, (point[0] - point_size * 3, point[1] - point_size * 3))
                            screen.blit(trajectory_surface, (point[0] - point_size * 2, point[1] - point_size * 2))
            
            # === Pull force indicator ===
            if bird_pos:
                pull_distance = math.sqrt((self.x - bird_pos[0])**2 + (self.y - bird_pos[1])**2)
                if pull_distance > 5:
                    # Display force bar above slingshot
                    bar_width = 80
                    bar_height = 8
                    bar_x = self.x - bar_width // 2
                    bar_y = self.y - 80
                    
                    # Background bar
                    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
                    pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), width=2, border_radius=4)
                    
                    # Force bar
                    power_ratio = min(pull_distance / 100, 1.0)  # Maximum pull distance 100
                    power_width = int(power_ratio * bar_width)
                    
                    # Choose color based on force
                    if power_ratio < 0.3:
                        power_color = (255, 100, 100)  # Red (insufficient force)
                    elif power_ratio < 0.7:
                        power_color = (255, 255, 100)  # Yellow (moderate)
                    else:
                        power_color = (100, 255, 100)  # Green (strong)
                    
                    pygame.draw.rect(screen, power_color, (bar_x, bar_y, power_width, bar_height), border_radius=4)
                    
                    # Force value display
                    power_percentage = int(power_ratio * 100)
                    font = pygame.font.Font(None, 24)
                    power_text = font.render(f"{power_percentage}%", True, (255, 255, 255))
                    text_rect = power_text.get_rect(center=(self.x, bar_y - 15))
                    screen.blit(power_text, text_rect)
            
        else:
            # Rope in resting state
            rope_color = (101, 67, 33)
            rope_highlight = (140, 95, 60)
            
            # Main rope
            pygame.draw.line(screen, rope_color, left_rope_point, right_rope_point, 4)
            
            # Rope highlight
            pygame.draw.line(screen, rope_highlight, left_rope_point, right_rope_point, 2)
            
            # Rope texture
            pygame.draw.line(screen, (120, 80, 50), left_rope_point, right_rope_point, 1)

class AngryBirdsGame:
    def __init__(self):
        pygame.init()
        self.width = 1200
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Gesture-Controlled Angry Birds")
        self.clock = pygame.time.Clock()
        
        # Background image
        self.background_image = None
        self.use_background_image = False
        try:
            # Attempt to load background image file
            self.background_image = pygame.image.load("background.png")
            self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))
            self.use_background_image = True
            print("✅ Loaded background image: background.png")
        except pygame.error as e:
            print(f"⚠️ Failed to load background.png: {e}")
            print("💡 Hint: Place background.png in the project directory; falling back to default background")
            self.use_background_image = False

        # Score panel background image
        self.score_bg_image = None
        try:
            self.score_bg_image = pygame.image.load("Scoring_Zone.png")
            print("✅ Loaded score panel background image: Scoring_Zone.png")
        except pygame.error as e:
            print(f"❌ Failed to load score panel background image Scoring_Zone.png: {e}")
            self.score_bg_image = None
        
        # Animation state
        self.time_counter = 0
        self.cloud_offset = 0
        self.particles = []  # Particle effects
        
        # Game objects
        self.slingshot = Slingshot(100, 400)
        self.bird = Bird(100, 400)
        self.pigs = []
        self.blocks = []
        
        # Game state
        self.score = 0
        self.level = 1
        self.is_aiming = False
        self.aim_power = 0
        self.aim_angle = 0
        
        # Fonts (attempt Chinese-capable fonts; fallback to default)
        try:
            self.font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 28)
            self.small_font = pygame.font.SysFont('microsoftyaheimicrosoftyaheiui', 20)
        except:
            try:
                # Fallback: use SimHei if available
                self.font = pygame.font.SysFont('simhei', 28)
                self.small_font = pygame.font.SysFont('simhei', 20)
            except:
                # Final fallback: default font
                self.font = pygame.font.Font(None, 36)
                self.small_font = pygame.font.Font(None, 24)
        
        self.create_level()
        
    def create_level(self):
        """Create level - reference screenshot design"""
        self.pigs = []
        self.blocks = []
        
        if self.level == 1:
            # Level 1: Basic structure
            # Left platform
            self.blocks.append(Block(600, 500, 80, 40, (101, 67, 33)))  # Bottom platform
            
            # Central building structure
            # Bottom layer blocks
            self.blocks.append(Block(750, 500, 50, 50, (160, 82, 45)))  # Wooden blocks
            self.blocks.append(Block(800, 500, 50, 50, (160, 82, 45)))
            self.blocks.append(Block(850, 500, 50, 50, (160, 82, 45)))
            
            # Middle layer structure
            self.blocks.append(Block(770, 450, 50, 50, (160, 82, 45)))
            self.blocks.append(Block(820, 450, 50, 50, (160, 82, 45)))
            
            # Top layer
            self.blocks.append(Block(795, 400, 50, 50, (160, 82, 45)))
            
            # Right tower
            for i in range(4):
                self.blocks.append(Block(950, 500 - i * 50, 40, 50, (128, 128, 128)))  # Stone blocks
            
            # Ice decorations
            self.blocks.append(Block(720, 480, 30, 30, (173, 216, 230)))  # Ice blocks
            self.blocks.append(Block(900, 480, 30, 30, (173, 216, 230)))
            
            # Place pigs
            self.pigs.append(Pig(625, 470))  # Pig on left platform
            self.pigs.append(Pig(795, 380))  # Pig on central top
            self.pigs.append(Pig(970, 330))  # Pig on right tower top
            
        elif self.level == 2:
            # Level 2: Complex structure
            # Multi-story building
            # Bottom foundation
            for i in range(5):
                self.blocks.append(Block(650 + i * 50, 500, 50, 50, (160, 82, 45)))
            
            # Second layer
            for i in range(3):
                self.blocks.append(Block(700 + i * 50, 450, 50, 50, (128, 128, 128)))
            
            # Third layer
            self.blocks.append(Block(725, 400, 50, 50, (160, 82, 45)))
            self.blocks.append(Block(775, 400, 50, 50, (160, 82, 45)))
            
            # Top layer
            self.blocks.append(Block(750, 350, 50, 50, (173, 216, 230)))
            
            # Side support towers
            for i in range(3):
                self.blocks.append(Block(600, 500 - i * 50, 40, 50, (128, 128, 128)))
                self.blocks.append(Block(900, 500 - i * 50, 40, 50, (128, 128, 128)))
            
            # Place pigs
            self.pigs.append(Pig(725, 480))
            self.pigs.append(Pig(775, 480))
            self.pigs.append(Pig(750, 430))
            self.pigs.append(Pig(750, 330))
            self.pigs.append(Pig(620, 430))
            
        else:
            # Random level
            base_x = 650
            for i in range(min(6, self.level)):
                x = base_x + i * 60 + random.randint(-20, 20)
                y = 500 - random.randint(0, 150)
                block_type = random.choice([(160, 82, 45), (128, 128, 128), (173, 216, 230)])
                self.blocks.append(Block(x, y, 50, 50, block_type))
                
                if random.random() < 0.4:  # 40% chance to place pig
                    self.pigs.append(Pig(x + 25, y - 30))
        
    def handle_gesture_input(self, gesture_params):
        """Handle gesture input"""
        self.last_gesture_params = gesture_params
        
        if not self.bird.is_launched:
            # Check if currently grabbing (aiming mode)
            if gesture_params['power'] > 0:  # Has pull action
                self.is_aiming = True
                self.aim_power = min(gesture_params['power'], 100)  # Limit maximum power
                # Use gesture detection angle directly, no additional conversion
                self.aim_angle = gesture_params['angle']
                
                # Make bird follow slingshot pull movement
                self.bird.set_aiming_position(self.aim_power, self.aim_angle)
                
            else:
                self.is_aiming = False
                # Reset bird to slingshot position
                self.bird.reset_position()
                
            # Check if should launch
            if gesture_params['should_launch']:
                # Launch bird using current aiming parameters
                print(f"🚀 Launching bird! Power: {self.aim_power:.1f}, Angle: {math.degrees(self.aim_angle):.1f}°")
                self.bird.launch(self.aim_power, self.aim_angle)
                self.is_aiming = False
            
    def check_collisions(self):
        """Check collisions"""
        if not self.bird.is_launched:
            return
            
        bird_rect = pygame.Rect(self.bird.x - self.bird.radius, self.bird.y - self.bird.radius, 
                               self.bird.radius * 2, self.bird.radius * 2)
        
        # Check collision with pigs
        for pig in self.pigs[:]:
            pig_rect = pygame.Rect(pig.x - pig.radius, pig.y - pig.radius, 
                                 pig.radius * 2, pig.radius * 2)
            if bird_rect.colliderect(pig_rect) and pig.is_alive:
                if pig.take_damage(50):
                    self.score += 100
                    self.pigs.remove(pig)
                    # Add explosion particle effects
                    self.add_explosion_particles(pig.x, pig.y)
                    
        # Check collision with blocks
        for block in self.blocks[:]:
            block_rect = pygame.Rect(block.x, block.y, block.width, block.height)
            if bird_rect.colliderect(block_rect) and not block.is_destroyed:
                if block.take_damage(30):
                    self.score += 50
                    self.blocks.remove(block)
                    # Add explosion particle effects
                    self.add_explosion_particles(block.x + block.width//2, block.y + block.height//2)
                    
    def update(self):
        """Update game state"""
        self.time_counter += 1
        self.cloud_offset = (self.cloud_offset + 0.2) % self.width  # Cloud floating
        
        # Update particle effects
        self.update_particles()
        
        self.bird.update()
        self.check_collisions()
        
        # Check if reset is needed
        if self.bird.is_launched and (self.bird.x > self.width or 
                                     (abs(self.bird.vx) < 0.1 and abs(self.bird.vy) < 0.1 and self.bird.y >= 545)):
            # Bird has stopped, reset
            self.bird.reset(100, 400)
            
        # Check victory condition
        if len(self.pigs) == 0:
            self.level += 1
            self.create_level()
            self.bird.reset(100, 400)
            # Victory particle effects
            self.add_victory_particles()
    
    def add_victory_particles(self):
        """Add victory particle effects"""
        for _ in range(20):
            self.particles.append({
                'x': random.randint(self.width//4, 3*self.width//4),
                'y': random.randint(100, 300),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-3, -1),
                'life': 60,
                'color': (255, 215, 0),  # Gold
                'size': random.randint(3, 8)
            })
    
    def add_explosion_particles(self, x, y):
        """Add explosion particle effects"""
        for _ in range(15):
            self.particles.append({
                'x': x + random.uniform(-10, 10),
                'y': y + random.uniform(-10, 10),
                'vx': random.uniform(-4, 4),
                'vy': random.uniform(-4, 4),
                'life': 30,
                'color': (255, random.randint(100, 200), 0),  # Orange-red
                'size': random.randint(2, 6)
            })
    
    def update_particles(self):
        """Update particle effects"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # Gravity
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
            
    def draw(self):
        """Draw the game"""
        # Draw background
        if self.use_background_image and self.background_image:
            # Use background image
            self.screen.blit(self.background_image, (0, 0))
            # Add dynamic cloud effects
            self.draw_animated_clouds()
        else:
            # Use optimized gradient background
            self.draw_gradient_background()
        
        # Draw ground shadow effects
        self.draw_ground_shadow()
        
        # Draw game objects
        for block in self.blocks:
            block.draw(self.screen)
            
        for pig in self.pigs:
            if pig.is_alive:
                pig.draw(self.screen)
        
        # Draw slingshot - draw slingshot and rope first
        if self.is_aiming and not self.bird.is_launched:
            # Bird is already in correct aiming position, connect rope directly to bird position
            self.slingshot.draw(self.screen, (self.bird.x, self.bird.y), True)
            
            # Draw enhanced prediction trajectory - starting from bird's current position
            self.draw_enhanced_trajectory(self.bird.x, self.bird.y, self.aim_power, self.aim_angle)
        else:
            self.slingshot.draw(self.screen)
        
        # Draw bird - after slingshot rope to ensure bird is on top of rope
        self.bird.draw(self.screen)
        
        # Draw particle effects
        self.draw_particles()
        
        # Draw optimized UI interface
        self.draw_enhanced_ui()
    
    def draw_gradient_background(self):
        """Draw beautiful gradient background and landscape"""
        # === Sky gradient ===
        for y in range(400):  # Sky area
            ratio = y / 400
            # Sky gradient from light blue to dark blue
            r = int(135 - (135 - 25) * ratio)
            g = int(206 - (206 - 25) * ratio)
            b = int(235 - (235 - 112) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))
        
        # === Distant mountain silhouettes ===
        # First layer distant mountains (light purple)
        mountain_points_1 = [
            (0, 300), (150, 250), (300, 280), (450, 220), (600, 260), 
            (750, 200), (900, 240), (1050, 190), (self.width, 230), 
            (self.width, 400), (0, 400)
        ]
        pygame.draw.polygon(self.screen, (98, 68, 132), mountain_points_1)
        
        # Second layer closer mountains (darker purple)
        mountain_points_2 = [
            (0, 350), (120, 320), (250, 340), (400, 300), (550, 330), 
            (700, 280), (850, 310), (1000, 270), (self.width, 300), 
            (self.width, 400), (0, 400)
        ]
        pygame.draw.polygon(self.screen, (78, 48, 112), mountain_points_2)
        
        # Add mountain peak highlights
        for i in range(len(mountain_points_1) - 2):
            if i % 2 == 0:
                start_point = mountain_points_1[i]
                end_point = mountain_points_1[i + 1]
                # Draw highlight lines
                pygame.draw.line(self.screen, (128, 98, 162), start_point, end_point, 2)
        
        # === Ground grass effects ===
        # Main ground
        ground_gradient_start = 450
        for y in range(ground_gradient_start, self.height):
            ratio = (y - ground_gradient_start) / (self.height - ground_gradient_start)
            # Ground gradient from light green to dark brown
            r = int(101 + (139 - 101) * (1 - ratio) * 0.7)
            g = int(67 + (169 - 67) * (1 - ratio))
            b = int(33 + (39 - 33) * (1 - ratio))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))
        
        # Grass texture
        grass_surface = pygame.Surface((self.width, 100), pygame.SRCALPHA)
        for i in range(0, self.width, 8):
            # Random grass height and color
            grass_height = random.randint(3, 12)
            grass_color_variation = random.randint(-20, 20)
            grass_color = (max(0, min(255, 34 + grass_color_variation)), 
                          max(0, min(255, 139 + grass_color_variation)), 
                          max(0, min(255, 34 + grass_color_variation)))
            
            # Draw grass blades
            start_x = i + random.randint(-2, 2)
            pygame.draw.line(grass_surface, grass_color, 
                           (start_x, 100), (start_x + random.randint(-2, 2), 100 - grass_height), 3)
            
            # Add some detail grass blades
            if random.random() < 0.3:
                pygame.draw.line(grass_surface, (20, 100, 20), 
                               (start_x + 1, 100), (start_x - 1, 100 - grass_height // 2), 1)
        
        self.screen.blit(grass_surface, (0, 450))
        
        # === Decorative clouds ===
        self.draw_enhanced_clouds()
        
    def draw_enhanced_clouds(self):
        """Draw enhanced cloud effects"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Multi-layer clouds, moving at different speeds
        cloud_layers = [
            {'positions': [(100, 80), (400, 60), (700, 90), (950, 70)], 'speed': 0.2, 'alpha': 180, 'size': 1.0},
            {'positions': [(200, 120), (500, 100), (800, 140), (50, 110)], 'speed': 0.15, 'alpha': 150, 'size': 0.8},
            {'positions': [(300, 50), (600, 180), (900, 40), (150, 160)], 'speed': 0.1, 'alpha': 120, 'size': 1.2}
        ]
        
        for layer in cloud_layers:
            cloud_surface = pygame.Surface((120, 60), pygame.SRCALPHA)
            
            for base_x, y in layer['positions']:
                # Cloud floating
                x = (base_x + current_time * layer['speed'] * 20) % (self.width + 120) - 60
                
                # Draw multiple overlapping circles to form 3D clouds
                cloud_surface.fill((0, 0, 0, 0))  # Clear surface
                
                # Cloud shadows
                shadow_offset = 3
                pygame.draw.circle(cloud_surface, (100, 100, 100, 40), 
                                 (35 + shadow_offset, 35 + shadow_offset), int(25 * layer['size']))
                pygame.draw.circle(cloud_surface, (100, 100, 100, 40), 
                                 (50 + shadow_offset, 25 + shadow_offset), int(20 * layer['size']))
                pygame.draw.circle(cloud_surface, (100, 100, 100, 40), 
                                 (65 + shadow_offset, 35 + shadow_offset), int(22 * layer['size']))
                
                # Main cloud body
                cloud_color = (255, 255, 255, layer['alpha'])
                pygame.draw.circle(cloud_surface, cloud_color, (35, 35), int(25 * layer['size']))
                pygame.draw.circle(cloud_surface, cloud_color, (50, 25), int(20 * layer['size']))
                pygame.draw.circle(cloud_surface, cloud_color, (65, 35), int(22 * layer['size']))
                
                # Cloud highlights
                highlight_color = (255, 255, 255, min(255, layer['alpha'] + 50))
                pygame.draw.circle(cloud_surface, highlight_color, (40, 30), int(12 * layer['size']))
                pygame.draw.circle(cloud_surface, highlight_color, (55, 20), int(10 * layer['size']))
                
                self.screen.blit(cloud_surface, (x, y))
    
    def draw_animated_clouds(self):
        """Draw animated cloud effects"""
        # Add subtle cloud floating effect
        cloud_alpha = 100 + int(20 * math.sin(self.time_counter * 0.02))
        cloud_surface = pygame.Surface((100, 50), pygame.SRCALPHA)
        cloud_surface.set_alpha(cloud_alpha)
        
        # Draw additional clouds
        positions = [(200 + self.cloud_offset % self.width, 80), 
                    (500 + self.cloud_offset % self.width, 120),
                    (800 + self.cloud_offset % self.width, 60)]
        
        for x, y in positions:
            pygame.draw.circle(cloud_surface, (255, 255, 255), (25, 25), 20)
            pygame.draw.circle(cloud_surface, (255, 255, 255), (40, 20), 15)
            pygame.draw.circle(cloud_surface, (255, 255, 255), (55, 25), 18)
            self.screen.blit(cloud_surface, (x - 50, y))
    
    def draw_shadow(self, x, y, width, height):
        """Draw rectangular shadow"""
        shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 50))
        self.screen.blit(shadow_surface, (x, y))
    
    def draw_circular_shadow(self, x, y, radius):
        """Draw circular shadow"""
        shadow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (0, 0, 0, 50), (radius, radius), radius)
        self.screen.blit(shadow_surface, (x - radius, y - radius))
    
    def draw_ground_shadow(self):
        """Draw ground shadow effects"""
        # Add gradient shadow above ground
        for i in range(20):
            alpha = 30 - i
            if alpha > 0:
                shadow_surface = pygame.Surface((self.width, 1), pygame.SRCALPHA)
                shadow_surface.fill((0, 0, 0, alpha))
                self.screen.blit(shadow_surface, (0, 530 + i))
    
    def draw_particles(self):
        """Draw enhanced particle effects"""
        for particle in self.particles[:]:
            # Update particle state
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # Gravity
            particle['vx'] *= 0.98  # Air resistance
            particle['life'] -= 1
            particle['size'] = max(0.5, particle['size'] * 0.98)  # Particle shrinking
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
                continue
            
            # Calculate transparency
            alpha = max(0, min(255, int(particle['life'] * 3)))
            
            # Draw different effects based on particle type
            if particle.get('type') == 'explosion':
                # Explosion particles - brighter and more dazzling
                # Outer glow
                outer_size = int(particle['size'] * 2)
                if outer_size > 0:
                    outer_surface = pygame.Surface((outer_size * 2, outer_size * 2), pygame.SRCALPHA)
                    outer_color = (*particle['color'], alpha // 3)
                    pygame.draw.circle(outer_surface, outer_color, (outer_size, outer_size), outer_size)
                    self.screen.blit(outer_surface, (int(particle['x'] - outer_size), int(particle['y'] - outer_size)))
                
                # Main particle
                main_size = int(particle['size'])
                if main_size > 0:
                    main_surface = pygame.Surface((main_size * 2, main_size * 2), pygame.SRCALPHA)
                    main_color = (*particle['color'], alpha)
                    pygame.draw.circle(main_surface, main_color, (main_size, main_size), main_size)
                    self.screen.blit(main_surface, (int(particle['x'] - main_size), int(particle['y'] - main_size)))
                
                # Core highlight
                core_size = max(1, int(particle['size'] * 0.6))
                core_surface = pygame.Surface((core_size * 2, core_size * 2), pygame.SRCALPHA)
                core_color = (255, 255, 200, min(255, alpha * 2))
                pygame.draw.circle(core_surface, core_color, (core_size, core_size), core_size)
                self.screen.blit(core_surface, (int(particle['x'] - core_size), int(particle['y'] - core_size)))
            
            elif particle.get('type') == 'spark':
                # Spark particles - trail effect
                spark_length = int(particle['size'] * 3)
                end_x = int(particle['x'] - particle['vx'] * 3)
                end_y = int(particle['y'] - particle['vy'] * 3)
                
                # Draw trail
                for i in range(spark_length):
                    trail_alpha = alpha * (1 - i / spark_length)
                    if trail_alpha > 10:
                        trail_x = particle['x'] - particle['vx'] * i * 0.3
                        trail_y = particle['y'] - particle['vy'] * i * 0.3
                        trail_size = max(1, int(particle['size'] * (1 - i / spark_length)))
                        
                        trail_surface = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                        trail_color = (*particle['color'], int(trail_alpha))
                        pygame.draw.circle(trail_surface, trail_color, (trail_size, trail_size), trail_size)
                        self.screen.blit(trail_surface, (int(trail_x - trail_size), int(trail_y - trail_size)))
            
            else:
                # Normal particles
                size = int(particle['size'])
                if size > 0:
                    particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    color = (*particle['color'], alpha)
                    pygame.draw.circle(particle_surface, color, (size, size), size)
                    self.screen.blit(particle_surface, (int(particle['x'] - size), int(particle['y'] - size)))
    
    def add_explosion_particles(self, x, y, intensity=20):
        """Add enhanced explosion particle effects"""
        # Main explosion particles
        for _ in range(intensity):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            self.particles.append({
                'x': x + random.uniform(-5, 5),
                'y': y + random.uniform(-5, 5),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(30, 60),
                'size': random.uniform(3, 8),
                'color': random.choice([(255, 100, 0), (255, 150, 0), (255, 200, 100), (255, 80, 80)]),
                'type': 'explosion'
            })
        
        # Spark particles
        for _ in range(intensity // 2):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(8, 15)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(15, 30),
                'size': random.uniform(1, 3),
                'color': random.choice([(255, 255, 0), (255, 200, 0), (255, 255, 200)]),
                'type': 'spark'
            })
        
        # Smoke particles
        for _ in range(intensity // 3):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.particles.append({
                'x': x + random.uniform(-10, 10),
                'y': y + random.uniform(-10, 10),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 2,  # Float upward
                'life': random.randint(40, 80),
                'size': random.uniform(5, 12),
                'color': random.choice([(100, 100, 100), (120, 120, 120), (80, 80, 80)]),
                'type': 'smoke'
            })
    
    def draw_enhanced_ui(self):
        """Draw beautiful UI interface"""
        # # === Main information panel ===
        # # Create UI background with gradient effects
        # ui_width, ui_height = 280, 80
        # ui_surface = pygame.Surface((ui_width, ui_height), pygame.SRCALPHA)
        
        # # Add outer glow shadow
        # shadow_size = 6
        # for i in range(shadow_size):
        #     shadow_alpha = 80 - i * 12
        #     if shadow_alpha > 0:
        #         shadow_rect = pygame.Rect(15 + i, 15 + i, ui_width, ui_height)
        #         pygame.draw.rect(self.screen, (0, 0, 0, shadow_alpha), shadow_rect, border_radius=18)
        
        # # Draw rich gradient background
        # for i in range(ui_height):
        #     # Create gradient from dark to light with subtle color variations
        #     progress = i / ui_height
        #     base_r = int(15 + progress * 25)  # From dark blue-black to light blue
        #     base_g = int(20 + progress * 35)
        #     base_b = int(40 + progress * 45)
            
        #     # Add subtle color layers
        #     if progress < 0.3:
        #         # Top area biased blue
        #         r, g, b = base_r, base_g, base_b + 20
        #     elif progress < 0.7:
        #         # Middle area
        #         r, g, b = base_r + 5, base_g + 10, base_b
        #     else:
        #         # Bottom area slightly brighter
        #         r, g, b = base_r + 10, base_g + 15, base_b - 5
            
        #     color = (min(255, r), min(255, g), min(255, b))
        #     pygame.draw.rect(ui_surface, color, (0, i, ui_width, 1))
        
        # # Multi-layer border system
        # # Outermost border - dark outline
        # pygame.draw.rect(ui_surface, (60, 90, 140), (0, 0, ui_width, ui_height), width=2, border_radius=15)
        
        # # Second layer border - medium brightness
        # pygame.draw.rect(ui_surface, (120, 160, 220), (1, 1, ui_width-2, ui_height-2), width=2, border_radius=14)
        
        # # Inner highlight border
        # pygame.draw.rect(ui_surface, (180, 210, 255), (3, 3, ui_width-6, ui_height-6), width=1, border_radius=12)
        
        # # Top highlight band
        # top_highlight = pygame.Rect(4, 4, ui_width-8, 16)
        # pygame.draw.rect(ui_surface, (255, 255, 255, 100), top_highlight, border_radius=10)
        
        # # Add detail decorations
        # # Top-left corner decoration
        # corner_points = [(10, 4), (4, 4), (4, 10)]
        # pygame.draw.lines(ui_surface, (255, 255, 255, 150), False, corner_points, 2)
        
        # # Top-right corner decoration
        # corner_points = [(ui_width-10, 4), (ui_width-4, 4), (ui_width-4, 10)]
        # pygame.draw.lines(ui_surface, (255, 255, 255, 150), False, corner_points, 2)
        
        # # Bottom subtle inner glow
        # bottom_glow = pygame.Rect(6, ui_height-12, ui_width-12, 6)
        # pygame.draw.rect(ui_surface, (100, 140, 200, 40), bottom_glow, border_radius=3)
        
        # self.screen.blit(ui_surface, (15, 15))
        
        # === Unified background image display (covering three information areas) ===
        # Calculate text area boundaries
        text_area_x, text_area_y = 15, 30
        text_area_width, text_area_height = 260, 85  # Increase background frame size
        
        # Define text padding
        padding_x = 18  # Horizontal padding, increased from 10 to 18
        padding_y = 15  # Vertical padding, increased from 8 to 15
        
        # Use entire score area background image as unified background
        if self.score_bg_image: 
            # Scale background image to appropriate size
            try:
                # Create a Surface that supports transparency
                transparent_surface = pygame.Surface((text_area_width, text_area_height), pygame.SRCALPHA)
                
                # Only draw rounded rectangle, don't fill first to avoid right-angle frames
                pygame.draw.rect(transparent_surface, (240, 240, 240, 128), (0, 0, text_area_width, text_area_height), border_radius=20)
                
                # Optional: add rounded border
                pygame.draw.rect(transparent_surface, (200, 200, 200, 160), (0, 0, text_area_width, text_area_height), width=2, border_radius=20)
                
                # Draw to screen
                self.screen.blit(transparent_surface, (text_area_x, text_area_y))
                
            except Exception as e:
                print(f"Background image display error: {e}")
                # Fallback: draw solid color background
                pygame.draw.rect(self.screen, (240, 240, 240), (text_area_x, text_area_y, text_area_width, text_area_height), border_radius=10)
                pygame.draw.rect(self.screen, (150, 150, 150), (text_area_x, text_area_y, text_area_width, text_area_height), width=2, border_radius=10)
        else:
            # Fallback when no background image
            pygame.draw.rect(self.screen, (240, 240, 240), (text_area_x, text_area_y, text_area_width, text_area_height), border_radius=10)
            pygame.draw.rect(self.screen, (150, 150, 150), (text_area_x, text_area_y, text_area_width, text_area_height), width=2, border_radius=10)

        # === Score display text ===
        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (text_area_x + padding_x, text_area_y + padding_y))
        
        # === Level display text ===
        level_text = self.font.render(f"Level: {self.level}", True, (0, 0, 0))
        self.screen.blit(level_text, (text_area_x + 160, text_area_y + padding_y))
        
        # === Remaining pigs display text ===
        pigs_remaining = len([pig for pig in self.pigs if pig.is_alive])
        pigs_text = self.font.render(f"huskies: {pigs_remaining}", True, (0, 0, 0))
        self.screen.blit(pigs_text, (text_area_x + padding_x, text_area_y + padding_y + 35))  # Second line text, increase line spacing
 
        
        # === Gesture status indicator (right side) ===
        if hasattr(self, 'last_gesture_params') and self.last_gesture_params:
            gesture_panel_width, gesture_panel_height = 200, 120
            gesture_surface = pygame.Surface((gesture_panel_width, gesture_panel_height), pygame.SRCALPHA)
            
            # Gradient background
            for i in range(gesture_panel_height):
                alpha = 180 - i * 1.5
                alpha = max(50, min(180, alpha))
                color = (35, 20, 45, alpha)
                pygame.draw.rect(gesture_surface, color, (0, i, gesture_panel_width, 1))
            
            # Border decoration
            pygame.draw.rect(gesture_surface, (150, 100, 200, 120), (2, 2, gesture_panel_width-4, gesture_panel_height-4), border_radius=12)
            pygame.draw.rect(gesture_surface, (200, 150, 255, 80), (2, 2, gesture_panel_width-4, gesture_panel_height-4), width=2, border_radius=12)
            
            self.screen.blit(gesture_surface, (self.width - gesture_panel_width - 15, 15))
            
            # Gesture information display
            params = self.last_gesture_params
            small_font = pygame.font.Font(None, 24)
            
            # Status indicator
            if params.get('params_locked', False):
                status_text = "🔒 LOCKED"
                status_color = (100, 255, 255)
            elif params.get('ready_to_launch', False):
                status_text = "✅ READY"
                status_color = (100, 255, 100)
            elif params['power'] > 0:
                status_text = "🎯 AIMING"
                status_color = (255, 255, 100)
            else:
                status_text = "⏳ WAITING"
                status_color = (200, 200, 200)
            
            status_render = small_font.render(status_text, True, status_color)
            status_shadow = small_font.render(status_text, True, (0, 0, 0))
            self.screen.blit(status_shadow, (self.width - gesture_panel_width + 12, 37))
            self.screen.blit(status_render, (self.width - gesture_panel_width + 10, 35))
            
            # Force indicator bar
            if params['power'] > 0:
                bar_x = self.width - gesture_panel_width + 10
                bar_y = 60
                bar_width = 120
                bar_height = 12
                
                # Background bar
                pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=6)
                pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), width=2, border_radius=6)
                
                # Force bar
                power_width = int((params['power'] / 100) * bar_width)
                power_color = (255, 100, 100) if params['power'] < 20 else (100, 255, 100)
                pygame.draw.rect(self.screen, power_color, (bar_x, bar_y, power_width, bar_height), border_radius=6)
                
                # Force value
                power_text = f"Power: {int(params['power'])}"
                power_render = small_font.render(power_text, True, (255, 255, 255))
                self.screen.blit(power_render, (bar_x + 135, bar_y - 2))
            
            # Angle display
            if params['power'] > 0:
                angle_degrees = math.degrees(params['angle'])
                angle_text = f"Angle: {int(angle_degrees)}°"
                angle_render = small_font.render(angle_text, True, (255, 255, 255))
                angle_shadow = small_font.render(angle_text, True, (0, 0, 0))
                self.screen.blit(angle_shadow, (self.width - gesture_panel_width + 12, 82))
                self.screen.blit(angle_render, (self.width - gesture_panel_width + 10, 80))
                
                # Angle indicator (small compass)
                compass_x = self.width - 50
                compass_y = 105
                compass_radius = 20
                
                # Compass background
                pygame.draw.circle(self.screen, (50, 50, 50), (compass_x, compass_y), compass_radius)
                pygame.draw.circle(self.screen, (100, 100, 100), (compass_x, compass_y), compass_radius, 2)
                
                # Angle pointer
                pointer_length = compass_radius - 3
                pointer_x = compass_x + pointer_length * math.cos(params['angle'])
                pointer_y = compass_y + pointer_length * math.sin(params['angle'])
                pygame.draw.line(self.screen, (255, 200, 100), (compass_x, compass_y), (pointer_x, pointer_y), 3)
                pygame.draw.circle(self.screen, (255, 255, 100), (compass_x, compass_y), 3)
        
        # === Game status prompts ===
        if len(self.pigs) == 0:
            # Victory prompt
            victory_text = self.font.render("🎉 LEVEL COMPLETE!", True, (255, 255, 0))
            victory_shadow = self.font.render("🎉 LEVEL COMPLETE!", True, (0, 0, 0))
            text_x = self.width // 2 - victory_text.get_width() // 2
            self.screen.blit(victory_shadow, (text_x + 2, 202))
            self.screen.blit(victory_text, (text_x, 200))
        elif self.bird.is_launched and self.bird.vy == 0 and abs(self.bird.vx) < 0.1:
            # Bird stopped but pigs still exist
            retry_text = self.font.render("Click to restart or adjust gesture", True, (255, 200, 200))
            text_x = self.width // 2 - retry_text.get_width() // 2
            self.screen.blit(retry_text, (text_x, 250))
        
    def draw_enhanced_trajectory(self, start_x, start_y, power, angle):
        """Draw dashed prediction trajectory - completely consistent with actual launch"""
        if power <= 0:  # Prevent invalid power values
            return
            
        points = []
        # Use same velocity calculation as Bird.launch
        vx = power * math.cos(angle) * 0.3  # Completely consistent with Bird.launch
        vy = power * math.sin(angle) * 0.3  # Completely consistent with Bird.launch
        x, y = start_x, start_y
        
        gravity = 0.3  # Consistent with gravity value in Bird class
        
        for i in range(50):
            if 0 <= x <= self.width and 0 <= y <= self.height + 100:  # Ensure within reasonable range
                points.append((int(x), int(y)))
            
            x += vx
            y += vy
            vy += gravity  # Use same gravity value
            
            if y > 550:  # Hit ground (consistent with Bird class)
                break
        
        # Draw dashed trajectory
        if len(points) > 1:
            dash_length = 8  # Dash length
            gap_length = 6   # Gap length
            
            for i in range(len(points) - 1):
                # Calculate current segment length
                dx = points[i + 1][0] - points[i][0]
                dy = points[i + 1][1] - points[i][1]
                segment_length = math.sqrt(dx * dx + dy * dy)
                
                if segment_length > 0.1:  # Prevent division by zero and overly short segments
                    # Normalize direction vector
                    unit_x = dx / segment_length
                    unit_y = dy / segment_length
                    
                    # Calculate transparency
                    alpha = max(0.1, 1 - (i / max(1, len(points))))
                    
                    # Draw dashed segments
                    current_pos = 0
                    while current_pos < segment_length:
                        # Calculate start and end positions of dash segment
                        start_pos = current_pos
                        end_pos = min(current_pos + dash_length, segment_length)
                        
                        if start_pos < segment_length:
                            # Calculate actual drawing points
                            start_point = (
                                int(points[i][0] + unit_x * start_pos),
                                int(points[i][1] + unit_y * start_pos)
                            )
                            end_point = (
                                int(points[i][0] + unit_x * end_pos),
                                int(points[i][1] + unit_y * end_pos)
                            )
                            
                            # Draw main dash segment
                            main_color = (int(255 * alpha), int(220 * alpha), int(50 * alpha))
                            pygame.draw.line(self.screen, main_color, start_point, end_point, 3)
                            
                            # Draw dash segment highlight
                            highlight_color = (int(255 * alpha), int(255 * alpha), int(150 * alpha))
                            pygame.draw.line(self.screen, highlight_color, start_point, end_point, 1)
                        
                        # Move to next dash segment
                        current_pos += dash_length + gap_length
        
        # Draw small circles at trajectory key points
        for i, point in enumerate(points):
            if i % 8 == 0 and len(points) > 0:  # Draw every 8th point
                alpha = max(0.2, 1 - (i / max(1, len(points))))
                pulse = 0.8 + 0.2 * math.sin(self.time_counter * 0.3 + i * 0.3)
                
                # Circle color
                color = (int(255 * alpha * pulse), int(220 * alpha * pulse), int(80 * alpha))
                size = max(1, int(4 * alpha * pulse))
                
                if size > 0:
                    # Draw main circle
                    pygame.draw.circle(self.screen, color, point, size)
                    
                    # Draw inner highlight
                    if size > 2:
                        pygame.draw.circle(self.screen, (255, 255, 255), point, size // 2)
    
    def draw_trajectory(self, start_x, start_y, power, angle):
        """Draw prediction trajectory (compatibility method)"""
        self.draw_enhanced_trajectory(start_x, start_y, power, angle)
    
    def run(self):
        """Run the main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()

if __name__ == "__main__":
    game = AngryBirdsGame()
    game.run()
