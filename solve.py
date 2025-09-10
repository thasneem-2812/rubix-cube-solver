import random
import copy
from tkinter import Tk, Canvas, Button, Label, Scale, HORIZONTAL, filedialog

# --------- Cube Model ---------

FACES = ['U', 'D', 'F', 'B', 'L', 'R']
MOVES = [f + s for f in FACES for s in ["", "'"]]

FACE_COLORS = {
    'U': 'white',
    'D': 'yellow',
    'F': 'green',
    'B': 'blue',
    'L': 'orange',
    'R': 'red'
}

def create_cube():
    return {face: [[face] * 3 for _ in range(3)] for face in FACES}

def rotate_face(face):
    return [list(row) for row in zip(*face[::-1])]

def rotate_face_ccw(face):
    return [list(row) for row in zip(*face)][::-1]

ROTATION_MAP = {
    'U': ([('F', 0), ('R', 0), ('B', 0), ('L', 0)], True),
    'D': ([('F', 2), ('L', 2), ('B', 2), ('R', 2)], True),
    'F': ([('U', 2), ('R', 'col0'), ('D', 0), ('L', 'col2')], False),
    'B': ([('U', 0), ('L', 'col0'), ('D', 2), ('R', 'col2')], False),
    'L': ([('U', 'col0'), ('F', 'col0'), ('D', 'col0'), ('B', 'col2')], False),
    'R': ([('U', 'col2'), ('B', 'col0'), ('D', 'col2'), ('F', 'col2')], False)
}

def get_line(cube, face, idx):
    if isinstance(idx, int):
        return cube[face][idx][:]
    elif isinstance(idx, str) and 'col' in idx:
        col = int(idx[3])
        return [cube[face][i][col] for i in range(3)]

def set_line(cube, face, idx, values):
    if isinstance(idx, int):
        cube[face][idx] = values
    elif isinstance(idx, str) and 'col' in idx:
        col = int(idx[3])
        for i in range(3):
            cube[face][i][col] = values[i]

def apply_move(cube, move):
    cube = copy.deepcopy(cube)
    face = move[0]
    prime = len(move) > 1 and move[1] == "'"
    neighbors, is_row = ROTATION_MAP[face]

    # rotate face
    cube[face] = rotate_face_ccw(cube[face]) if prime else rotate_face(cube[face])

    # rotate neighbors
    lines = [get_line(cube, f, idx) for f, idx in neighbors]
    lines = lines[1:] + lines[:1] if prime else lines[-1:] + lines[:-1]
    for (f, idx), line in zip(neighbors, lines):
        set_line(cube, f, idx, line)
    return cube

def apply_moves(cube, moves):
    for move in moves:
        cube = apply_move(cube, move)
    return cube

def is_solved(cube):
    return all(all(cell == face for row in cube[face] for cell in row) for face in FACES)

# --------- IDA* Solver ---------

def cube_to_string(cube):
    return ''.join(''.join(''.join(row) for row in cube[face]) for face in FACES)

def heuristic(cube):
    return sum(cell != face for face in FACES for row in cube[face] for cell in row) // 8

def dfs(cube, path, g, threshold, visited):
    f = g + heuristic(cube)
    if f > threshold:
        return f, None
    if is_solved(cube):
        return f, path
    min_threshold = float('inf')
    for move in MOVES:
        new_cube = apply_move(cube, move)
        state = cube_to_string(new_cube)
        if state in visited:
            continue
        visited.add(state)
        t, result = dfs(new_cube, path + [move], g + 1, threshold, visited)
        if result:
            return t, result
        if t < min_threshold:
            min_threshold = t
        visited.remove(state)
    return min_threshold, None

def ida_star_solve(start_cube):
    threshold = heuristic(start_cube)
    while True:
        visited = set()
        visited.add(cube_to_string(start_cube))
        t, result = dfs(start_cube, [], 0, threshold, visited)
        if result:
            return result
        if t == float('inf'):
            return None
        threshold = t

# --------- GUI & Logic ---------

CELL_SIZE = 40
cube = create_cube()
canvas = None
solution_label = None
animation_speed = 500
scramble_moves = []
solution_moves = []
scramble_depth = 8

face_positions = {
    'U': (3, 0),
    'L': (0, 3),
    'F': (3, 3),
    'R': (6, 3),
    'B': (9, 3),
    'D': (3, 6),
}

def draw_cube():
    canvas.delete("all")
    for face in FACES:
        fx, fy = face_positions[face]
        for i in range(3):
            for j in range(3):
                color = FACE_COLORS[cube[face][i][j]]
                x0 = (fx + j) * CELL_SIZE
                y0 = (fy + i) * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='black')

def show_move_history(moves, title="Moves"):
    move_str = f"{title}: " + ' '.join(moves) if moves else f"{title}: (none)"
    solution_label.config(text=move_str)

def animate_solution(moves, index=0):
    global cube
    if index >= len(moves):
        return
    move = moves[index]
    cube = apply_move(cube, move)
    draw_cube()
    root.after(animation_speed, animate_solution, moves, index + 1)

def update_speed(value):
    global animation_speed
    animation_speed = int(value)

def update_scramble_depth(value):
    global scramble_depth
    scramble_depth = int(value)

def scramble_cube():
    global cube, scramble_moves
    scramble_moves = random.choices(MOVES, k=scramble_depth)
    cube = apply_moves(create_cube(), scramble_moves)
    show_move_history(scramble_moves, title="Scramble")
    draw_cube()

def solve_cube():
    global cube, solution_moves
    solution_moves = ida_star_solve(cube)
    if solution_moves:
        show_move_history(solution_moves, title="Solution")
        animate_solution(solution_moves)

def reset_cube():
    global cube
    cube = create_cube()
    show_move_history([], title="Reset")
    draw_cube()

def export_solution():
    if not scramble_moves and not solution_moves:
        return
    with open("rubik_solution.txt", "w") as f:
        f.write("Scramble Moves:\n")
        f.write(' '.join(scramble_moves) + "\n\n")
        f.write("Solution Moves:\n")
        f.write(' '.join(solution_moves) + "\n")
    solution_label.config(text="Exported to rubik_solution.txt")

def run_gui():
    global canvas, solution_label, root
    root = Tk()
    root.title("Rubik's Cube Solver")

    canvas = Canvas(root, width=600, height=600)
    canvas.pack()

    solution_label = Label(root, text="Moves will appear here", font=('Arial', 12))
    solution_label.pack(pady=5)

    # Speed slider
    Label(root, text="Animation Speed (ms):").pack()
    Scale(root, from_=100, to=1000, orient=HORIZONTAL, command=update_speed).pack()

    # Scramble depth slider
    # Scramble depth slider (limited to 10 for performance)
    Label(root, text="Scramble Length (max 10):").pack()
    Scale(root, from_=1, to=10, orient=HORIZONTAL, command=update_scramble_depth).pack()

    # Buttons
    Button(root, text="Scramble", command=scramble_cube).pack(side='left', padx=10, pady=10)
    Button(root, text="Solve", command=solve_cube).pack(side='left', padx=10, pady=10)
    Button(root, text="Reset", command=reset_cube).pack(side='left', padx=10, pady=10)
    Button(root, text="Export", command=export_solution).pack(side='left', padx=10, pady=10)

    draw_cube()
    root.mainloop()

# Launch GUI
if __name__ == "__main__":
    run_gui()
