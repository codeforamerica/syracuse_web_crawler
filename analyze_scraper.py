from collections import Counter
from scraper import *
import pickle
import igraph as ig
import plotly.plotly as py
from plotly.graph_objs import *
from plotly.offline import offline
from plotly.offline import plot
import plotly.graph_objs as go


path = '.'
all_pages = pickle.load(open(path+'/all_pages.pickle', 'rb'))
broken_links = pickle.load(open(path+'/all_broken_links.pickle', 'rb'))
top_pages = pickle.load(open(path+'/top_pages.pickle', 'rb'))

print('top pages: %i' % len(top_pages))
print('all pages: %i' % len(all_pages))
print('broken links: %i' % len(list(broken_links.elements())))


print('top 100 linked pages')
pages = list(all_pages.values())
pages.sort(key=lambda x: x.count, reverse=True)
for page in pages[0:100]:
    print('(%s)  %s: %i' % (','.join(page.categories),
        page.url, page.count))

print('pages with broken links')
pages.sort(key=lambda x: len(x.broken_targets), reverse=True)
for page in pages:
    broken_count = len(page.broken_targets)
    if broken_count==0:
        break
    print('(%s)  %s: %i' % (','.join(page.categories),
        page.url, broken_count))

print('mosted linked to broken links')
ms = broken_links.most_common(100)
for c in ms:
    print('%s: %s' % c)

def retrieve_node_group(categories):
    if categories:
        category = categories.pop()
        group = SYRACUSE_SITE_CATEGORIES.index(category)
    else:
        group = 22
    return group

def create_link_relationships(pages,category=None):
    if category:
        pages = list(filter(lambda page: category in page.categories, pages))
    nodes = []
    urls_to_nodes = {}
    for i, p in enumerate(pages):
        group = retrieve_node_group(p.categories)
        node = {"name":p.url, "group":group}
        nodes.append(node)
        urls_to_nodes[p.url] = i
    nodes_to_targets = []
    for i, p in enumerate(pages):
        for t in p.targets:
            if t.url in urls_to_nodes:
                nodes_to_targets.append((urls_to_nodes[p.url],
                                         urls_to_nodes[t.url]))
    links = {
        "nodes": nodes,
        "links": nodes_to_targets,
        }
    import pdb; pdb.set_trace()
    return links

def create_network_graph(pages, filename,category=None):
    if category:
        data = create_link_relationships(pages, category)
    else:
        data = create_link_relationships(pages)

    L=len(data['links'])
    Edges=data['links']
    G=ig.Graph(Edges, directed=True)

    labels=[]
    group=[]
    for node in data['nodes']:
        labels.append(node['name'])
        group.append(node['group'])
    print(category)
    layt=G.layout('kk', dim=3)
    print('built layout')
    N=len(layt)
    Xn=[layt[k][0] for k in range(N)]# x-coordinates of nodes
    Yn=[layt[k][1] for k in range(N)]# y-coordinates
    Zn=[layt[k][2] for k in range(N)]# z-coordinates
    Xe=[]
    Ye=[]
    Ze=[]
    for e in Edges:
        Xe+=[layt[e[0]][0],layt[e[1]][0], None]# x-coordinates of edge ends
        Ye+=[layt[e[0]][1],layt[e[1]][1], None]
        Ze+=[layt[e[0]][2],layt[e[1]][2], None]

    trace1=Scatter3d(x=Xe,
                y=Ye,
                z=Ze,
                mode='lines',
                line=Line(color='rgb(125,125,125)', width=1),
                hoverinfo='none'
                )
    trace2=Scatter3d(x=Xn,
                y=Yn,
                z=Zn,
                mode='markers',
                name='actors',
                marker=Marker(symbol='dot',
                                size=6,
                                color=group,
                                colorscale='Viridis',
                                line=Line(color='rgb(50,50,50)', width=0.5)
                                ),
                text=labels,
                hoverinfo='text'
                )


    axis=dict(showbackground=False,
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title=''
            )

    if category:
        title= filename.replace('_', ' ')
    else:
        title= "All Site Pages: Syracuse City Site Analysis"

    layout = Layout(
            title=title,
            width=1000,
            height=1000,
            showlegend=False,
            scene=Scene(
            xaxis=XAxis(axis),
            yaxis=YAxis(axis),
            zaxis=ZAxis(axis),
            ),
        margin=Margin(
            t=100
        ),
        hovermode='closest',
        annotations=Annotations([
            Annotation(
            showarrow=True,
                text="Data source: <a href='http://syrnet.net'>[1]</a>",
                xref='paper',
                yref='paper',
                x=0,
                y=0.1,
                xanchor='left',
                yanchor='bottom',
                font=Font(
                size=14
                )
                )
            ]),    )

    data=Data([trace1, trace2])
    fig=Figure(data=data, layout=layout)
    offline.plot(fig, filename=filename)

create_network_graph(pages, 'graphs/all_pages')
for category in SYRACUSE_SITE_CATEGORIES:
    create_network_graph(pages, 'graphs/' + category, category)

