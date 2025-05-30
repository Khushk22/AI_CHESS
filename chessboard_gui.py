import pygame
import chess
import random

# Initialize pygame
pygame.init()

# Constants
BOARD_SIZE = 8
SQUARE_SIZE = 60
WIDTH = HEIGHT = SQUARE_SIZE * BOARD_SIZE
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
LIGHT_SQUARE = (222, 184, 135)
DARK_SQUARE = (139, 69, 19)
HIGHLIGHT_COLOR = (0, 255, 0)
HINT_COLOR = (0, 0, 255)
ERROR_COLOR = (255, 0, 0)
PROMOTION_OPTIONS = ["q", "r", "b", "n"]
PROMOTION_FONT_SIZE = 48

# Difficulty modes
MODES = ["easy", "medium", "hard"]
selected_mode_index = 0  # Default to easy mode

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Load the images for the pieces
pieces = {
    "p": pygame.image.load("images/pawn.png"),
    "r": pygame.image.load("images/rook.png"),
    "n": pygame.image.load("images/knight.png"),
    "b": pygame.image.load("images/bishop.png"),
    "q": pygame.image.load("images/queen.png"),
    "k": pygame.image.load("images/king.png"),
    "P": pygame.image.load("images/pawn_white.png"),
    "R": pygame.image.load("images/rook_white.png"),
    "N": pygame.image.load("images/knight_white.png"),
    "B": pygame.image.load("images/bishop_white.png"),
    "Q": pygame.image.load("images/queen_white.png"),
    "K": pygame.image.load("images/king_white.png"),
}

# Initialize the chess board
board = chess.Board()

# Stack to store board states for undo functionality
move_stack = []

# Clock for managing frame rate and timing
clock = pygame.time.Clock()

# State flags
game_started = False
selected_square = None
invalid_move = False
ai_thinking = False
ai_move_time = 0
promotion_pending = False
promotion_move = None
mode = "easy"  # Default mode

def draw_board():
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces():
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            square = chess.square(col, row)
            piece = board.piece_at(square)
            if piece:
                symbol = piece.symbol()
                piece_image = pieces.get(symbol)
                if piece_image:
                    piece_rect = piece_image.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                    screen.blit(piece_image, piece_rect)

def highlight_square(square, color):
    row, col = divmod(square, 8)
    pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

def show_hints(selected_square):
    legal_moves = list(board.legal_moves)
    for move in legal_moves:
        if move.from_square == selected_square:
            highlight_square(move.to_square, HINT_COLOR)

def show_text(text, size, color, pos):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

def get_winner():
    if board.is_checkmate():
        return "You Win!" if board.turn == chess.BLACK else "AI Wins!"
    elif board.is_stalemate():
        return "Draw: Stalemate!"
    elif board.is_insufficient_material():
        return "Draw: Insufficient Material!"
    elif board.can_claim_threefold_repetition():
        return "Draw: Threefold Repetition!"
    elif board.can_claim_fifty_moves():
        return "Draw: Fifty-Move Rule!"
    return "Game Over!"

def undo_move():
    if move_stack:
        previous_fen = move_stack.pop()
        board.set_fen(previous_fen)

def handle_pawn_promotion(move):
    global promotion_pending, promotion_move
    piece = board.piece_at(move.from_square)
    if piece and piece.piece_type == chess.PAWN:
        if chess.square_rank(move.to_square) in (0, 7):
            promotion_pending = True
            promotion_move = move

def ai_move_easy():
    legal_moves = list(board.legal_moves)
    return random.choice(legal_moves)

def evaluate_board(board):
    """Simple evaluation function that returns a score based on material count."""
    material_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 1000,  # King is considered as the most valuable piece for end game
    }

    evaluation = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_value = material_values.get(piece.piece_type, 0)
            if piece.color == chess.WHITE:
                evaluation -= piece_value
            else:
                evaluation += piece_value
    return evaluation

def ai_move_medium():
    legal_moves = list(board.legal_moves)
    best_move = None
    best_score = -float('inf')
    for move in legal_moves:
        board.push(move)
        score = evaluate_board(board)
        if score > best_score:
            best_score = score
            best_move = move
        board.pop()
    return best_move

def minimax(board, depth, maximizing_player, alpha, beta):
    """Minimax algorithm with alpha-beta pruning."""
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)

    if maximizing_player:
        max_eval = -float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth-1, False, alpha, beta)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth-1, True, alpha, beta)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def ai_move_hard():
    legal_moves = list(board.legal_moves)
    best_move = None
    best_score = -float('inf')
    
    for move in legal_moves:
        board.push(move)
        score = minimax(board, 3, False, -float('inf'), float('inf'))  # Depth 3 is usually a good balance for hard mode
        if score > best_score:
            best_score = score
            best_move = move
        board.pop()
    
    return best_move

def ai_move_based_on_mode():
    legal_moves = list(board.legal_moves)
    
    if mode == "easy":
        return ai_move_easy()  # Easy mode with random move
    elif mode == "medium":
        return ai_move_medium()  # Medium mode with material-based evaluation
    elif mode == "hard":
        return ai_move_hard()  # Hard mode with minimax search

def main():
    global game_started, selected_square, invalid_move, ai_thinking, ai_move_time, promotion_pending, promotion_move, mode, selected_mode_index

    running = True

    while running:
        screen.fill((0, 0, 0))
        draw_board()
        draw_pieces()

        if not game_started:
            # Show instructions to choose mode with up/down keys
            show_text("Select Mode: Use UP/DOWN arrow keys to choose Easy, Medium, or Hard.", 17, WHITE_COLOR, (WIDTH // 8, HEIGHT // 3))
            show_text("Then, click anywhere to start.", 24, WHITE_COLOR, (WIDTH // 4, HEIGHT // 2))
            show_text(f"Current mode: {MODES[selected_mode_index].capitalize()}", 28, WHITE_COLOR, (WIDTH // 3, HEIGHT // 2 + 40))
        else:
            if board.is_game_over():
                result = get_winner()
                show_text(result, 36, WHITE_COLOR, (WIDTH // 4, HEIGHT // 2 - 40))
                show_text("Press 'R' to restart or 'E' to exit.", 24, WHITE_COLOR, (WIDTH // 5, HEIGHT // 2 + 10))
            elif ai_thinking:
                show_text("AI is thinking...", 24, WHITE_COLOR, (WIDTH // 3, HEIGHT // 2 + 40))
            elif promotion_pending:
                show_text("Select promotion piece.", 24, WHITE_COLOR, (WIDTH // 3, HEIGHT // 2 + 10))
            else:
                show_text("Your turn!", 24, WHITE_COLOR, (WIDTH // 3, HEIGHT // 2 + 40))

        if selected_square is not None and game_started and not board.is_game_over() and not promotion_pending:
            highlight_square(selected_square, HIGHLIGHT_COLOR)
            show_hints(selected_square)

        if invalid_move:
            show_text("Invalid move!", 28, ERROR_COLOR, (WIDTH // 3, HEIGHT - 40))
            invalid_move = False

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_started:
                    game_started = True
                    continue

                if board.is_game_over():
                    continue

                mouse_pos = pygame.mouse.get_pos()
                col = mouse_pos[0] // SQUARE_SIZE
                row = mouse_pos[1] // SQUARE_SIZE
                square = chess.square(col, row)

                if promotion_pending:
                    board.push(chess.Move(promotion_move.from_square, promotion_move.to_square, promotion=chess.QUEEN))
                    promotion_pending = False
                    continue

                if selected_square is None:
                    piece = board.piece_at(square)
                    if piece and piece.color == chess.WHITE:
                        selected_square = square
                else:
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        move_stack.append(board.fen())
                        board.push(move)
                        handle_pawn_promotion(move)
                        selected_square = None
                        ai_thinking = True
                        ai_move_time = pygame.time.get_ticks() + 2000
                    else:
                        invalid_move = True
                        selected_square = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_mode_index = (selected_mode_index - 1) % len(MODES)
                elif event.key == pygame.K_DOWN:
                    selected_mode_index = (selected_mode_index + 1) % len(MODES)

                if event.key == pygame.K_u:
                    undo_move()
                elif event.key == pygame.K_r:
                    board.reset()
                    move_stack.clear()
                    game_started = False
                elif event.key == pygame.K_e and board.is_game_over():
                    running = False

        if ai_thinking and pygame.time.get_ticks() >= ai_move_time:
            legal_moves = list(board.legal_moves)
            if legal_moves:
                ai_move = ai_move_based_on_mode()
                move_stack.append(board.fen())
                board.push(ai_move)
                ai_thinking = False
            else:
                ai_thinking = False

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
