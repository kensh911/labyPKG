import tkinter as tk
from tkinter import colorchooser, messagebox
from tkinter import ttk
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color

# Функции преобразования цветов
def rgb_to_cmyk(r, g, b):
    r, g, b = [x / 255.0 for x in (r, g, b)]
    k = 1 - max(r, g, b)
    if k == 1:
        return 0, 0, 0, 100
    c = (1 - r - k) / (1 - k) if (1 - k) != 0 else 0
    m = (1 - g - k) / (1 - k) if (1 - k) != 0 else 0
    y = (1 - b - k) / (1 - k) if (1 - k) != 0 else 0
    return round(c * 100), round(m * 100), round(y * 100), round(k * 100)

def cmyk_to_rgb(c, m, y, k):
    c, m, y, k = [x / 100.0 for x in (c, m, y, k)]
    r = 255 * (1 - c) * (1 - k)
    g = 255 * (1 - m) * (1 - k)
    b = 255 * (1 - y) * (1 - k)
    return int(round(r)), int(round(g)), int(round(b))

def rgb_to_lab(r, g, b):
    rgb_color = sRGBColor(r / 255.0, g / 255.0, b / 255.0)
    lab_color = convert_color(rgb_color, LabColor)
    return lab_color.lab_l, lab_color.lab_a, lab_color.lab_b

def lab_to_rgb(l, a, b):
    lab_color = LabColor(l, a, b)
    rgb_color = convert_color(lab_color, sRGBColor)
    r = rgb_color.clamped_rgb_r * 255
    g = rgb_color.clamped_rgb_g * 255
    b = rgb_color.clamped_rgb_b * 255
    return int(round(r)), int(round(g)), int(round(b))

# Основное приложение
class ColorConverterApp(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.title("Цветовое преобразование: RGB ↔ LAB ↔ CMYK")
        self.parent.geometry("600x700")
        self.parent.resizable(False, False)
        
        # Инициализация стилей
        self.style = ttk.Style(self.parent)
        self.style.theme_use('clam')  # Можно выбрать другую тему, например 'vista' или 'default'
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("TScale", background="#f0f0f0")
        
        self.updating = False  # Флаг для предотвращения рекурсии
        
        # Создание основного фрейма
        self.main_frame = ttk.Frame(self.parent, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Панель отображения цвета
        self.color_display = tk.Canvas(self.main_frame, width=580, height=100, bg="#FFFFFF", bd=2, relief=tk.SUNKEN)
        self.color_display.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # RGB Controls
        self.rgb_frame = ttk.LabelFrame(self.main_frame, text="RGB", padding="10")
        self.rgb_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)
        
        self.create_rgb_controls()
        
        # LAB Controls
        self.lab_frame = ttk.LabelFrame(self.main_frame, text="LAB", padding="10")
        self.lab_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=5)
        
        self.create_lab_controls()
        
        # CMYK Controls
        self.cmyk_frame = ttk.LabelFrame(self.main_frame, text="CMYK", padding="10")
        self.cmyk_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=5)
        
        self.create_cmyk_controls()
        
        # Кнопки
        self.pick_color_button = ttk.Button(self.main_frame, text="Выбрать цвет", command=self.choose_color)
        self.pick_color_button.grid(row=4, column=0, columnspan=2, pady=20, sticky="ew")
        
        self.update_button = ttk.Button(self.main_frame, text="Обновить цвет", command=self.update_color)
        self.update_button.grid(row=4, column=2, columnspan=2, pady=20, sticky="ew")
        
        # Статусная строка
        self.status_label = ttk.Label(self.main_frame, text="", foreground="red")
        self.status_label.grid(row=5, column=0, columnspan=4, pady=(10,0))
        
        # Устанавливаем начальные значения
        self.set_initial_values()
    
    def create_rgb_controls(self):
        # R
        self.r_label = ttk.Label(self.rgb_frame, text="R:")
        self.r_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.r_var = tk.IntVar(value=255)
        self.r_slider = ttk.Scale(self.rgb_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.r_var, command=self.on_rgb_slider)
        self.r_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.r_entry = ttk.Entry(self.rgb_frame, width=5)
        self.r_entry.grid(row=0, column=2, padx=5, pady=5)
        self.r_entry.bind("<Return>", self.on_rgb_entry)
        
        # G
        self.g_label = ttk.Label(self.rgb_frame, text="G:")
        self.g_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.g_var = tk.IntVar(value=255)
        self.g_slider = ttk.Scale(self.rgb_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.g_var, command=self.on_rgb_slider)
        self.g_slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.g_entry = ttk.Entry(self.rgb_frame, width=5)
        self.g_entry.grid(row=1, column=2, padx=5, pady=5)
        self.g_entry.bind("<Return>", self.on_rgb_entry)
        
        # B
        self.b_label = ttk.Label(self.rgb_frame, text="B:")
        self.b_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.b_var = tk.IntVar(value=255)
        self.b_slider = ttk.Scale(self.rgb_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.b_var, command=self.on_rgb_slider)
        self.b_slider.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.b_entry = ttk.Entry(self.rgb_frame, width=5)
        self.b_entry.grid(row=2, column=2, padx=5, pady=5)
        self.b_entry.bind("<Return>", self.on_rgb_entry)
        
        self.rgb_frame.columnconfigure(1, weight=1)
    
    def create_lab_controls(self):
        # L
        self.l_label = ttk.Label(self.lab_frame, text="L:")
        self.l_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.l_var = tk.DoubleVar(value=100.0)
        self.l_slider = ttk.Scale(self.lab_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.l_var, command=self.on_lab_slider)
        self.l_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.l_entry = ttk.Entry(self.lab_frame, width=5)
        self.l_entry.grid(row=0, column=2, padx=5, pady=5)
        self.l_entry.bind("<Return>", self.on_lab_entry)
        
        # a
        self.a_label = ttk.Label(self.lab_frame, text="a:")
        self.a_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.a_var = tk.DoubleVar(value=0.0)
        self.a_slider = ttk.Scale(self.lab_frame, from_=-128, to=128, orient=tk.HORIZONTAL, variable=self.a_var, command=self.on_lab_slider)
        self.a_slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.a_entry = ttk.Entry(self.lab_frame, width=5)
        self.a_entry.grid(row=1, column=2, padx=5, pady=5)
        self.a_entry.bind("<Return>", self.on_lab_entry)
        
        # b
        self.b_label_lab = ttk.Label(self.lab_frame, text="b:")
        self.b_label_lab.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.b_var_lab = tk.DoubleVar(value=0.0)
        self.b_slider_lab = ttk.Scale(self.lab_frame, from_=-128, to=128, orient=tk.HORIZONTAL, variable=self.b_var_lab, command=self.on_lab_slider)
        self.b_slider_lab.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.b_entry_lab = ttk.Entry(self.lab_frame, width=5)
        self.b_entry_lab.grid(row=2, column=2, padx=5, pady=5)
        self.b_entry_lab.bind("<Return>", self.on_lab_entry)
        
        self.lab_frame.columnconfigure(1, weight=1)
    
    def create_cmyk_controls(self):
        # C
        self.c_label = ttk.Label(self.cmyk_frame, text="C:")
        self.c_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.c_var = tk.DoubleVar(value=0.0)
        self.c_slider = ttk.Scale(self.cmyk_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.c_var, command=self.on_cmyk_slider)
        self.c_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.c_entry = ttk.Entry(self.cmyk_frame, width=5)
        self.c_entry.grid(row=0, column=2, padx=5, pady=5)
        self.c_entry.bind("<Return>", self.on_cmyk_entry)
        
        # M
        self.m_label = ttk.Label(self.cmyk_frame, text="M:")
        self.m_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.m_var = tk.DoubleVar(value=0.0)
        self.m_slider = ttk.Scale(self.cmyk_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.m_var, command=self.on_cmyk_slider)
        self.m_slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.m_entry = ttk.Entry(self.cmyk_frame, width=5)
        self.m_entry.grid(row=1, column=2, padx=5, pady=5)
        self.m_entry.bind("<Return>", self.on_cmyk_entry)
        
        # Y
        self.y_label = ttk.Label(self.cmyk_frame, text="Y:")
        self.y_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.y_var = tk.DoubleVar(value=0.0)
        self.y_slider = ttk.Scale(self.cmyk_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.y_var, command=self.on_cmyk_slider)
        self.y_slider.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.y_entry = ttk.Entry(self.cmyk_frame, width=5)
        self.y_entry.grid(row=2, column=2, padx=5, pady=5)
        self.y_entry.bind("<Return>", self.on_cmyk_entry)
        
        # K
        self.k_label = ttk.Label(self.cmyk_frame, text="K:")
        self.k_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.k_var = tk.DoubleVar(value=0.0)
        self.k_slider = ttk.Scale(self.cmyk_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.k_var, command=self.on_cmyk_slider)
        self.k_slider.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.k_entry = ttk.Entry(self.cmyk_frame, width=5)
        self.k_entry.grid(row=3, column=2, padx=5, pady=5)
        self.k_entry.bind("<Return>", self.on_cmyk_entry)
        
        self.cmyk_frame.columnconfigure(1, weight=1)
    
    def set_initial_values(self):
        self.update_color_from_rgb()
    
    def choose_color(self):
        color_code = colorchooser.askcolor(title="Выберите цвет")
        if color_code[0]:
            r, g, b = map(int, color_code[0])
            self.updating = True
            try:
                self.r_var.set(r)
                self.g_var.set(g)
                self.b_var.set(b)
                self.update_color_from_rgb()
            finally:
                self.updating = False
    
    def on_rgb_slider(self, event):
        if self.updating:
            return
        self.updating = True
        try:
            r = int(self.r_var.get())
            g = int(self.g_var.get())
            b = int(self.b_var.get())
            
            # Обновляем поля ввода
            self.r_entry.delete(0, tk.END)
            self.r_entry.insert(0, str(r))
            self.g_entry.delete(0, tk.END)
            self.g_entry.insert(0, str(g))
            self.b_entry.delete(0, tk.END)
            self.b_entry.insert(0, str(b))
            
            # Преобразования
            l, a, b_lab = rgb_to_lab(r, g, b)
            c, m, y_cmyk, k = rgb_to_cmyk(r, g, b)
            
            # Обновление LAB
            self.l_var.set(l)
            self.l_entry.delete(0, tk.END)
            self.l_entry.insert(0, f"{l:.2f}")
            self.a_var.set(a)
            self.a_entry.delete(0, tk.END)
            self.a_entry.insert(0, f"{a:.2f}")
            self.b_var_lab.set(b_lab)
            self.b_entry_lab.delete(0, tk.END)
            self.b_entry_lab.insert(0, f"{b_lab:.2f}")
            
            # Обновление CMYK
            self.c_var.set(c)
            self.c_entry.delete(0, tk.END)
            self.c_entry.insert(0, f"{c:.2f}")
            self.m_var.set(m)
            self.m_entry.delete(0, tk.END)
            self.m_entry.insert(0, f"{m:.2f}")
            self.y_var.set(y_cmyk)
            self.y_entry.delete(0, tk.END)
            self.y_entry.insert(0, f"{y_cmyk:.2f}")
            self.k_var.set(k)
            self.k_entry.delete(0, tk.END)
            self.k_entry.insert(0, f"{k:.2f}")
            
            # Обновление отображения цвета
            self.color_display.configure(bg=f'#{r:02x}{g:02x}{b:02x}')
            self.status_label.config(text="")
        finally:
            self.updating = False
    
    def on_rgb_entry(self, event):
        if self.updating:
            return
        self.updating = True
        try:
            r = int(self.r_entry.get())
            g = int(self.g_entry.get())
            b = int(self.b_entry.get())
            
            if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                raise ValueError("RGB значения должны быть от 0 до 255")
            
            self.r_var.set(r)
            self.g_var.set(g)
            self.b_var.set(b)
            self.update_color_from_rgb()
        except ValueError as ve:
            self.status_label.config(text=f"Ошибка: {ve}")
            messagebox.showwarning("Ошибка", f"Некорректные значения RGB: {ve}")
        finally:
            self.updating = False
    
    def on_lab_slider(self, event):
        if self.updating:
            return
        self.updating = True
        try:
            l = self.l_var.get()
            a = self.a_var.get()
            b_lab = self.b_var_lab.get()
            
            # Обновляем поля ввода
            self.l_entry.delete(0, tk.END)
            self.l_entry.insert(0, f"{l:.2f}")
            self.a_entry.delete(0, tk.END)
            self.a_entry.insert(0, f"{a:.2f}")
            self.b_entry_lab.delete(0, tk.END)
            self.b_entry_lab.insert(0, f"{b_lab:.2f}")
            
            # Преобразование LAB в RGB
            r, g, b = lab_to_rgb(l, a, b_lab)
            clipped = False
            if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                clipped = True
                r = min(max(0, r), 255)
                g = min(max(0, g), 255)
                b = min(max(0, b), 255)
            
            # Обновление RGB
            self.r_var.set(r)
            self.g_var.set(g)
            self.b_var.set(b)
            self.r_entry.delete(0, tk.END)
            self.r_entry.insert(0, str(r))
            self.g_entry.delete(0, tk.END)
            self.g_entry.insert(0, str(g))
            self.b_entry.delete(0, tk.END)
            self.b_entry.insert(0, str(b))
            
            # Обновление CMYK
            c, m, y_cmyk, k = rgb_to_cmyk(r, g, b)
            self.c_var.set(c)
            self.c_entry.delete(0, tk.END)
            self.c_entry.insert(0, f"{c:.2f}")
            self.m_var.set(m)
            self.m_entry.delete(0, tk.END)
            self.m_entry.insert(0, f"{m:.2f}")
            self.y_var.set(y_cmyk)
            self.y_entry.delete(0, tk.END)
            self.y_entry.insert(0, f"{y_cmyk:.2f}")
            self.k_var.set(k)
            self.k_entry.delete(0, tk.END)
            self.k_entry.insert(0, f"{k:.2f}")
            
            # Обновление отображения цвета
            self.color_display.configure(bg=f'#{r:02x}{g:02x}{b:02x}')
            
            if clipped:
                self.status_label.config(text="Предупреждение: RGB значения были обрезаны до диапазона 0-255.")
            else:
                self.status_label.config(text="")
        except Exception as e:
            self.status_label.config(text=f"Ошибка: {e}")
            messagebox.showwarning("Ошибка", f"Некорректные значения LAB: {e}")
        finally:
            self.updating = False
    
    def on_lab_entry(self, event):
        if self.updating:
            return
        self.updating = True
        try:
            l = float(self.l_entry.get())
            a = float(self.a_entry.get())
            b_lab = float(self.b_entry_lab.get())
            
            if not (0 <= l <= 100 and -128 <= a <= 128 and -128 <= b_lab <= 128):
                raise ValueError("LAB значения вне допустимого диапазона")
            
            self.l_var.set(l)
            self.a_var.set(a)
            self.b_var_lab.set(b_lab)
            self.on_lab_slider(None)
        except ValueError as ve:
            self.status_label.config(text=f"Ошибка: {ve}")
            messagebox.showwarning("Ошибка", f"Некорректные значения LAB: {ve}")
        finally:
            self.updating = False
    
    def on_cmyk_slider(self, event):
        if self.updating:
            return
        self.updating = True
        try:
            c = self.c_var.get()
            m = self.m_var.get()
            y = self.y_var.get()
            k = self.k_var.get()
            
            # Обновляем поля ввода
            self.c_entry.delete(0, tk.END)
            self.c_entry.insert(0, f"{c:.2f}")
            self.m_entry.delete(0, tk.END)
            self.m_entry.insert(0, f"{m:.2f}")
            self.y_entry.delete(0, tk.END)
            self.y_entry.insert(0, f"{y:.2f}")
            self.k_entry.delete(0, tk.END)
            self.k_entry.insert(0, f"{k:.2f}")
            
            # Преобразование CMYK в RGB
            r, g, b = cmyk_to_rgb(c, m, y, k)
            clipped = False
            if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                clipped = True
                r = min(max(0, r), 255)
                g = min(max(0, g), 255)
                b = min(max(0, b), 255)
            
            # Обновление RGB
            self.r_var.set(r)
            self.g_var.set(g)
            self.b_var.set(b)
            self.r_entry.delete(0, tk.END)
            self.r_entry.insert(0, str(r))
            self.g_entry.delete(0, tk.END)
            self.g_entry.insert(0, str(g))
            self.b_entry.delete(0, tk.END)
            self.b_entry.insert(0, str(b))
            
            # Обновление LAB
            l, a, b_lab = rgb_to_lab(r, g, b)
            self.l_var.set(l)
            self.l_entry.delete(0, tk.END)
            self.l_entry.insert(0, f"{l:.2f}")
            self.a_var.set(a)
            self.a_entry.delete(0, tk.END)
            self.a_entry.insert(0, f"{a:.2f}")
            self.b_var_lab.set(b_lab)
            self.b_entry_lab.delete(0, tk.END)
            self.b_entry_lab.insert(0, f"{b_lab:.2f}")
            
            # Обновление отображения цвета
            self.color_display.configure(bg=f'#{r:02x}{g:02x}{b:02x}')
            
            if clipped:
                self.status_label.config(text="Предупреждение: RGB значения были обрезаны до диапазона 0-255.")
            else:
                self.status_label.config(text="")
        except Exception as e:
            self.status_label.config(text=f"Ошибка: {e}")
            messagebox.showwarning("Ошибка", f"Некорректные значения CMYK: {e}")
        finally:
            self.updating = False
    
    def on_cmyk_entry(self, event):
        if self.updating:
            return
        self.updating = True
        try:
            c = float(self.c_entry.get())
            m = float(self.m_entry.get())
            y = float(self.y_entry.get())
            k = float(self.k_entry.get())
            
            if not (0 <= c <= 100 and 0 <= m <= 100 and 0 <= y <= 100 and 0 <= k <= 100):
                raise ValueError("CMYK значения должны быть от 0 до 100")
            
            self.c_var.set(c)
            self.m_var.set(m)
            self.y_var.set(y)
            self.k_var.set(k)
            self.on_cmyk_slider(None)
        except ValueError as ve:
            self.status_label.config(text=f"Ошибка: {ve}")
            messagebox.showwarning("Ошибка", f"Некорректные значения CMYK: {ve}")
        finally:
            self.updating = False
    
    def update_color(self):
        # Обновление значений при нажатии кнопки "Обновить цвет"
        self.on_rgb_slider(None)
    
    def update_color_from_rgb(self):
        # Метод для инициализации значений при запуске
        self.on_rgb_slider(None)

# Запуск приложения
def main():
    root = tk.Tk()
    app = ColorConverterApp(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()