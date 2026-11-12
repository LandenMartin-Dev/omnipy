from src.app import Interpret
from src.shell import init

import os
import sys



_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)



def findPath(arg: str) -> str:
    if os.path.isabs(arg):
        return arg

    if os.path.exists(arg):
        return os.path.abspath(arg)

    beside: str = os.path.join(_SCRIPT_DIR, arg)
    if os.path.exists(beside):
        return beside

    return arg



def main() -> None:
    if len(sys.argv) > 1: arg = sys.argv[1]
    else:
        init()

    scriptPath: str = findPath(arg)
    if not os.path.exists(scriptPath):
        print(f"Error: {scriptPath} not found.")
        sys.exit(1)

    with open(scriptPath, "r") as file:
        script: str = str(file.read())

    for lineno, raw in enumerate(script.split("\n"), start=1):
        line = raw.strip()
        if not line:
            continue

        Interpret.run(line.split(), lineno)


if __name__ == "__main__":
    main()