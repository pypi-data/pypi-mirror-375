from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from collections.abc import Iterable
from pathlib import Path
from tempfile import TemporaryDirectory

GIT_URL = "https://github.com/munificent/craftinginterpreters.git"
REMOTE_TESTS_DIR = "test"

RULES = {
    "add_line_numbers_static": {r"(//)( Error)": r"\1 [line {line_number}]\2"},
    "add_line_numbers_runtime": {r"(// expect runtime error:)": r"\1 [line {line_number}]"},
    "remove_prefix": {r"\[{prefix} (line \d+)]": r"[\1]"},
}

RESOURCES = {
    "ast-generator": "generate_ast.py",
    "ast-printer": "print_ast.py",
}


def download(destination: Path, url: str, remote_tests_dir: str, force: bool = False):
    """Clones a remote git repository and sparse-checks-out a specific directory."""
    if destination.exists() and not force:
        raise FileExistsError(f"Destination '{destination}' already exists..")

    if (git := shutil.which("git")) is None:
        raise FileNotFoundError("Error: Command 'git' not found.")

    print(f"Downloading tests to '{destination}'...")
    with TemporaryDirectory() as temp_dir:
        commands = [
            [git, "clone", "--no-checkout", "--depth=1", "--filter=blob:none", url, "."],
            ["git", "sparse-checkout", "set", "--no-cone", remote_tests_dir],
            [git, "checkout"],
        ]
        for cmd in commands:
            subprocess.run(
                cmd,
                cwd=temp_dir,
                check=True,
                capture_output=True,
                text=True,
            )

        if destination.exists():
            shutil.rmtree(destination)

        source = Path(temp_dir) / remote_tests_dir
        shutil.move(source, destination)


def process_file(path: Path, rules: Iterable[dict[re.Pattern, str]]):
    text = path.read_text()
    has_trailing_newline = text.endswith("\n")
    lines = text.splitlines()
    for nb, line in enumerate(lines, 1):
        for rule in rules:
            ((pattern, replacement),) = rule.items()
            line = re.sub(pattern, replacement.format(line_number=nb), line)
        lines[nb - 1] = line

    text = "\n".join(lines) + "\n" * has_trailing_newline
    path.write_text(text)


def update_prefix_rule(rules: dict[str, dict[str, str]], prefixes: list[str]):
    rule: dict[str, str] = rules.pop(key := "remove_prefix")
    for prefix in prefixes:
        ((pattern, replacement),) = rule.items()
        pattern = pattern.format(prefix=prefix)
        key = "_".join([key, prefix])
        rules[key] = {pattern: replacement}


def process_rules(rules: dict[str, dict[str, str]], add_ln: bool, prefixes: list[str]):
    if not add_ln:
        rules.pop("add_line_numbers_static")
        rules.pop("add_line_numbers_runtime")

    update_prefix_rule(rules, prefixes)

    return {
        name: {re.compile(pattern): replacement for pattern, replacement in rule.items()}
        for name, rule in rules.items()
    }


def process_directory(
    path: Path,
    rules: dict[str, dict[str, str]],
    add_ln: bool,
    prefixes: list[str],
):
    """Processes all .lox files in a directory."""
    print(f"Processing files in '{path}'...")
    paths = path.rglob("*.lox")
    active_rules = process_rules(rules, add_ln, prefixes)
    for path in paths:
        process_file(path, active_rules.values())
    print("Processing complete.")


def handle_setup(args: argparse.Namespace):
    download(args.directory, GIT_URL, REMOTE_TESTS_DIR, args.force)
    process_directory(path=args.directory, rules=RULES, add_ln=True, prefixes=["java"])


def handle_download(args: argparse.Namespace):
    download(
        args.directory,
        GIT_URL,
        REMOTE_TESTS_DIR,
        args.force,
    )


def handle_process(args: argparse.Namespace):
    process_directory(
        args.directory,
        RULES,
        args.add_line_numbers,
        args.prefix,
    )


def handle_run(args: argparse.Namespace, *unknown_args):
    cmd = ["pytest"]
    if args.pytest_help:
        subprocess.run(cmd + ["--help"])
        return
    if args.interpreter_cmd:
        cmd.extend(["--interpreter_cmd", args.interpreter_cmd])
    if args.skip_dirs:
        cmd.extend([item for dir in args.skip_dirs for item in ["--skip_dirs", dir]])

    cmd.extend(list(unknown_args))
    subprocess.run(cmd)


def handle_clean(args: argparse.Namespace):
    if not args.directory.is_dir():
        print(f"Directory not found: {args.directory}")
        return

    if not (force := args.force):
        response = input(f"Are you sure you want to permanently delete {args.directory}? [y/N] ")
        force = response.lower() == "y"

    if force:
        shutil.rmtree(args.directory)
        print(f"Successfully removed {args.directory}")
    else:
        print("Clean command cancelled.")


def handle_export(args: argparse.Namespace):
    project_root = Path(__file__).parent.parent.parent
    resource_path = project_root / "scripts" / RESOURCES[args.resource]
    destination_path = Path.cwd() / resource_path.name
    if destination_path.exists() and not args.force:
        print("File already exists. Use --force to overwrite.")
        return
    shutil.copy(resource_path, destination_path)
    print(f"Exported '{resource_path.name}' to current directory.")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "A toolkit for downloading and running the Crafting Interpreters Lox test suite."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    path_parser = argparse.ArgumentParser(add_help=False)
    path_parser.add_argument(
        "directory",
        type=Path,
        help="directory where the operation will be performed",
    )

    force_parser = argparse.ArgumentParser(add_help=False)
    force_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="overwrite destination directory if it exists",
    )

    parser_setup = subparsers.add_parser(
        "setup",
        parents=[path_parser, force_parser],
        help="download and process all tests in one step",
    )
    parser_setup.set_defaults(func=handle_setup)

    parser_download = subparsers.add_parser(
        "download",
        parents=[path_parser, force_parser],
        help="download the official Lox test suite",
    )
    parser_download.set_defaults(func=handle_download)

    parser_process = subparsers.add_parser(
        "process",
        parents=[path_parser],
        help="process an existing directory of Lox tests",
    )
    parser_process.add_argument(
        "-p",
        "--prefix",
        action="append",
        choices=["java", "c"],
        default=[],
        help="remove a specific language prefix",
    )
    parser_process.add_argument(
        "--no-ln",
        "--no-line-numbers",
        dest="add_line_numbers",
        action="store_false",
        help="do not add [line N] context to error comments",
    )
    parser_process.set_defaults(func=handle_process)

    parser_run = subparsers.add_parser(
        "run",
        help="run tests against a Lox interpreter",
    )
    parser_run.add_argument(
        "--pytest-help",
        action="store_true",
        help="display pytest's command-line help message and exit",
    )
    parser_run.add_argument(
        "-i",
        "--interpreter_cmd",
        type=str,
        help="the command to run the interpreter",
    )
    parser_run.add_argument(
        "-s",
        "--skip_dirs",
        action="append",
        type=str,
        help="skip tests within the specified subdirectory (e.g., benchmark);"
        " this can be specified multiple times",
    )
    parser_run.set_defaults(func=handle_run)

    parser_clean = subparsers.add_parser(
        "clean",
        parents=[path_parser, force_parser],
        help="remove a directory of downloaded tests",
    )
    parser_clean.set_defaults(func=handle_clean)

    parser_export = subparsers.add_parser(
        "export",
        parents=[force_parser],
        help="export a resource to the current directory",
    )
    parser_export.add_argument(
        "resource",
        choices=["ast-generator", "ast-printer"],
        default=[],
        help="choose the resource to export",
    )
    parser_export.set_defaults(func=handle_export)

    args, unknown_args = parser.parse_known_args()
    if args.command != "run" and unknown_args:
        parser.parse_args()
    args.func(args, *unknown_args)


if __name__ == "__main__":
    main()
