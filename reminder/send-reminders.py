import os
import json
import datetime
import requests

DOMAIN = 'flowi.es'
COUCHDB_URL = os.environ['COUCHDB_URL']
MAILGUN_URL = 'https://api:' + os.environ['MAILGUN_SECRET_KEY'] + \
              '@api.mailgun.net/v3/' + DOMAIN


def main():
    today = datetime.date.today()
    print('reminders for {}'.format(today.isoformat()))
    res = requests.get(
        COUCHDB_URL + '/_design/reminders/_view/dates',
        params={
            'key': json.dumps([today.year, today.month, today.day])
        }
    ).json()
    for row in res['rows']:
        val = row['value']
        url = 'https://workflowy.com/#/' + val['id']
        name = val['name']
        note = val['note']
        target = val['target']
        send_reminder(name, note, url, target)


def send_reminder(name, note, url, target):
    print('sending "{}" to {}.'.format(name, target))
    r = requests.post(MAILGUN_URL + '/messages', data={
        'from': 'Workflowy Item Reminder <reminder@%s>' % (DOMAIN),
        'to': target,
        'subject': '"%s" is due today' % (name),
        'text': '''Workflowy item due today: "{name}"

{name} {url}

  {note}
        '''.format(
            name=name,
            note=note,
            url=url
        )
    })
    print(r.text)


if __name__ == '__main__':
    main()
