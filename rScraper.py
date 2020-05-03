from .utils import scriptToJSON, datetimeFromTimestamp, get, preprocessCodes
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

def posts(soup):
    posts = []
    script = soup.find('script', id = 'data')
    if script:
        script = scriptToJSON(script.text)
    else:
        return posts
    script = json.loads(script)
    try:
        allPosts = script["posts"]["models"]
    except (KeyError, TypeError):
        print("Major Error")
        return []
    for p in allPosts.values():
        post = {
            "poster": {
                "id": "",
                "username": "",
                "link": ""
            },
            "post_id": "",
            "post_link": "",
            "timestamp": "",
            "subreddit": {
                "id": "",
                "name": "",
                "link": "",
            },
            "is_promoted": False,
            "text": "",
            "media": "",
            "statistics": {
                "upvote_ratio": 0,
                "num_comments": 0,
                "num_crossposts": 0,
                "score": 0
            }
        }
        post["post_id"] = p.get("postId", '')
        post["poster"]["id"] = p.get('authorId', '')
        post["poster"]["username"] = p.get('author', '')
        if post["poster"]["username"] != "":
            post["poster"]["link"] = 'https://www.reddit.com/user/' + post["poster"]["username"]
        post["text"] = p.get('title', '')
        post["statistics"]["num_comments"] = p.get('numComments', 0)
        post["statistics"]["num_crossposts"] = p.get('numCrossposts', 0)
        post["statistics"]["score"] = p.get('score', 0)
        post["statistics"]["upvote_ratio"] = p.get('upvoteRatio', 0)
        post["post_link"] = p.get('permalink', '')
        try:
            if p["belongsTo"]["type"] == 'subreddit':
                post["subreddit"]["id"] = p["belongsTo"]["id"]
                post["subreddit"]["name"] = post["post_link"].partition("/r/")[2].partition("/")[0]
                post["subreddit"]["link"] = "".join(post["post_link"].partition(f'/r/{post["subreddit"]["name"]}')[:-1])
            elif p["belongsTo"]["type"] == 'profile':
                post["is_promoted"] = True
            post["media"] = p["media"]["content"]
        except (KeyError, TypeError):
            pass
        ti = p.get('created')
        if ti:
            ti = round(ti/1000)
            post["timestamp"] = datetimeFromTimestamp(ti)
        posts.append(post)
    return posts

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
        "timestamp": "",
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
            basic["timestamp"] = datetimeFromTimestamp(g.get('created'))
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
