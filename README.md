# Car Racer

A simple 2D racing game built with Python and Pygame. The player races a computer-controlled car around a track, completes laps, advances through two hardcoded levels, and receives clear winner messages for each level.

## Features

- Main menu with Start Game and Settings options
- Background music with adjustable volume
- Player-controlled red car
- Computer-controlled green car
- Track border collision and finish-line detection
- Two hardcoded levels:
  - Level 1: 1 lap
  - Level 2: 2 laps
- Per-level winner message
- Final win/loss message after the game ends

## Requirements

- Python 3.10 or newer
- Pygame

## Installation

1. Clone or download this project.
2. Open a terminal in the project folder.
3. Install the required package:

```bash
pip install -r requirements.txt
```

## How To Run

Run the game with:

```bash
python main.py
```

If you are using a conda environment, activate it first:

```bash
conda activate game
cd C:\Users\Ashish\CAR-RACER
python main.py
```

## Controls

| Key | Action |
| --- | --- |
| `W` | Move forward |
| `S` | Move backward |
| `A` | Turn left |
| `D` | Turn right |
| `Space` | Boost |
| `Enter` or `Space` | Start from menu / start level |
| `Esc` | Return to menu while playing |
| `Left Arrow` / `Right Arrow` | Adjust volume in settings |

## Project Structure

```text
CAR-RACER/
+-- assets/              # Music and audio files
+-- imgs/                # Track, car, finish line, and background images
+-- main.py              # Main game file
+-- utils.py             # Helper functions for scaling, rotation, and text
+-- requirements.txt     # Python dependencies
+-- README.md            # Project documentation
```

## Game Rules

The player wins a level by completing the required number of laps before the computer car does. If the computer completes the required laps first, the player loses the game. After winning level 1, the game starts level 2. After winning level 2, the game displays the final victory message and resets.

## Notes

Make sure the `assets` and `imgs` folders stay in the same directory as `main.py`, because the game loads images and music from those folders.

## Troubleshooting

- Use `python main.py`, not `pyton main.py`.
- If you see `KeyboardInterrupt` and `^C` in the terminal, it means the game was stopped with `Ctrl+C`. Close the game window normally or press `Esc` while playing to return to the menu.
- If Pygame is missing, run `pip install -r requirements.txt` inside the project folder.
