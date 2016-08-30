import os
import datetime
import requests

DOMAIN = 'sandbox54719.mailgun.org '
COUCHDB_URL = os.environ['COUCHDB_URL']
MAILGUN_URL = 'https://api:' + os.environ['MAILGUN_SECRET_KEY'] + \
              '@api.mailgun.net/v3/' + DOMAIN


def main():
    today = datetime.date.today()
    print('reminders for {}'.format(today.isoformat()))
    res = requests.get(COUCHDB_URL +
                       '/_design/reminders/_view/dates?key=[%s, %s, %s]' %
                       (today.year, today.month, today.day)).json()
    for row in res['rows']:
        val = row['value']
        url = 'https://workflowy.com/#/' + val['id']
        name = val['name']
        target = val['target']
        send_reminder(name, url, target)


def send_reminder(name, url, target):
    print('sending "{}" to {}.'.format(name, target))
    r = requests.post(MAILGUN_URL + '/messages', data={
        'from': 'Workflowy Item Reminder <reminder@%s>' % (DOMAIN),
        'to': target,
        'subject': '"%s" is due today' % (name),
        'text': 'The Workflowy item "%s" is due today. \nSee it at %s.' %
                (name, url)
    })
    print(r.text)


if __name__ == '__main__':
    main()
