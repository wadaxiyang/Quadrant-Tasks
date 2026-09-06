# SPDX-FileCopyrightText: Copyright (c) 2026 Quadrant contributors
# SPDX-License-Identifier: GPL-3.0-only
"""Small fail-closed declaration scanner, not a Slint semantic compiler.

Replaces the original guard's regex/line-based extraction while retaining its
export, layering, cycle and API comparison approach. Slint 1.17.1 + API probe
remain responsible for expression typing, builtin inheritance and UI semantics.
"""
from dataclasses import dataclass
import json
from pathlib import Path
import re


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class Token:
    value: str
    kind: str = 'symbol'


def lex(source):
    tokens = []
    i = 0
    while i < len(source):
        if source[i].isspace():
            i += 1
        elif source.startswith('//', i):
            end = source.find('\n', i)
            i = len(source) if end < 0 else end + 1
        elif source.startswith('/*', i):
            depth = 1
            i += 2
            while depth and i < len(source):
                if source.startswith('/*', i):
                    depth += 1
                    i += 2
                elif source.startswith('*/', i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
            if depth:
                raise ContractError('Unterminated comment')
        elif source[i] == '"':
            i += 1
            value = ''
            while i < len(source) and source[i] != '"':
                if source[i] == '\\':
                    i += 1
                    if i == len(source):
                        raise ContractError('Unterminated string escape')
                    escapes = {'n': '\n', '"': '"', '\\': '\\'}
                    if source[i] == 'u':
                        match = re.match(r'u\{([0-9a-fA-F]+)\}', source[i:])
                        if not match:
                            raise ContractError('Invalid Unicode escape')
                        codepoint = int(match[1], 16)
                        if codepoint > 0x10ffff or 0xd800 <= codepoint <= 0xdfff:
                            raise ContractError('Invalid Unicode scalar')
                        value += chr(codepoint)
                        i += len(match.group()) - 1
                    elif source[i] not in escapes:
                        raise ContractError('Unsupported string escape; extend scanner explicitly')
                    else:
                        value += escapes[source[i]]
                else:
                    value += source[i]
                i += 1
            if i == len(source):
                raise ContractError('Unterminated string')
            tokens.append(Token(value, 'string'))
            i += 1
        else:
            match = re.match(r'[A-Za-z_][A-Za-z0-9_-]*|[0-9]+(?:\.[0-9]+)?(?:[A-Za-z%]+)?|<=>|=>|->|:=|==|!=|<=|>=|&&|\|\|', source[i:])
            value = match.group() if match else source[i]
            kind = 'identifier' if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_-]*', value) else 'symbol'
            tokens.append(Token(value.replace('_', '-') if kind == 'identifier' else value, kind))
            i += len(value)
    # Strings and comments cannot affect delimiter balance.
    stack = []
    for token in tokens:
        if token.kind != 'symbol':
            continue
        if token.value in ('{', '(', '['):
            stack.append(token.value)
        elif token.value in ('}', ')', ']'):
            if not stack or stack.pop() != {'}': '{', ')': '(', ']': '['}[token.value]:
                raise ContractError('Unbalanced delimiters')
    if stack:
        raise ContractError('Unclosed delimiter')
    return tokens


def canonical(tokens):
    return ' '.join(json.dumps(t.value, ensure_ascii=False) if t.kind == 'string' else t.value for t in tokens)


class Cursor:
    def __init__(self, tokens):
        self.tokens, self.i = tokens, 0

    def peek(self, value=None):
        token = self.tokens[self.i] if self.i < len(self.tokens) else Token('')
        if token.kind == 'string':
            return False if value is not None else json.dumps(token.value)
        return token.value == value if value is not None else token.value

    def take(self, value=None):
        if self.i >= len(self.tokens) or (value is not None and not self.peek(value)):
            raise ContractError(f'Expected {value or "token"}, got {self.peek()!r}')
        token = self.tokens[self.i]
        self.i += 1
        return token

    def name(self):
        token = self.take()
        if token.kind != 'identifier':
            raise ContractError(f'Expected identifier, got {token.value!r}')
        return token.value

    def group(self, opening, closing):
        self.take(opening)
        start, depth = self.i, 1
        while depth:
            token = self.take()
            if token.kind == 'symbol':
                if token.value == opening:
                    depth += 1
                elif token.value == closing:
                    depth -= 1
        return self.tokens[start:self.i - 1]

    def until(self, stops):
        start = self.i
        while self.peek() and self.peek() not in stops:
            if self.peek() in ('{', '(', '['):
                opening = self.peek()
                self.group(opening, {'{': '}', '(': ')', '[': ']'}[opening])
            else:
                self.take()
        return self.tokens[start:self.i]


def fields(tokens, named):
    cursor, result = Cursor(tokens), []
    while cursor.peek():
        part = Cursor(cursor.until({','}))
        if named:
            name = part.name()
            part.take(':')
            value = canonical(part.tokens[part.i:])
            if not value:
                raise ContractError('Missing field/argument type')
            result.append({'name': name, 'type': value})
        else:
            value = canonical(part.tokens)
            if not value:
                raise ContractError('Empty argument')
            result.append(value)
        if cursor.peek(','):
            cursor.take(',')
    if named and len({f['name'] for f in result}) != len(result):
        raise ContractError('Duplicate field/argument')
    return result


def members(tokens):
    cursor, signatures, defaults = Cursor(tokens), {}, {}
    while cursor.peek():
        start = cursor.i
        direction = cursor.take().value if cursor.peek() in ('in', 'out', 'in-out') else None
        modifiers = []
        while cursor.peek() in ('public', 'pure', 'private'):
            modifiers.append(cursor.take().value)
        if len(set(modifiers)) != len(modifiers) or {'public', 'private'} <= set(modifiers):
            raise ContractError('Duplicate/conflicting declaration modifiers')
        if direction or modifiers or cursor.peek('callback'):
            kind = cursor.take().value
            if kind == 'property' and ((direction and not modifiers) or (not direction and modifiers == ['private'])):
                type_name = canonical(cursor.group('<', '>'))
                if not type_name:
                    raise ContractError('Missing property type')
                name = cursor.name()
                signature = {'kind': kind, 'direction': direction, 'type': type_name}
                binding = cursor.take().value if cursor.peek() in (':', '<=>') else None
                value = canonical(cursor.until({';'}))
                cursor.take(';')
                if value and not binding:
                    raise ContractError('Unknown property syntax')
                if modifiers == ['private']:
                    continue
                defaults[name] = {'binding': binding, 'expression': value}
            elif kind == 'callback' and not direction and all(m == 'pure' for m in modifiers):
                name = cursor.name()
                args = fields(cursor.group('(', ')'), False) if cursor.peek('(') else []
                result = 'void'
                if cursor.peek('->'):
                    cursor.take()
                    result = canonical(cursor.until({';', '<=>'}))
                    if not result:
                        raise ContractError('Missing callback return type')
                signature = {'kind': kind, 'arguments': args, 'return': result, 'pure': 'pure' in modifiers}
                if cursor.peek('<=>'):
                    cursor.take()
                    defaults[name] = {'binding': '<=>', 'expression': canonical(cursor.until({';'}))}
                cursor.take(';')
            elif kind == 'function' and not direction and set(modifiers) <= {'public', 'private', 'pure'}:
                name = cursor.name()
                args = fields(cursor.group('(', ')'), True)
                result = 'void'
                if cursor.peek('->'):
                    cursor.take()
                    result = canonical(cursor.until({'{'}))
                    if not result:
                        raise ContractError('Missing function return type')
                cursor.group('{', '}')
                if 'public' not in modifiers:
                    continue
                signature = {'kind': kind, 'arguments': args, 'return': result, 'pure': 'pure' in modifiers}
            else:
                raise ContractError(f'Unrecognized public declaration: {canonical(cursor.tokens[start:cursor.i])}')
            if name in signatures:
                raise ContractError(f'Duplicate public member: {name}')
            signatures[name] = signature
        else:
            # Skip private implementation statements/children by balanced groups.
            # Any public marker in an unrecognized top-level prefix is an error.
            prefix = cursor.until({';', '{'})
            if any(t.value in ('public', 'pure', 'in', 'out', 'in-out', 'callback') for t in prefix if t.kind == 'identifier'):
                raise ContractError(f'Unrecognized public declaration: {canonical(prefix)}')
            if cursor.peek('{'):
                cursor.group('{', '}')
            elif cursor.peek(';'):
                cursor.take()
            elif prefix:
                raise ContractError(f'Unterminated implementation statement: {canonical(prefix)}')
    return signatures, defaults


def parse(source):
    cursor = Cursor(lex(source))
    definitions, exports, imports = {}, {}, []

    def expose(name, target):
        if name in exports:
            raise ContractError(f'Duplicate export: {name}')
        exports[name] = target

    while cursor.peek():
        exported = cursor.peek('export')
        if exported:
            cursor.take()
        if cursor.peek('import') or (exported and cursor.peek('{')):
            if not exported:
                cursor.take('import')
            names = Cursor(cursor.group('{', '}'))
            aliases = []
            while names.peek():
                original = names.name()
                alias = original
                if names.peek('as'):
                    names.take()
                    alias = names.name()
                aliases.append((original, alias))
                if names.peek():
                    names.take(',')
            source_path = None
            if cursor.peek('from'):
                cursor.take()
                token = cursor.take()
                if token.kind != 'string':
                    raise ContractError('Import source must be a string')
                source_path = token.value
                imports.append((source_path, aliases))
            elif not exported:
                raise ContractError('Import requires from')
            cursor.take(';')
            if exported:
                for original, alias in aliases:
                    expose(alias, (source_path, original))
        elif cursor.peek() in ('component', 'global', 'enum', 'struct'):
            kind, name = cursor.take().value, cursor.name()
            base = None
            if cursor.peek('inherits'):
                cursor.take()
                base = cursor.name()
            body = cursor.group('{', '}')
            signature = {'kind': kind, 'inherits': base}
            defaults = {}
            if kind == 'enum':
                enum = Cursor(body)
                values = []
                while enum.peek():
                    values.append(enum.name())
                    if enum.peek():
                        enum.take(',')
                if len(set(values)) != len(values):
                    raise ContractError('Duplicate enum value')
                signature['values'] = values
            elif kind == 'struct':
                signature['fields'] = sorted(fields(body, True), key=lambda f: f['name'])
            else:
                signature['members'], defaults = members(body)
            if name in definitions:
                raise ContractError(f'Duplicate definition: {name}')
            definitions[name] = {'signature': signature, 'defaults': defaults}
            if exported:
                expose(name, (None, name))
        else:
            raise ContractError(f'Unrecognized top-level declaration: {cursor.peek()}')
    return {'definitions': definitions, 'exports': exports, 'imports': imports}


def local_path(owner, source, root):
    if not source or source.startswith(('@', '/', '\\')) or ':' in source or '\\' in source:
        raise ContractError(f'Illegal external path: {source}')
    path = (owner.parent / source).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ContractError(f'Missing/escaping path: {owner}: {source}')
    return path


def images(source):
    tokens = lex(source)
    result = []
    for i, token in enumerate(tokens):
        if token.value == '@' and i + 1 < len(tokens) and tokens[i + 1].value == 'image-url':
            args = Cursor(tokens[i + 2:]).group('(', ')')
            if len(args) != 1 or args[0].kind != 'string':
                raise ContractError('Static image-url requires one literal path')
            result.append(args[0].value)
    return result


def public_api(root):
    root = Path(root).resolve()
    cache = {}

    def module(path):
        if path not in cache:
            try:
                cache[path] = parse(path.read_text(encoding='utf-8'))
            except ContractError as error:
                raise ContractError(f'{path}: {error}') from error
        return cache[path]

    def resolve(path, name, trail):
        key = (path, name)
        if key in trail:
            raise ContractError(f'Export cycle at {path}: {name}')
        parsed = module(path)
        if name not in parsed['exports']:
            raise ContractError(f'Unresolved public export {name} in {path}')
        source, original = parsed['exports'][name]
        if source is None and original in parsed['definitions']:
            return parsed['definitions'][original]
        if source is None:
            matches = [(s, n) for s, pairs in parsed['imports'] for n, a in pairs if a == original]
            if len(matches) != 1:
                raise ContractError(f'Unresolved/ambiguous re-export: {original}')
            source, original = matches[0]
        return resolve(local_path(path, source, root), original, trail | {key})

    facade = root / 'ui/kit.slint'
    return {name: resolve(facade, name, set()) for name in sorted(module(facade)['exports'])}
