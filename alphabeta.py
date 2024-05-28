# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import filedialog
import numpy as np
import time
from tkinter import Tk, Frame, Label, StringVar, Canvas, Scrollbar

# Board initialization
# 0: empty, 1: cross, 2: circle, 3: points can be placed
board = np.array([[0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 3, 0, 0, 0],
                  [0, 0, 0, 1, 2, 3, 0, 0],
                  [0, 0, 3, 2, 1, 0, 0, 0],
                  [0, 0, 0, 3, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]])
initBoard = board.copy()
# Board weight
weight = np.array([[-3,  9, -1, -1, -1, -1,  9, -3],
                   [ 9,  9, -2, -2, -2, -2,  9,  9],
                   [-1, -2, -2, -2, -2, -2, -2, -1],
                   [-1, -2, -2, -3, -3, -2, -2, -1],
                   [-1, -2, -2, -3, -3, -2, -2, -1],
                   [-1, -2, -2, -2, -2, -2, -2, -1],
                   [ 9,  9, -2, -2, -2, -2,  9,  9],
                   [-3,  9, -1, -1, -1, -1,  9, -3]])
initweight = weight.copy()
# Record moves & hands & positions & notes
boardRecord = [board.copy()]
whoRecord = [2]
nowPos = 0
notelist = [''] * 64
gameover = 0
# 0: close, 1: cross, 2: circle
aiturn = 0
start_time = 0
end_time = 0
wcount = 0
bcount = 0
total_time = 0

def heuristic(board):
    # Defining positional weights to guide AI's strategic placements
    weights = [
        [ 20, -10,  5,  5,  5,  5, -10,  20],
        [-10, -20, -1, -1, -1, -1, -20, -10],
        [  5,  -1, -2, -2, -2, -2,  -1,   5],
        [  5,  -1, -2,  0,  0, -2,  -1,   5],
        [  5,  -1, -2,  0,  0, -2,  -1,   5],
        [  5,  -1, -2, -2, -2, -2,  -1,   5],
        [-10, -20, -1, -1, -1, -1, -20, -10],
        [ 20, -10,  5,  5,  5,  5, -10,  20]
    ]

    # Scores will reflect AI's goal to have fewer pieces with positionally strategic penalties
    my_score = 0
    opponent_score = 0
    for i in range(8):
        for j in range(8):
            if board[i][j] == 1:  # Assuming '1' is AI's color
                my_score += weights[i][j]
            elif board[i][j] == 2:  # Assuming '2' is the opponent's color
                opponent_score += weights[i][j]

    # Since the goal is to have fewer pieces, we subtract the weighted score of AI from the opponent's
    return opponent_score - my_score


def is_game_over(board):
    for i in range(8):
        for j in range(8):
            if board[i][j] == 3:
                return False
    return True

# Scan the board to draw
def render():
    global board, notelist, nowPos
    gameBox.delete("all")
    for i in range(1, 8):
        gameBox.create_line(60*i, 0, 60*i, 480, width=2, fill='black')
        gameBox.create_line(0, 60*i, 480, 60*i, width=2, fill='black')
    for i in range(8):
        for j in range(8):
            if board[i][j] == 0:    # empty
                gameBox.create_oval(i*60+5, j*60+5, i*60+55, j*60+55, fill='white', outline='white')
            elif board[i][j] == 1:  # cross
                gameBox.create_line(i*60+5, j*60+5, i*60+55, j*60+55, fill='#0000ff', width=5)
                gameBox.create_line(i*60+5, j*60+55, i*60+55, j*60+5, fill='#0000ff', width=5)
            elif board[i][j] == 2:   # circle
                gameBox.create_oval(i*60+5, j*60+5, i*60+55, j*60+55, fill='', outline='#ff0000', width=5)
            elif board[i][j] == 3:  # points can be placed
                gameBox.create_rectangle(i*60+5, j*60+5, i*60+55, j*60+55, fill='', outline='yellow', width=5)
    # Waiting for idle time to run, will not directly block what is being executed.
    gameBox.update_idletasks()
    # hand
    pos['text'] = str(nowPos)

# Detect the position of the mouse on the board
def mouseCatch(event):
    global board, whoRecord, boardRecord, nowPos, aiturn, whoturn, final_x, final_y, gameover, weight, total_time
    mx = int(event.x/60)
    my = int(event.y/60)
    if aiturn != whoturn and gameover == 0:
        if board[mx][my] == 3:
            if whoturn == 1:
                step = f"Move {nowPos+1} : X ({mx}, {my})\n"
                writeNote(step)
                print(str(nowPos) + " X " + str((mx, my)))
            else:
                step = f"Move {nowPos+1} : O ({mx}, {my})\t"
                writeNote(step)
                print(str(nowPos) + " O " + str((mx, my)))

            if nowPos < (len(whoRecord)-1):
                del boardRecord[nowPos+1:]
                del whoRecord[nowPos+1:]
            nowboard = board.copy()
            whoturn, chesscount, gameover = reversi(nowboard, mx, my, whoturn)
            weightChange(final_x, final_y, 1)
            nowPos += 1
            
            board = nowboard.copy()
            boardRecord.append(board)
            whoRecord.append(whoturn)
            render()
            numHint()
    if aiturn == whoturn:
        if aiturn != 0 and nowPos+1 == len(whoRecord) and aiturn == whoturn:
            while whoturn == aiturn and gameover == 0:
                numHint()
                start_time = time.time()
                runAI()
                end_time = time.time()
                total_time = total_time + (end_time - start_time)
                AItime['text'] = str("{:1.10f}".format(end_time - start_time))
                Totaltime['text'] = str("{:1.10f}".format(total_time))
                if whoturn == 1:
                    step = f"Move {nowPos+1} : X ({ final_x}, {final_y})\n"
                    writeNote(step)
                    print(str(nowPos) + " X " + str((final_x, final_y)))
                else:
                    step = f"Move {nowPos+1} : O ({ final_x}, {final_y})\t"
                    writeNote(step)
                    print(str(nowPos) + " O " + str((final_x, final_y)))
                nowboard = board.copy()
                whoturn, chesscount, gameover = reversi(nowboard, final_x, final_y, whoturn)
                weightChange(final_x, final_y, 0)
                nowPos += 1
                
                board = nowboard.copy()
                boardRecord.append(board)
                whoRecord.append(whoturn)
                render()
                numHint()

# Change weight
def weightChange(x, y, who):
    global weight
    # When the AI ??goes down to the corner, it adjusts the weights of the two adjacent rows of edges.
    if x == 0 and y == 0:
        weight[x+1][y+1] = 9
        for i in range(1,7):
            weight[x+i][y] = 10-i
            weight[x][y+i] = 10-i
    elif x == 7 and y == 0:
        weight[x-1][y+1] = 9
        for i in range(1,7):
            weight[x-i][y] = 10-i
            weight[x][y+i] = 10-i
    elif x == 7 and y == 7:
        weight[x-1][y-1] = 9
        for i in range(1,7):
            weight[x-i][y] = 10-i
            weight[x][y-i] = 10-i
    elif x == 0 and y == 7:
        weight[x+1][y-1] = 9
        for i in range(1,7):
            weight[x+i][y] = 10-i
            weight[x][y-i] = 10-i

# AI
tmp_x, tmp_y, final_x, final_y, tmp_chesscount, final_min = -1, -1, -1, -1, -1, 100
def alpha_beta(whoturn, board, depth, alpha, beta, is_maximizing_player):
    # if depth == 0 or is_game_over(board):
    #     return heuristic(board)

    # if is_maximizing_player:
    #     value = float('inf')
    #     for i in range(8):
    #         for j in range(8):
    #             if board[i][j] == 3:
    #                 aiboard = board.copy()
    #                 _, _, _ = reversi(aiboard, i, j, whoturn)
    #                 value = min(value, alpha_beta(whoturn, aiboard, depth - 1, alpha, beta, False))
    #                 alpha = min(alpha, value)
    #                 if alpha <= beta:
    #                     break
    #     return value
    # else:
    #     value = float('-inf')
    #     for i in range(8):
    #         for j in range(8):
    #             if board[i][j] == 3:
    #                 aiboard = board.copy()
    #                 _, _, _ = reversi(aiboard, i, j, whoturn)
    #                 value = max(value, alpha_beta(whoturn, aiboard, depth - 1, alpha, beta, True))
    #                 beta = max(beta, value)
    #                 if beta <= alpha:
    #                     break
    #     return value
    
    # change the upper code to the new rule that less pieces is better
    if depth == 0 or is_game_over(board):
        return heuristic(board)
    
    if is_maximizing_player:
        value = float('-inf')
        for i in range(8):
            for j in range(8):
                if board[i][j] == 3:
                    aiboard = board.copy()
                    _, _, _ = reversi(aiboard, i, j, whoturn)
                    value = max(value, alpha_beta(whoturn, aiboard, depth - 1, alpha, beta, False))
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break
        return value
    else:
        value = float('inf')
        for i in range(8):
            for j in range(8):
                if board[i][j] == 3:
                    aiboard = board.copy()
                    _, _, _ = reversi(aiboard, i, j, whoturn)
                    value = min(value, alpha_beta(whoturn, aiboard, depth - 1, alpha, beta, True))
                    beta = min(beta, value)
                    if beta <= alpha:
                        break
        return value



def myAI(whoturn, board, total, weight):
    best_move = (-1, -1)
    best_score = float('-inf')
    for i in range(8):
        for j in range(8):
            if board[i][j] == 3:
                print(f"Evaluating move at ({i}, {j})")
                aiboard = board.copy()
                _, _, _ = reversi(aiboard, i, j, whoturn)
                score = alpha_beta(whoturn, aiboard, 5, float('-inf'), float('inf'), True)
                print(f"Score for move ({i}, {j}): {score}")
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
    print(f"Best move selected: {best_move} with score {best_score}")
    global final_x, final_y
    final_x, final_y = best_move
    return best_move


def reversi(nowboard, mx, my, whoturn):
    global board, boardRecord, whoRecord, wcount, bcount
    gameover = 0
    # Circle makes a move and changes hands
    if whoturn == 2:
        nowboard[mx][my] = 2
        chesscount = turnOver(nowboard, mx, my, 2)
        whoturn = 1
    # Cross makes a move and changes hands
    else:
        nowboard[mx][my] = 1
        chesscount = turnOver(nowboard, mx, my, 1)
        whoturn = 2
    # Calculate whether there are points to be placed.If not, change hands and recalculate the points to be placed. If there are no more points, the gameover will occur.
    permit = 0
    for i in range(8):
        for j in range(8):
            if nowboard[i][j] == 3:
                nowboard[i][j] = 0
            if nowboard[i][j] == 0:
                tryboard = nowboard.copy()
                turnOver(tryboard, i, j, whoturn)
                if (tryboard != nowboard).any():
                    permit = 1
                    nowboard[i][j] = 3
    if permit == 0:
        if whoturn == 2:
            step = f"Move {nowPos+1} : O Pass\n"
            writeNote(step)
            print(str(nowPos) + " O pass")
            whoturn = 1
        else:
            step = f"Move {nowPos+1} : X Pass\n"
            writeNote(step)
            print(str(nowPos) + " X pass")
            whoturn = 2
        for i in range(8):
            for j in range(8):
                if nowboard[i][j] == 3:
                    nowboard[i][j] = 0
                if nowboard[i][j] == 0:
                    tryboard = nowboard.copy()
                    turnOver(tryboard, i, j, whoturn)
                    if (tryboard != nowboard).any():
                        permit = 1
                        nowboard[i][j] = 3
    if permit == 0 :
        if wcount < bcount:
            step = f"Move {nowPos+1} : X win\n"
            writeNote(step)
            print(str(nowPos) + " X win")
        elif wcount > bcount:
            step = f"Move {nowPos+1} : O win\n"
            writeNote(step)
            print(str(nowPos) + " O win")
        else:
            step = f"Move {nowPos+1} : Draw\n"
            writeNote(step)
            print(str(nowPos) + " Draw")
        gameover = 1

    # print(chesscount)
    return whoturn, chesscount, gameover

total = 4
# Display the number of chess pieces on the board & player prompts
def numHint():
    global total, whoturn, board, wcount, bcount
    whitenum = 0
    blacknum = 0
    for i in range(8):
        for j in range(8):
            if board[i][j] == 1:
                whitenum += 1
            elif board[i][j] == 2:
                blacknum += 1
    total = whitenum + blacknum
    wcount = whitenum
    bcount = blacknum
    wnum['text'] = str(whitenum)
    bnum['text'] = str(blacknum)
    if whoturn == 1:
        wnum['relief'] = "solid"
        bnum['relief'] = "flat"
    elif whoturn == 2:
        bnum['relief'] = "solid"
        wnum['relief'] = "flat"

# Bring in new points => Flip according to Othello rules
def turnOver(nowboard, mx, my, whoturn):
    chesscount = 0
    # Search up
    for i in range(my-1, -1, -1):
        if nowboard[mx][i] == 0 or nowboard[mx][i] == 3:
            break
        if nowboard[mx][i] == whoturn:
            for j in range(my-1, i, -1):
                nowboard[mx][j] = whoturn
                chesscount += 1
            break
    # Search right
    for i in range(mx+1, 8):
        if nowboard[i][my] == 0 or nowboard[i][my] == 3:
            break
        if nowboard[i][my] == whoturn:
            for j in range(mx+1, i):
                nowboard[j][my] = whoturn
                chesscount += 1
            break
    # Search down
    for i in range(my+1, 8):
        if nowboard[mx][i] == 0 or nowboard[mx][i] == 3:
            break
        if nowboard[mx][i] == whoturn:
            for j in range(my+1, i):
                nowboard[mx][j] = whoturn
                chesscount += 1
            break
    # Search left
    for i in range(mx-1, -1, -1):
        if nowboard[i][my] == 0 or nowboard[i][my] == 3:
            break
        if nowboard[i][my] == whoturn:
            for j in range(mx-1, i, -1):
                nowboard[j][my] = whoturn
                chesscount += 1
            break
    # Search to the upper right
    for i in range(1, 8):
        if (mx+i) <= 7 and (my-i) >= 0:
            if nowboard[mx+i][my-i] == 0 or nowboard[mx+i][my-i] == 3:
                break
            if nowboard[mx+i][my-i] == whoturn:
                for j in range(1, i):
                    nowboard[mx+j][my-j] = whoturn
                    chesscount += 1
                break
    # Search to the lower right
    for i in range(1, 8):
        if (mx+i) <= 7 and (my+i) <= 7:
            if nowboard[mx+i][my+i] == 0 or nowboard[mx+i][my+i] == 3:
                break
            if nowboard[mx+i][my+i] == whoturn:
                for j in range(1, i):
                    nowboard[mx+j][my+j] = whoturn
                    chesscount += 1
                break
    # Search to the lower left
    for i in range(1, 8):
        if (mx-i) >= 0 and (my+i) <= 7:
            if nowboard[mx-i][my+i] == 0 or nowboard[mx-i][my+i] == 3:
                break
            if nowboard[mx-i][my+i] == whoturn:
                for j in range(1, i):
                    nowboard[mx-j][my+j] = whoturn
                    chesscount += 1
                break
    # Search to the upper left
    for i in range(1, 8):
        if (mx-i) >= 0 and (my-i) >= 0:
            if nowboard[mx-i][my-i] == 0 or nowboard[mx-i][my-i] == 3:
                break
            if nowboard[mx-i][my-i] == whoturn:
                for j in range(1, i):
                    nowboard[mx-j][my-j] = whoturn
                    chesscount += 1
                break

    return chesscount


def runAI():
    global tmp_x, tmp_y, final_x, final_y, tmp_chesscount, final_min, board, whoturn, aiturn, total, weight
    tmp_x, tmp_y, final_x, final_y, tmp_chesscount, final_min = -1, -1, -1, -1, -1, 100
    myAI(whoturn, board, total, weight)

# Open a new game
def restart():
    global board, boardRecord, whoRecord, initBoard, whoturn, nowPos, aiturn, total, gameover, weight, initweight, final_x, final_y, notelist
    total = 0
    gameover = 0
    notelist = [''] * 64
    note_text.set('')
    board = initBoard.copy()
    weight = initweight.copy()
    del boardRecord[1:]
    del whoRecord[1:]
    whoturn = 0
    nowPos = 0
    aiturn = 0
    render()
    numHint()
    player['relief'] = RAISED
    player['state'] = NORMAL
    ai['relief'] = RAISED
    ai['state'] = NORMAL
    AItime['text'] = str(0)
    Totaltime['text'] = str(0)

# Change mode
def switchMode(mode):
    global whoturn, aiturn, board, nowPos, total, final_x, final_y, total_time
    # Player mode
    if mode == 0:
        whoturn = 1
        player['relief'] = SUNKEN
        player['state'] = DISABLED
        ai['relief'] = RAISED
        ai['state'] = DISABLED
        aiturn = 2
    # AI mode
    else:
        whoturn = 1
        ai['relief'] = SUNKEN
        ai['state'] = DISABLED
        player['relief'] = RAISED
        player['state'] = DISABLED
        aiturn = whoturn
        start_time = time.time()
        runAI()
        end_time = time.time()
        total_time = total_time + (end_time - start_time)
        AItime['text'] = str("{:1.10f}".format(end_time - start_time))
        Totaltime['text'] = str("{:1.10f}".format(total_time))
        if whoturn == 1:
            step = f"Move {nowPos+1} : X ({ final_x}, {final_y})\n"
            writeNote(step)
            print(str(nowPos) + " X " + str((final_x, final_y)))
        else:
            step = f"Move {nowPos+1} : O ({ final_x}, {final_y})\t"
            writeNote(step)
            print(str(nowPos) + " O " + str((final_x, final_y)))
        nowboard = board.copy()
        whoturn, chesscount, g = reversi(nowboard, final_x, final_y, whoturn)
        nowPos += 1
        board = nowboard.copy()
        render()
        numHint()
        boardRecord.append(board)
        whoRecord.append(whoturn)

def writeNote(step):
    global notelist, nowPos, note_text
    notation = step
    notelist[nowPos] = notation
    note_content = "".join(notelist)
    note_text.set(note_content)

def update_scrollregion(event=None):
    canvas.update_idletasks()
    bbox = canvas.bbox("all")
    canvas.config(scrollregion=bbox)

root = Tk()
root.state("zoomed")
root.resizable(False, False)

window_width = root.winfo_screenwidth()
window_height = root.winfo_screenheight()
myframe = Frame(root, bg='black', padx=2, pady=2)
myframe.place(x=(window_width - 480) // 2, y=(window_height - 480) // 2)
mysize = 480
gameBox = Canvas(myframe, width=mysize, height=mysize, bg='white')
gameBox.pack()
for i in range(1,8):
    gameBox.create_line(60*i, 0, 60*i, mysize+2, width=2, fill='black')
    gameBox.create_line(0, 60*i, mysize+2, 60*i, width=2, fill='black')

# Mode
restart = Button(root, text="Restart", width=12, height=1, bg='#55ee55', font=('Arial', 20), command=restart)
restart.place(x=(window_width - 480) // 2 + 600, y=(window_height - 480) // 2 + 50)
player = Button(root, text="You First", width=12, height=1, bg='red', fg='white', font=('Arial', 20), command=lambda:switchMode(0))
player.place(x=(window_width - 480) // 2 + 600, y=(window_height - 480) // 2 + 200)
ai = Button(root, text="AI First",  width=12, height=1, bg='blue', fg='white', font=('Arial', 20), command=lambda:switchMode(1))
ai.place(x=(window_width - 480) // 2 + 600, y=(window_height - 480) // 2 + 250)
hand = Label(root, text='      Move', font=('Arial', 40))
hand.place(x=(window_width - 480) // 2 + 600, y=(window_height - 480) // 2 + 400)

# Ratio & Move
wnum = Label(root, text="2", borderwidth=3, fg='blue', font=('Arial', 50))
wnum.place(x=(window_width - 480) // 2 + 600, y=(window_height - 480) // 2 - 50)
ver = Label(root, text=':', font=('Arial', 50))
ver.place(x=(window_width - 480) // 2 + 700, y=(window_height - 480) // 2 - 50)
bnum = Label(root, text="2", borderwidth=3, fg='red', font=('Arial', 50))
bnum.place(x=(window_width - 480) // 2 + 780, y=(window_height - 480) // 2 - 50)
pos = Label(root, text='0', font=('Arial', 40))
pos.place(x=(window_width - 480) // 2 + 600, y=(window_height - 480) // 2 + 400)

# Calculate AI time
aititle = Label(root, text='AI Time', font=('Arial', 30))
aititle.place(x=(window_width - 480) // 2 - 25, y=(window_height - 480) // 2 - 150)
AItime = Label(root, text="0", width=12, borderwidth=3, bg='black', fg='white', font=('Arial', 30))
AItime.place(x=(window_width - 480) // 2 - 100, y=(window_height - 480) // 2 - 100)
totaltitle = Label(root, text='Total Time', font=('Arial', 30))
totaltitle.place(x=(window_width - 480) // 2 + 350, y=(window_height - 480) // 2 - 150)
Totaltime = Label(root, text="0", width=12, borderwidth=3, bg='black', fg='white', font=('Arial', 30))
Totaltime.place(x=(window_width - 480) // 2 + 300, y=(window_height - 480) // 2 - 100)

# Note positions & pass
notelabel = Label(root, text="Note", font=('Arial', 50, 'bold'))
notelabel.place(x=(window_width - 480) // 2 - 340, y=(window_height - 480) // 2 - 50)
note_frame = Frame(root)
note_frame.place(x=(window_width - 480) // 2 - 470, y=(window_height - 480) // 2 + 50)
canvas = Canvas(note_frame, bg="#dddddd", width=420, height=400, scrollregion=(0, 0, 1000, 1000))
scrollbar = Scrollbar(note_frame, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
note_text = StringVar()
note_text_widget = Label(scrollable_frame, bg="#dddddd", textvariable=note_text, font=('Arial', 18))
note_text_widget.pack()
note_text.trace_add("write", lambda *args: update_scrollregion())
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

render()
whoturn = 0
numHint()
gameBox.bind("<Button-1>", mouseCatch)

root.mainloop()