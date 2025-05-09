
                if event.type == MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    col = mouse_x // self.cell_size
                    row = mouse_y // self.cell_size

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

            # Highlight valid moves if a piece is selected
            if selected_piece:
                moves = self.highlight_moves(selected_piece, selected_row, selected_col)
                for move in moves:
                    pygame.draw.rect(self.screen, (0, 255, 0), (move[1] * self.cell_size, move[0] * self.cell_size, self.cell_size, self.cell_size), 3)

            # Draw promotion popup if a pawn is being promoted
            if promoting_pawn:
                self.draw_promotion_popup(promotion_position, current_turn, white_pieces, black_pieces)

            # Update the display
            pygame.display.update()






 # Create a ChessBoard instance and run the game
if __name__ == "__main__":
    chess_board = ChessBoard(640, 640)

    chess_board.run()