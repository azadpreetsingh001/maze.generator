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
custom_css = """
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, #0f2027, #203a43, #2c5364);
    color: white;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #232526, #414345);
    color: white;
}
h1, h2, h3, h4 {
    text-align: center;
    color: #FFD700;
    font-family: 'Trebuchet MS', sans-serif;
}
.stButton>button {
    background: linear-gradient(90deg, #f5b642, #ffcc00);
    color: black;
    border: none;
    border-radius: 10px;
    padding: 10px 25px;
    font-weight: bold;
    transition: 0.3s;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #ffcc00, #ffee88);
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
    color: #f2f2f2;
}
hr {
    border: 1px solid #f5b642;
}
.card {
    background-color: rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 0px 10px rgba(255,255,255,0.2);
    margin-top: 10px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------- HEADER ----------------------
st.markdown("<h1>🧩 Maze Generator & Solver</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>DFS Maze Generation | BFS Path Solving | Group 3</h3>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------- INPUTS ----------------------
st.subheader("🎯 Maze Configuration")

colA, colB, colC = st.columns(3)
with colA:
    cell_rows = st.number_input("Enter Maze Length (Rows):", min_value=3, max_value=60, value=15, step=1)
with colB:
    cell_cols = st.number_input("Enter Maze Breadth (Columns):", min_value=3, max_value=60, value=15, step=1)
with colC:
    scale = st.slider("🧱 Wall Thickness (Visual Scale):", 4, 18, 8)



# ---------------------- LOGIC ----------------------
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

def bfs_solve(grid, r_cells, c_cells):
    start = (0,0)
    goal = (r_cells-1, c_cells-1)
    q = deque([start])
    parent = {}
    seen = set([start])

    def open_between(a, b):
        ax, ay = a; bx, by = b
        wx = (2*ax+1 + 2*bx+1)//2
        wy = (2*ay+1 + 2*by+1)//2
        return grid[wx, wy] == 0

    steps = []
    while q:
        x,y = q.popleft()
        steps.append((x,y))
        if (x,y) == goal:
            break
        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < r_cells and 0 <= ny < c_cells and (nx,ny) not in seen:
                if open_between((x,y),(nx,ny)):
                    seen.add((nx,ny))
                    parent[(nx,ny)] = (x,y)
                    q.append((nx,ny))

    path = []
    if goal in parent:
        cur = goal
        while cur != start:
            path.append(cur)
            cur = parent[cur]
        path.append(start)
        path.reverse()
    return path, steps

def visualize(grid, path_cells=None, scale_factor=8):
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

# ---------------------- BUTTON ----------------------
center_col = st.columns([1,2,1])[1]
with center_col:
    if st.button("🚀 Generate & Solve Maze"):
        with st.spinner("🌀 Generating Maze and Solving Step-by-Step..."):
            time.sleep(1)
            seed = None
            if seed_input.strip():
                try:
                    seed = int(seed_input.strip())
                except:
                    seed = seed_input.strip()

            grid = generate_maze_grid(cell_rows, cell_cols, seed)
            path, steps = bfs_solve(grid, cell_rows, cell_cols)

            colA, colB = st.columns(2)
            with colA:
                st.markdown("<div class='card'><h3>🧱 Generated Maze</h3></div>", unsafe_allow_html=True)
                fig1 = visualize(grid, None, scale_factor=scale)
                st.pyplot(fig1)

            with colB:
                st.markdown("<div class='card'><h3>✅ Solved Path (Green Route)</h3></div>", unsafe_allow_html=True)
                fig2 = visualize(grid, path, scale_factor=scale)
                st.pyplot(fig2)

            # ---------------------- EXPLANATION ----------------------
            st.markdown("<div class='card'><h3>🧠 Step-by-Step Explanation of BFS Solving</h3>", unsafe_allow_html=True)
            explanation = f"""
            - The **Breadth-First Search (BFS)** algorithm starts at the **top-left corner (0,0)**.
            - It explores all possible paths **level by level**, ensuring the **shortest path** is found.
            - Each move checks four directions: *Up, Down, Left, Right*.
            - Whenever BFS finds a connected open cell, it marks it as *visited* and stores its *parent*.
            - Once the **bottom-right corner ({cell_rows-1},{cell_cols-1})** is reached,
              the algorithm **backtracks** from the goal to the start using the parent dictionary.
            - This backtracking produces the **green path** shown above, representing the **shortest route**.
            - In total, BFS expanded **{len(steps)} cells** and discovered the final path length of **{len(path)}**.
            """
            st.markdown(explanation)
            st.markdown("</div>", unsafe_allow_html=True)
            st.success("🎉 Maze Generated and Solved Successfully with Explanation!")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
### 📘 Project Summary
This interactive *Maze Generator and Solver* demonstrates two fundamental **graph algorithms**:
- **DFS (Depth-First Search)** → for generating random, unique maze patterns.
- **BFS (Breadth-First Search)** → for finding the *shortest path* through the maze.
  Made By Dilwinder Singh (24BCS10080)
  Azadpreet Singh (24BCS10082)
  Jashandeep Singh (24BCS10068)
""")
