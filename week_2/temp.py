"""Falling Sand Simulation — assignment template.

Your task: implement the physics inside ``SandSim.update()`` so that
sand and water behave like they do in real life.

  Sand  -> falls straight down; if blocked, slides diagonally downhill.
  Water -> falls like sand, but when it *can't* fall it spreads sideways.

Only SAND and WATER are required. Fire, smoke, walls, wood, etc. are a
bonus — add a new entry to :class:`Material`, a colour, and a rule.

Run it:  uv run python assignment/temp.py
"""

from __future__ import annotations

from enum import IntEnum

import numpy as np
import pygame


class Material(IntEnum):
    """Every cell in the grid holds one of these values.

    IntEnum means each name is also a normal integer, so a grid can be a
    plain NumPy array of numbers. EMPTY must stay 0 so that a fresh grid
    (which NumPy fills with zeros) starts out as empty space.
    """

    EMPTY = 0
    SAND = 1
    WATER = 2
    WALL = 3
    SMOKE = 4
    # BONUS: add more materials here, e.g.
    # WALL = 3   (immovable — never update it)
    # FIRE = 4   (lives a few ticks, then becomes EMPTY)
    # SMOKE = 5  (rises instead of falling, then fades)


# The colour (R, G, B) drawn for each material.
PALETTE = {
    Material.EMPTY: (0, 0, 0),
    Material.SAND: (194, 178, 128),
    Material.WATER: (52, 120, 235),
    Material.WALL: (120, 120, 120),
    Material.SMOKE: (150, 150, 150)
}
# Turned into a NumPy array so that looking up a cell's colour is a single
# fast indexing operation: COLORS[grid] gives the RGB value of every cell.
_COLORS = np.array([PALETTE[m] for m in Material], dtype=np.uint8)

# One shared random generator for the whole program. Everything that needs
# a coin-flip (diagonal direction, which side to move) pulls from this.
_rng = np.random.default_rng()


class SandSim:
    """Holds the grid and does the physics + rendering.

    The grid is ``self._types``, a 2D NumPy array of shape (HEIGHT, WIDTH)
    where grid[y, x] is the material at row ``y`` (0 = top) and column
    ``x`` (0 = left).
    """

    def __init__(self, width: int, height: int, cell_size: int = 4, fps: int = 60) -> None:
        self.cell_size = cell_size
        self.fps = fps
        self.brush = Material.SAND
        self.brush_radius = 2
        self.resize_cells(width, height)

    # ------------------------------------------------------------------ #
    # Grid lifecycle
    # ------------------------------------------------------------------ #
    def resize_cells(self, width: int, height: int) -> None:
        """Replace the grid with a fresh empty one of the given size."""
        self.width = int(width)
        self.height = int(height)
        # NumPy fills with zeros = Material.EMPTY. Good.
        self._types = np.zeros((self.height, self.width), dtype=np.uint8)
        self._age = np.zeros((self.height, self.width), dtype=np.uint16)

    def clear(self) -> None:
        """Reset every cell to empty space."""
        self._types[:] = 0
        self._age[:] = 0

    # ------------------------------------------------------------------ #
    # Painting (mouse input)
    # ------------------------------------------------------------------ #
    def paint_at(self, x: int, y: int) -> None:
        """Place the current brush material in a disc of cells at (x, y).

        ``x``/``y`` are in *grid* coordinates (screen pixels / cell_size).
        """
        r = self.brush_radius
        x0, x1 = max(0, x - r), min(self.width, x + r + 1)
        y0, y1 = max(0, y - r), min(self.height, y + r + 1)
        if x1 <= x0 or y1 <= y0:
            return
        # mgrid gives two grids of y- and x-coordinates over the block;
        # the `disc` mask keeps only cells within a circle of radius r.
        yy, xx = np.mgrid[y0:y1, x0:x1]
        disc = ((xx - x) ** 2 + (yy - y) ** 2) <= r * r
        xs, ys = xx[disc], yy[disc]
        self._types[ys, xs] = int(self.brush)

    # ------------------------------------------------------------------ #
    # Physics
    # ------------------------------------------------------------------ #
    def update(self) -> None:
        """Advance the simulation by one tick. This is YOUR job.

        Rules to implement:

        * Process rows from the BOTTOM up (y = height-1 .. 0). If you go top
          down, a grain falls several cells per tick and flickers.
        * Process columns left-to-right but in a different random order each
          tick, so falling looks symmetrical instead of leaning one way.
        * SAND:
            1. if the cell directly below is EMPTY   -> move straight down
            2. else pick a random side; if the cell down-left or down-right
               is EMPTY -> move diagonally there
            3. else stay put (it rests)
        * WATER: the same as sand, PLUS:
            4. if it couldn't fall at all, move into a random EMPTY
               left/right neighbour — this is what makes water pool flat.

        Hint: if you write straight into the grid you'll re-process cells
        that already moved. Copy the grid before the loop, read from the
        copy, and write the result into the live grid (or vice versa).
        """

        G = self._types
        Gp = G.copy()
        H, W = self.height, self.width
        
        A = self._age
        Ap = A.copy()

        for y in range(H - 1, -1, -1):
            row = G[y, :]
            is_solid = (row == Material.SAND) | (row == Material.WATER)
            has_smoke = (row == Material.SMOKE).any()
            
            if not is_solid.any() and not has_smoke:
                continue

            can_fall = y + 1 < H
            below = Gp[y + 1, :] if can_fall else None

            #vertical fall
            if can_fall:
                fall_mask = is_solid & (below == Material.EMPTY)
                Gp[y + 1, fall_mask] = row[fall_mask]
                Gp[y, fall_mask] = Material.EMPTY
                remaining = is_solid & ~fall_mask
            else:
                remaining = is_solid.copy()

        
            #diagonal slide
            if can_fall and remaining.any():
                below = Gp[y + 1, :]
                xs = np.nonzero(remaining)[0]

                left_ok = (xs - 1 >= 0) & (below[np.clip(xs - 1, 0, W - 1)] == Material.EMPTY)
                right_ok = (xs + 1 < W) & (below[np.clip(xs + 1, 0, W - 1)] == Material.EMPTY)

                coin = np.random.random(xs.size) < 0.5
                want_left = (left_ok & right_ok & coin) | (left_ok & ~right_ok)
                want_right = (left_ok & right_ok & ~coin) | (right_ok & ~left_ok)
                dx = np.where(want_left, -1, np.where(want_right, 1, 0))

                move_xs = xs[dx != 0]
                move_targets = move_xs + dx[dx != 0]

                if move_xs.size:
                    order = np.random.permutation(move_xs.size)
                    move_xs, move_targets = move_xs[order], move_targets[order]
                    _, first_idx = np.unique(move_targets, return_index=True)
                    wx, wt = move_xs[first_idx], move_targets[first_idx]

                    Gp[y + 1, wt] = row[wx]
                    Gp[y, wx] = Material.EMPTY
                    below[wt] = row[wx]
                    remaining[wx] = False

            #  Sideways spread — water only
            water_remaining = remaining & (row == Material.WATER)
            if water_remaining.any():
                live = Gp[y, :]
                xs = np.nonzero(water_remaining)[0]

                left_ok = (xs - 1 >= 0) & (live[np.clip(xs - 1, 0, W - 1)] == Material.EMPTY)
                right_ok = (xs + 1 < W) & (live[np.clip(xs + 1, 0, W - 1)] == Material.EMPTY)

                coin = np.random.random(xs.size) < 0.5
                want_left = (left_ok & right_ok & coin) | (left_ok & ~right_ok)
                want_right = (left_ok & right_ok & ~coin) | (right_ok & ~left_ok)
                dx = np.where(want_left, -1, np.where(want_right, 1, 0))

                move_xs = xs[dx != 0]
                move_targets = move_xs + dx[dx != 0]

                if move_xs.size:
                    order = np.random.permutation(move_xs.size)
                    move_xs, move_targets = move_xs[order], move_targets[order]
                    _, first_idx = np.unique(move_targets, return_index=True)
                    wx, wt = move_xs[first_idx], move_targets[first_idx]

                    Gp[y, wt] = Material.WATER
                    Gp[y, wx] = Material.EMPTY
                    
            
            #smoke
            
            smoke_row = row == Material.SMOKE
            if not smoke_row.any():
                continue
            
            ages = A[y, :] + 1
            
            dying = smoke_row & (ages >= 40)
            Gp[y, dying] = Material.EMPTY
            Ap[y, dying] = 0
            alive = smoke_row & ~dying
            if not alive.any():
                continue
            
            can_rise = y - 1 >= 0    
            if not can_rise:
                Ap[y, alive] = ages[alive]
                continue
            
            above = Gp[y - 1, :]
            
            #up
            rise_mask = alive & (above == Material.EMPTY)
            Gp[y - 1, rise_mask] = Material.SMOKE
            Ap[y - 1, rise_mask] = ages[rise_mask]
            Gp[y, rise_mask] = Material.EMPTY        
            Ap[y, rise_mask] = 0
            remaining_smoke = alive & ~rise_mask
            
            #diagonal
            if remaining_smoke.any():
                above = Gp[y - 1, :]
                xs = np.nonzero(remaining_smoke)[0]
                
                left_ok = (xs - 1 >= 0) & (above[np.clip(xs - 1, 0, W - 1)] == Material.EMPTY)
                right_ok = (xs + 1 < W) & (above[np.clip(xs + 1, 0, W - 1)] == Material.EMPTY)
                
                coin = np.random.random(xs.size) < 0.5
                want_left = (left_ok & right_ok & coin) | (left_ok & ~right_ok)
                want_right = (left_ok & right_ok & ~coin) | (right_ok & ~left_ok)
                dx = np.where(want_left, -1, np.where(want_right, 1, 0))
                
                move_xs = xs[dx != 0]
                move_targets = move_xs + dx[dx != 0]
                
                if move_xs.size:
                    order = np.random.permutation(move_xs.size)
                    move_xs, move_targets = move_xs[order], move_targets[order]
                    _, first_idx = np.unique(move_targets, return_index=True)
                    wx, wt = move_xs[first_idx], move_targets[first_idx]
                    
                    Gp[y - 1, wt] = Material.SMOKE
                    Ap[y - 1, wt] = ages[wx]
                    Gp[y, wx] = Material.EMPTY
                    Ap[y, wx] = 0
                    remaining_smoke[wx] = False
                    
                Ap[y, remaining_smoke] = ages[remaining_smoke]

        self._types = Gp
        self._age = Ap

                    
                    
            
            

    # ------------------------------------------------------------------ #
    # Rendering (boilerplate — nothing to do here)
    # ------------------------------------------------------------------ #
    def surface(self) -> pygame.Surface:
        """Snapshot the grid as a pygame.Surface, scaled up by cell_size.

        _COLORS[grid] turns the cell-material grid into a grid of RGB
        pixels in one shot. pygame expects the axes as (WIDTH, HEIGHT),
        numpy stores them as (HEIGHT, WIDTH), so transpose swaps them back.
        """
        rgb = _COLORS[self._types]
        surf = pygame.surfarray.make_surface(
            np.ascontiguousarray(np.transpose(rgb, (1, 0, 2)))
        )
        if self.cell_size > 1:
            surf = pygame.transform.scale(
                surf, (self.width * self.cell_size, self.height * self.cell_size)
            )
        return surf


    


def main() -> None:
    """Setup + event loop. Boilerplate — nothing to do here."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Falling Sand — 1 sand, 2 water, 0 erase, [ ] brush, C clear")
    clock = pygame.time.Clock()

    sim = SandSim(800 // 4, 600 // 4)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE:
                    running = False
                elif k == pygame.K_1:
                    sim.brush = Material.SAND
                elif k == pygame.K_2:
                    sim.brush = Material.WATER
                elif k == pygame.K_3: 
                    sim.brush = Material.WALL
                elif k == pygame.K_4:
                    sim.brush = Material.SMOKE
                elif k in (pygame.K_0, pygame.K_e):
                    sim.brush = Material.EMPTY
                elif k == pygame.K_LEFTBRACKET:
                    sim.brush_radius = max(1, sim.brush_radius - 1)
                elif k == pygame.K_RIGHTBRACKET:
                    sim.brush_radius = min(40, sim.brush_radius + 1)
                elif k == pygame.K_c:
                    sim.clear()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                sim.resize_cells(event.size[0] // sim.cell_size, event.size[1] // sim.cell_size)

        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            sim.paint_at(mx // sim.cell_size, my // sim.cell_size)

        sim.update()
        screen.blit(sim.surface(), (0, 0))

        pygame.display.flip()
        clock.tick(sim.fps)

    pygame.quit()


if __name__ == "__main__":
    main()