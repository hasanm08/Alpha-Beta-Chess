from collections import namedtuple

from board import Board
from moves import MOVES

State = namedtuple('State', ['player', 'rights', 'en_passant', 'ply', 'turn'])


class InvalidMove(Exception):
    pass


class Game(object):

    NORMAL = 0
    CHECK = 1
    CHECKMATE = 2
    STALEMATE = 3

    default_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    def __init__(self, fen=default_fen, validate=True):
        self.board = Board()
        self.state = State(' ', ' ', ' ', ' ', ' ')
        self.history = []
        self.fen_history = []
        self.validate = validate
        self.set_fen(fen=fen)

    def __str__(self):
        return ' '.join(str(x) for x in [self.board] + list(self.state))

    @staticmethod
    def indexToXY(pos_index):
        return chr(97 + pos_index % 8) + str(8 - pos_index // 8)

    @staticmethod
    def xyToIndex(pos_xy):
        return (8 - int(pos_xy[1])) * 8 + (ord(pos_xy[0]) - ord('a'))

    def get_fen(self):
        return ' '.join(str(x) for x in [self.board] + list(self.state))

    def set_fen(self, fen):
        self.fen_history.append(fen)
        state_arr = fen.split(' ')
        state_arr[4] = int(state_arr[4])
        state_arr[5] = int(state_arr[5])
        self.state = State(*state_arr[1:])
        self.board.setPosition(state_arr[0])

    def resetBoard(self, fen=default_fen):
        self.history = []
        self.fen_history = []
        self.set_fen(fen)

    def makeMove(self, move):
	
        state_arr = ['w', 'KQkq', '-', 0, 1]
        if move is None or move == '' or len(move) < 4:
            raise InvalidMove("\nIllegal move: {}\nfen: {}".format(move,
                                                                   str(self)))

        move = move.lower()

        start = Game.xyToIndex(move[:2])
        end = Game.xyToIndex(move[2:4])
        piece = self.board.getPiece(start)
        target = self.board.getPiece(end)

        if self.validate and move not in self.moves(index_list=[start]):
            raise InvalidMove("\nIllegal move: {}\nfen: {}".format(move,
                                                                   str(self)))

        state_arr[0] = {'w': 'b', 'b': 'w'}[self.state.player]

        rights = {0: 'q', 4: 'kq', 7: 'k',
                      56: 'Q', 60: 'KQ', 63: 'K'}
        void_set = ''.join([rights.get(start, ''),
                           rights.get(end, '')])
        new_rights = [r for r in self.state.rights if r not in void_set]
        state_arr[1] = ''.join(new_rights) or '-'

        if piece.lower() == 'p' and abs(start - end) == 16:
            state_arr[2] = Game.indexToXY((start + end) // 2)

        state_arr[3] = self.state.ply + 1
        if piece.lower() == 'p' or target.lower() != ' ':
            state_arr[3] = 0

        state_arr[4] = self.state.turn
        if self.state.player == 'b':
            state_arr[4] = self.state.turn + 1

        if len(move) == 5:
            piece = move[4]
            if self.state.player == 'w':
                piece = piece.upper()

        self.history.append(move)
        self.board.movePiece(start, end, piece)

        c_type = {62: 'K', 58: 'Q', 6: 'k', 2: 'q'}.get(end, None)
        if piece.lower() == 'k' and c_type and c_type in self.state.rights:
            coords = {'K': (63, 61), 'Q': (56, 59),
                      'k': (7, 5), 'q': (0, 3)}[c_type]
            r_piece = self.board.getPiece(coords[0])
            self.board.movePiece(coords[0], coords[1], r_piece)

        if piece.lower() == 'p' and self.state.en_passant != '-' \
                and Game.xyToIndex(self.state.en_passant) == end:
            ep_tgt = Game.xyToIndex(self.state.en_passant)
            if ep_tgt < 24:
                self.board.movePiece(end + 8, end + 8, ' ')
            elif ep_tgt > 32:
                self.board.movePiece(end - 8, end - 8, ' ')

        self.set_fen(' '.join(str(x) for x in [self.board] + list(state_arr)))

    def moves(self, player=None, index_list=range(64)):
        if not self.validate:
            return self._all_moves(player=player, index_list=index_list)

        if not player:
            player = self.state.player

        result = []
        test = Game(fen=str(self), validate=False)
        for move in self._all_moves(player=player, index_list=index_list):

            test.resetBoard(fen=str(self))

            king, opponent = {'w': ('K', 'b'), 'b': ('k', 'w')}.get(player)
            kingx = self.board.findPiece(king)
            king_location = Game.indexToXY(kingx)
            dx = abs(kingx - Game.xyToIndex(move[2:4]))

            if move[0:2] == king_location and dx == 2:

                opponent_move = set([m[2:4] for m in test.moves(player=opponent)])
                castle_move = {'e1g1': 'e1f1', 'e1c1': 'e1d1',
                              'e8g8': 'e8f8', 'e8c8': 'e8d8'}.get(move, '')

                if (king_location in opponent_move or castle_move and castle_move not in result):
                    continue
            test.makeMove(move)
            tgts = set([m[2:4] for m in test.moves()])

            if Game.indexToXY(test.board.findPiece(king)) not in tgts:
                result.append(move)

        return result

    def _all_moves(self, player=None, index_list=range(64)):
        player = player or self.state.player
        result = []
        for start in index_list:
            if self.board.getOwner(start) != player:
                continue
            piece = self.board.getPiece(start)
            rays = MOVES.get(piece, [''] * 64)

            for r in rays[start]:
                new_moves = self._trace(start, piece, r, player)
                result.extend(new_moves)

        return result

    def _trace(self, start, piece, ray, player):
        result = []

        for end in ray:

            sym = piece.lower()
            del_x = abs(end - start) % 8
            move = [Game.indexToXY(start) + Game.indexToXY(end)]
            tgt_owner = self.board.getOwner(end)

            if tgt_owner == player:
                break

            if sym == 'k' and del_x == 2:
                gap_owner = self.board.getOwner((start + end) // 2)
                out_owner = self.board.getOwner(end - 1)
                rights = {62: 'K', 58: 'Q', 6: 'k', 2: 'q'}.get(end, ' ')
                if (tgt_owner or gap_owner or rights not in self.state.rights or
                        (rights.lower() == 'q' and out_owner)):
                    break

            if sym == 'p':
                if del_x == 0 and tgt_owner:
                    break

                elif del_x != 0 and not tgt_owner:
                    ep_coords = self.state.en_passant
                    if ep_coords == '-' or end != Game.xyToIndex(ep_coords):
                        break

                if (end < 8 or end > 55):
                    move = [move[0] + s for s in ['b', 'n', 'r', 'q']]

            result.extend(move)

            if tgt_owner:
                break

        return result

    @property
    def status(self):

        king, opponent = {'w': ('K', 'b'), 'b': ('k', 'w')}.get(self.state.player)
        king_location = Game.indexToXY(self.board.findPiece(king))
        can_move = len(self.moves())
        is_exposed = [m[2:] for m in self._all_moves(player=opponent)
                      if m[2:] == king_location]

        status = Game.NORMAL
        if is_exposed:
            status = Game.CHECK
            if not can_move:
                status = Game.CHECKMATE
        elif not can_move:
            status = Game.STALEMATE

        return status
