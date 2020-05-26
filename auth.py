import json
from jose import jwt
from urllib.request import urlopen
from functools import wraps
from flask import request, abort

AUTH0_DOMAIN = 'dev-sbac.auth0.com'
API_AUDIENCE = 'sendhug'
ALGORITHMS = ['RS256']
