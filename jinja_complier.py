import os
from jinja2 import Environment, FileSystemLoader
from scraper import SYRACUSE_SITE_CATEGORIES, Page
import pickle

path = '.'
all_pages = pickle.load(open(path+'/all_pages.pickle', 'rb'))
broken_links = pickle.load(open(path+'/all_broken_links.pickle', 'rb'))

pages = list(all_pages.values())
pages.sort(key=lambda x: x.count, reverse=True)
top_pages = pages[0:200]

PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)

def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

def create_index_html():
    fname = "index.html"

    svgs = []
    for category in SYRACUSE_SITE_CATEGORIES:
        name = category.replace('_',' ')
        count = [p for p in all_pages.values() if category in p.categories]
        dpt = {'href':'graphs/' + category + '.html',
                'name':name,
                'count':len(count)}
        svgs.append(dpt)

    for p in all_pages.values():
        url_keys = list(p.broken_targets.elements())
        js_keys = []
        for k in url_keys:
            if 'javascript' in k:
                del p.broken_targets[k]
    pages_with_broken_links = [p for p in all_pages.values() if len(p.broken_targets) > 0]

    context = {
        'svgs': svgs,
        'all_pages_count':len(all_pages),
        'broken_links_count':len(pages_with_broken_links),
        'pages_with_broken_links':pages_with_broken_links,
        'top_pages':top_pages
    }

    #
    with open(fname, 'w') as f:
        html = render_template('base_layout.html', context)
        f.write(html)

create_index_html()