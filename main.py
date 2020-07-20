# 2 or 3, stay alive
# exactly 3, become alive
import itertools

# Finds the next state of the sell at the coordinates (x,y).
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

# Steps a 4x4 board to a 2x2 board.
def step(board):
  next_board = [[0, 0], [0, 0]]
  for x in (1,2):
    for y in (1,2):
      next_board[x-1][y-1] = nextState(board, x, y)
  return next_board


# A cell represents a square region whose side length is a power of two. This
# power is called its rank; so a rank 1 cell has side length 2, a rank 2 cell
# has side length 4, ..., & a rank-n cell has side length 2^n.
#
# Cells of rank 1 (2x2) are represented by integers.
#
# Cells of rank >1 are represented by objects of class Cell.
class Cell:
  __slots__ = ('nw', 'ne', 'sw', 'se', 'result')
  def __init__(self, nw, ne, sw, se):
    self.nw, self.ne, self.sw, self.se = nw, ne, sw, se
    self.result = None
  def __eq__(self, other): return self is other
  def __hash__(self): return id(self)
  def __repr__(self):
    return f"Cell({self.nw},{self.ne},{self.sw},{self.se})"

def get_rank(cell):
  if isinstance(cell, int): return 1
  assert isinstance(cell, Cell)
  return 1 + get_rank(cell.nw)

def to_board(rank: int, cell):
  return [list(line) for line in to_board_iter(rank, cell)]

def to_board_iter(rank: int, cell: Cell):
  assert rank == get_rank(cell)
  if rank == 1:
    assert isinstance(cell, int)
    return [[cell>>0&1, cell>>1&1],
            [cell>>2&1, cell>>3&1]]
  nw, ne, sw, se = (to_board_iter(rank-1, cell.nw),
                    to_board_iter(rank-1, cell.ne),
                    to_board_iter(rank-1, cell.sw), 
                    to_board_iter(rank-1, cell.se))
  return itertools.chain(map(itertools.chain, nw, ne),
                         map(itertools.chain, sw, se))


# ----- CONSTRUCTING CELLS -----
memo_table = {}

def make_cell(rank, nw, ne, sw, se):
  assert rank > 1
  assert rank-1 == get_rank(nw) == get_rank(ne) == get_rank(sw) == get_rank(se)
  if (nw, ne, sw, se) in memo_table:
    return memo_table[(nw, ne, sw, se)]
  x = memo_table[(nw, ne, sw, se)] = Cell(nw, ne, sw, se)
  return x

def from_board(rank, board):
  assert rank > 0
  assert 1 << rank == len(board) == len(board[0])
  if rank == 1:
    return (board[0][0] | board[0][1]<<1 | board[1][0]<<2 | board[1][1]<<3)
  size = 1 << (rank-1)
  return make_cell(rank,
              from_board(rank-1, [line[:size] for line in board[:size]]),
              from_board(rank-1, [line[size:] for line in board[:size]]),
              from_board(rank-1, [line[:size] for line in board[size:]]),
              from_board(rank-1, [line[size:] for line in board[size:]])
  )


# ----- THE HASHLIFE ALGORITHM -----
def result(rank: int, cell: Cell):
  assert rank > 1
  assert isinstance(cell, Cell)
  if cell.result is not None:
    return cell.result
  
  nw, ne, sw, se = cell.nw, cell.ne, cell.sw, cell.se
  if rank == 2:
    # 4x4 cell; nw, ne, sw, se are all integers.
    # Just perform the simulation.
    board = to_board(2, cell)
    next_inner = step(board)
    res = from_board(1, next_inner)
  else:
    # Run the hashlife algorithm.
    # First make our overlapping nine quads.
    n = make_cell(rank-1, nw.ne, ne.nw, nw.se, ne.sw)
    w = make_cell(rank-1, nw.sw, nw.se, sw.nw, sw.ne)
    c = make_cell(rank-1, nw.se, ne.sw, sw.ne, se.nw)
    e = make_cell(rank-1, ne.sw, ne.se, se.nw, se.ne)
    s = make_cell(rank-1, sw.ne, se.nw, sw.se, se.sw)
    # Now find their results.
    nwr, nr, ner, wr, cr, er, swr, sr, ser = \
      [result(rank-1, cell) for cell in (nw, n, ne, w, c, e, sw, s, se)]
    # Now combine the results into four overlapping quads.
    nw = make_cell(rank-1, nwr, nr, wr, cr)
    ne = make_cell(rank-1, nr, ner, cr, er)
    sw = make_cell(rank-1, wr, cr, swr, sr)
    se = make_cell(rank-1, cr, er, sr, ser)
    # Combine the results of these four quads to get our final result.
    res = make_cell(rank-1, *(result(rank-1, cell) for cell in (nw, ne, sw, se)))
  cell.result = res
  return res


# ----- EXAMPLES -----
a1 = 0b0101
a2 = make_cell(2,a1,a1,a1,a1)
chess = [[(i+j)%2 for i in range(0,8)] for j in range(0,8)]
assert chess == to_board(3, from_board(3, chess))

# ----- Rank 2 works -----
# cell:
# 1010
# 1010
# 1010
# 1010
# result(2, cell)
# result:
#  01
#  01
assert 0b1010 == result(2, from_board(2, [[1, 0] * 2] * 4))

# ----- Rank 3 works -----
# cell:
# 10101010
# 10101010
# 10101010
# 10101010
# 10101010
# 10101010
# 10101010
# 10101010
#
# steps to:
#  010101
#  010101
#  010101
#  010101
#  010101
#  010101
#
# steps to result(3, cell):
#   1010
#   1010
#   1010
#   1010
assert ([[1,0] * 2] * 4 
  == to_board(2, result(3, from_board(3, [[1,0] * 4] * 8))))

# ----- Rank 3 All 1's goes to all 0's -----
assert ([[0] * 4] * 4
  == to_board(2, result(3, from_board(3, [[1] * 8] * 8))))

# ----- Rank 3 Glider -----
# 00000000
# 00000000
# 00000000
# 00000000
# 00011100
# 00010000
# 00001000
# 00000000

# steps to
#  000000
#  000000
#  000100
#  001100
#  001010
#  000000

# steps to result(3, cell):
#   0000
#   0110
#   0101
#   0100

rows = ([[0] * 8] * 4
        + [[0, 0, 0, 1, 1, 1, 0, 0],
           [0, 0, 0, 1, 0, 0, 0, 0],
           [0, 0, 0, 0, 1, 0, 0, 0]]
        + [[0] * 8])

expected = [
  [0, 0, 0, 0],
  [0, 1, 1, 0],
  [0, 1, 0, 1],
  [0, 1, 0, 0]]

assert (expected == to_board(2, result(3, from_board(3, rows))))

# ----- Rank 4 -----

blank_row = [0] * 16
test_board = [
  blank_row,
  blank_row,
  blank_row,
  blank_row,
  blank_row,
  blank_row,
  [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
  blank_row,
  blank_row,
  blank_row,
  blank_row,
  blank_row,
  blank_row,
  blank_row,
  ]

blank_row_8 = [0] * 8
expected_board = [
  blank_row_8,
  [0, 0, 1, 0, 1, 0, 0, 0],
  [0, 1, 0, 0, 1, 0, 0, 0],
  [0, 1, 0, 0, 1, 0, 0, 0],
  [0, 0, 1, 1, 0, 0, 0, 0],
  blank_row_8,
  blank_row_8,
  blank_row_8,
  ]

assert (expected_board == to_board(3, result(4, from_board(4, test_board))))