# app.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
import time
from collections import deque
from matplotlib.colors import ListedColormap

# ---------- Page Setup ----------
st.set_page_config(page_title="Animated Maze Solver", page_icon="🧩", layout="centered")
st.title("🧩 Maze Generator & Animated Solver")

st.caption("Generate a maze using DFS and watch BFS solve it with smooth animation!")

# ---------- Input Section ----------
col1, col2, col3 = st.columns(3)
with col1:
    rows = st.number_input("Rows (cells):", min_value=3, max_value=40, value=15)
with col2:
    cols = st.number_input("Columns (cells):", min_value=3, max_value=40, value=15)
with col3:
    scale = st.slider("Cell Scale (pixels per block)", 5, 20, 8)

seed_val = st.text_input("Optional Seed (for same maze):", "")

# ---------- Maze Generation ----------
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def generate_maze(r, c, seed=None):
    if seed:
        random.seed(seed)
        np.random.seed(seed)

    grid = np.ones((2*r+1, 2*c+1), dtype=np.uint8)
    for i in range(r):
        for j in range(c):
            grid[2*i+1, 2*j+1] = 0

    visited = [[False]*c for _ in range(r)]

    def in_bounds(x, y): return 0 <= x < r and 0 <= y < c

    def remove_wall(a, b):
        ax, ay = a
        bx, by = b
        wx, wy = (2*ax+1 + 2*bx+1)//2, (2*ay+1 + 2*by+1)//2
        grid[wx, wy] = 0

    def dfs(x, y):
        visited[x][y] = True
        random.shuffle(DIRS)
        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and not visited[nx][ny]:
                remove_wall((x, y), (nx, ny))
                dfs(nx, ny)
    dfs(0, 0)
    return grid

def bfs_solve(grid, r, c):
    start, goal = (0, 0), (r-1, c-1)
    q = deque([start])
    parent = {}
    seen = {start}

    def open_between(a, b):
        ax, ay = a
        bx, by = b
        wx, wy = (2*ax+1 + 2*bx+1)//2, (2*ay+1 + 2*by+1)//2
        return grid[wx, wy] == 0

    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            break
        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < r and 0 <= ny < c and (nx, ny) not in seen:
                if open_between((x, y), (nx, ny)):
                    parent[(nx, ny)] = (x, y)
                    seen.add((nx, ny))
                    q.append((nx, ny))

    # reconstruct path
    if goal not in parent and goal != start:
        return []
    path = [goal]
    cur = goal
    while cur != start:
        cur = parent[cur]
        path.append(cur)
    path.reverse()
    return path

# ---------- Visualization ----------
def upscale_grid(grid, s):
    """Upscale grid by factor s"""
    return np.kron(grid, np.ones((s, s), dtype=np.uint8))

def draw_maze(grid, path=None, s=8):
    """Draw maze and optional path scaled properly"""
    fig, ax = plt.subplots(figsize=(6, 6))
    cmap = ListedColormap(["#ffffff", "#000000"])
    ax.imshow(grid, cmap=cmap, interpolation="nearest")

    if path:
        xs, ys = [], []
        for (r, c) in path:
            gx, gy = (2*r+1)*s + s//2, (2*c+1)*s + s//2
            xs.append(gy)
            ys.append(gx)
        ax.plot(xs, ys, color="#00FF66", linewidth=max(1, s/3), solid_capstyle="round")

    ax.set_xticks([]); ax.set_yticks([])
    ax.set_aspect("equal")
    plt.tight_layout()
    return fig

# ---------- Main Logic ----------
if st.button("🎬 Generate & Animate"):
    try:
        seed = int(seed_val) if seed_val.strip() else None
    except ValueError:
        seed = None

    grid = generate_maze(rows, cols, seed)
    img = upscale_grid(grid, scale)
    path = bfs_solve(grid, rows, cols)

    st.subheader("🧱 Generated Maze")
    st.pyplot(draw_maze(img, None, s=1))
    plt.close("all")

    if not path:
        st.error("⚠️ No path found!")
    else:
        st.subheader("🎥 Solving Animation")
        placeholder = st.empty()
        frame_delay = 0.03
        step = max(1, len(path)//200)

        for i in range(1, len(path)+1, step):
            fig = draw_maze(img, path[:i], s=1)
            placeholder.pyplot(fig)
            plt.close(fig)
            time.sleep(frame_delay)
        st.success("✅ Maze solved!")

