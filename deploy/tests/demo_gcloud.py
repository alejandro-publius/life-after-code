#!/usr/bin/env python3
"""Demo cloud responses for destructive-script tests. No Google calls occur."""
import json, os, pathlib, sys
args = sys.argv[1:]
p = pathlib.Path(os.environ['LAC_MOCK_REMOTE'])
s = json.loads(p.read_text()) if p.exists() else {'project': {'projectNumber': '123456789012', 'labels': {}}, 'apis': ['storage.googleapis.com', 'cloudresourcemanager.googleapis.com', 'serviceusage.googleapis.com'], 'resources': {}, 'budgets': [], 'bindings': [], 'commands': [], 'backup': None}
s['commands'].append(args)

def save():
    p.write_text(json.dumps(s))

def out(value):
    save()
    print(json.dumps(value))
    sys.exit(0)

def flag(key, default=None):
    return next((a.split('=', 1)[1] for a in args if a.startswith('--' + key + '=')), default)

def denied():
    save()
    print('ERROR: (PERMISSION_DENIED) permission rejected', file=sys.stderr)
    sys.exit(1)

def missing():
    save()
    print('ERROR: (NOT_FOUND) resource was not found', file=sys.stderr)
    sys.exit(1)

def key(prefix):
    return prefix + ':' + next((a for a in args[len(prefix.split()) + 1:] if not a.startswith('--')), '')
if args[:2] == ['billing', 'budgets'] and 'billingbudgets.googleapis.com' not in s['apis']:
    save()
    print('ERROR: (SERVICE_DISABLED) budget API disabled', file=sys.stderr)
    sys.exit(1)
if args[:3] == ['billing', 'projects', 'describe'] and 'cloudbilling.googleapis.com' not in s['apis']:
    save()
    print('ERROR: (SERVICE_DISABLED) billing API disabled', file=sys.stderr)
    sys.exit(1)
if os.environ.get('LAC_MOCK_PERMISSION') and os.environ['LAC_MOCK_PERMISSION'] in ' '.join(args):
    denied()
if args[:2] == ['projects', 'describe']:
    out(s['project'])
if args[:3] == ['billing', 'projects', 'describe']:
    out({'billingEnabled': True, 'billingAccountName': 'billingAccounts/ABCDEF-123456-UVWXYZ'})
if args[:3] == ['billing', 'budgets', 'list']:
    out(s['budgets'])
if args[:3] == ['billing', 'budgets', 'create']:
    b = {'name': 'billingAccounts/ABCDEF-123456-UVWXYZ/budgets/demo', 'displayName': flag('display-name'), 'budgetFilter': {'projects': [flag('filter-projects')]}}
    s['budgets'].append(b)
    out(b)
if args[:3] == ['billing', 'budgets', 'update']:
    out({})
if args[:3] == ['billing', 'budgets', 'delete']:
    s['budgets'] = []
    out({})
if args[:2] == ['services', 'list']:
    out([{'config': {'name': a}} for a in s['apis']])
if args[:2] == ['services', 'enable']:
    s['apis'] = sorted(set(s['apis']) | {a for a in args[2:] if not a.startswith('--')})
    out({})
if args[:2] == ['services', 'disable']:
    s['apis'] = [a for a in s['apis'] if a not in args[2:]]
    out({})
if args[:3] == ['alpha', 'projects', 'update']:
    if flag('update-labels'):
        k, v = flag('update-labels').split('=')
        s['project']['labels'][k] = v
    if flag('remove-labels'):
        s['project']['labels'].pop(flag('remove-labels'), None)
    out({})
if args[:3] == ['beta', 'services', 'identity']:
    out({})
if args[:2] == ['projects', 'add-iam-policy-binding']:
    b = {'role': flag('role'), 'members': [flag('member')]}
    if b not in s['bindings']:
        s['bindings'].append(b)
    out({})
if args[:2] == ['projects', 'get-iam-policy']:
    out({'bindings': s['bindings']})
if args[:2] == ['projects', 'remove-iam-policy-binding']:
    s['bindings'] = [b for b in s['bindings'] if not (b['role'] == flag('role') and flag('member') in b['members'])]
    out({})
if args[:2] == ['builds', 'list']:
    out([])
if args[:2] == ['storage', 'cp']:
    src, dst = args[2:4]
    if src.startswith('gs://'):
        if s['backup'] is None:
            missing()
        pathlib.Path(dst).write_text(json.dumps(s['backup']))
    else:
        s['backup'] = json.loads(pathlib.Path(src).read_text())
    out({})
if args[:3] == ['storage', 'objects', 'describe']:
    if s['backup'] is None:
        missing()
    out({'name': 'bootstrap/state.json'})
if args[:2] == ['storage', 'rm']:
    s['resources'].pop('bucket', None)
    s['backup'] = None
    out({})
for prefix, typ in [(['storage', 'buckets'], 'bucket'), (['iam', 'service-accounts'], 'sa'), (['iam', 'workload-identity-pools', 'providers'], 'provider'), (['iam', 'workload-identity-pools'], 'pool'), (['artifacts', 'repositories'], 'artifact'), (['run', 'services'], 'run')]:
    if args[:len(prefix)] != prefix:
        continue
    op = args[len(prefix)]
    if op in ('add-iam-policy-binding',):
        out({})
    name = args[len(prefix) + 1] if len(args) > len(prefix) + 1 else ''
    identity = typ + ':' + name if typ == 'sa' else typ
    if op == 'describe':
        if identity not in s['resources']:
            missing()
        out(s['resources'][identity])
    if op in ('create', 'create-oidc'):
        value = {'description': flag('description'), 'labels': {}}
        if flag('labels'):
            k, v = flag('labels').split('=')
            value['labels'][k] = v
        if typ == 'artifact':
            value['format'] = 'DOCKER'
        if typ == 'sa':
            identity = 'sa:' + name + '@demo-project-123.iam.gserviceaccount.com'
        if typ in ('pool', 'provider'):
            value['state'] = 'ACTIVE'
        s['resources'][identity] = value
        out(value)
    if op in ('update', 'update-oidc'):
        if identity not in s['resources']:
            missing()
        if flag('update-labels'):
            k, v = flag('update-labels').split('=')
            s['resources'][identity]['labels'][k] = v
        out({})
    if op == 'delete':
        if typ in ('pool', 'provider'):
            s['resources'][identity]['state'] = 'DELETED'
        else:
            s['resources'].pop(identity, None)
        out({})
    if op == 'undelete':
        s['resources'][identity]['state'] = 'ACTIVE'
        out({})
if args[:2] == ['run', 'deploy']:
    k, v = flag('labels').split('=')
    s['resources']['run'] = {'metadata': {'labels': {k: v}}}
    out({})
print('Unknown mock command: ' + repr(args), file=sys.stderr)
sys.exit(2)
