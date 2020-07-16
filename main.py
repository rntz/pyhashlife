# 2 or 3, stay alive
# exactly 3, become alive

board = [
[0, 1, 0, 0],
[0, 0, 1, 1],
[0, 1, 0, 0],
[0, 0, 1, 0]
]

def nextState(board, x, y):
  lifecounter = 0
  for i in (-1, 0, 1):
    for j in (-1, 0, 1):
      if i == j == 0: continue
      if board[x+i][y+j] == 1:
        lifecounter += 1
  current_state = board[x][y]
  next_state = 1 if (lifecounter == 3 or (lifecounter == 2 and current_state)) else 0
  return next_state

def hashLife(board):
  next_board = [[0, 0], [0, 0]]
  for x in (1,2):
    for y in (1,2):
      next_board[x-1][y-1] = nextState(board, x, y)
  return next_board