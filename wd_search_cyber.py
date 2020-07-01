import wd_search as wds
import json


# cybersecurity-relevant wikidata types: one of these must be a type
# of a good search result

wd_cyber_whitelist = {
  'Q5': 'human',
  'Q43229': 'organization',
  'Q82794': 'geographic region',
  'Q1048835': 'political territorial entity',
  'Q7397': 'software',
  'Q205663': 'process',
  'Q68': 'computer',
  'Q1301371': 'network',
  'Q14001': 'malware',
  'Q783794': 'company',
  'Q161157': 'password',
  'Q1541645': 'process identifier',
  'Q4418000': 'network address',
  'Q5830907': 'computer memory',
  'Q82753': 'computer file',
  'Q2904148': 'information leak',
  'Q4071928': 'cyberattack',
  'Q477202': 'cryptographic hash function',
  'Q141090': 'encryption',
  'Q5227362': 'data theft',
  'Q631425': 'computer vulnerability',
  'Q627226': 'Common Vulnerabilities and Exposures',
  'Q2801262': 'hacker group',
  'Q2798820': 'security hacker',
  'Q8142': 'currency',
  'Q2587068': 'sensitive information',
  'Q3966': 'computer hardware',
  'Q17517': 'mobile phone',
  'Q986008': 'payment system',
  'Q13479982': 'cryptocurrency',
  'Q20826013': 'software version',
  'Q20631656': 'software release',
  'Q44601380': 'property that may violate privacy',
  'Q1058914': 'software company',
  'Q278610': 'Dropper',
  'Q1332289':'black hat',
  'Q2798820':'security hacker',
  'Q22685':'hacktivism',
  'Q47913':'intelligence agency',
  'Q28344495':'computer security consultant',
  'Q26102':'whistleblower',
  'Q317671':'botnet',
  'Q9135':'operating system',
  'Q4825885':'authentication protocol',
  'Q2659904':'government organization',
  'Q1668024':'service on internet',
  'Q202833':'social media',
  'Q870898':'computer security software'
}

# wikidata types that should not be in a search result
wd_cyber_blacklist = {
  'Q4438121':'sports organization',
  'Q11410':'game',
  'Q14897293':'fictional entity',
  'Q32178211':'music organisation',
  'Q16010345':'performer',
  'Q483501':'artist',
  'Q56678558':'unknown composer author',
  'Q28555911':'ordinary matter',
  'Q49848':'document'
}


def wd_search_cyber(string, required_types=[], good_types=wd_cyber_whitelist, bad_types=wd_cyber_blacklist, isa_type=False, limit=10):
    return wds.wd_search(string, required_types=required_types, good_types=good_types, bad_types=bad_types, isa_type=isa_type, limit=limit)

### Test examples
# wd_search_cyber('acrobat')
# wd_search_cyber('ukraine')
# wd_search_cyber('anonymous')
# wd_search_cyber('ibm')
# wd_search_cyber('black hat')
# wd_search_cyber('Shadow Brokers')
# wd_search_cyber('julian assange')
# wd_search_cyber('ddos')
# wd_search_cyber('linux')


def main(args):
    result = wd_search_cyber(args.string, limit=args.limit, required_types=args.types)
    with args.out as out:
        out.write(json.dumps(result, indent=2, separators=(',', ':')))

if __name__ == '__main__':
    args = wds.get_args()
    main(args)


