from math import atan2
from copy import deepcopy

move_direction = [(1, 0), (1, 1), (0, 1), (-1,1),
              (-1, 0), (-1, -1), (0, -1), (1,-1),
              (2, 1), (1, 2), (-1, 2), (-2, 1),
              (-2, -1), (-1, -2), (1, -2), (2, -1),
              ]
RAYS = [atan2(direct[1],direct[0]) for direct in move_direction]

PIECES = {'k': lambda y, deltax, deltay: abs(deltax) <= 1 and abs(deltay) <= 1,
          'q': lambda y, deltax, deltay: deltax == 0 or deltay == 0 or abs(deltax) == abs(deltay),
          'n': lambda y, deltax, deltay: (abs(deltax) >= 1 and
                                  abs(deltay) >= 1 and
                                  abs(deltax) + abs(deltay) == 3),
          'b': lambda y, deltax, deltay: abs(deltax) == abs(deltay),
          'r': lambda y, deltax, deltay: deltax == 0 or deltay == 0,
          'p': lambda y, deltax, deltay: (y < 8 and abs(deltax) <= 1 and deltay == -1),
          'P': lambda y, deltax, deltay: (y > 1 and abs(deltax) <= 1 and deltay == 1),
          }

MOVES = dict()

for p, is_legal_move in PIECES.items():

    MOVES[p] = list()

    for x in range(64):

        MOVES[p].append([list() for _ in range(8)])

        for end in sorted(range(64), key=lambda n: abs(n - x)):

            y = 8 - x // 8
            dx = (end % 8) - (x % 8)
            dy = (8 - end // 8) - y

            if x == end or not is_legal_move(y, dx, dy):
                continue

            angle = atan2(dy, dx)
            if angle in RAYS:
                ray_num = RAYS.index(angle) % 8
                MOVES[p][x][ray_num].append(end)

        MOVES[p][x] = [r for r in MOVES[p][x] if r]

for p in ['K', 'Q', 'N', 'B', 'R']:
    MOVES[p] = deepcopy(MOVES[p.lower()])

MOVES['k'][4][0].append(6)
MOVES['k'][4][1].append(2)
MOVES['K'][60][0].append(62)
MOVES['K'][60][4].append(58)

x = 0
for i in range(8):
    MOVES['p'][8 + i][x].append(24 + i)
    MOVES['P'][55 - i][x].append(39 - i)
    x = 1
