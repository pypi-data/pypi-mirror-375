import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image
import io
import sys

from terminal_formatter.core import (
    RGB,
    ColorFuncs,
    Terminal,
    TextFormatter,
    PrintOptions,
    Printer,
    MinecraftColors,
    ImageRenderer,
    RAINBOW_COLORS,
    RESET,
    IMAGE_CHARACTER
)


class TestRGB:
    
    def test_rgb_creation(self):
        rgb = RGB(255, 128, 0)
        assert rgb.r == 255
        assert rgb.g == 128
        assert rgb.b == 0
    
    def test_rgb_invalid_values(self):
        with pytest.raises(ValueError):
            RGB(256, 0, 0)
        
        with pytest.raises(ValueError):
            RGB(-1, 0, 0)
        
        with pytest.raises(ValueError):
            RGB(0, 0, 256)
    
    def test_rgb_from_sequence(self):
        rgb1 = RGB.from_sequence([255, 128, 64])
        assert rgb1.r == 255
        assert rgb1.g == 128
        assert rgb1.b == 64
        
        rgb2 = RGB.from_sequence((100, 200, 50))
        assert rgb2.r == 100
        assert rgb2.g == 200
        assert rgb2.b == 50
    
    def test_rgb_from_sequence_invalid(self):
        with pytest.raises(ValueError):
            RGB.from_sequence([255, 128])
        
        with pytest.raises(ValueError):
            RGB.from_sequence([255, 128, 64, 32])
    
    def test_rgb_color_codes(self):
        rgb = RGB(255, 128, 64)
        
        foreground = rgb.to_foreground()
        assert foreground == "\033[38;2;255;128;64m"
        
        background = rgb.to_background()
        assert background == "\033[48;2;255;128;64m"
        
        bottom_rgb = RGB(100, 200, 50)
        dual = rgb.to_dual(bottom_rgb)
        assert dual == "\033[48;2;255;128;64;38;2;100;200;50m"


class TestColorFuncs:
    
    def test_rgb_fore_with_rgb_object(self):
        rgb = RGB(255, 0, 0)
        result = ColorFuncs.rgb_fore(rgb)
        assert result == "\033[38;2;255;0;0m"
    
    def test_rgb_fore_with_list(self):
        result = ColorFuncs.rgb_fore([0, 255, 0])
        assert result == "\033[38;2;0;255;0m"
    
    def test_rgb_fore_with_tuple(self):
        result = ColorFuncs.rgb_fore((0, 0, 255))
        assert result == "\033[38;2;0;0;255m"
    
    def test_rgb_back_with_rgb_object(self):
        rgb = RGB(128, 128, 128)
        result = ColorFuncs.rgb_back(rgb)
        assert result == "\033[48;2;128;128;128m"


class TestTextFormatter:
    
    def test_rainbow_text_basic(self):
        text = "Hello"
        result = TextFormatter.rainbow_text(text)
        
        assert "\033[38;2;" in result
        assert RESET in result
        assert "Hello" in result
    
    def test_rainbow_text_empty(self):
        result = TextFormatter.rainbow_text("")
        assert result == ""
    
    def test_rainbow_text_spaces_only(self):
        text = "   "
        result = TextFormatter.rainbow_text(text)
        assert result == text
    
    def test_rainbow_text_background(self):
        text = "Test"
        result = TextFormatter.rainbow_text(text, background=True)
        
        assert "\033[48;2;" in result
        assert RESET in result
    
    def test_align_text_left(self):
        text = "Hello"
        result = TextFormatter.align_text(text, 10, "left")
        assert result == "Hello     "
        assert len(result) == 10
    
    def test_align_text_right(self):
        text = "Hello"
        result = TextFormatter.align_text(text, 10, "right")
        assert result == "     Hello"
        assert len(result) == 10
    
    def test_align_text_center(self):
        text = "Hi"
        result = TextFormatter.align_text(text, 6, "center")
        assert result == "  Hi  "
        assert len(result) == 6
    
    def test_align_text_invalid_width(self):
        with pytest.raises(ValueError):
            TextFormatter.align_text("Hello", 3, "left")
    
    def test_align_text_invalid_alignment(self):
        with pytest.raises(ValueError):
            TextFormatter.align_text("Hello", 10, "invalid")
    
    def test_substitute_text_basic(self):
        text = "Hello World"
        result = TextFormatter.substitute_text(text, "Python", 6)
        assert result == "Hello Python"
    
    def test_substitute_text_with_end(self):
        text = "Hello World"
        result = TextFormatter.substitute_text(text, "Beautiful", 6, 11)
        assert result == "Hello Beautiful"
    
    def test_substitute_text_no_end(self):
        text = "Hello World"
        result = TextFormatter.substitute_text(text, "Python", 6)
        assert result == "Hello Python"


class TestPrintOptions:
    
    def test_print_options_defaults(self):
        options = PrintOptions()
        assert options.speed == 10.0
        assert options.text_color is None
        assert options.background_color is None
        assert options.end == "\n"
        assert options.newline_delay == 0.5
    
    def test_print_options_custom(self):
        options = PrintOptions(
            speed=20.0,
            text_color=[255, 0, 0],
            background_color=(0, 255, 0),
            end="",
            newline_delay=1.0
        )
        assert options.speed == 20.0
        assert options.text_color == [255, 0, 0]
        assert options.background_color == (0, 255, 0)
        assert options.end == ""
        assert options.newline_delay == 1.0


class TestPrinter:
    
    @patch('builtins.print')
    @patch('time.sleep')
    def test_slow_print_basic(self, mock_sleep, mock_print):
        Printer.slow_print("Hi")
        
        assert mock_print.call_count >= 3
        mock_sleep.assert_called()
    
    @patch('builtins.print')
    def test_print_box(self, mock_print):
        Printer.print_box("Test")
        
        assert mock_print.call_count == 1
        printed_text = mock_print.call_args[0][0]
        assert "Test" in printed_text
        assert "#" in printed_text
        assert "=" in printed_text


class TestMinecraftColors:
    
    def test_minecraft_colors_basic(self):
        mc = MinecraftColors()
        text = "&cRed &aGreen &9Blue"
        result = mc.format_text(text)
        
        assert "\033[38;2;" in result
        assert result.endswith(RESET)
        assert "Red" in result
        assert "Green" in result
        assert "Blue" in result
    
    def test_minecraft_colors_formatting(self):
        mc = MinecraftColors()
        
        result = mc.format_text("&lBold")
        assert "\033[1m" in result
        
        result = mc.format_text("&nUnderline")
        assert "\033[4m" in result
        
        result = mc.format_text("&oItalic")
        assert "\033[3m" in result
        
        result = mc.format_text("&rReset")
        assert "\033[0m" in result
    
    def test_minecraft_colors_no_codes(self):
        mc = MinecraftColors()
        text = "Plain text"
        result = mc.format_text(text)
        assert result == text + RESET


class TestImageRenderer:
    
    def create_test_image(self, width=10, height=10, color=(255, 0, 0)):
        img = Image.new('RGB', (width, height), color)
        return img
    
    def test_image_to_ascii_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            ImageRenderer.image_to_ascii("nonexistent.jpg")
    
    @patch('PIL.Image.open')
    def test_image_to_ascii_basic(self, mock_open):
        mock_img = MagicMock()
        mock_img.mode = 'RGB'
        mock_img.size = (4, 4)
        mock_img.getpixel.return_value = (255, 0, 0)
        mock_img.__enter__.return_value = mock_img
        mock_img.__exit__.return_value = None
        
        mock_open.return_value = mock_img
        
        result = ImageRenderer.image_to_ascii("test.jpg")
        
        assert "\033[48;2;" in result
        assert IMAGE_CHARACTER in result
        assert RESET in result
    
    def test_image_to_ascii_with_real_image(self):
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            img = self.create_test_image(4, 4, (255, 128, 0))
            img.save(tmp_file.name, 'PNG')
            tmp_path = tmp_file.name
        
        try:
            result = ImageRenderer.image_to_ascii(tmp_path)
            
            assert isinstance(result, str)
            assert len(result) > 0
            assert IMAGE_CHARACTER in result
            assert "\033[" in result
            
        finally:
            os.unlink(tmp_path)


class TestTerminal:
    
    @patch('builtins.print')
    def test_clear_screen(self, mock_print):
        Terminal.clear_screen()
        mock_print.assert_called_once_with("\033c\033[H", end="")
    
    @patch('builtins.print')
    def test_set_cursor_position(self, mock_print):
        Terminal.set_cursor_position(10, 5)
        mock_print.assert_called_once_with("\033[10;5H", end="")
    
    @patch('builtins.print')
    def test_scroll_cursor_up(self, mock_print):
        Terminal.scroll_cursor(-3)
        mock_print.assert_called_once_with("\033[3A", end="")
    
    @patch('builtins.print')
    def test_scroll_cursor_down(self, mock_print):
        Terminal.scroll_cursor(3)
        mock_print.assert_called_once_with("\033[3B", end="")
    
    @patch('builtins.print')
    def test_replace_current_line(self, mock_print):
        Terminal.replace_current_line("New text")
        mock_print.assert_called_once_with("\33[2K\rNew text", end="")
    
    @patch('builtins.print')
    def test_replace_line(self, mock_print):
        Terminal.replace_line(5, "Line content")
        mock_print.assert_called_once_with("\33[s\33[5;0H\33[2K\rLine content\33[u", end="")


class TestConstants:
    
    def test_rainbow_colors_length(self):
        assert len(RAINBOW_COLORS) == 6
    
    def test_rainbow_colors_format(self):
        for color in RAINBOW_COLORS:
            assert len(color) == 3
            assert all(0 <= val <= 255 for val in color)
    
    def test_reset_constant(self):
        assert RESET == "\033[0m"
    
    def test_image_character_constant(self):
        assert IMAGE_CHARACTER == "▄"


class TestIntegration:
    
    def test_rgb_with_text_formatter(self):
        rgb = RGB(255, 0, 0)
        text = "Test"
        
        colored_text = f"{rgb.to_foreground()}{text}{RESET}"
        assert colored_text == f"\033[38;2;255;0;0m{text}\033[0m"
    
    def test_minecraft_colors_with_formatting(self):
        mc = MinecraftColors()
        text = "&c&lRed Bold &r&aGreen Normal"
        result = mc.format_text(text)
        
        assert "\033[38;2;" in result
        assert "\033[1m" in result
        assert "\033[0m" in result
    
    @patch('builtins.print')
    def test_complete_workflow(self, mock_print):
        Terminal.clear_screen()
        
        rainbow = TextFormatter.rainbow_text("Hello World!")
        
        aligned = TextFormatter.align_text("Centered", 20, "center")
        
        Printer.print_box("Demo")
        
        assert mock_print.call_count > 0


if __name__ == "__main__":
    pytest.main([__file__])