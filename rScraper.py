from .utils import scriptToJSON, datetimeFromTimestamp, get, preprocessCodes, posts
from .codes import COUNTRY_CODES, TIME_CODES
from bs4 import BeautifulSoup
import json

def popularPosts(category = "hot", country = "everywhere", timePeriod = "now"):
    # forming the url for scraping top posts
    url = 'https://www.reddit.com/r/popular/'
    category = preprocessCodes(category)
    if category in ["hot", "new", "top", "rising"]:
        url += category
        if category == "hot":
            country = preprocessCodes(country)
            if country in COUNTRY_CODES:
                url = f'{url}?geo_filter={COUNTRY_CODES[country]}'
            else:
                print("Invalid country. Resorting to default.")
        elif category == "top":
            timePeriod = preprocessCodes(timePeriod)
            if timePeriod in TIME_CODES:
                url = f'{url}?t={TIME_CODES[timePeriod]}'
            else:
                print("Invalid time period. Resorting to default.")
    else:
        print("Invalid Category. Choose either of hot, new, top, rising")
        return []
    print("Fetching results from: ", url)

    # extracting content from data block
    return posts(BeautifulSoup(get(url), "html.parser"))

def subreddit(subreddit, category = "hot", timePeriod = "now"):
    # forming the url for scraping top posts
    url = 'https://www.reddit.com/r/'
    url += f'{subreddit}/'
    if category in ["hot", "new", "top", "rising"]:
        url += category
        if category == "top":
            timePeriod = preprocessCodes(timePeriod)
            if timePeriod in TIME_CODES:
                url = f'{url}?t={TIME_CODES[timePeriod]}'
            else:
                print("Invalid time period. Resorting to default.")
    else:
        print("Invalid Category. Choose either of hot, new, top, rising")
        return []
    print("Fetching results from: ", url)

    # retrieving general information
    basic = {
        "id": "",
        "name": "",
        "url": "",
        "category": "",
        "type": "",
        "description": "",
        "num_subscribers": 0,
        "currently_active": 0,
        "timestamp_created": "",
        "icon_media_directory": "",
        "num_moderators": 0,
        "top_moderators": [],
        "posts": []
    }
    soup = BeautifulSoup(get(f'{url}wiki/index'), "html.parser")
    s = soup.find('script', id = 'data')
    if s:
        k = json.loads(scriptToJSON(s.text))
    else:
        return basic
    sub = k.get('subreddits')
    if sub:
        g = sub.get('about')
        if g:
            g = list(g.values())[0]
            basic["category"] = g.get('advertiserCategory', '')
            basic["num_subscribers"] = g.get('subscribers', 0)
            basic["description"] = g.get('publicDescription', '')
            basic["timestamp_created"] = datetimeFromTimestamp(g.get('created'))
            basic["currently_active"] = g.get('accountsActive', 0)
        g = sub.get('models')
        if g:
            g = list(g.values())[0]
            basic["type"] = g.get('type', '')
            basic["name"] = g.get('name', '')
            basic["id"] = g.get('id', '')
            basic["url"] = "https://www.reddit.com" +  g.get('url', '')
            g = g.get('icon')
            if g:
                basic["icon_media_directory"] = g.get("url", '')
    sub = k.get('widgets')
    if sub:
        sub = sub.get('models')
        if sub:
            for widget in sub.values():
                if widget.get('kind', '') == "moderators":
                    g = widget.get('mods')
                    if g:
                        for m in g:
                            moder = {
                                'name': "",
                                "link": ""
                            }
                            moder["name"] = m.get('name', '')
                            moder["link"] = "https://www.reddit.com/user/" + moder["name"]
                            basic["top_moderators"].append(moder)
                    basic["num_moderators"] = widget.get("totalMods")
    
    # extracting content from data block
    basic["posts"] = posts(soup)

    return basic

def user(username, category = "hot", timePeriod = "now"):
    # forming the url for scraping top posts
    url = 'https://www.reddit.com/user/'
    url += f'{username}/posts/'
    if category in ["hot", "new", "top", "rising"]:
        url += f'?sort={category}'
        if category == "top":
            timePeriod = preprocessCodes(timePeriod)
            if timePeriod in TIME_CODES:
                url = f'{url}&t={TIME_CODES[timePeriod]}'
            else:
                print("Invalid time period. Resorting to default.")
    else:
        print("Invalid Category. Choose either of hot, new, top, rising")
        return []
    print("Fetching results from: ", url)

    # extracting data
    basic = {
        "id": "",
        "username": "",
        "url": "",
        "description": "",
        "icon_media_directory": "",
        "timestamp_created": "",
        "karma_points": {
            "comment_karma": 0,
            "post_karma": 0
        },
        "birthday": "",
        "subscribers": 0,
        "custom_feeds": [],
        "subreddits": [],
        "posts": []
    }
    soup = BeautifulSoup(get(url), "html.parser")
    s = soup.find('script', id = 'data')
    if s:
        k = json.loads(scriptToJSON(s.text))
    else:
        return basic
    g = soup.find('span', id = 'profile--id-card--highlight-tooltip--cakeday')
    if g:
        basic["birthday"] = g.text
    pk = k.get('profiles')
    if pk:
        pr = pk.get('about')
        if pr:
            pr = list(pr.values())[0]
            basic["description"] = pr.get('publicDescription', '')
            basic["karma_points"]["comment_karma"] = pr.get('commentKarma', 0)
            basic["karma_points"]["post_karma"] = pr.get('postKarma', 0)
            pr = pk.get('models')
            if pr:
                pr = list(pr.values())[0]
                basic["username"] = pr.get("name", "")
                basic["url"] = "https://www.reddit.com" + pr.get('url', "")
                g = pr.get('icon')
                if g:
                    basic["icon_media_directory"] = g.get('url', '')
                basic["subscribers"] = pr.get('subscribers', 0)
    pr = k.get('multireddits')
    if pr:
        pid = pr.get('byUserId')
        if pid:
            basic["id"] = list(pid.keys())[0]
        pr = pr.get('models')
        if pr:
            for p in pr.values():
                feed = {
                    "name": "",
                    "url": "",
                    "icon_media_directory": "",
                    "num_subreddits": 0,
                    "num_followers": 0,
                    "timestamp_created": "",
                    "visibility": ""
                }
                feed["name"] = p.get("name", "")
                feed["url"] = "https://www.reddit.com" + p.get("url", "")
                feed["icon_media_directory"] = p.get('icon', "")
                feed["num_subreddits"] = p.get("subredditCount", 0)
                feed["num_followers"] = p.get("followerCount", 0)
                feed["visibility"] = p.get("visibility", "")
                pk = p.get('created')
                if pk:
                    feed["timestamp_created"] = datetimeFromTimestamp(pk)
                basic["custom_feeds"].append(feed)
    pr = k.get("users")
    if pr:
        pr = pr.get("models")
        if pr:
            pr = list(pr.values())[0]
            pr = pr.get('created')
            if pr:
                basic["timestamp_created"] = datetimeFromTimestamp(pr)
    pr = k.get('subreddits')
    if pr:
        pr = pr.get('models')
        if pr:
            for m in pr.values():
                sub = {
                    "id": "",
                    "name": "",
                    "url": "",
                    "icon_media_directory": "",
                    "title": "",
                    "num_subscribers": 0,
                    "type": ""
                }
                sub["id"] = m.get("id", "")
                sub["name"] = m.get("name", "")
                sub["url"] = "https://www.reddit.com" + m.get("url", "")
                g = m.get('icon')
                if g:
                    sub["icon_media_directory"] = g.get('url', "")
                if sub["icon_media_directory"] == "":
                    sub["icon_media_directory"] = m.get("communityIcon", "")
                sub["title"] = m.get("title", "")
                sub["num_subscribers"] = m.get("subscribers", 0)
                sub["type"] = m.get("type", "")
                basic["subreddits"].append(sub)
    basic["posts"] = posts(soup)
    return basic
