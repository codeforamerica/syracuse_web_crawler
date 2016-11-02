from bs4 import BeautifulSoup
import requests
import itertools
import pprint

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


def retrieve_page_links(url): 
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
        for link in body.find_all('a'):
            href = link.get('href')
            if 'http' not in href:
                try:
                    requests.get(ROOT_URL + href)
                except Exception:
                    broken_links.append(href)
                else:
                    all_links.append(href)
            return all_links, broken_links 
    return [], []


ALL_PAGES = {} # url->Page object
ALL_BROKEN_LINKS = set()
    
class Page():
#     examples of targets dict {round:2, url: 'Home.apsx', count:1}
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

    def collect_links(self):
        [links, self.broken_targets] = retrieve_page_links(self.url)
        print('PAGE FXN')
        print(links, self.broken_targets)

        ALL_BROKEN_LINKS.update(set(self.broken_targets))
        for link in links:
            # handle anchor links 
            if '#' in link: 
                anchor = link.index('#')
                link = g[:anchor]
            if link not in ALL_PAGES:
                page = Page(link, self.depth+1, self.categories)
                self.targets.append(page)
                ALL_PAGES[link] = page
            else:
                ALL_PAGES[link].up_count()
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
    import pdb; pdb.set_trace()

