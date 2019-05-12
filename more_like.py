import sys
import wd_search as wds
import json

usage = """
  usage: more_like.py <entity>
  Where phrase is a word or phrase describing a entity, e.g.:
    more_like.py BWI
    more_like.py camry
    more_like.py "harvard university"
"""


if len(sys.argv) != 2:
    print(usage)
    exit(0)

phrase = sys.argv[1]

hits = wds.wd_name_search(phrase)

if not hits:
    print('Nothing found')
    exit(0)


print(json.dumps(hits, ensure_ascii=False, indent=2, separators=(',', ':')))

Wikimedia disambiguation page

