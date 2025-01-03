import pygame
import pygame.gfxdraw
from enum import Enum
from typing import List, Tuple

# ПАРАМЕТРЫ ОКНА И СЕТКИ
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
GRID_SIZE = 50
INFO_PANEL_WIDTH = 400

# НОВАЯ ЦВЕТОВАЯ СХЕМА
BACKGROUND = (32, 32, 32)      # Фон основного поля
GRID_COLOR = (60, 60, 60)      # Сетка
AXIS_COLOR = (200, 80, 80)     # Оси координат, границы окна отсечения
WINDOW_COLOR = (45, 45, 45)    # Прямоугольник окна отсечения
SHAPE_COLOR = (80, 220, 120)   # Отрисовка отрезков
POLYGON_COLOR = (70, 150, 230) # Отрисовка многоугольников
CLIPPED_COLOR = (255, 200, 50) # Цвет отсечённых фигур
PANEL_COLOR = (40, 40, 50)     # Фон панели справа
TEXT_COLOR = (220, 220, 220)   # Текст

class Mode(Enum):
    LINE = 1
    POLYGON = 2

class State(Enum):
    DRAWING = 1
    WINDOW_CREATION = 2

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        # Меняем заголовок окна (можно дополнить уточнением “Обновлённый интерфейс”):
        pygame.display.set_caption("Алгоритм Коэна-Сазерленда (Обновлённый интерфейс)")
        self.clock = pygame.time.Clock()
        # Изменяем шрифт и размер на что-то более читаемое:
        self.font = pygame.font.SysFont("Arial", 20)

        self.mode = Mode.LINE
        self.state = State.DRAWING
        self.temp_point = None
        self.current_line = []
        self.current_polygon = []
        self.shapes = []
        self.clipping_window = None
        self.window_start = None
        self.clipped_shapes = []
        self.show_grid = True
        self.creating_window = False
        self.window_mode = False

    def draw_grid(self):
        """
        Отрисовка сетки и осей координат.
        """
        if not self.show_grid:
            return

        # Вертикальные и горизонтальные линии сетки:
        for x in range(0, WINDOW_WIDTH - INFO_PANEL_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH - INFO_PANEL_WIDTH, y))

        # Оси X и Y:
        mid_x = (WINDOW_WIDTH - INFO_PANEL_WIDTH) // 2
        mid_y = WINDOW_HEIGHT // 2
        pygame.draw.line(self.screen, AXIS_COLOR, (0, mid_y), (WINDOW_WIDTH - INFO_PANEL_WIDTH, mid_y), 2)
        pygame.draw.line(self.screen, AXIS_COLOR, (mid_x, 0), (mid_x, WINDOW_HEIGHT), 2)

        # Подписи на осях X и Y:
        for i in range(-10, 11):
            if i != 0:
                x_pos = mid_x + (i * GRID_SIZE)
                label_x = self.font.render(str(i), True, TEXT_COLOR)
                self.screen.blit(label_x, (x_pos - 10, mid_y + 5))

                y_pos = mid_y - (i * GRID_SIZE)
                label_y = self.font.render(str(i), True, TEXT_COLOR)
                self.screen.blit(label_y, (mid_x + 5, y_pos - 10))

    def draw_info_panel(self):
        """
        Отрисовка панели с информацией и подсказками управления.
        """
        panel_rect = pygame.Rect(WINDOW_WIDTH - INFO_PANEL_WIDTH, 0, INFO_PANEL_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel_rect)
        pygame.draw.line(self.screen, AXIS_COLOR,
                         (WINDOW_WIDTH - INFO_PANEL_WIDTH, 0),
                         (WINDOW_WIDTH - INFO_PANEL_WIDTH, WINDOW_HEIGHT), 3)

        mode_text = f"Режим: {'Многоугольник' if self.mode == Mode.POLYGON else 'Линия'}"
        window_mode_text = f"Окно: {'Включено' if self.window_mode else 'Выключено'}"
        state_text = f"Состояние: {'Рисование' if self.state == State.DRAWING else 'Создание окна'}"
        mode_surface = self.font.render(mode_text, True, TEXT_COLOR)
        window_mode_surface = self.font.render(window_mode_text, True, TEXT_COLOR)
        state_surface = self.font.render(state_text, True, TEXT_COLOR)

        self.screen.blit(mode_surface, (WINDOW_WIDTH - INFO_PANEL_WIDTH + 20, 20))
        self.screen.blit(window_mode_surface, (WINDOW_WIDTH - INFO_PANEL_WIDTH + 20, 50))
        self.screen.blit(state_surface, (WINDOW_WIDTH - INFO_PANEL_WIDTH + 20, 80))

        controls = [
            "Управление:",
            "M    - Сменить режим (линия/многоуг.)",
            "W    - Вкл/выкл создание окна",
            "Space - Замкнуть многоугольник",
            "Enter - Отсечь все фигуры",
            "Backspace - Удалить последнюю точку",
            "Delete    - Удалить последнюю фигуру",
            "C    - Сбросить окно отсечения",
            "G    - Показать/скрыть сетку",
            "ESC  - Очистить всё",
        ]

        y_offset = 120
        for control in controls:
            control_surface = self.font.render(control, True, TEXT_COLOR)
            self.screen.blit(control_surface, (WINDOW_WIDTH - INFO_PANEL_WIDTH + 20, y_offset))
            y_offset += 30

    def compute_outcode(self, x: float, y: float) -> int:
        """
        Вычисление кода положения точки (x, y) относительно окна отсечения.
        """
        if not self.clipping_window:
            return 0
        code = 0
        xmin, ymin, xmax, ymax = self.clipping_window

        if x < xmin:
            code |= 1
        elif x > xmax:
            code |= 2
        if y < ymin:
            code |= 4
        elif y > ymax:
            code |= 8

        return code

    def cohen_sutherland_clip(self, x1: float, y1: float, x2: float, y2: float) -> Tuple[bool, float, float, float, float]:
        """
        Алгоритм отсечения отрезка (x1,y1)-(x2,y2) окном по Коэну-Сазерленду.
        Возвращает (accept, x1, y1, x2, y2).
        """
        if not self.clipping_window:
            return False, x1, y1, x2, y2

        xmin, ymin, xmax, ymax = self.clipping_window
        outcode1 = self.compute_outcode(x1, y1)
        outcode2 = self.compute_outcode(x2, y2)
        accept = False

        while True:
            if not (outcode1 | outcode2):
                # Полностью внутри
                accept = True
                break
            elif outcode1 & outcode2:
                # Полностью вне
                break
            else:
                # Есть частичное пересечение
                outcode_out = outcode1 if outcode1 else outcode2

                if outcode_out & 8:  # Точка выше окна
                    x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                    y = ymax
                elif outcode_out & 4:  # Точка ниже окна
                    x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                    y = ymin
                elif outcode_out & 2:  # Точка справа
                    y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                    x = xmax
                else:  # outcode_out & 1, Точка слева
                    y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                    x = xmin

                if outcode_out == outcode1:
                    x1, y1 = x, y
                    outcode1 = self.compute_outcode(x1, y1)
                else:
                    x2, y2 = x, y
                    outcode2 = self.compute_outcode(x2, y2)

        return accept, x1, y1, x2, y2

    def clip_polygon(self, polygon: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Отсечение многоугольника алгоритмом Клипа–Коэна (Sutherland–Hodgman).
        """
        def inside(p: Tuple[float, float], cp1: Tuple[float, float], cp2: Tuple[float, float]) -> bool:
            return (cp2[0] - cp1[0]) * (p[1] - cp1[1]) > (cp2[1] - cp1[1]) * (p[0] - cp1[0])

        def compute_intersection(p1: Tuple[float, float], p2: Tuple[float, float],
                                 cp1: Tuple[float, float], cp2: Tuple[float, float]) -> Tuple[float, float]:
            dc = (cp1[0] - cp2[0], cp1[1] - cp2[1])
            dp = (p1[0] - p2[0], p1[1] - p2[1])
            n1 = cp1[0] * cp2[1] - cp1[1] * cp2[0]
            n2 = p1[0] * p2[1] - p1[1] * p2[0]
            n3 = 1.0 / (dc[0] * dp[1] - dc[1] * dp[0])
            return ((n1 * dp[0] - n2 * dc[0]) * n3, (n1 * dp[1] - n2 * dc[1]) * n3)

        if not self.clipping_window:
            return polygon

        output_polygon = polygon
        xmin, ymin, xmax, ymax = self.clipping_window
        clip_polygon = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]

        for i in range(len(clip_polygon)):
            cp1 = clip_polygon[i]
            cp2 = clip_polygon[(i + 1) % len(clip_polygon)]

            input_polygon = output_polygon
            output_polygon = []

            if not input_polygon:
                break

            s = input_polygon[-1]
            for e in input_polygon:
                if inside(e, cp1, cp2):
                    if not inside(s, cp1, cp2):
                        output_polygon.append(compute_intersection(s, e, cp1, cp2))
                    output_polygon.append(e)
                elif inside(s, cp1, cp2):
                    output_polygon.append(compute_intersection(s, e, cp1, cp2))
                s = e

        return output_polygon

    def clip_shapes(self):
        """
        Запуск отсечения для всех нарисованных фигур (отрезков и многоугольников).
        """
        self.clipped_shapes = []
        for shape in self.shapes:
            # Отрезки (2 точки)
            if len(shape) == 2:
                accept, x1, y1, x2, y2 = self.cohen_sutherland_clip(shape[0][0], shape[0][1],
                                                                    shape[1][0], shape[1][1])
                if accept:
                    self.clipped_shapes.append([(x1, y1), (x2, y2)])
            # Многоугольники
            else:
                clipped = self.clip_polygon(shape)
                if clipped:
                    self.clipped_shapes.append(clipped)

    def handle_mouse_click(self, pos):
        x, y = pos
        # Игнорируем клики в области панели:
        if x >= WINDOW_WIDTH - INFO_PANEL_WIDTH:
            return

        # Создание окна отсечения
        if self.window_mode and not self.creating_window:
            self.window_start = pos
            self.creating_window = True
            self.state = State.WINDOW_CREATION
            return

        # Рисование фигур
        if self.state == State.DRAWING:
            if self.mode == Mode.LINE:
                if not self.current_line:
                    self.current_line = [pos]
                else:
                    self.current_line.append(pos)
                    self.shapes.append(self.current_line)
                    self.current_line = []
            else:
                # Режим многоугольника
                self.current_polygon.append(pos)

    def handle_mouse_up(self, pos):
        # Завершение создания окна отсечения
        if self.creating_window and self.window_start:
            x, y = pos
            x1, y1 = self.window_start
            if x < WINDOW_WIDTH - INFO_PANEL_WIDTH:
                self.clipping_window = (min(x1, x), min(y1, y), max(x1, x), max(y1, y))
                self.clipped_shapes = []
                self.creating_window = False
                self.window_start = None

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    # Смена режима рисования (линия/многоугольник)
                    if event.key == pygame.K_m and self.state == State.DRAWING:
                        self.mode = Mode.POLYGON if self.mode == Mode.LINE else Mode.LINE
                        self.current_line = []
                        self.current_polygon = []

                    # Режим окна отсечения
                    elif event.key == pygame.K_w:
                        self.window_mode = not self.window_mode
                        if not self.window_mode:
                            self.creating_window = False
                            self.window_start = None
                            self.state = State.DRAWING

                    # Замыкание многоугольника (пробел)
                    elif event.key == pygame.K_SPACE and self.mode == Mode.POLYGON:
                        if len(self.current_polygon) == 2:
                            self.shapes.append(self.current_polygon)
                            self.current_polygon = []
                        elif len(self.current_polygon) > 2:
                            self.shapes.append(self.current_polygon)
                            self.current_polygon = []

                    # Отсечение (Enter)
                    elif event.key == pygame.K_RETURN and self.clipping_window:
                        self.clip_shapes()

                    # Удаление последней точки (Backspace)
                    elif event.key == pygame.K_BACKSPACE:
                        if self.current_polygon:
                            self.current_polygon.pop()

                    # Удаление последней фигуры (Delete)
                    elif event.key == pygame.K_DELETE:
                        if self.shapes:
                            self.shapes.pop()

                    # Сброс окна отсечения (C)
                    elif event.key == pygame.K_c:
                        self.clipping_window = None
                        self.clipped_shapes = []
                        self.state = State.DRAWING

                    # Показать/скрыть сетку (G)
                    elif event.key == pygame.K_g:
                        self.show_grid = not self.show_grid

                    # Очистить всё (ESC)
                    elif event.key == pygame.K_ESCAPE:
                        self.shapes = []
                        self.current_line = []
                        self.current_polygon = []
                        self.clipped_shapes = []
                        self.clipping_window = None
                        self.state = State.DRAWING
                        self.creating_window = False
                        self.window_mode = False
                        self.window_start = None

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_mouse_click(event.pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.handle_mouse_up(event.pos)

            # Заливка фона
            self.screen.fill(BACKGROUND)

            # Сетка
            self.draw_grid()

            # Уже созданное окно отсечения
            if self.clipping_window:
                x, y, w, h = self.clipping_window
                window_rect = pygame.Rect(x, y, w - x, h - y)
                pygame.draw.rect(self.screen, WINDOW_COLOR, window_rect)
                pygame.draw.rect(self.screen, AXIS_COLOR, window_rect, 2)

            # Процесс создания окна отсечения (рисуем прямоугольник следом за мышкой)
            if self.creating_window and self.window_start:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] < WINDOW_WIDTH - INFO_PANEL_WIDTH:
                    x1, y1 = self.window_start
                    x2, y2 = mouse_pos
                    rect = pygame.Rect(min(x1, x2), min(y1, y2),
                                       abs(x2 - x1), abs(y2 - y1))
                    pygame.draw.rect(self.screen, WINDOW_COLOR, rect)
                    pygame.draw.rect(self.screen, AXIS_COLOR, rect, 2)

            # Отрисовка уже готовых фигур (линий или многоугольников)
            for shape in self.shapes:
                color = POLYGON_COLOR if len(shape) > 2 else SHAPE_COLOR
                pygame.draw.lines(self.screen, color, len(shape) > 2, shape, 3)

            # Текущий отрезок, рисуем “на лету”
            if self.current_line:
                temp_line = self.current_line + [pygame.mouse.get_pos()]
                pygame.draw.lines(self.screen, SHAPE_COLOR, False, temp_line, 3)

            # Текущий многоугольник, рисуем “на лету”
            if self.current_polygon:
                points = self.current_polygon + [pygame.mouse.get_pos()]
                pygame.draw.lines(self.screen, POLYGON_COLOR, False, points, 3)
                for point in self.current_polygon:
                    pygame.draw.circle(self.screen, POLYGON_COLOR, point, 5)

            # Отсечённые фигуры
            for shape in self.clipped_shapes:
                pygame.draw.lines(self.screen, CLIPPED_COLOR, len(shape) > 2, shape, 3)

            # Информационная панель справа
            self.draw_info_panel()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    app = App()
    app.run()
