#include <iostream>
#include <string>
#include <fstream>

unsigned int findWinner(unsigned int gameArray[9]) {
    for (unsigned int i = 1; i < 3; i++) {
        for (unsigned int j = 0; j < 3; j++) {
            if (gameArray[j*3] == i && gameArray[j*3+1] == i && gameArray[j*3+2] == i) { // Horizontal 
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

int getBestMove(unsigned int gameArray[9], int* parentWins, unsigned int turnInt, unsigned int depth) {
    int nextBestMove = -1;
    int nextWorstMove = -1; 
    int bestMove = -1;
    int worstMove = -1;
    unsigned int wins = 0;
    unsigned int losses = 0;
    bool nextWinnerExists = false;
    bool winnerExists = false;
    unsigned int winner = findWinner(gameArray);

    if (winner == turnInt % 2 + 1) { // Previous won, Stel: nu = 1 en winner() geeft 2 dan return -2 naar vorige
        *parentWins = -1;
        return -2;
    } else if (winner == turnInt) { // Previous lost, Stel: nu = 2 en winner() geeft 2 dan return -3 naar vorige
        *parentWins = 1;
        return -3;
    } else if (winner == 3) { // Draw
        *parentWins = 0;
        return -4;
    } else { // No team won: continue
        int highestWlr = -99999;
        for (unsigned int i = 0; i < 9; i++) {
            if (gameArray[i] == 0) {
                int childWlr = 0;

                gameArray[i] = turnInt;
                int childBestMove = getBestMove(gameArray, &childWlr, turnInt % 2 + 1, depth + 1);
                gameArray[i] = 0;
                *parentWins += childWlr; 
                if (childBestMove >= 0 && highestWlr < childWlr && winnerExists == false) {
                    bestMove = i;
                    highestWlr = childWlr;
                } else if (childBestMove == -2) {
                    wins += 1;
                    bestMove = i;
                    nextBestMove = i;
                    winnerExists = true;
                    nextWinnerExists = true;
                } else if (childBestMove == -4) {
                    if (winnerExists == false) {
                        bestMove = i;
                    }
                } else if (childBestMove == -3) {
                    losses += 1;
                    worstMove = i;
                    nextWorstMove = i;
                } else if (childBestMove == -5) {
                    wins += 1;
                    winnerExists = true;
                    if (wins == 1) {
                        highestWlr = childWlr;
                        bestMove = i;
                    } else if (highestWlr < childWlr && nextWinnerExists == false) {
                        bestMove = i;
                    }
                } else if (childBestMove == -6 || childBestMove == -9) {
                    losses += 1;
                    worstMove = i;
                }
            }
        }
    }

    if (depth == 1) {
        if (nextBestMove != -1) {
            return nextBestMove;
        }
        return bestMove;
    } 
    if (nextWorstMove != -1) {
        return nextWorstMove;
    } else if (nextBestMove != -1) {
        return -6;
    } else if (losses >= 2) {
        return -5;
    } else if (worstMove != -1) {
        return worstMove;
    } else if (wins >= 2) { // Not merged with nextBestMove != 1 because of priorization
        return -6;
    } 

    return bestMove;
}


void appendToCSV(std::ofstream* file, unsigned int state[9], int output, int wins) {
    std::string stateStr = "";
    for (int i = 0; i < 9; i++) {
        stateStr += std::to_string(state[i]);
    }
    *file << stateStr << "," << output << "," << wins << "\n";
}


// Cellstates and winner states: Empty = 0, Player = 1, AI = 2, Draw = 3
// Exit codes: -1 = No move found, -2 = Won next,   -3 = Lost next,                     -4 = Draw next, 
//             -5 = Won future unsolvable,          -6 = Lost future unsolvable,        -7 = All draws
//             -8 = Won (warning) future,           -9 = Lost (warning) future
int main(){
    unsigned int gameArray[9] = { 0, 0, 0,
                                  0, 0, 0,
                                  0, 0, 0, }; 

    bool gather_dataset = true;


    if (!gather_dataset) {
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
            unsigned int turnInt = 2;
            int bestIndex = getBestMove(gameArray, &wins, turnInt, 1);
            if (bestIndex == -2) {
                std::cout << "Match ended: the AI won" << "\n";
                break;
            } else if (bestIndex == -3) {
                std::cout << "Math ended: the player Won" << "\n";
                break;
            } else if (bestIndex == -4) {
                std::cout << "Match ended: draw" << "\n";
                break;
            } else {
                std::cout << "The best move for AI is: " << bestIndex << "\n";
                gameArray[bestIndex] = 2;
            }
        }
    } else {
        std::ofstream file;
        file.open("tictactoe_dataset.csv");
        file << "state,best,wins\n"; // Overwrite existing data, for debugging
        file.close();
        file.open("tictactoe_dataset.csv", std::ios_base::app); // Open in append mode


        unsigned int turnInt = 0;
        int wins = 0;
        int bestIndex = 0;
        for (int a = 0; a < 3; a++) {
            for (int b = 0; b < 3; b++) {
                for (int c = 0; c < 3; c++) {
                    for (int d = 0; d < 3; d++) {
                        for (int e = 0; e < 3; e++) {
                            for (int f = 0; f < 3; f++) {
                                for (int g = 0; g < 3; g++) {
                                    for (int h = 0; h < 3; h++) {
                                        for (int i = 0; i < 3; i++) {
                                            gameArray[0] = a;
                                            gameArray[1] = b;
                                            gameArray[2] = c;
                                            gameArray[3] = d;
                                            gameArray[4] = e;
                                            gameArray[5] = f;
                                            gameArray[6] = g;
                                            gameArray[7] = h;
                                            gameArray[8] = i;
                                            turnInt = 2;
                                            wins = 0;
                                            bestIndex = getBestMove(gameArray, &wins, turnInt, 1);
                                            appendToCSV(&file, gameArray, bestIndex, wins);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return 0;
}

