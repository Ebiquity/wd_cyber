"""
wd_search(string, required_types=[], limit=10) Search Wikidata for up to 10
relevant items whose label, alias or text matches string and has at least one type in required_types, if provided.  candidates found are filtered by their immediate and inherited types to require that they have at least one cybersecurity-relevant type (e.g., malware) and no typoes from a blacklist (e.g., musical artist).

The return value is a list, roughly ordered from best to worst match.  For example, searching for 'wannacry' produces two hits:

 [{ 'concepturi':'http://www.wikidata.org/entity/Q29957041',
    'description':'ransomware cyberattack',
    'id':'Q29957041',
    'label':'WannaCry ransomware attack',
    'match':{ 'language':'en', 'text':'WannaCry ransomware attack', 'type':'label'},
    'types':[('Q4071928','cyberattack')]},
  { 'concepturi':'http://www.wikidata.org/entity/Q29908721',
    'description':'Ransomware',
    'id':'Q29908721',
    'label':'WannaCry',
    'match':{'language':'en', 'text':'WannaCry', 'type':'label'},
    'types':[('Q14001','malware'), ('Q7397','software')]}]

Call this from the command line for experimentation, e.g.:
   python3 wd_search.py <string> [<required types>]
   python3 wd_search.py Adobe
   python3 wd_search.py python Q7397
   python3 wd_search.py mitre  "Q783794,Q2659904"

"""

import argparse as ap
import sys
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import requests

def get_args():
    p = ap.ArgumentParser()
    p.add_argument('string', help='string to search for in label, alias or text')
    p.add_argument('--limit', nargs='?', type=int, default=10, help='number of hits to find')    
    p.add_argument('-t', '--types', nargs='?', default='Q35120', help='must be one of these types (comma seperate IDs: "Q5,Q68")')
    p.add_argument('-o', '--out', nargs='?', type=ap.FileType('w'), default=sys.stdout, help='file for output (defaults to stdout)')
    args = p.parse_args()
    args.types = [t for t in args.types.split(',')]
    return args


# sparql endpoints
default_endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"


# user agent for http request (required by wikidata query service)
USER_AGENT = "SearchBot/1.0 (Tim Finin)"


# SPARQL query to get a wikidata item's type IDs and labels
q_types_labels_query = """
select ?type ?typeLabel where {{
   wd:{QID} wdt:P31/wdt:P279* ?type .
   SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}}} 
"""

# searching wikidata returns entities some of whch are of interest and
# others not.  We filter these by requiring an entities to have a type
# on the whitelist and no types on the backlist


def wd_entity_id(url):
    """ returns entity id if url is an entity, else the url"""
    return url.split('http://www.wikidata.org/entity/')[1] if url.startswith('http://www.wikidata.org/entity/') else url

def wd_search(string, required_types=[], good_types=[], bad_types=[], isa_type=False, limit=10):
    """ search for up to limit items whose text matches string and has at least one type in
        required_types, if not [] """
    candidates = wd_string_search(string, limit=limit)
    # print("CANDIDATES:", len(candidates))
    hits = []
    seen = set()
    # get each item's types
    for item in candidates:
        id = item['title']
        # print('Checking:', id)
        if id not in seen:
            seen.add(id)
            types = get_types(id , required_types, good_types, bad_types, isa_type)
            if types:
                # print('NEW HIT:', id)
                item['types'] = list(types)
                # remmove unwanted properties
                item.pop('ns', None)
                hits.append(item)
    return hits

def wd_string_search(string, limit=20):
    # search wikidata for items containing string
    api_url = "https://www.wikidata.org/w/api.php"
    params = {'action':'query', 'list':'search', 'srsearch':string, 'srlimit':limit, 'format':'json'}
    result = requests.Session().get(url=api_url, params=params).json()
    #print(json.dumps(result, indent=2))
    #return [item['title'] for item in result['query']['search']]
    return [item for item in result['query']['search']]

def get_types(id, required_types, good_types, bad_types, isa_type, endpoint=default_endpoint):
    """
    Given a wikidata id (e.g., Q7803487), returns a set of its types.
    """
    def process_type_collection(types):
        """ convert a dict or list to a set if neccessary, sample element to see if it's a Qd """
        if isinstance(types, dict):
            types = set(types.keys())
        elif isinstance(types, list):
            types = set(types)
        elif not isinstance(types, set):
            print('***** Arg to get_types must be a dict, list or set', types)
            types = set([])
        if types:
            sample = next(iter(s))
            if not sample[0] == 'Q':
                print('***** Arg to get_types must specify wikidata entity ids', types)
                types = set()
        return types
            
    # retrieve types for wd id
    query = q_types_labels_query.format(QID=id)
    results = query_wd(query, endpoint=endpoint)
    # select the good types, bail if we find a bad type
    types = set([])
    found_required_type = False if required_types else True
    for result in results["results"]["bindings"]:
        id_label = (wd_entity_id(result['type']['value']), result['typeLabel']['value'])
        id = id_label[0]
        if id in required_types:
            found_required_type = True
            types.add(id_label)
        if id in good_types:
            types.add(id_label)
        elif id in bad_types:
            return None
    # bail if we did not find a required type
    if required_types and not found_required_type:
        return None
    return types

def query_wd(query, endpoint=default_endpoint):
    sparql = SPARQLWrapper(endpoint, agent=USER_AGENT)
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    return sparql.query().convert()

def isa_type(qid):
    """ returns True iff qid is a type, i.e., has an instance, a subtype or a supertype """
    query = "ASK {{?x wdt:P31|wdt:P279|^wdt:P279 wd:{} }}".format(qid)
    result = query_wd(query, endpoint=default_endpoint)
    return result['boolean']


def main(args):
    result = wd_search(args.string, limit=args.limit, required_types=args.types)
    with args.out as out:
        out.write(json.dumps(result, indent=2, separators=(',', ':')))

if __name__ == '__main__':
    args = get_args()
    main(args)


