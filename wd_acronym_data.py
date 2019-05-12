## todo: eliminate properties,

query = """
select ?x ?xLabel ?xAltLabel ?xDescription ?link where {{
  ?x rdfs:label|skos:altLabel "{}"@en .
  OPTIONAL {{?link schema:about ?x; 
                 schema:inLanguage "en"; 
                 schema:isPartOf <https://en.wikipedia.org/>}}
  #FILTER (?xDescription != "Wikimedia disambiguation page")
  FILTER NOT EXISTS {{?x schema:description "Wikimedia disambiguation page"@en}}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" .}}
  }} """

