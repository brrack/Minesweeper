import random

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
BOMB_COUNT = 40
BOMB_IMAGE_PATH = "bomb.png"
FLAG_IMAGE_PATH = "flag.png"
NUMBER_IMAGE_PATHS = {
    1: "one.png",
    2: "two.png",
    3: "three.png",
    4: "four.png",
    5: "five.png",
    6: "six.png",
    7: "seven.png",
    8: "eight.png",
}

NEIGHBOR_DIRECTIONS = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
]

STRAIGHT_DIRECTIONS = [
    (-1, 0),
    (0, -1),
    (0, 1),
    (1, 0),
]


def create_bombs():
    all_tiles = []

    for row in range(ROWS):
        for col in range(COLS):
            all_tiles.append((row, col))

    bomb_count = min(BOMB_COUNT, len(all_tiles))
    return set(random.sample(all_tiles, bomb_count))


def count_touching_bombs(row, col, bomb_tiles):
    bomb_count = 0

    for row_change, col_change in NEIGHBOR_DIRECTIONS:
        neighbor_pos = (row + row_change, col + col_change)

        if neighbor_pos in bomb_tiles:
            bomb_count += 1

    return bomb_count


def create_number_grid(bomb_tiles):
    number_grid = {}

    for row in range(ROWS):
        for col in range(COLS):
            tile_pos = (row, col)

            if tile_pos not in bomb_tiles:
                touching_bombs = count_touching_bombs(row, col, bomb_tiles)

                if touching_bombs > 0:
                    number_grid[tile_pos] = touching_bombs

    return number_grid


def uncover_blank_tiles(start_tile, bomb_tiles, number_grid):
    tiles_to_check = [start_tile]
    uncovered_tiles = set()

    while tiles_to_check:
        tile_pos = tiles_to_check.pop()

        if tile_pos in uncovered_tiles:
            continue

        row, col = tile_pos

        if not (0 <= row < ROWS and 0 <= col < COLS):
            continue

        if tile_pos in bomb_tiles or tile_pos in number_grid:
            continue

        uncovered_tiles.add(tile_pos)

        for row_change, col_change in STRAIGHT_DIRECTIONS:
            neighbor_pos = (row + row_change, col + col_change)
            tiles_to_check.append(neighbor_pos)

    for row, col in list(uncovered_tiles):
        for row_change, col_change in NEIGHBOR_DIRECTIONS:
            neighbor_pos = (row + row_change, col + col_change)

            if neighbor_pos in number_grid:
                uncovered_tiles.add(neighbor_pos)

    return uncovered_tiles


def uncover_tile(tile_pos, clicked_tiles, flagged_tiles, bomb_tiles, number_grid):
    if tile_pos in clicked_tiles or tile_pos in flagged_tiles:
        return

    clicked_tiles.add(tile_pos)

    if tile_pos not in bomb_tiles and tile_pos not in number_grid:
        clicked_tiles.update(uncover_blank_tiles(tile_pos, bomb_tiles, number_grid))


def get_neighbor_tiles(tile_pos):
    row, col = tile_pos
    neighbor_tiles = []

    for row_change, col_change in NEIGHBOR_DIRECTIONS:
        neighbor_pos = (row + row_change, col + col_change)
        neighbor_row, neighbor_col = neighbor_pos

        if 0 <= neighbor_row < ROWS and 0 <= neighbor_col < COLS:
            neighbor_tiles.append(neighbor_pos)

    return neighbor_tiles


def count_touching_flags(tile_pos, flagged_tiles):
    flag_count = 0

    for neighbor_pos in get_neighbor_tiles(tile_pos):
        if neighbor_pos in flagged_tiles:
            flag_count += 1

    return flag_count


def can_uncover_nearby_tiles(tile_pos, clicked_tiles, flagged_tiles, number_grid):
    if tile_pos not in clicked_tiles or tile_pos not in number_grid:
        return False

    return count_touching_flags(tile_pos, flagged_tiles) == number_grid[tile_pos]


def get_chord_preview_tiles(tile_pos, clicked_tiles, flagged_tiles, number_grid):
    if tile_pos is None or tile_pos not in clicked_tiles or tile_pos not in number_grid:
        return set()

    preview_tiles = set()

    for neighbor_pos in get_neighbor_tiles(tile_pos):
        if neighbor_pos not in clicked_tiles and neighbor_pos not in flagged_tiles:
            preview_tiles.add(neighbor_pos)

    return preview_tiles


def uncover_nearby_tiles(tile_pos, clicked_tiles, flagged_tiles, bomb_tiles, number_grid):
    if tile_pos not in clicked_tiles or tile_pos not in number_grid:
        return

    for neighbor_pos in get_neighbor_tiles(tile_pos):
        uncover_tile(neighbor_pos, clicked_tiles, flagged_tiles, bomb_tiles, number_grid)


def load_tile_image(path):
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))


def load_number_images():
    number_images = {}

    for number, path in NUMBER_IMAGE_PATHS.items():
        number_images[number] = load_tile_image(path)

    return number_images


def draw(
    screen,
    clicked_tiles,
    flagged_tiles,
    chord_preview_tiles,
    bomb_tiles,
    number_grid,
    bomb_image,
    flag_image,
    number_images,
):
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
            elif tile_pos in chord_preview_tiles:
                tile_color = TILE_HOVER_COLOR
            elif is_hovered and mouse_pressed:
                tile_color = TILE_PRESSED_COLOR
            elif is_hovered:
                tile_color = TILE_HOVER_COLOR
            else:
                tile_color = TILE_COLOR

            pygame.draw.rect(screen, tile_color, tile_rect)

            if tile_pos in clicked_tiles and tile_pos in bomb_tiles:
                screen.blit(bomb_image, tile_rect)
            elif tile_pos in clicked_tiles and tile_pos in number_grid:
                number = number_grid[tile_pos]
                screen.blit(number_images[number], tile_rect)
            elif tile_pos in flagged_tiles:
                screen.blit(flag_image, tile_rect)

            pygame.draw.rect(screen, TILE_BORDER_COLOR, tile_rect, width=1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Minesweeper")
    clock = pygame.time.Clock()
    clicked_tiles = set()
    flagged_tiles = set()
    bomb_tiles = create_bombs()
    number_grid = create_number_grid(bomb_tiles)
    bomb_image = load_tile_image(BOMB_IMAGE_PATH)
    flag_image = load_tile_image(FLAG_IMAGE_PATH)
    number_images = load_number_images()
    chord_tile = None
    suppress_left_click = False
    suppress_right_click = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                left_pressed, _, right_pressed = pygame.mouse.get_pressed()

                if left_pressed and right_pressed:
                    mouse_x, mouse_y = event.pos
                    col = mouse_x // TILE_SIZE
                    row = mouse_y // TILE_SIZE

                    if 0 <= row < ROWS and 0 <= col < COLS:
                        tile_pos = (row, col)

                        if tile_pos in clicked_tiles and tile_pos in number_grid:
                            chord_tile = tile_pos

                        suppress_left_click = True
                        suppress_right_click = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if suppress_left_click:
                    if can_uncover_nearby_tiles(
                        chord_tile,
                        clicked_tiles,
                        flagged_tiles,
                        number_grid,
                    ):
                        uncover_nearby_tiles(
                            chord_tile,
                            clicked_tiles,
                            flagged_tiles,
                            bomb_tiles,
                            number_grid,
                        )

                    chord_tile = None
                    suppress_left_click = False
                    continue

                mouse_x, mouse_y = event.pos
                col = mouse_x // TILE_SIZE
                row = mouse_y // TILE_SIZE

                if 0 <= row < ROWS and 0 <= col < COLS:
                    uncover_tile(
                        (row, col),
                        clicked_tiles,
                        flagged_tiles,
                        bomb_tiles,
                        number_grid,
                    )
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                if suppress_right_click:
                    if can_uncover_nearby_tiles(
                        chord_tile,
                        clicked_tiles,
                        flagged_tiles,
                        number_grid,
                    ):
                        uncover_nearby_tiles(
                            chord_tile,
                            clicked_tiles,
                            flagged_tiles,
                            bomb_tiles,
                            number_grid,
                        )

                    chord_tile = None
                    suppress_right_click = False
                    continue

                mouse_x, mouse_y = event.pos
                col = mouse_x // TILE_SIZE
                row = mouse_y // TILE_SIZE

                if 0 <= row < ROWS and 0 <= col < COLS:
                    tile_pos = (row, col)

                    if tile_pos not in clicked_tiles:
                        if tile_pos in flagged_tiles:
                            flagged_tiles.remove(tile_pos)
                        else:
                            flagged_tiles.add(tile_pos)

        left_pressed, _, right_pressed = pygame.mouse.get_pressed()
        if left_pressed and right_pressed:
            chord_preview_tiles = get_chord_preview_tiles(
                chord_tile,
                clicked_tiles,
                flagged_tiles,
                number_grid,
            )
        else:
            chord_preview_tiles = set()

        draw(
            screen,
            clicked_tiles,
            flagged_tiles,
            chord_preview_tiles,
            bomb_tiles,
            number_grid,
            bomb_image,
            flag_image,
            number_images,
        )
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
