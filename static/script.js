document.addEventListener('DOMContentLoaded', () => {
    const gameBoard = document.getElementById('gameBoard');
    const keyboard = document.getElementById('keyboard');
    const guessInput = document.getElementById('guessInput');
    const submitButton = document.getElementById('submitGuess');
    const hintButton = document.getElementById('hintButton');
    const messageDiv = document.getElementById('message');
    const totalScoreSpan = document.getElementById('totalScore');
    const currentLevelSpan = document.getElementById('currentLevel');
    const attemptsSpan = document.getElementById('attempts');
    
    const keyboardLayout = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'DEL']
    ];
    
    let currentLevel = 3;
    
    function showMessage(text, isError = false) {
        messageDiv.textContent = text;
        messageDiv.className = isError ? 'message error' : 'message success';
        setTimeout(() => {
            messageDiv.textContent = '';
            messageDiv.className = 'message';
        }, 3000);
    }
    
    function createGameBoard() {
        gameBoard.innerHTML = '';
        
        // Create 8 rows for attempts
        for (let i = 0; i < 8; i++) {
            const row = document.createElement('div');
            row.className = 'row';
            
            // Create cells based on current level
            for (let j = 0; j < currentLevel; j++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                row.appendChild(cell);
            }
            
            gameBoard.appendChild(row);
        }
        
        // Reset hint button
        hintButton.disabled = false;
        hintButton.title = "Get a hint (-1 point)";
        
        // Update input max length and placeholder
        guessInput.maxLength = currentLevel;
        guessInput.placeholder = `Enter ${currentLevel}-letter word`;
        guessInput.value = ''; // Clear any existing input
        
        // Update level display
        currentLevelSpan.textContent = currentLevel;
        
        // Reset attempts
        attemptsSpan.textContent = '0';
        
        // Create fresh keyboard
        createKeyboard();
    }
    
    function createKeyboard() {
        keyboard.innerHTML = '';
        
        keyboardLayout.forEach(row => {
            const rowDiv = document.createElement('div');
            rowDiv.className = 'keyboard-row';
            
            row.forEach(key => {
                const keyButton = document.createElement('button');
                keyButton.className = key === 'ENTER' || key === 'DEL' ? 'key key-special' : 'key';
                keyButton.textContent = key === 'DEL' ? '⌫' : key;
                keyButton.dataset.key = key;
                keyButton.addEventListener('click', () => {
                    if (key === 'ENTER') {
                        submitGuess();
                    } else if (key === 'DEL') {
                        guessInput.value = guessInput.value.slice(0, -1);
                    } else if (guessInput.value.length < currentLevel) {
                        guessInput.value += key;
                    }
                });
                rowDiv.appendChild(keyButton);
            });
            
            keyboard.appendChild(rowDiv);
        });
    }
    
    function updateStaircase(completedWords) {
        const staircase = document.querySelector('.staircase');
        staircase.innerHTML = '';
        
        completedWords.forEach(word => {
            const stair = document.createElement('div');
            stair.className = 'stair';
            stair.style.setProperty('--level', word.level - 3); // Start indentation from 0
            
            const wordSpan = document.createElement('span');
            wordSpan.className = 'word';
            wordSpan.textContent = word.word;
            
            const attemptsSpan = document.createElement('span');
            attemptsSpan.className = 'attempts';
            attemptsSpan.textContent = `Solved in ${word.attempts} ${word.attempts === 1 ? 'try' : 'tries'}`;
            
            stair.appendChild(wordSpan);
            stair.appendChild(attemptsSpan);
            staircase.appendChild(stair);
        });
    }
    
    async function submitGuess() {
        const guess = guessInput.value.trim().toUpperCase();
        
        if (guess.length !== currentLevel) {
            showMessage(`Please enter a ${currentLevel}-letter word`, true);
            return;
        }
        
        try {
            const response = await fetch('/api/guess', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ guess: guess })
            });
            
            const data = await response.json();
            
            if (data.error) {
                showMessage(data.error, true);
                return;
            }
            
            // Update total score and attempts
            totalScoreSpan.textContent = data.total_score;
            attemptsSpan.textContent = data.attempts;
            
            // Update current level if it changed
            if (data.current_level && data.current_level !== currentLevel) {
                currentLevel = data.current_level;
            }
            
            // Get current row and update cells
            const currentRow = gameBoard.children[data.attempts - 1];
            if (!currentRow) {
                console.error('No row found for attempt:', data.attempts);
                return;
            }
            
            // Update the cells in the current row
            const cells = currentRow.children;
            data.result.forEach((result, index) => {
                const cell = cells[index];
                cell.textContent = result.letter;
                cell.className = `cell ${result.status}`;
                
                // Update keyboard
                const key = keyboard.querySelector(`button[data-key="${result.letter.toUpperCase()}"]`);
                if (key) {
                    // Get the current status of the key
                    const currentStatus = key.classList.contains('correct') ? 'correct' :
                                       key.classList.contains('wrong-position') ? 'wrong-position' :
                                       key.classList.contains('wrong') ? 'wrong' : null;
                    
                    // Only update if the new status is better than the current one
                    // Priority: correct > wrong-position > wrong
                    const shouldUpdate = 
                        !currentStatus || // No current status
                        (currentStatus === 'wrong' && (result.status === 'correct' || result.status === 'wrong-position')) || // Upgrade from wrong
                        (currentStatus === 'wrong-position' && result.status === 'correct'); // Upgrade to correct
                    
                    if (shouldUpdate) {
                        // Remove all status classes but keep the base 'key' class
                        key.className = 'key';
                        
                        // Add the new status class
                        key.classList.add(result.status);
                        
                        // Keep the key-special class if it's a special key
                        if (key.dataset.key === 'ENTER' || key.dataset.key === 'DEL') {
                            key.classList.add('key-special');
                        }
                    }
                }
            });
            
            // Clear input
            guessInput.value = '';
            
            if (data.is_correct) {
                showMessage('Correct! Well done!');
                
                // Update progress staircase
                if (data.completed_words) {
                    updateStaircase(data.completed_words);
                }
                
                if (data.current_level) {
                    // Wait for animation and message to complete before changing level
                    await new Promise(resolve => setTimeout(resolve, 1500));
                    currentLevel = data.current_level;
                    showMessage(`Moving to ${currentLevel}-letter words...`);
                    // Wait for message to show before resetting board
                    await new Promise(resolve => setTimeout(resolve, 500));
                    createGameBoard();
                    // Clear keyboard colors for new level
                    const keys = keyboard.querySelectorAll('.key');
                    keys.forEach(key => {
                        key.className = 'key';
                        if (key.dataset.key === 'ENTER' || key.dataset.key === 'DEL') {
                            key.classList.add('key-special');
                        }
                    });
                } else {
                    showMessage('Congratulations! You\'ve completed all levels!');
                    // Update progress staircase one final time
                    if (data.completed_words) {
                        updateStaircase(data.completed_words);
                    }
                    guessInput.disabled = true;
                    submitButton.disabled = true;
                    hintButton.disabled = true;
                }
            } else if (data.game_over) {
                showMessage(`Game Over! The word was: ${data.word}. Final Score: ${data.total_score}`);
                guessInput.disabled = true;
                submitButton.disabled = true;
                hintButton.disabled = true;
            }
            
        } catch (error) {
            console.error('Error:', error);
            showMessage('Error submitting guess', true);
        }
    }
    
    async function getHint() {
        try {
            const response = await fetch('/api/hint', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.error) {
                showMessage(data.error, true);
                return;
            }
            
            if (data.letter) {
                // Update total score
                totalScoreSpan.textContent = data.total_score;
                
                // Find the key element
                const key = keyboard.querySelector(`button[data-key="${data.letter.toUpperCase()}"]`);
                if (key) {
                    if (!key.classList.contains('correct')) {
                        key.className = 'key wrong-position';
                        showMessage(`Hint: The word contains the letter ${data.letter.toUpperCase()}`);
                        hintButton.disabled = true;
                        hintButton.title = "Hint already used for this level";
                    } else {
                        showMessage('That letter is already correctly placed!', true);
                    }
                }
            } else {
                showMessage('No new letters to hint - try guessing the letters you see in red!', true);
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('Error getting hint', true);
        }
    }
    
    // Add event listeners
    submitButton.addEventListener('click', submitGuess);
    guessInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitGuess();
        }
    });
    
    hintButton.addEventListener('click', getHint);
    
    // Initialize the game
    createGameBoard();
});
