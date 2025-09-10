
import os
import sys
from arabic_reshaper import ArabicReshaper
from bidi.algorithm import get_display

def _apply_rtl_and_bidi(text):
    reshaper = ArabicReshaper()
    reshaped_text = reshaper.reshape(text)
    return get_display(reshaped_text)

def print_persian(text):
    """
    Prints Persian text correctly, handling right-to-left display.
    Attempts to use platform-specific methods for better compatibility.
    """
    processed_text = _apply_rtl_and_bidi(text)
    sys.stdout.write(processed_text + '\n')
    sys.stdout.flush()

def colored_print(text, color="reset", style="normal", background="default"):
    """
    Prints text with specified color, style, and background.
    Available colors: black, red, green, yellow, blue, magenta, cyan, white, reset.
    Available styles: normal, bold, underline.
    Available backgrounds: black, red, green, yellow, blue, magenta, cyan, white, default.
    """
    colors = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m"
    }

    styles = {
        "normal": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m"
    }

    backgrounds = {
        "black": "\033[40m",
        "red": "\033[41m",
        "green": "\033[42m",
        "yellow": "\033[43m",
        "blue": "\033[44m",
        "magenta": "\033[45m",
        "cyan": "\033[46m",
        "white": "\033[47m",
        "default": "\033[49m"
    }
    
    color_code = colors.get(color.lower(), colors["reset"])
    style_code = styles.get(style.lower(), styles["normal"])
    background_code = backgrounds.get(background.lower(), backgrounds["default"])
    
    formatted_text = _apply_rtl_and_bidi(text)
    
    sys.stdout.write(f"{style_code}{background_code}{color_code}{formatted_text}{colors['reset']}{styles['normal']}{backgrounds['default']}\n")
    sys.stdout.flush()


