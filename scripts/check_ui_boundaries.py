#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 Quadrant contributors
# SPDX-License-Identifier: GPL-3.0-only
"""Tasks Product contracts and remote Kit/Agent/GUI ownership guard.

Retains the original export/import/dependency/provenance checks, using the
scanner reviewed in Kit commit 838ecfbead2d0a1966907ddd742cb6f34516d3f6.
Slint compilation supplements this bounded source scanner.
"""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from slint_contract import ContractError, Cursor, canonical, images, lex, local_path, parse

ROOT = Path(__file__).resolve().parents[1]
KIT_URL = 'https://github.com/wadaxiyang/Quadrant-Kit.git'
KIT_REV = '838ecfbead2d0a1966907ddd742cb6f34516d3f6'
REMOVED = ('ui/kit', 'ui/gallery', 'crates/quadrant-ui-gallery', 'scripts/capture_gallery_baseline.ps1')
EXCLUDED = {'.git', 'target', '__pycache__'}


def files(root, pattern):
    return sorted(p for p in root.rglob(pattern) if not EXCLUDED.intersection(p.relative_to(root).parts) and not any(part.startswith('.tmp-') for part in p.relative_to(root).parts))


def fingerprint_definitions(text):
    """Ignore imports, declaration names and comments when detecting copies."""
    cursor, result = Cursor(lex(text)), []
    while cursor.peek():
        if cursor.peek('export'):
            cursor.take()
        if cursor.peek() in ('component', 'global', 'enum', 'struct'):
            kind, name = cursor.take().value, cursor.name()
            header = cursor.until({'{'})
            body = cursor.group('{', '}')
            result.append((name, hashlib.sha256((kind + canonical(header + body)).encode()).hexdigest()))
        elif cursor.peek('import') or cursor.peek('{'):
            if cursor.peek('import'):
                cursor.take()
            cursor.group('{', '}')
            cursor.until({';'})
            cursor.take(';')
        else:
            raise ContractError(f'Unknown declaration: {cursor.peek()}')
    return result


def product_api(root=ROOT):
    exports = {}
    for path in files(root / 'ui', '*.slint'):
        module = parse(path.read_text(encoding='utf-8'))
        for name in module['definitions'].keys() & module['exports'].keys():
            if name in exports:
                raise ContractError(f'Duplicate Product export: {name}')
            exports[name] = module['definitions'][name]
    return dict(sorted(exports.items()))


def rust_host_api(root=ROOT):
    source = (root / 'crates/quadrant-ui/src/shell.rs').read_text(encoding='utf-8')
    methods = {}
    for match in re.finditer(r'\bpub fn\s+([a-z_]+)\s*\(', source):
        owners = list(re.finditer(r'\bimpl\s+(\w+)\s*\{', source[:match.start()]))
        if not owners:
            raise ContractError('Unknown public Rust method owner')
        header = source[match.start():source.index('{', match.start())]
        methods[owners[-1][1] + '::' + match[1]] = canonical(lex(header))
    declarations = re.findall(r'pub type\s+[^;]+;|pub enum GuiShell\s*\{[^}]+\}', source)
    facade = (root / 'crates/quadrant-ui/src/lib.rs').read_text(encoding='utf-8')
    return {'methods': methods, 'declarations': [canonical(lex(d)) for d in declarations],
            'reexports': [canonical(lex(d)) for d in re.findall(r'pub use\s+[^;]+;', facade)],
            'generated_module': 'slint::include_modules!();' in facade}


def check_baseline(actual, expected):
    if actual != expected:
        delta = '\n'.join(difflib.unified_diff(json.dumps(expected, indent=2, sort_keys=True).splitlines(), json.dumps(actual, indent=2, sort_keys=True).splitlines(), fromfile='reviewed baseline', tofile='current', lineterm=''))
        raise ContractError('Product contract changed; explicit review required:\n' + delta)


def acyclic(graph):
    active, done = [], set()
    def visit(node):
        if node in active:
            raise ContractError('Product import cycle: ' + ' -> '.join(map(str, active + [node])))
        if node in done:
            return
        active.append(node)
        for edge in graph.get(node, []):
            visit(edge)
        active.pop()
        done.add(node)
    for node in graph:
        visit(node)


def check_ui(root, reference):
    for name in REMOVED:
        if (root / name).exists():
            raise ContractError(f'Embedded Kit/Gallery still present: {name}')
    graph, assets, symbols = {}, set(), {}
    for path in files(root, '*.slint'):
        if not path.is_relative_to(root / 'ui'):
            raise ContractError(f'Slint source outside Product UI: {path}')
        text = path.read_text(encoding='utf-8')
        try:
            module = parse(text)
        except ContractError as error:
            raise ContractError(f'{path}: {error}') from error
        if 'SPDX-License-Identifier: GPL-3.0-only' not in text[:1500] or 'SPDX-FileCopyrightText:' not in text[:1500]:
            raise ContractError(f'Missing Product attribution: {path}')
        for name, fingerprint in fingerprint_definitions(text):
            if name in reference['public_names'] or fingerprint in reference['definition_fingerprints']:
                raise ContractError(f'Copied/renamed Kit implementation in {path}: {name}')
            if name in module['exports']:
                if name in symbols:
                    raise ContractError(f'Duplicate Product definition: {name}')
                symbols[name] = path
        graph[path] = []
        for source, aliases in module['imports']:
            if source == 'std-widgets.slint':
                continue
            if source == '@quadrant-kit':
                if any(name not in reference['public_names'] for name, _ in aliases):
                    raise ContractError(f'Unknown Kit public name: {path}')
                continue
            target = local_path(path, source, root / 'ui')
            if target.suffix != '.slint':
                raise ContractError(f'Invalid Product import: {path}: {source}')
            if path.is_relative_to(root / 'ui/product') and not target.is_relative_to(root / 'ui/product'):
                raise ContractError('Product semantic layer depends on view/component')
            graph[path].append(target)
        for source in images(text):
            target = local_path(path, source, root)
            if not target.is_relative_to(root / 'assets'):
                raise ContractError(f'Static resource outside owned assets: {path}')
            assets.add(target.relative_to(root).as_posix())
    acyclic(graph)
    entry = parse((root / 'ui/app.slint').read_text(encoding='utf-8'))
    for name in ('MainWindow', 'QuickAddWindow', 'TaskEditorWindow'):
        if name not in entry['exports']:
            raise ContractError(f'Missing generated window: {name}')
    manifest = json.loads((root / 'scripts/product_assets_v1.json').read_text(encoding='utf-8'))
    recorded = set()
    for asset in manifest['assets']:
        path = (root / asset['path']).resolve()
        if not path.is_relative_to(root / 'assets/icons') or asset['path'] in recorded:
            raise ContractError('Invalid/duplicate Product asset record')
        if asset['spdx_license'] != 'MIT' or hashlib.sha256(path.read_bytes()).hexdigest() != asset['sha256']:
            raise ContractError(f'Product asset hash/license changed: {asset["path"]}')
        recorded.add(asset['path'])
    if {p for p in assets if p.startswith('assets/icons/')} != recorded:
        raise ContractError('Product icon closure differs from manifest')
    if {p.relative_to(root).as_posix() for p in (root / 'assets/icons').glob('*.svg')} != recorded:
        raise ContractError('Unowned/generic icon copies remain in Tasks')
    if 'Permission is hereby granted' not in (root / 'assets/icons/LICENSE-MIT').read_text(encoding='utf-8'):
        raise ContractError('Missing original icon MIT license')
    return {'product_exports': len(symbols), 'static_assets': len(assets)}


def dependencies(manifest):
    for kind in ('dependencies', 'build-dependencies', 'dev-dependencies'):
        for alias, value in manifest.get(kind, {}).items():
            yield kind, alias, value
    for table in manifest.get('target', {}).values():
        yield from dependencies(table)


def check_manifest(manifest, workspace):
    if manifest.get('patch') or manifest.get('replace'):
        raise ContractError('Cargo patch/replace is forbidden')
    found = 0
    for kind, alias, value in dependencies(manifest):
        value = {'version': value} if isinstance(value, str) else dict(value)
        if value.get('workspace'):
            inherited = workspace.get('dependencies', {}).get(alias)
            if inherited is None:
                raise ContractError(f'Unknown inherited dependency: {alias}')
            inherited = {'version': inherited} if isinstance(inherited, str) else inherited
            value = {**inherited, **value}
        name = value.get('package', alias)
        if name == 'quadrant-ui-gallery':
            raise ContractError('Removed Gallery dependency')
        if name == 'quadrant-kit':
            found += 1
            if value.get('git') != KIT_URL or value.get('rev') != KIT_REV or any(k in value for k in ('path', 'branch', 'tag', 'registry')):
                raise ContractError(f'Kit must use verified public Git + full SHA: {alias}')
            owner = manifest.get('package', {}).get('name')
            if owner and (owner != 'quadrant-ui' or kind != 'build-dependencies'):
                raise ContractError('Kit is only a quadrant-ui build dependency')
    return found


def check_config(config):
    if any(config.get(key) for key in ('patch', 'replace', 'paths', 'source')):
        raise ContractError('Cargo source override/replacement detected')
    if any(name.startswith(('SLINT_INCLUDE', 'SLINT_LIBRARY')) for name in config.get('env', {})):
        raise ContractError('Cargo env overrides Slint discovery')
    if any(k in config.get('build', {}) for k in ('rustc', 'rustc-wrapper', 'rustc-workspace-wrapper')):
        raise ContractError('Compiler wrapper requires separate source review')


def check_manifests(root):
    workspace = tomllib.loads((root / 'Cargo.toml').read_text(encoding='utf-8'))['workspace']
    check_manifest({'dependencies': workspace.get('dependencies', {})}, workspace)
    count = sum(check_manifest(tomllib.loads(p.read_text(encoding='utf-8')), workspace) for p in files(root, 'Cargo.toml'))
    if count != 1:
        raise ContractError('Expected one effective Product Kit dependency')
    configs = {directory / '.cargo' / name for directory in (root, *root.parents) for name in ('config', 'config.toml')}
    cargo_home = Path(os.environ.get('CARGO_HOME', Path.home() / '.cargo'))
    configs.update(cargo_home / name for name in ('config', 'config.toml'))
    configs.update(p for p in files(root, 'config*') if p.parent.name == '.cargo')
    for config in configs:
        if config.is_file():
            check_config(tomllib.loads(config.read_text(encoding='utf-8')))
    if any(k.startswith(('SLINT_INCLUDE', 'SLINT_LIBRARY')) for k in os.environ):
        raise ContractError('Environment overrides Slint discovery')


def reachable(metadata, initial, kinds):
    nodes = {n['id']: n for n in metadata['resolve']['nodes']}
    visited, pending = set(), [initial]
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        visited.add(current)
        for edge in nodes[current]['deps']:
            if any(k['kind'] in kinds for k in edge['dep_kinds']):
                pending.append(edge['pkg'])
    return visited - {initial}


def check_metadata(metadata, root):
    packages = {p['id']: p for p in metadata['packages']}
    kit = [p for p in packages.values() if p['name'] == 'quadrant-kit']
    if len(kit) != 1 or kit[0].get('source') != f'git+{KIT_URL}?rev={KIT_REV}#{KIT_REV}':
        raise ContractError('Actual Kit source differs from verified remote commit')
    kit_path = Path(kit[0]['manifest_path']).resolve()
    cargo_home = Path(os.environ.get('CARGO_HOME', Path.home() / '.cargo')).resolve()
    if not kit_path.is_relative_to(cargo_home / 'git/checkouts') or kit_path.is_relative_to(root.resolve()):
        raise ContractError('Kit source is not in Cargo fetched Git storage')
    if reachable(metadata, kit[0]['id'], (None,)):
        raise ContractError('Kit helper acquired runtime dependencies')
    by_name = {p['name']: p for p in packages.values() if p['id'] in metadata['workspace_members']}
    incoming = [(node['id'], kind['kind']) for node in metadata['resolve']['nodes']
                for edge in node['deps'] if edge['pkg'] == kit[0]['id']
                for kind in edge['dep_kinds']]
    if incoming != [(by_name['quadrant-ui']['id'], 'build')]:
        raise ContractError('Resolved Kit edge must be exclusively quadrant-ui build')
    if 'quadrant-ui-gallery' in by_name:
        raise ContractError('Gallery remains a workspace member')
    for name in ('quadrant-agent', 'quadrant-app', 'quadrant-ui'):
        kinds = (None, 'build', 'dev') if name == 'quadrant-agent' else (None,)
        for dependency in reachable(metadata, by_name[name]['id'], kinds):
            dep = packages[dependency]['name']
            bad_agent = dep in ('quadrant-ui', 'quadrant-kit', 'slint', 'slint-build', 'winit', 'femtovg', 'skia-safe') or dep.startswith('i-slint-')
            bad_gui = dep in ('quadrant-storage', 'rusqlite', 'quadrant-agent', 'quadrant-kit')
            if (name == 'quadrant-agent' and bad_agent) or (name != 'quadrant-agent' and bad_gui):
                raise ContractError(f'Resolved {name} dependency path reaches {dep}')
    for package in packages.values():
        if package['name'] in ('slint', 'slint-build') and package['version'] != '1.17.1':
            raise ContractError('Unexpected resolved Slint version')
    return {'kit_source': kit[0]['source'], 'kit_manifest': str(kit_path)}


def check(root=ROOT, metadata=True, target=None):
    reference = json.loads((root / 'scripts/kit_source_v1.json').read_text(encoding='utf-8'))
    check_baseline(reference['rev'], KIT_REV)
    result = check_ui(root, reference)
    baseline = json.loads((root / 'scripts/product_ui_api_v1.json').read_text(encoding='utf-8'))
    check_baseline(product_api(root), baseline['exports'])
    check_baseline(rust_host_api(root), baseline['rust_host'])
    check_baseline(canonical(lex((root / 'crates/quadrant-ui/build.rs').read_text(encoding='utf-8'))), baseline['build_contract'])
    check_manifests(root)
    if metadata:
        host = target or next(line.split(': ', 1)[1] for line in subprocess.check_output(['rustc', '-vV'], cwd=root, text=True).splitlines() if line.startswith('host: '))
        data = json.loads(subprocess.check_output(['cargo', 'metadata', '--locked', '--format-version', '1', '--filter-platform', host], cwd=root, text=True, encoding='utf-8'))
        result.update(check_metadata(data, root))
        result['target'] = host
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', help='Target triple for resolved dependency graph filtering')
    args = parser.parse_args()
    try:
        print(json.dumps(check(target=args.target), indent=2))
    except (ValueError, OSError, subprocess.SubprocessError, KeyError) as error:
        print(f'Boundary check failed: {error}', file=sys.stderr)
        sys.exit(1)
