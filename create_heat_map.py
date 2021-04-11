
import argparse
import logging

import chess.pgn
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import nltk
import numpy as np

# To suppress errors while reading the pgn
logging.getLogger("chess.pgn").setLevel(logging.CRITICAL)


def get_pieces_by_move_count(game):

	"""
	Takes a game and spits out how many total moves were played for each piece
	"""

	pieces = ['N', 'Q', 'K', 'B', 'R']
	final_counts = {}
	
	for piece in pieces:
		count = 0
		
		move = game.next()
		while move:
			move_san = move.san()
			if move_san[0] == piece:
				count += 1
			move = move.next()
		
		final_counts[piece] = count
		
	return final_counts


def get_piece_squares(game, piece_abbrev):
	
	"""
	Takes a game and a piece to spit out what
	non-starting squares piece travelled/touched.
	"""
	squares = []
	
	move = game.next()
	while move:
		move_san = move.san()
		if move_san[0] == piece_abbrev:
			possible_square = move_san[-2:]
			if '+' in possible_square or '#' in possible_square:
				possible_square = move_san[-3:-1]
			squares.append(possible_square)
		move = move.next()
	
	return squares

def get_piece_move_heat_map(list_of_games, piece_abbrev):
	
	"""
	Takes a list of games and a piece
	and spits out a frequency distribution
	of touched squares.
	"""
	
	piece_squares_list = []
	
	for game in list_of_games:
		try:
			squares = get_piece_squares(game, piece_abbrev)
			piece_squares_list.extend(squares)
		except ValueError:
			continue
	
	freq_dist = nltk.FreqDist(piece_squares_list)
	return freq_dist.most_common()

def numpyize_heat_map(heat_map_freq):
	
	"""
	Make a numpy array from the frequency distribution
	to ultimately represent like a chess board.
	"""

	board = np.zeros([8, 8])
	
	for square_freq in heat_map_freq:
		square = square_freq[0]
		
		num_x = 8 - int(square[1])
		num_y = ord(square[0]) - 97
		
		board[num_x][num_y] = square_freq[1]
	
	return board

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("pgnfile")
	args = parser.parse_args()
	
	pgn_file = args.pgnfile
	
	# Read the games into memory
	games = []

	with open(pgn_file) as pgn:
		game = chess.pgn.read_game(pgn)
		while game:
			games.append(game)
			game = chess.pgn.read_game(pgn)

	print(games[-1])

	# For each piece that's not a pawn, create heat map and save to a file
	for piece in ['K', 'Q', 'N', 'B', 'R']:
		piece_move_heat_map = get_piece_move_heat_map(games, piece)
		X = numpyize_heat_map(piece_move_heat_map)

		fig, ax = plt.subplots()
		i = ax.imshow(X, cmap=cm.jet, interpolation='nearest')
		
		ax.set_xticks([0,1,2,3,4,5,6,7])
		ax.set_xticklabels(['a','b','c','d','e','f','g','h'])
		
		ax.set_yticks([0,1,2,3,4,5,6,7])
		ax.set_yticklabels([8,7,6,5,4,3,2,1])
		
		fig.colorbar(i)
		
		plt.title(label=piece, size='24', c='black')
		plt.savefig(f'{piece}.png')

if __name__ == "__main__":
	main()

