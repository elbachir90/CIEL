import tkinter as tk
from tkinter import ttk, messagebox
import math
import re


class ComplexRotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rotation dans le plan complexe")
        self.root.geometry("950x960")
        self.root.resizable(False, False)

        # Variables
        self.z = complex(2, 3)
        self.angle = 0
        self.target_angle = 90
        self.rotating = False
        self.show_result = False
        self.animation_id = None

        self._setup_ui()
        self.update_calculation()
        self.draw()

    def _setup_ui(self):
        """Configure l'interface utilisateur"""
        self._create_header()
        self._create_input_section()
        self._create_canvas()
        self._create_calculation_section()

    def _create_header(self):
        """Crée l'en-tête de l'application"""
        header = tk.Frame(self.root, bg='#6366f1', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(
            header,
            text="Rotation dans le plan complexe",
            font=('Segoe UI', 18, 'bold'),
            bg='#6366f1',
            fg='white'
        ).pack(pady=12)

    def _create_input_section(self):
        """Crée la section de saisie"""
        input_frame = tk.Frame(self.root, bg='#f8fafc', padx=20, pady=15)
        input_frame.pack(fill='x')

        # Label d'instruction
        tk.Label(
            input_frame,
            text="Nombre complexe (ex: 2+3i, -1-4i, 5, 3i)",
            font=('Segoe UI', 11, 'bold'),
            bg='#f8fafc',
            fg='#1e293b'
        ).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 5))

        # Champ de saisie
        self.complex_entry = tk.Entry(input_frame, font=('Consolas', 12), width=22)
        self.complex_entry.insert(0, "2+3i")
        self.complex_entry.grid(row=1, column=0, padx=(0, 10), sticky='ew')
        self.complex_entry.bind('<Return>', lambda e: self.start_rotation())

        # Sélection de rotation
        tk.Label(
            input_frame,
            text="Rotation :",
            font=('Segoe UI', 11, 'bold'),
            bg='#f8fafc',
            fg='#1e293b'
        ).grid(row=2, column=0, sticky='w', pady=(10, 5))

        self.rotation_var = tk.StringVar(value="90")
        rotation_combo = ttk.Combobox(
            input_frame,
            textvariable=self.rotation_var,
            values=["90", "180"],
            state="readonly",
            width=20
        )
        rotation_combo.grid(row=3, column=0, padx=(0, 10), sticky='ew')

        # Boutons
        btn_frame = tk.Frame(input_frame, bg='#f8fafc')
        btn_frame.grid(row=1, column=1, rowspan=3, sticky='ns', padx=(10, 0))

        self.start_btn = tk.Button(
            btn_frame,
            text="Démarrer",
            bg='#3b82f6',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            command=self.start_rotation,
            height=2,
            width=16,
            cursor='hand2'
        )
        self.start_btn.pack(pady=5, fill='x')

        self.reset_btn = tk.Button(
            btn_frame,
            text="Recommencer",
            bg='#6b7280',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            command=self.reset,
            height=2,
            width=16,
            cursor='hand2'
        )
        self.reset_btn.pack(pady=5, fill='x')

        input_frame.grid_columnconfigure(0, weight=1)

    def _create_canvas(self):
        """Crée le canvas pour la visualisation"""
        canvas_frame = tk.Frame(self.root, pady=20)
        canvas_frame.pack()
        self.canvas = tk.Canvas(
            canvas_frame,
            width=400,
            height=400,
            bg='white',
            highlightthickness=2,
            highlightbackground='#e2e8f0'
        )
        self.canvas.pack()

    def _create_calculation_section(self):
        """Crée la section des calculs"""
        calc_frame = tk.Frame(self.root, bg='#f1f5f9', padx=20, pady=20)
        calc_frame.pack(fill='both', expand=True, padx=20)

        # Zone de texte avec scrollbar
        text_frame = tk.Frame(calc_frame)
        text_frame.pack(fill='both', expand=True)

        self.calc_text = tk.Text(
            text_frame,
            font=('Consolas', 12),
            height=22,
            wrap='word',
            bg='#f8fafc',
            relief='flat',
            padx=15,
            pady=15,
            spacing1=4,
            spacing3=4
        )

        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=self.calc_text.yview)
        self.calc_text.config(yscrollcommand=scrollbar.set)
        self.calc_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Label de résultat
        self.result_label = tk.Label(
            calc_frame,
            text="",
            font=('Segoe UI', 12, 'bold'),
            bg='#ecfdf5',
            fg='#166534',
            justify='left',
            anchor='w',
            padx=20,
            pady=15,
            bd=0
        )

    def parse_complex(self, s):
        """Parse une chaîne en nombre complexe"""
        s = s.strip().replace(' ', '')
        if not s:
            return None

        # Essai de parsing standard
        try:
            return complex(s.replace('i', 'j'))
        except ValueError:
            pass

        # Gestion des cas spéciaux (i, -i, 3i, etc.)
        match = re.match(r'^([+-]?)(\d*\.?\d*)i$', s)
        if match:
            sign = -1 if match.group(1) == '-' else 1
            coeff = match.group(2)
            val = 1.0 if not coeff else float(coeff)
            return complex(0, sign * val)

        messagebox.showerror(
            "Erreur",
            "Format invalide !\nExemples valides: 2+3i, -1-4i, 5, 3i, -i"
        )
        return None

    def to_canvas(self, c):
        """Convertit un nombre complexe en coordonnées canvas"""
        scale = 40
        center_x, center_y = 200, 200
        return (center_x + c.real * scale, center_y - c.imag * scale)

    def draw_arrowhead(self, x1, y1, x2, y2, color):
        """Dessine une flèche à l'extrémité d'une ligne"""
        angle = math.atan2(y2 - y1, x2 - x1)
        size = 10
        x3 = x2 - size * math.cos(angle - math.pi / 6)
        y3 = y2 - size * math.sin(angle - math.pi / 6)
        x4 = x2 - size * math.cos(angle + math.pi / 6)
        y4 = y2 - size * math.sin(angle + math.pi / 6)
        self.canvas.create_polygon(x2, y2, x3, y3, x4, y4, fill=color, outline=color)

    def format_complex(self, c):
        """Formate un nombre complexe pour l'affichage"""
        # Partie réelle
        r = f"{c.real:.2f}".rstrip('0').rstrip('.') if c.real % 1 else str(int(c.real))
        # Partie imaginaire
        i = f"{abs(c.imag):.2f}".rstrip('0').rstrip('.') if abs(c.imag) % 1 else str(int(abs(c.imag)))

        if c.imag == 0:
            return r
        if c.real == 0:
            prefix = '-' if c.imag < 0 else ''
            coeff = '' if i == '1' else i
            return f"{prefix}{coeff}i"

        sign = '+' if c.imag > 0 else '-'
        coeff = '' if i == '1' else i
        return f"{r} {sign} {coeff}i".strip()

    def draw(self):
        """Dessine la visualisation sur le canvas"""
        self.canvas.delete("all")
        scale = 40
        center = (200, 200)

        # Grille
        for i in range(-10, 11):
            if i == 0:
                continue
            x = center[0] + i * scale
            y = center[1] - i * scale
            self.canvas.create_line(x, 0, x, 400, fill='#e5e7eb', width=0.5)
            self.canvas.create_line(0, y, 400, y, fill='#e5e7eb', width=0.5)

        # Axes
        self.canvas.create_line(0, center[1], 400, center[1], fill='#374151', width=2)
        self.canvas.create_line(center[0], 0, center[0], 400, fill='#374151', width=2)
        self.canvas.create_text(380, center[1] - 10, text="Réel", fill='#374151', font=('Segoe UI', 10))
        self.canvas.create_text(center[0] + 30, 20, text="Imag", fill='#374151', font=('Segoe UI', 10))

        # Graduations
        for n in [-4, -3, -2, -1, 1, 2, 3, 4]:
            x = center[0] + n * scale
            y = center[1] - n * scale
            self.canvas.create_line(x, center[1] - 5, x, center[1] + 5, fill='#374151')
            self.canvas.create_text(x, center[1] + 20, text=str(n), fill='#374151', font=('Segoe UI', 9))
            self.canvas.create_line(center[0] - 5, y, center[0] + 5, y, fill='#374151')
            self.canvas.create_text(center[0] - 25, y + 5, text=f"{n}i", fill='#374151', font=('Segoe UI', 9))

        # Calcul des positions
        start_pos = self.to_canvas(self.z)
        rad = math.radians(self.angle)
        rotated = complex(
            self.z.real * math.cos(rad) - self.z.imag * math.sin(rad),
            self.z.real * math.sin(rad) + self.z.imag * math.cos(rad)
        )
        current_pos = self.to_canvas(rotated)

        # Arc de rotation
        if self.angle > 0:
            color = '#8b5cf6' if self.target_angle == 90 else '#f97316'
            # Calculer l'angle initial du vecteur z
            initial_angle = math.degrees(math.atan2(self.z.imag, self.z.real))
            self.canvas.create_arc(
                center[0] - 60, center[1] - 60, center[0] + 60, center[1] + 60,
                start=initial_angle, extent=self.angle, style='arc', outline=color, width=2, dash=(5, 5)
            )

        # Vecteur initial
        self.canvas.create_line(center[0], center[1], start_pos[0], start_pos[1], fill='#3b82f6', width=3)
        self.draw_arrowhead(center[0], center[1], start_pos[0], start_pos[1], '#3b82f6')
        self.canvas.create_oval(start_pos[0] - 6, start_pos[1] - 6, start_pos[0] + 6, start_pos[1] + 6,
                                fill='#3b82f6', outline='')
        self.canvas.create_text(start_pos[0] + 40, start_pos[1] - 15,
                                text=f"z = {self.format_complex(self.z)}",
                                fill='#3b82f6', font=('Segoe UI', 12, 'bold'))

        # Vecteur tourné
        if self.angle > 0:
            self.canvas.create_line(center[0], center[1], current_pos[0], current_pos[1], fill='#ef4444', width=3)
            self.draw_arrowhead(center[0], center[1], current_pos[0], current_pos[1], '#ef4444')
            self.canvas.create_oval(current_pos[0] - 6, current_pos[1] - 6, current_pos[0] + 6, current_pos[1] + 6,
                                    fill='#ef4444', outline='')

            if self.show_result:
                op = 'i·z' if self.target_angle == 90 else '-z'
                self.canvas.create_text(current_pos[0] - 15, current_pos[1] - 15,
                                        text=f"{op} = {self.format_complex(rotated)}",
                                        fill='#ef4444', font=('Segoe UI', 12, 'bold'), anchor='e')

        # Affichage de l'angle
        if self.angle > 0:
            color = '#8b5cf6' if self.target_angle == 90 else '#f97316'
            self.canvas.create_text(center[0] + 80, center[1] - 30,
                                    text=f"{int(self.angle)}°",
                                    fill=color, font=('Segoe UI', 11, 'bold'))

    def update_calculation(self):
        """Met à jour l'affichage des calculs"""
        self.calc_text.config(state='normal')
        self.calc_text.delete(1.0, 'end')

        is90 = self.target_angle == 90
        op = 'i' if is90 else '-1'
        title = 'Multiplication par i' if is90 else 'Multiplication par -1'
        color_tag = 'purple' if is90 else 'orange'

        rotated = complex(-self.z.imag, self.z.real) if is90 else -self.z

        lines = [
            f"z = {self.format_complex(self.z)}",
            f"→ Position : ({self.z.real:g}, {self.z.imag:g})",
            "",
            "─" * 50,
            "",
            f"{title} :",
            f"{op} · z = {op} · ({self.format_complex(self.z)})",
        ]

        if is90:
            lines.extend([
                "",
                f"= {self.z.real}i + {self.z.imag}i²",
                f"= {self.z.real}i + {self.z.imag}·(−1)",
                f"= {self.z.real}i − {abs(self.z.imag)}",
                f"= {self.format_complex(rotated)}",
            ])
        else:
            lines.extend([
                "",
                f"= −({self.format_complex(self.z)})",
                f"= {self.format_complex(rotated)}",
            ])

        lines.extend([
            "",
            "─" * 50,
            "",
            f"{op}·z = {self.format_complex(rotated)}",
            f"→ Position : ({rotated.real:g}, {rotated.imag:g})"
        ])

        # Insertion avec coloration
        for line in lines:
            if line == "" or "─" in line:
                self.calc_text.insert('end', line + "\n")
                continue

            start_idx = self.calc_text.index('end')
            self.calc_text.insert('end', line + "\n")

            if 'z =' in line:
                self.calc_text.tag_add('blue', start_idx, 'end-1c')
            elif title in line:
                self.calc_text.tag_add(color_tag, start_idx, 'end-1c')
            elif any(x in line for x in ['=', '−', 'i²']) and 'Position' not in line:
                self.calc_text.tag_add('red', start_idx, 'end-1c')

        # Configuration des couleurs
        self.calc_text.tag_config('blue', foreground='#3b82f6', font=('Consolas', 12, 'bold'))
        self.calc_text.tag_config('red', foreground='#ef4444', font=('Consolas', 12, 'bold'))
        self.calc_text.tag_config('purple', foreground='#8b5cf6', font=('Consolas', 12, 'bold'))
        self.calc_text.tag_config('orange', foreground='#f97316', font=('Consolas', 12, 'bold'))

        self.calc_text.config(state='disabled')
        self.calc_text.see('1.0')

    def animate(self):
        """Anime la rotation"""
        if self.angle >= self.target_angle:
            self.rotating = False
            self.show_result = True
            self.start_btn.config(text="Démarrer", state='normal')

            direction = "inverse des aiguilles d'une montre" if self.target_angle == 90 else "opposé (180°)"
            self.result_label.config(
                text=f"✓ Résultat :\nLe point a effectué une rotation de {self.target_angle}° "
                     f"dans le sens {direction} !"
            )
            self.result_label.pack(fill='x', side='bottom', pady=(10, 0))
            self.draw()
            return

        self.angle = min(self.angle + 2, self.target_angle)
        self.draw()
        self.animation_id = self.root.after(20, self.animate)

    def start_rotation(self):
        """Démarre l'animation de rotation"""
        if self.rotating:
            return

        text = self.complex_entry.get()
        parsed = self.parse_complex(text)
        if parsed is None:
            return

        self.z = parsed
        self.target_angle = int(self.rotation_var.get())
        self.angle = 0
        self.show_result = False
        self.result_label.pack_forget()

        self.rotating = True
        self.start_btn.config(text="Rotation en cours...", state='disabled')
        self.update_calculation()
        self.draw()
        self.animation_id = self.root.after(50, self.animate)

    def reset(self):
        """Réinitialise l'application"""
        if self.animation_id:
            self.root.after_cancel(self.animation_id)

        self.angle = 0
        self.rotating = False
        self.show_result = False
        self.start_btn.config(text="Démarrer", state='normal')
        self.result_label.pack_forget()
        self.update_calculation()
        self.draw()


def main():
    """Point d'entrée de l'application"""
    root = tk.Tk()
    app = ComplexRotationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
