#!/usr/bin/env python3

"""
Icinga2 check that performs a simple authentication request
on a given Moodle instance
"""

__author__ = "Niels Gandraß"
__email__ = "ngandrass@squacu.de"
__copyright__ = "Copyright 2018, Niels Gandraß"
__license__ = "MIT License"
__version__ = "1.0.1"

import sys
import requests
import argparse
from urllib.parse import urljoin

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--target', required=True, help='URL of the Moodle installation')
parser.add_argument('-u', '--username', required=True, help='Username to use for authentication')
parser.add_argument('-p', '--password', required=True, help='Password to use for authentication')
args = parser.parse_args()

# Try to login
try:
    login_request = requests.post(urljoin(args.target, 'login/index.php'), data={
        'username': args.username,
        'password': args.password
    })

    if login_request.status_code == 200 and login_request.url.endswith("/my/"):
        print("OK - Login as", args.username, "successful")
        sys.exit(0)
    elif login_request.status_code == 200 and not login_request.url.endswith("/my/"):
        print("CRITICAL - Login as", args.username, "failed")
        sys.exit(2)
    else:
        print("UNKNOWN - Status code: ", login_request.status_code)
        sys.exit(3)

except Exception as e:
    print("UNKNOWN - Exception raised:", type(e).__name__)
    sys.exit(3)
