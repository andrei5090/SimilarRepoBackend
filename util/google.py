import requests

API_KEY = "AIzaSyB81vXMOsNOF-xRo_Lh7NXKaA3u9BQgWqA"
SEARCH_ENGINE_ID = "5ab9439e0450be483"

#https://www.googleapis.com/customsearch/v1/siterestrict?key=AIzaSyB81vXMOsNOF-xRo_Lh7NXKaA3u9BQgWqA&cx=5ab9439e0450be483&q=test&start=1
def get_start_no(page):
    return (page - 1) * 10 + 1


def google_search(query, pages=7):
    global API_KEY
    global SEARCH_ENGINE_ID
    res = []

    for page in range(1, pages):
        start = get_start_no(page)
        url = f"https://www.googleapis.com/customsearch/v1/siterestrict?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}"
        data = requests.get(url).json()

        search_items = data.get("items")

        for i, search_item in enumerate(search_items, start=1):
            try:
                long_description = search_item["pagemap"]["metatags"][0]["og:description"]
            except KeyError:
                long_description = "N/A"
            title = search_item.get("title")
            snippet = search_item.get("snippet")
            html_snippet = search_item.get("htmlSnippet")
            link = search_item.get("link")
            res.append(link)
            # print("=" * 10, f"Result #{i + start - 1}", "=" * 10)
            # print("Title:", title)
            # print("Description:", snippet)
            # print("Long description:", long_description)
            # print("URL:", link, "\n")

    res_set = []
    for i in res:
        if i.count('/') == 4 and i.count('?') == 0 and i.count('https://github.com') == 1 and i.count("topics") == 0 and i.count("https://github.com/blog/") == 0:
            res_set.append(i)

    return {'links': res_set}
