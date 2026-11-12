import sys


shell_mode: bool = False
variables: list = []


class Utils:
    @staticmethod
    def exit(msg: str, line: int) -> None:
        if shell_mode:
            print(f"Error @ line {line}:")
            print(f"  {msg}")
        else:
            print(msg)


    @staticmethod
    def getVar(name: str) -> str:
        for item in variables:
            if item.get("var") == name:
                return item.get("val")

        return None


    @staticmethod
    def resolveValue(value: str) -> str:
        value = value.strip()
        if value.startswith("="):
            value = value[1:].strip()

        if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
            return value[1:-1]

        for item in variables:
            if item.get("var") == value:
                return item.get("val")

        return value


    @staticmethod
    def setVar(name: str, value: str) -> bool:
        for item in variables:
            if item.get("var") == name:
                item["val"] = value
                return True

        return False


    @staticmethod
    def unquote(value: str) -> str:
        if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
            return value[1:-1]

        return value



class Interpret:
    def __init__(self, chunks: list, line: int) -> None:
        self.chunks = chunks
        self.line = line


    @staticmethod
    def qprintf(chunks: list, line: int) -> None:
        if len(chunks) < 2:
            Utils.exit(
                "Invalid syntax: `qprintf` requires at least one argument",
                line
            )
            return  # unreachable, but defensive


        value = " ".join(chunks[1:])
        if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
            print(value[1:-1])
            return

        if len(chunks) == 2 and any(item.get("var") == chunks[1] for item in variables):
            print(Utils.getVar(chunks[1]))
            return

        if len(chunks) > 2:
            print(value)
            return

        Utils.exit(
            f"Invalid syntax: unknown object `{chunks[1]}`. ",
            line
        )


    @staticmethod
    def let(chunks: list, line: int) -> None:
        if len(chunks) < 2:
            Utils.exit(
                "Invalid syntax: `let` requires a variable name",
                line,
            )
            return

        varName: str = chunks[1]
        if varName == "":
            Utils.exit("Invalid Name: variable name cannot be empty.", line, shell_mode)
            return

        if "`" in varName:
            Utils.exit(
                f"Invalid Name: variable name `{varName}` cannot contain backticks.",
                line,
            )
            return

        if "=" in varName:
            Utils.exit(
                f"Invalid Name: variable name `{varName}` cannot contain `=`. ",
                line,
            )
            return

        if varName.startswith("/"):
            Utils.exit(
                f"Invalid Name: `{varName}` cannot start with `/` (reserved for comments).",
                line,
            )
            return

        if varName in ("qprintf", "let", "set"):
            Utils.exit(
                f"Invalid Name: `{varName}` is a reserved keyword and cannot be used as a variable name.",
                line,
            )
            return

        if any(item.get("var") == varName for item in variables):
            Utils.exit(f"Invalid Name: variable `{varName}` is already defined.", line)
            return

        if len(chunks) == 2:
            variables.append({"var": varName, "val": ""})
            return

        varVal: str = " ".join(chunks[2:]).strip()
        if varVal == "":
            Utils.exit(
                f"Invalid syntax: no value provided for variable `{varName}`.",
                line,
            )
            return

        resolved: str = Utils.resolveValue(varVal)
        is_quoted_empty = len(varVal) >= 2 and varVal.startswith("`") and varVal.endswith("`")
        if resolved == "" and not is_quoted_empty:
            Utils.exit(
                f"Invalid syntax: value for variable `{varName}` resolved to an empty string. ",
                line,
            )
            return

        variables.append({"var": varName, "val": resolved})


    @staticmethod
    def sets(chunks: list, line: int) -> None:
        if len(chunks) < 2:
            Utils.exit(
                "Invalid syntax: `set` requires a variable name",
                line,
            )
            return

        varName: str = chunks[1]
        if varName == "":
            Utils.exit("Invalid Name: variable name cannot be empty.", line)
            return

        if not any(item.get("var") == varName for item in variables):
            Utils.exit(
                f"Var `{varName}` is not defined! Use `let {varName} = ...` before assigning it.",
                line,
            )
            return

        varVal: str = " ".join(chunks[2:]).strip()
        if varVal == "":
            Utils.exit(
                f"Invalid syntax: no value provided for variable `{varName}`.",
                line,
            )
            return

        resolved: str = Utils.resolveValue(varVal)
        is_quoted_empty = len(varVal) >= 2 and varVal.startswith("`") and varVal.endswith("`")
        if resolved == "" and not is_quoted_empty:
            Utils.exit(
                f"Invalid syntax: value for variable `{varName}` resolved to an empty string. ",
                line,
            )
            return

        Utils.setVar(varName, resolved)


    @staticmethod
    def run(chunks: list, line: int, isShell: bool = False) -> None:
        shell_mode = isShell
        for index, chunk in enumerate(chunks):
            if not isinstance(chunk, str):
                Utils.exit(
                    f"Invalid syntax: expected a string token at index {index}, ",
                    f"got `{type(chunk).__name__}`.",
                    line,
                )
                return
            if chunk.startswith("/:"):
                chunks = chunks[:index]
                break

        if not chunks:
            return

        base: str = chunks[0]
        if base == "":
            Utils.exit("Invalid syntax: empty command.", line, shell_mode)
            return

        if base == "qprintf":
            Interpret.qprintf(chunks, line)
        elif base == "let":
            Interpret.let(chunks, line)
        elif base == "set":
            Interpret.sets(chunks, line)
        else:
            Utils.exit(
                f"Unknown attribute `{base}`. Available attributes: `qprintf`, `let`, `set`.",
                line,
            )