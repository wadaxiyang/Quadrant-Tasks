# SPDX-FileCopyrightText: Copyright (c) 2026 Quadrant contributors
# SPDX-License-Identifier: GPL-3.0-only
import copy
import json
import os
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from slint_contract import ContractError, parse
from check_ui_boundaries import (KIT_REV, KIT_URL, ROOT, acyclic, check,
    check_baseline, check_config, check_manifest, check_metadata, check_ui,
    fingerprint_definitions, reachable)

HEADER = '// SPDX-FileCopyrightText: Copyright (c) 2026 Quadrant contributors\n// SPDX-License-Identifier: GPL-3.0-only\n'


class ScannerTests(unittest.TestCase):
    def shape(self, source):
        return parse(source)['definitions']

    def test_multiline_alias_comments_strings_and_binding(self):
        source = '''import { Theme as T, } from "@quadrant-kit";
        export struct Record { id: string, selected: bool, }
        export component A inherits FocusScope {
          in-out property <string> some_value <=> child.text;
          out property <string> note: "{ // /* } \\\" ";
          pure callback calculate(int) -> int;
          public pure function apply(value: Record) -> bool { return true; }
        }'''
        self.assertEqual(parse(source)['imports'][0][1], [('Theme', 'T')])
        self.assertEqual(self.shape(source), self.shape(source.replace('in-out property', 'in-out /* } */\n property').replace('some_value', 'some-value')))

    def test_struct_direction_callback_pure_and_default_mutations(self):
        source = '''export struct InboxItem { id: string, disabled: bool }
        export component A { in property <string> label: "a  b"; callback done(string,int);
        public pure function test(x: int) -> bool { return true; } }'''
        for old, new in [(', disabled: bool', ''), ('disabled: bool', 'disabled: int'),
                         ('in property', 'out property'), ('string,int', 'string'),
                         ('public pure', 'public'), ('x: int', 'x: string'),
                         ('a  b', 'a b')]:
            with self.subTest(old=old), self.assertRaises(ContractError):
                check_baseline(self.shape(source.replace(old,new)), self.shape(source))

    def test_unknown_public_syntax_fails_closed(self):
        for source in ['export trait A {}', 'export component A { public mystery x; }',
                       'export struct A { missing_type }', 'export component A { in property <int> a unknown; }']:
            with self.subTest(source=source), self.assertRaises(ContractError):
                parse(source)

    def test_unicode_and_empty_string(self):
        self.assertEqual(self.shape(r'export global A { out property <string> a: "\u{41}"; out property <string> b: ""; }'),
                         self.shape('export global A { out property <string> a: "A"; out property <string> b: ""; }'))

    def test_copy_fingerprint_ignores_name_import_and_comments(self):
        old = 'import { Theme } from "foundation.slint"; export component FluentButton inherits Rectangle { in property <bool> enabled: true; background: Theme.card_bg; }'
        new = old.replace('foundation.slint','@quadrant-kit').replace('FluentButton','RenamedButton').replace('background:', '/* } */ background:')
        self.assertEqual(fingerprint_definitions(old)[0][1], fingerprint_definitions(new)[0][1])


class ImportFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.write('ui/app.slint','import { Theme } from "@quadrant-kit"; export component MainWindow inherits Window {} export component QuickAddWindow inherits Window {} export component TaskEditorWindow inherits Window {}')
        self.write('scripts/product_assets_v1.json',json.dumps({'assets': []}), header=False)
        self.write('assets/icons/LICENSE-MIT','Permission is hereby granted',header=False)
        self.ref = {'public_names':['Theme'], 'definition_fingerprints':[]}

    def write(self, path, source, header=True):
        path = self.root / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text((HEADER if header else '') + source, encoding='utf-8')

    def test_legal_product_relative_and_generic_focus_task(self):
        self.write('ui/components/a.slint','import { Theme } from "@quadrant-kit"; component A inherits FocusScope { in property <string> task: "general task"; }')
        self.write('ui/components/b.slint','import { A } from "a.slint"; component B {}')
        check_ui(self.root,self.ref)

    def test_external_raw_facade_and_escape_imports_fail(self):
        for target in ('../../Quadrant-Kit/ui/kit.slint', '@quadrant-kit/internal', '/tmp/kit.slint', 'C:/kit.slint'):
            self.write('ui/bad.slint', f'import {{ Theme }} from "{target}";')
            with self.subTest(target=target), self.assertRaises(ContractError):
                check_ui(self.root,self.ref)

    def test_cycle_and_removed_embedded_directory(self):
        with self.assertRaises(ContractError):
            acyclic({'a':['b'],'b':['a']})
        (self.root/'ui/gallery').mkdir()
        with self.assertRaises(ContractError):
            check_ui(self.root,self.ref)

    def test_existing_outside_resource_and_missing_attribution(self):
        self.write('outside.svg','<svg/>',header=False)
        self.write('ui/bad.slint','component X { in property <image> icon: @image-url("../outside.svg"); }')
        with self.assertRaisesRegex(ContractError,'outside owned'):
            check_ui(self.root,self.ref)
        self.write('ui/bad.slint','component X {}',header=False)
        with self.assertRaisesRegex(ContractError,'attribution'):
            check_ui(self.root,self.ref)

    def test_named_or_renamed_kit_copy_rejected(self):
        original = 'export component A inherits Rectangle { in property <bool> enabled: true; }'
        self.ref['definition_fingerprints'] = [fingerprint_definitions(original)[0][1]]
        for source in ('component Theme {}', original.replace('A inherits','Renamed inherits')):
            self.write('ui/bad.slint',source)
            with self.assertRaisesRegex(ContractError,'Copied/renamed'):
                check_ui(self.root,self.ref)


class CargoTests(unittest.TestCase):
    def test_alias_workspace_target_and_dev_sources(self):
        valid = {'package':'quadrant-kit','git':KIT_URL,'rev':KIT_REV}
        check_manifest({'package':{'name':'quadrant-ui'},'build-dependencies':{'kit':valid}}, {})
        workspace = {'dependencies':{'kit':valid}}
        check_manifest({'package':{'name':'quadrant-ui'},'build-dependencies':{'kit':{'workspace':True}}},workspace)
        check_manifest({'dependencies':{'domain':{'package':'quadrant-domain','path':'../domain'}}},{})
        for kind in ('dependencies','build-dependencies','dev-dependencies'):
            with self.subTest(kind=kind), self.assertRaises(ContractError):
                check_manifest({'target':{'cfg(windows)':{kind:{'kit':{**valid,'path':'../../Quadrant-Kit'}}}}}, {})
        with self.assertRaises(ContractError):
            check_manifest({'build-dependencies':{'kit':{'workspace':True}}}, {'dependencies':{'kit':{'package':'quadrant-kit','path':'../kit'}}})

    def test_unverified_revision_and_overrides(self):
        for value in ({'git':KIT_URL,'rev':'main'},{'git':KIT_URL,'rev':'a'*40},{'git':'file:///kit','rev':KIT_REV}):
            with self.assertRaises(ContractError):
                check_manifest({'build-dependencies':{'quadrant-kit':value}}, {})
        for config in ({'source':{'crates-io':{'replace-with':'local'}}}, {'paths':['../kit']},
                       {'env':{'SLINT_LIBRARY_PATH':'../kit'}}, {'build':{'rustc-wrapper':'override'}}):
            with self.assertRaises(ContractError):
                check_config(config)
        for kind in ('patch','replace'):
            with self.assertRaises(ContractError):
                check_manifest({kind:{'source':{}}},{})

    def metadata(self, cache):
        names=['quadrant-agent','quadrant-app','quadrant-ui','quadrant-kit','slint','helper','rusqlite']
        packages=[{'id':n,'name':n,'version':'1.17.1' if n=='slint' else '0.1.0'} for n in names]
        packages[3].update(source=f'git+{KIT_URL}?rev={KIT_REV}#{KIT_REV}',manifest_path=str(cache/'git/checkouts/kit/Cargo.toml'))
        nodes=[{'id':n,'deps':[]} for n in names]
        nodes[1]['deps']=[{'pkg':'quadrant-ui','dep_kinds':[{'kind':None}]}]
        nodes[2]['deps']=[{'pkg':'slint','dep_kinds':[{'kind':None}]},{'pkg':'quadrant-kit','dep_kinds':[{'kind':'build'}]}]
        return {'packages':packages,'workspace_members':names[:3],'resolve':{'nodes':nodes}}

    def test_actual_git_source_and_cache_location(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ,{'CARGO_HOME':temporary}):
            cache=Path(temporary).resolve()
            metadata=self.metadata(cache)
            check_metadata(metadata, ROOT)
            metadata['packages'][3]['source']=None
            with self.assertRaises(ContractError):check_metadata(metadata, ROOT)
            metadata=self.metadata(cache)
            metadata['packages'][3]['manifest_path']=str(ROOT/'../Quadrant-Kit/Cargo.toml')
            with self.assertRaises(ContractError):check_metadata(metadata, ROOT)

    def test_transitive_runtime_and_build_edges(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ,{'CARGO_HOME':temporary}):
            data=self.metadata(Path(temporary))
            self.assertNotIn('quadrant-kit',reachable(data,'quadrant-app',(None,)))
            for owner,target,kind in [('quadrant-agent','slint','build'),('quadrant-agent','quadrant-kit','dev'),('quadrant-app','rusqlite',None)]:
                changed=copy.deepcopy(data)
                next(n for n in changed['resolve']['nodes'] if n['id']==owner)['deps'].append({'pkg':'helper','dep_kinds':[{'kind':kind}]})
                next(n for n in changed['resolve']['nodes'] if n['id']=='helper')['deps'].append({'pkg':target,'dep_kinds':[{'kind':None}]})
                with self.subTest(owner=owner,target=target), self.assertRaises(ContractError):
                    check_metadata(changed,ROOT)

    def test_kit_edge_removed_or_attached_to_another_consumer(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ,{'CARGO_HOME':temporary}):
            data=self.metadata(Path(temporary))
            data['resolve']['nodes'][2]['deps'].pop()
            with self.assertRaisesRegex(ContractError, 'Resolved Kit edge'):
                check_metadata(data,ROOT)
            data['resolve']['nodes'][5]['deps'].append({'pkg':'quadrant-kit','dep_kinds':[{'kind':'build'}]})
            with self.assertRaisesRegex(ContractError, 'Resolved Kit edge'):
                check_metadata(data,ROOT)


class CurrentRepositoryTests(unittest.TestCase):
    def test_product_contracts_and_sources(self):
        self.assertEqual(check(metadata=False)['product_exports'],27)

    def test_git_windows_checkout_preserves_asset_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/'.gitattributes').write_bytes((ROOT/'.gitattributes').read_bytes())
            asset='assets/icons/quadrants-20-regular.svg'
            path=root/asset
            path.parent.mkdir(parents=True)
            original=(ROOT/asset).read_bytes()
            path.write_bytes(original)
            def git(*args):
                subprocess.run(['git','-c','core.autocrlf=true','-c','core.safecrlf=false',*args],cwd=root,check=True,capture_output=True)
            git('init','-q')
            git('add','.gitattributes',asset)
            path.unlink()
            git('checkout-index','--all','--force')
            self.assertEqual(path.read_bytes(),original)
            recorded=json.loads((ROOT/'scripts/product_assets_v1.json').read_text())['assets'][0]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),recorded['sha256'])


if __name__ == '__main__':
    unittest.main()
