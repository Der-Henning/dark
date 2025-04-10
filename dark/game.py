import random

import pygame

from dark.labyrinth import Labyrinth
from dark.ray_tracing import RayTracing

WIDTH = 40
HEIGHT = 20
CELL_SIZE = 30
RAYS = 120
FPS_LIMIT = 60

SCREEN_SIZE = (WIDTH * CELL_SIZE + 1, HEIGHT * CELL_SIZE + 1)


def generate_labyrinth() -> list[tuple[pygame.Vector2, pygame.Vector2]]:
    """Generate new random labyrinth.

    Returns:
        list[tuple[pygame.Vector2, pygame.Vector2]]: labyrinth walls
    """
    labyrinth = Labyrinth(WIDTH, HEIGHT)
    edges = labyrinth.generate()
    walls = []
    for edge in edges:
        start_wall = pygame.Vector2(edge.start) * CELL_SIZE
        end_wall = pygame.Vector2(edge.end) * CELL_SIZE
        walls.append((start_wall, end_wall))
    return walls


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.my_font = pygame.font.SysFont('Comic Sans MS', CELL_SIZE)
        self.background_color = pygame.Color(0, 0, 0)
        self.font_color = pygame.Color(255, 255, 255)
        self.circle_color = pygame.Color(255, 255, 255)
        self.goal_color = pygame.Color(0, 255, 0)
        self.ray_color = pygame.Color(150, 150, 150)
        self.wall_color = pygame.Color(255, 255, 255)
        self.trace_color = pygame.Color(255, 0, 0)
        
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()

        self.goal_text = self.my_font.render(f"You reached the Goal!", False, self.font_color)
        self.goal_text_rect = self.goal_text.get_rect(center=(SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2))

        self.new_game_button_text = self.my_font.render("New Game", False, self.font_color)
        self.new_game_button = self.new_game_button_text.get_rect(center=(SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2 + CELL_SIZE + 10))

        self.circle_radius = CELL_SIZE / 4

    def reset(self):
        """Reset game state and generate new random labyrinth.
        """
        self.goal = pygame.Vector2(random.randint(0, WIDTH - 1) + 0.5, random.randint(0, HEIGHT - 1) + 0.5) * CELL_SIZE
        self.position = pygame.Vector2(random.randint(0, WIDTH - 1) + 0.5, random.randint(0, HEIGHT - 1) + 0.5) * CELL_SIZE
        self.walls = generate_labyrinth()
        self.rays = RayTracing(self.walls, RAYS)
        self.trace = []
        self.reached_goal = False

    def get_fps(self) -> int:
        return int(self.clock.get_fps())

    def run(self):
        self.reset()

        running = True
        while running:
            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.reached_goal and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Start new game
                    if self.new_game_button.collidepoint(event.pos):
                        self.reset()

            # Clear screen
            self.screen.fill(self.background_color)

            # Draw walls
            # for wall in self.walls:
            #     pygame.draw.line(self.screen, (180, 180, 180), wall[0], wall[1], 2)

            # Get target direction
            mouse_position = pygame.Vector2(pygame.mouse.get_pos())
            direction = mouse_position - self.position

            # Check if target direction collides with wall and reduce direction vector
            intersection = self.rays.get_wall_collision(self.position, direction)
            if intersection is not None and intersection != self.position:
                pygame.draw.circle(self.screen, pygame.Color(255, 0, 0), intersection, 2)
                # Move the position to the intersection
                direction = intersection - self.position
                direction.scale_to_length(direction.length() - self.circle_radius)
            
            # Move to next position
            self.position = self.position + direction.normalize() * direction.length() * 0.1

            # Store position in Trace
            if len(self.trace) == 0 or (self.position - self.trace[-1]).length_squared() > self.circle_radius**2:
                self.trace.append(self.position)

            # Calculate ray-wall intersections and draw rays
            intersections = self.rays.get_ray_intersections(self.position)
            for intersection in intersections:
                pygame.draw.line(self.screen, self.ray_color, self.position, intersection, 1)

            # Draw goal and player
            pygame.draw.circle(self.screen, self.goal_color, self.goal, self.circle_radius)
            pygame.draw.circle(self.screen, self.circle_color, self.position, self.circle_radius)

            # Check if player reached the goal
            if (self.goal - self.position).length_squared() < self.circle_radius**2:
                self.reached_goal = True

            # Display walls and trace when player reached the goal
            # Enable new game button
            if self.reached_goal:
                for wall in self.walls:
                    pygame.draw.line(self.screen, self.wall_color, wall[0], wall[1], 2)
                for i in range(1, len(self.trace)):
                    pygame.draw.line(self.screen, self.trace_color, self.trace[i - 1], self.trace[i], 2)
                self.screen.blit(self.goal_text, self.goal_text_rect)
                self.screen.blit(self.new_game_button_text, self.new_game_button)

            # Add FPS Overlay
            fps_text = self.my_font.render(f"{self.get_fps()} FPS", False, self.font_color)
            self.screen.blit(fps_text, (0,0))

            # Flip screen
            pygame.display.flip()
            self.clock.tick(FPS_LIMIT)

        pygame.quit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
