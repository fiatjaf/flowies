import json
import requests
from flask import request
from wfapi import Workflowy, error

import settings


def webhook():
    to = request.form['To'].split('@')[0].strip()
    sender = request.form['sender']
    title = request.form['subject']
    body = request.form['stripped-text']

    r = requests.get(settings.COUCHDB_URL + '/_design/email/_view/incoming',
                     params={'key': json.dumps(to)})
    rows = r.json()['rows']
    if not rows:
        return 'target list not found', 201

    row = rows[0]
    wfshid = row['id']
    restrict_from = row['value'].strip()

    # check email restriction
    if restrict_from != '*' and restrict_from != 'any':
        if sender != restrict_from:
            return 'address not allowed', 201

    print(wfshid, body)

    try:
        wf = Workflowy(wfshid)
    except error.WFLoginError:
        print('login error.')
        return 'login error', 201

    for child in wf.root:
        if child.name == title:
            node = child
            break
    else:
        node = wf.root.create()
        node.edit(name=title)

    lines = body.replace('*', '').replace('\u200b', '').splitlines()
    print(lines)
