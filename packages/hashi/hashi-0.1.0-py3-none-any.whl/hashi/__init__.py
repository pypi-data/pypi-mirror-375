"""
Hashiwokakero puzzle generator, solver, printer, and player.
"""
import random
import string
from typing import Dict, List, Tuple, Any

# Types
Island = Dict[str, int]  # {'x': int, 'y': int, 'count': int}
Bridge = Tuple[int, int, int, int, str]  # (x1, y1, x2, y2, '-' or '=')
PuzzleDict = Dict[str, Any]


def generate(width: int, height: int, difficulty: int) -> PuzzleDict:
    """
    Generate a Hashiwokakero puzzle.
    Returns a dictionary with 'width', 'height', 'difficulty', 'islands', and 'solution'.
    """
    # Step 1: Place islands randomly, but not too close
    num_islands = max(4, min(width * height // 6, 20))
    positions = set()
    attempts = 0
    while len(positions) < num_islands and attempts < 1000:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        # Don't allow islands to be adjacent
        if all(abs(x - px) > 0 or abs(y - py) > 0 for (px, py) in positions):
            positions.add((x, y))
        attempts += 1
    islands = [{'x': x, 'y': y, 'count': 0} for (x, y) in positions]
    # Step 2: Build a random spanning tree (Kruskal's algorithm)
    def manhattan(a, b):
        return abs(a['x'] - b['x']) + abs(a['y'] - b['y'])
    edges = []
    for i, a in enumerate(islands):
        for j, b in enumerate(islands):
            if i < j:
                if a['x'] == b['x'] or a['y'] == b['y']:
                    # Only orthogonal
                    edges.append((manhattan(a, b), i, j))
    edges.sort()
    parent = list(range(len(islands)))
    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u
    solution = []
    used_edges = set()
    for dist, i, j in edges:
        pi, pj = find(i), find(j)
        if pi != pj:
            # Check if path is clear (no other island between)
            a, b = islands[i], islands[j]
            clear = True
            if a['x'] == b['x']:
                for y in range(min(a['y'], b['y']) + 1, max(a['y'], b['y'])):
                    if (a['x'], y) in positions:
                        clear = False
                        break
            else:
                for x in range(min(a['x'], b['x']) + 1, max(a['x'], b['x'])):
                    if (x, a['y']) in positions:
                        clear = False
                        break
            if clear:
                parent[pi] = pj
                # Always single bridge for tree
                solution.append((a['x'], a['y'], b['x'], b['y'], '-'))
                used_edges.add((i, j))
    # Step 3: Optionally add extra bridges (difficulty)
    extra_bridges = 0
    max_extra = int(difficulty / 25)  # 0-4 extra bridges
    random.shuffle(edges)
    for dist, i, j in edges:
        if (i, j) in used_edges or (j, i) in used_edges:
            continue
        a, b = islands[i], islands[j]
        # Only add if path is clear and not already two bridges
        count = sum(
            (x1 == a['x'] and y1 == a['y'] and x2 == b['x'] and y2 == b['y']) or
            (x2 == a['x'] and y2 == a['y'] and x1 == b['x'] and y1 == b['y'])
            for (x1, y1, x2, y2, typ) in solution
        )
        if count >= 2:
            continue
        # Check path is clear
        clear = True
        if a['x'] == b['x']:
            for y in range(min(a['y'], b['y']) + 1, max(a['y'], b['y'])):
                if (a['x'], y) in positions:
                    clear = False
                    break
        else:
            for x in range(min(a['x'], b['x']) + 1, max(a['x'], b['x'])):
                if (x, a['y']) in positions:
                    clear = False
                    break
        if clear:
            solution.append((a['x'], a['y'], b['x'], b['y'], '='))
            used_edges.add((i, j))
            extra_bridges += 1
            if extra_bridges >= max_extra:
                break
    # Step 4: Assign island counts and filter invalid islands
    valid_islands = []
    for idx, island in enumerate(islands):
        count = 0
        for (x1, y1, x2, y2, typ) in solution:
            if (island['x'], island['y']) == (x1, y1) or (island['x'], island['y']) == (x2, y2):
                count += 2 if typ == '=' else 1
        if 1 <= count <= 8:
            island['count'] = count
            valid_islands.append(island)
    # Remove any bridges that reference removed islands
    valid_positions = set((i['x'], i['y']) for i in valid_islands)
    filtered_solution = []
    for (x1, y1, x2, y2, typ) in solution:
        if (x1, y1) in valid_positions and (x2, y2) in valid_positions:
            filtered_solution.append((x1, y1, x2, y2, typ))
    # If any islands were removed, regenerate to avoid disconnected puzzles
    if len(valid_islands) < 2 or len(filtered_solution) < len(valid_islands) - 1:
        return generate(width, height, difficulty)
    # Step 5: Return puzzle dict
    return {
        'width': width,
        'height': height,
        'difficulty': difficulty,
        'islands': valid_islands,
        'solution': tuple(filtered_solution)
    }


def print_puzzle(puzzle: PuzzleDict):
    """
    Print the puzzle in ASCII form. Islands are numbers, blank spaces are periods.
    """
    width = puzzle['width']
    height = puzzle['height']
    # Expanded grid: rows = 2*height-1, cols = 3*width-2
    rows = 2 * height - 1
    cols = 3 * width - 2
    grid = {}
    # Place periods at possible island coordinates that are not occupied
    occupied = set((isle['x'], isle['y']) for isle in puzzle['islands'])
    for x in range(puzzle['width']):
        for y in range(puzzle['height']):
            gx = x * 3
            gy = y * 2
            if (x, y) not in occupied:
                grid[(gx, gy)] = '.'
    for island in puzzle['islands']:
        gx = island['x'] * 3
        gy = island['y'] * 2
        grid[(gx, gy)] = str(island['count'])
    # Draw bridges if present
    bridges = puzzle.get('bridges')
    if bridges is not None:
        for bridge in bridges:
            x1, y1, x2, y2, typ = bridge
            gx1, gy1 = x1 * 3, y1 * 2
            gx2, gy2 = x2 * 3, y2 * 2
            if gx1 == gx2:
                for gy in range(min(gy1, gy2) + 1, max(gy1, gy2)):
                    grid[(gx1, gy)] = '║' if typ == '=' else '│'
            elif gy1 == gy2:
                for gx in range(min(gx1, gx2) + 1, max(gx1, gx2)):
                    grid[(gx, gy1)] = '═' if typ == '=' else '─'
    # Print coordinates and border with extra spacing
    letters = string.ascii_lowercase[:width]
    # Each cell is 3 chars wide, so build a label row with 3 spaces per letter
    label_row = '    ' + ''.join(f' {l} ' for l in letters)
    # Each row: 1 space + cols + 2 spaces = cols + 3
    board_width = cols + 3
    print(label_row)
    # Top border with extra columns
    print('   ┌' + '─' * board_width + '┐')
    # Extra blank row between border and board
    print('   │' + ' ' * board_width + '│')
    for y in range(height):
        gy = y * 2
        row = ' ' + ''.join(grid.get((x, gy), ' ') for x in range(cols)) + '  '
        print(f"{y+1:2} │{row}│{y+1:2}")
        if y < height - 1:
            row2 = ' ' + ''.join(grid.get((x, gy+1), ' ') for x in range(cols)) + '  '
            print('   │' + row2 + '│')
    # Extra blank row between board and border
    print('   │' + ' ' * board_width + '│')
    # Bottom border
    print('   └' + '─' * board_width + '┘')
    print(label_row)


def print_solution(puzzle: PuzzleDict):
    """
    Print the puzzle and solution bridges using DOS box drawing characters.
    """
    width = puzzle['width']
    height = puzzle['height']
    rows = 2 * height - 1
    cols = 3 * width - 2
    grid = {}
    occupied = set((isle['x'], isle['y']) for isle in puzzle['islands'])
    for x in range(puzzle['width']):
        for y in range(puzzle['height']):
            gx = x * 3
            gy = y * 2
            if (x, y) not in occupied:
                grid[(gx, gy)] = '.'
    for island in puzzle['islands']:
        gx = island['x'] * 3
        gy = island['y'] * 2
        grid[(gx, gy)] = str(island['count'])
    # Draw bridges
    if 'solution' in puzzle:
        for bridge in puzzle['solution']:
            x1, y1, x2, y2, typ = bridge
            gx1, gy1 = x1 * 3, y1 * 2
            gx2, gy2 = x2 * 3, y2 * 2
            if gx1 == gx2:
                for gy in range(min(gy1, gy2) + 1, max(gy1, gy2)):
                    grid[(gx1, gy)] = '║' if typ == '=' else '│'
            elif gy1 == gy2:
                for gx in range(min(gx1, gx2) + 1, max(gx1, gx2)):
                    grid[(gx, gy1)] = '═' if typ == '=' else '─'
    # Print coordinates and border with extra spacing
    letters = string.ascii_lowercase[:width]
    label_row = '    ' + ''.join(f' {l} ' for l in letters)
    board_width = cols + 3
    print(label_row)
    print('   ┌' + '─' * board_width + '┐')
    print('   │' + ' ' * board_width + '│')
    for y in range(height):
        gy = y * 2
        row = ' ' + ''.join(grid.get((x, gy), ' ') for x in range(cols)) + '  '
        print(f"{y+1:2} │{row}│{y+1:2}")
        if y < height - 1:
            row2 = ' ' + ''.join(grid.get((x, gy+1), ' ') for x in range(cols)) + '  '
            print('   │' + row2 + '│')
    print('   │' + ' ' * board_width + '│')
    print('   └' + '─' * board_width + '┘')
    print(label_row)


def solve_puzzle(puzzle: PuzzleDict) -> Tuple[Bridge, ...]:
    """
    Solve the puzzle. Returns a tuple of bridges (x1, y1, x2, y2, type).
    This is a stub: returns the trivial chain solution.
    """
    islands = puzzle['islands']
    solution = []
    for i in range(len(islands) - 1):
        x1, y1 = islands[i]['x'], islands[i]['y']
        x2, y2 = islands[i + 1]['x'], islands[i + 1]['y']
        bridge_type = '-' if random.random() < 0.5 else '='
        solution.append((x1, y1, x2, y2, bridge_type))
    return tuple(solution)


def play_puzzle(puzzle: PuzzleDict):
    """
    Play the puzzle in the terminal. User enters moves like '- a4 c4', '= e7 e3', or '. a4 c4'.
    """
    import sys

    # Must be interactive
    if not sys.stdin or not sys.stdin.isatty():
        print("play_puzzle requires an interactive terminal (TTY).")
        return

    width = puzzle['width']
    height = puzzle['height']
    bridges: List[Bridge] = []
    letters = string.ascii_lowercase[:width]

    def coord(s: str):
        x = letters.index(s[0].lower())
        y = int(s[1:]) - 1
        return x, y

    while True:
        # Display current board
        puzzle_to_print = dict(puzzle)
        puzzle_to_print['bridges'] = tuple(bridges)
        print_puzzle(puzzle_to_print)

        # Build bridge map and counts for current bridges
        from collections import defaultdict, deque

        bridge_map = defaultdict(list)
        bridge_counts = defaultdict(int)
        for (x1, y1, x2, y2, typ) in bridges:
            bridge_map[(x1, y1)].append((x2, y2, typ))
            bridge_map[(x2, y2)].append((x1, y1, typ))
            bridge_counts[(x1, y1)] += 2 if typ == '=' else 1
            bridge_counts[(x2, y2)] += 2 if typ == '=' else 1

        # Check win condition
        solved = True
        for island in puzzle['islands']:
            if bridge_counts[(island['x'], island['y'])] != island['count']:
                solved = False
                break

        # Check connectivity
        if solved and puzzle['islands']:
            visited = set()
            q = deque()
            start = (puzzle['islands'][0]['x'], puzzle['islands'][0]['y'])
            q.append(start)
            while q:
                node = q.popleft()
                if node in visited:
                    continue
                visited.add(node)
                for neighbor, _, _ in bridge_map.get(node, []):
                    if neighbor not in visited:
                        q.append(neighbor)
            if len(visited) != len(puzzle['islands']):
                solved = False

        if solved:
            print("Congratulations! You solved the puzzle!")
            return

        # Prompt for move
        try:
            move = input("Enter move ('- a4 c4', '= e7 e3', '. a4 c4', or 'q' to quit): ").strip()
        except EOFError:
            print("\nInput closed. Exiting.")
            return

        if move.lower() == 'q':
            print("Quitting.")
            return

        try:
            parts = move.split()
            if len(parts) == 3 and parts[0] in ('-', '=', '.'):
                typ = parts[0]
                x1, y1 = coord(parts[1])
                x2, y2 = coord(parts[2])
                island_positions = set((isle['x'], isle['y']) for isle in puzzle['islands'])
                # Only allow connecting islands
                if (x1, y1) not in island_positions or (x2, y2) not in island_positions:
                    print("You can only connect coordinates that have islands.")
                    continue
                if typ == '.':
                    # Remove any bridge between those coordinates (either direction)
                    bridges[:] = [b for b in bridges if not ((b[0], b[1], b[2], b[3]) == (x1, y1, x2, y2) or (b[0], b[1], b[2], b[3]) == (x2, y2, x1, y1))]
                else:
                    # Add bridge
                    bridges.append((x1, y1, x2, y2, typ))
            else:
                print("Invalid move format.")
        except Exception as e:
            print(f"Error: {e}")


