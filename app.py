from flask import Flask, render_template, jsonify, request
from datetime import datetime
import random

app = Flask(__name__)

# Word lists for different levels using common, everyday words
WORD_LISTS = {
    3: ["cat", "dog", "sun", "hat", "run", "box", "car", "day", "fun", "map"],
    4: ["time", "home", "book", "game", "food", "rain", "play", "door", "tree", "star"],
    5: ["happy", "house", "water", "music", "light", "green", "beach", "smile", "dream", "pizza"],
    6: ["family", "garden", "school", "friend", "coffee", "sunset", "summer", "window", "purple", "orange"],
    7: ["holiday", "morning", "evening", "weekend", "rainbow", "chicken", "freedom", "dolphin", "penguin", "sunrise"],
    8: ["birthday", "sunshine", "computer", "baseball", "chocolate", "elephant", "universe", "mountain", "treasure", "butterfly"],
    9: ["adventure", "education", "beautiful", "happiness", "discovery", "wonderful", "beginning", "celebrate", "different", "knowledge"]
}

class GameState:
    def __init__(self):
        self.reset_game()
        
    def reset_game(self):
        self.current_level = 3  # Start with 3-letter words
        self.current_word = self._get_new_word()
        self.attempts = 0
        self.total_score = 0
        self.completed_words = []  # List to store completed words and their attempts
        self.hint_used = False  # Track if hint was used for current level
        self.feedback_history = {}  # Store feedback history for hint selection
        print(f"Game reset to level {self.current_level}, word: {self.current_word}")
        
    def get_points_for_attempt(self, attempt_number):
        points_map = {
            1: 10,
            2: 8,
            3: 6,
            4: 5,
            5: 4,
            6: 3,
            7: 2,
            8: 1
        }
        return points_map.get(attempt_number, 0)
    
    def _get_new_word(self):
        word = random.choice(WORD_LISTS[self.current_level])
        print(f"Selected word for level {self.current_level}: {word}")
        return word
    
    def check_guess(self, guess):
        print(f"Checking guess '{guess}' against word '{self.current_word}'")
        if len(guess) != len(self.current_word):  
            print(f"Length mismatch: guess={len(guess)}, expected={len(self.current_word)}")
            return None
        
        self.attempts += 1
        result = []
        is_correct = guess.lower() == self.current_word.lower()
        print(f"Is correct: {is_correct}")
        
        # Convert strings to lists for easier manipulation
        word_chars = list(self.current_word.lower())
        guess_chars = list(guess.lower())
        
        if is_correct:
            # If the guess is correct, mark all letters as correct
            result = [{"letter": c, "status": "correct"} for c in guess_chars]
            print("Word is correct - all letters marked as correct")
            # Add points for correct guess
            points = self.get_points_for_attempt(self.attempts)
            self.total_score += points
            print(f"Added {points} points for solving in {self.attempts} attempts")
        else:
            # First pass: Check for exact matches
            for i in range(len(guess)):  
                if guess_chars[i] == word_chars[i]:
                    result.append({"letter": guess_chars[i], "status": "correct"})
                else:
                    result.append({"letter": guess_chars[i], "status": "wrong"})
            
            # Second pass: Check for letters in wrong position
            remaining_chars = word_chars.copy()
            for i, char in enumerate(guess_chars):
                if result[i]["status"] == "correct":
                    if char in remaining_chars:  
                        remaining_chars.remove(char)
            
            for i, char in enumerate(guess_chars):
                if result[i]["status"] == "wrong" and char in remaining_chars:
                    result[i]["status"] = "wrong-position"
                    remaining_chars.remove(char)
        
        print(f"Result statuses: {[r['status'] for r in result]}")
        
        # Store feedback history for hint selection
        self.feedback_history[self.attempts] = [item["status"] for item in result]
        
        return {
            "result": result,
            "is_correct": is_correct,
            "attempts": self.attempts
        }

    def get_hint(self):
        print(f"Getting hint. Hint used this level: {self.hint_used}, Total score: {self.total_score}")
        if self.hint_used:
            print("Hint already used for this level")
            return None
            
        if self.total_score < 1:
            print("Not enough points for hint")
            return None
        
        # Get all discovered letters (both correct and wrong-position)
        discovered_letters = set()
        correct_positions = {}  # Track correct positions
        
        # Go through all previous guesses
        for attempt_num, feedback in self.feedback_history.items():
            for i, status in enumerate(feedback):
                if status == "correct":
                    # For correct letters, store their position
                    discovered_letters.add(self.current_word[i].lower())
                    correct_positions[i] = self.current_word[i].lower()
                elif status == "wrong-position":
                    discovered_letters.add(self.current_word[i].lower())
        
        print(f"Already discovered letters: {discovered_letters}")
        print(f"Correct positions: {correct_positions}")
        
        # Find letters that haven't been discovered yet
        undiscovered_letters = []
        for i, letter in enumerate(self.current_word.lower()):
            # Only add if letter hasn't been discovered and isn't correctly placed
            if letter not in discovered_letters and i not in correct_positions:
                undiscovered_letters.append(letter)
        
        print(f"Available undiscovered letters: {undiscovered_letters}")
        
        if not undiscovered_letters:
            print("No new letters to hint")
            return None
            
        # Choose a random undiscovered letter
        hint_letter = random.choice(undiscovered_letters)
        self.hint_used = True
        self.total_score -= 1
        
        print(f"Providing hint letter: {hint_letter}")
        return hint_letter

    def next_level(self):
        """Move to the next level and reset game state for the new level."""
        if self.current_level < 9:  
            self.current_level += 1
            self.attempts = 0
            self.hint_used = False  # Reset hint usage for new level
            self.feedback_history = {}
            self.current_word = self._get_new_word()
            print(f"Moving to level {self.current_level} with word {self.current_word}, hint_used reset to {self.hint_used}")
            return True
        return False

game_state = GameState()

MAX_ATTEMPTS = 8

@app.route('/')
def home():
    # Reset game state when home page is loaded
    global game_state
    game_state.reset_game()
    return render_template('index.html')

@app.route('/api/guess', methods=['POST'])
def guess():
    data = request.get_json()
    guess = data.get('guess', '').lower()
    
    if not guess:
        return jsonify({"error": "No guess provided"}), 400
        
    result = game_state.check_guess(guess)
    if result is None:
        return jsonify({"error": f"Invalid guess length. Expected {len(game_state.current_word)} letters"}), 400
    
    response = {
        "result": result["result"],
        "is_correct": result["is_correct"],
        "attempts": result["attempts"],
        "total_score": game_state.total_score
    }
    
    if result["is_correct"]:
        # Add the completed word to the list
        game_state.completed_words.append({
            "word": game_state.current_word,
            "level": len(game_state.current_word),  
            "attempts": game_state.attempts
        })
        
        # Move to next level
        next_level = game_state.next_level()
        if next_level:
            response["current_level"] = game_state.current_level
            response["completed_words"] = game_state.completed_words
        else:
            response["game_over"] = True
            response["word"] = game_state.current_word
            response["completed_words"] = game_state.completed_words  
    elif game_state.attempts >= MAX_ATTEMPTS:
        response["game_over"] = True
        response["word"] = game_state.current_word
        
    print(f"Sending response for guess '{guess}': {response}")
    return jsonify(response)

@app.route('/api/hint', methods=['POST'])
def get_hint():
    if game_state.hint_used:
        return jsonify({"error": "Hint already used for this level"}), 400
        
    if game_state.total_score < 1:
        return jsonify({"error": "Need at least 1 point to use hint"}), 400
        
    hint = game_state.get_hint()
    if hint:
        response = {
            "letter": hint,
            "total_score": game_state.total_score
        }
        print(f"Sending hint response: {response}")
        return jsonify(response)
    return jsonify({"error": "No hint available"}), 400

if __name__ == '__main__':
    app.run(debug=True)
