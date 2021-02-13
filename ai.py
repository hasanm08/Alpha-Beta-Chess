from node import Node
from game import Game
import json
import random


def readCache():
	with open("./cache.json", "r") as f:
		try:
			return json.load(f)
		except:
			return {}

cachedMoves= readCache()

class AI:
	def __init__(self,game):
		self.depth_max=4	
		self.game=game
		self.numberOfVisitedNode=0
		self.cache=cachedMoves
		self.nodeInCache = 0

	def printBoard(self, board_state, captured={"w": [], "b": []}):
		symbols = {
						'P': '♟',
						'B': '♝',
						'N': '♞',
						'R': '♜',
						'Q': '♛',
						'K': '♚',
						'p': '\033[36m\033[1m♙\033[0m',
						'b': '\033[36m\033[1m♗\033[0m',
						'n': '\033[36m\033[1m♘\033[0m',
						'r': '\033[36m\033[1m♖\033[0m',
						'q': '\033[36m\033[1m♕\033[0m',
						'k': '\033[36m\033[1m♔\033[0m'}

		states = board_state.split(' ')[0].split("/")
		board_str = "\n"
		w_captured = " ".join(symbols[p] for p in captured['w'])
		b_captured = " ".join(symbols[p] for p in captured['b'])
		for i, r in enumerate(states):
			board_str +='\033[93m'+str(8-i)+'\033[0m'
			for c in r:
				if c.isdigit():
					board_str += "\033[93m ♢\033[0m" * int(c)
				else:
					board_str += " " + symbols[c]
			if i == 0:
				board_str += "   Captured:" if len(w_captured) > 0 else ""
			if i == 1:
				board_str += "   " + w_captured
			if i == 6:
				board_str += "   Captured:" if len(b_captured) > 0 else ""
			if i == 7:
				board_str += "   " + b_captured
			board_str += "\n"
		board_str += "\033[93m  A B C D E F G H\033[0m"
		self.nodeInCache = 0
		self.numberOfVisitedNode = 0
		print(board_str)

	def moves(self,board_state=None):
		if board_state == None:
			board_state = str(self.game)
		possible = []
		for move in Game(board_state).moves():
			if (len(move) < 5 or move[4] == "q"):
				test = Game(board_state)
				test.makeMove(move)
				node = Node(str(test))
				node.algebraic_move = move
				possible.append(node)
		return possible

	def heuristic(self, board_state=None):
		if board_state == None:
			board_state = str(self.game)
		cachedata = board_state.split(" ")[0] + " " + board_state.split(" ")[1]
		if cachedata in self.cache:
			self.nodeInCache += 1
			return self.cache[cachedata]
		
		test = Game(board_state)
		total = 0
		
		#material
		b_points = 0
		board0 = board_state.split(' ')[0]
		piece_values = {'p': 1, 'b': 3, 'n': 3, 'r': 5, 'q': 9, 'k': 0}
		for p in board0:
			if p.islower():
				b_points += piece_values[p]
			elif p.isupper():
				b_points -= piece_values[p.lower()]
		total+=b_points * 100

		#in_check
		b_points = 0
		status = test.status
		turn = str(test).split(" ")[1]
		if turn == "w":
			if status == 1:
				b_points += 1
			elif status == 2:
				b_points += float("inf")
		else:
			if status == 1:
				b_points -= 1
			elif status == 2:
				b_points -= float("inf")
		total += b_points

		#pawn structure
		b_points = 0
		board, player = [segment for segment in board_state.split(' ')[:2]]
		board = board.split("/")
		board_state_arr = []
		for row in board:
			row_arr = []
			for char in row:
				if char.isdigit():
					for i in range(int(char)):
						row_arr.append(" ")
				else:
					row_arr.append(char)
			board_state_arr.append(row_arr)
		for i, row in enumerate(board_state_arr):
			for j in range(len(row)):
				if board_state_arr[i][j] == "p":
					tl = i-1, j-1
					tr = i-1, j+1
					if tl[0] >= 0 and tl[0] <= 7 and tl[1] >= 0 and tl[1] <= 7:
						if board_state_arr[tl[0]][tl[1]] == "p":
							b_points += 1
					if tr[0] >= 0 and tr[0] <= 7 and tr[1] >= 0 and tr[1] <= 7:
						if board_state_arr[tr[0]][tr[1]] == "p":
							b_points += 1
		total += b_points

		self.cache[cachedata] = total
		return total

	def doMove(self, board_state):
		possible = self.moves(board_state)
		alpha = float("-inf")
		beta = float("inf")
		best = possible[0]
		for move in possible:
			v = self.miniMax(move, alpha, beta, 1)
			if alpha < v:
				alpha = v
				best = move
				best.value = alpha
		return best.algebraic_move

	def miniMax(self, node, alpha, beta, depth=0):
		depth += 1
		if depth == self.depth_max:
			v = self.heuristic(node.board_state)
			if depth % 2 == 0:
				if (alpha < v):
					alpha = v
				self.numberOfVisitedNode += 1
				return alpha
			else:
				if (beta > v):
					beta = v
				self.numberOfVisitedNode += 1
				return beta
		if depth % 2 == 0:
			# min player's turn
			for child in self.moves(node.board_state):
				if alpha < beta:
					v = self.miniMax(child,alpha, beta, depth)
					if beta > v:
						beta = v
			return beta
		else:
			# max player's turn
			for child in self.moves(node.board_state):
				if alpha < beta:
					v = self.miniMax(child,alpha, beta, depth)
					if alpha < v:
						alpha = v
			return alpha
