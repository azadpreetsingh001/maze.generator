#include <iostream>
#include <vector>
#include <stack>
#include <queue>
#include <cstdlib>
#include <ctime>
using namespace std;

const int N = 10; // Maze size (you can change)
int maze[N][N];   // 0 = path, 1 = wall
bool visited[N][N];

// Directions: up, right, down, left
int dr[4] = {-1, 0, 1, 0};
int dc[4] = {0, 1, 0, -1};

// Check valid cell
bool valid(int r, int c) {
    return (r >= 0 && c >= 0 && r < N && c < N);
}

// Maze generation using DFS
void generateMaze(int r, int c) {
    visited[r][c] = true;
    maze[r][c] = 0; // path

    // Randomize directions
    vector<int> dirs = {0, 1, 2, 3};
    random_shuffle(dirs.begin(), dirs.end());

    for (int i = 0; i < 4; i++) {
        int nr = r + dr[dirs[i]] * 2;
        int nc = c + dc[dirs[i]] * 2;

        if (valid(nr, nc) && !visited[nr][nc]) {
            maze[r + dr[dirs[i]]][c + dc[dirs[i]]] = 0; // remove wall
            generateMaze(nr, nc);
        }
    }
}

// BFS to solve the maze (shortest path)
bool solveMaze() {
    queue<pair<int, int>> q;
    bool seen[N][N] = {false};
    q.push({0, 0});
    seen[0][0] = true;

    while (!q.empty()) {
        int r = q.front().first;
        int c = q.front().second;
        q.pop();

        if (r == N - 1 && c == N - 1) return true; // reached end

        for (int i = 0; i < 4; i++) {
            int nr = r + dr[i];
            int nc = c + dc[i];
            if (valid(nr, nc) && maze[nr][nc] == 0 && !seen[nr][nc]) {
                seen[nr][nc] = true;
                q.push({nr, nc});
            }
        }
    }
    return false;
}

// Print maze
void printMaze() {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            if (i == 0 && j == 0)
                cout << "S "; // Start
            else if (i == N - 1 && j == N - 1)
                cout << "E "; // End
            else
                cout << (maze[i][j] ? "# " : ". ");
        }
        cout << endl;
    }
}

int main() {
    srand(time(0));

    // Fill with walls
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            maze[i][j] = 1;

    // Generate maze
    generateMaze(0, 0);

    cout << "\nGenerated Maze:\n";
    printMaze();

    // Solve maze
    if (solveMaze())
        cout << "\nPath Found!\n";
    else
        cout << "\nNo Path Found!\n";

    return 0;
}
