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
    int bestMove = -1;
    int wlr = 0;
    bool drawExists = false;
    bool winnerExists = false;
    unsigned int winner = findWinner(gameArray);
    if (winner == (turnInt) % 2 + 1) { // Previous won
        *parentWins = 1;
        return -2;
    } else if (winner == turnInt) { // Previous lost
        *parentWins = -1;
        return -3;
    } else if (winner == 3) { // Draw
        *parentWins = 0;
        return -4;
    } else { // No team won: continue
        for (unsigned int i = 0; i < 9; i++) {
            int highestWins = -99999;
            if (gameArray[i] == 0) {
                int childWins = 0;
                gameArray[i] = turnInt;
                int bestMoveTmp = getBestMove(gameArray, &childWins, (turnInt) % 2 + 1, depth+1);
                gameArray[i] = 0;
                *parentWins += childWins;
                if (bestMoveTmp == -2) {
                    wlr += 1;
                    bestMove = i;
                    winnerExists = true;
                } else if (bestMoveTmp == -4) {
                    wlr += 1;
                    drawExists = true;
                    if (winnerExists == false) {
                        bestMove = i;
                    }
                } else if (bestMoveTmp == -3) {
                    wlr -= 1;
                } else if (highestWins < childWins && winnerExists == false && drawExists == false) {
                    bestMove = i;
                    highestWins = childWins;
                }
            }
        }
    }

    if (wlr == -9) {
        return -3; // All children lost; might want to change the parent as well then
    } else if (wlr == 9) {
        return -2; // All the children won, same as above but this is probably impossible
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
// Exit codes: -1 = No best move, -2 = AI won, -3 = Player won, -4 = Draw, -5 = Skip using recursion
int main(){
    unsigned int gameArray[9] = { 0, 0, 0,
                                  0, 0, 0,
                                  0, 0, 0, }; 

    bool gather_dataset = false;


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
            if (bestIndex == 2) {
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


        unsigned int turnInt = 2;
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
                                            turnInt = 1;
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

