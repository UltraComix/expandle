# Expandle

A word-guessing game where words get progressively longer as you advance through the levels.

## How to Play

1. Start with 3-letter words and work your way up to 9-letter words
2. You have 8 attempts to guess each word
3. After each guess, you'll get feedback:
   - Purple: Letter is correct and in the right position
   - Red: Letter is in the word but in the wrong position
   - Gray: Letter is not in the word
4. Use hints to reveal a letter (costs 1 point)
5. Score points based on how quickly you solve each word:
   - 1st attempt: 10 points
   - 2nd attempt: 8 points
   - 3rd attempt: 6 points
   - 4th attempt: 5 points
   - 5th attempt: 4 points
   - 6th attempt: 3 points
   - 7th attempt: 2 points
   - 8th attempt: 1 point

## Features

- Progressive difficulty: Words get longer as you advance
- Hint system: Get help when stuck (costs points)
- Visual keyboard feedback
- Progress tracking with a staircase visualization
- Score tracking system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/expandle.git
cd expandle
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install flask
```

4. Run the game:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Technologies Used

- Backend: Python with Flask
- Frontend: HTML, CSS, JavaScript
- No external database required - runs entirely in memory

## License

MIT License - Feel free to use, modify, and distribute this code.
