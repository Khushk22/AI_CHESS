def draw_pieces():
    # Draw the pieces on the board based on the state of the chessboard
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            square = chess.square(col, row)  # Get the square's index
            piece = board.piece_at(square)   # Get the piece at the square
            if piece:
                piece_image = pieces.get(piece.symbol())  # Get the image based on piece symbol
                piece_rect = piece_image.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                screen.blit(piece_image, piece_rect)  # Draw the piece image at the correct position
