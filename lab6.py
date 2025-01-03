import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


base_vertices = {
    # Передняя грань
    'A': (0, 0, 0),  # Нижний левый угол
    'A1': (0, 0, 6),  # Верхний левый угол
    'B': (4, 0, 6),  # Верхняя правая часть верхней петли
    'B1': (4, 0, 4),  # Правая часть средней линии
    'C': (4, 0, 0),  # Нижняя правая часть
    'D': (0, 0, 4),  # Центральная левая точка
    'E': (4, 0, 2),  # Правая часть нижней петли
    'F': (0, 0, 2),  # Центральная левая точка нижней петли

    # Задняя грань
    'A_back': (0, -2, 0),
    'A1_back': (0, -2, 6),
    'B_back': (4, -2, 6),
    'B1_back': (4, -2, 4),
    'C_back': (4, -2, 0),
    'D_back': (0, -2, 4),
    'E_back': (4, -2, 2),
    'F_back': (0, -2, 2),
}

# Обновленные рёбра для объемной буквы "Б"
edges = [
    # Передняя грань
    ('A', 'A1'),
    ('A1', 'B'),
    ('B', 'B1'),
    ('B1', 'D'),
    ('D', 'F'),
    ('F', 'E'),
    ('E', 'C'),
    ('C', 'A'),

    # Задняя грань
    ('A_back', 'A1_back'),
    ('A1_back', 'B_back'),
    ('B_back', 'B1_back'),
    ('B1_back', 'D_back'),
    ('D_back', 'F_back'),
    ('F_back', 'E_back'),
    ('E_back', 'C_back'),
    ('C_back', 'A_back'),

    # Соединяющие рёбра между передней и задней гранями
    ('A', 'A_back'),
    ('A1', 'A1_back'),
    ('B', 'B_back'),
    ('B1', 'B1_back'),
    ('C', 'C_back'),
    ('D', 'D_back'),
    ('E', 'E_back'),
    ('F', 'F_back'),
]




def create_scaling_matrix(sx, sy, sz):

    return np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ])


def create_translation_matrix(tx, ty, tz):

    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ])


def create_rotation_matrix_x(theta):
    theta = np.radians(theta)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    return np.array([
        [1, 0, 0, 0],
        [0, cos_t, -sin_t, 0],
        [0, sin_t, cos_t, 0],
        [0, 0, 0, 1]
    ])


def create_rotation_matrix_y(theta):

    theta = np.radians(theta)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    return np.array([
        [cos_t, 0, sin_t, 0],
        [0, 1, 0, 0],
        [-sin_t, 0, cos_t, 0],
        [0, 0, 0, 1]
    ])


def create_rotation_matrix_z(theta):

    theta = np.radians(theta)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    return np.array([
        [cos_t, -sin_t, 0, 0],
        [sin_t, cos_t, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])


def apply_transformation(vertices, transformation_matrix):

    transformed = {}
    for label, (x, y, z) in vertices.items():
        vec = np.array([x, y, z, 1])
        transformed_vec = transformation_matrix @ vec
        transformed[label] = (transformed_vec[0], transformed_vec[1], transformed_vec[2])
    return transformed


def plot_wireframe(ax, vertices, title='Трехмерная каркасная модель'):

    ax.cla()


    for edge in edges:
        start, end = edge
        x_vals = [vertices[start][0], vertices[end][0]]
        y_vals = [vertices[start][1], vertices[end][1]]
        z_vals = [vertices[start][2], vertices[end][2]]
        ax.plot(x_vals, y_vals, z_vals, color='b')


    for label, (x, y, z) in vertices.items():
        ax.scatter(x, y, z, color='r')
        ax.text(x, y, z, f' {label}', size=10, zorder=1, color='k')


    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')


    all_coords = np.array(list(vertices.values()))
    max_range = np.max(all_coords, axis=0) - np.min(all_coords, axis=0)
    max_range = max(max_range) / 2 * 1.2

    mid_x = (np.max(all_coords[:, 0]) + np.min(all_coords[:, 0])) * 0.5
    mid_y = (np.max(all_coords[:, 1]) + np.min(all_coords[:, 1])) * 0.5
    mid_z = (np.max(all_coords[:, 2]) + np.min(all_coords[:, 2])) * 0.5

    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)


    ax.grid(True)

    ax.set_title(title)


class WireframeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Каркасная Модель с Преобразованиями")


        self.scale_x = tk.DoubleVar(value=1.0)
        self.scale_y = tk.DoubleVar(value=1.0)
        self.scale_z = tk.DoubleVar(value=1.0)
        self.translate_x = tk.DoubleVar(value=0.0)
        self.translate_y = tk.DoubleVar(value=0.0)
        self.translate_z = tk.DoubleVar(value=0.0)
        self.rotation_x = tk.DoubleVar(value=0.0)
        self.rotation_y = tk.DoubleVar(value=0.0)
        self.rotation_z = tk.DoubleVar(value=0.0)


        self.create_widgets()


        self.transformed_vertices = apply_transformation(base_vertices, np.identity(4))


        self.update_plot()

    def create_widgets(self):

        top_frame = ttk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


        plot_frame = ttk.Frame(top_frame)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        self.fig = plt.Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')


        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


        matrix_frame = ttk.Frame(top_frame)
        matrix_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)


        matrix_label = ttk.Label(matrix_frame, text="Итоговая Матрица Преобразований:")
        matrix_label.pack(anchor=tk.NW)


        self.matrix_text = scrolledtext.ScrolledText(matrix_frame, width=30, height=15, font=("Courier", 10))
        self.matrix_text.pack(fill=tk.BOTH, expand=True)
        self.matrix_text.configure(state='disabled')


        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)


        scaling_frame = ttk.LabelFrame(bottom_frame, text="Масштабирование")
        scaling_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)


        self.scale_x_label = ttk.Label(scaling_frame, text="Scale X: 1.0")
        self.scale_x_label.pack(anchor=tk.W)
        self.scale_x_slider = ttk.Scale(scaling_frame, from_=0.1, to=3.0, orient=tk.HORIZONTAL, variable=self.scale_x,
                                        command=lambda e: self.update_plot())
        self.scale_x_slider.pack(fill=tk.X, padx=5)
        self.scale_x.trace('w', lambda *args: self.update_label('scale_x'))


        self.scale_y_label = ttk.Label(scaling_frame, text="Scale Y: 1.0")
        self.scale_y_label.pack(anchor=tk.W)
        self.scale_y_slider = ttk.Scale(scaling_frame, from_=0.1, to=3.0, orient=tk.HORIZONTAL, variable=self.scale_y,
                                        command=lambda e: self.update_plot())
        self.scale_y_slider.pack(fill=tk.X, padx=5)
        self.scale_y.trace('w', lambda *args: self.update_label('scale_y'))


        self.scale_z_label = ttk.Label(scaling_frame, text="Scale Z: 1.0")
        self.scale_z_label.pack(anchor=tk.W)
        self.scale_z_slider = ttk.Scale(scaling_frame, from_=0.1, to=3.0, orient=tk.HORIZONTAL, variable=self.scale_z,
                                        command=lambda e: self.update_plot())
        self.scale_z_slider.pack(fill=tk.X, padx=5)
        self.scale_z.trace('w', lambda *args: self.update_label('scale_z'))


        translation_frame = ttk.LabelFrame(bottom_frame, text="Перенос")
        translation_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)


        self.translate_x_label = ttk.Label(translation_frame, text="Translate X: 0.0")
        self.translate_x_label.pack(anchor=tk.W)
        self.translate_x_slider = ttk.Scale(translation_frame, from_=-10.0, to=10.0, orient=tk.HORIZONTAL,
                                            variable=self.translate_x, command=lambda e: self.update_plot())
        self.translate_x_slider.pack(fill=tk.X, padx=5)
        self.translate_x.trace('w', lambda *args: self.update_label('translate_x'))


        self.translate_y_label = ttk.Label(translation_frame, text="Translate Y: 0.0")
        self.translate_y_label.pack(anchor=tk.W)
        self.translate_y_slider = ttk.Scale(translation_frame, from_=-10.0, to=10.0, orient=tk.HORIZONTAL,
                                            variable=self.translate_y, command=lambda e: self.update_plot())
        self.translate_y_slider.pack(fill=tk.X, padx=5)
        self.translate_y.trace('w', lambda *args: self.update_label('translate_y'))

        self.translate_z_label = ttk.Label(translation_frame, text="Translate Z: 0.0")
        self.translate_z_label.pack(anchor=tk.W)
        self.translate_z_slider = ttk.Scale(translation_frame, from_=-10.0, to=10.0, orient=tk.HORIZONTAL,
                                            variable=self.translate_z, command=lambda e: self.update_plot())
        self.translate_z_slider.pack(fill=tk.X, padx=5)
        self.translate_z.trace('w', lambda *args: self.update_label('translate_z'))


        rotation_frame = ttk.LabelFrame(bottom_frame, text="Вращение")
        rotation_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)


        self.rotation_x_label = ttk.Label(rotation_frame, text="Rotate X (°): 0.0")
        self.rotation_x_label.pack(anchor=tk.W)
        self.rotation_x_slider = ttk.Scale(rotation_frame, from_=0.0, to=360.0, orient=tk.HORIZONTAL,
                                           variable=self.rotation_x, command=lambda e: self.update_plot())
        self.rotation_x_slider.pack(fill=tk.X, padx=5)
        self.rotation_x.trace('w', lambda *args: self.update_label('rotation_x'))


        self.rotation_y_label = ttk.Label(rotation_frame, text="Rotate Y (°): 0.0")
        self.rotation_y_label.pack(anchor=tk.W)
        self.rotation_y_slider = ttk.Scale(rotation_frame, from_=0.0, to=360.0, orient=tk.HORIZONTAL,
                                           variable=self.rotation_y, command=lambda e: self.update_plot())
        self.rotation_y_slider.pack(fill=tk.X, padx=5)
        self.rotation_y.trace('w', lambda *args: self.update_label('rotation_y'))

        self.rotation_z_label = ttk.Label(rotation_frame, text="Rotate Z (°): 0.0")
        self.rotation_z_label.pack(anchor=tk.W)
        self.rotation_z_slider = ttk.Scale(rotation_frame, from_=0.0, to=360.0, orient=tk.HORIZONTAL,
                                           variable=self.rotation_z, command=lambda e: self.update_plot())
        self.rotation_z_slider.pack(fill=tk.X, padx=5)
        self.rotation_z.trace('w', lambda *args: self.update_label('rotation_z'))


        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)


        self.refresh_button = ttk.Button(button_frame, text="Обновить", command=self.update_plot)
        self.refresh_button.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)


        self.reset_button = ttk.Button(button_frame, text="Сбросить", command=self.reset_transformations)
        self.reset_button.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)


        self.projections_button = ttk.Button(button_frame, text="Показать проекции", command=self.show_projections)
        self.projections_button.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)


        self.quit_button = ttk.Button(button_frame, text="Выход", command=self.root.quit)
        self.quit_button.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

    def update_label(self, param):

        if param == 'scale_x':
            self.scale_x_label.config(text=f"Scale X: {self.scale_x.get():.2f}")
        elif param == 'scale_y':
            self.scale_y_label.config(text=f"Scale Y: {self.scale_y.get():.2f}")
        elif param == 'scale_z':
            self.scale_z_label.config(text=f"Scale Z: {self.scale_z.get():.2f}")
        elif param == 'translate_x':
            self.translate_x_label.config(text=f"Translate X: {self.translate_x.get():.2f}")
        elif param == 'translate_y':
            self.translate_y_label.config(text=f"Translate Y: {self.translate_y.get():.2f}")
        elif param == 'translate_z':
            self.translate_z_label.config(text=f"Translate Z: {self.translate_z.get():.2f}")
        elif param == 'rotation_x':
            self.rotation_x_label.config(text=f"Rotate X (°): {self.rotation_x.get():.1f}")
        elif param == 'rotation_y':
            self.rotation_y_label.config(text=f"Rotate Y (°): {self.rotation_y.get():.1f}")
        elif param == 'rotation_z':
            self.rotation_z_label.config(text=f"Rotate Z (°): {self.rotation_z.get():.1f}")

    def reset_transformations(self):

        self.scale_x.set(1.0)
        self.scale_y.set(1.0)
        self.scale_z.set(1.0)
        self.translate_x.set(0.0)
        self.translate_y.set(0.0)
        self.translate_z.set(0.0)
        self.rotation_x.set(0.0)
        self.rotation_y.set(0.0)
        self.rotation_z.set(0.0)
        self.update_plot()

    def update_plot(self):

        S = create_scaling_matrix(self.scale_x.get(), self.scale_y.get(), self.scale_z.get())
        Rx = create_rotation_matrix_x(self.rotation_x.get())
        Ry = create_rotation_matrix_y(self.rotation_y.get())
        Rz = create_rotation_matrix_z(self.rotation_z.get())
        T = create_translation_matrix(self.translate_x.get(), self.translate_y.get(), self.translate_z.get())


        total_matrix = T @ Rz @ Ry @ Rx @ S


        self.transformed_vertices = apply_transformation(base_vertices, total_matrix)


        plot_wireframe(self.ax, self.transformed_vertices)
        self.canvas.draw()


        self.display_transformation_matrix(total_matrix)

    def display_transformation_matrix(self, matrix):

        self.matrix_text.configure(state='normal')
        self.matrix_text.delete('1.0', tk.END)
        formatted_matrix = np.array2string(matrix, formatter={'float_kind': lambda x: f"{x: .3f}"})
        self.matrix_text.insert(tk.END, formatted_matrix)
        self.matrix_text.configure(state='disabled')

    def show_projections(self):

        if not hasattr(self, 'transformed_vertices'):
            transformed = apply_transformation(base_vertices, np.identity(4))
        else:
            transformed = self.transformed_vertices


        proj_window = tk.Toplevel(self.root)
        proj_window.title("Ортографические проекции")


        fig, axs = plt.subplots(1, 3, figsize=(15, 5))

        plot_projection(axs[0], transformed, projection='Oxy')


        plot_projection(axs[1], transformed, projection='Oxz')


        plot_projection(axs[2], transformed, projection='Oyz')

        fig.tight_layout()


        canvas = FigureCanvasTkAgg(fig, master=proj_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def plot_projection(ax, vertices, projection='Oxy'):

    ax.cla()


    if projection == 'Oxy':

        proj_vertices = {label: (x, y) for label, (x, y, z) in vertices.items()}
        xlabel, ylabel = 'X', 'Y'
    elif projection == 'Oxz':

        proj_vertices = {label: (x, z) for label, (x, y, z) in vertices.items()}
        xlabel, ylabel = 'X', 'Z'
    elif projection == 'Oyz':

        proj_vertices = {label: (y, z) for label, (x, y, z) in vertices.items()}
        xlabel, ylabel = 'Y', 'Z'
    else:
        raise ValueError("Неверный тип проекции. Используйте 'Oxy', 'Oxz' или 'Oyz'.")


    edges_2d = [
        (start, end) for start, end in edges
        if start in proj_vertices and end in proj_vertices
    ]


    for edge in edges_2d:
        start, end = edge
        x_vals = [proj_vertices[start][0], proj_vertices[end][0]]
        y_vals = [proj_vertices[start][1], proj_vertices[end][1]]
        ax.plot(x_vals, y_vals, color='b')


    for label, (x, y) in proj_vertices.items():
        ax.scatter(x, y, color='r')
        ax.text(x, y, f' {label}', size=8, zorder=1, color='k')


    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


    all_coords = np.array(list(proj_vertices.values()))
    max_range = np.max(all_coords, axis=0) - np.min(all_coords, axis=0)
    max_range = max(max_range) / 2 * 1.2

    mid_x = (np.max(all_coords[:, 0]) + np.min(all_coords[:, 0])) * 0.5
    mid_y = (np.max(all_coords[:, 1]) + np.min(all_coords[:, 1])) * 0.5

    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)


    ax.grid(True)


    ax.set_title(f'Проекция на {projection}')



def main():
    root = tk.Tk()
    app = WireframeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
