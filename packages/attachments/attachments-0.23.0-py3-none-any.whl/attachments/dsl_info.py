"""
DSL Introspection Tool (AST-based)
===================================

This module provides advanced tools for discovering and documenting all
available DSL (Domain-Specific Language) commands within the attachments library.

It works by parsing the Abstract Syntax Tree (AST) of all registered functions
to statically analyze how the `commands` dictionary is used. This provides a
much more accurate and detailed view than simple regex matching.
"""

import ast
import inspect
from collections.abc import Callable
from typing import Any


def _get_str_from_node(node: ast.AST) -> str | None:
    """Helper to safely get a string value from an ast.Str or ast.Constant node."""
    if isinstance(node, ast.Str):
        return node.s  # Deprecated in Python 3.8+
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _get_value_from_node(node: ast.AST) -> Any:
    """Helper to safely get any value from ast.Constant node."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Str):
        return node.s
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.NameConstant):
        return node.value
    return None


def _describe_type_from_node(node: ast.AST) -> str:
    """Infer type description from AST node."""
    if isinstance(node, (ast.Str, ast.Constant)) and isinstance(
        getattr(node, "value", getattr(node, "s", None)), str
    ):
        return "string"
    if isinstance(node, (ast.Num, ast.Constant)) and isinstance(
        getattr(node, "value", getattr(node, "n", None)), int
    ):
        return "integer"
    if isinstance(node, (ast.Num, ast.Constant)) and isinstance(
        getattr(node, "value", getattr(node, "n", None)), float
    ):
        return "float"
    if isinstance(node, (ast.NameConstant, ast.Constant)) and isinstance(
        getattr(node, "value", None), bool
    ):
        return "boolean"
    if isinstance(node, ast.List):
        return "list"
    if isinstance(node, ast.Dict):
        return "dict"
    return "unknown"


class DslCommandVisitor(ast.NodeVisitor):
    """
    An AST visitor that walks the code to find all usages of DSL commands.
    It looks for access patterns like `var.commands['key']` or `var.commands.get('key')`.
    """

    def __init__(self, context_name: str, context_type: str, func: Callable):
        self.found_commands: dict[str, dict[str, Any]] = {}
        self.context_name = context_name
        self.context_type = context_type
        self.func = func

    def add_command(
        self, command: str, node: ast.AST, default_value: Any = None, inferred_type: str = None
    ):
        """Adds a discovered command to the results."""
        if command not in self.found_commands:
            self.found_commands[command] = {
                "used_in": self.context_name,
                "type": self.context_type,
                "docstring": self.func.__doc__ or "No docstring.",
                "source_file": inspect.getfile(self.func),
                "source_line": node.lineno,
                "default_value": default_value,
                "inferred_type": inferred_type or "unknown",
                "allowable_values": self._extract_allowable_values(command),
                "description": self._extract_command_description(command),
            }

    def _extract_allowable_values(self, command: str) -> list[str]:
        """Extract allowable values for a command from docstring or code patterns."""
        docstring = self.func.__doc__ or ""
        allowable = []

        # Look for patterns like "Positions: value1, value2, value3"
        import re

        # Pattern for explicit value lists in docstrings
        patterns = [
            rf"{command}[:\s]+([^.\n]+)",  # "command: value1, value2"
            r"Options[:\s]+([^.\n]+)",  # "Options: value1, value2"
            r"Valid[:\s]+([^.\n]+)",  # "Valid: value1, value2"
            r"Allowed[:\s]+([^.\n]+)",  # "Allowed: value1, value2"
        ]

        for pattern in patterns:
            match = re.search(pattern, docstring, re.IGNORECASE)
            if match:
                values_str = match.group(1)
                # Split by comma
                raw_values = [v.strip() for v in values_str.split(",")]

                cleaned_values = []
                for v_raw in raw_values:
                    v = v_raw  # Start with the raw value for this iteration

                    # 1. Remove content within balanced parentheses first
                    v_no_balanced_paren = re.sub(r"\s*\([^)]*\)\s*", "", v).strip()

                    # 2. If an opening parenthesis exists and v was unchanged by balanced paren removal
                    #    (e.g., "val (unclosed" or "val (explanation, with comma)"),
                    #    split at the first '(' and take the part before it.
                    if "(" in v and v_no_balanced_paren == v:
                        v = v.split("(", 1)[0].strip()
                    else:
                        # Otherwise, use the result of balanced paren removal
                        v = v_no_balanced_paren

                    # 3. Remove common trailing explanations (e.g., " - ...", " = ...", " for ...")
                    v = re.sub(r"\s*-\s*.*$", "", v).strip()
                    v = re.sub(r"\s*=\s*.*$", "", v).strip()  # Handles "value = explanation"
                    v = re.sub(r"\s+for\s+.*$", "", v).strip()
                    v = re.sub(r"\s+to\s+.*$", "", v).strip()

                    # 4. Clean extraneous characters (e.g., trailing brackets from "[value]")
                    v = v.strip("[]")

                    # 5. Remove potential command context like "command:value" -> "value"
                    if ":" in v:
                        parts = v.split(":", 1)
                        if len(parts) > 1 and parts[0].lower() == command.lower():
                            v = parts[1].strip()

                    # 6. Final cleanup of any remaining brackets if value is simple (no spaces, other brackets, colons)
                    if not any(c in v for c in [" ", "(", ")", ":"]):
                        v = v.strip("[]{}()")

                    # 7. Skip words that look like explanations or are too short/generic
                    exclusion_keywords = [
                        "default",
                        "affects",
                        "size",
                        "and",
                        "e.g.",
                        "etc",
                        "example",
                    ]
                    if (
                        v
                        and not any(word in v.lower() for word in exclusion_keywords)
                        and len(v) > 0
                    ):
                        if v not in ["[]", "{}"]:  # Skip empty list/dict artifacts
                            cleaned_values.append(v)

                if cleaned_values:
                    # Remove duplicates while preserving order
                    seen = set()
                    unique_cleaned_values = [
                        x for x in cleaned_values if not (x in seen or seen.add(x))
                    ]
                    allowable.extend(unique_cleaned_values)
                    # Do not break here yet, let the fallback logic after the loop handle overrides.
                    # allowable.extend(unique_cleaned_values) # Values are extended, not reset
                    # break # We don't break, to allow multiple patterns to contribute if necessary.

        # --- New Fallback/Override Logic (Iteration 4 - Part B) ---

        # Make sure `allowable` contains unique values gathered so far if any pattern matched.
        if allowable:
            seen = set()
            allowable = [x for x in allowable if not (x in seen or seen.add(x))]

        # Check quality of initially parsed values for typical boolean commands
        is_poor_quality_for_boolean = False
        typical_boolean_cmds = [
            "files",
            "images",
            "head",
            "summary",
            "fullpage",
            "recursive",
            "force",
            "dirs_only_with_files",
        ]
        if command in typical_boolean_cmds and allowable:  # only check if we found something
            # If any extracted value (not 'true' or 'false') for these commands still contains typical explanation markers
            if any(
                ("=" in val or "[" in val or "]" in val or ":" in val or "(" in val or ")" in val)
                for val in allowable
                if val.lower() not in ["true", "false"]
            ):
                is_poor_quality_for_boolean = True

        # If quality is poor for a boolean command, or if nothing was found for it, set to true/false.
        if command in typical_boolean_cmds and (is_poor_quality_for_boolean or not allowable):
            allowable = ["true", "false"]

        # Format command (specific list, should override if command is 'format')
        # This is 'if', not 'elif', so it can potentially override a 'true,false' if command is 'format'
        if command == "format":
            base_formats = [
                "plain",
                "text",
                "txt",
                "markdown",
                "md",
                "html",
                "code",
                "xml",
                "csv",
                "structured",
            ]
            # If allowable is empty, or contains values not in base_formats (e.g. true/false from above rule)
            # or if it's just generally messy and doesn't look like format values.
            current_is_valid_format_subset = False
            if allowable:  # Check if current allowable values are a valid subset of base_formats
                current_is_valid_format_subset = all(val in base_formats for val in allowable)

            if not allowable or not current_is_valid_format_subset:
                allowable = base_formats  # Override with standard formats
            # No complex merge needed here; if it's 'format', it should be these values.
            # If specific docstring parsing yielded a subset of these, that's fine, but if it yielded
            # 'true','false', this override fixes it.

        # Position/Watermark (specific list) - only if nothing specific was parsed by the main loop
        elif command in ["watermark"] or "position" in command.lower():
            if not allowable:  # Only if the main parsing loop found nothing suitable
                position_keywords = [
                    "bottom-right",
                    "bottom-left",
                    "top-right",
                    "top-left",
                    "center",
                ]
                # Check if docstring mentions any position keyword, then use full list.
                if any(kw in docstring for kw in position_keywords):
                    allowable = position_keywords

        # Final filter for any empty strings and ensure uniqueness again after overrides
        final_allowable = []
        seen_final = set()
        for val in allowable:
            if val and not (val in seen_final or seen_final.add(val)):
                final_allowable.append(val)

        return final_allowable

    def _extract_command_description(self, command: str) -> str:
        """Extract description for a command from docstring."""
        docstring = self.func.__doc__ or ""

        # Look for DSL command documentation patterns
        import re

        # Pattern for "- [command:...] - description"
        pattern = rf"[•\-\*]\s*\[{re.escape(command)}[:\]]([^-\n]*)-\s*([^\n]+)"
        match = re.search(pattern, docstring, re.IGNORECASE)
        if match:
            return match.group(2).strip()

        # Pattern for DSL: [command:description]
        pattern = rf"DSL[:\s]*.*\[{re.escape(command)}[:\s]*([^\]]+)\]"
        match = re.search(pattern, docstring, re.IGNORECASE)
        if match:
            desc = match.group(1).strip()
            # Clean up common patterns
            desc = re.sub(r"\[.*?\]", "", desc)  # Remove nested [examples]
            desc = re.sub(r"[=\|].*$", "", desc)  # Remove = explanations
            return desc.strip()

        # Pattern for "command description" in parentheses or after comma
        pattern = rf"{re.escape(command)}[:\s]*([^,\(\)\[\]]+)"
        match = re.search(pattern, docstring, re.IGNORECASE)
        if match:
            desc = match.group(1).strip()
            # Skip if it looks like code or has special chars
            if not any(char in desc for char in ["(", ")", "[", "]", "=", "|"]) and len(desc) < 50:
                return desc

        return ""

    def visit_Subscript(self, node: ast.Subscript):
        """Detects usage like: var.commands['...']"""
        if (
            isinstance(node.value, ast.Attribute)
            and node.value.attr == "commands"
            and isinstance(node.slice, ast.Index)
        ):
            command = _get_str_from_node(node.slice.value)
            if command:
                self.add_command(command, node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Detects usage like: var.commands.get('...', default)"""
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and isinstance(node.func.value, ast.Attribute)
            and node.func.value.attr == "commands"
        ):
            if node.args:
                command = _get_str_from_node(node.args[0])
                if command:
                    # Extract default value if present
                    default_value = None
                    inferred_type = None
                    if len(node.args) > 1:
                        default_value = _get_value_from_node(node.args[1])
                        inferred_type = _describe_type_from_node(node.args[1])
                    self.add_command(command, node, default_value, inferred_type)

        # Also look for int(), float(), .lower() patterns to infer types
        if (
            isinstance(node.func, ast.Name)
            and node.func.id in ["int", "float", "bool", "str"]
            and len(node.args) == 1
        ):
            # Check if the argument is a commands.get() call
            arg = node.args[0]
            if (
                isinstance(arg, ast.Call)
                and isinstance(arg.func, ast.Attribute)
                and arg.func.attr == "get"
                and isinstance(arg.func.value, ast.Attribute)
                and arg.func.value.attr == "commands"
            ):
                if arg.args:
                    command = _get_str_from_node(arg.args[0])
                    if command:
                        default_value = None
                        if len(arg.args) > 1:
                            default_value = _get_value_from_node(arg.args[1])

                        inferred_type = node.func.id  # int, float, bool, str
                        self.add_command(command, node, default_value, inferred_type)

        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare):
        """Detects usage like: '...' in var.commands"""
        # Check for '<string>' in var.commands
        if len(node.ops) == 1 and isinstance(node.ops[0], ast.In):
            comparator = node.comparators[0]
            if isinstance(comparator, ast.Attribute) and comparator.attr == "commands":
                command = _get_str_from_node(node.left)
                if command:
                    self.add_command(command, node)
        self.generic_visit(node)


def _find_commands_in_function(
    func: Callable, context_name: str, context_type: str
) -> dict[str, dict[str, Any]]:
    """Helper to inspect a single function for DSL command usage using AST."""
    try:
        # We need to unwrap decorators to get to the original source code
        source = inspect.getsource(inspect.unwrap(func))
        tree = ast.parse(source)
        visitor = DslCommandVisitor(context_name, context_type, func)
        visitor.visit(tree)
        return visitor.found_commands
    except (TypeError, OSError, IndentationError):
        # Ignore errors for built-ins or functions we can't get source for.
        return {}


def get_dsl_info() -> dict[str, list[dict[str, Any]]]:
    """
    Scans the library to find all available DSL commands and their contexts.
    """
    dsl_map: dict[str, list[dict[str, Any]]] = {}

    from . import highest_level_api
    from .core import _adapters, _loaders, _modifiers, _presenters, _refiners, _splitters
    from .pipelines import _processor_registry

    registries = {
        "loader": _loaders,
        "modifier": _modifiers,
        "presenter": _presenters,
        "refiner": _refiners,
        "splitter": _splitters,
        "adapter": _adapters,
    }

    def add_to_map(command, context):
        if command not in dsl_map:
            dsl_map[command] = []
        # Avoid adding duplicate contexts
        if context not in dsl_map[command]:
            dsl_map[command].append(context)

    # Scan all verb registries
    for verb_type, registry in registries.items():
        for name, funcs in registry.items():
            # funcs can be a list of handlers, a single handler func, or a tuple (for loaders)
            if isinstance(funcs, list):
                handler_list = funcs
            else:
                handler_list = [funcs]  # a list with a single func or a single tuple

            for handler_item in handler_list:
                # The item can be a tuple (type_hint/match_fn, func) or just the function itself
                if isinstance(handler_item, tuple):
                    func = handler_item[1]
                else:
                    func = handler_item

                context_name = f"{verb_type}.{name}"
                commands = _find_commands_in_function(func, context_name, verb_type)
                for cmd, ctx in commands.items():
                    add_to_map(cmd, ctx)

    # Scan all registered processors
    for proc_info in _processor_registry._processors:
        func = proc_info.original_fn
        context_name = f"processor.{proc_info.name}"
        commands = _find_commands_in_function(func, context_name, "processor")
        for cmd, ctx in commands.items():
            add_to_map(cmd, ctx)

    # Scan the high-level Attachments API
    api_contexts = [
        (highest_level_api.Attachments._process_files, "Attachments._process_files", "api"),
        (highest_level_api._get_smart_text_presenter, "_get_smart_text_presenter", "api"),
    ]
    for func, name, type in api_contexts:
        commands = _find_commands_in_function(func, name, type)
        for cmd, ctx in commands.items():
            add_to_map(cmd, ctx)

    # Sort the contexts for each command for consistent output
    for contexts in dsl_map.values():
        contexts.sort(key=lambda x: x["used_in"])

    return dsl_map


if __name__ == "__main__":
    import json

    print("Discovering all DSL commands via AST analysis...")
    dsl_info = get_dsl_info()

    print("\\nFound the following DSL commands:")
    print(json.dumps(dsl_info, indent=2, default=str))
