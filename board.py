import pygame
from pygame.locals import *
import sys
from pieces import PieceManager


pygame.init()

class ChessBoard:
    
    def __init__(self, width, height):
        # Set up the display
        self.LIGHT_COLOR = (255, 255, 255)  # White color for light squares
        self.DARK_COLOR = (125, 135, 150)
        self.screen = pygame.display.set_mode((width, height))
        self.width = width
        self.height = height
        self.cell_size = width // 8  # Assuming an 8x8 grid

        self.start_time_white = pygame.time.get_ticks()  
        self.start_time_black = pygame.time.get_ticks() 
        self.elapsed_time_white = 0
        self.elapsed_time_black = 0
        self.time_limit = 60000  
        self.is_white_turn = True 
        # Define colors
        self.WHITE = (115, 149, 82)
        self.BLACK = (235, 236, 208)

        # Track the board state: 2D array for piece positions (None for empty squares)
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = 'white'  # Start with white's turn


        # Initialize the PieceManager
        self.piece_manager = PieceManager(self.cell_size)

        # Initialize starting positions for pieces
        self.setup_pieces()

        # Track selected piece and position
        self.selected_piece = None
        self.selected_position = None

        #promotion vaaste
        self.promotion_piece = None
        self.promoting_pawn_position = None
        self.promotion_options = ['queen', 'bishop', 'rook', 'knight']

    def setup_pieces(self):
        """Set up initial piece positions on the board."""
        for i in range(8):
            self.board[1][i] = ('pawn', 'black')  # Black pawns
            self.board[6][i] = ('pawn', 'white')  # White pawns

        # Setup other pieces for black
        self.board[0][0] = self.board[0][7] = ('rook', 'black')
        self.board[0][1] = self.board[0][6] = ('knight', 'black')
        self.board[0][2] = self.board[0][5] = ('bishop', 'black')
        self.board[0][3] = ('queen', 'black')
        self.board[0][4] = ('king', 'black')

        # Setup other pieces for white
        self.board[7][0] = self.board[7][7] = ('rook', 'white')
        self.board[7][1] = self.board[7][6] = ('knight', 'white')
        self.board[7][2] = self.board[7][5] = ('bishop', 'white')
        self.board[7][3] = ('queen', 'white')
        self.board[7][4] = ('king', 'white')


    def draw_timer(self):
        """Draw the timers for both players."""
        font = pygame.font.SysFont(None, 36)

        # Calculate remaining time for each player
        time_remaining_white = max(0, self.time_limit - self.elapsed_time_white) // 1000
        time_remaining_black = max(0, self.time_limit - self.elapsed_time_black) // 1000

        # Render timers
        white_timer_text = font.render(f'White Time: {time_remaining_white}s', True, (255, 0, 0))
        black_timer_text = font.render(f'Black Time: {time_remaining_black}s', True, (255, 0, 0))

        # Draw timers at the top of the screen
        self.screen.blit(white_timer_text, (10, 590))
        self.screen.blit(black_timer_text, (10, 20))

    def switch_turn(self):
        """Switch the turn between players."""
        if self.is_white_turn:
            # Switch from White to Black
            self.elapsed_time_white += pygame.time.get_ticks() - self.start_time_white
            self.start_time_black = pygame.time.get_ticks()
        else:
            # Switch from Black to White
            self.elapsed_time_black += pygame.time.get_ticks() - self.start_time_black
            self.start_time_white = pygame.time.get_ticks()

        self.is_white_turn = not self.is_white_turn  # Toggle turn


    def highlight_moves(self, piece, row, col):
        """Calculate valid moves for the selected piece."""
        piece_type, piece_color = piece
        moves = []

        # Pawn movement logic
        if piece_type == 'pawn':
            direction = -1 if piece_color == 'white' else 1  # White moves up, black moves down
            start_row = 6 if piece_color == 'white' else 1
            new_row = row + direction

            # Move forward one square
            if 0 <= new_row < 8 and self.board[new_row][col] is None:
                moves.append((new_row, col))

            # Move forward two squares from starting position
            if row == start_row and self.board[new_row][col] is None:
                new_row_two = row + 2 * direction
                if 0 <= new_row_two < 8 and self.board[new_row_two][col] is None:
                    moves.append((new_row_two, col))

            # Capture diagonally
            for dx in [-1, 1]:
                if 0 <= new_row < 8 and 0 <= col + dx < 8:
                    target = self.board[new_row][col + dx]
                    if target and target[1] != piece_color:
                        moves.append((new_row, col + dx))

        # Knight movement logic
        elif piece_type == 'knight':
            knight_moves = [
                (2, 1), (2, -1), (-2, 1), (-2, -1),  # Two squares horizontally
                (1, 2), (1, -2), (-1, 2), (-1, -2)   # Two squares vertically
            ]
            for dx, dy in knight_moves:
                new_row, new_col = row + dx, col + dy
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if self.board[new_row][new_col] is None or self.board[new_row][new_col][1] != piece_color:
                        moves.append((new_row, new_col))


        # Rook movement logic
        elif piece_type == 'rook':
            for d in [-1, 1]:  # Check both directions
                for step in range(1, 8):  # Move up to 7 squares
                    new_row = row + d * step
                    if 0 <= new_row < 8:
                        if self.board[new_row][col] is None:
                            moves.append((new_row, col))  # Empty square
                        else:
                            if self.board[new_row][col][1] != piece_color:
                                moves.append((new_row, col))  # Capture
                            break  # Blocked by another piece
                    else:
                        break  # Out of bounds

            for d in [-1, 1]:  # Check left and right
                for step in range(1, 8):  # Move up to 7 squares
                    new_col = col + d * step
                    if 0 <= new_col < 8:
                        if self.board[row][new_col] is None:
                            moves.append((row, new_col))  # Empty square
                        else:
                            if self.board[row][new_col][1] != piece_color:
                                moves.append((row, new_col))  # Capture
                            break  # Blocked by another piece
                    else:
                        break  # Out of bounds

        # Bishop movement logic
        elif piece_type == 'bishop':
            for d in [-1, 1]:  # Check diagonals
                for step in range(1, 8):
                    new_row = row + d * step
                    new_col = col + d * step
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        if self.board[new_row][new_col] is None:
                            moves.append((new_row, new_col))  # Empty square
                        else:
                            if self.board[new_row][new_col][1] != piece_color:
                                moves.append((new_row, new_col))  # Capture
                            break  # Blocked by another piece
                    else:
                        break  # Out of bounds

            for d in [-1, 1]:  # Check the other diagonal
                for step in range(1, 8):
                    new_row = row + d * step
                    new_col = col - d * step
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        if self.board[new_row][new_col] is None:
                            moves.append((new_row, new_col))  # Empty square
                        else:
                            if self.board[new_row][new_col][1] != piece_color:
                                moves.append((new_row, new_col))  # Capture
                            break  # Blocked by another piece
                    else:
                        break  # Out of bounds

        # Queen movement logic (combines rook and bishop)
        elif piece_type == 'queen':
            # Use rook logic
            for d in [-1, 1]:  # Check vertical
                for step in range(1, 8):
                    new_row = row + d * step
                    if 0 <= new_row < 8:
                        if self.board[new_row][col] is None:
                            moves.append((new_row, col))  # Empty square
                        else:
                            if self.board[new_row][col][1] != piece_color:
                                moves.append((new_row, col))  # Capture
                            break  # Blocked by another piece
                    else:
                        break  # Out of bounds

            for d in [-1, 1]:  # Check horizontal
                for step in range(1, 8):
                    new_col = col + d * step
                    if 0 <= new_col < 8:
                        if self.board[row][new_col] is None:
                            moves.append((row, new_col))  # Empty square
                        else:
                            if self.board[row][new_col][1] != piece_color:
                                moves.append((row, new_col))  # Capture
                            break  # Blocked by another piece
                    else:
                        break  # Out of bounds

            # Use bishop logic
            for d in [-1, 1]:  # Check diagonal
                for step in range(1, 8):
                    new_row = row + d * step
                    new_col = col + d * step
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        if self.board[new_row][new_col] is None:
                            moves.append((new_row, new_col))  # Empty square
                        else:
                            if self.board[new_row][new_col][1] != piece_color:
                                moves.append((new_row, new_col))  # Capture
                            break  # Blocked by another piece
                    else:
                        break  # Out of bounds

            for d in [-1, 1]:  # Check the other diagonal
                for step in range(1, 8):
                    new_row = row + d * step
                    new_col = col - d * step
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        if self.board[new_row][new_col] is None:
                            moves.append((new_row, new_col))  # Empty square
                        else:
                            if self.board[new_row][new_col][1] != piece_color:
                                moves.append((new_row, new_col))  # Capture
                            break  # Blocked by another piece
                    else:
                        break  # Out of bounds

        # King movement logic
        elif piece_type == 'king':
            king_moves = [
                (1, 0), (-1, 0), (0, 1), (0, -1),
                (1, 1), (1, -1), (-1, 1), (-1, -1)
            ]
            for dx, dy in king_moves:
                new_row, new_col = row + dx, col + dy
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if self.board[new_row][new_col] is None or self.board[new_row][new_col][1] != piece_color:
                        moves.append((new_row, new_col))

        return moves

         # Add check for pawn promotion
        if piece[0] == 'pawn' and ((piece[1] == 'white' and row == 0) or (piece[1] == 'black' and row == 7)):
            self.promoting_pawn_position = (row, col)
            return []  # Temporarily disable normal moves for the pawn

        return moves  # Continue with other moves


    def find_king(self, color):
        """Find the position of the king for the specified color."""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece[0] == 'king' and piece[1] == color:
                    return (row, col)  # Return the position of the king as a tuple (row, col)
        return None  # Return None if the king is not found

    
    
    def draw_board(self):
        """Draw the chess board and pieces."""
        # Iterate over the board and draw each piece
        for row in range(8):
            for col in range(8):
                # Alternate colors for the board squares
                if (row + col) % 2 == 0:
                    color = self.LIGHT_COLOR  # Define this color somewhere in your class
                else:
                    color = self.DARK_COLOR  # Define this color somewhere in your class
                
                pygame.draw.rect(self.screen, color, (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size))

                # Draw the pieces
                # Highlight the square if it's a valid move
                if self.selected_position and (row, col) in self.highlight_moves(self.selected_piece, *self.selected_position):
                    pygame.draw.rect(self.screen, (0, 255, 0, 128),
                                     (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size))

                # Draw pieces on the board

                piece = self.board[row][col]
                if piece:
                    piece_type, piece_color = piece
                    self.piece_manager.draw_piece(self.screen, piece_type, piece_color, col, row)


    def draw_promotion_popup(self, promotion_position, current_turn, white_pieces, black_pieces):
        """Draws a promotion popup for white and black pawns, positioning options and handling clicks."""
        row, col = promotion_position
        cell_size = self.cell_size
        popup_piece_size = int(cell_size * 0.8)  # Size of the piece images
        padding = int(cell_size * 0.1)  # Padding

        # Determine the pieces available for promotion based on the current turn
        pieces = white_pieces if current_turn == 'white' else black_pieces

        # Store the positions of the promotion options
        self.promotion_option_rects = []

        # Adjust position based on the current turn
        if current_turn == 'white':
            start_row = row + 1  # Place options below the promotion row
            if start_row + 4 > 7:  # Ensure it stays within the board bounds
                start_row = 7 - 4  # Adjust to fit options
        else:
            start_row = row - 4  # Place options above the promotion row
            if start_row < 0:  # Adjust if it goes out of bounds
                start_row = 0

        # Draw the promotion options on different blocks (cells)
        for i, piece_image in enumerate(pieces):
            option_row = start_row + i
            popup_x = col * cell_size + padding  # X position (same for all pieces in this column)
            popup_y = option_row * cell_size + padding  # Y position (adjusted by row for each piece)

            # Draw the piece option in the popup
            self.screen.blit(pygame.transform.scale(piece_image, (popup_piece_size, popup_piece_size)), (popup_x, popup_y))

            # Store the position (rect) for each promotion option for click detection
            rect = pygame.Rect(popup_x, popup_y, popup_piece_size, popup_piece_size)
            self.promotion_option_rects.append(rect)

    def is_in_promotion_popup(self, mouse_x, mouse_y, promotion_position, current_turn):
        """Check if the mouse is within the bounds of the promotion popup."""
        row, col = promotion_position
        tile_size = self.cell_size

        if current_turn == 'white':
            popup_x = col * tile_size + tile_size // 2  # Center the popup relative to the column
            popup_y = (row + 1) * tile_size  # Position for white dropdown
        else:
            popup_x = col * tile_size + tile_size // 2  # Center the popup relative to the column
            popup_y = (row - 4) * tile_size  # Position for black dropup
        
        popup_width = tile_size
        popup_height = tile_size * 4  # Space for 4 pieces

        return popup_x <= mouse_x < popup_x + popup_width and popup_y <= mouse_y < popup_y + popup_height

    def handle_promotion_selection(self, mouse_x, mouse_y, promotion_position, current_turn):
        """Handle the promotion piece selection based on mouse click."""
        tile_size = self.cell_size

        # Adjust index based on current turn
        if current_turn == 'white':
            index = (mouse_y - ((promotion_position[0] + 1) * tile_size)) // tile_size
        else:
            index = (mouse_y - ((promotion_position[0] - 4) * tile_size)) // tile_size

        if 0 <= index < 4:  # Ensure the index is within the valid range
            if current_turn == 'white':
                return ('queen', 'white') if index == 0 else ('rook', 'white') if index == 1 else ('knight', 'white') if index == 2 else ('bishop', 'white')
            else:
                return ('queen', 'black') if index == 0 else ('rook', 'black') if index == 1 else ('knight', 'black') if index == 2 else ('bishop', 'black')
        return None  # Return None if index is out of bounds

    def is_king_in_check(self, color):
        """Check if the king of the specified color is in check."""
        # Find the king's position
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece[0] == 'king' and piece[1] == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        # Check for threats from opponent's pieces
        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece[1] == opponent_color:
                    moves = self.highlight_moves(piece, row, col)  # Get potential moves for opponent piece
                    if king_pos in moves:  # If any opponent piece can move to the king's position
                        return True  # The king is in check

        return False  # The king is safe

    def is_checkmate(self, color):
        """Check if the given player is in checkmate."""
        # Check if the king is in check
        if not self.is_king_in_check(color):
            return False  # The king is not in check, no checkmate

        # Try every possible move for the current player
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece[1] == color:  # Only look at the current player's pieces
                    valid_moves = self.highlight_moves(piece, row, col)
                    for move in valid_moves:
                        new_row, new_col = move

                        # Simulate the move
                        previous_piece = self.board[new_row][new_col]
                        self.board[new_row][new_col] = piece
                        self.board[row][col] = None

                        # Check if the king is still in check after the move
                        if not self.is_king_in_check(color):
                            # Revert the move and return False (no checkmate)
                            self.board[row][col] = piece
                            self.board[new_row][new_col] = previous_piece
                            return False

                        # Revert the move
                        self.board[row][col] = piece
                        self.board[new_row][new_col] = previous_piece

        return True  # No valid moves left and the king is in check


    def display_game_over(self, winner):
        """Display 'Game Over' message."""
        font = pygame.font.SysFont(None, 48)
        text = font.render(f"Checkmate! {winner} wins!", True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)
        pygame.display.update()

        # Pause for 3 seconds to allow the player to see the message
        pygame.time.wait(3000)

        # Exit the game
        pygame.quit()
        sys.exit()

    def is_stalemate(self, color):
        """Check if the player with the specified color is in stalemate."""
        # If the king is in check, it's not a stalemate
        if self.is_king_in_check(color):
            return False

        # Check if any piece of the current player can make a legal move
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece[1] == color:  # Current player's piece
                    # Check all valid moves for the piece
                    moves = self.highlight_moves(piece, row, col)
                    for move in moves:
                        # Simulate the move
                        target_row, target_col = move
                        previous_piece = self.board[target_row][target_col]  # Remember the target piece
                        self.board[target_row][target_col] = piece  # Move the piece
                        self.board[row][col] = None  # Remove it from the original position

                        # Check if the king is still safe after the move
                        if not self.is_king_in_check(color):
                            # Revert the move and return False (not stalemate)
                            self.board[row][col] = piece
                            self.board[target_row][target_col] = previous_piece
                            return False  # A legal move exists

                        # Revert the move
                        self.board[row][col] = piece
                        self.board[target_row][target_col] = previous_piece

        return True  # No legal moves available, and the king is not in check


    def display_message(self, text):
        """Display a message on the screen."""
        font = pygame.font.Font(None, 74)  # You can customize the font and size here
        message = font.render(text, True, (255, 0, 0))  # Render the text in red color
        text_rect = message.get_rect(center=(self.screen.get_width() / 2, self.screen.get_height() / 2))
        self.screen.blit(message, text_rect)
        pygame.display.update()  # Update the display to show the text


    def run(self):
        """Main game loop."""
        selected_piece = None
        selected_row = None
        selected_col = None
        current_turn = 'white'  # White starts first
        promoting_pawn = False
        promotion_position = None

        game_over = False  # Track if the game is over


        # Load images for promotion options for both white and black
        white_pieces = [
            pygame.image.load('images/white_queen.png'), 
            pygame.image.load('images/white_rook.png'), 
            pygame.image.load('images/white_knight.png'), 
            pygame.image.load('images/white_bishop.png')
        ]
        black_pieces = [
            pygame.image.load('images/black_queen.png'), 
            pygame.image.load('images/black_rook.png'), 
            pygame.image.load('images/black_knight.png'), 
            pygame.image.load('images/black_bishop.png')
        ]

        while True:

            if self.is_white_turn:
                self.elapsed_time_white = pygame.time.get_ticks() - self.start_time_white
            else:
                self.elapsed_time_black = pygame.time.get_ticks() - self.start_time_black

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()


                if game_over:
                    continue  # Skip input if the game is over


                if event.type == MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    col = mouse_x // self.cell_size
                    row = mouse_y // self.cell_size

                    self.switch_turn()


                    # Handle pawn promotion selection
                    if promoting_pawn:
                        if self.is_in_promotion_popup(mouse_x, mouse_y, promotion_position, current_turn):
                            promoted_piece = self.handle_promotion_selection(mouse_x, mouse_y, promotion_position, current_turn)
                            if promoted_piece:
                                # Replace the pawn with the promoted piece
                                self.board[promotion_position[0]][promotion_position[1]] = promoted_piece
                                promoting_pawn = False  # Reset promotion state
                                current_turn = 'black' if current_turn == 'white' else 'white'  # Switch turn
                        continue  # Skip other logic if promoting

                    # If a piece is already selected
                    if selected_piece is not None:
                        # Store the current state before the move
                        previous_piece = self.board[selected_row][selected_col]
                        previous_target = self.board[row][col]

                        if (row, col) in self.highlight_moves(selected_piece, selected_row, selected_col):  # Move piece
                            # Move the piece
                            self.board[row][col] = selected_piece  # Place the piece in the new position
                            self.board[selected_row][selected_col] = None  # Remove it from the old position

                            # Check for pawn promotion
                            if selected_piece[0] == 'pawn' and (row == 0 or row == 7):
                                promoting_pawn = True
                                promotion_position = (row, col)
                                selected_piece = None  # Deselect to handle promotion properly

                            # Check if the king is in check
                            if self.is_king_in_check(current_turn):
                                # Revert the move if the king is in check
                                self.board[selected_row][selected_col] = previous_piece
                                self.board[row][col] = previous_target
                                # Display a message (optional)
                                print(f"{current_turn} is in check! Move reverted.")
                            else:

                                # Check for checkmate after a valid move
                                opponent = 'black' if current_turn == 'white' else 'white'
                                if self.is_checkmate(opponent):
                                    self.display_game_over(current_turn)  # Display game over message and exit


                                # Switch turn after a move if not in promotion
                                if not promoting_pawn:
                                    selected_piece = None  # Clear the selection after move
                                    current_turn = 'black' if current_turn == 'white' else 'white'


                                    # Check for checkmate
                                    if self.is_king_in_check(current_turn):
                                        if self.is_checkmate(current_turn):
                                            print(f"Checkmate! {current_turn} loses. Game Over!")
                                            game_over = True
                                            self.display_message("Checkmate!")
                                    else:
                                        # Check for stalemate
                                        if self.is_stalemate(current_turn):
                                            print("Stalemate! The game is a draw. Game Over!")
                                            game_over = True
                                            self.display_message("Game Draw!")  # Display the message
                        else:
                                # Deselect the piece if the click is not a valid move
                                selected_piece = None  # Deselect if it's not a valid move

                    # If no piece is selected, try to select a piece
                    else:
                        piece = self.board[row][col]
                        if piece and piece[1] == current_turn:  # Check if it's the current player's piece
                            selected_piece = piece
                            selected_row, selected_col = row, col

            # Fill the screen with white color
            self.screen.fill(self.WHITE)

            # Draw the chess board
            self.draw_board()
            self.draw_timer()

            # Highlight valid moves if a piece is selected
            if selected_piece:
                moves = self.highlight_moves(selected_piece, selected_row, selected_col)
                for move in moves:
                    pygame.draw.rect(self.screen, (0, 255, 0), (move[1] * self.cell_size, move[0] * self.cell_size, self.cell_size, self.cell_size), 3)

            # Draw promotion popup if a pawn is being promoted
            if promoting_pawn:
                self.draw_promotion_popup(promotion_position, current_turn, white_pieces, black_pieces)

            # Highlight valid moves if a piece is selected
            if selected_piece:
                moves = self.highlight_moves(selected_piece, selected_row, selected_col)
                for move in moves:
                    pygame.draw.rect(self.screen, (0, 255, 0), (move[1] * self.cell_size, move[0] * self.cell_size, self.cell_size, self.cell_size), 3)

            # Draw the king square in red if in check
            if self.is_king_in_check(current_turn):
                king_pos = self.find_king(current_turn)
                if king_pos:
                    pygame.draw.rect(self.screen, (255, 0, 0), (king_pos[1] * self.cell_size, king_pos[0] * self.cell_size, self.cell_size, self.cell_size), 3)

            # Draw promotion popup if a pawn is being promoted
            if promoting_pawn:
                self.draw_promotion_popup(promotion_position, current_turn, white_pieces, black_pieces)

            # Update the display
            pygame.display.update()








 # Create a ChessBoard instance and run the game
if __name__ == "__main__":
    chess_board = ChessBoard(640, 640)

    chess_board.run()

            
