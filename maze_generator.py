import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
from collections import deque
from matplotlib.colors import ListedColormap
import time

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Animated Maze Solver", page_icon="🧩", layout="centered")
st.title("🧩 Maze Generator & Animated Solver (DFS + BFS)")

st.markdown("""
This app **generates and solves a maze** using:
- 🌀 **DFS (Depth-First Search)** → Maze Generation  
- 🧭 **BFS (Breadth-First Search)** → Path Finding  
- 🎬 **Animated Solution Path** → Green path grows from start to end  
""")

# --- User Inputs ---
rows = st.number_input("Enter Maze Rows (Height):", min_value=5, max_value=50, value=15)
cols = st.number_input("Enter Maze Columns (Width):", min_value=5, max_value=50, value=15)
seed = st.text_input("Enter a Random Seed (optional):", "")

if seed.strip():
    random.seed(int(seed))
else:
    random.seed()

# Directions (Up, Down, Left, Right)
directions = [(-1,0), (1,0), (0,-1), (0,1)]

# --- Maze Generation using DFS ---
def generate_maze(n, m):
    maze = np.ones((n, m), dtype=int)  # 1 = wall, 0 = path
    visited = np.zeros((n, m), dtype=bool)

    def is_valid(x, y):
        return 0 <= x < n and 0 <= y < m

    def dfs(x, y):
        visited[x][y] = True
        maze[x][y] = 0
        dirs = directions[:]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx*2, y + dy*2
            if is_valid(nx, ny) and not visited[nx][ny]:
                maze[x + dx][y + dy] = 0
                dfs(nx, ny)

    dfs(0, 0)
    return maze

# --- Maze Solving using BFS ---
def solve_maze(maze):
    n, m = maze.shape
    start, end = (0, 0), (n-1, m-1)
    q = deque([start])
    visited = np.zeros_like(maze, dtype=bool)
    parent = {}

    while q:
        x, y = q.popleft()
        if (x, y) == end:
            break
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < m and not visited[nx][ny] and maze[nx][ny] == 0:
                visited[nx][ny] = True
                parent[(nx, ny)] = (x, y)
                q.append((nx, ny))

    # Reconstruct path
    path = []
    cell = end
    while cell in parent:
        path.append(cell)
        cell = parent[cell]
    path.append(start)
    path.reverse()
    return path

# --- Visualization Function ---
def visualize_maze(maze, path=None):
    n, m = maze.shape
    maze_color = np.copy(maze).astype(float)
    cmap = ListedColormap(["white", "black", "limegreen"])

    if path:
        for (x, y) in path:
            maze_color[x, y] = 2  # mark solution in green

    fig, ax = plt.subplots(figsize=(6,6))
    ax.imshow(maze_color, cmap=cmap, interpolation='nearest')
    ax.set_xticks([]); ax.set_yticks([])
    ax.grid(which='major', color='black', linewidth=1.5)
    ax.set_xticks(np.arange(-.5, m, 1))
    ax.set_yticks(np.arange(-.5, n, 1))
    ax.tick_params(which='both', bottom=False, left=False, labelbottom=False, labelleft=False)
    return fig

# --- Animate Path Function ---
def animate_solution(maze, path):
    placeholder = st.empty()
    n, m = maze.shape
    maze_color = np.copy(maze).astype(float)
    cmap = ListedColormap(["white", "black", "limegreen"])

    for i in range(len(path)):
        x, y = path[i]
        maze_color[x, y] = 2  # paint cell green
        fig, ax = plt.subplots(figsize=(6,6))
        ax.imshow(maze_color, cmap=cmap, interpolation='nearest')
        ax.set_xticks([]); ax.set_yticks([])
        ax.grid(which='major', color='black', linewidth=1.5)
        ax.set_xticks(np.arange(-.5, m, 1))
        ax.set_yticks(np.arange(-.5, n, 1))
        ax.tick_params(which='both', bottom=False, left=False, labelbottom=False, labelleft=False)
        placeholder.pyplot(fig)
        time.sleep(0.05)  # controls animation speed

# --- Main Logic ---
if st.button("🎬 Generate & Animate Maze"):
    with st.spinner("Generating and Solving Maze..."):
        maze = generate_maze(rows, cols)
        path = solve_maze(maze)

        st.subheader("🧱 Generated Maze")
        fig1 = visualize_maze(maze)
        st.pyplot(fig1)

        st.subheader("🎥 Animated Solution Path (Green Path)")
        animate_solution(maze, path)

        st.success("✅ Animation Complete! Maze Solved.")

# --- Explanation ---
st.markdown("""
---
### 🧠 How It Works:
- **DFS (Depth-First Search)** builds the maze by carving paths randomly.  
- **BFS (Breadth-First Search)** finds the **shortest route** from start (top-left) to end (bottom-right).  
- The **green line** grows cell-by-cell to show how the path travels.

### 🎨 Color Legend:
- ⚪ White → Path  
- ⬛ Black → Wall (thick)  
- 🟢 Green → Animated solution path  
""")
