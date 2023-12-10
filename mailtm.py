import socket
from multiprocessing.connection import Client

import requests
import time
import json

MAILTM_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


class MailTmError(Exception):
    pass


def _make_mailtm_request( request_fn, timeout=600 ):
    tstart = time.monotonic()
    error = None
    status_code = None
    while time.monotonic() - tstart < timeout:
        try:
            print( "trying" )
            r = request_fn()
            status_code = r.status_code
            if status_code == 200 or status_code == 201:
                return r.json()
            if status_code != 429:
                break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            error = e
        time.sleep(1.0)

    if error is not None:
        raise MailTmError(error) from error
    if status_code is not None:
        raise MailTmError(f"Status code: {status_code}")
    if time.monotonic() - tstart >= timeout:
        raise MailTmError("timeout")
    raise MailTmError("unknown error")


def get_mailtm_domains():
    def _domain_req():
        return requests.get("https://api.mail.tm/domains", headers=MAILTM_HEADERS)

    r = _make_mailtm_request(_domain_req)

    return [x['domain'] for x in r]


def create_mailtm_account(address, password):
    account = json.dumps({"address": address, "password": password})

    def _acc_req():
        return requests.post("https://api.mail.tm/accounts", data=account, headers=MAILTM_HEADERS)

    r = _make_mailtm_request( _acc_req )
    assert len(r['id']) > 0

def main() :
    print( "Main Executing" )
    createAccount()
    getToken()
    connectionToServer = connectToLocalServer()
    listenForIncomingEmails()

def createAccount() :
    print(get_mailtm_domains())
    create_mailtm_account( "kabamutambialwaysat1999@wireconnected.com", "123456789" )

def getToken() :
    account = json.dumps( { "address": "kabamutambialwaysat1999@wireconnected.com", "password": "123456789" } )
    def _token_request() :
        return requests.post( "https://api.mail.tm/token", data = account, headers = MAILTM_HEADERS )
    r = _make_mailtm_request( _token_request )
    print( r )

def connectToLocalServer() :
    server_address = ( 'localhost', 18000 )

    client_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

    try:
        # Connect to the server
        client = Client()
        client_socket.connect( server_address )

        mail_title = "Subject"
        mail_body = "Hello, this is the body of the email."
        await client.call('send_mail', mail_title, mail_body)

    except Exception as e :
        print( "Exception occurred while connecting to the server" )
    return client_socket

def listenForIncomingEmails() :
    while True :
        try:
            getEmails()
        except Exception as e:
            print( e )
        time.sleep( 60000 )

def getEmails() :
    def _mails_request() :
        token = json.dumps( { "Authorization": "Bearer TOKEN 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3MDIyMDE4NDAsInJvbGVzIjpbIlJPTEVfVVNFUiJdLCJhZGRyZXNzIjoia2FiYW11dGFtYmlhbHdheXNAd2lyZWNvbm5lY3RlZC5jb20iLCJpZCI6IjY1NzU4NDQ4YzRhZDg4MmFmYzAyMDg0YSIsIm1lcmN1cmUiOnsic3Vic2NyaWJlIjpbIi9hY2NvdW50cy82NTc1ODQ0OGM0YWQ4ODJhZmMwMjA4NGEiXX19.028IJSfvp3fLO8pAUTOfi6SEVJLV7NWRUA1uSD0k5lVDQNrp0eOR-4FBh0vJEbQMtpUSIKXJZxESe3k2yJNBEw' "} )
        return requests.get( "https://api/mail.tm/messages", data = token, headers = MAILTM_HEADERS )
    r = _make_mailtm_request( _mails_request )
    print( r )



if __name__ == "__main__" :
    main()