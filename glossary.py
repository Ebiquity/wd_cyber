#!/usr/bin/env python
# coding: utf-8

"""
Retrieve possibly useful data on cybersecurity concepts from Wikidata

wd_cyber_concepts is bound to a dict where keys are QIDs of some cybersecurity concepts (e.g., malware, cyberattack).  For each we find all subclasses and instances, both immediate and inherited, and for each one return a a json object with potentially useful items. Here's an example of one for malware:

 {"item": "http://www.wikidata.org/entity/Q23670513",
  "itemLabel": "Petya",
  "itemDescription": "malware",
  "link": "https://en.wikipedia.org/wiki/Petya_(malware)",
  "text": "Petya is a family of encrypting ransomware that was first discovered in 2016. The malware targets Microsoft Windows-based systems, infecting the master boot record to execute a payload that encrypts a hard drive's file system table and prevents Windows from booting. It subsequently demands that the user make a payment in Bitcoin in order to regain access to the system.\nVariants of Petya were first seen in March 2016, which propagated via infected e-mail attachments. In June 2017, a new variant of Petya was used for a global cyberattack, primarily targeting Ukraine. The new variant propagates via the EternalBlue exploit, which is generally believed to have been developed by the  U.S. National Security Agency (NSA), and was used earlier in the year by the WannaCry ransomware. Kaspersky Lab referred to this new version as NotPetya to distinguish it from the 2016 variants, due to these differences in operation. In addition, although it purports to be ransomware, this variant was modified so that it is unable to actually revert its own changes.",
  "aliases": ["Petya.2017"],
  "superClasses": [],
  "types": ["computer worm", "Trojan horse"] }

It can be called from the command line like:
   python3 glossary.py <output directory>
and it writes one line for each of the concepts in wd_

"""

from SPARQLWrapper import SPARQLWrapper, JSON
import os, os.path
import json
import requests
import pywikibot
import argparse
from urllib.parse import quote_plus

# make wikidata the default for pywikibot search
default_search_site = pywikibot.Site("wikidata", "wikidata")

# sparql endpoints
wd_endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
dbpedia = "http://dbpedia.org/sparql"
default_endpoint = wd_endpoint

# given a concept (e.g., Q14001 for 'malware'), information about all
# of its subclasses and instances, including their QIDs, labels,
# aliases, immediate super-classes and immediate types.

concept_query = """
select distinct ?item ?itemLabel ?itemDescription ?link
  (GROUP_CONCAT(DISTINCT(?alias); separator = ", ") AS ?aliases)
  (GROUP_CONCAT(DISTINCT(?superClassLabel); separator = ", ") AS ?superClasses) 
  (GROUP_CONCAT(DISTINCT(?instanceOfLabel); separator = ",") AS ?types)
WHERE {{
  ?item wdt:P31/wdt:P279*|wdt:P279+ wd:{QID}.
  OPTIONAL{{?item wdt:P31 ?instanceOf. ?instanceOf rdfs:label ?instanceOfLabel. FILTER (lang(?instanceOfLabel) = "en")}}
  OPTIONAL{{?item wdt:P279 ?superClass . ?superClass rdfs:label ?superClassLabel. FILTER (lang(?superClassLabel) = "en")}}
  OPTIONAL {{?item skos:altLabel ?alias . FILTER (lang(?alias) = "en")}}
  OPTIONAL {{?link schema:about ?item; schema:isPartOf <https://en.wikipedia.org/>}}
  SERVICE wikibase:label {{bd:serviceParam wikibase:language "en"}}
  }}
group by ?item ?itemLabel ?itemDescription ?link
order by ?item
"""

# wd concepts of interest

wd_cyber_concepts = {
  'Q14001': 'malware',
  'Q4071928': 'cyberattack',
  'Q477202': 'cryptographic hash function',
  'Q5227362': 'data theft',
  'Q631425': 'computer vulnerability',
  'Q2798820': 'security hacker',
  'Q2587068': 'sensitive information',
#  'Q3966': 'computer hardware',
#  'Q17517': 'mobile phone',
  'Q13479982': 'cryptocurrency',
  'Q47913':'intelligence agency',
  'Q28344495':'computer security consultant',
  'Q317671':'botnet',
  'Q4825885':'authentication protocol',
}

# for testing...
# wd_cyber_concepts = {'Q14001': 'malware'}

def get_data(qid, endpoint=default_endpoint):
        query = concept_query.format(QID=qid)
        sparql = SPARQLWrapper(endpoint)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        query_results = sparql.query().convert()
        results = []
        for result in query_results["results"]["bindings"]:
            obj = {}
            for property, value in result.items():
                v = value['value']
                if property in ['aliases', 'superClasses', 'types']:
                    obj[property] = [] if not v else [s.strip() for s in v.split(',')]
                else:
                    obj[property] = v
                    # add wilipedia abstract?
                    if property == 'link':
                        obj['text'] = get_wikipedia_text(v)
            results.append(obj)
        return results


wikipedia_query = """https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles="""

def get_wikipedia_text(wp_name_or_url):
    name = wp_name_or_url.split('/')[-1]
    query_url = wikipedia_query + quote_plus(name)
    response = requests.get(query_url)
    json_data = json.loads(response.text)
    result = list(json_data['query']['pages'].values())[0]
    return result.get('extract', '')
    
def print_data(qid, endpoint=default_endpoint):
    result = get_data(qid, endpoint=default_endpoint)
    print(json.dumps(result, indent=2))

def dump_data(outdir='glossary_output', concepts=wd_cyber_concepts):
    # create output directory if needed
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    # process each qid in wd_cyber_concepts    
    for qid, name in concepts.items():
        print(qid, name)
        filename = name.replace(' ', '_') + '.json'
        path = os.path.join(outdir, filename)
        with open(path, 'w') as out:
            json.dump(get_data(qid), out, indent=2)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-o', '--outputDirectory', default='glossary_output', help='directory for output')
    p.add_argument('-c', '--concept', default=None, help='specific wikidata concept qid, e.g. Q14001')
    args = p.parse_args()
    if args.concept:
        concepts = {args.concept:args.concept}
    else:
        concepts = wd_cyber_concepts        
    dump_data(outdir=args.outputDirectory, concepts=concepts)

