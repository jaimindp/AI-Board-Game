# Board-Game
This repository contains a program which plays Chinese Checkers. For a description of the game, refer to https://en.wikipedia.org/wiki/Halma

This implementation is a two player game where the goal is to move all pieces of a side to the opposition corner or 'camp' where the opposition starts from. The Python script is a variation from that entered in a tournament playing two sides against one another. In this version, the computer plays against itself and displays the history of moves for an entire game.

The script utilises the minimax algorithm with alpha beta pruning up to a specified depth. A function to evaluate the value of moves is implemented which is calculated based on the board configuration before and after each possible move. The higher the depth of pruning, more moves are considered for a player's own pieces and opposition's pieces resulting in a better performing AI player.

There were various rules required for the competition:

1. Spoiling tactics cannot be used (when a player blocks off spaces in it's own camp to prevent the opposition from entering  these spaces)
2. 
