#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for make_colors module
Tests all colors, shortcuts, and functionalities
"""

import os
import sys
from make_colors import make_colors, MakeColors, make_color
import time

def print_separator(title, char="=", width=60):
    """Print a formatted separator with title"""
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}")

def test_color_support():
    """Test color support detection"""
    print_separator("COLOR SUPPORT TEST")
    print(f"Platform: {sys.platform}")
    print(f"Color support: {MakeColors.supports_color()}")
    print(f"MAKE_COLORS env: {os.getenv('MAKE_COLORS', 'not set')}")
    print(f"MAKE_COLORS_FORCE env: {os.getenv('MAKE_COLORS_FORCE', 'not set')}")
    if hasattr(sys.stdout, 'isatty'):
        print(f"Is TTY: {sys.stdout.isatty()}")

def test_standard_colors():
    """Test all standard colors as foreground"""
    print_separator("STANDARD FOREGROUND COLORS")
    
    standard_colors = [
        'black', 'red', 'green', 'yellow', 
        'blue', 'magenta', 'cyan', 'white'
    ]
    
    for color in standard_colors:
        colored_text = make_colors(f"  ● {color.ljust(12)}", color, 'black')
        print(f"{colored_text} | {make_colors('Sample text', color)}")

def test_light_colors():
    """Test all light variant colors as foreground"""
    print_separator("LIGHT FOREGROUND COLORS")
    
    light_colors = [
        'lightblack', 'lightred', 'lightgreen', 'lightyellow',
        'lightblue', 'lightmagenta', 'lightcyan', 'lightwhite', 'lightgrey'
    ]
    
    for color in light_colors:
        colored_text = make_colors(f"  ● {color.ljust(15)}", color, 'black')
        print(f"{colored_text} | {make_colors('Sample text', color)}")

def test_background_colors():
    """Test all colors as background"""
    print_separator("BACKGROUND COLORS")
    
    all_colors = [
        'black', 'red', 'green', 'yellow', 
        'blue', 'magenta', 'cyan', 'white',
        'lightblack', 'lightred', 'lightgreen', 'lightyellow',
        'lightblue', 'lightmagenta', 'lightcyan', 'lightwhite'
    ]
    
    for bg_color in all_colors:
        # Use contrasting foreground color
        fg_color = 'white' if 'black' in bg_color or bg_color in ['blue', 'red', 'magenta'] else 'black'
        colored_text = make_colors(f"  {bg_color.ljust(15)} ", fg_color, bg_color)
        print(f"{colored_text} Background sample")

def test_color_shortcuts():
    """Test all color shortcuts"""
    print_separator("COLOR SHORTCUTS TEST")
    
    # Define all shortcuts
    shortcuts = {
        'Standard Colors': {
            'b': 'black', 'bk': 'black',
            'bl': 'blue',
            'r': 'red', 'rd': 'red', 're': 'red',
            'g': 'green', 'gr': 'green', 'ge': 'green',
            'y': 'yellow', 'ye': 'yellow', 'yl': 'yellow',
            'm': 'magenta', 'mg': 'magenta', 'ma': 'magenta',
            'c': 'cyan', 'cy': 'cyan', 'cn': 'cyan',
            'w': 'white', 'wh': 'white', 'wi': 'white', 'wt': 'white'
        },
        'Light Colors': {
            'lb': 'lightblue',
            'lr': 'lightred',
            'lg': 'lightgreen',
            'ly': 'lightyellow',
            'lm': 'lightmagenta',
            'lc': 'lightcyan',
            'lw': 'lightwhite'
        }
    }
    
    for category, shortcut_dict in shortcuts.items():
        print(f"\n--- {category} ---")
        for shortcut, full_name in shortcut_dict.items():
            shortcut_result = make_colors(f"'{shortcut}'", shortcut)
            full_result = make_colors(f"'{full_name}'", full_name)
            print(f"  {shortcut.ljust(3)} → {shortcut_result} | {full_result}")

def test_separator_notation():
    """Test underscore and dash separator notation"""
    print_separator("SEPARATOR NOTATION TEST")
    
    test_combinations = [
        'red_white', 'green_black', 'blue_yellow',
        'white_red', 'yellow_blue', 'cyan_magenta',
        'red-white', 'green-black', 'blue-yellow',
        'lr_b', 'lg_r', 'lb_y',  # light + standard
        'w_lr', 'b_lg', 'y_lb'   # standard + light
    ]
    
    print("Underscore notation (_):")
    for combo in test_combinations[:6]:
        if '_' in combo:
            result = make_colors(f"  {combo.ljust(12)}", combo)
            print(f"{result} | Sample: {make_colors('Hello World', combo)}")
    
    print("\nDash notation (-):")
    for combo in test_combinations[6:9]:
        if '-' in combo:
            result = make_colors(f"  {combo.ljust(12)}", combo)
            print(f"{result} | Sample: {make_colors('Hello World', combo)}")
    
    print("\nShortcut combinations:")
    for combo in test_combinations[9:]:
        result = make_colors(f"  {combo.ljust(8)}", combo)
        print(f"{result} | Sample: {make_colors('Hello World', combo)}")

def test_force_parameter():
    """Test force parameter functionality"""
    print_separator("FORCE PARAMETER TEST")
    
    print("Normal behavior:")
    normal = make_colors("Normal coloring", "red", "white")
    print(f"  {normal}")
    
    print("\nForced coloring:")
    forced = make_colors("Forced coloring", "green", "yellow", force=True)
    print(f"  {forced}")
    
    print("\nEnvironment variable test:")
    # Temporarily set environment variable
    original_env = os.getenv('MAKE_COLORS')
    os.environ['MAKE_COLORS'] = '0'
    disabled = make_colors("Should be disabled", "blue", "white")
    print(f"  MAKE_COLORS=0: '{disabled}'")
    
    forced_despite_env = make_colors("Should be forced", "blue", "white", force=True)
    print(f"  force=True: {forced_despite_env}")
    
    # Restore environment
    if original_env is None:
        if 'MAKE_COLORS' in os.environ:
            del os.environ['MAKE_COLORS']
    else:
        os.environ['MAKE_COLORS'] = original_env

def test_mixed_parameters():
    """Test various parameter combinations"""
    print_separator("MIXED PARAMETERS TEST")
    
    test_cases = [
        ("Standard fg/bg", "red", "white"),
        ("Shortcut fg/bg", "r", "w"),
        ("Mixed notation", "red", "w"),
        ("Light colors", "lightred", "lightblue"),
        ("Light shortcuts", "lr", "lb"),
        ("No background", "green", None),
        ("Default params", None, None),
    ]
    
    for description, fg, bg in test_cases:
        if fg is None:
            result = make_colors("Sample text")
        elif bg is None:
            result = make_colors("Sample text", fg)
        else:
            result = make_colors("Sample text", fg, bg)
        print(f"  {description.ljust(20)}: {result}")

def test_aliases():
    """Test function aliases"""
    print_separator("ALIASES TEST")
    
    # Test make_color alias
    original = make_colors("Original function", "red", "white")
    alias = make_color("Original function", "red", "white")
    
    print(f"make_colors() original [red on white]: {original}")
    print(f"make_color() alias [red on white]:  {alias}")
    print(f"Results match: {original == alias}")
    
    original = make_colors("Original function", "red", "white")
    alias = make_color("Original function", "white", "blue")
    
    print(f"make_colors() original [red on white]: {original}")
    print(f"make_color() alias [white on blue]:  {alias}")
    print(f"Results match: {original == alias}")

def test_error_conditions():
    """Test various error conditions and edge cases"""
    print_separator("ERROR CONDITIONS & EDGE CASES")
    
    print("Testing edge cases:")
    
    # Empty string
    empty_result = make_colors("", "red")
    print(f"  Empty string: '{empty_result}'")
    
    # Unknown colors (should use defaults)
    unknown_fg = make_colors("Unknown foreground", "unknowncolor")
    print(f"  Unknown foreground: {unknown_fg}")
    
    unknown_bg = make_colors("Unknown background", "red", "unknowncolor")
    print(f"  Unknown background: {unknown_bg}")
    
    # Very long text
    long_text = "A" * 100
    long_result = make_colors(long_text, "blue")
    print(f"  Long text (100 chars): {long_result[:50]}...")
    
    # Special characters
    special = make_colors("Special chars: áéíóú ñ 中文 🌈", "magenta")
    print(f"  Special characters: {special}")

def test_real_world_examples():
    """Test real-world usage examples"""
    print_separator("REAL-WORLD EXAMPLES")
    
    # Log levels
    print("Log levels:")
    print(f"  {make_colors('[ERROR]', 'white', 'red')} Something went wrong")
    print(f"  {make_colors('[WARN] ', 'black', 'yellow')} Warning message")
    print(f"  {make_colors('[INFO] ', 'white', 'blue')} Information")
    print(f"  {make_colors('[DEBUG]', 'white', 'black')} Debug info")
    
    # Status indicators
    print("\nStatus indicators:")
    print(f"  {make_colors('✓ PASS', 'lightgreen')} Test passed")
    print(f"  {make_colors('✗ FAIL', 'lightred')} Test failed")
    print(f"  {make_colors('⚠ SKIP', 'lightyellow')} Test skipped")
    print(f"  {make_colors('● RUNNING', 'lightblue')} Test running")
    
    # Progress bar simulation
    print("\nProgress simulation multiple bar:")
    for i in range(0, 101, 25):
        if i < 50:
            color = 'red'
        elif i < 80:
            color = 'yellow'
        else:
            color = 'green'
        
        filled = "█" * (i // 5)
        empty = "░" * (20 - i // 5)
        bar = make_colors(f"[{filled}{empty}] {i}%", color)
        print(f"  {bar}")
        time.sleep(0.5)
    
    print("\nProgress simulation in one bar:")
    for i in range(0, 101, 10):
        if i < 50:
            color = 'red'
        elif i < 80:
            color = 'yellow'
        else:
            color = 'green'
        
        filled = "█" * (i // 2)
        empty = "░" * (50 - i // 2)
        bar = make_colors(f"[{filled}{empty}] {i}%", color)
        print(f"\r  {bar}", end="")
        sys.stdout.flush()
        time.sleep(0.2)
    print()  # New line after progress bar
    
def run_all_tests():
    """Run all test functions"""
    print(make_colors("MAKE_COLORS MODULE TEST SUITE", "white", "blue"))
    print(make_colors("Testing all colors, shortcuts, and functionality", "lightblue"))
    
    test_functions = [
        test_color_support,
        test_standard_colors,
        test_light_colors,
        test_background_colors,
        test_color_shortcuts,
        test_separator_notation,
        test_force_parameter,
        test_mixed_parameters,
        test_aliases,
        test_error_conditions,
        test_real_world_examples
    ]
    
    for i, test_func in enumerate(test_functions, 1):
        try:
            test_func()
        except Exception as e:
            print(f"\n{make_colors(f'ERROR in {test_func.__name__}: {e}', 'white', 'red')}")
    
    print_separator("TEST SUITE COMPLETED", "=")
    print(make_colors("All tests completed! Check output above for results.", "lightgreen"))
    print(make_colors("If colors appear properly, your make_colors module is working!", "lightblue"))

if __name__ == "__main__":
    run_all_tests()