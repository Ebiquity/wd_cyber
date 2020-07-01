# wd_cyber
tools for using wikidata for cybersecurity

## wd_search.py 

*wd_search_cyber(string, required_types=[], limit=10)* searches for up to 10 cyber-relevant entities whose label or alias matches string
and has at least one type in required_types, if provided.  Candidates found are filtered by their immediate and inherited types to require that they have at least one cybersecurity-relevant type (e.g., malware) and no types from a blacklist (e.g., musical artist).

The return value is a list, roughly ordered from best to worst match.  For example, searching for 'wannacry' produces two hits:
```
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
```

You can call this from the *command line* for experimentation, e.g. usage:
 * python3 wd_search_cyber.py `<string> 
 * python3 wd_search_cyber.py Adobe

## requirements

It requires SPARQLWrapper, pywikibot and pprint
