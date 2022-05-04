import requests
import json
import time

from typing import Generator
from typing_extensions import Literal

X_YOUTUBE_CLIENT_NAME = '1'

# Single session initialization
session = requests.Session()
session.headers['User-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                                'Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.72'

session.cookies.set("CONSENT", "YES+cb", domain="youtube.com")

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


# Получить все видео с канала
def get_channel(channel_id: str = None, channel_url: str = None, limit: int = None,
                sleep: int = 1, sort_by: str = "newest"):
    sort_by_dict = {"newest": "dd", "oldest": "da", "popular": "p"}
    url = "{url}/videos?view=0&sort={sort_by}&flow=grid".format(
        url=channel_url or f"https://www.youtube.com/channel/{channel_id}",
        sort_by=sort_by_dict[sort_by],
    )
    videos = get_videos(url, "gridVideoRenderer", limit, sleep)
    for video in videos:
        yield video


def get_videos(url: str, param: str, limit: int, sleep: int):
    is_first, quit, count = True, False, 0
    client_data = INNERTUBE_CLIENT['web']['INNERTUBE_CONTEXT']['client']
    api_key = INNERTUBE_CLIENT['web']['INNERTUBE_API_KEY']

    while True:
        if is_first:
            html = get_html_data(session, url)
            session.headers["X-YouTube-Client-Name"] = X_YOUTUBE_CLIENT_NAME
            session.headers["X-YouTube-Client-Version"] = client_data['clientVersion']
            data = json.loads(parse_part_of_data(html, "var ytInitialData = ", "};")[20:] + "}")
            next_data = get_next_data(data)
            is_first = False
        else:
            data = get_data(session, api_key, next_data, client_data)
            next_data = get_next_data(data)
        for result in get_videos_items(data, param):
            try:
                count += 1
                yield result
                if count == limit:
                    quit = True
                    break
            except GeneratorExit:
                quit = True
                break
        if not next_data or quit:
            break

        time.sleep(sleep)

    session.close()


def parse_part_of_data(data: str, key: str, stop_key: str, skip: str = 0):
    start = data.find(key)
    end = data.find(stop_key, start + len(key) + skip)
    return data[start:end]


def get_html_data(session: requests.Session, url: str):
    response = session.get(url)
    if response.status_code == 200:
        html = response.text
        return html


def get_data(session: requests.Session, api_key: str, next_data: dict, client_data: dict):
    data = {
        "context": {"clickTracking": next_data["click_params"], "client": client_data},
        "continuation": next_data["token"],
    }
    response = session.post(api_endpoint, params={"key": api_key}, json=data).json()
    return response


# Запрос следующей порции данных
def get_next_data(data: dict):
    raw_next_data = next(search_dict(data, "continuationEndpoint"), None)
    if raw_next_data:
        next_data = {
            "token": raw_next_data["continuationCommand"]["token"],
            "click_params": {"clickTrackingParams": raw_next_data["clickTrackingParams"]},
        }
        return next_data


# The stack of iterators паттерн с использованием генератора, чтоб не было простоя и выполнять IO последовательно
def search_dict(partial: dict, search_key: str):
    stack = [partial]
    while stack:
        current_item = stack.pop(0)
        if isinstance(current_item, dict):
            for key, value in current_item.items():
                if key == search_key:
                    yield value
                else:
                    stack.append(value)
        elif isinstance(current_item, list):
            for value in current_item:
                stack.append(value)


def get_videos_items(data: dict, selector: str) -> Generator[dict, None, None]:
    return search_dict(data, selector)


if __name__ == '__main__':
    v = get_channel(channel_url='https://www.youtube.com/c/TheCyberMentor')
    for i in v:
        print(i['videoId'])