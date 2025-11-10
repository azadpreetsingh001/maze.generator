#include <iostream>
#include <vector>
#include <stack>
#include <queue>
#include <cstdlib>
#include <ctime>
using namespace std;

const int N = 15; 
int maze[N][N];
bool visited[N][N];

int dr[4] = {-1, 0, 1, 0};
int dc[4] = {0, 1, 0, -1};

bool valid(int r, int c) {
    return (r >= 0 && c >= 0 && r < N && c < N);
}

void generateMaze(int r, int c) {
    visited[r][c] = true;
    maze[r][c] = 0; 

    vector<int> dirs = {0, 1, 2, 3};
    random_shuffle(dirs.begin(), dirs.end());

    for (int i = 0; i < 4; i++) {
        int nr = r + dr[dirs[i]] * 2;
        int nc = c + dc[dirs[i]] * 2;

        if (valid(nr, nc) && !visited[nr][nc]) {
            maze[r + dr[dirs[i]]][c + dc[dirs[i]]] = 0; 
            generateMaze(nr, nc);
        }
    }
}

bool solveMaze() {
    queue<pair<int, int>> q;
    bool seen[N][N] = {false};
    q.push({0, 0});
    seen[0][0] = true;

    while (!q.empty()) {
        int r = q.front().first;
        int c = q.front().second;
        q.pop();

        if (r == N - 1 && c == N - 1) return true; 

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

void printMaze() {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            if (i == 0 && j == 0)
                cout << "S "; 
            else if (i == N - 1 && j == N - 1)
                cout << "E "; 
            else
                cout << (maze[i][j] ? "# " : ". ");
        }
        cout << endl;
    }
}

int main() {
    srand(time(0));

    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            maze[i][j] = 1;

    generateMaze(0, 0);

    cout << "\nGenerated Maze:\n";
    printMaze();

    if (solveMaze())
        cout << "\nPath Found!\n";
    else
        cout << "\nNo Path Found!\n";

    return 0;
}


