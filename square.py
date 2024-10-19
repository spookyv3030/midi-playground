try:
    from glowing import make_glowy2
except ImportError:
    make_glowy2 = None
from utils import *
import pygame
from pygame import Color
from bounce import Bounce


class Square:
    def __init__(self, x: float = 0, y: float = 0, dx: int = 1, dy: int = 1):
        self.pos: list[float] = [x, y]
        self.dir: list[int] = [dx, dy]
        self.last_bounce_time = -100
        self.latest_bounce_direction = 0  # 0 = horiz, 1 = vert
        self.past_colors = []
        self.died = False

        self.time_since_glow_start = 0
        self.glowy_surfaces = {}

    def register_past_color(self, col: tuple[int, int, int]):
        for _ in range(max(Config.square_swipe_anim_speed, 1)):
            self.past_colors.insert(0, col)
        while len(self.past_colors) > Config.SQUARE_SIZE * 4 / 5:
            self.past_colors.pop()

    def get_surface(self, size: tuple[int, int]):
        ss = int(Config.SQUARE_SIZE * 4 / 5)
        surf = pygame.Surface((ss, ss))
        for index, col in enumerate(self.past_colors):
            y = index if self.dir_y != 1 else ss - 1 - index
            pygame.draw.line(surf, col, (0, y), (ss, y))
        return pygame.transform.scale(surf, size)

    def copy(self) -> "Square":
        new = Square(*self.pos, *self.dir)
        new.last_bounce_time = self.last_bounce_time
        new.latest_bounce_direction = self.latest_bounce_direction
        return new

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    def title_screen_physics(self, bounding: pygame.Rect):
        self.reg_move()
        r = self.rect
        if r.right > bounding.right:
            self.dir[0] = -1
            self.latest_bounce_direction = 0
        elif r.left < bounding.left:
            self.dir[0] = 1
            self.latest_bounce_direction = 0
        elif r.bottom > bounding.bottom:
            self.dir[1] = -1
            self.latest_bounce_direction = 1
        elif r.top < bounding.top:
            self.dir[1] = 1
            self.latest_bounce_direction = 1
        else:
            return False
        self.start_bounce()
        self.last_bounce_time = get_current_time()
        return True

   def compute_glowy_surface(self, rect, val):
    # Set the glow color to yellow
    glow_color = (255, 255, 0)  # RGB value for yellow
    # Create the glowing borders with the yellow color
    glowy_borders = make_glowy2((rect.size[0] + 40, rect.size[1] + 40),  color(pygame.color(255.255.0) 
                                
    # Create a transparent surface with enough space for the glow effect
    surface = pygame.Surface(rect.inflate(100, 100).size, pygame.SRCALPHA)
    
    # Blit the glowing borders onto the surface with an add blend mode
    surface.blit(glowy_borders, (20, 20), special_flags=pygame.BLEND_RGBA_ADD)
    
    return surface

    def draw_glowing3(self, win, rect):
        if self.died:
            return

        if Config.square_glow:
            if pygame.time.get_ticks() - self.time_since_glow_start < Config.square_glow_duration * 1000:
                progress = 1 - (pygame.time.get_ticks() - self.time_since_glow_start) / (
                        Config.square_glow_duration * 1000)
                val = int(progress * Config.glow_intensity)
            else:
                val = 1
            val = max(val, Config.square_min_glow)
            surf = self.compute_glowy_surface(rect, val)

            win.blit(surf, rect.move(-40, -40).topleft, special_flags=pygame.BLEND_RGBA_ADD)

    def draw(self, screen: pygame.Surface, sqrect: pygame.Rect):
        if self.died:
            return
        square_color_index = round((self.dir_x + 1) / 2 + self.dir_y + 1)
        self.register_past_color(get_colors()["square"][square_color_index % len(get_colors()["square"])])

        if Config.theme == "dark_modern" and make_glowy2 is not None:
            self.draw_glowing3(screen, sqrect)
        else:
            pygame.draw.rect(screen, (0, 0, 0), sqrect)
            sq_surf = self.get_surface(
                tuple(sqrect.inflate(-int(Config.SQUARE_SIZE / 5), -int(Config.SQUARE_SIZE / 5))[2:]))
            screen.blit(sq_surf, sq_surf.get_rect(center=sqrect.center))

    @x.setter
    def x(self, val: int):
        self.pos[0] = val

    @y.setter
    def y(self, val: int):
        self.pos[1] = val

    @property
    def dir_x(self):
        return self.dir[0]

    @property
    def dir_y(self):
        return self.dir[1]

    @property
    def rect(self):
        return pygame.Rect(self.x - Config.SQUARE_SIZE / 2, self.y - Config.SQUARE_SIZE / 2,
                           *([Config.SQUARE_SIZE] * 2))

    def start_bounce(self):
        self.time_since_glow_start = pygame.time.get_ticks()

    def obey_bounce(self, bounce: Bounce):
        # planned bounces
        self.start_bounce()
        self.pos = bounce.square_pos
        self.dir = bounce.square_dir
        self.latest_bounce_direction = bounce.bounce_dir
        self.last_bounce_time = bounce.time
        return

    def reg_move(self, use_dt: bool = True):
        self.x += self.dir_x * Config.square_speed * (Config.dt if use_dt else 1 / FRAMERATE)
        self.y += self.dir_y * Config.square_speed * (Config.dt if use_dt else 1 / FRAMERATE)
