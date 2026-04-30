#!/usr/bin/env python3
"""
ChromaCode Interpreter v1.0
A programming language where colors represent logic.

Color Roles:
  BLUE   - variables / data
  GREEN  - functions / output
  YELLOW - conditions (if/elif/else)
  PURPLE - loops / repetition
  RED    - stop / end block
"""

import sys
import re
import math

# ─────────────────────────────────────────────
#  LEXER
# ─────────────────────────────────────────────

VALID_COLORS = {"BLUE", "GREEN", "YELLOW", "PURPLE", "RED"}

class ChromaToken:
    def __init__(self, color, text, lineno):
        self.color = color   # e.g. "BLUE"
        self.text = text     # rest of the line after the color tag
        self.lineno = lineno

    def __repr__(self):
        return f"[{self.color}] {self.text!r} (line {self.lineno})"


class ColorTypeError(Exception):
    def __init__(self, color, expected, lineno):
        super().__init__(
            f"ColorTypeError on line {lineno}: "
            f"color {color} cannot be used for '{expected}'. "
            f"Expected color role: {_color_role(color)}"
        )

def _color_role(color):
    roles = {
        "BLUE":   "variable assignment / data",
        "GREEN":  "function definition / print / return",
        "YELLOW": "condition (if/elif/else)",
        "PURPLE": "loop (for/while)",
        "RED":    "end block / stop",
    }
    return roles.get(color, "unknown")


def lex(source: str) -> list[ChromaToken]:
    """Tokenize source into ChromaTokens."""
    tokens = []
    for lineno, raw_line in enumerate(source.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("//"):
            continue  # skip blank lines and comments
        # Remove inline comments
        line = re.sub(r'\s*//.*$', '', line).strip()
        if not line:
            continue

        # Split on first whitespace to get color tag
        parts = line.split(None, 1)
        color = parts[0].upper()
        rest = parts[1].strip() if len(parts) > 1 else ""

        if color not in VALID_COLORS:
            raise SyntaxError(f"Line {lineno}: Unknown color tag '{parts[0]}'. "
                              f"Valid tags: {', '.join(VALID_COLORS)}")

        tokens.append(ChromaToken(color, rest, lineno))
    return tokens


# ─────────────────────────────────────────────
#  PARSER — builds an AST from tokens
# ─────────────────────────────────────────────

class Node:
    pass

class AssignNode(Node):
    def __init__(self, name, expr, lineno):
        self.name = name; self.expr = expr; self.lineno = lineno

class PrintNode(Node):
    def __init__(self, expr, lineno):
        self.expr = expr; self.lineno = lineno

class FuncDefNode(Node):
    def __init__(self, name, params, body, lineno):
        self.name = name; self.params = params
        self.body = body; self.lineno = lineno

class ReturnNode(Node):
    def __init__(self, expr, lineno):
        self.expr = expr; self.lineno = lineno

class IfNode(Node):
    def __init__(self, branches, else_body, lineno):
        # branches: list of (condition_expr, body)
        self.branches = branches
        self.else_body = else_body
        self.lineno = lineno

class ForNode(Node):
    def __init__(self, var, start, end, body, lineno):
        self.var = var; self.start = start; self.end = end
        self.body = body; self.lineno = lineno

class WhileNode(Node):
    def __init__(self, condition, body, lineno):
        self.condition = condition; self.body = body; self.lineno = lineno

class ExprNode(Node):
    """Raw expression string — evaluated by Python eval."""
    def __init__(self, expr, lineno):
        self.expr = expr; self.lineno = lineno

class FuncCallNode(Node):
    def __init__(self, expr, lineno):
        self.expr = expr; self.lineno = lineno


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse(self):
        return self._parse_block(top_level=True)

    def _parse_block(self, top_level=False, if_body=False):
        nodes = []
        while self.pos < len(self.tokens):
            tok = self.peek()
            # RED ends a block
            if tok.color == "RED":
                if top_level:
                    self.consume()
                break
            # YELLOW elif/else ends a sub-block (let _parse_yellow handle them)
            if tok.color == "YELLOW" and (
                tok.text.startswith("elif ") or
                tok.text in ("else", "else:")
            ):
                break
            # When parsing an if/elif/else body, stop at PURPLE (loops) or new YELLOW if
            # so loops aren't accidentally captured inside an if branch
            if if_body and tok.color in ("PURPLE",):
                break
            if if_body and tok.color == "YELLOW" and tok.text.startswith("if "):
                break
            nodes.append(self._parse_statement())
        return nodes

    def _parse_statement(self):
        tok = self.peek()
        color = tok.color
        text = tok.text
        lineno = tok.lineno

        if color == "BLUE":
            self.consume()
            return self._parse_blue(text, lineno)
        elif color == "GREEN":
            self.consume()
            return self._parse_green(text, lineno)
        elif color == "YELLOW":
            return self._parse_yellow()
        elif color == "PURPLE":
            self.consume()
            return self._parse_purple(text, lineno)
        elif color == "RED":
            self.consume()
            return None  # end sentinel
        else:
            self.consume()
            raise SyntaxError(f"Line {lineno}: Unexpected token {tok}")

    def _parse_blue(self, text, lineno):
        """BLUE: variable assignment — e.g. 'x = 42' or 'name = "World"'"""
        if "=" not in text:
            raise ColorTypeError("BLUE", text, lineno)
        lhs, _, rhs = text.partition("=")
        return AssignNode(lhs.strip(), rhs.strip(), lineno)

    def _parse_green(self, text, lineno):
        """GREEN: print, func def, return, or function call."""
        if text.startswith("print(") or text.startswith("print ("):
            inner = re.match(r'print\s*\((.+)\)', text)
            if inner:
                return PrintNode(inner.group(1).strip(), lineno)
            raise SyntaxError(f"Line {lineno}: Malformed print statement: {text!r}")
        elif text.startswith("func "):
            # func name(params) — body follows until RED end
            m = re.match(r'func\s+(\w+)\s*\(([^)]*)\)', text)
            if not m:
                raise SyntaxError(f"Line {lineno}: Malformed func definition: {text!r}")
            name = m.group(1)
            params = [p.strip() for p in m.group(2).split(",") if p.strip()]
            body = self._parse_block()
            # consume RED end
            if self.peek() and self.peek().color == "RED":
                self.consume()
            return FuncDefNode(name, params, body, lineno)
        elif text.startswith("return ") or text == "return":
            expr = text[7:].strip() if text.startswith("return ") else ""
            return ReturnNode(expr, lineno)
        elif re.match(r'\w+\s*\(', text):
            # function call as a statement
            return FuncCallNode(text, lineno)
        else:
            raise ColorTypeError("GREEN", text, lineno)

    def _parse_yellow(self):
        """YELLOW: if / elif / else chain."""
        branches = []
        else_body = None
        lineno = self.peek().lineno

        while self.peek() and self.peek().color == "YELLOW":
            tok = self.consume()
            text = tok.text.strip()

            if text.startswith("if "):
                cond = text[3:].rstrip(":")
                body = self._parse_block(if_body=True)
                branches.append((cond, body))
            elif text.startswith("elif "):
                cond = text[5:].rstrip(":")
                body = self._parse_block(if_body=True)
                branches.append((cond, body))
            elif text == "else" or text == "else:":
                body = self._parse_block(if_body=True)
                else_body = body
                break
            else:
                raise ColorTypeError("YELLOW", text, tok.lineno)

        return IfNode(branches, else_body, lineno)

    def _parse_purple(self, text, lineno):
        """PURPLE: for loop or while loop."""
        # for i in 1..100  (bounds can be integers OR variable names)
        m_for = re.match(r'for\s+(\w+)\s+in\s+(-?\d+|\w+)\.\.(-?\d+|\w+)', text)
        if m_for:
            var = m_for.group(1)
            start = m_for.group(2)
            end = m_for.group(3)
            body = self._parse_block()
            if self.peek() and self.peek().color == "RED":
                self.consume()
            return ForNode(var, start, end, body, lineno)

        # for i in range(...)
        m_range = re.match(r'for\s+(\w+)\s+in\s+range\((.+)\)', text)
        if m_range:
            var = m_range.group(1)
            range_args = m_range.group(2)
            body = self._parse_block()
            if self.peek() and self.peek().color == "RED":
                self.consume()
            # Expand range(...) into start..end
            parts = [p.strip() for p in range_args.split(",")]
            if len(parts) == 1:
                start, end = "0", str(int(parts[0]) - 1)
            elif len(parts) == 2:
                start, end = parts[0], str(int(parts[1]) - 1)
            else:
                raise SyntaxError(f"Line {lineno}: range() takes 1-2 args")
            return ForNode(var, start, end, body, lineno)

        # while condition
        m_while = re.match(r'while\s+(.+)', text)
        if m_while:
            cond = m_while.group(1).rstrip(":")
            body = self._parse_block()
            if self.peek() and self.peek().color == "RED":
                self.consume()
            return WhileNode(cond, body, lineno)

        raise ColorTypeError("PURPLE", text, lineno)


# ─────────────────────────────────────────────
#  INTERPRETER — walks the AST
# ─────────────────────────────────────────────

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class ChromaInterpreter:
    def __init__(self):
        self.global_env = {
            # Built-ins available in expressions
            "math": math,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "abs": abs,
            "max": max,
            "min": min,
            "round": round,
            "range": range,
            "list": list,
            "True": True,
            "False": False,
            "None": None,
        }
        self.output = []

    def run(self, nodes, env=None):
        if env is None:
            env = self.global_env
        for node in nodes:
            if node is None:
                continue
            self._exec(node, env)

    def _exec(self, node, env):
        if isinstance(node, AssignNode):
            val = self._eval(node.expr, env, node.lineno)
            env[node.name] = val

        elif isinstance(node, PrintNode):
            val = self._eval(node.expr, env, node.lineno)
            line = str(val)
            print(line)
            self.output.append(line)

        elif isinstance(node, FuncDefNode):
            def make_func(params, body, closure):
                def func(*args):
                    local_env = dict(closure)
                    if len(args) != len(params):
                        raise TypeError(f"Expected {len(params)} args, got {len(args)}")
                    for p, a in zip(params, args):
                        local_env[p] = a
                    try:
                        self.run(body, local_env)
                    except ReturnException as r:
                        return r.value
                    return None
                return func
            env[node.name] = make_func(node.params, node.body, env)
            self.global_env[node.name] = env[node.name]

        elif isinstance(node, ReturnNode):
            val = self._eval(node.expr, env, node.lineno) if node.expr else None
            raise ReturnException(val)

        elif isinstance(node, IfNode):
            for cond, body in node.branches:
                if self._eval(cond, env, node.lineno):
                    self.run(body, env)
                    return
            if node.else_body is not None:
                self.run(node.else_body, env)

        elif isinstance(node, ForNode):
            start = int(self._eval(str(node.start), env, node.lineno))
            end = int(self._eval(str(node.end), env, node.lineno))
            for i in range(start, end + 1):
                env[node.var] = i
                self.run(node.body, env)

        elif isinstance(node, WhileNode):
            while self._eval(node.condition, env, node.lineno):
                self.run(node.body, env)

        elif isinstance(node, FuncCallNode):
            self._eval(node.expr, env, node.lineno)

        elif isinstance(node, ExprNode):
            self._eval(node.expr, env, node.lineno)

    def _eval(self, expr, env, lineno):
        """Safely evaluate an expression in the current environment."""
        try:
            # Merge global + local env for eval
            combined = {**self.global_env, **env}
            return eval(expr, {"__builtins__": {}}, combined)
        except Exception as e:
            raise RuntimeError(f"Line {lineno}: Error evaluating '{expr}': {e}")


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────

def interpret_file(filepath: str):
    with open(filepath, "r") as f:
        source = f.read()
    tokens = lex(source)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = ChromaInterpreter()
    interpreter.run(ast)
    return interpreter.output


def interpret_source(source: str):
    tokens = lex(source)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = ChromaInterpreter()
    interpreter.run(ast)
    return interpreter.output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python chromacode.py <file.chroma>")
        sys.exit(1)
    filepath = sys.argv[1]
    try:
        interpret_file(filepath)
    except (SyntaxError, ColorTypeError, RuntimeError) as e:
        print(f"\n❌ {e}", file=sys.stderr)
        sys.exit(1)
