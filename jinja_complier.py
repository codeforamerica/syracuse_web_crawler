import os
from jinja2 import Environment, FileSystemLoader
from scraper import SYRACUSE_SITE_CATEGORIES

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
        dpt = {'href':'graphs/' + category + '.html', 'name':name}
        svgs.append(dpt)

    context = {
        'svgs': svgs
    }

    #
    with open(fname, 'w') as f:
        html = render_template('base_layout.html', context)
        f.write(html)

create_index_html()