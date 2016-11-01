from bs4 import BeautifulSoup
import requests
import itertools
import pprint

SYRACUSE_SITE_CATEGORIES = {1:'Services', 
                            2:'Assessment', 
                            3:'Budget_Home_Page',
                            4:'Code_Enforcement', 
                           5: 'Community_Development',
                           6:'Dept_of_Public_Works', 
                           7:'ED_Home', 
                           8:'Engineering',
                           9: 'Finance_Dept',
                           10: 'Fire_Department',
                           11: 'Fleet_Management',
                           12:'Information_Systems',
                           13 : 'Lakefront', 
                           14: 'Law_Department', 
                           16: 'Personnel',
                           17: 'Police_Department', 
                           18: 'Purchase', 
                           19: 'Research_Department', 
                           20: 'Water_Department', 
                           21: 'Zoning', 
                           22: 'Other_Departments'}

def retrieve_page_links(self, url): 
    broken_links = []
    all_links = []

    try: 
        syr_site_map = requests.get(url)
        html = syr_site_map.text
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.body
        for link in body.find_all('a'):
            href = link.get('href')
            if href not in all_links: 
                all_links.append(href)
    except: 
        broken_links.append(url)

    return all_links, broken_links 

class Round():
    def __init__(self, count, all_links):
        self.count = count 
        self.all_links = []

class Node():
     def __init__(self, href, group, category):
        self.href = href
        self.group = group 
        self.category = category 
    
class Link():
    def __init__(self, source,target,category, target_broken=None):
        self.category = category
        self.source = source
        self.target = target 
        self.value = 1
        target_broken = False 
        
class SyracuseSiteMapScraper(): 
    def __init__(self):
        self.site_categories = SYRACUSE_SITE_CATEGORIES 
        self.d3_nodes = []
        self.internal_links = []
        self.url = 'http://www.syrgov.net/Sitemap.aspx'
        self.rounds = []
        
    def retrieve_group_num(self, key):
        for k,v in self.site_categories.items(): 
            if v == key: 
                return k 
    
    def retrieve_syracuse_site_map_body(self): 
        try: 
            syr_site_map = requests.get(self.url)
        except: 
            raise Exception(self.url + " errored during request.")
        html = syr_site_map.text
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.body
        return body 
        
    def create_page_nodes(self, key): 
        body = self.retrieve_syracuse_site_map_body()
        page_links = []
        nodes = []
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
                    self.internal_links.append(href)
                    group = self.retrieve_group_num(key)
                    page_links.append({"href":href, 
                                           "group":group, 
                                           "category":key, 
                                            "round":1})
        return page_links 

    def initialize_and_return_origin_nodes(self): 
        d3_nodes = []
        links = []
        for key in self.site_categories.values():
            nodes = self.create_page_nodes(key)
            d3_nodes += nodes 

        deduped_d3_nodes = [dict(t) for t in set([tuple(d.items()) for d in d3_nodes])]
        nodes = [Node(href=n['href'], group=n['group'], category=n['category']) for n in deduped_d3_nodes]
        self.d3_nodes = nodes 
            
        return nodes 
    
    def intialize_and_return_round_one_links(self):
        links = []
        for n in self.d3_nodes:
            r = requests.get(self.url + n.href)
            source='/'
            target=n.href
            category=n.category
            if r.ok == True: 
                target_broken=False
            else: 
                target_broken=True 
            l = Link(source='/', 
                     target=n.href, 
                     category=category,
                     target_broken=target_broken)
            links.append(l)
        round_one = Round(count=0, all_links=links)
        self.rounds.append(round_one)
        return links 
        
    
    def create_rounds(self, single_round): 
        
        round_num = len(self.rounds)
        last_round = self.rounds[len(self.rounds) - 1]
        origin_links = [link.target for link in last_round.all_links]
        
        single_round = Round(count=round_num, origin_links=origin_links)
        for url in single_round.origin_links:
            all_links, broken_links = retrieve_page_links(url)
            for link in all_links: 
                link = Link(source=url, target=link) 
                single_round.all_links.append(link)
                single_round.target_urls.append(link)
            for link in broken_links: 
                link = Link(source=url, target=link, target_broken=True) 
                single_round.all_links.append(link)
        self.rounds.append(single_round)