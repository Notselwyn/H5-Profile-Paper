#include <iostream>

unsigned int findWinner(unsigned int gameArray[9]) {
    for (unsigned int i = 1; i < 3; i++) {
        for (unsigned int j = 0; j < 3; j++) {
            if (gameArray[j*3] == i && gameArray[j*3 + 1] == i && gameArray[j*3 + 2] == i) { // Horizontal 
                return i;
            } else if (gameArray[j] == i && gameArray[j+3] == i && gameArray[j+6] == i) { // Vertical
                return i;
            }
        }
        if (gameArray[0] == i && gameArray[4] == i && gameArray[8] == i) { // Diagonal (0,0) -> (2,2)
            return i;
        } else if (gameArray[2] == i && gameArray[4] == i && gameArray[6] == i) { // Diagonal (2,0) -> (0,2)
            return i;
        }
    }
    for (unsigned int i = 0; i < 9; i++) { // Check if all cells are taken; if there are, it has to be a draw
        if (gameArray[i] == 0) {
            return 0;
        }
    }
    return 3;
}

int getBestMove(unsigned int gameArray[9], int* parentWins, bool* nextChild, unsigned int turnInt, unsigned int depth) {
    int bestMove = -1;
    unsigned int winner = findWinner(gameArray);
    if (winner == 2) { // AI wins
        *parentWins = 1;
        *nextChild = true;
    } else if (winner == 1) { // Player wins
        *parentWins = -1;
        *nextChild = true;
    } else if (winner == 3) { // Draw
        *parentWins = -2;
        *nextChild = true;
    } else { // No team won: continue
        *nextChild = false;
        for (unsigned int i = 0; i < 9; i++) {
            unsigned int highestWins = 0;
            if (gameArray[i] == 0) {
                int childWins = 0;
                bool nextChild = false;
                gameArray[i] = turnInt;
                unsigned int bestMoveTmp = getBestMove(gameArray, &childWins, &nextChild, (turnInt) % 2 + 1, depth+1);
                gameArray[i] = 0;
                *parentWins += childWins;

                if (bestMoveTmp == -2) {
                    continue;
                } else if (nextChild == true && (childWins == 1 || childWins == -2)) { // AI Win or draw
                    return i;
                } else if (nextChild == true && childWins == -1) { // Player Win 
                    if (depth == 1) {
                        return i;
                    }
                    return -2;
                } else if (highestWins < childWins) {
                    bestMove = i;
                    highestWins = childWins;
                }
            }
        }
    }
    return bestMove;
}

int main(){
    unsigned int gameArray[9] = { 0, 0, 0,
                                  0, 0, 0,
                                  0, 0, 0, };
    unsigned int turnInt = 1;
    bool nextChild = false;
    while (true) {
        for (int i = 0; i < 9; i++) {
            if (i % 3 == 0 && i > 0) {
                std::cout << "\n";
            }
            std::cout << gameArray[i] << " ";
        }

        int inputIndex = 0;
        std::cout << "\n\nEnter an index (0-8): ";
        std::cin >> inputIndex;
        while ((inputIndex < 0) || (inputIndex > 8) || (gameArray[inputIndex] != 0)) {
            std::cout << "\nThat cell is invalid. Please pick another one. \nEnter an index (0-8): ";
            std::cin >> inputIndex;

        }
        gameArray[inputIndex] = 1; 

        int wins = 0;
        bool nextChild = false;
        int bestIndex = getBestMove(gameArray, &wins, &nextChild, turnInt, 1);
        if (nextChild == true) {
            if (wins == 1) {
                std::cout << "Match ended: the AI won" << "\n";
            } else if (wins == -1) {
                std::cout << "Math ended: the player Won" << "\n";
            } else {
                std::cout << "Match ended: draw" << "\n";
            }
            break;
        } else {
            std::cout << "The best move for AI is: " << bestIndex << "\n";
            gameArray[bestIndex] = 2;
        }
    }
    return 0;
}

