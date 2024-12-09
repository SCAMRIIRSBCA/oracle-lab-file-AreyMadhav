# End of the World 

End of the World is a Python-based 2D car racing game where you control a car, avoid obstacles, and earn points as you survive longer. The game includes dynamic obstacles, explosions, and background music. It also saves high scores to a local SQLite database for tracking player performance.

## Features
- **Car control**: Move your car left or right to avoid obstacles.
- **Dynamic obstacles**: Obstacles appear randomly and move towards the bottom of the screen.
- **Explosions**: Explosions when an obstacle reaches the bottom or collides with the car.
- **Score tracking**: The longer you survive, the higher your score.
- **High score storage**: High scores are saved to a local SQLite database (`game_scores.db`).
- **Background music**: A background soundtrack plays while you're racing.

## Installation

### Prerequisites
Ensure you have Python 3.x installed on your system. You'll also need the following Python libraries:
- `pygame`: For handling the game logic and graphics.
- `sqlite3`: For database integration (built into Python).

You can install `pygame` via pip if you don't already have it:

```bash
pip install pygame
