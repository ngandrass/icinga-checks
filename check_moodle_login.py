#!/usr/bin/env python3

"""
Icinga2 check that performs a simple authentication request
on a given Moodle instance
"""

__author__ = "Niels Gandraß"
__email__ = "ngandrass@squacu.de"
__copyright__ = "Copyright 2018, Niels Gandraß"
__license__ = "MIT License"
__version__ = "2.0.0"

import sys
import requests
import argparse
import re
from enum import Enum

from urllib.parse import urljoin


class IcingaVerdict(Enum):
    """
    Exit codes for the corresponding verdicts
    """
    OK = 0,
    WARNING = 1,
    CRITICAL = 2,
    UNKNOWN = 3


def exit(verdict: IcingaVerdict, *msgs: str) -> None:
    """
    Prints test verdict and exits with appropriate exit code
    :param verdict: Verdict of the test
    :param msgs: Additional messages
    :return: None
    """
    print(verdict.name, "-", " ".join(msgs))
    sys.exit(verdict.value)


def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', required=True, help='URL of the Moodle installation')
    parser.add_argument('-u', '--username', required=True, help='Username to use for authentication')
    parser.add_argument('-p', '--password', required=True, help='Password to use for authentication')
    parser.add_argument('-s', '--skip-logintoken', required=False, help='Ignore moodle logintoken', action='store_true')
    args = parser.parse_args()

    # Initiate common session in order to supply a valid login token
    s = requests.Session()

    # Get login token
    logintoken = ""
    if not args.skip_logintoken:
        try:
            token_request = s.get(urljoin(args.target, 'login/index.php'))

            if token_request.status_code == 200:
                logintoken_input = re.search("<input type=\"hidden\" name=\"logintoken\" value=\"([a-zA-Z0-9]+)\">", token_request.text)

                if not logintoken_input:
                    exit(IcingaVerdict.UNKNOWN, "Couldn't find logintoken")
                else:
                    logintoken = logintoken_input.group(1)
            else:
                exit(IcingaVerdict.UNKNOWN, "Received HTTP status code during token request:", str(token_request.status_code))

        except Exception as e:
            exit(IcingaVerdict.UNKNOWN, "Exception raised during token request:", type(e).__name__)

    # Try to login
    try:
        login_request = s.post(urljoin(args.target, 'login/index.php'), data={
            'username': args.username,
            'password': args.password,
            'logintoken': logintoken
        })

        sc = login_request.status_code

        # Evaluate login try
        if sc == 200 and login_request.url.endswith("/my/"):
            exit(IcingaVerdict.OK, "Login as", args.username, "successful")
        elif sc == 200 and not login_request.url.endswith("/my/"):
            exit(IcingaVerdict.CRITICAL, "Login as", args.username, "failed")
        elif (400 <= sc <= 405) or (500 <= sc <= 504):
            exit(IcingaVerdict.CRITICAL, "Failed with HTTP status code", str(sc))
        else:
            exit(IcingaVerdict.UNKNOWN, "Received HTTP status code:", str(sc))

    except Exception as e:
        exit(IcingaVerdict.UNKNOWN, "Exception raised during login:", type(e).__name__)


if __name__ == "__main__":
    main()
