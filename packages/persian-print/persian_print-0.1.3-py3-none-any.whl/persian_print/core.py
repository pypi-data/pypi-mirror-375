
import os
import sys
from arabic_reshaper import ArabicReshaper
from bidi.algorithm import get_display

def _apply_rtl_and_bidi(text):
    reshaper = ArabicReshaper()
    reshaped_text = reshaper.reshape(text)
    # The get_display function handles the visual reordering for display.
    # For better cross-platform compatibility, especially on Windows, we will
    # rely on the terminal's ability to render Unicode correctly. 
    # The bidi algorithm is still important for logical ordering.
    bidi_text = get_display(reshaped_text)
    return bidi_text

def print_persian(text):
    """
    Prints Persian text correctly, handling right-to-left display.
    """
    # On Windows, using 'chcp 65001' might be necessary in cmd/powershell
    # to ensure UTF-8 support. For other OS, it usually works out of the box.
    # The key is to ensure the terminal font supports Persian characters.
    print(_apply_rtl_and_bidi(text))

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
    
    print(f"{style_code}{background_code}{color_code}{formatted_text}{colors["reset"]}{styles["normal"]}{backgrounds["default"]}")




