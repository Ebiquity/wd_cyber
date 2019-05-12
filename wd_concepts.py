# -*- coding: utf-8 -*-

"""

Query wikidata to get names, aliases and description of instances of a
concept (e.g., airport, currency, car model, programming language) in English, Russian and Chinese.


"""

#!pip install SPARQLWrapper

from SPARQLWrapper import SPARQLWrapper, JSON
import json
from collections import defaultdict

default_endpoint = "https://query.wikidata.org/sparql"

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
  GROUP BY ?ent ?name_en ?name_ru ?name_zh """

# get English name and description of a wikidata item
query_name_desc = """
SELECT DISTINCT ?name ?description where {{
  wd:{} rdfs:label ?name; schema:description ?description .
  FILTER (lang(?name)="en")
  FILTER (lang(?description)="en") }} """


# some example concepts to try...
concepts = {'automobile_model':'Q3231690',
            'airport':'Q1248784',
            'currency' :'Q8142',
            'programming language':'Q9143',
            'usstate':'Q35657'}

def utf8ify(s): return s.encode("utf-8").decode("utf-8")

def ask_wikidata(endpoint=default_endpoint, query=default_query):
    """Send query to endpoint, get results as json """
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def process(type_id, query=default_query):
    """ given a wikidata type id, return a dict of its instances,
        including names and aliases in english, russian and chinese """
    global query_name_desc
    
    # get concept name and description
    response = ask_wikidata(query=query_name_desc.format(type_id))
    type_name = response["results"]["bindings"][0]['name']['value']
    type_description = response["results"]["bindings"][0]['description']['value']    

    response = ask_wikidata(query=query.format(type_id))
    entities = {'type_id':type_id, 'type':type_name, 'type_description':type_description}
    for result in response["results"]["bindings"]:
        url = result['ent']['value']
        eid = url.split('/')[-1]
        if eid not in entities:
            entities[eid] = defaultdict(dict)
        if 'name_en' in result:
          entities[eid]['en']['name'] = result['name_en']['value']
        if 'aliases_en' in result and result['aliases_en']['value']:
          entities[eid]['en']['alias'] = result['aliases_en']['value'].split('|')
        if 'name_ru' in result:
          entities[eid]['ru']['name'] = result['name_ru']['value'].encode("utf-8").decode("utf-8")
        if 'aliases_ru' in result and result['aliases_ru']['value']:
          entities[eid]['ru']['alias'] = [s.encode("utf-8").decode("utf-8") for s in result['aliases_ru']['value'].split('|')]
        if 'name_zh' in result:
          entities[eid]['zh']['name'] = result['name_zh']['value']
        if 'aliases_zh' in result and result['aliases_zh']['value']:
          entities[eid]['zh']['alias'] = [s.encode("utf-8").decode("utf-8") for s in result['aliases_zh']['value'].split('|')]
    return entities


with open('wdc.json', mode="w", encoding="utf8") as out:
    out.write(json.dumps(process(concepts['usstate']), ensure_ascii=False, indent=2, separators=(',', ':')))


