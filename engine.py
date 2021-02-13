from game import Game
from node import Node
import time
import json
import random
from ai import AI


def readCache():
	with open("./cache.json", "r") as f:
		try:
			return json.load(f)
		except:
			return {}

cachedMoves= readCache()
class Engine:
	def __init__(self):
		self.game=Game()
		self.computer =AI(self.game)
	
	def cli(self):
		self.computer.printBoard(str(self.game))
		try:
			while self.game.status < 2:
				umove = input("\nMake a move: \033[91m ")
				while umove not in self.game.moves() and umove != "ff":
					umove = input("Please enter a valid move: ")
				if umove == "ff":
					break;
				self.game.makeMove(umove)
				captured = self.capPieces(str(self.game))
				start_time = time.time()
				
				self.computer.printBoard(str(self.game), captured)
				print("Wait...\n")
				if self.game.status < 2:
					cstate = str(self.game)
					ai_move = self.computer.doMove(cstate)
					PIECE_NAME = {'p': 'pawn', 'b': 'bishop', 'n': 'knight', 'r': 'rook', 'q': 'queen', 'k': 'king'}
					start = ai_move[:2]
					end = ai_move[2:4]
					piece = PIECE_NAME[self.game.board.getPiece(self.game.xyToIndex(ai_move[:2]))]
					captured_piece = self.game.board.getPiece(self.game.xyToIndex(ai_move[2:4]))
					if captured_piece != " ":
						captured_piece = PIECE_NAME[captured_piece.lower()]
					print("\033[1mNodes visited:\033[0m        \033[93m{}\033[0m".format(self.computer.numberOfVisitedNode))
					print("\033[1mNodes cached:\033[0m         \033[93m{}\033[0m".format(len(self.computer.cache)))
					print("\033[1mNodes found in cache:\033[0m \033[93m{}\033[0m".format(self.computer.nodeInCache))
					print("\033[1mElapsed time in sec:\033[0m  \033[93m{time}\033[0m".format(time=time.time() - start_time))
					self.game.makeMove(ai_move)
				captured = self.capPieces(str(self.game))
				self.computer.printBoard(str(self.game), captured)
			umove = print("Game over")
			with open("./cache.json", "w") as f:
				for key in self.computer.cache:
					cachedMoves[key] = self.computer.cache[key]
				json.dump(cachedMoves, f)
		except KeyboardInterrupt:
			with open("./cache.json", "w") as f:
				for key in self.computer.cache:
					cachedMoves[key] = self.computer.cache[key]
				json.dump(cachedMoves, f)

	def capPieces(self, board_state):
		pieces = {'P': 8, 'B': 2, 'N': 2, 'R': 2, 'Q': 1, 'K': 1, 'p': 8, 'b': 2, 'n': 2, 'r': 2, 'q': 1, 'k': 1}
		cap = {
			"w": [],
			"b": []
		}
		for char in board_state.split(' ')[0]:
			if char in pieces:
				pieces[char] -= 1
		for p in pieces:
			if pieces[p] > 0:
				if p.isupper():
					cap['w'] += pieces[p] * p
				else:
					cap['b'] += pieces[p] * p
			pieces[p] = 0
		return cap


if __name__ == '__main__':
	game = Engine()
	game.cli()