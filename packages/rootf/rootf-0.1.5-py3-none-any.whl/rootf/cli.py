import argparse
import sys
import platform
import os
from .system_info import get_distro, get_ascii_art, get_system_info
from .config import load_config, get_config_path
from .ascii_art import ASCII_ART

def print_colored(text, color, enable_colors=True):
    if not enable_colors:
        return text
    colors = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "reset": "\033[0m"
    }
    return f"{colors[color]}{text}{colors['reset']}"

def main():
    parser = argparse.ArgumentParser(description="System information tool")
    parser.add_argument("--distro", help="Specify distro for ASCII art")
    parser.add_argument("--list-distros", action="store_true", help="List available distros")
    parser.add_argument("--no-art", action="store_true", help="Disable ASCII art")
    parser.add_argument("--public-ip", action="store_true", help="Show public IP")
    parser.add_argument("--colors", action="store_true", help="Enable colored output")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--minimal", action="store_true", help="Minimal output")
    parser.add_argument("--stdout", action="store_true", help="Force plain stdout output (no formatting)")
    parser.add_argument("--version", action="store_true", help="Show version")
    parser.add_argument("--config", action="store_true", help="Show config path")
    
    args = parser.parse_args()
    
    if args.version:
        from . import __version__
        print(f"root {__version__}")
        sys.exit(0)
    
    if args.config:
        print(get_config_path())
        sys.exit(0)
    
    if args.list_distros:
        print("\n".join(sorted(ASCII_ART.keys())))
        sys.exit(0)
    
    config = load_config()
    distro = args.distro or config.get("default_distro", "auto")
    use_colors = args.colors or config.get("colors", True)
    if args.no_color:
        use_colors = False
    minimal = args.minimal or config.get("minimal", False)
    show_public_ip = args.public_ip or config.get("public_ip", False)
    
    is_termux = platform.system() == "Linux" and os.path.exists("/system/build.prop")
    
    if distro == "auto":
        distro = get_distro()
    
    ascii_art = get_ascii_art(distro) if not args.no_art else ""
    info = get_system_info(show_public_ip)
    
    if minimal or args.stdout:
        for key, value in info.items():
            if is_termux and value == "unknown":
                continue
            print(f"{key.replace('_', ' ').title()}: {value}")
        return
    
    filtered_info = {
        key: value for key, value in info.items()
        if not (is_termux and value == "unknown")
    }
    info_lines = [
        f"{key.replace('_', ' ').title()}: {value}" for key, value in filtered_info.items()
    ]
    
    art_lines = ascii_art.splitlines()
    max_art_lines = len(art_lines)
    max_info_lines = len(info_lines)
    max_lines = max(max_art_lines, max_info_lines)
    
    art_lines += [""] * (max_lines - max_art_lines)
    info_lines += [""] * (max_lines - max_info_lines)
    
    for art, info_line in zip(art_lines, info_lines):
        art = art.ljust(20)
        if use_colors:
            art = print_colored(art, "blue", use_colors)
            if info_line:
                key, value = info_line.split(": ", 1)
                info_line = f"{print_colored(key, 'yellow', use_colors)}: {value}"
        print(f"{art}  {info_line}")