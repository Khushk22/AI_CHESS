import chess
import chess.svg

# Initialize the chess board
board = chess.Board()

# Generate the chessboard image (SVG format)
svg_image = chess.svg.board(board)

# Save the image as an SVG file
with open("chessboard.svg", "w") as f:
    f.write(svg_image)

print("Chessboard SVG image has been generated.")
