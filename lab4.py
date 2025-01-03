import pygame
import math
import time
from typing import List, Tuple
import numpy as np

pygame.init()

# Настройки экрана
WIDTH = 1200
HEIGHT = 800
CELL_SIZE = 20
GRID_COLOR = (220, 220, 220)
AXIS_COLOR = (50, 50, 50)
TEXT_COLOR = (30, 30, 30)
POINT_COLOR = (0, 0, 0)
LINE_COLOR = (0, 0, 0)
BACKGROUND = (245, 245, 245)

# Настройки кнопок
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (170, 170, 170)
BUTTON_ACTIVE_COLOR = (100, 149, 237)  # Cornflower Blue

FONT_NAME = pygame.font.match_font('arial')

class Button:
    def __init__(self, text, x, y, width, height, algorithm):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.algorithm = algorithm
        self.color = BUTTON_COLOR
        self.hover = False
        self.active = False
        self.font = pygame.font.Font(FONT_NAME, 20)
    
    def draw(self, screen):
        # Изменение цвета при наведении и активном состоянии
        if self.active:
            color = BUTTON_ACTIVE_COLOR
        elif self.hover:
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR
        
        # Рисование закругленного прямоугольника
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        # Рендеринг текста
        text_surf = self.font.render(self.text, True, (255, 255, 255) if self.active else TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def handle_event(self, event, current_algorithm):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.algorithm == 'clear':
                    return 'clear'
                else:
                    return self.algorithm
        # Обновление состояния активности
        self.active = (current_algorithm == self.algorithm)
        return None

class RasterizationApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Растровые алгоритмы")
        self.font = pygame.font.Font(FONT_NAME, 20)
        self.clock = pygame.time.Clock()
        self.offset_x = WIDTH // 2
        self.offset_y = HEIGHT // 2
        self.start_point = None
        self.end_point = None
        self.is_drawing = False
        self.current_algorithm = "step"
        self.show_smoothed = False
        self.execution_time = 0
        self.buttons = self.create_buttons()
        self.drawn_lines = []
        self.drawn_points = []
    
    def create_buttons(self):
        buttons = []
        algorithms = [
            ('Step', 'step'),
            ('DDA', 'dda'),
            ('Bresenham', 'bresenham'),
            ('Circle', 'circle'),
            ('Castle-Pitway', 'castle'),
            ("Wu's Line", 'smooth'),
            ('Clear', 'clear')
        ]
        x = BUTTON_MARGIN
        y = BUTTON_MARGIN
        for text, algo in algorithms:
            button = Button(text, x, y, BUTTON_WIDTH, BUTTON_HEIGHT, algo)
            buttons.append(button)
            y += BUTTON_HEIGHT + BUTTON_MARGIN
        return buttons
    
    def clear(self):
        self.start_point = None
        self.end_point = None
        self.is_drawing = False
        self.execution_time = 0
        self.drawn_lines = []
        self.drawn_points = []
    
    def screen_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        return ((x - self.offset_x) // CELL_SIZE,
                (self.offset_y - y) // CELL_SIZE)
    
    def grid_to_screen(self, x: int, y: int) -> Tuple[int, int]:
        return (x * CELL_SIZE + self.offset_x,
                self.offset_y - y * CELL_SIZE)
    
    def draw_grid(self):
        self.screen.fill(BACKGROUND)
        
        # Рисование сетки
        for x in range(0, WIDTH, CELL_SIZE):
            color = GRID_COLOR if x != self.offset_x else AXIS_COLOR
            pygame.draw.line(self.screen, color, (x, 0), (x, HEIGHT))
            if x != self.offset_x and (x - self.offset_x) % (CELL_SIZE * 5) == 0:
                grid_x = (x - self.offset_x) // CELL_SIZE
                text = self.font.render(str(grid_x), True, TEXT_COLOR)
                self.screen.blit(text, (x - self.font.size(str(grid_x))[0] // 2, self.offset_y + 5))
        
        for y in range(0, HEIGHT, CELL_SIZE):
            color = GRID_COLOR if y != self.offset_y else AXIS_COLOR
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))
            if y != self.offset_y and (self.offset_y - y) % (CELL_SIZE * 5) == 0:
                grid_y = (self.offset_y - y) // CELL_SIZE
                text = self.font.render(str(grid_y), True, TEXT_COLOR)
                self.screen.blit(text, (self.offset_x + 5, y - self.font.get_height() // 2))
        
        # Рисование осей
        pygame.draw.line(self.screen, AXIS_COLOR, (self.offset_x, 0),
                         (self.offset_x, HEIGHT), 2)
        pygame.draw.line(self.screen, AXIS_COLOR, (0, self.offset_y),
                         (WIDTH, self.offset_y), 2)
    
    def draw_buttons(self):
        # Рисование боковой панели
        panel_width = BUTTON_WIDTH + 2 * BUTTON_MARGIN
        pygame.draw.rect(self.screen, (230, 230, 230), (0, 0, panel_width, HEIGHT))
        
        for button in self.buttons:
            button.draw(self.screen)
    
    def draw_coordinates(self):
        info_y = HEIGHT - 80
        padding = 10
        
        if self.start_point:
            start_text = f"Start: ({self.start_point[0]}, {self.start_point[1]})"
            text_surface = self.font.render(start_text, True, TEXT_COLOR)
            self.screen.blit(text_surface, (padding, info_y))
        
        if self.end_point:
            end_text = f"End: ({self.end_point[0]}, {self.end_point[1]})"
            text_surface = self.font.render(end_text, True, TEXT_COLOR)
            self.screen.blit(text_surface, (padding, info_y + 30))
        
        # Отображение времени выполнения, если есть
        if self.execution_time > 0:
            time_text = self.font.render(f"Time: {self.execution_time:.2f} µs", True, TEXT_COLOR)
            self.screen.blit(time_text, (padding, info_y + 60))
    
    def draw_pixel(self, pos: Tuple[int, int, float]):
        x, y, alpha = pos
        screen_x, screen_y = self.grid_to_screen(x, y)
        color = (*LINE_COLOR, int(255 * alpha))
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surface, color, (0, 0, CELL_SIZE, CELL_SIZE))
        self.screen.blit(surface, (screen_x, screen_y - CELL_SIZE))
    
    def step_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        points = []
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy))

        if steps == 0:
            return [(x0, y0, 1.0)]

        x_increment = dx / steps
        y_increment = dy / steps

        x, y = x0, y0
        for _ in range(steps + 1):
            points.append((round(x), round(y), 1.0))
            x += x_increment
            y += y_increment

        return points

    def dda_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        points = []
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy))

        if steps == 0:
            return [(x0, y0, 1.0)]

        x_increment = dx / steps
        y_increment = dy / steps

        x, y = x0, y0
        for _ in range(steps + 1):
            points.append((round(x), round(y), 1.0))
            x += x_increment
            y += y_increment

        return points

    def bresenham_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        x, y = x0, y0

        step_x = 1 if x1 > x0 else -1
        step_y = 1 if y1 > y0 else -1

        if dx > dy:
            err = dx / 2
            while x != x1:
                points.append((x, y, 1.0))
                err -= dy
                if err < 0:
                    y += step_y
                    err += dx
                x += step_x
        else:
            err = dy / 2
            while y != y1:
                points.append((x, y, 1.0))
                err -= dx
                if err < 0:
                    x += step_x
                    err += dy
                y += step_y

        points.append((x, y, 1.0))
        return points

    def bresenham_circle(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        points = []
        radius = int(math.hypot(x1 - x0, y1 - y0))
        x = radius
        y = 0
        err = 0

        while x >= y:
            points.extend([
                (x0 + x, y0 + y, 1.0), (x0 + y, y0 + x, 1.0),
                (x0 - y, y0 + x, 1.0), (x0 - x, y0 + y, 1.0),
                (x0 - x, y0 - y, 1.0), (x0 - y, y0 - x, 1.0),
                (x0 + y, y0 - x, 1.0), (x0 + x, y0 - y, 1.0)
            ])
            y += 1
            err += 1 + 2 * y
            if 2 * (err - x) + 1 > 0:
                x -= 1
                err += 1 - 2 * x

        return points

    def castle_pitway_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = y1 - y0
        derror = abs(dy / dx) if dx != 0 else 0
        error = 0
        y = y0

        for x in range(x0, x1 + 1):
            if steep:
                points.append((y, x, 1.0))
            else:
                points.append((x, y, 1.0))

            error += derror
            if error >= 0.5:
                y += 1 if y1 > y0 else -1
                error -= 1

        return points

    def wu_line_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        def plot(x: int, y: int, brightness: float) -> Tuple[int, int, float]:
            return x, y, brightness

        def ipart(x: float) -> int:
            return math.floor(x)

        def round_nearest(x: float) -> int:
            return ipart(x + 0.5)

        def fpart(x: float) -> float:
            return x - math.floor(x)

        def rfpart(x: float) -> float:
            return 1 - fpart(x)

        points = []

        if abs(y1 - y0) > abs(x1 - x0):
            steep = True
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        else:
            steep = False

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = y1 - y0
        gradient = dy / dx if dx != 0 else 1

        # Handle first endpoint
        xend = round_nearest(x0)
        yend = y0 + gradient * (xend - x0)
        xgap = rfpart(x0 + 0.5)
        xpxl1 = xend
        ypxl1 = ipart(yend)

        if steep:
            points.append(plot(ypxl1, xpxl1, rfpart(yend) * xgap))
            points.append(plot(ypxl1 + 1, xpxl1, fpart(yend) * xgap))
        else:
            points.append(plot(xpxl1, ypxl1, rfpart(yend) * xgap))
            points.append(plot(xpxl1, ypxl1 + 1, fpart(yend) * xgap))

        intery = yend + gradient

        # Handle second endpoint
        xend = round_nearest(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = fpart(x1 + 0.5)
        xpxl2 = xend
        ypxl2 = ipart(yend)

        if steep:
            points.append(plot(ypxl2, xpxl2, rfpart(yend) * xgap))
            points.append(plot(ypxl2 + 1, xpxl2, fpart(yend) * xgap))
        else:
            points.append(plot(xpxl2, ypxl2, rfpart(yend) * xgap))
            points.append(plot(xpxl2, ypxl2 + 1, fpart(yend) * xgap))

        # Main loop
        if steep:
            for x in range(xpxl1 + 1, xpxl2):
                y = ipart(intery)
                points.append(plot(y, x, rfpart(intery)))
                points.append(plot(y + 1, x, fpart(intery)))
                intery += gradient
        else:
            for x in range(xpxl1 + 1, xpxl2):
                y = ipart(intery)
                points.append(plot(x, y, rfpart(intery)))
                points.append(plot(x, y + 1, fpart(intery)))
                intery += gradient

        return points

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                for button in self.buttons:
                    result = button.handle_event(event, self.current_algorithm)
                    if result:
                        if result == 'clear':
                            self.clear()
                        else:
                            self.current_algorithm = result
                            self.start_point = None
                            self.end_point = None
                            self.is_drawing = False
                        break
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = event.pos
                        panel_width = BUTTON_WIDTH + 2 * BUTTON_MARGIN
                        if x > panel_width:
                            self.start_point = self.screen_to_grid(x, y)
                            self.is_drawing = True
                    elif event.type == pygame.MOUSEBUTTONUP and self.is_drawing:
                        x, y = event.pos
                        panel_width = BUTTON_WIDTH + 2 * BUTTON_MARGIN
                        if x > panel_width:
                            self.end_point = self.screen_to_grid(x, y)
                            self.is_drawing = False
                            
                            if self.start_point and self.end_point:
                                self.drawn_lines.append({
                                    'start': self.start_point,
                                    'end': self.end_point,
                                    'algorithm': self.current_algorithm
                                })
            
            self.draw_grid()
            self.draw_buttons()
            self.draw_coordinates()

            for line in self.drawn_lines:
                algorithm = line['algorithm']
                if algorithm == 'step':
                    points = self.step_algorithm(*line['start'], *line['end'])
                elif algorithm == 'dda':
                    points = self.dda_algorithm(*line['start'], *line['end'])
                elif algorithm == 'bresenham':
                    points = self.bresenham_algorithm(*line['start'], *line['end'])
                elif algorithm == 'circle':
                    points = self.bresenham_circle(*line['start'], *line['end'])
                elif algorithm == 'castle':
                    points = self.castle_pitway_algorithm(*line['start'], *line['end'])
                elif algorithm == 'smooth':
                    points = self.wu_line_algorithm(*line['start'], *line['end'])
                else:
                    points = []

                for point in points:
                    self.draw_pixel(point)

            if self.start_point and self.is_drawing:
                current_end = self.screen_to_grid(*pygame.mouse.get_pos())

                start_time = time.perf_counter()

                algorithm = self.current_algorithm
                if algorithm == 'step':
                    points = self.step_algorithm(*self.start_point, *current_end)
                elif algorithm == 'dda':
                    points = self.dda_algorithm(*self.start_point, *current_end)
                elif algorithm == 'bresenham':
                    points = self.bresenham_algorithm(*self.start_point, *current_end)
                elif algorithm == 'circle':
                    points = self.bresenham_circle(*self.start_point, *current_end)
                elif algorithm == 'castle':
                    points = self.castle_pitway_algorithm(*self.start_point, *current_end)
                elif algorithm == 'smooth':
                    points = self.wu_line_algorithm(*self.start_point, *current_end)
                else:
                    points = []

                for point in points:
                    self.draw_pixel(point)

                end_time = time.perf_counter()
                self.execution_time = (end_time - start_time) * 1_000_000  # в микросекундах

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == '__main__':
    app = RasterizationApp()
    app.run()
