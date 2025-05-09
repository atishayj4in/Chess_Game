import pygame

class PieceManager:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.piece_images = self.load_piece_images()
        # Define separate scaling factors for white and black pieces
        self.scale_factors = {
            'white': {
                'pawn': 0.9,
                'rook': 0.9,
                'knight': 0.9,
                'bishop': 0.9,
                'queen': 0.9,
                'king': 0.9
            },
            'black': {
                'pawn': 0.9,
                'rook': 0.9,
                'knight': 0.9,
                'bishop': 0.9,
                'queen': 0.9,
                'king': 0.9
            }
        }

    def load_piece_images(self):
        """Load and store images for all chess pieces."""
        piece_images = {}
        piece_colors = ['white', 'black']
        piece_names = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
        
        for color in piece_colors:
            for piece in piece_names:
                try:
                    piece_images[f"{color}_{piece}"] = pygame.image.load(f"images/{color}_{piece}.png").convert_alpha()

                except pygame.error as e:
                    print(f"Error loading image for {color} {piece}: {e}")
        return piece_images

    def draw_piece(self, screen, piece, color, col, row):
        """Draw a specific piece of a given color at a given cell position."""
        key = f"{color}_{piece}"
        if key in self.piece_images:
            piece_image = self.piece_images[key]
            scale_factor = self.scale_factors.get(color, {}).get(piece, 1)  # Get color-specific factor
            scaled_width = int(self.cell_size * scale_factor)
            scaled_height = int(self.cell_size * scale_factor)

            # Scale the image to the desired size
            scaled_image = pygame.transform.scale(piece_image, (scaled_width, scaled_height))

            # Calculate the position to center the image in the cell
            position = (col * self.cell_size + (self.cell_size - scaled_width) // 2,
                        row * self.cell_size + (self.cell_size - scaled_height) // 2)
            screen.blit(scaled_image, position)
