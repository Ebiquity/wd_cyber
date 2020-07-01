"""
Query wikidata to get names, aliases and description of instances of a
concept (e.g., airport, currency, car model, programming language) in English, Russian and Chinese.
"""

#!pip install SPARQLWrapper

import argparse as ap
import sys
import json
from collections import defaultdict
from SPARQLWrapper import SPARQLWrapper, JSON


def get_args():
    p = ap.ArgumentParser()
    p.add_argument('id', help='Wikidata ID for a concept, e.g., Q1248784')
    p.add_argument('-l', '--limit', nargs='?', type=int, default=default_limit, help='number of instances to find')    
    p.add_argument('-o', '--out', nargs='?', type=ap.FileType('w', encoding='UTF-8'), default=sys.stdout, help='file for output (defaults to stdout)')
    #p.add_argument('-o', '--out', nargs='?', default="stdout", help='file for output (defaults to stdout)')
    args = p.parse_args()
    return args

default_endpoint = "https://query.wikidata.org/sparql"
default_limit = 100

PRETTY_PRINT = True

# Example concepts to try...
concepts = {'automobile_model':'Q3231690',
            'airport':'Q1248784',
            'currency' :'Q8142',
            'programming language':'Q9143',
            'usstate':'Q35657'}

# entities with their english names and aliases
default_query = """
SELECT DISTINCT ?ent ?name_en ?name_ru ?name_zh
   (group_concat(distinct ?alias_en; separator='|') as ?aliases_en)
   (group_concat(distinct ?alias_ru; separator='|') as ?aliases_ru)
   (group_concat(distinct ?alias_zh; separator='|') as ?aliases_zh)
 WHERE {{
  ?ent wdt:P31/wdt:P279* wd:{}.
  OPTIONAL {{?ent rdfs:label ?name_en. FILTER(lang(?name_en) = "en") }}
  OPTIONAL {{?ent rdfs:label ?name_ru. FILTER(lang(?name_ru) = "ru") }}
  OPTIONAL {{?ent rdfs:label ?name_zh. FILTER(lang(?name_zh) = "zh") }}
  OPTIONAL {{?ent skos:altLabel ?alias_en. FILTER(lang(?alias_en) = "en") }}
  OPTIONAL {{?ent skos:altLabel ?alias_ru. FILTER(lang(?alias_ru) = "ru") }}
  OPTIONAL {{?ent skos:altLabel ?alias_zh. FILTER(lang(?alias_zh) = "zh") }}
  }}
  GROUP BY ?ent ?name_en ?name_ru ?name_zh
  LIMIT {} """

# get English name and description of a wikidata item
query_name_desc = """
SELECT DISTINCT ?name ?description where {{
  wd:{} rdfs:label ?name; schema:description ?description .
  FILTER (lang(?name)="en")
  FILTER (lang(?description)="en") }} """

def utf8ify(s): return s.encode("utf-8").decode("utf-8")

def ask_wikidata(endpoint=default_endpoint, query=default_query):
    """Send query to endpoint, get results as json """
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def concept_instances(concept_id, query=default_query, limit=default_limit):
    """ given a wikidata type id, return a dict of its instances,
        including names and aliases in english, russian and chinese """
    global query_name_desc

    # get concept name and description
    response = ask_wikidata(query=query_name_desc.format(concept_id, limit))
    concept_name = response["results"]["bindings"][0]['name']['value']
    concept_description = response["results"]["bindings"][0]['description']['value']    

    # get instance data
    response = ask_wikidata(query=query.format(concept_id, limit))
    instance_list = []    

    concept_data = {'type_id':concept_id,
                    'type':concept_name,
                    'type_description':concept_description,
                    'instances': instance_list}

    # populate instances
    for result in response["results"]["bindings"]:
        instance = defaultdict(dict)
        instance_list.append(instance)
        url = result['ent']['value']
        instance['url'] = url
        eid = url.split('/')[-1]
        instance['id'] = eid
        if 'name_en' in result:
          instance['en']['name'] = result['name_en']['value']
        if 'aliases_en' in result and result['aliases_en']['value']:
          instance['en']['alias'] = result['aliases_en']['value'].split('|')
        if 'name_ru' in result:
          instance['ru']['name'] = utf8ify(result['name_ru']['value'])
        if 'aliases_ru' in result and result['aliases_ru']['value']:
          instance['ru']['alias'] = [utf8ify(s) for s in result['aliases_ru']['value'].split('|')]
        if 'name_zh' in result:
          instance['zh']['name'] = result['name_zh']['value']
        if 'aliases_zh' in result and result['aliases_zh']['value']:
          instance['zh']['alias'] = [utf8ify(s) for s in result['aliases_zh']['value'].split('|')]
    return concept_data
    
def main(args):
    #print args
    instances = concept_instances(args.id, limit=args.limit)
    is = json.dumps(instances, ensure_ascii=False, indent=2, separators=(',', ':'))
    with args.out as out:
        if PRETTY_PRINT:
            out.write(is)
        else:
            out.write(json.dumps(instances, ensure_ascii=False).encode('utf8'))

        
if __name__ == '__main__':
    args = get_args()
    main(args)
    
