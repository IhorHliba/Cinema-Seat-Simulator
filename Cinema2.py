"""
Cinema Seat Booking Simulator (turtle version)
- OOP structure with Seat and CinemaHall
- Fast drawing via tracer(0, 0)
- Persist seat states to seats.json (auto-save on every toggle)
- UI: free/sold counters, legend, "SCREEN" bar
- Controls:
    * Mouse click  : toggle a seat
    * R            : reset all seats (set to free)
    * Q / Escape   : save and exit
"""

import json
import math
import os
import turtle


# --------------- Config --------------- #
WINDOW_W, WINDOW_H = 1000, 700

ROWS = 8
COLS = 12

SEAT_RADIUS = 16
SEAT_GAP_X = 18       # horizontal gap between seats
SEAT_GAP_Y = 24       # vertical gap between rows

TOP_MARGIN = 150      # space for "SCREEN" banner
BOTTOM_MARGIN = 80    # space for counters/legend

DATA_FILE = "seats.json"

# Colors
COLOR_BG = "#0f0f14"
COLOR_SEAT_FREE = "#39d353"     # green
COLOR_SEAT_SOLD = "#cc2626"     # deep red
COLOR_SEAT_OUTLINE = "#1f6feb"
COLOR_TEXT = "#e6edf3"
COLOR_NOTE = "#8b949e"
COLOR_SCREEN = "#30363d"

# Turtle speed tweaks
turtle.colormode(255)


# --------------- Model --------------- #
class Seat:
    """Single seat model + drawing helper."""
    def __init__(self, row: int, col: int, x: float, y: float, r: float):
        self.row = row
        self.col = col
        self.x = x
        self.y = y
        self.r = r
        self.booked = False

    def contains(self, px: float, py: float) -> bool:
        """Point-in-circle hit test."""
        return math.hypot(px - self.x, py - self.y) <= self.r

    def draw(self, pen: turtle.Turtle):
        """Draw the seat as a filled circle with outline."""
        fill = COLOR_SEAT_SOLD if self.booked else COLOR_SEAT_FREE
        pen.up()
        pen.goto(self.x, self.y - self.r)
        pen.setheading(0)
        pen.down()
        pen.color(COLOR_SEAT_OUTLINE, fill)
        pen.begin_fill()
        pen.circle(self.r)
        pen.end_fill()

    def to_dict(self):
        return {"row": self.row, "col": self.col, "booked": self.booked}

    def from_dict(self, data):
        self.booked = bool(data.get("booked", False))


class CinemaHall:
    """Cinema grid of seats with drawing, events, and persistence."""
    def __init__(self, rows, cols, radius, gap_x, gap_y):
        self.rows = rows
        self.cols = cols
        self.radius = radius
        self.gap_x = gap_x
        self.gap_y = gap_y

        self.seats: list[Seat] = []
        self.pen = turtle.Turtle(visible=False)
        self.pen.speed(0)
        self.pen.pensize(2)

        self.text = turtle.Turtle(visible=False)
        self.text.speed(0)

        self._build_grid()
        self.load_state()

    # ---------- layout ----------
    def _grid_origin(self):
        """Compute bottom-left anchor for the grid area."""
        grid_w = self.cols * (2 * self.radius) + (self.cols - 1) * self.gap_x
        grid_h = self.rows * (2 * self.radius) + (self.rows - 1) * self.gap_y
        x0 = -grid_w / 2
        y0 = -WINDOW_H / 2 + BOTTOM_MARGIN + self.radius  # keep space for footer
        y0 += (WINDOW_H - TOP_MARGIN - BOTTOM_MARGIN - grid_h) / 2
        return x0, y0

    def _build_grid(self):
        """Create seat objects with computed positions."""
        self.seats.clear()
        x0, y0 = self._grid_origin()
        for r in range(self.rows):
            for c in range(self.cols):
                x = x0 + c * (2 * self.radius + self.gap_x) + self.radius
                y = y0 + r * (2 * self.radius + self.gap_y) + self.radius
                self.seats.append(Seat(r, c, x, y, self.radius))

    # ---------- persistence ----------
    def load_state(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return
        # map by (row,col)
        state = {(d["row"], d["col"]): d for d in data.get("seats", [])}
        for seat in self.seats:
            d = state.get((seat.row, seat.col))
            if d:
                seat.from_dict(d)

    def save_state(self):
        data = {"seats": [s.to_dict() for s in self.seats]}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ---------- drawing ----------
    def draw_all(self):
        turtle.tracer(0, 0)
        self._draw_background()
        self._draw_screen_banner()
        self._draw_seats()
        self._draw_footer()
        turtle.update()

    def _draw_background(self):
        self.pen.clear()
        self.text.clear()
        bg = turtle.Turtle(visible=False)
        bg.speed(0)
        bg.up(); bg.goto(-WINDOW_W/2, -WINDOW_H/2); bg.down()
        bg.color(COLOR_BG, COLOR_BG)
        bg.begin_fill()
        for _ in range(2):
            bg.forward(WINDOW_W); bg.left(90)
            bg.forward(WINDOW_H); bg.left(90)
        bg.end_fill()
        bg.clear()  # avoid lingering heavy turtle
        del bg

    def _draw_screen_banner(self):
        # banner rectangle
        self.pen.up()
        top_y = WINDOW_H/2 - 70
        self.pen.goto(-WINDOW_W/2 + 80, top_y)
        self.pen.color(COLOR_SCREEN, COLOR_SCREEN)
        self.pen.down()
        self.pen.begin_fill()
        for _ in range(2):
            self.pen.forward(WINDOW_W - 160); self.pen.left(90)
            self.pen.forward(28); self.pen.left(90)
        self.pen.end_fill()

        # "SCREEN" label
        self.text.up()
        self.text.color(COLOR_TEXT)
        self.text.goto(0, top_y + 6)
        self.text.write("SCREEN", align="center", font=("Verdana", 16, "bold"))

    def _draw_seats(self):
        for s in self.seats:
            s.draw(self.pen)

    def _draw_footer(self):
        free = sum(not s.booked for s in self.seats)
        sold = self.rows * self.cols - free

        # counters
        self.text.up()
        self.text.color(COLOR_TEXT)
        self.text.goto(-WINDOW_W/2 + 20, -WINDOW_H/2 + 30)
        self.text.write(f"Free: {free}   Sold: {sold}",
                        align="left", font=("Verdana", 14, "bold"))

        # legend (two samples)
        legend_x = WINDOW_W/2 - 220
        legend_y = -WINDOW_H/2 + 40
        self._legend_dot(legend_x, legend_y, COLOR_SEAT_FREE, "Free")
        self._legend_dot(legend_x + 110, legend_y, COLOR_SEAT_SOLD, "Sold")

        # help
        self.text.color(COLOR_NOTE)
        self.text.goto(0, -WINDOW_H/2 + 30)
        self.text.write("Click seats to toggle   •   R = reset   •   Q / Esc = save & quit",
                        align="center", font=("Verdana", 11, "normal"))

    def _legend_dot(self, x, y, color, label):
        self.pen.up(); self.pen.goto(x, y); self.pen.down()
        self.pen.color(COLOR_SEAT_OUTLINE, color)
        self.pen.begin_fill()
        self.pen.circle(8)
        self.pen.end_fill()
        self.text.up(); self.text.color(COLOR_TEXT)
        self.text.goto(x + 18, y - 6)
        self.text.write(label, align="left", font=("Verdana", 12, "normal"))

    # ---------- interactions ----------
    def toggle_at(self, x, y):
        """Toggle a seat if click is inside; return True if any changed."""
        changed = False
        # iterate in reverse drawing order so visually topmost seats get priority
        for seat in reversed(self.seats):
            if seat.contains(x, y):
                seat.booked = not seat.booked
                changed = True
                break
        if changed:
            self.save_state()
            self.draw_all()
        return changed

    def reset_all(self):
        for s in self.seats:
            s.booked = False
        self.save_state()
        self.draw_all()


# --------------- App setup --------------- #
screen = turtle.Screen()
screen.setup(WINDOW_W, WINDOW_H)
screen.title("Cinema Seat Booking — turtle")
screen.bgcolor(COLOR_BG)

hall = CinemaHall(ROWS, COLS, SEAT_RADIUS, SEAT_GAP_X, SEAT_GAP_Y)
hall.draw_all()


# --------------- Event bindings --------------- #
def on_click(x, y):
    hall.toggle_at(x, y)

def on_reset():
    hall.reset_all()

def on_quit():
    hall.save_state()
    screen.bye()

# Mouse + keys
screen.onscreenclick(on_click, btn=1, add=False)
screen.onkey(on_reset, "r")
screen.onkey(on_quit, "q")
screen.onkey(on_quit, "Escape")
screen.listen()

turtle.done()