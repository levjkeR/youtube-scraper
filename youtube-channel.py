import requests

x_YOUTUBE_CLIENT_NAME = '1'

# Single session initialization
session = requests.Session()
session.headers['User-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                                'Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.72 '

api_endpoint = "https://www.youtube.com/youtubei/v1/browse"

INNERTUBE_CLIENT = {
    'web': {
        'INNERTUBE_API_KEY': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
        'INNERTUBE_CONTEXT': {
            'client': {
                'clientName': 'WEB',
                'clientVersion': '2.20211221.00.00',
            }
        }
    }
}

