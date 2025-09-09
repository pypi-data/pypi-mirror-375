
import argparse
from . import generate, play_puzzle

def main():
	parser = argparse.ArgumentParser(description="Play a Hashiwokakero puzzle.")
	parser.add_argument('--width', type=int, default=5, help='Puzzle width (default: 5)')
	parser.add_argument('--height', type=int, default=5, help='Puzzle height (default: 5)')
	parser.add_argument('--difficulty', type=int, default=40, help='Puzzle difficulty (default: 40)')
	args = parser.parse_args()

	puzzle = generate(args.width, args.height, args.difficulty)
	play_puzzle(puzzle)

if __name__ == "__main__":
	main()
