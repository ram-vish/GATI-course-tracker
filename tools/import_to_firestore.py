"""One-time copy of tracker data into Firestore.

Reads the JSON files exported from the Claude version of the tracker
(one file per document, as courses/<id>.json and config/main.json) and
writes them to Firestore with the REST API. Also creates the first
program-team profiles.

Usage:
  python3 tools/import_to_firestore.py EXPORT_DIR emulator
  python3 tools/import_to_firestore.py EXPORT_DIR production   (needs `gcloud auth application-default login`)
"""
import json, os, subprocess, sys, urllib.request, glob, datetime

PROJECT = 'gati-course-tracker'
PROGRAM_TEAM = [
    ('ram.viswanath@tataiis.org', 'Ram Viswanath'),
    ('sourav.dasgupta@tataiis.org', 'Sourav Dasgupta'),
    ('preeti.chakravarty@tataiis.org', 'Preeti Chakravarty'),
]

def enc(v):
    if v is None: return {'nullValue': None}
    if isinstance(v, bool): return {'booleanValue': v}
    if isinstance(v, int): return {'integerValue': str(v)}
    if isinstance(v, float):
        return {'integerValue': str(int(v))} if v.is_integer() else {'doubleValue': v}
    if isinstance(v, str): return {'stringValue': v}
    if isinstance(v, list): return {'arrayValue': {'values': [enc(x) for x in v]}}
    if isinstance(v, dict): return {'mapValue': {'fields': {k: enc(x) for k, x in v.items()}}}
    raise TypeError(type(v))

def main(export_dir, target):
    if target == 'emulator':
        base = 'http://127.0.0.1:8080/v1'
        headers = {'Authorization': 'Bearer owner'}
    else:
        token = subprocess.check_output(['gcloud', 'auth', 'application-default', 'print-access-token'], text=True).strip()
        base = 'https://firestore.googleapis.com/v1'
        headers = {'Authorization': 'Bearer ' + token, 'x-goog-user-project': PROJECT}
    root = f'projects/{PROJECT}/databases/(default)/documents'
    docs = []
    for f in sorted(glob.glob(os.path.join(export_dir, 'courses', '*.json'))):
        docs.append(('courses/' + os.path.basename(f)[:-5], json.load(open(f))))
    cfg = json.load(open(os.path.join(export_dir, 'config', 'main.json')))
    cfg.pop('owners', None)
    docs.append(('config/main', cfg))
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    for email, name in PROGRAM_TEAM:
        docs.append(('users/' + email, {'name': name, 'role': 'program', 'gatis': [], 'mustChangePassword': True,
                                        'createdAt': now, 'createdBy': 'setup'}))
    for i in range(0, len(docs), 400):
        writes = [{'update': {'name': f'{root}/{path}', 'fields': {k: enc(v) for k, v in data.items()}}} for path, data in docs[i:i + 400]]
        req = urllib.request.Request(f'{base}/{root}:commit', data=json.dumps({'writes': writes}).encode(),
                                     headers={**headers, 'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req) as r:
            print('committed', len(writes), 'documents, status', r.status)
    print('done:', sum(p.startswith('courses/') for p, _ in docs), 'courses, 1 config,', len(PROGRAM_TEAM), 'people')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
