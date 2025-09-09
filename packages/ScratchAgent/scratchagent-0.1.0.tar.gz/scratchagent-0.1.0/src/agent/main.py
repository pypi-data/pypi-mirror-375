"""
ScratchAgent main module.

This module contains the core functionality of the ScratchAgent framework.
"""

def greet(name):
    """
    Generate a greeting message.
    
    Args:
        name (str): The name to greet.
        
    Returns:
        str: A greeting message.
    """
    return f"Hello, {name}!"


def main():
    """
    Main entry point for the command line interface.
    """
    print("Welcome to ScratchAgent!")
    print("Version: 0.1.0")
    print(greet("ScratchAgent User"))
    print("\nFor more information, visit: https://github.com/AbQaadir/ScratchAgent")


if __name__ == "__main__":
    main() 