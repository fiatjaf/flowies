import os
import sys
import json
import requests
from hashlib import md5
from wfapi import Workflowy


COUCHDB_URL = os.environ['COUCHDB_URL']


def main():
    res = requests.get(COUCHDB_URL + '/_design/apps/_view/apps').json()
    wfshids = {row['key'][1]: row['key'][4] for row in res['rows']}
    for wfshid, hash in wfshids.items():
        # TODO deal with deleted or unshared wfitems
        process(wfshid, hash)


def process(wfshid, hash=None):
    print('processing', wfshid, 'hash', hash)

    wf = Workflowy(wfshid)
    root = build(wf.root)

    newhash = md5(json.dumps(root, sort_keys=True).encode('utf-8')).hexdigest()
    print('newhash', newhash)
    if hash and hash == newhash:
        print('have not changed.\n')
        return

    r = requests.put(COUCHDB_URL + '/_design/apps/_update/update-data/' +
                     wfshid, data=json.dumps(root), params={'hash': newhash})
    print(r.text, r.headers)


def build(node):
    data = extract(node)
    data['children'] = []

    for child in node:
        data['children'].append(build(child))

    return data


def extract(node):
    return {
      'name': node.name,
      'note': node.description,
      'last': node.last_modified,
      'id': node.projectid,
      'cp': node.is_completed
    }


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        process(sys.argv[1])
    else:
        main()
