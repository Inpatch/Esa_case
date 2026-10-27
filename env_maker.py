#!/usr/bin/env python3
"""Create a .env file from a predefined set of typed variables.

Edit VARIABLES below, then run the script and answer the prompts.
Supported types: str, int, float, bool, secret (input is hidden).
A default is optional; press Enter to accept it.
"""
import getpass
import re
from pathlib import Path

OUTPUT_FILE = ".env"

# (name, type, default)  -> use None for "no default / required"
VARIABLES = [
    ("HOST", "str", "my-app"),
    ("PORT", "int", "development"),
    ("USERNAME", "str", None),
    ("PASSWORD", "str", None),
    ("DATABASE", "str", "MBADDD_ESA"),
    ("API_KEY", "secret", None),
]



def parse(raw: str, type_: str):
    """Convert raw input to the given type, raising ValueError if invalid."""
    if type_ in ("str", "secret"):
        return raw
    if type_ == "int":
        return int(raw)
    if type_ == "float":
        return float(raw)
    if type_ == "bool":
        lowered = raw.strip().lower()
        if lowered in ("y", "yes", "true", "t", "1"):
            return True
        if lowered in ("n", "no", "false", "f", "0"):
            return False
        raise ValueError("enter yes/no or true/false")
    raise ValueError(f"unknown type '{type_}'")


def to_text(value, type_: str) -> str:
    if type_ == "bool":
        return "true" if value else "false"
    return str(value)


def quote(value: str) -> str:
    """Wrap the value in double quotes only when needed."""
    if value == "" or re.search(r'[\s#"\'\\$`]', value):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def ask(name: str, type_: str, default):
    hint = f"{type_}"
    if default is not None and type_ != "secret":
        hint += f", default: {to_text(default, type_)}"
    elif default is not None:
        hint += ", default set"
    prompt = f"{name} ({hint}): "

    while True:
        raw = getpass.getpass(prompt) if type_ == "secret" else input(prompt)
        if raw == "":
            if default is not None:
                return default
            print("  A value is required.")
            continue
        try:
            return parse(raw, type_)
        except ValueError as err:
            print(f"  Invalid {type_}: {err}")


def main():
    out = Path(OUTPUT_FILE)
    if out.exists():
        answer = input(f"{out} already exists. Overwrite? [y/N]: ").strip().lower()
        if answer != "y":
            print("Cancelled.")
            return

    lines = []
    for name, type_, default in VARIABLES:
        value = ask(name, type_, default)
        lines.append(f"{name}={quote(to_text(value, type_))}\n")

    out.write_text("".join(lines))
    print(f"\nWrote {len(lines)} variable(s) to {out}")


if __name__ == "__main__":
    main()