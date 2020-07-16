# 2 or 3, stay alive
# exactly 3, become alive
import itertools

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


# A cell represents a square region whose side length is a power of two. This
# power is called its rank; so a rank 1 cell has side length 2, a rank 2 cell
# has side length 4, ..., & a rank-n cell has side length 2^n.
#
# Cells of rank 1 (2x2) are represented by integers.
#
# Cells of rank >2 are represented by objects of class Cell.
class Cell:
  __slots__ = ('nw', 'ne', 'sw', 'se', 'result')
  def __init__(self, nw, ne, sw, se):
    self.nw, self.ne, self.sw, self.se = nw, ne, sw, se
    self.result = None
  def __eq__(self, other): return self is other
  def __hash__(self): return id(self)
  def __repr__(self):
    return f"Cell({self.nw},{self.ne},{self.sw},{self.se})"
#    return "Cell({},{},{},{})" % (self.nw, self.ne, self.sw, self.se)

def get_rank(cell):
  if isinstance(cell, int): return 1
  assert isinstance(cell, Cell)
  return 1 + get_rank(cell.nw)

# Cell construction memoization table.
memo_table = {}

def cell(rank, nw, ne, sw, se):
  assert rank > 1
  assert rank-1 == get_rank(nw) == get_rank(ne) == get_rank(sw) == get_rank(se)
  if (nw, ne, sw, se) in memo_table:
    return memo_table[(nw, ne, sw, se)]
  x = memo_table[(nw, ne, sw, se)] = Cell(nw, ne, sw, se)
  return x

def to_board_iter(rank: int, cell: Cell):
  assert rank == get_rank(cell)
  if rank == 1:
    assert isinstance(cell, int)
    return [[cell>>0&1, cell>>1&1],
            [cell>>2&1, cell>>3&1]]
  nw, ne, sw, se = (to_board_iter(rank-1, cell.nw), to_board_iter(rank-1, cell.ne),
                    to_board_iter(rank-1, cell.sw), to_board_iter(rank-1, cell.se))
  return itertools.chain(map(itertools.chain, nw, ne),
                         map(itertools.chain, sw, se))

def to_board(rank: int, cell):
  return [list(line) for line in to_board_iter(rank, cell)]

def result(rank: int, cell: Cell):
  assert rank > 1
  assert isinstance(cell, Cell)
  if cell.result is not None:
    return cell.result
  
  nw, ne, sw, se = cell.nw, cell.ne, cell.sw, cell.se
  if rank == 2:
    # 4x4 cell; nw, ne, sw, se are all integers.
    # Just perform the simulation.
    assert False #TODO: implement
  else:
    # Run the hashlife algorithm.
    assert False #TODO: implement
  cell.result = result
  return result


# Examples
a1 = 0b0101
a2 = cell(2,a1,a1,a1,a1)
