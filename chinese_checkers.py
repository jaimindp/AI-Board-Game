import time
import random
import copy
import collections
import os.path
from os import path
from ast import literal_eval

# Global variables for number of positions searched and pruned
tot_search_white = 0
tot_search_black = 0
prune_white = 0
prune_black = 0


# Class of board coordinate
class Board_Coord:
    value = -1
    value_2 = -1
    locked = False

    def __init__(self,coordinate):
        self.coordinate = coordinate


# Move class containing the variables required for each possible move
class Move:
    def __init__(self, start, end, value, parent):
        self.start = start
        self.end = end
        self.value = value
        self.parent = parent


# Return the layout of the board
def Print_Board(white_list, black_list):
    board_rep = ''

    for i in range(16):
        for j in range(16):
            if (j, i) in white_list:
                board_rep += ' W'
            elif (j, i) in black_list:
                board_rep += ' B'
            else:
                board_rep += ' .'

        board_rep += '\n'
    print(board_rep)


# Returns the values of the heuristic function
def Print_Heuristic_vals(board, w_b):
    board_rep = ''

    for i in range(16):
        for j in range(16):
            this_space = ""
            if w_b == 'white':
                this_value = str(board[i][j].value)
                for k in range(5 - len(this_value)):
                    this_space = this_space + " "
                board_rep = board_rep + this_space + this_value
            else:
                this_value = str(board[i][j].value_2)
                for k in range(5 - len(this_value)):
                    this_space = this_space + " "
                board_rep = board_rep + this_space + this_value
        board_rep += '\n'
    print(board_rep)


# Function to insert the coordinate object in the right place for the admissible heuristic
def InsertList_H_2(coordinate, list):
    index = len(list)
    for i in range(len(list)):
        if list[i].value_2 < coordinate.value_2:
            index = i
            break

    # Inserting n in the list
    list = list[:index] + [coordinate] + list[index:]
    return list


# Function to insert the coordinate object in the right place for the admissible heuristic
def InsertList_H_3(coordinate, list):
    index = len(list)
    for i in range(len(list)):
        if list[i].value < coordinate.value:
            index = i
            break

    # Inserting n in the list
    list = list[:index] + [coordinate] + list[index:]
    return list


# Returns the total value for the position of these pieces
def Board_Total(board, piece_list, w_b):

    total = 0
    if w_b == "white":
        for piece in piece_list:
            total += board[piece[1]][piece[0]].value
    else:
        for piece in piece_list:
            total += board[piece[1]][piece[0]].value_2

    return total


# Function to assign the heuristic scores for the board
# This implementation uses the min horizontal or vertical distance from your own camp corner
def Assign_Board(board, w_b):

    # Implement the search queue in a list
    if w_b == 'black':
        for y_coord in range(16):
            for x_coord in range(16):
                board[y_coord][x_coord].value_2 = 15 - y_coord + 15 - x_coord
    else:
        for y_coord in range(16):
            for x_coord in range(16):
                board[y_coord][x_coord].value = 15 - y_coord + 15 - x_coord
    return board


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
############################################## STARTING AND FINISHING PROCEDURE #######################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


# Finished state
def Is_Finished(board, piece_list):
    finished = True
    if piece_list.get(next(iter(piece_list))) == 1:
        for piece in piece_list:
            if not ((piece[0] <= 4 and piece[1] <= 1) or (piece[0] <= 3 and piece[1] == 2) or (piece[0] <= 2 and piece[1] == 3) or (piece[0] <= 1 and piece[1] == 4)):
                finished = False
    else:
        for piece in piece_list:
            if not ((piece[0] >= 11 and piece[1] >= 14) or (piece[0] >= 12 and piece[1] == 13) or (piece[0] >= 13 and piece[1] == 12) or (piece[0] >= 14 and piece[1] == 11)):
                finished = False

    return finished


# Unlock pieces
def Unlock(board, piece_list):
    for piece in piece_list:
        value_board[piece[1]][piece[0]].locked = False


# Function to return a list to play next to move out of camp
def Camp_Spaces_Left(board, piece_list):

    # to_move is a dict of camp coordinates which have not been filled
    # end_camp is the list of camp coordinates which have been filled
    camp_spaces = []
    camp_filled = []

    # Each line corresponds to how close to camp edge it is
    inner_camp = 0
    outer_camp = 0

    if piece_list.get(next(iter(piece_list))) == 1:
        end_camp = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (0, 2), (1, 2),(2, 2), (3, 2), (0, 3), (1, 3), (2, 3), (0, 4), (1, 4)]
        for piece in piece_list:
            if piece[0] + piece[1] < 4:
                inner_camp += 1
            elif piece[0] + piece[1] == 4 or piece[0] + piece[1] == 5:
                outer_camp += 1
    else:
        end_camp = [(15, 15), (14, 15), (13, 15), (12, 15), (11, 15), (15, 14), (14, 14), (13, 14), (12, 14),(11, 14), (15, 13), (14, 13), (13, 13), (12, 13), (15, 12), (14, 12), (13, 12), (15, 11),(14, 11)]
        for piece in piece_list:
            if piece[0] + piece[1] > 26:
                inner_camp += 1
            elif piece[0] + piece[1] == 26 or piece[0] + piece[1] == 25:
                outer_camp += 1

    for coord in end_camp:
        if coord not in piece_list:
            camp_spaces.append(coord)
        else:
            camp_filled.append(coord)

    is_locked = False

    if inner_camp == 10:
        for coord in camp_filled:
            board[coord[1]][coord[0]].locked = True
            is_locked = True
    elif inner_camp != 10 and outer_camp > 6:
        for piece in piece_list:
            if piece not in camp_filled:
                board[piece[1]][piece[0]].locked = True

    # Do you need to_move
    return camp_spaces, camp_filled, is_locked


# New Heuristic for when there are pieces in the opposition camp
def End_Heuristic(board, black_list, white_list, w_b):

    # Reset the heuristic for all coordinates before reassigning
    if w_b == 'white':
        for i in range(16):
            for j in range(16):
                board[j][i].value = -1
        camp_spaces, camp_filled,  is_locked = Camp_Spaces_Left(board, white_list)
    else:
        for i in range(16):
            for j in range(16):
                board[j][i].value_2 = -1
        camp_spaces, camp_filled, is_locked = Camp_Spaces_Left(board, black_list)

    order_x = [0, 1, 0, -1, 1, 1, -1, -1]
    order_y = [-1, 0, 1, 0, -1, 1, 1, -1]

    # Exit if the game state is in the finished position for this colour
    if len(camp_spaces) == 0:
        print("Game finished for " + w_b + " player")
        return board

    # If there are less than 5 gaps on the board to fill, make a new lowest value for the heuristic
# Consider locking pieces in enemy camp in place at this point if reachable
    if is_locked:
        camp_spaces.sort(key=lambda x: abs(x[0]-x[1]))
        if w_b == "white":
            board[camp_spaces[0][1]][camp_spaces[0][0]].value = 0
            search_queue = [board[camp_spaces[0][1]][camp_spaces[0][0]]]

        else:
            board[camp_spaces[0][1]][camp_spaces[0][0]].value_2 = 0
            search_queue = [board[camp_spaces[0][1]][camp_spaces[0][0]]]

    # If the game is not near the end
    else:
        if w_b == 'black':
            board[15][15].value_2 = 0
            search_queue = [board[15][15]]

        else:
            board[0][0].value = 0
            search_queue = [board[0][0]]

    # Protocol for invalid locations
    while len(search_queue) != 0:  # and queue not empty
        this_node = search_queue[0]
        search_queue.pop(0)

        # Loop to check all adjacent values
        for i in range(8):
            x_coord = this_node.coordinate[0] + order_x[i]
            y_coord = this_node.coordinate[1] + order_y[i]

            # Assign costs for direction from this node
            if order_x[i] == 0 or order_y[i] == 0:
                if w_b == 'white':
                    min_cost = -10
                else:
                    min_cost = -10
            else:
                # 14 or 15 are best
                if w_b == 'white':
                    min_cost = -13
                else:
                    min_cost = -13

            # Does not go out of bounds node not visited already
            if not (x_coord < 0 or y_coord < 0):
                if not (x_coord >= 16 or y_coord >= 16):
                    if w_b == 'white':
                        if board[y_coord][x_coord].value == -1:
                            board[y_coord][x_coord].value = min_cost + this_node.value
                            search_queue = InsertList_H_3(board[y_coord][x_coord], search_queue)

                    else:
                        if board[y_coord][x_coord].value_2 == -1:
                            # Add the cost of this path to the total length of the path
                            board[y_coord][x_coord].value_2 = min_cost + this_node.value_2
                            search_queue = InsertList_H_2(board[y_coord][x_coord], search_queue)

    if len(camp_filled) > 7:

        if w_b == 'white':
            for i in range(5):
                for j in range(5):
                    if (i <= 4 and j <= 1) or (i <= 3 and j == 2) or (i <= 2 and j == 3) or (i <= 1 and j == 4):
                        board[j][i].value = board[j][i].value + 20
        else:
            for i in range(11,16):
                for j in range(11,16):
                    if (i >= 11 and j >= 14) or (i >= 12 and j == 13) or (i >= 13 and j == 12) or (i >= 14 and j == 11):
                        board[j][i].value_2 = board[j][i].value_2 + 20


        # Print_Heuristic_vals(board, "white")

    return board

# Function to return a list to play next to move out of camp
def Move_From_Camp_Lines(board, piece_list, w_b):

    # to_move = []

    # Each line corresponds to how close to camp edge it is
    line_1 = {}
    line_2 = {}
    line_3 = {}
    line_4 = {}
    line_5 = {}
    line_6 = {}

    # White camp procedure
    if w_b == 'white':
        for piece in piece_list:
            board[piece[1]][piece[0]].locked = True
            if (piece[0] >= 11 and piece[1] >= 14) or (piece[0] >= 12 and piece[1] == 13) or (piece[0] >= 13 and piece[1] == 12) or (piece[0] >= 14 and piece[1] == 11):
                # to_move.append(piece)
                if piece[0] + piece[1] == 25:
                    line_1[piece] = 1
                elif piece[0] + piece[1] == 26:
                    line_2[piece] = 1
                elif piece[0] + piece[1] == 27:
                    line_3[piece] = 1
                elif piece[0] + piece[1] == 28:
                    line_4[piece] = 1
                elif piece[0] + piece[1] == 29:
                    line_5[piece] = 1
                elif piece[0] + piece[1] == 30:
                    line_6[piece] = 1
                board[piece[1]][piece[0]].locked = False

    # Black camp procedure
    else:
        for piece in piece_list:
            board[piece[1]][piece[0]].locked = True

            if (piece[0] <= 4 and piece[1] <= 1) or (piece[0] <= 3 and piece[1] == 2) or (piece[0] <= 2 and piece[1] == 3) or (piece[0] <= 1 and piece[1] == 4):
                # to_move.append(piece)
                if piece[0] + piece[1] == 5:
                    line_1[piece] = 2
                elif piece[0] + piece[1] == 4:
                    line_2[piece] = 2
                elif piece[0] + piece[1] == 3:
                    line_3[piece] = 2
                elif piece[0] + piece[1] == 2:
                    line_4[piece] = 2
                elif piece[0] + piece[1] == 1:
                    line_5[piece] = 2
                elif piece[0] + piece[1] == 0:
                    line_6[piece] = 2
                board[piece[1]][piece[0]].locked = False

    pieces_in_camp = True
    if not line_1 and not line_2 and not line_3 and not line_4 and not line_5 and not line_6:
        pieces_in_camp = False
        for piece in piece_list:
            board[piece[1]][piece[0]].locked = False

    return pieces_in_camp


##################################################################################################################
##################################################################################################################
##################################################################################################################
######################################### STARTING AND FINISHING PROCEDURE END ###################################
##################################################################################################################
##################################################################################################################


# Recursive search function to look at hop moves and find maximal play
def Recursive_Search(board, white_list, black_list, start_coord, coordinate, prev_hops, all_moves, w_b, parent, depth, in_camp):
    depth += 1
    parent = parent[:depth]
    prev_hops[coordinate] = 1
    parent.append(coordinate)
    global contact

    # Search moves by calling Move function with the start and end coordinates
    if w_b == 'white':
        if not in_camp or (coordinate[0] <= start_coord[0] and coordinate[1] <= start_coord[1]):
            all_moves.append(Move(start_coord, coordinate, board[coordinate[1]][coordinate[0]].value - board[start_coord[1]][start_coord[0]].value, parent))
            global tot_search_white
            tot_search_white += 1
    else:
        if not in_camp or (coordinate[0] >= start_coord[0] and coordinate[1] >= start_coord[1]):
            all_moves.append(Move(start_coord, coordinate, board[coordinate[1]][coordinate[0]].value_2 - board[start_coord[1]][start_coord[0]].value_2, parent))
            global tot_search_black
            tot_search_black += 1

    move_x = [1, 1, 0, 1, -1, 0, -1, -1]
    move_y = [1, 0, 1, -1, 1, -1, 0, -1]

    # Loop through to check all directions
    for i in range(8):
        x_coord = coordinate[0] + move_x[i]
        y_coord = coordinate[1] + move_y[i]

        # Checking there is a piece in adjacent locations
        if not (x_coord < 0 or y_coord < 0) and not (x_coord >= 16 or y_coord >= 16):
            if (x_coord, y_coord) in white_list or (x_coord, y_coord) in black_list:
                if not contact:
                    if w_b == "white" and (x_coord, y_coord) in black_list:
                        contact = True
                    elif w_b == "black" and (x_coord, y_coord) in white_list:
                        contact = True

                x_coord = coordinate[0] + move_x[i] * 2
                # Next hop location must be empty and not previously visited
                y_coord = coordinate[1] + move_y[i] * 2
                if not (x_coord < 0 or y_coord < 0) and not (x_coord >= 16 or y_coord >= 16):
                    if (x_coord, y_coord) not in white_list and (x_coord, y_coord) not in black_list:
                        if (x_coord, y_coord) not in prev_hops:
                            if w_b == 'white':
                                all_moves = Recursive_Search(board, white_list, black_list, start_coord, (x_coord, y_coord), prev_hops, all_moves, 'white', parent, depth, in_camp)
                            else:
                                all_moves = Recursive_Search(board, white_list, black_list, start_coord, (x_coord, y_coord), prev_hops, all_moves, 'black', parent, depth, in_camp)
    depth -= 1
    return all_moves


# Search legal moves and return a list of best moves and a list of pieces to move
# Two strategies:
# 1 look at the furthest back pieces and see what their best moves are
# 2 look at the highest value moves first
def List_Moves(board, white_list, black_list, all_moves, w_b, in_camp):

    move_x = [1, 1, 0, 1, -1, 0, -1, -1]
    move_y = [1, 0, 1, -1, 1, -1, 0, -1]

    if w_b == 'white':
        piece_list = white_list
    else:
        piece_list = black_list

    # Loop through all pieces and find all possible moves for all piece
    for piece in piece_list:

        # Loop to check all adjacent operations
        for i in range(8):
            x_coord = piece[0] + move_x[i]
            y_coord = piece[1] + move_y[i]

            # Add valid one step move
            if not (x_coord < 0 or y_coord < 0) and not (x_coord >= 16 or y_coord >= 16):
                if (x_coord, y_coord) not in white_list and (x_coord, y_coord) not in black_list:
                    if w_b == 'white':
                        # Handling for pieces in camp
                        if not in_camp or (x_coord <= piece[0] and y_coord <= piece[1]):

                            # if (board[x_coord][y_coord].value - board[piece[1]][piece[0]].value) > 0:
                            all_moves.append(Move(piece, (x_coord, y_coord), board[y_coord][x_coord].value - board[piece[1]][piece[0]].value, [piece, (x_coord, y_coord)]))
                    else:
                        if not in_camp or (x_coord >= piece[0] and y_coord >= piece[1]):
                            # if (board[x_coord][y_coord].value_2 - board[piece[1]][piece[0]].value_2) > 0:
                            all_moves.append(Move(piece, (x_coord, y_coord), board[y_coord][x_coord].value_2 - board[piece[1]][piece[0]].value_2, [piece, (x_coord, y_coord)]))

                # Add a valid hop move
                else:
                    x_coord = piece[0] + move_x[i] * 2
                    y_coord = piece[1] + move_y[i] * 2
                    if not (x_coord < 0 or y_coord < 0) and not (x_coord >= 16 or y_coord >= 16):
                        if (x_coord, y_coord) not in white_list and (x_coord, y_coord) not in black_list:
                            if w_b == 'white':
                                all_moves = Recursive_Search(board, white_list, black_list, piece, (x_coord, y_coord), {}, all_moves, 'white', [piece], 1, in_camp)
                            else:
                                all_moves = Recursive_Search(board, white_list, black_list, piece, (x_coord, y_coord), {}, all_moves, 'black', [piece], 1, in_camp)

    all_moves = sorted(all_moves, key=lambda x: x.value, reverse=True)
    return all_moves


# This returns the board state and updates the value of the piece
def Move_Piece(piece_list, start_coord, end_coord, w_b):
    del piece_list[start_coord]
    if w_b == 'white':
        piece_list[end_coord] = 1
    else:
        piece_list[end_coord] = 2
    return piece_list


# Returns a list of coordinates closest to starting base
def Least_Val(board, piece_list):

    least_coords = []

    if piece_list.get(next(iter(piece_list))) == 1:
        least_val = -1000
        for piece in piece_list:
            if piece[0] + piece[1] > least_val:
                least_coords = []
                least_coords.append(piece)
                least_val = piece[0] + piece[1]

            elif piece[1] + piece[0] == least_val:
                least_coords.append(piece)
    else:
        least_val = 10000
        for piece in piece_list:
            if piece[0] + piece[1] < least_val:
                least_coords = []
                least_coords.append(piece)
                least_val = piece[0] + piece[1]

            elif piece[0] + piece[1] == least_val:
                least_coords.append(piece)

    return least_coords


# Function to  Play the pieces out of each respective starting camp
def Play_Out_Camp(board, white_list, black_list, move_list, w_b):
    best_move = None
    random.shuffle(move_list)

    # White's move
    if w_b == "white":
        max_value = -10000

        # Loop over potential moves
        for move in move_list:

            # Skip move if it starts outside camp or it doesn't move out of camp
            if board[move.start[1]][move.start[0]].locked:
                continue
            if not ((move.start[0] >= 11 and move.start[1] >= 14) or (move.start[0] >= 12 and move.start[1] == 13) or (move.start[0] >= 13 and move.start[1] == 12) or (move.start[0] >= 14 and move.start[1] == 11)):
                continue
            if (move.end[0] >= 11 and move.end[1] >= 14) or (move.end[0] >= 12 and move.end[1] == 13) or (move.end[0] >= 13 and move.end[1] == 12) or (move.end[0] >= 14 and move.end[1] == 11):
                continue

            Move_Piece(white_list, move.start, move.end, "white")
            value = Board_Total(board, white_list, "white") - Board_Total(board, black_list, "black")
            if value > max_value:
                max_value = value
                best_move = move

            del white_list[move.end]
            white_list[move.start] = 1

        # Procedure if there are no moves which can move a peice out of camp
        if best_move is None:
            for move in move_list:
                if board[move.start[1]][move.start[0]].locked:
                    continue
                if not ((move.start[0] >= 11 and move.start[1] >= 14) or (move.start[0] >= 12 and move.start[1] == 13) or (move.start[0] >= 13 and move.start[1] == 12) or (move.start[0] >= 14 and move.start[1] == 11)):
                    continue
                if move.end[0] > move.start[0] or move.end[1] > move.start[1]:
                    continue

                # Do best move anyway
                Move_Piece(white_list, move.start, move.end, "white")
                value = Board_Total(board, white_list, "white") - Board_Total(board, black_list, "black")
                if value > max_value:
                    max_value = value
                    best_move = move

                del white_list[move.end]
                white_list[move.start] = 1

    # Black's move
    else:
        min_value = 10000
        for move in move_list:
            if board[move.start[1]][move.start[0]].locked:
                continue
            if not ((move.start[0] <= 4 and move.start[1] <= 1) or (move.start[0] <= 3 and move.start[1] == 2) or (move.start[0] <= 2 and move.start[1] == 3) or (move.start[0] <= 1 and move.start[1] == 4)):
                continue
            if (move.end[0] <= 4 and move.end[1] <= 1) or (move.end[0] <= 3 and move.end[1] == 2) or (move.end[0] <= 2 and move.end[1] == 3) or (move.end[0] <= 1 and move.end[1] == 4):
                continue

            Move_Piece(black_list, move.start, move.end, "black")
            value = Board_Total(board, white_list, "white") - Board_Total(board, black_list, "black")

            if value < min_value:
                min_value = value
                best_move = move
            del black_list[move.end]
            black_list[move.start] = 2

        if best_move is None:
            for move in move_list:
                if board[move.start[1]][move.start[0]].locked:
                    continue
                if not ((move.start[0] <= 4 and move.start[1] <= 1) or (move.start[0] <= 3 and move.start[1] == 2) or (move.start[0] <= 2 and move.start[1] == 3) or (move.start[0] <= 1 and move.start[1] == 4)):
                    continue
                if move.end[0] < move.start[0] or move.end[0] < move.start[1]:
                    continue

                Move_Piece(black_list, move.start, move.end, "black")
                value = Board_Total(board, white_list, "white") - Board_Total(board, black_list, "black")

                if value < min_value:
                    min_value = value
                    best_move = move

                del black_list[move.end]
                black_list[move.start] = 2

    return best_move


# Alpha Beta pruning algorithm with input prune depth
def Alpha_Beta(board, white_list, black_list, w_b, in_camp, prune_depth):

    # Set everything parameters for alpha beta pruning
    if w_b == "white":
        best_value = -1000000000000
        beta = 1000000000000
        best_move = None
        least_pieces = Least_Val(board, white_list)
    else:
        best_value = 1000000000000
        alpha = -1000000000000
        best_move = None
        least_pieces = Least_Val(board, black_list)

    # Get all moves
    move_list = collections.deque([])
    if w_b == "white":
        move_list = List_Moves(board, white_list, black_list, move_list, 'white', in_camp)
    else:
        move_list = List_Moves(board, white_list, black_list, move_list, 'black', in_camp)

    # Print_Board(white_list, black_list)
    global previous_moves
    global white_camp
    global black_camp
    completed_moves = {}

    # Procedure if piece in own camp, returns null if none can be moved out
    if in_camp:
        this_move = Play_Out_Camp(board, white_list, black_list, move_list, w_b)
        if this_move:
            return this_move

    # Search moves and return best move
    for move in move_list:

        continue_loop = False
        move_start_end = str(move.start) + " " + str(move.end)

        # Skip move if move already computed, or if it can't move
        if move_start_end in completed_moves:
            continue
        completed_moves[move_start_end] = 1
        if board[move.start[1]][move.start[0]].locked:
            continue

        # Skip move if start and end of move have already been tried
        for history_move in previous_moves:
            if history_move.start == move.start and history_move.end == move.end:
                continue_loop = True

        # Skip move if piece cannot does not move out of camp
        if w_b == 'white':
            if move.start in black_camp:
                if move.end not in black_camp:
                    continue
        else:
            if move.start in white_camp:
                if move.end not in white_camp:
                    continue
        if continue_loop:
            continue

        # White's move
        if w_b == 'white':

            # Ensures only forward moves
            if board[move.start[1]][move.start[0]].value > board[move.end[1]][move.end[0]].value:
                continue

            white_list = Move_Piece(white_list, move.start, move.end, "white")
            value = Min_Value(board, white_list, black_list, best_value, beta, 0, in_camp, prune_depth)

            # Heuristic to prevent pieces getting stranded
            if move.start in least_pieces:
                value += 20 + 5 * abs(move.start[0] - move.start[1])

            # Storing move with greatest value
            if value > best_value:
                best_value = value
                best_move = move
            del white_list[move.end]
            white_list[move.start] = 1

            # Check for finish condition
            if Is_Finished(board, white_list):
                print("Game Finished white  a-b")
                return best_move

        # Black's move
        else:

            # Ensures only forward moves
            if board[move.start[1]][move.start[0]].value_2 > board[move.end[1]][move.end[0]].value_2:
                continue

            black_list = Move_Piece(black_list, move.start, move.end, "black")
            value = Max_Value(board, white_list, black_list, alpha, best_value, 0, in_camp, prune_depth)

            # Heuristic to prevent pieces getting stranded
            if move.start in least_pieces:
                value -= 20 + 5 * abs(move.start[0] - move.start[1])

            # Storing move with greatest value
            if value < best_value:
                best_value = value
                best_move = move
            del black_list[move.end]
            black_list[move.start] = 2

            # Check for finish condition
            if Is_Finished(board, black_list):
                print("Game Finished black a-b")
                return best_move

    # Return best move
    print(best_value)
    return best_move


# Max function for alpha beta pruning with a depth limit
def Max_Value(board, white_list, black_list, alpha, beta, cur_depth, in_camp, max_depth = 2):

    if cur_depth == 0:
        if Is_Finished(board, black_list):
            print("Game Finished black max")
            return -1000000

    cur_depth += 1

    in_camp_this = False
    if white_black == 2 and in_camp:
        in_camp_this = True

    # Return the value at this end depth
    if cur_depth == max_depth:
        return Board_Total(board, white_list, "white") - Board_Total(board, black_list, "black")

    value = -1000000000000
    global contact

    # Store all potential moves in a deque and loop through to determine the move with the highest value
    move_list = collections.deque([])
    move_list = List_Moves(board, white_list, black_list, move_list, 'white', in_camp_this)
    for move in move_list:

        white_list = Move_Piece(white_list, move.start, move.end, 'white')
        value = max(value, Min_Value(board, white_list, black_list, alpha, beta, cur_depth, in_camp_this, max_depth))

        del white_list[move.end]
        white_list[move.start] = 1

        if value >= beta:
            global prune_black
            prune_black += 1
            return value

        alpha = max(alpha, value)

    return value


# Min function for alpha beta pruning with depth limit
def Min_Value(board, white_list, black_list, alpha, beta, cur_depth, in_camp, max_depth = 2):

    if cur_depth == 0:
        if Is_Finished(board, white_list):
            print("Game finished White Min")
            return 1000000

    cur_depth += 1

    in_camp_this = False
    if white_black == 1 and in_camp:
        in_camp_this = True

    # Return the value at this end depth
    if cur_depth == max_depth:
        return Board_Total(board, white_list, "white") - Board_Total(board, black_list, "black")

    value = 1000000000000
    global contact

    # Store all potential moves in a deque and loop through to determine the move with the highest value
    move_list = collections.deque([])
    move_list = List_Moves(board, white_list, black_list, move_list, 'black', in_camp_this)
    for move in move_list:

        black_list = Move_Piece(black_list, move.start, move.end, 'black') # black only rn
        value = min(value, Max_Value(board, white_list, black_list, alpha, beta, cur_depth, in_camp_this, max_depth))

        del black_list[move.end]
        black_list[move.start] = 2

        if value <= alpha:
            global prune_white
            prune_white += 1
            return value

        beta = min(beta, value)

    return value


# For a move if user is white
def Play_White(board, white_list, black_list, in_camp, prune_depth):
    print("White coordinates")

    # Search for all possible moves and apply alpha beta pruning algorithm
    best_move = Alpha_Beta(board, white_list, black_list, 'white', in_camp, prune_depth)

    if best_move is None:
        return None, ''

    move_x = [1, 1, 0, 1, -1, 0, -1, -1]
    move_y = [1, 0, 1, -1, 1, -1, 0, -1]
    e_j = "J"

    # Loop to check all adjacent operations
    for i in range(8):
        x_coord = best_move.start[0] + move_x[i]
        y_coord = best_move.start[1] + move_y[i]
        if x_coord == best_move.end[0] and y_coord == best_move.end[1]:
            e_j = "E"

    print("Finished white turn")
    return best_move, e_j


# For a move if user is black
def Play_Black(board, white_list, black_list, in_camp, prune_depth):
    print("Black coordinates")

    # Search for all possible moves and apply alpha beta pruning alg
    best_move = Alpha_Beta(board, white_list, black_list, 'black', in_camp, prune_depth)

    if best_move is None:
        return None, ''

    move_x = [1, 1, 0, 1, -1, 0, -1, -1]
    move_y = [1, 0, 1, -1, 1, -1, 0, -1]
    e_j = "J"

    # Loop to check all adjacent operations
    for i in range(8):
        x_coord = best_move.start[0] + move_x[i]
        y_coord = best_move.start[1] + move_y[i]
        if x_coord == best_move.end[0] and y_coord == best_move.end[1]:
            e_j = "E"

    print("Finished black turn")
    return best_move, e_j


# Function to play an entire game, start to finish and return results
def Play_Game(white_black, value_board, depth_white, depth_black, time_left_w, time_left_b):

    # Selecting a pruning depth for game and the time left for the game
    white_tot_time = 0
    black_tot_time = 0
    last_two_b = []
    last_two_w = []
    global previous_moves

    # Loop to execute one move at a time
    for i in range(400):
        start_time = time.time()

        # For white move, look at previous moves and do not repeat any previous moves
        if white_black == 1:
            white_pre_move = time.time()
            if len(last_two_w) > 1:
                last_two_w = last_two_w[:2]
                previous_moves = last_two_w

            # After the 20th move
            if i // 2 < 20:
                depth_white_turn = 1
            else:
                depth_white_turn = depth_white

            # Get white pieces still in starting camp
            print("Playing white")
            in_camp = Move_From_Camp_Lines(value_board, white_list, "white")

            # Get heuristics for the current board position and find the best possible move
            value_board = End_Heuristic(value_board, black_list, white_list, 'white')
            value_board = End_Heuristic(value_board, black_list, white_list, 'black')
            move, e_j = Play_White(value_board, white_list, black_list, in_camp, depth_white_turn)

            # If no move returned then allow all pieces to be moved
            if move is None:
                print("Unlocking")
                Unlock(value_board, white_list)
                move, e_j = Play_White(value_board, white_list, black_list, in_camp, depth_white_turn)

            # White move timing and unlock the pieces for the next move
            white_post_move = time.time()
            white_tot_time += white_post_move - white_pre_move
            time_left_w -= white_post_move - white_pre_move
            Unlock(value_board, white_list)

        # For black move, look at previous moves and do not repeat any previous moves
        else:
            black_pre_move = time.time()
            if len(last_two_w) > 1:
                last_two_b = last_two_b[:2]
                previous_moves = last_two_b

            if not contact:
                depth_black_turn = 1
            else:
                depth_black_turn = depth_black

            # Get black pieces still in starting camp
            print("Playing black")
            in_camp = Move_From_Camp_Lines(value_board, black_list, "black")

            # Get heuristics for the current board position and find the best possible move
            value_board = End_Heuristic(value_board, black_list, white_list, 'white')
            value_board = End_Heuristic(value_board, black_list, white_list, 'black')
            move, e_j = Play_Black(value_board, white_list, black_list, in_camp, depth_black_turn)

            # If no move returned then allow all pieces to be moved
            if move is None:
                print("Unlocking")
                Unlock(value_board, black_list)
                move, e_j = Play_Black(value_board, white_list, black_list, in_camp, depth_black_turn)

            # Black move timing and unlock the pieces for the next move
            black_post_move = time.time()
            black_tot_time += black_post_move - black_pre_move
            time_left_b -= black_post_move - black_pre_move
            Unlock(value_board, black_list)

        # Loop over to print the list of jumps
        output = open("output.txt", "w+")
        for j in range(len(move.parent) - 1):
            output.write(e_j + " " + str(move.parent[j][0]) + "," + str(move.parent[j][1]) + " " + str(
                move.parent[j + 1][0]) + "," + str(move.parent[j + 1][1]) + "\n")
            print(e_j + " " + str(move.parent[j][0]) + "," + str(move.parent[j][1]) + " " + str(
                move.parent[j + 1][0]) + "," + str(move.parent[j + 1][1]))

        output.close()

        # Code to print board after move
        if white_black == 1:
            Move_Piece(white_list, move.parent[0], move.end, "white")
        else:
            Move_Piece(black_list, move.parent[0], move.end, "black")
        print("After Move\n")
        Print_Board(white_list, black_list)
        end_time = time.time()
        print("\n Move time: " + str(end_time - start_time))

        # Breaks loop when finished
        if Is_Finished(value_board, white_list):
            print("White finished in " + str((i + 2) // 2) + " moves")
            break

        if Is_Finished(value_board, black_list):
            print("Black finished in " + str((i + 2) // 2) + " moves")
            break

        print("Move no: " + str(i // 2))
        # Inserting previous moves
        if white_black == 1:
            last_two_w.insert(0, move)
            if len(last_two_w) > 2:
                last_two_w = last_two_w[:2]
        else:
            last_two_b.insert(0, move)
            if len(last_two_b) > 2:
                last_two_b = last_two_b[:2]

        if white_black == 1:
            white_black = 2
        else:
            white_black = 1


# Print statistics of game after finished
def Print_Statistics(depth_white, depth_black, very_start):

    # Printing the statistics for game play
    print("White Prune Depth")
    print(depth_white)
    print("Black Prune Depth")
    print(depth_black)
    print("Final Value Diff")

    very_end = time.time()
    print("Total game time: " + str(very_end - very_start))

    print("Total white time")
    print(white_tot_time)
    print("Total black time")
    print(black_tot_time)

    print("Time left white")
    print(time_left_w)
    print("Time left black")
    print(time_left_b)

    print("Tot search white: ")
    print(tot_search_white)
    print("Tot search black: ")
    print(tot_search_black)

    print("Whites pruned")
    print(prune_white)
    print("Blacks pruned")
    print(prune_black)


###################################################################################################
###################################################################################################
################################# Main function ###################################################
###################################################################################################
###################################################################################################
if __name__ == "__main__" :
    very_start = time.time()
    white_tot_time = 0
    black_tot_time = 0

    file = open("/Users/jaimin/PycharmProjects/ai2/venv/input.txt","r")

    input_file = file.read()
    lines = input_file.split("\n")
    file.close()

    # If white, white_black = 1
    white_black = 2
    if lines[1] == "WHITE":
        white_black = 1

    # Create board in a loop from input.txt
    white_list = {}
    black_list = {}
    y_counter = 0
    value_board = []

    for line in lines[3:]:
        this_line = []
        x_counter = 0
        for char in line:

            this_coord = Board_Coord((x_counter, y_counter))

            # Empty places are 0s
            if char == '.':
                this_line.append(this_coord)

            # Whites are 1s and blacks are 2s
            elif char == 'W':
                this_line.append(this_coord)

                # Add this coordinate
                white_list[(x_counter, y_counter)] = 1

            elif char == 'B':
                this_line.append(this_coord)

                # Add this coordinate
                black_list[(x_counter, y_counter)] = 2

            x_counter += 1

        value_board.append(this_line)
        y_counter += 1

    # Set pruning depth and time for game
    very_start = time.time()
    depth_white = 2
    depth_black = 3
    time_left_w = 300
    time_left_b = 300
    contact = False
    previous_moves = []
    
    white_camp = {(15, 15): 0, (14, 15): 0, (13, 15): 0, (12, 15): 0, (11, 15): 0, (15, 14): 0, (14, 14): 0, (13, 14): 0, (12, 14): 0, (11, 14): 0, (15, 13): 0, (14, 13): 0, (13, 13): 0, (12, 13): 0,(15, 12): 0, (14, 12): 0, (13, 12): 0, (15, 11): 0, (14, 11): 0}
    black_camp = {(0, 0): 0, (1, 0): 0, (2, 0): 0, (3, 0): 0, (4, 0): 0, (0, 1): 0, (1, 1): 0, (2, 1): 0, (3, 1): 0,(4, 1): 0, (0, 2): 0, (1, 2): 0, (2, 2): 0, (3, 2): 0, (0, 3): 0, (1, 3): 0, (2, 3): 0, (0, 4): 0,(1, 4): 0}


    Play_Game(white_black, value_board, depth_white, depth_black, time_left_w, time_left_b)
    Print_Statistics(depth_white, depth_black, very_start)

