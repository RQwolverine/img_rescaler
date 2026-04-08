# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the game

```bash
python snake.py
```

Requires `pygame`. Install with:

```bash
pip install pygame
```

## Controls

- Arrow keys or WASD to move
- `P` to pause/unpause
- `R` to restart after game over
- `ESC` to quit

## Code structure

`snake.py` is a single-file pygame game with:

- **Constants** at the top: grid dimensions (`COLS`/`ROWS` = 30×30), `CELL` size (20px), `FPS` (10)
- **`main()`**: contains the full game loop — event handling, state update, and rendering all inline
- **`new_game()`**: nested inside `main()`, returns initial `(snake, direction, food, score)` state tuple
- Snake state is a list of `(col, row)` tuples; index 0 is the head
- Food pulsing and snake eyes are computed each frame from `pygame.time.get_ticks()`

The reference files `git-commands.md` and `claude-code-guide.md` are personal cheat sheets unrelated to the game.
