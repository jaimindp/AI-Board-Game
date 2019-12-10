# AI-Board-Game
This repository contains a program which plays Halma (a variation of Chinese-Checkers). Description of the game: https://en.wikipedia.org/wiki/Halma

This implementation is a two player game where the goal is to move all of your own pieces to the opposition corner or 'camp' where the opposition starts. The Python script is a variation of that entered in a tournament playing two sides against each another. In this version, the computer plays against itself and displays the history of moves for the entire game.

Starting board layout

![Image description](https://github.com/jaimindp/AI-Board-Game/blob/master/end_game)

Black win board layout

![Image description](https://github.com/jaimindp/AI-Board-Game/blob/master/start_game)

Program placed 29th of 750 competition entries

Competition specific rules:

1. Spoiling tactics cannot be used (when a player blocks off spaces in it's own camp to prevent the opposition from entering  these spaces: http://www.cyningstan.com/post/1060/halmas-spoiling-strategy-revisited)
2. There is a time limit specified by the Tournament Agent, if an AI player runs out of time, they lose.
3. If any piece can be moved out of starting camp, this must be played before any other moves.

The script utilises the minimax algorithm with alpha-beta pruning up to a specified depth. A function to evaluate the value of moves is implemented which is calculated based on the board configuration before and after each possible move. The higher the depth of pruning, more moves are considered for a player's own pieces and opposition's pieces resulting in a better performing AI player. 

A pruning depth of 3 was used completing games in under 1 minute. If a pruning depth of 4 is used, the AI agent performs improves however games can take up to 1hr. A strategy to implement a depth of pruning based on how much time for the game is remaining ensures the AI does not run out of time but uses an optimal game playing strategy.

