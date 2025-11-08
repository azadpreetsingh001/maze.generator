import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
from collections import deque
from matplotlib.colors import ListedColormap
import time

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="Maze Generator & Solver", layout="wide", page_icon="🧩")

# ---------------------- CUSTOM CSS ----------------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #1c1c1c, #232526, #414345);
    color: white;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141E30, #243B55);
    color: white;
}
h1, h2, h3 {
    text-align: center;
    color: #f5b642;
    font-family: 'Trebuchet MS', sans-serif;
}
.stButton>button {
    background-color: #f5b642;
    color: black;
    border: none;
    border-radius: 10px;
    padding: 10px 25px;
    font-weight: bold;
    transition: 0.3s;
}
.stButton>button:hover {
    background-color: #ffcc00;
    transform: scale(1.05);
}
.stNumberInput input, .stTextInput input {
    background-color: #ffffff;
    color: black;
    border-radius: 8px;
    padding: 6px;
}
div[data-testid="stMarkdownContainer"] p {
    text-align: justify;
    font-size: 16px;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ---------------------- HEADER ----------------------
st.markdown("<h1>🧩 Maze Generator & Solver</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>DFS Maze Generation | BFS Solving | Stylish Streamlit UI</h3>", unsafe_allow_html=True)
st.markdown("---")

# ---------------------- USER INPUT SECTION ----------------------
st.subheader("🎯 Enter Maze Dimensions")

colA, colB, colC = st.columns(3)
with colA:
    cell_rows = st.number_input("Enter Maze Length (Rows):", min_value=3, max_value=60, value=15, step=1)
with colB:
    cell_cols = st.number_input("Enter Maze Breadth (Columns):", min_value=3, max_value=60, value=15, step=1)
with colC:
    scale = st.slider("🧱 Wall Thickness (Visual Scale):", 4, 18, 8)

seed_input = st.text_input("🎲 Random Seed (optional):", value="")
st.markdown("---")

# ---------------------- MAZE LOGIC ----------------------
DIRS = [(-1,0),(1,0),(0,-1),(0,1)]

def generate_maze_grid(r_cells, c_cells, seed=None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    R = 2 * r_cells + 1
    C = 2 * c_cells + 1
    grid = np.ones((R, C), dtype=np.uint8)
    for i in range(r_cells):
        for j in range(c_cells):
            grid[2*i+1, 2*j+1] = 0
    visited = [[False]*c_cells for _ in range(r_cells)]

    def in_cell(nx, ny):
        return 0 <= nx < r_cells and 0 <= ny < c_cells

    def remove_wall_between(cx, cy, nx, ny):
        wx = (2*cx+1 + 2*nx+1)//2
        wy = (2*cy+1 + 2*ny+1)//2
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

def solve_maze_on_cells(grid, r_cells, c_cells):
    start = (0,0)
    goal = (r_cells-1, c_cells-1)
    q = deque([start])
    parent = {}
    seen = set([start])

    def is_open_between(a, b):
        ax, ay = a; bx, by = b
        wall_x = (2*ax+1 + 2*bx+1)//2
        wall_y = (2*ay+1 + 2*by+1)//2
        return grid[wall_x, wall_y] == 0

    while q:
        x,y = q.popleft()
        if (x,y) == goal:
            break
        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < r_cells and 0 <= ny < c_cells and (nx,ny) not in seen:
                if is_open_between((x,y),(nx,ny)):
                    seen.add((nx,ny))
                    parent[(nx,ny)] = (x,y)
                    q.append((nx,ny))

    if goal not in parent:
        return []

    path = []
    cur = goal
    while cur != start:
        path.append(cur)
        cur = parent[cur]
    path.append(start)
    path.reverse()
    return path

def visualize(grid, path_cells, scale_factor=8):
    R, C = grid.shape
    img = np.kron(grid, np.ones((scale_factor, scale_factor), dtype=np.uint8))
    cmap = ListedColormap(["#ffffff","#000000"])
    fig, ax = plt.subplots(figsize=(7,7))
    ax.imshow(img, cmap=cmap, interpolation='nearest')

    if path_cells:
        coords_x, coords_y = [], []
        for (r, c) in path_cells:
            gx, gy = 2*r+1, 2*c+1
            img_x = gx * scale_factor + scale_factor//2
            img_y = gy * scale_factor + scale_factor//2
            coords_x.append(img_y)
            coords_y.append(img_x)
        ax.plot(coords_x, coords_y, color="#00FF66", linewidth=max(1, scale_factor//3), solid_capstyle='round')

    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(-0.5, img.shape[1]-0.5)
    ax.set_ylim(img.shape[0]-0.5, -0.5)
    ax.set_aspect('equal')
    plt.tight_layout()
    return fig

# ---------------------- BUTTON & OUTPUT ----------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    generate_button = st.button("🚀 Generate & Solve Maze")

if generate_button:
    with st.spinner("🌀 Generating and Solving Maze..."):
        time.sleep(1)
        seed = None
        if seed_input.strip():
            try:
                seed = int(seed_input.strip())
            except:
                seed = seed_input.strip()

        grid = generate_maze_grid(cell_rows, cell_cols, seed)
        path = solve_maze_on_cells(grid, cell_rows, cell_cols)

        colA, colB = st.columns(2)
        with colA:
            st.subheader("🧱 Generated Maze")
            fig1 = visualize(grid, None, scale_factor=scale)
            st.pyplot(fig1)

        with colB:
            st.subheader("✅ Solved Path (Green Route)")
            fig2 = visualize(grid, path, scale_factor=scale)
            st.pyplot(fig2)

        st.success("Maze Generated and Solved Successfully! 🎉")

st.markdown("---")
st.markdown("""
### 📘 Project Summary
This *Maze Generator and Solver* is a demonstration of core *ADSA concepts*:
- *DFS (Depth-First Search)* → for generating random maze structure.  
- *BFS (Breadth-First Search)* → for finding the shortest path between start & goal.  
- *Visualization* → displays thick black walls and a glowing green solution path.

✨ Developed using Streamlit for web presentation. The logic mirrors C++ implementations using DFS & BFS techniques.
""")