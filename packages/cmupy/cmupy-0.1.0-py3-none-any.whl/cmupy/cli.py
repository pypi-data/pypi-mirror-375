"""
Command Line Interface for cmupy.
"""

import argparse
import sys
from typing import List, Optional

from .core import *


def main(args: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="cmupy - Computational Mathematics Utilities for Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cmupy hello
  cmupy add 5 3
  cmupy factorial 5
  cmupy is-prime 17
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Hello command
    hello_parser = subparsers.add_parser("hello", help="Print hello message")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add two numbers")
    add_parser.add_argument("a", type=float, help="First number")
    add_parser.add_argument("b", type=float, help="Second number")
    
    # Factorial command
    factorial_parser = subparsers.add_parser("factorial", help="Calculate factorial")
    factorial_parser.add_argument("n", type=int, help="Number to calculate factorial for")
    
    # Is-prime command
    prime_parser = subparsers.add_parser("is-prime", help="Check if number is prime")
    prime_parser.add_argument("n", type=int, help="Number to check")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version")
    
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 1
    
    try:
        if parsed_args.command == "hello":
            print(hello_world())
        
        elif parsed_args.command == "add":
            result = add_numbers(parsed_args.a, parsed_args.b)
            print(f"{parsed_args.a} + {parsed_args.b} = {result}")
        
        elif parsed_args.command == "factorial":
            result = factorial(parsed_args.n)
            print(f"{parsed_args.n}! = {result}")
        
        elif parsed_args.command == "is-prime":
            result = is_prime(parsed_args.n)
            status = "prime" if result else "not prime"
            print(f"{parsed_args.n} is {status}")
        
        elif parsed_args.command == "version":
            from . import __version__
            print(f"cmupy version {__version__}")
        
        return 0
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())