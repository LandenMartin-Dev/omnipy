from src.app import Interpret
from sys import exit

import sys



def init() -> None:
    print("Welcome to omnipy shell (exit to exit)")
    while True:
        try:
            main()

        except KeyboardInterrupt:
            print()
            sys.exit(0)



def main() -> None:
    command: str = input(">>> ")
    if command.lower() == "exit":
        sys.exit(0)

    Interpret.run(command.split(), 0, isShell=True)