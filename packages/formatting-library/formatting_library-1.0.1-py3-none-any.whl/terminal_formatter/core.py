# ======= #
# Imports #
# ======= #

import time
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from PIL import Image # type: ignore

# ========= #
# Variables # 
# ========= #

IMAGE_CHARACTER = "▄"
RESET = "\033[0m"

RAINBOW_COLORS = [
    (255, 179, 179),
    (255, 217, 179),
    (255, 255, 179),
    (179, 255, 179),
    (179, 179, 255),
    (217, 179, 255)
]

# ================ #
# Color Converters #
# ================ #

@dataclass
class RGB:

    r: int
    g: int
    b: int

    def __post_init__(self):
        if not all(0 <= val <= 255 for val in (self.r, self.g, self.b)):
            raise ValueError("RGB values must be between 0 and 255")

    @classmethod
    def from_sequence(cls, rgb: Union[List[int], Tuple[int, ...]]) -> 'RGB':
        if len(rgb) != 3:
            raise ValueError("RGB must contain exactly 3 values")
        return cls(*rgb)
    
    def to_foreground(self) -> str:
        return f"\033[38;2;{self.r};{self.g};{self.b}m"
    
    def to_background(self) -> str:
        return f"\033[48;2;{self.r};{self.g};{self.b}m"
    
    def to_dual(self, bottom: 'RGB') -> str:
        return f"\033[48;2;{self.r};{self.g};{self.b};38;2;{bottom.r};{bottom.g};{bottom.b}m"
    
class ColorFuncs:

    @staticmethod
    def rgb_fore(rgb: Union[RGB, List[int], Tuple[int, ...]]) -> str:
        if not isinstance(rgb, RGB):
            rgb = RGB.from_sequence(rgb)
        return rgb.to_foreground()

    @staticmethod
    def rgb_back(rgb: Union[RGB, List[int], Tuple[int, ...]]) -> str:
        if not isinstance(rgb, RGB):
            rgb = RGB.from_sequence(rgb)
        return rgb.to_background()

# ================== #
# Terminal Modifiers #
# ================== #

class Terminal:
    
    @staticmethod
    def clear_screen():
        print("\033c\033[H", end="")
    
    @staticmethod
    def set_cursor_position(x: int, y: int):
        print(f"\033[{x};{y}H", end="")
    
    @staticmethod
    def scroll_cursor(lines: int):
        direction = "A" if lines <= 0 else "B"
        print(f"\033[{abs(lines)}{direction}", end="")
    
    @staticmethod
    def replace_current_line(text: str):
        print(f"\33[2K\r{text}", end="")
    
    @staticmethod
    def replace_line(y: int, text: str):
        print(f"\33[s\33[{y};0H\33[2K\r{text}\33[u", end="")


# =============== #
# Cool Formatting #
# =============== #

class TextFormatter:
    
    @staticmethod
    def rainbow_text(text: str, *, background: bool = False) -> str:
        color_func = ColorFuncs.rgb_back if background else ColorFuncs.rgb_fore
        non_spaces = [(i, c) for i, c in enumerate(text) if c != ' ']
        
        if not non_spaces:
            return text
        
        result = list(text)
        
        for i, (pos, char) in enumerate(non_spaces):
            color_index = min(
                int(i * len(RAINBOW_COLORS) / len(non_spaces)),
                len(RAINBOW_COLORS) - 1
            )
            rgb_color = RAINBOW_COLORS[color_index]
            result[pos] = f"{color_func(rgb_color)}{char}{RESET}"
        
        return ''.join(result)
    
    @staticmethod
    def align_text(text: str, width: int, alignment: str = "right") -> str:
        if width < len(text):
            raise ValueError(f"Width ({width}) cannot be less than text length ({len(text)})")
        
        mappings = {
            "left": f"{text:<{width}}",
            "right": f"{text:>{width}}",
            "center": f"{text:^{width}}"
        }
        
        try:
            return mappings[alignment.lower()]
        except KeyError:
            raise ValueError("Invalid alignment. Choose: 'left', 'right', 'center'")
    
    @staticmethod
    def substitute_text(text: str, replacement: str, start: int = 0, end: Optional[int] = None) -> str:
        if end is None:
            return text[:start] + replacement
        return text[:start] + replacement + text[end:]
    
@dataclass
class PrintOptions:
    speed: float = 10.0
    text_color: Optional[Union[RGB, List[int], Tuple[int, ...]]] = None
    background_color: Optional[Union[RGB, List[int], Tuple[int, ...]]] = None
    end: str = "\n"
    newline_delay: float = 0.5


class Printer:
    
    @staticmethod
    def slow_print(text: str, options: Optional[PrintOptions] = None):
        if options is None:
            options = PrintOptions()
        
        delay = 1 / options.speed
        
        if options.text_color:
            print(ColorFuncs.rgb_fore(options.text_color), end="")
        if options.background_color:
            print(ColorFuncs.rgb_back(options.background_color), end="")
        
        for char in text:
            print(char, end="", flush=True)
            time.sleep(delay)
            if char == "\n":
                time.sleep(options.newline_delay)
        
        print(RESET, end=options.end)
    
    @staticmethod
    def print_box(text: str):
        """
        You can use this function to create the cool looking boxes that I've been using to group the code!
        """
        border = f"# {'=' * len(text)} #"
        print(f"{border}\n# {text} #\n{border}")

# ===================== #
# Custom Text Formatter #
# ===================== #

@dataclass
class ImprovedColors:
    
    COLOR_MAP: Dict[str, str] = field(default_factory=lambda: {
        '0': "\33[38;2;0;0;0m",
        '1': "\33[38;2;0;0;170m",
        '2': "\33[38;2;0;170;0m",
        '3': "\33[38;2;0;170;170m",
        '4': "\33[38;2;170;0;0m",
        '5': "\33[38;2;170;0;170m",
        '6': "\33[38;2;255;170;0m",
        '7': "\33[38;2;170;170;170m",
        '8': "\33[38;2;85;85;85m",
        '9': "\33[38;2;85;85;255m",
        'a': "\33[38;2;85;255;85m",
        'b': "\33[38;2;85;255;255m",
        'c': "\33[38;2;255;85;85m",
        'd': "\33[38;2;255;85;255m",
        'e': "\33[38;2;255;255;85m",
        'f': "\33[38;2;255;255;255m",
        'l': '\33[1m',
        'n': '\33[4m',
        'o': '\33[3m',
        'r': "\33[0m"
    })
    
    def format_text(self, text: str) -> str:
        def replace_color_code(match):
            code = match.group(1).lower()
            return self.COLOR_MAP.get(code, '')
        
        result = re.sub(r'&(.)', replace_color_code, text)
        return result + RESET

# ============== #
# Image Renderer #
# ============== #

class ImageRenderer:
    
    @staticmethod
    def image_to_ascii(image_path: Union[str, Path]) -> str:
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        lines = []
        
        with Image.open(image_path) as image:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            width, height = image.size
            
            for y in range(0, height - 1, 2):
                line_parts = []
                for x in range(width):
                    top_pixel = RGB(*image.getpixel((x, y)))
                    bottom_pixel = RGB(*image.getpixel((x, y + 1)))
                    
                    color_code = top_pixel.to_dual(bottom_pixel)
                    line_parts.append(f"{color_code}{IMAGE_CHARACTER}")
                
                lines.append(''.join(line_parts) + RESET)
            
            if height % 2 == 1:
                line_parts = []
                for x in range(width):
                    top_pixel = RGB(*image.getpixel((x, height - 1)))
                    bottom_pixel = RGB(255, 255, 255)
                    
                    color_code = top_pixel.to_dual(bottom_pixel)
                    line_parts.append(f"{color_code}{IMAGE_CHARACTER}")
                
                lines.append(''.join(line_parts) + RESET)
        
        return '\n'.join(lines)
    
# ======= #
# Aliases #
# ======= #

clear_screen = Terminal.clear_screen
set_cursor_position = Terminal.set_cursor_position
scroll_cursor = Terminal.scroll_cursor
replace_current_line = Terminal.replace_current_line
replace_line = Terminal.replace_line

rainbow_text = TextFormatter.rainbow_text
align = TextFormatter.align_text
substitute = TextFormatter.substitute_text

slow_print = Printer.slow_print
ccb_gen = Printer.print_box

rgb_fore = ColorFuncs.rgb_fore
rgb_back = ColorFuncs.rgb_back

COLORS = ImprovedColors()
formatted = COLORS.format_text

img_to_ascii = ImageRenderer.image_to_ascii
