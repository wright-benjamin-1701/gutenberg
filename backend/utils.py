import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime

import services
import cr

from models import Session, Asset, DownloadsData, SiteContent

def now():
    return datetime.datetime.now(datetime.timezone.utc).timestamp()

SECONDS_PER_DAY = 86400

def get_site_content():
    base_url = "https://www.gutenberg.org/browse/scores/top"
    retrieved = datetime.datetime.now(datetime.timezone.utc).timestamp()

    score_res = requests.get(base_url)
    content = score_res.text

    return retrieved, base_url, content

def get_dfs(content, retrieved):

    def extract_data_row(ele):
        a = ele.find("a")
        text = a.text
        href = a["href"]
        count_start = text.rfind("(")
        name = text[:count_start].strip()
        count = int(text[count_start + 1 : -1])

        return href, name, count

    dfs = {}
    data_list = []

    score_soup = BeautifulSoup(content, "html.parser")
    score_raw_data = score_soup.select("ol li")

    headings = [
        "Top 100 EBooks yesterday",
        "Top 100 Authors yesterday",
        "Top 100 EBooks last 7 days",
        "Top 100 Authors last 7 days",
        "Top 100 EBooks last 30 days",
        "Top 100 Authors last 30 days",
    ]

    for i in range(len(headings)):

        data_list = []

        for ii in range(100):
            data_list.append(extract_data_row(score_raw_data[i * 100 + ii]))

        dfs[headings[i]] = pd.DataFrame(data_list, columns=["asset", "name", "count"])

    return dfs

def update():

    session = Session()

    most_recent_retrieved = services.get_most_recent_download_timestamp(session)

    if now() - most_recent_retrieved >= SECONDS_PER_DAY/2:

        retrieved, url, content = get_site_content()

        site_content = SiteContent(retrieved=retrieved, url=url, content=content)
        cr.create_site_content(session=session, site_content_create=site_content)

        dfs = get_dfs(content, retrieved)

        services.translate_fetched_data_to_database(session, retrieved, dfs)

    session.close()