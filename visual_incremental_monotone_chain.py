import queue
import sys
import threading
import matplotlib.pyplot as plt

from incremental_monotone_chain import insert_point_incremental
from monotone_chain import monotone_chain

AYUDA = """Comandos:
  add x,y     agrega un punto (actualiza el hull incrementalmente)
  del x,y     quita un punto exacto
  load ruta   agrega los puntos de un archivo x,y
  clear       quita todos los puntos
  list        muestra los puntos actuales
  hull        muestra los vertices del convex hull actual
  help        muestra esta ayuda
  quit        cierra el programa
En el grafico: clic izquierdo agrega un punto (incremental), clic derecho quita el mas cercano."""


def read_points(path):
    points = []
    with open(path, "r", encoding="utf-8") as f:
        for num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                x, y = line.replace(";", ",").split(",")
                points.append([float(x), float(y)])
            except ValueError:
                print(f"Linea {num} ignorada (formato invalido): {line!r}")
    return points


def parse_point(text):
    x, y = text.strip().split(",")
    return [float(x), float(y)]


class IncrementalHullApp:
    def __init__(self, points):
        self.points = []
        for p in points:
            pt = [float(p[0]), float(p[1])]
            if pt not in self.points:
                self.points.append(pt)

        # Calculo inicial del hull (ya viene en sentido antihorario con monotone_chain)
        self.hull = monotone_chain(self.points) if len(self.points) >= 3 else []
        self.last_status = "Hull inicial calculado"

        self.cmds = queue.Queue()
        self.running = True

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.fig.canvas.mpl_connect("close_event", self.on_close)

        self.timer = self.fig.canvas.new_timer(interval=100)
        self.timer.add_callback(self.poll)

    def add_point_incremental(self, p):
        pt = [float(p[0]), float(p[1])]
        if pt in self.points:
            return False, f"El punto {pt} ya existe"

        self.points.append(pt)
        self.hull, changed = insert_point_incremental(self.hull, pt)

        if changed:
            self.last_status = f"Punto {pt} exterior -> HULL ACTUALIZADO"
            return True, f"Agregado {pt} (exterior: convex hull recalculado incrementalmente)"
        else:
            self.last_status = f"Punto {pt} interior/borde -> SIN CAMBIOS"
            return True, f"Agregado {pt} (interior o en borde: convex hull sin cambios)"

    def apply_command(self, line):
        line = line.strip()
        if not line:
            return False, ""

        parts = line.split(None, 1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        try:
            if cmd == "add":
                p = parse_point(arg)
                return self.add_point_incremental(p)

            if cmd in ("del", "remove", "rm"):
                p = parse_point(arg)
                if p not in self.points:
                    return False, f"El punto {p} no existe"
                self.points.remove(p)
                # Al eliminar un punto se recalcula desde los puntos restantes
                self.hull = monotone_chain(self.points) if len(self.points) >= 3 else []
                self.last_status = f"Eliminado {p} -> hull recalculado"
                return True, f"Quitado {p}"

            if cmd == "load":
                new_pts = read_points(arg)
                added = 0
                any_hull_change = False
                for p in new_pts:
                    pt = [float(p[0]), float(p[1])]
                    if pt not in self.points:
                        self.points.append(pt)
                        self.hull, ch = insert_point_incremental(self.hull, pt)
                        any_hull_change = any_hull_change or ch
                        added += 1
                self.last_status = (
                    f"Cargados {added} pts -> {'HULL ACTUALIZADO' if any_hull_change else 'SIN CAMBIOS'}"
                )
                return True, f"Se agregaron {added} puntos de {arg}"

            if cmd == "clear":
                self.points.clear()
                self.hull = []
                self.last_status = "Lienzo limpiado"
                return True, "Todos los puntos fueron quitados"

            if cmd == "list":
                return False, f"{len(self.points)} puntos: {self.points}"

            if cmd == "hull":
                if len(self.hull) < 3:
                    return False, "No hay convex hull (faltan puntos o son colineales)"
                return False, f"{len(self.hull)} vertices (sentido antihorario): {self.hull}"

            if cmd == "help":
                return False, AYUDA

            if cmd in ("quit", "exit", "q"):
                self.running = False
                return False, "Cerrando..."

            return False, f"Comando desconocido: {cmd} (escribe help)"
        except ValueError:
            return False, "Formato invalido, usa: x,y (ej: 10,20)"
        except OSError as e:
            return False, f"No se pudo leer el archivo: {e}"

    def on_click(self, event):
        if event.inaxes != self.ax or event.xdata is None:
            return

        toolbar = getattr(self.fig.canvas, "toolbar", None)
        if toolbar is not None and getattr(toolbar, "mode", ""):
            return

        if event.button == 1:
            p = [round(float(event.xdata), 2), round(float(event.ydata), 2)]
            changed, msg = self.add_point_incremental(p)
            if msg:
                print(msg)
            if changed:
                self.draw()
        elif event.button == 3 and self.points:
            x0, x1 = self.ax.get_xlim()
            y0, y1 = self.ax.get_ylim()
            tol = 0.04 * max(abs(x1 - x0), abs(y1 - y0))
            best = min(
                self.points,
                key=lambda p: (p[0] - event.xdata) ** 2 + (p[1] - event.ydata) ** 2,
            )
            dist = ((best[0] - event.xdata) ** 2 + (best[1] - event.ydata) ** 2) ** 0.5
            if dist <= tol:
                self.points.remove(best)
                self.hull = monotone_chain(self.points) if len(self.points) >= 3 else []
                self.last_status = f"Quitado {best} -> hull recalculado"
                print(f"Quitado {best}")
                self.draw()

    def on_close(self, event):
        self.running = False

    def read_stdin(self):
        for line in sys.stdin:
            self.cmds.put(line)
        self.cmds.put(None)

    def poll(self):
        changed = False
        while True:
            try:
                line = self.cmds.get_nowait()
            except queue.Empty:
                break
            if line is None:
                break
            ch, msg = self.apply_command(line)
            if msg:
                print(msg)
            changed = changed or ch
            if not self.running:
                plt.close(self.fig)
                return
            print("> ", end="", flush=True)
        if changed:
            self.draw()

    def draw(self):
        ax = self.ax
        ax.clear()

        if self.points:
            ax.scatter(
                [p[0] for p in self.points],
                [p[1] for p in self.points],
                color="steelblue",
                label="Puntos",
                zorder=2,
            )

        if len(self.hull) >= 3:
            closed = self.hull + [self.hull[0]]
            hx = [p[0] for p in closed]
            hy = [p[1] for p in closed]
            ax.fill(hx, hy, color="tomato", alpha=0.15, zorder=1)
            ax.plot(hx, hy, color="tomato", linewidth=2, label="Convex hull", zorder=3)
            ax.scatter(hx[:-1], hy[:-1], color="tomato", s=70, zorder=4)
            ax.set_title(
                f"Convex hull: {len(self.hull)} vertices de {len(self.points)} pts | {self.last_status}"
            )
        else:
            ax.set_title(
                f"{len(self.points)} puntos - sin convex hull | {self.last_status}"
            )

        ax.set_aspect("equal", adjustable="datalim")
        if self.points:
            ax.legend()
        self.fig.canvas.draw_idle()

    def run(self):
        print(AYUDA)
        print("> ", end="", flush=True)
        self.draw()
        threading.Thread(target=self.read_stdin, daemon=True).start()
        self.timer.start()
        plt.show()


if __name__ == "__main__":
    initial = read_points(sys.argv[1]) if len(sys.argv) > 1 else []
    IncrementalHullApp(initial).run()