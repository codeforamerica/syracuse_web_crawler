from scraper import *
import pickle


all_pages = pickle.load(open('./all_pages.pickle', 'rb'))
broken_links = pickle.load(open('./all_broken_links.pickle', 'rb'))
top_pages = pickle.load(open('./top_pages.pickle', 'rb'))

print('top pages: %i' % len(top_pages))
print('all pages: %i' % len(all_pages))
print('broken links: %i' % len(broken_links))


print('top 100 linked pages')
pages = list(all_pages.values())
pages.sort(key=lambda x: x.count, reverse=True)
for page in pages[0:100]:
    print('(%s)  %s: %i' % (','.join(page.categories),
        page.url, page.count))
