# Teris (Tetris in Python)

A simple Tetris-style game built with Python and `tkinter`.

This repo also includes a Galaga-style arcade shooter.

## Requirements

- Python 3.x
- `tkinter` (included with standard Python on most installations)

## Run

From this folder, run:

```powershell
C:/Users/jiesu/Downloads/VSCode/Python/PythonLearning/venv1/Scripts/python.exe Teris.py
```

## Controls

- Left / Right Arrow: Move piece
- Up Arrow: Rotate
- Down Arrow: Soft drop
- Space: Hard drop
- `P`: Pause / Resume
- `R`: Restart game

## Notes

- Score increases from soft drops, hard drops, and line clears.
- Level increases every 10 cleared lines.

## Galaga

### Run

From this folder, run:

```powershell
C:/Users/jiesu/Downloads/VSCode/Python/PythonLearning/venv1/Scripts/python.exe Galaga.py
```

### Controls

- Left / Right Arrow or `A` / `D`: Move ship
- Space: Shoot
- `P`: Pause / Resume
- `R`: Restart (after game over)

### Gameplay

- Clear all enemies to advance to the next wave.
- You have 3 lives.
- Game ends if lives reach 0 or enemies reach the player line.
