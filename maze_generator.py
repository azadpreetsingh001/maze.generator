# app.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
import time
from collections import deque
from matplotlib.colors import ListedColormap

# ---------- Page config ----------
st.set_page_config(page_title="Animated Maze Solver", page_icon="🧩", layout="centered")
st.title("🧩 Maze Generator & Animated Solver (DFS + BFS)")

st.markdown(
    "Generate a maze (DFS) and watch the BFS solution animate from start → end. "
    "If you deploy to Streamlit Cloud, keep maze size moderate (e.g. ≤ 30) to avoid timeouts."
)

# ---------- Inputs ----------
cols = st.columns([1, 1, 1])
with cols[0]:
    rows = st.number_input("Maze rows (cells):", min_value=3, max_value=40, value=15, step=1)
with cols[1]:
    cols_n = st.number_input("Maze cols (cells):", min_value=3, max_value=40, value=15, step=1)
with cols[2]:
    scale = st.slider("Visual scale (wall thickness)", 3, 16, 8)

seed_text = st.text_input("Optional seed (integer, blank → random):", value="")

# small safety caps
MAX_CELLS = 40
if rows > MAX_CELLS or cols_n > MAX_CELLS:
    st.warning(f"Large mazes can be slow. Consider using ≤ {MAX_CELLS} for smooth animation.")

# ---------- Maze logic ----------
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

def generate_maze_grid(r_cells, c_cells, seed=None):
    """Return grid of shape (2*r_cells+1, 2*c_cells+1): 1=wall, 0=passage."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    R = 2 * r_cells + 1
    C = 2 * c_cells + 1
    grid = np.ones((R, C), dtype=np.uint8)
    # mark cell centers as passages
    for i in range(r_cells):
        for j in range(c_cells):
            grid[2 * i + 1, 2 * j + 1] = 0

    visited = [[False] * c_cells for _ in range(r_cells)]

    def in_cell(x, y):
        return 0 <= x < r_cells and 0 <= y < c_cells

    def remove_wall_between(ax, ay, bx, by):
        wx = (2 * ax + 1 + 2 * bx + 1) // 2
        wy = (2 * ay + 1 + 2 * by + 1) // 2
        grid[wx, wy] = 0

    def dfs(cx, cy):
        visited[cx][cy] = True
        dirs = DIRS[:]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if in_cell(nx, ny) and not visited[nx][ny]:
                remove_wall_between(cx, cy, nx, ny)
                dfs(nx, ny)

    dfs(0, 0)
    return grid

def solve_bfs_on_cells(grid, r_cells, c_cells):
    """BFS on cell coordinates (0..r_cells-1, 0..c_cells-1). Returns list of cell coords path."""
    start = (0, 0)
    goal = (r_cells - 1, c_cells - 1)
    q = deque([start])
    parent = {}
    seen = {start}

    def open_between(a, b):
        ax, ay = a; bx, by = b
        wx = (2 * ax + 1 + 2 * bx + 1) // 2
        wy = (2 * ay + 1 + 2 * by + 1) // 2
        return grid[wx, wy] == 0

    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            break
        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < r_cells and 0 <= ny < c_cells and (nx, ny) not in seen:
                if open_between((x, y), (nx, ny)):
                    seen.add((nx, ny))
                    parent[(nx, ny)] = (x, y)
                    q.append((nx, ny))

    if goal not in parent and goal != start:
        return []  # no path found

    path = []
    cur = goal
    path.append(cur)
    while cur != start:
        cur = parent[cur]
        path.append(cur)
    path.reverse()
    return path

# ---------- Visualization helpers ----------
def upscaled_image_from_grid(grid, scale_factor):
    """Return an upscaled (pixel) image where each original cell becomes a block of size scale x scale."""
    return np.kron(grid, np.ones((scale_factor, scale_factor), dtype=np.uint8))

def draw_static_maze(img, path_cells=None, scale_factor=8):
    """Return matplotlib figure for a given upscaled image and optional path (list of cell coords)."""
    fig, ax = plt.subplots(figsize=(6, 6))
    cmap = ListedColormap(["#ffffff", "#000000"])  # passage white, wall black
    ax.imshow(img, cmap=cmap, interpolation="nearest")

    if path_cells:
        # draw path as a thin colored line across centers of cell-blocks
        xs, ys = [], []
        for (r, c) in path_cells:
            grid_r = 2 * r + 1
            grid_c = 2 * c + 1
            img_r = grid_r * scale_factor + scale_factor // 2
            img_c = grid_c * scale_factor + scale_factor // 2
            xs.append(img_c)  # x is column
            ys.append(img_r)  # y is row
        ax.plot(xs, ys, color="#00FF66", linewidth=max(1, scale_factor // 4), solid_capstyle='round')

    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(-0.5, img.shape[1] - 0.5)
    ax.set_ylim(img.shape[0] - 0.5, -0.5)
    ax.set_aspect('equal')
    plt.tight_layout()
    return fig

# ---------- App actions ----------
generate_btn = st.button("🎬 Generate Maze & Animate Solution")

# Show small explanation
st.caption("Tip: Enter an integer seed to get the same maze each run; leave blank for random.")

if generate_btn:
    try:
        # parse seed
        seed_val = None
        if seed_text.strip() != "":
            try:
                seed_val = int(seed_text.strip())
            except ValueError:
                seed_val = seed_text.strip()

        # generate maze grid using cell counts rows x cols_n
        grid = generate_maze_grid(rows, cols_n, seed_val)

        # build upscaled image for display
        img = upscaled_image_from_grid(grid, scale)
        st.subheader("🧱 Generated Maze")
        fig0 = draw_static_maze(img, path_cells=None, scale_factor=1)  # img already upscaled
        st.pyplot(fig0)
        plt.close(fig0)

        # solve on cell-coords
        path = solve_bfs_on_cells(grid, rows, cols_n)
        if not path:
            st.error("No path found — unexpected for a perfect maze. Try another seed/size.")
        else:
            st.subheader("🎥 Animated Solution (green path grows)")
            placeholder = st.empty()

            # animate: progressively show path prefix
            # to avoid too many redraws, we can batch frames if path is long
            n_steps = len(path)
            # Choose a reasonable frame delay (seconds)
            frame_delay = 0.03
            # For long paths, increase step size per frame to keep animation short
            if n_steps > 300:
                step_batch = max(1, n_steps // 120)
            else:
                step_batch = 1

            for end_idx in range(1, n_steps + 1, step_batch):
                subpath = path[:end_idx]
                fig = draw_static_maze(img, path_cells=subpath, scale_factor=1)
                placeholder.pyplot(fig)
                plt.close(fig)
                time.sleep(frame_delay)

            st.success("Animation finished ✅")

    except Exception as exc:
        # show the actual error message so you can debug on Streamlit Cloud
        st.error("An error occurred while generating or animating the maze.")
        st.exception(exc)
