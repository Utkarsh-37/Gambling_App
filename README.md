# 🎰 Gambling App Simulator

A comprehensive, command-line based gambling simulation application built in Python. This project allows users to create gambler profiles, deposit virtual funds, play interactive betting games (manually or via automated strategies), and track extensive analytics about their win/loss rates over time.

Built with a robust **Layered Architecture**, the application strictly separates user interface, business logic, data models, and database interactions, making it highly scalable and easy to maintain.

---

## ✨ Features

* **👤 Gambler Profile Management:** Create players with specific initial stakes, win thresholds, and loss limits.
* **🏦 Banking & Transactions:** Deposit funds and maintain a strict ledger of all transactions (stakes, wins, losses, deposits).
* **⏱️ Session Tracking:** Start, pause, resume, and end gambling sessions. The app tracks peak stakes, lowest stakes, and session duration.
* **🎲 Betting Room:**
  * **Manual Play:** Place single bets and view instant outcomes.
  * **Auto-Play Strategies:** Automate betting using popular strategies such as **Martingale**, **Reverse Martingale**, **Fixed**, and **Percentage** betting.
* **📊 Advanced Analytics:** Generate detailed session summaries, calculate net profit/loss, and track win/loss streaks and ROI.
* **🖥️ Rich Terminal UI:** Uses the `rich` Python library to display colorful, interactive, and formatted terminal menus and tables.

---

## 🏗️ Project Architecture

This project follows a classic **Layered Architecture Pattern**:

1. **UI Layer (`ui/`):** Handles all user interactions, input validation, and rendering terminal visuals using `rich`.
2. **Controller Layer (`controllers/`):** Acts as the bridge. It receives input from the UI, formats it, and routes it to the correct background service.
3. **Service Layer (`services/`):** Contains the core business logic, math, game rules, and strategy execution.
4. **Repository Layer (`repositories/`):** Manages all database interactions (saving and retrieving data).
5. **Data Models (`models/`):** Dataclasses representing the core entities (e.g., `Gambler`, `GameSession`, `Bet`, `StakeTransaction`).

---

## 📂 Directory Structure

```text
gambling_app/
├── config/                 # Database connection and environment variables
├── controllers/            # Routes UI requests to services
├── models/                 # Data classes (Gambler, Session, Bet, etc.)
├── repositories/           # Database execution (CRUD operations)
├── services/               # Core business logic and calculations
├── strategies/             # Auto-play betting strategies (Martingale, etc.)
├── ui/                     # Interactive terminal menus and displays
├── utils/                  # Helper functions, custom exceptions, and decorators
└── main.py                 # The entry point of the application

🚀 Getting Started
Prerequisites
Python 3.8+ installed on your machine.

A virtual environment (recommended).

Installation
Clone the repository:

Bash
git clone [https://github.com/your-username/Gambling_App-dev.git](https://github.com/your-username/Gambling_App-dev.git)
cd Gambling_App-dev/gambling_app
Install the required dependencies:
The primary external dependency for this project is the rich library for terminal formatting.

Bash
pip install rich
(If you have a requirements.txt file, run pip install -r requirements.txt instead).

Set up Environment Variables:

Create a .env file in the root directory if necessary (based on your settings.py configuration) to configure database paths or application secrets.

Running the Application
To start the simulator, run the main script from the root of the project:

Bash
python main.py
Upon starting, the application will automatically initialize the database schema (creating all 11 required tables if they don't exist) and load the Interactive Main Menu.

🎮 How to Play (Usage Flow)
Create a Profile (Option 1): Start by creating a new gambler profile. Set your initial money and your safe limits (Win/Loss Thresholds).

Start a Session (Option 6): You must start a session before you can place bets.

Place Bets (Option 10 or 11): * Choose Option 10 to play one game at a time.

Choose Option 11 to let the computer play for you using a specific strategy (e.g., set it to Martingale for 50 rounds).

End Session & View Summary (Option 8): When you are done, end the session to get a detailed receipt of your net profit, ROI, and streaks!

🛠️ Error Handling & Safety
Input Validation: The app features a SafeInputHandler to prevent crashes when a user types letters instead of numbers.

Financial Boundaries: The system constantly checks your balance against your configured "Loss Limits" and will automatically end your session or prevent bets if you run out of money.

Decorator Logging: Backend services utilize a custom @service_logger decorator to trace execution paths and capture errors in the background without breaking the UI.

📜 License
This project is open-source and available under the MIT License.
