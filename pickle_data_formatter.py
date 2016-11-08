import pickle
import os, sys
from scraper import Page as Page, SYRACUSE_SITE_CATEGORIES
import requests
import json


class PickleFileReader():
    def __init__(self):
        self.all_pages = self.retrieve_file_data('all_pages.pickle')
        self.top_pages = self.retrieve_file_data('top_pages.pickle')
        self.broken_pages = self.retrieve_file_data('all_broken_links.pickle')

    def retrieve_file_data(self, filename): 
        f = open(filename,'rb')
        pickle_data = pickle.load(f)
        f.close()
        return pickle_data 

    def create_d3_nodes(self): 
        nodes = []
        for k,v in self.all_pages.items():
            if v.categories: 
                category = v.categories.pop()
                group = SYRACUSE_SITE_CATEGORIES.index(category)
            else: 
                group = 22
            node = {"id":k, "group":group}
            nodes.append(node)
        return nodes 

    def create_d3_link_relationships_from_top_pages(self): 
        # nodes = [{"id":k, "group":group}]
        # node_urls = []
        d3_link_relationships = []

        for p in self.top_pages: 
            if p.targets: 
                for t in p.targets:
                    link_relationship = {"source": p.url, "target": t.url, "value": t.count}
                    # if p.url not in node_urls: 
                    #     node_urls.append(p.url)
                    # elif t.url not in node_urls : 
                    #     node_urls.append(t.url)

                    d3_link_relationships.append(link_relationship)
        return d3_link_relationships


    def package_d3_json(self):
        d3 = {
        "nodes": self.create_d3_nodes(), 
        "links":self.create_d3_link_relationships_from_top_pages()
        }
        return d3

def write_json_file(data): 
    with open('./static/data/d3_force_graph.json', 'w') as outfile:
        json.dump(data, outfile)
    outfile.close()





