import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'mcp'))
from adik_contracts import ContractError, SECTIONS, load_registry, registry_report, relative_path, validate_bundle, validate_registry


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result

bundle=module('bundle','scripts/adik-bundle.py')
REFERENCE=ROOT/'examples/hello-adik'
REGISTRY=json.loads((REFERENCE/'contracts/registry.json').read_text())


def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value))


def markdown(registry):
    text='```yaml\n'+json.dumps(registry['metadata'])+'\n```\n'
    for section in SECTIONS:
        symbols=registry['symbols'] if section=='FUNCTIONS' else []
        text+=f'<!-- ADIK:{section}:START -->\n```yaml\n'+json.dumps(symbols)+f'\n```\n<!-- ADIK:{section}:END -->\n'
    return text


class Workspace(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
    def fixture(self):
        path=self.root/'bundle';shutil.copytree(REFERENCE,path);return path
    def run_cli(self,*args,ok=True):
        result=subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        if ok:self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        else:self.assertNotEqual(result.returncode,0,result.stdout)
        return result


class RegistryTests(Workspace):
    def test_canonical_and_yaml_legacy_agree(self):
        write_json(self.root/'contracts/registry.json',REGISTRY)
        self.assertEqual(load_registry(self.root),REGISTRY)
        (self.root/'contracts/registry.json').unlink()
        (self.root/'Registry.md').write_text(markdown(REGISTRY))
        self.assertEqual(load_registry(self.root),REGISTRY)
        self.assertEqual(registry_report(self.root)['status'],'PASS')
    def test_table_legacy(self):
        text=markdown(REGISTRY)
        symbol=REGISTRY['symbols'][0]
        fields=['id','kind','name','namespace','signature','description']
        table='| '+' | '.join(fields)+' |\n| '+' | '.join(['---']*len(fields))+' |\n| '+' | '.join(symbol[f] for f in fields)+' |\n'
        start='<!-- ADIK:FUNCTIONS:START -->';end='<!-- ADIK:FUNCTIONS:END -->'
        before,rest=text.split(start);_,after=rest.split(end)
        (self.root/'Registry.md').write_text(before+start+'\n'+table+end+after)
        self.assertEqual(registry_report(self.root)['status'],'PASS')
        self.assertEqual(load_registry(self.root)['symbols'][0]['id'],symbol['id'])
    def test_missing_markers_and_empty_template_fail(self):
        (self.root/'Registry.md').write_text('```yaml\n'+json.dumps(REGISTRY['metadata'])+'\n```')
        self.assertEqual(registry_report(self.root)['status'],'FAIL')
        data=copy.deepcopy(REGISTRY);data['symbols']=[]
        (self.root/'Registry.md').write_text(markdown(data))
        self.assertEqual(registry_report(self.root)['status'],'FAIL')
    def test_invalid_types_fail_cleanly(self):
        for value in [None,{},'wrong',[None],[{'kind':[]}]]:
            with self.subTest(value=value):
                data=copy.deepcopy(REGISTRY);data['symbols']=value
                write_json(self.root/'contracts/registry.json',data)
                self.assertEqual(registry_report(self.root)['status'],'FAIL')
    def test_duplicate_and_invalid_project_type(self):
        data=copy.deepcopy(REGISTRY);data['symbols']*=2;data['metadata']['projectType']='auto'
        errors=validate_registry(data)
        self.assertTrue(any('Duplicate' in e for e in errors));self.assertTrue(any('projectType' in e for e in errors))
    def test_partition_activation_and_consistency(self):
        (self.root/'Registry.md').write_text(markdown(REGISTRY))
        shutil.copyfile(ROOT/'Registry.index.md',self.root/'Registry.index.md')
        self.assertEqual(load_registry(self.root),REGISTRY)
        metadata={**REGISTRY['metadata'],'registryMode':'partitioned'}
        index='```yaml\n'+json.dumps(metadata)+'\n```\n<!-- ADIK:PARTITIONS:START -->\n| domain | file |\n| --- | --- |\n| hello | Registry.hello.md |\n<!-- ADIK:PARTITIONS:END -->'
        (self.root/'Registry.index.md').write_text(index)
        (self.root/'Registry.hello.md').write_text(markdown(REGISTRY))
        self.assertEqual(registry_report(self.root)['status'],'PASS')
        child=copy.deepcopy(REGISTRY);child['metadata']['lastAnalysedCommit']='stale'
        (self.root/'Registry.hello.md').write_text(markdown(child))
        self.assertEqual(registry_report(self.root)['status'],'FAIL')
    def test_strict_promotes_warning(self):
        data=copy.deepcopy(REGISTRY);data['symbols'][0].pop('description')
        write_json(self.root/'contracts/registry.json',data)
        self.assertEqual(registry_report(self.root)['status'],'WARN')
        self.assertEqual(registry_report(self.root,strict=True)['status'],'FAIL')


class BundleTests(Workspace):
    def test_reference_schemas(self):
        import jsonschema
        for instance,schema in [(REFERENCE/'adik.manifest.json','adik-manifest.schema.json'),(REFERENCE/'contracts/registry.json','registry.schema.json')]:
            jsonschema.Draft202012Validator(json.loads((ROOT/'schemas'/schema).read_text())).validate(json.loads(instance.read_text()))
        validate_bundle(REFERENCE)
    def test_requires_sdk_and_skill_and_real_files(self):
        root=self.fixture();original=json.loads((root/'adik.manifest.json').read_text())
        for key in ['sdks','implementationSkills']:
            data=copy.deepcopy(original);data[key]=[];write_json(root/'adik.manifest.json',data)
            with self.assertRaises(ContractError):bundle.seal(root)
        write_json(root/'adik.manifest.json',original)
        entry=root/original['sdks'][0]['entryPoint'];entry.write_text('')
        with self.assertRaises(ContractError):bundle.seal(root)
    def test_references_and_versions_are_consistent(self):
        root=self.fixture();original=json.loads((root/'adik.manifest.json').read_text())
        for mutate in [lambda m:m['sdks'][0].update(version='2.0.0'),lambda m:m['implementationSkills'][0].update(symbolIds=['missing']),lambda m:m['implementationSkills'][0].update(references=['missing.md']),lambda m:m['source'].update(revision='other')]:
            data=copy.deepcopy(original);mutate(data);write_json(root/'adik.manifest.json',data)
            with self.assertRaises(ContractError):bundle.seal(root)
        write_json(root/'adik.manifest.json',original)
        skill=root/original['implementationSkills'][0]['path'];skill.write_text(skill.read_text().replace('sdk-version: 1.0.0','sdk-version: 2.0.0'))
        with self.assertRaises(ContractError):bundle.seal(root)
    def test_hash_drift_and_unlisted_files_fail(self):
        root=self.fixture();extra=root/'extra.txt';extra.write_text('extra')
        with self.assertRaises(ContractError):validate_bundle(root)
        bundle.seal(root);validate_bundle(root)
        extra.write_text('changed')
        with self.assertRaises(ContractError):validate_bundle(root)
    def test_paths_and_symlinks_rejected(self):
        for name in ['../escape','/tmp/escape','./sdk','sdk//file','sdk/../file','C:escape','sdk\\file']:
            with self.assertRaises(ContractError):relative_path(self.root,name)
        root=self.fixture();(root/'linked').symlink_to(ROOT/'README.md')
        with self.assertRaises(ContractError):bundle.seal(root)
    def test_archives_reproducible_and_complete(self):
        a=self.root/'a.zip';b=self.root/'b.zip'
        bundle.pack(REFERENCE,a);bundle.pack(REFERENCE,b)
        self.assertEqual(a.read_bytes(),b.read_bytes())
        with zipfile.ZipFile(a) as z:
            z.extractall(self.root/'unpacked')
        validate_bundle(self.root/'unpacked')
        with self.assertRaises(ContractError):bundle.pack(REFERENCE,a)
    def test_registration_idempotence_and_safe_removal_all_clients(self):
        for client,(_,context_name) in bundle.CLIENTS.items():
            target=self.root/client;context=target/context_name;context.parent.mkdir(parents=True);context.write_text('Host instructions\n')
            unrelated=target/'agents/host.md';unrelated.parent.mkdir();unrelated.write_text('host')
            receipt=bundle.install(REFERENCE,target,client)
            self.assertEqual(receipt,bundle.install(REFERENCE,target,client))
            context.write_text(context.read_text()+'\nLater host instructions\n')
            extra=target/'.adik/hello/user.txt';extra.write_text('host addition')
            before=context.read_text();bundle.remove(target,'hello',dry_run=True)
            self.assertEqual(context.read_text(),before)
            bundle.remove(target,'hello')
            self.assertEqual(extra.read_text(),'host addition');self.assertEqual(unrelated.read_text(),'host')
            self.assertIn('Host instructions',context.read_text());self.assertIn('Later host instructions',context.read_text())
            self.assertNotIn('ADIK:hello',context.read_text())
    def test_modified_owned_file_aborts_before_any_removal(self):
        target=self.root/'app';receipt=bundle.install(REFERENCE,target,'codex')
        owned=target/next(iter(receipt['files']));owned.write_text('user edit')
        before={p.relative_to(target):p.read_bytes() for p in target.rglob('*') if p.is_file()}
        with self.assertRaises(ContractError):bundle.remove(target,'hello')
        self.assertEqual(before,{p.relative_to(target):p.read_bytes() for p in target.rglob('*') if p.is_file()})
    def test_refuses_unowned_bundle_or_skill(self):
        for directory in ['.adik/hello','.agents/skills/hello-implement-hello']:
            target=self.root/directory.replace('/','-');(target/directory).mkdir(parents=True)
            with self.assertRaises(ContractError):bundle.install(REFERENCE,target,'codex')
            self.assertFalse((target/'AGENTS.md').exists())
    def test_multiple_bundles_share_context(self):
        other=self.fixture();data=json.loads((other/'adik.manifest.json').read_text());data['id']='another';write_json(other/'adik.manifest.json',data)
        target=self.root/'app';bundle.install(REFERENCE,target,'codex');bundle.install(other,target,'codex')
        bundle.remove(target,'hello')
        self.assertIn('ADIK:another:START',(target/'AGENTS.md').read_text());validate_bundle(target/'.adik/another')
    def test_receipt_cannot_claim_host_file(self):
        target=self.root/'app';bundle.install(REFERENCE,target,'codex')
        receipt_path=target/'.adik/.receipts/hello.json';data=json.loads(receipt_path.read_text());data['files']['host.txt']='x';write_json(receipt_path,data)
        with self.assertRaises(ContractError):bundle.remove(target,'hello')
        self.assertTrue((target/'.adik/hello/adik.manifest.json').exists())
    def test_bundle_id_cannot_collide_with_receipt_directory(self):
        root=self.fixture();data=json.loads((root/'adik.manifest.json').read_text())
        data['id']='installed';write_json(root/'adik.manifest.json',data)
        target=self.root/'app';bundle.install(root,target,'codex')
        validate_bundle(target/'.adik/installed')
        bundle.remove(target,'installed')
    def test_symlink_target_is_rejected_before_writes(self):
        target=self.root/'app';target.mkdir();outside=self.root/'outside';outside.mkdir()
        (target/'.adik').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(ContractError):bundle.install(REFERENCE,target,'codex')
        self.assertEqual(list(outside.iterdir()),[])
    def test_cli_reports_failure(self):
        root=self.fixture();(root/'sdk/python/hello_sdk/__init__.py').unlink()
        result=self.run_cli(ROOT/'scripts/adik-bundle.py','validate','--bundle',root,ok=False)
        self.assertIn('FAIL',result.stderr)


class WorkflowTests(Workspace):
    def test_producer_deploy_embed_eject_preserves_host(self):
        target=self.root/'producer';(target/'agents').mkdir(parents=True)
        (target/'agents/host.md').write_text('host');(target/'AGENTS.md').write_text('host instructions\n')
        self.run_cli(ROOT/'scripts/adik-deploy.py','--source',ROOT,'--target',target,'--embed','--force')
        self.assertTrue((target/'adik-lint.py').is_file())
        self.assertIn('`Registry.md`',(target/'AGENTS.md').read_text())
        self.assertNotIn('`Registry.index.md`',(target/'AGENTS.md').read_text())
        (target/'sdk').mkdir();(target/'sdk/generated.py').write_text('preserve')
        (target/'skills/build-adik/SKILL.md').write_text('producer customization')
        self.run_cli(ROOT/'scripts/adik-eject.py','--target',target,'--confirm')
        self.assertEqual((target/'agents/host.md').read_text(),'host')
        self.assertEqual((target/'sdk/generated.py').read_text(),'preserve')
        self.assertEqual((target/'skills/build-adik/SKILL.md').read_text(),'producer customization')
        self.assertIn('host instructions',(target/'AGENTS.md').read_text())
        self.assertNotIn('ADIK:PRODUCER',(target/'AGENTS.md').read_text())
        self.assertFalse((target/'ADIK.md').exists())
    def test_legacy_removal_refuses_without_receipt(self):
        (self.root/'agents').mkdir();(self.root/'agents/host.md').write_text('keep')
        self.run_cli(ROOT/'scripts/adik-eject.py','--target',self.root,'--confirm',ok=False)
        self.assertTrue((self.root/'agents/host.md').exists())
    def test_mcp_blocks_invalid_registry_and_hands_off_complete_bundle(self):
        import adik_mcp_server as server
        with patch.object(server,'_find_project_root',return_value=self.root):
            self.assertEqual(json.loads(server.adik_build_sdk())['status'],'BLOCKED')
            write_json(self.root/'contracts/registry.json',REGISTRY)
            write_json(self.root/'adik.config.json',{'consumerFrameworks':['react'],'outputDir':'generated/hello'})
            result=json.loads(server.adik_build_sdk())
            self.assertEqual(result['status'],'READY');self.assertEqual(result['action'],'build_adik')
            self.assertEqual(result['context']['consumerFrameworks'],['react'])
            self.assertEqual(result['context']['outputDir'],'generated/hello')
            self.assertEqual(len(json.loads(server.adik_get_registry())['symbols']),1)
            bundle.install(REFERENCE,self.root,'codex')
            result=json.loads(server.adik_implement('.adik/hello'))
            self.assertEqual(result['action'],'implement_adik');self.assertTrue(result['skillFiles'])
    def test_reference_behavior_matches_source_and_consumer(self):
        sdk=module('hello_sdk','examples/hello-adik/sdk/python/hello_sdk/__init__.py')
        source=module('hello_source','examples/producer/hello.py')
        with patch.dict(sys.modules,{'hello_sdk':sdk}):
            app=module('consumer','examples/consumer/app.py')
            for name in ['Ada','  Ada  ','世界']:
                self.assertEqual(sdk.greet(name),source.greet(name))
                self.assertEqual(app.welcome(name)['status'],200)
            for name in ['', '  ',None,42]:
                for implementation in [source,sdk]:
                    with self.assertRaises((TypeError,ValueError)):implementation.greet(name)
                self.assertEqual(app.welcome(name)['status'],400)
    def test_installed_bundle_works_without_producer_repository(self):
        target=self.root/'consumer';bundle.install(REFERENCE,target,'codex')
        sdk=target/'.adik/hello/sdk/python'
        script="from hello_sdk import greet; assert greet(' Ada ') == 'Hello, Ada!'"
        result=subprocess.run([sys.executable,'-c',script],cwd=target,env={**os.environ,'PYTHONPATH':str(sdk),'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        validate_bundle(target/'.adik/hello')


if __name__=='__main__':unittest.main()
