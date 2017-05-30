fields = {
  'reminders': {
    'to': {
      'placeholder': 'your-email-address@example.com',
      'help': 'The email address to which we will send the reminders.',
      'default': ''
    }
  },
  'sites': {
    'theme': {
      'placeholder': 'subtle',
      'help': 'A theme name, chosen from one of the <a target="_blank" '
              'href="https://github.com/websitesfortrello/classless/'
              'tree/gh-pages/themes">classless</a> themes.',
      'default': 'lebo'
    },
    'domain': {
      'placeholder': 'mysite',
      'help': 'Any value. Your site will be served at '
              'http://&lt;domain&gt;.on.flowi.es/',
      'default': ''
    }
  },
  'email': {
    'from': {
      'placeholder': '"*" or "any" to allow any address',
      'help': 'An email address from which to accept updates.',
      'default': '*'
    },
    'alias': {
      'placeholder': 'my-workflowy-list-super',
      'help': 'The email address to which updates to this list should be '
              'sent. To update the list, you will send emails to '
              '&lt;alias&gt;@flowi.es',
      'default': '{{ wfshid }}'
    }
  }
}
