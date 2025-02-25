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
    const gameOverModal = document.getElementById('gameOverModal');
    const closeModalBtn = document.querySelector('.close');
    const gameOverTitle = document.getElementById('gameOverTitle');
    const gameOverScore = document.getElementById('gameOverScore');
    const gameOverStaircase = document.getElementById('gameOverStaircase');
    const staircase = document.querySelector('.staircase');
    const playAgainButton = document.getElementById('playAgainButton');
    
    const keyboardLayout = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'DEL']
    ];
    
    let currentLevel = 3;
    
    function trackGameEvent(eventName, data) {
        // Implement Google Analytics event tracking here
        console.log(`Tracking event: ${eventName}`, data);
    }
    
    // Track game start
    trackGameEvent('game_start', {
        starting_level: currentLevel
    });
    
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
    }
    
    function createKeyboard() {
        keyboard.innerHTML = '';
        keyboardLayout.forEach((row, i) => {
            const keyboardRow = document.createElement('div');
            keyboardRow.className = 'keyboard-row';
            
            row.forEach(key => {
                const button = document.createElement('button');
                button.className = 'key';
                button.textContent = key;
                button.setAttribute('data-key', key);
                
                if (key === 'ENTER') {
                    button.onclick = submitGuess;
                } else if (key === 'DEL') {
                    button.onclick = () => {
                        guessInput.value = guessInput.value.slice(0, -1);
                    };
                } else {
                    button.onclick = () => {
                        if (guessInput.value.length < currentLevel) {
                            guessInput.value += key.toLowerCase();
                        }
                    };
                }
                
                keyboardRow.appendChild(button);
            });
            
            keyboard.appendChild(keyboardRow);
        });
    }
    
    function updateStaircase(completedWords) {
        staircase.innerHTML = '';
        
        // Create steps for levels 3 to 8
        for (let level = 3; level <= 8; level++) {
            const step = document.createElement('div');
            step.className = 'step';
            step.style.setProperty('--level', level - 3);  // For indentation
            
            // Find if this level was completed
            const completedWord = completedWords ? completedWords.find(w => w.level === level) : null;
            
            if (completedWord) {
                step.classList.add('completed');
                step.innerHTML = `${level}: ${completedWord.word} <span class="attempts">(${completedWord.attempts} tries)</span>`;
            } else if (level === currentLevel) {
                step.classList.add('current');
                step.textContent = `${level}: Current Level`;
            } else if (level < currentLevel) {
                step.textContent = `${level}: Skipped`;
            } else {
                step.textContent = '';  // Leave future levels blank
            }
            
            staircase.appendChild(step);
        }
    }
    
    async function submitGuess() {
        const guess = guessInput.value.toLowerCase();
        if (!guess) return;
        
        try {
            const response = await fetch('/guess', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    guess: guess
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                showMessage(data.error, true);
                return;
            }
            
            // Update attempts and score
            attemptsSpan.textContent = data.attempts;
            totalScoreSpan.textContent = data.total_score;
            
            // Get the current row
            const currentRow = gameBoard.children[data.attempts - 1];
            
            // Update the cells with the result
            data.result.forEach((result, index) => {
                const cell = currentRow.children[index];
                cell.textContent = guess[index].toUpperCase();
                
                // Update cell color based on result
                if (result === 2) {
                    cell.className = 'cell correct';
                    // Update keyboard
                    const key = keyboard.querySelector(`button[data-key="${guess[index].toUpperCase()}"]`);
                    if (key) key.className = 'key correct';
                } else if (result === 1) {
                    cell.className = 'cell wrong-position';
                    // Update keyboard
                    const key = keyboard.querySelector(`button[data-key="${guess[index].toUpperCase()}"]`);
                    if (key && !key.classList.contains('correct')) key.className = 'key wrong-position';
                } else {
                    cell.className = 'cell wrong';
                    // Update keyboard
                    const key = keyboard.querySelector(`button[data-key="${guess[index].toUpperCase()}"]`);
                    if (key && !key.classList.contains('correct') && !key.classList.contains('wrong-position')) {
                        key.className = 'key wrong';
                    }
                }
            });
            
            // Update attempts display
            attemptsSpan.textContent = data.attempts;
            
            // Clear input
            guessInput.value = '';
            
            if (!data.is_correct && !data.game_over) {
                // Track incorrect guess
                trackGameEvent('incorrect_guess', {
                    level: currentLevel,
                    attempt: data.attempts
                });
            }
            
            if (data.game_over) {
                // Track game over event
                trackGameEvent('game_over', {
                    final_score: data.total_score,
                    final_level: currentLevel,
                    completed_words: data.completed_words ? data.completed_words.length : 0
                });
                
                // Update and display stats
                const isWin = currentLevel > 8;  // Won if completed level 8
                const stats = updateStats(currentLevel, data.total_score, isWin);
                displayStats(stats);
                
                gameOverTitle.textContent = "Game Over!";
                gameOverScore.innerHTML = `Final Score: ${data.total_score}<br><br>Correct Word: ${data.word}`;
                gameOverModal.style.display = 'block';
            }
            
            if (data.is_correct && !data.game_over) {
                // Track level completion
                trackGameEvent('level_complete', {
                    level: currentLevel,
                    attempts: data.attempts,
                    score: data.total_score
                });
                
                showMessage('Level Complete! Moving to next level...');
                currentLevel = data.current_level;
                currentLevelSpan.textContent = currentLevel;
                
                setTimeout(() => {
                    createGameBoard();
                    // Reset keyboard colors
                    keyboard.querySelectorAll('.key').forEach(key => {
                        if (key.getAttribute('data-key') !== 'ENTER' && key.getAttribute('data-key') !== 'DEL') {
                            key.className = 'key';
                        }
                    });
                    // Enable hint button for new level
                    hintButton.disabled = false;
                    hintButton.title = "Get a hint (-1 point)";
                }, 1500);
            }
            
            if (data.is_correct) {
                // Track correct guess
                trackGameEvent('correct_guess', {
                    level: currentLevel,
                    attempt: data.attempts
                });
            }
            
            if (data.completed_words) {
                updateStaircase(data.completed_words);
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('Error submitting guess', true);
        }
    }
    
    async function getHint() {
        try {
            const response = await fetch('/hint', {
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
                // Track hint usage
                trackGameEvent('hint_used', {
                    level: currentLevel,
                    remaining_score: data.total_score
                });
                
                // Update total score
                totalScoreSpan.textContent = data.total_score;
                
                // Update keyboard
                const key = keyboard.querySelector(`button[data-key="${data.letter.toUpperCase()}"]`);
                if (key) {
                    key.className = 'key wrong-position';
                }
                
                showMessage(`Hint: The word contains the letter ${data.letter.toUpperCase()}`);
                hintButton.disabled = true;
                hintButton.title = "Hint already used for this level";
            } else {
                showMessage('No new letters to hint - try guessing the letters you see in red!', true);
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('Error getting hint', true);
        }
    }
    
    // Stats management functions
    function getStats() {
        const defaultStats = {
            gamesPlayed: 0,
            gamesWon: 0,
            totalLevelsReached: 0,
            topScore: 0
        };
        
        const stats = localStorage.getItem('expandle_stats');
        return stats ? JSON.parse(stats) : defaultStats;
    }

    function updateStats(finalLevel, finalScore, isWin) {
        const stats = getStats();
        stats.gamesPlayed++;
        stats.totalLevelsReached += finalLevel;
        stats.topScore = Math.max(stats.topScore, finalScore);
        if (isWin) stats.gamesWon++;
        
        localStorage.setItem('expandle_stats', JSON.stringify(stats));
        return stats;
    }

    function displayStats(stats) {
        document.getElementById('gamesPlayed').textContent = stats.gamesPlayed;
        document.getElementById('winRate').textContent = 
            ((stats.gamesWon / stats.gamesPlayed) * 100).toFixed(1) + '%';
        document.getElementById('topScore').textContent = stats.topScore;
        document.getElementById('avgLevel').textContent = 
            (stats.totalLevelsReached / stats.gamesPlayed).toFixed(2);
    }

    // Add event listeners
    submitButton.addEventListener('click', submitGuess);
    guessInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitGuess();
        }
    });
    
    // Add hint button event listener
    hintButton.addEventListener('click', getHint);

    // Close modal when clicking the X
    closeModalBtn.onclick = function() {
        gameOverModal.style.display = "none";
    }
    
    // Close modal when clicking outside of it
    window.onclick = function(event) {
        if (event.target == gameOverModal) {
            gameOverModal.style.display = "none";
        }
    }
    
    // Handle play again button click
    playAgainButton.addEventListener('click', async function() {
        try {
            const response = await fetch('/', {
                method: 'GET'
            });
            
            if (response.ok) {
                window.location.reload();
            } else {
                showMessage('Error starting new game', true);
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('Error starting new game', true);
        }
    });
    
    // Initialize game
    createGameBoard();
    createKeyboard();
});
