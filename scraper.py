from bs4 import BeautifulSoup
import requests
import requests_cache
import itertools
import pprint

import pickle

requests_cache.install_cache('syracuse_web_crawler_cache')

ROOT_URL = 'http://www.syrgov.net'
SITE_MAP_URL = ROOT_URL + '/Sitemap.aspx'
SYRACUSE_SITE_CATEGORIES = ['Services',
                            'Assessment',
                            'Budget_Home_Page',
                           'Code_Enforcement',
                           'Community_Development',
                           'Dept_of_Public_Works',
                           'ED_Home',
                           'Engineering',
                           'Finance_Dept',
                           'Fire_Department',
                           'Fleet_Management',
                           'Information_Systems',
                           'Lakefront',
                           'Law_Department',
                           'Personnel',
                            'Police_Department',
                           'Purchase',
                           'Research_Department',
                           'Water_Department',
                          'Zoning',
                           'Other_Departments']

ALL_PAGES = {} # url->Page object
ALL_BROKEN_LINKS = set()


def retrieve_page_links(url,):
    if url.startswith('mailto') or url.endswith('docx') or \
            url.endswith('pdf') or url.endswith('doc'):
        return [], []
    broken_links = []
    all_links = []

    # deal with inconsistent links
    if not '/' in url:
        url = '/' + url

    syr_site_map = requests.get(ROOT_URL + url)
    html = syr_site_map.text
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.body
    if body:
        links =  body.find_all('a')
        if links:
            urls = []
            for link in links:
                href = link.get('href')
                if href and 'http' not in href:
                    urls.append(href)
            links = urls
        else:
            links = []
        print(links)
        for href in links:
            if not '/' in href:
                href = '/' + href
            try:
                res = requests.get(ROOT_URL + href)
            except Exception:
                broken_links.append(href)
            else:
                if res.status_code == 404:
                    broken_links.append(href)
                else:
                    all_links.append(href)
        return all_links, broken_links
    return [], []


class Page():
    def __init__(self, url, depth=None, categories=None):
        self.url = url
        self.targets = []
        self.broken_targets = []
        if depth:
            self.depth=depth
        else:
            self.depth = 0
        self.count = 1
        self.categories=set(categories,)


    def __unicode__(self):
        return self.url

    def up_count(self):
        self.count += 1

    def add_categories(self, categories):
        self.categories.update(categories)

    def set_depth(self, depth):
        if depth < self.depth:
            self.depth=depth

    def collect_links(self):
        print('PAGE FXN:' + self.url)
        [links, self.broken_targets] = retrieve_page_links(self.url)
        print(links, self.broken_targets)

        ALL_BROKEN_LINKS.update(set(self.broken_targets))
        for link in links:
            # handle anchor links
            if '#' in link:
                anchor = link.index('#')
                link = link[:anchor]
            if link not in ALL_PAGES:
                page = Page(link, self.depth+1, self.categories)
                self.targets.append(page)
                ALL_PAGES[link] = page
            else:
                ALL_PAGES[link].up_count()
                ALL_PAGES[link].set_depth(self.depth)
                if self.categories:
                    ALL_PAGES[link].add_categories(self.categories)
        for target in self.targets:
            target.collect_links()



def retrieve_syracuse_site_map_body():
    try:
        syr_site_map = requests.get(SITE_MAP_URL)
    except:
        raise Exception(url + " errored during request.")
    html = syr_site_map.text
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.body
    return body

def initialize_origin_pages():
    internal_links = []
    body = retrieve_syracuse_site_map_body()
    for key in SYRACUSE_SITE_CATEGORIES:
        href= '/' + key + '.aspx'
        f = body.find(href=href)
        try:
            lis = f.parent.parent.findChildren()
        except:
            raise Exception(href + ' not found while parsing html')
        for li in lis:
            links = li.find_all('a')
            for l in links:
                href = l.get('href')
                if 'http' not in href:
                    page_data = {'url':href, 'category':key}
                    internal_links.append(page_data)

    top_pages = []
    for l in internal_links:
        url = l['url']
        categories = [l['category']]
        page = Page(url=url,categories=categories)
        if url not in ALL_PAGES:
            ALL_PAGES[url] = page
            page.collect_links()
            top_pages.append(page)
        else:
            ALL_PAGES[url].add_categories(categories)
    return top_pages

if __name__ == "__main__":
    top_pages = initialize_origin_pages()
    pickle.dump(top_pages, open('./top_pages.pickle', 'wb'))
    pickle.dump(ALL_PAGES, open('./all_pages.pickle', 'wb'))
    pickle.dump(ALL_BROKEN_LINKS, open('./all_broken_links.pickle', 'wb'))

