import pygame


WIDTH = 800
HEIGHT = 600
FPS = 60

BACKGROUND_COLOR = (24, 28, 36)
TILE_COLOR = (48, 58, 72)
TILE_HOVER_COLOR = (62, 74, 92)
TILE_PRESSED_COLOR = (32, 38, 48)
TILE_CLICKED_COLOR = (0, 0, 0)
TILE_BORDER_COLOR = (90, 102, 120)

TILE_SIZE = 40
ROWS = HEIGHT // TILE_SIZE
COLS = WIDTH // TILE_SIZE


def draw(screen, clicked_tiles):
    screen.fill(BACKGROUND_COLOR)
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]

    for row in range(ROWS):
        for col in range(COLS):
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            tile_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

            tile_pos = (row, col)
            is_hovered = tile_rect.collidepoint(mouse_pos)

            if tile_pos in clicked_tiles:
                tile_color = TILE_CLICKED_COLOR
            elif is_hovered and mouse_pressed:
                tile_color = TILE_PRESSED_COLOR
            elif is_hovered:
                tile_color = TILE_HOVER_COLOR
            else:
                tile_color = TILE_COLOR

            pygame.draw.rect(screen, tile_color, tile_rect)
            pygame.draw.rect(screen, TILE_BORDER_COLOR, tile_rect, width=1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Minesweeper")
    clock = pygame.time.Clock()
    clicked_tiles = set()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_x, mouse_y = event.pos
                col = mouse_x // TILE_SIZE
                row = mouse_y // TILE_SIZE

                if 0 <= row < ROWS and 0 <= col < COLS:
                    clicked_tiles.add((row, col))

        draw(screen, clicked_tiles)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
