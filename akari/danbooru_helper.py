import requests

"""
    just a simple switch-case for category_id to category's string
    i know it could be better if using match-case introduced in python3.10
    but for legacy, just do this dummy thing
"""


def category_formatter(category_id):
    if category_id == 0:
        return "general"
    elif category_id == 1:
        return "artist"
    elif category_id == 3:
        return "copyright"
    elif category_id == 4:
        return "character"
    elif category_id == 5:
        return "meta"
    else:
        raise ValueError("unknown category: %s", category_id)


"""
    a function for searching tag category, 
    using simple requests to query tags by Danbooru API
    
    :parameter
        tag_name: str : tag name to be queried
        proxy: dict : set proxy for request, default is None
        
    :return
        category_name: str : the result of query: 
                            including "general"/"artist"/"copyright"/"character"/"meta"
    
    :exception
         ValueError: raise when parse bad parameter
         NotImplementedError: raise when the handler of status code is not implemented
"""


def search_tag_category(tag_name: str, proxy: dict = None):
    if proxy is None:
        resp = requests.get(
            url=f"https://danbooru.donmai.us/tags.json?search[name]={tag_name}&_method=GET")
    else:
        resp = requests.get(url=f"https://danbooru.donmai.us/tags.json?search[name]={tag_name}&_method=GET",
                            proxies=proxy)

    # See danbooru wiki https://danbooru.donmai.us/wiki_pages/help%3Aapi

    if resp.status_code == 200:
        return category_formatter(resp.json()[0]["category"])
    elif resp.status_code == 400:
        raise ValueError("Bad parameter for parsing")
    elif resp.status_code == 502:
        raise UserWarning("Unavailable due to heavy traffic")
    elif resp.status_code == 503:
        raise UserWarning("Site down")
    else:
        raise NotImplementedError(f"{resp.status_code} is not handled.\n " +
                                  f"See danbooru wiki https://danbooru.donmai.us/wiki_pages/help%3Aapi")
