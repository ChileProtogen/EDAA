import sys
import threading
import queue
import matplotlib.pyplot as plt

# reutilizamos el algoritmo y las funciones de lectura del archivo anterior
from convex_hull import findConvexHull, readPoints, orderCounterClockwise

AYUDA = """Comandos:
  add x,y     agrega un punto            (ej: add 50,40)
  del x,y     quita un punto exacto      (ej: del 50,40)
  load ruta   agrega los puntos de un archivo x,y
  clear       quita todos los puntos
  list        muestra los puntos actuales
  hull        muestra los vertices del convex hull
  help        muestra esta ayuda
  quit        cierra el programa
En el grafico: clic izquierdo agrega un punto, clic derecho quita el mas cercano."""


def parsePoint(text):
    x, y = text.strip().split(",")
    return [float(x), float(y)]


class HullApp:
    def __init__(self, points):
        self.points = []
        for p in points:
            if p not in self.points:
                self.points.append(p)

        self.cmds = queue.Queue()
        self.running = True

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.fig.canvas.mpl_connect("button_press_event", self.onClick)
        self.fig.canvas.mpl_connect("close_event", self.onClose)

        # revisa cada 100 ms si llego un comando desde la terminal
        self.timer = self.fig.canvas.new_timer(interval=100)
        self.timer.add_callback(self.poll)

    # ---------- logica de comandos ----------

    # ejecuta un comando y devuelve (hubo_cambio, mensaje)
    def applyCommand(self, line):
        line = line.strip()
        if not line:
            return False, ""

        parts = line.split(None, 1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        try:
            if cmd == "add":
                p = parsePoint(arg)
                if p in self.points:
                    return False, f"El punto {p} ya existe"
                self.points.append(p)
                return True, f"Agregado {p}"

            if cmd in ("del", "remove", "rm"):
                p = parsePoint(arg)
                if p not in self.points:
                    return False, f"El punto {p} no existe"
                self.points.remove(p)
                return True, f"Quitado {p}"

            if cmd == "load":
                new = readPoints(arg)
                added = 0
                for p in new:
                    if p not in self.points:
                        self.points.append(p)
                        added += 1
                return True, f"Se agregaron {added} puntos de {arg}"

            if cmd == "clear":
                self.points.clear()
                return True, "Todos los puntos fueron quitados"

            if cmd == "list":
                return False, f"{len(self.points)} puntos: {self.points}"
            
            if cmd == "hull":
                hullPoints = findConvexHull(self.points) if len(self.points) >= 3 else []
                if not hullPoints:
                    return False, "No hay convex hull (faltan puntos o son colineales)"
                ordered = orderCounterClockwise(hullPoints)
                return False, f"{len(ordered)} vertices (sentido antihorario): {ordered}"

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

    # ---------- eventos del grafico ----------

    def onClick(self, event):
        if event.inaxes != self.ax or event.xdata is None:
            return

        # no hacer nada mientras se usa zoom o pan de la barra de herramientas
        toolbar = getattr(self.fig.canvas, "toolbar", None)
        if toolbar is not None and getattr(toolbar, "mode", ""):
            return

        if event.button == 1:
            p = [round(event.xdata, 2), round(event.ydata, 2)]
            if p not in self.points:
                self.points.append(p)
                print(f"Agregado {p}")
                self.draw()
        elif event.button == 3 and self.points:
            # quita el punto mas cercano al clic, si esta cerca
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
                print(f"Quitado {best}")
                self.draw()

    def onClose(self, event):
        self.running = False

    # ---------- entrada por terminal ----------

    def readStdin(self):
        for line in sys.stdin:
            self.cmds.put(line)
        # fin de la entrada (Ctrl+D): se deja abierta la ventana
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
            ch, msg = self.applyCommand(line)
            if msg:
                print(msg)
            changed = changed or ch
            if not self.running:
                plt.close(self.fig)
                return
            print("> ", end="", flush=True)
        if changed:
            self.draw()

    # ---------- dibujo ----------

    def draw(self):
        ax = self.ax
        ax.clear()

        hullPoints = findConvexHull(self.points) if len(self.points) >= 3 else []

        if self.points:
            ax.scatter(
                [p[0] for p in self.points],
                [p[1] for p in self.points],
                color="steelblue",
                label="Puntos",
                zorder=2,
            )

        if hullPoints:
            ordered = orderCounterClockwise(hullPoints)
            closed = ordered + [ordered[0]]
            hx = [p[0] for p in closed]
            hy = [p[1] for p in closed]
            ax.fill(hx, hy, color="tomato", alpha=0.15, zorder=1)
            ax.plot(hx, hy, color="tomato", linewidth=2, label="Convex hull", zorder=3)
            ax.scatter(hx[:-1], hy[:-1], color="tomato", s=70, zorder=4)
            ax.set_title(
                f"Convex hull: {len(hullPoints)} vertices de {len(self.points)} puntos"
            )
        else:
            ax.set_title(
                f"{len(self.points)} puntos - sin convex hull (faltan puntos o son colineales)"
            )

        ax.set_aspect("equal", adjustable="datalim")
        self.fig.canvas.draw_idle()

    def run(self):
        print(AYUDA)
        print("> ", end="", flush=True)
        self.draw()
        threading.Thread(target=self.readStdin, daemon=True).start()
        self.timer.start()
        plt.show()


if __name__ == "__main__":
    # uso: python convex_hull_interactivo.py [puntos.txt]
    initial = readPoints(sys.argv[1]) if len(sys.argv) > 1 else []
    HullApp(initial).run()