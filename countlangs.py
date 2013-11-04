import json

from utils.marcutils import generate_marcfiles, get_language, get_subfield

langs = set()
langcount = {}

def addlang(lang):
  langs.add(lang)
  if not lang in langcount:
    langcount[lang] = 0
  langcount[lang] += 1


def count_and_store():
  for docfile, doc in generate_marcfiles():
    print("Processing {0}".format(docfile))
    for item in doc:
      addlang(get_language(doc))

  with open("langcounts.json", "w") as langcountfile:
    json.dump(langcount, langcountfile)
  with open("langs.json", "w") as langfile:
    json.dump(list(langs), langfile)

def field_coverage():
  count = 0
  from collections import defaultdict
  coverage = defaultdict(lambda: 0)
  for docfile, doc in generate_marcfiles():
    print("Processing {0}".format(docfile))
    for item in doc:
      field_set = set()
      for field in item.as_dict()["fields"]:
        for fkey in field.keys():
          field_set.add(fkey)
      
      for fflag in list(field_set):
        coverage[fflag] += 1
      count += 1
    print("--  {0}  --".format(docfile))
    for k in sorted(coverage.keys()):
      print(". {0}   {1:07d}".format(k, coverage[k]))
    print("\n\n")
  return coverage, count

def sfx_rosetta(reverse_order = False):
  with open("sfx_mapping.tsv", "w") as sfxfile:
    sfxfile.write("System Number\t$b\t$j\n")
    for docfile, doc in generate_marcfiles(reverse_order):
      print("Processing {0}".format(docfile))
      for item in doc:
        sysnumber = item.get_fields()[0].data
        domid = ""
        b = ""
        eightfivetwo = filter(lambda x: x.tag == "852", item.get_fields())
        for loc in eightfivetwo:
          c = loc.get_subfields("c")
          if c and "SFX" in c:
            domid = loc.get_subfields("j")[0]
            b = loc.get_subfields("b")[0]
        if domid:
          print("HIT! '{0}' might link to '{1}'. PDF at http://access.dl.bl.uk/{1}".format(sysnumber, domid))
          sfxfile.write("{0}\t{1}\t{2}\n".format(sysnumber, b, domid))
        
