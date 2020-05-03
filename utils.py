from datetime import datetime
import requests

def get(query):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
    }
    try:
        r = requests.get(query, headers = headers)
    except requests.exceptions.RequestException as rExcep:
        print("Failed: ", rExcep)
        return ''
    if r.status_code == 200:
        return r.text
    else:
        print(r.status_code)
        return ''

def preprocessCodes(code):
    return "_".join(code.lower().split())

def scriptToJSON(script):
    return "{" + "}".join(script.partition("{")[2].split("}")[:-1]) + "}"

def datetimeFromTimestamp(timestamp):
    if timestamp:
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return ''

