from flask import Flask, render_template, jsonify, request, make_response
from datetime import datetime
import random
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key

# Word lists for different levels using common, everyday words
WORD_LISTS = {
    3: ["cat", "dog", "sun", "hat", "run", "box", "car", "day", "fun", "map", 
        "bag", "cup", "pen", "bus", "leg", "sky", "toy", "bed", "key", "egg",
        "pig", "red", "big", "top", "dad", "mom", "wet", "hot", "sad", "joy",
        "ant", "bat", "bee", "cow", "cry", "dry", "ear", "eye", "fly", "fox",
        "gym", "ham", "ice", "jam", "jog", "lip", "mix", "nap", "net", "owl",
        "paw", "pin", "rat", "rug", "sip", "tag", "van", "wig", "air", "arm",
        "art", "boy", "bun", "can", "cap", "den", "dot", "fan", "fit", "fog",
        "fur", "gas", "get", "got", "had", "has", "hit", "let", "new", "old"],
    4: ["time", "home", "book", "game", "food", "rain", "play", "door", "tree", "star",
        "ball", "fish", "bird", "cake", "milk", "jump", "desk", "hand", "moon", "bear",
        "bike", "park", "song", "leaf", "snow", "baby", "duck", "gift", "love", "wind",
        "bell", "boat", "cave", "coin", "cool", "dark", "dish", "drum", "farm", "fire",
        "frog", "gold", "hair", "hero", "king", "kite", "lamp", "lion", "mail", "mint",
        "nest", "pipe", "ring", "sail", "seed", "soap", "tail", "wave", "wing", "yarn",
        "arch", "army", "aunt", "bank", "barn", "beef", "belt", "bone", "bowl", "bulb",
        "cart", "chef", "chin", "clip", "code", "cork", "corn", "crew", "deer", "diet"],
    5: ["happy", "house", "water", "music", "light", "green", "smile", "dream", "pizza",
        "dance", "cloud", "phone", "chair", "sleep", "bread", "paper", "heart", "grass", "train",
        "apple", "river", "ocean", "tiger", "horse", "plant", "mouse", "earth", "clock", "angel",
        "brush", "candy", "chess", "crown", "diary", "eagle", "fairy", "flame", "globe", "grape",
        "honey", "juice", "magic", "medal", "nurse", "paint", "queen", "robot", "shark", "skate",
        "space", "storm", "sugar", "sword", "table", "torch", "whale", "witch", "youth", "actor",
        "alarm", "alien", "arrow", "bacon", "badge", "blade", "bloom", "brain", "brick", "bride",
        "camel", "chain", "chalk", "charm", "cheek", "chest", "child", "clown", "coast", "crane",
        "world"],
    6: ["family", "garden", "school", "friend", "coffee", "sunset", "summer", "window", "purple", "orange",
        "monkey", "pencil", "flower", "butter", "cookie", "rabbit", "bridge", "forest", "planet", "winter",
        "spring", "turtle", "dragon", "soccer", "basket", "doctor", "silver", "yellow", "anchor", "ballet",
        "castle", "circus", "desert", "dinner", "escape", "flight", "guitar", "hammer", "island", "jungle",
        "knight", "market", "museum", "palace", "parade", "rocket", "sailor", "shield", "spirit", "temple",
        "throne", "ticket", "towers", "valley", "vessel", "violin", "wallet", "wonder", "action", "artist",
        "bamboo", "barrel", "battle", "beetle", "branch", "breath", "bubble", "button", "cactus", "candle",
        "canyon", "carpet", "carrot", "cattle", "cellar", "circle", "comedy", "copper", "cotton", "danger"],
    7: ["holiday", "morning", "evening", "weekend", "rainbow", "chicken", "freedom", "dolphin", "penguin", "sunrise",
        "airport", "balloon", "camping", "diamond", "factory", "harmony", "history", "journey", "library", "mystery",
        "orchard", "painter", "sailing", "silence", "singing", "skating", "soldier", "student", "teacher", "theater",
        "thunder", "trumpet", "village", "volcano", "warrior", "weather", "whisper", "whistle", "writing", "admiral",
        "android", "antenna", "antique", "archive", "athlete", "balance", "banquet", "battery", "bedroom", "bicycle",
        "boiling", "buffalo", "builder", "cabinet", "caravan", "cartoon", "cascade", "ceiling", "channel", "chariot",
        "chimney", "college", "compass", "concert", "counter", "crystal", "curtain", "cushion", "dessert", "doorway",
        "eclipse", "emerald", "feather", "fishing", "playing", "flowers", "gallery", "general", "hammock", "highway"],
    8: ["birthday", "sunshine", "computer", "baseball", "discover", "personal", "universe", "mountain", "treasure", "decision",
        "alphabet", "daughter", "distance", "festival", "grateful", "thinking", "interest", "kindness", "language", "laughter",
        "material", "neighbor", "original", "peaceful", "possible", "practice", "pressure", "progress", "question", "remember",
        "security", "separate", "strength", "struggle", "surprise", "together", "tomorrow", "training", "valuable", "planning",
        "watching", "wellness", "whispers", "wildlife", "painting", "yourself", "absolute", "accuracy", "advanced", "approval",
        "business", "attitude", "balanced", "believes", "blessing", "breaking", "briefing", "bringing", "capacity", "catching",
        "complete", "changing", "creative", "critical", "crossing", "darkness", "delicate", "spinning", "building", "drinking",
        "directed", "dreaming", "emerging", "standing", "exercise", "floating", "focusing", "starting", "friendly", "climbing"]
}

class GameState:
    def __init__(self):
        # Try to get state from cookie
        state_cookie = request.cookies.get('game_state')
        if state_cookie:
            try:
                state = json.loads(state_cookie)
                self.current_level = state['current_level']
                self.current_word = state['current_word']
                self.attempts = state['attempts']
                self.total_score = state['total_score']
                self.completed_words = state['completed_words']
                self.hint_used = state['hint_used']
                self.feedback_history = state['feedback_history']
                print(f"Loaded from cookie - level: {self.current_level}, word: {self.current_word}, attempts: {self.attempts}")
            except:
                print("Error loading cookie, starting new game")
                self.reset_game()
        else:
            print("No cookie found, starting new game")
            self.reset_game()

    def to_dict(self):
        return {
            'current_level': self.current_level,
            'current_word': self.current_word,
            'attempts': self.attempts,
            'total_score': self.total_score,
            'completed_words': self.completed_words,
            'hint_used': self.hint_used,
            'feedback_history': self.feedback_history
        }

    def reset_game(self):
        self.current_level = 3  # Start with 3-letter words
        self.current_word = self._get_new_word()
        self.attempts = 0
        self.total_score = 0
        self.completed_words = []  # List to store completed words and their attempts
        self.hint_used = False  # Track if hint was used for current level
        self.feedback_history = {}  # Store feedback history for hint selection
        print(f"Game reset to level {self.current_level}, word: {self.current_word}")

    def save_to_session(self):
        """Save current state to session"""
        print(f"Saving to session - level: {self.current_level}, word: {self.current_word}, attempts: {self.attempts}")
        session['current_level'] = self.current_level
        session['current_word'] = self.current_word
        session['attempts'] = self.attempts
        session['total_score'] = self.total_score
        session['completed_words'] = self.completed_words
        session['hint_used'] = self.hint_used
        session['feedback_history'] = self.feedback_history
        print("Session after save:", dict(session))

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
        print(f"Checking guess '{guess}' against word '{self.current_word}' (attempts: {self.attempts})")
        if len(guess) != len(self.current_word):
            print(f"Length mismatch: guess={len(guess)}, expected={len(self.current_word)}")
            return None
        
        self.attempts += 1
        print(f"Attempts now: {self.attempts}")
        result = []
        is_correct = guess.lower() == self.current_word.lower()
        
        # Convert strings to lists for easier manipulation
        word_chars = list(self.current_word.lower())
        guess_chars = list(guess.lower())
        
        # Count occurrences of each letter in the target word
        word_letter_count = {}
        for letter in word_chars:
            word_letter_count[letter] = word_letter_count.get(letter, 0) + 1
        
        # Track how many of each letter we've marked as correct
        correct_letter_count = {}
        
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
            result = [{"letter": c, "status": "wrong"} for c in guess_chars]
            
            # Mark correct positions first
            for i, (guess_char, word_char) in enumerate(zip(guess_chars, word_chars)):
                if guess_char == word_char:
                    result[i]["status"] = "correct"
                    correct_letter_count[guess_char] = correct_letter_count.get(guess_char, 0) + 1
            
            # Second pass: Check for wrong positions
            # Only mark as wrong-position if we haven't exceeded the count of that letter in the word
            for i, guess_char in enumerate(guess_chars):
                if result[i]["status"] == "wrong":  # Skip already correct ones
                    correct_count = correct_letter_count.get(guess_char, 0)
                    wrong_pos_allowed = word_letter_count.get(guess_char, 0) - correct_count
                    
                    if wrong_pos_allowed > 0 and guess_char in word_chars:
                        result[i]["status"] = "wrong-position"
                        correct_letter_count[guess_char] = correct_letter_count.get(guess_char, 0) + 1
        
        # Store feedback for hint system
        self.feedback_history[self.attempts] = [r["status"] for r in result]
        
        # Save state after updating
        # self.save_to_session()
        print(f"Returning result for guess '{guess}': {result}")
        return {"result": result, "is_correct": is_correct, "attempts": self.attempts}

    def get_hint(self):
        print(f"Getting hint. Hint used this level: {self.hint_used}, Total score: {self.total_score}")
        if self.hint_used:
            print("Hint already used for this level")
            return None
            
        if self.total_score < 1:
            print("Not enough points for hint")
            return None
        
        # Count occurrences of each letter in the target word
        word_letter_count = {}
        for letter in self.current_word.lower():
            word_letter_count[letter] = word_letter_count.get(letter, 0) + 1
        
        print(f"Letter counts in word: {word_letter_count}")
        
        # Track discovered letters and their counts
        discovered_letter_count = {}
        
        # Go through all previous guesses
        for attempt_num, feedback in self.feedback_history.items():
            for i, status in enumerate(feedback):
                letter = self.current_word[i].lower()
                if status in ["correct", "wrong-position"]:
                    discovered_letter_count[letter] = discovered_letter_count.get(letter, 0) + 1
        
        print(f"Discovered letter counts: {discovered_letter_count}")
        
        # Find letters that haven't been fully discovered yet
        available_letters = []
        for letter, target_count in word_letter_count.items():
            discovered_count = discovered_letter_count.get(letter, 0)
            remaining_count = target_count - discovered_count
            
            if remaining_count > 0:
                # Add the letter as many times as it's still undiscovered
                available_letters.extend([letter] * remaining_count)
        
        print(f"Available letters for hint: {available_letters}")
        
        if not available_letters:
            print("No new letters to hint")
            return None
            
        # Choose a random undiscovered letter
        hint_letter = random.choice(available_letters)
        self.hint_used = True
        self.total_score -= 1
        # self.save_to_session()
        print(f"Providing hint letter: {hint_letter}")
        return hint_letter

    def next_level(self):
        """Move to the next level and reset game state for the new level."""
        if self.current_level < 8:  # Max word length is 8
            self.current_level += 1
            self.current_word = self._get_new_word()
            self.attempts = 0  # Reset attempts for new level
            self.hint_used = False  # Reset hint status
            self.feedback_history = {}  # Reset feedback history
            # self.save_to_session()
            print(f"Moving to level {self.current_level}, new word: {self.current_word}")
            return True
        return False

MAX_ATTEMPTS = 8

@app.route('/')
def home():
    # Reset game state when home page is loaded
    game_state = GameState()
    game_state.reset_game()
    response = make_response(render_template('index.html'))
    response.set_cookie('game_state', json.dumps(game_state.to_dict()))
    return response

@app.route('/api/guess', methods=['POST'])
def guess():
    game_state = GameState()  # This will load from cookie
    print(f"Current game state - level: {game_state.current_level}, attempts: {game_state.attempts}, word: {game_state.current_word}")

    data = request.get_json()
    guess = data.get('guess', '').lower()
    print(f"Received guess: {guess}")
    
    if not guess:
        return jsonify({"error": "No guess provided"}), 400
        
    result = game_state.check_guess(guess)
    if result is None:
        return jsonify({"error": f"Invalid guess length. Expected {len(game_state.current_word)} letters"}), 400
    
    response = {
        "result": result["result"],
        "is_correct": result["is_correct"],
        "attempts": result["attempts"],
        "total_score": game_state.total_score,
        "current_level": game_state.current_level,  # Always include current level
        "current_word_length": len(game_state.current_word)  # Add word length
    }
    
    if result["is_correct"]:
        # Add the completed word to the list
        game_state.completed_words.append({
            "word": game_state.current_word,
            "level": len(game_state.current_word),  
            "attempts": game_state.attempts
        })
        # game_state.save_to_session()
        
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
        response["completed_words"] = game_state.completed_words  # Add completed words when game is lost
    
    # Create response with cookie
    resp = make_response(jsonify(response))
    resp.set_cookie('game_state', json.dumps(game_state.to_dict()))
    return resp

@app.route('/api/hint', methods=['POST'])
def get_hint():
    game_state = GameState()  # This will load from cookie

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
        # Create response with cookie
        resp = make_response(jsonify(response))
        resp.set_cookie('game_state', json.dumps(game_state.to_dict()))
        return resp
        
    return jsonify({"error": "No hint available"}), 400

if __name__ == '__main__':
    app.run(debug=True)
