# AgentQuest

An autonomous agent simulation developed in Python using Pygame. This project implements pathfinding algorithms and state management to complete collection tasks in an environment with procedurally generated obstacles.

## 📋 Features

* **A* Algorithm (A-Star):** Custom implementation to find the most efficient route while avoiding walls.
* **Finite State Machine (FSM):** The agent dynamically switches behaviors (Searching, Collected, Charging, Dead).
* **Energy Management:** The agent calculates when it's safe to keep searching and when it must return to the charging station.
* **Procedural Generation:** Obstacles and objectives appear in random positions every run.
* **Visual Themes:** Switchable skins (Circus 🎪, Knight 🛡️, Aztec ☀️).
* **Developer Mode:** Real-time visualization of the grid, visited nodes, and path costs.

## 🛠️ Requirements

* Python 3.8+
* `pygame` library

## 🚀 Installation & Execution

1.  **Clone the repository.**
    ```bash
    git clone https://github.com/AbelMorals/AgentQuest.git
    ```
3.  **Install dependencies:**
    ```bash
    pip install pygame
    ```
4.  **Run the game:**
    ```bash
    python game.py
    ```

## 🎮 Controls

* **Arrow Keys ↑ / ↓:** Navigate the theme selection menu.
* **ENTER:** Select theme / Start simulation.
* **SPACE:** Pause / Resume.
* **R:** Restart simulation (Soft reset).
* **Q:** Return to the selection menu.
* **ESC:** Quit the game.

### Debug Tools (Dev Mode)
* **D:** Toggle Pathfinding visualization (nodes and costs).
* **S:** Step-by-step execution in debug mode.
* **A (Hold):** Fast forward in debug mode.

## 📂 Project Structure

* `game.py`: Entry point. Handles the main loop and events.
* `robot.py`: Agent logic (decisions and states).
* `pathfinder.py`: Pure A* algorithm implementation.
* `world.py`: Map and obstacle generation.
* `render.py`: Graphics handling and drawing.
* `config.py`: Constants, file paths, and theme settings.
