import os

PORT = int(os.getenv('PORT', '5000'))
COUCHDB_URL = os.getenv('COUCHDB_URL')
REMEMBER_COOKIE_NAME = 'rmeflowies'
SECRET_KEY = os.getenv('SECRET', 'whiplash')
