import sys, random, argparse
from urllib.parse import non_hierarchical

def valid(board, dim_x, dim_y) -> bool:
    '''
    Validates board
    '''
    def validate_sqr_board(board) -> bool:
        '''
        Validate square boards
        '''
        n = len(board)
        sqr_n = n ** 0.5
        return sqr_n % 1 == 0
    def validate_rectangle_board(board, dim_x,dim_y) -> bool:
        '''
        Validate Rectangle boards
        '''
        n = len(board)
        return dim_y * dim_x == n
    for tile in board:
        if tile != '-' and tile != 'X':
            print(f'"{tile}" is invalid.')
            return False 
    if dim_y == dim_x == -1:        
        return validate_sqr_board(board)
    else:
        return validate_rectangle_board(board, dim_x,dim_y)

def pretty_print_board(board, dim_x, dim_y):
    '''
    Nice board output with emojis
    '''
    NUMBERS = ['⬛️','1️⃣ ','2️⃣ ','3️⃣ ','4️⃣ ','5️⃣ ','6️⃣ ','7️⃣ ','8️⃣ ']
    for y in range(dim_y):
        row = ''
        for x in range(dim_x):
            label = board[x + (y * dim_x)]
            if label == 'X':
                label = '💣'
            elif label == '-':
                label = '⬜️'
            elif label == 'F':
                label = '🚩'
            else:
                label = NUMBERS[label]
            row += f'{label}'
        print(row)
def create_labelled_board(board, dim_x, dim_y):
    '''
    creates an array of numbers and Xs for bombs.
    this is the solved minesweeper board
    '''
    def label_mine(x,y,board_index):
        for i in range(-1,2):
            for j in range(-1,2):
                if i == j == 0:
                    continue
                if i + x >= dim_x or i + x < 0:
                    #out of bounds
                    continue
                if j + y >= dim_y or j + y < 0:
                    continue
                label_index = (board_index + i) + (j * dim_x)
                curr_label = board[label_index]
                if curr_label == 'X':
                    continue
                if curr_label == '-':
                    board[label_index] = 1
                else:
                    board[label_index] +=1

    for board_index in range(dim_x * dim_y):
        x = board_index % dim_x
        y = int(board_index / dim_x)
        if board[board_index] == 'X':
            label_mine(x,y,board_index)
        elif board[board_index] == '-':
            board[board_index] = 0
    return board
    

def minesweeper(board, dim_x=-1, dim_y=-1):
    '''
    This is the function required from the challenge. 
    It takes an Array of strings (board), and optionally takes the dimensions x and y of the board.
    If no dimensions are provided, the board will be assumed as a square.

    Prints the solved board
    '''
    if not valid(board,dim_x,dim_y):
        print ('Invalid Board :(')
        return
    if dim_x == dim_y == -1:
        dim_x = dim_y = int(len(board)**0.5)
    labelled_board = create_labelled_board(board, dim_x,dim_y)
    pretty_print_board(labelled_board,dim_x,dim_y)

def generate_random_board(difficulty, dim_x, dim_y,curr_x,curr_y):
    '''
    Creates a random solved board.
    Difficulty options: EASY, HARD, (Any other string will be considered MEDIUM)
    Curr_x, Curr_y are required. These are the user's first coordinate guess.
    Guarantees user does not select the bomb on the first guess.
    If you must, you can set these to -1 to avoid this feature.
    '''
    curr_index = curr_x + (curr_y*dim_x)
    def difficulty_to_num(difficulty):
        '''
        converts the difficulty parameter to a number of bombs given the board size
        '''
        if difficulty == 'EASY':
            return int((3/25) * (dim_x * dim_y)) #3 in every 25 squares - stolen from example
        elif difficulty == 'HARD':
            return int((5/25) * dim_x * dim_y)
        else:
            return int((4/25) * dim_x * dim_y)
    def bomb_coords(num_bombs):
        '''
        generates unique bomb coords, excluding the user coords
        '''
        valid_bombs = []
        while(len(valid_bombs) < num_bombs):
            index = int(dim_x * dim_y * random.random())

            if index not in valid_bombs and index is not curr_index:
                valid_bombs.append(index)
        return valid_bombs
    bomb_coords = bomb_coords(difficulty_to_num(difficulty))
    blank_board = generate_blank_board(dim_x,dim_y)
    for bomb_coord in bomb_coords:
        blank_board[bomb_coord] = 'X'
    return create_labelled_board(blank_board,dim_x,dim_y)

def generate_blank_board(dim_x, dim_y):
    '''
    Generates empty board
    '''
    return ['-' for _ in range(dim_x * dim_y)]

def valid_flag(player_input,dim_x,dim_y):
    '''
    Checks if player flag input is valid
    '''
    split_input = player_input.split(' ')
    if not len(split_input) == 3:
        return False
    return valid_coord (player_input[2:],dim_x,dim_y)
    
def valid_coord(player_input,dim_x,dim_y):
    '''
    Checks if player coordinate input is valid
    '''
    split_input = player_input.split(' ')
    if not len(split_input) == 2:
        return False
    x , y = split_input
    if x.isdigit() and y.isdigit():
        x = int(x)
        y = int(y)
        if x < dim_x and x >= 0:
            if y < dim_y and y >= 0:
                return True

    return False

def apply_flag(x,y,output_board, dim_x,dim_y):
    '''
    Applies flag coordinate
    '''
    guess_index = x + (y * dim_x)
    if output_board[guess_index] == 'F':
        output_board[guess_index] = '-'
        print('Flag removed')
        return
    elif not output_board[guess_index] == '-':
        print("Can't place a flag here!")
        return
    else:
        output_board[guess_index] = 'F'
        return



def apply_no_bomb_guess(x,y,output_board,secret_board,dim_x,dim_y):
    '''
    Applies user's coordinate for safe spot. 
    If user selects a flag place, this input will be skipped.

    '''
    guess_index = x + (y * dim_x)
    if output_board[guess_index] == 'F':
        print("Flag placed there, be careful next time!")
        return output_board,False
    if secret_board[guess_index] == 'X':
        output_board[guess_index] = secret_board[guess_index]
        print('Game Over - You Lose')
        return output_board, True
    elif output_board[guess_index] == '-':
        def recursive_release_tiles(x,y):
            '''
            Checks if coord x y is 'revealable' (not a bomb)
            Checks if coord if coord should propogate to more revealed tiles
            '''
            guess_index = x + (y * dim_x)
            if output_board[guess_index] == '-':
                if not secret_board[guess_index] == 'X':
                    output_board[guess_index] = secret_board[guess_index]
                    if output_board[guess_index] == 0:
                        
                        if x + 1 < dim_x:
                            recursive_release_tiles(x+1,y)
                        if x -1 >= 0:
                            recursive_release_tiles(x-1,y)
                        if y + 1 < dim_y:
                            recursive_release_tiles(x,y+1)
                        if y - 1 >= 0:
                            recursive_release_tiles(x,y-1)
                        if y - 1 >= 0 and x - 1 >= 0:
                            recursive_release_tiles(x-1,y-1)

                        if y - 1 >= 0 and x + 1 < dim_x:
                            recursive_release_tiles(x+1,y-1)
                        if y+ 1 < dim_y and x - 1 >= 0:
                            recursive_release_tiles(x-1,y+1)
                        if y + 1 < dim_y and x + 1 < dim_x:
                            recursive_release_tiles(x+1,y+1)

        recursive_release_tiles(x,y)
    return output_board, False

def check_game_over(secret_board,output_board):
    '''
    Checks if board is solved
    '''
    for s , o in zip (secret_board,output_board):
        if s == 'X':
            continue
        if not s == o:
            return False
    print('You won!')
    return True

def play(difficulty = 'EASY', dim_x = 5, dim_y = 5):
    '''
    Runs the minesweeper game
    '''
    #generate bomb locations after user has selected first tile. This ensures user never selects a bomb first
    secret_board = None
    output_board = generate_blank_board(dim_x,dim_y)
    pretty_print_board(output_board,dim_x,dim_y)
    print(f'To enter coords: x(0 - {dim_x}) y(0 - {dim_y})')
    print(f'e.g. {int(random.random() * dim_x)} {int(random.random() * dim_y)}')
    print(f'To enter flag: f x y')
    print(f'e.g. f {int(random.random() * dim_x)} {int(random.random() * dim_y)}')
    print('Flags are toggle-able')
    game_over = False
    
    while(not game_over):

        player_input = input()
        if player_input[0] == 'f':
            #flag
            if not valid_flag(player_input,dim_x,dim_y):
                print('Invalid Input')
                continue
            _, x, y = player_input.split(' ')
            x = int(x)
            y = int(y)
            apply_flag(x,y,output_board,dim_x,dim_y)
        else:
            if not valid_coord(player_input,dim_x,dim_y):
                print('Invalid Input')
                continue
            x, y = player_input.split(' ')
            x = int(x)
            y = int(y)
            if secret_board is None:
                secret_board = generate_random_board(difficulty, dim_x, dim_y, x, y)

            #should make this better really
            output_board, game_over = apply_no_bomb_guess(x,y,output_board,secret_board,dim_x,dim_y)
        
        pretty_print_board(output_board,dim_x,dim_y)
        if not game_over:
            game_over = check_game_over(secret_board,output_board)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Minesweeper')
    parser.add_argument('-d, --difficulty', default='EASY',type=str,
                        help='Default: EASY. Difficulty setting. Options are EASY, MEDIUM, HARD. Invalid inputs will default to MEDIUM',dest = 'difficulty')
    parser.add_argument('-x','--x_size', default=8,type=int,
                        help='Default: 8. Width of the board',dest ='dim_x')
    parser.add_argument('-y','--y_size', default=8,type=int,
                        help='Default: 8. Height of the board',dest ='dim_y')
    parser.add_argument('-m','--minesweeper_example', action='store_true',
                        help='Does not play the game. Displays a solved minesweeper board. Include -b parameter to set board.',dest ='minesweeper')
    parser.add_argument('-b','--board', default=["-", "-", "-", "-", "-","-", "-", "-", "-", "-","X", "X", "-", "-", "-","-", "-", "-", "-", "-","-", "-", "-", "-", "X"],
                        nargs='+',
                        help='This parameter must be used with conjunction with the -m --minesweeper parameter. Sets the board to solve. Put each board tile as a space-seperated value. Either "-" or "X".',
                        dest ='board')
    
    args : argparse.Namespace = parser.parse_args()

    if args.minesweeper:
        print(f'''Running minesweeper({args.board})''')
        minesweeper(args.board)
    else:
        play(args.difficulty,args.dim_x,args.dim_y)
    
    

    