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

    def retrieve_node_group(self,categories):
        if categories: 
            category = categories.pop()
            group = SYRACUSE_SITE_CATEGORIES.index(category)
        else: 
            group = 22
        return group 

    def create_d3_nodes(self): 
        nodes = []
        for k,v in self.all_pages.items():
            group = retrieve_node_group(v.categories)
            node = {"id":k, "group":group}
            nodes.append(node)
        return nodes 

    def create_d3_link_relationships_from_all_pages(self, pages): 
        nodes = []
        node_urls = []
        d3_link_relationships = []

        for p in self.all_pages.values(): 
            for t in p.targets:
                if p.url not in node_urls: 
                    node_urls.append(p.url)
                    group = self.retrieve_node_group(p.categories)
                    node = {"id":p.url, "group":group}
                    nodes.append(node)
                if t.url not in node_urls: 
                    node_urls.append(t.url)
                    group = self.retrieve_node_group(t.categories)
                    node = {"id":t.url, "group":group}
                    nodes.append(node)
                link_relationship = {"source": node_urls.index(p.url), "target": node_urls.index(t.url), "value": t.count}
                d3_link_relationships.append(link_relationship)
        d3 = {
            "nodes": nodes, 
            "links":d3_link_relationships
            }
        return d3
    
    def create_d3_link_relationships_from_top_pages(self): 
        nodes = []
        node_urls = []
        d3_link_relationships = []

        for p in self.top_pages: 
            if p.targets: 
                for t in p.targets:
                    if p.url not in node_urls: 
                        node_urls.append(p.url)
                        group = self.retrieve_node_group(p.categories)
                        node = {"id":p.url, "group":group}
                        nodes.append(node)
                    if t.url not in node_urls: 
                        node_urls.append(t.url)
                        group = self.retrieve_node_group(t.categories)
                        node = {"id":t.url, "group":group}
                        nodes.append(node)
                    link_relationship = {"source": node_urls.index(p.url), "target": node_urls.index(t.url), "value": t.count}
                    d3_link_relationships.append(link_relationship)
        d3 = {
            "nodes": nodes, 
            "links":d3_link_relationships
            }
        return d3


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





