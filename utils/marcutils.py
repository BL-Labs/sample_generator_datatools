#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymarc, os, re

from collections import defaultdict

from settings import DATAROOT

def generate_marcfiles(reverse_order = False):
  docfiles = sorted([x for x in os.listdir(DATAROOT) if x.startswith("19C_0")])
  if reverse_order:
    docfiles.reverse()
  for docfile in docfiles:
    docfilepath = os.path.join(DATAROOT, docfile)
    yield (docfilepath, pymarc.parse_xml_to_array(docfilepath))

def get_language(marcdoc):
  oh_eights = filter(lambda x: x.has_key("008"), marcdoc.as_dict()["fields"])
  if len(oh_eights) == 1:
    return oh_eight[0]['008'][35:38]
  elif len(oh_eights) > 1:
    raise Exception("More than one 008 field found. Bigger problem likely")
  else:
    return ""

def get_subfield(field, marccode, subfield):
  subfields = filter(lambda x: x.has_key(subfield), field[marccode].get('subfields', [{}]))
  for subf in subfields:
    yield subf[subfield]

def collate(record):
  collated = defaultdict(list)
  for field in record.get_fields():
    collated[field.tag].append(field)
  return collated

def _normalise_name(args):
  name, date, relator = args
  # If no relator, assume author?
  # Spaces to "_"
  # eg "SMITH, John", "1948-", "" ---> "author/SMITH,_John__1948-"
  if not relator:
    relator = u"author"
  else:
    relator = relator[0].lower()
  if not name:
    name = u""
  else:
    name = name[0]

  if not date:
    date = u""
  else:
    date = date[0] 

  return (name, date, relator)

def flatten_name(args):
  name, date, relator = _normalise_name(args)
  fname = u"{0}/{1}".format(relator, name)
  if date:
    fname = u"{0}/{1} {2}".format(relator, name, date)
  return fname

def flatten_name_for_facet(args):
  name, date, relator = _normalise_name(args)
  fname = u"{0}/{1}".format(relator, name)
  if date:
    fname = u"{0}/{1}__{2}".format(relator, name, date)
  return re.sub(u" ", u"_", fname)

def get_sysnum(collated_record):
  if len(collated_record["001"]) == 1:
    return collated_record["001"][0].value()
  else:
    return ""

def get_lang(collated_record):
  if len(collated_record["008"]) == 1:
    return collated_record["008"][0].value()[35:38]
  else:
    return ""

def _gather_names(namefield):
  name = namefield.get_subfields("a")
  date = namefield.get_subfields("d")
  relator = namefield.get_subfields("e")
  return (name, date, relator)

def get_raw_names(collated_record):
  # personal 100 - $a name $d date $e relator
  # Corp 110 - $a name $b subgroup
  # alt name 700 - $a name $t title of previous/related work (ADD later maybe?)
  names = {'100':[], '110':[]}
  for nametype in names:
    for namefield in collated_record.get(nametype, []):
      names[nametype].append(_gather_names(namefield))
  return names

def get_names(collated_record, facet = False):
  names = get_raw_names(collated_record)
  if facet:
    return {'personal': map(flatten_name_for_facet, names['100']),
            'corporate': map(flatten_name_for_facet, names['110'])}
  else:
    return {'personal': map(flatten_name, names['100']),
            'corporate': map(flatten_name, names['110'])}

def get_titles(collated_record):
  # A title can hide in 245 $a + $b, 240 and 130 on occasion.
  # ~99.9% of records had a main title in 245
  # and 240 + 130 coverage was below 15% so skipping for now
  # Output is still as a list, in case this changes
  if collated_record.get('245', u""):
    maintitles = [x.value() for x in collated_record['245'] + collated_record['240'] + collated_record['130']]
    return maintitles
  else:
    return u""

def get_pub_detail(collated_record):
  # 260 $a Place of Publication/Distribution
  #     $b Name of Publisher/Distrib
  #     $c date of Pub
  #     $e Place of Manuf
  #     $f manufacturer
  #     $g Manuf date
  #  Near 95% coverage in the dataset
  if collated_record.get("260", u""):
    # Typically all contained in a single field.
    pubfield = collated_record['260'][0]
    pdtype = u"m"
    place = pubfield.get_subfields("e")
    date = pubfield.get_subfields("f")
    maker = pubfield.get_subfields("g")
    if pubfield.get_subfields("a"):
      pdtype = u"p"
      place = pubfield.get_subfields("a")
      date = pubfield.get_subfields("c")
      maker = pubfield.get_subfields("b")
    def present_value(items):
      if len(items[0]) == 1:
        return u"{0}/{1}".format(items[1], items[0][0])
      return u""

    return map(present_value, [(place, pdtype), (maker, pdtype), (date, pdtype)])

def get_phys_desc(collated_record):
  # $a - Extent (R)
  # $b - Other physical details (NR)
  # $c - Dimensions (R)
  # $e - Accompanying material (NR)
  # $f - Type of unit (R)
  # $g - Size of unit (R)
  # $3 - Materials specified (NR)
  # $6 - Linkage (NR)
  # $8 - Field link and sequence number (R)
  # Lump it all in there? 
  def iter_subf(fields):
    for x in fields:
      for y in x.get_subfields("a", "b", "c", "e", "f", "g", "3", "6"):
        yield y
  if collated_record.get("300"):
    return  [y for y in iter_subf(collated_record["300"])]
  return []

def get_general_note(collated_record):
  if collated_record.get("500"):
    return [x.value() for x in collated_record['500']]
  return []

def get_domids(collated_record):
  if collated_record.get("852"):
    sfx = filter(lambda x: x.get_subfields("c") == [u"SFX"], collated_record["852"])
    if sfx:
      domids = [x.get_subfields("j")[0] for x in sfx if x.get_subfields("j") and x.get_subfields("j")[0].startswith("lsid")]
      return domids
  return []

def get_shelfmarks(collated_record):
  # ignore SFX + lsid shelfmarks, as these are harvested by the get_domids part
  marks = []
  if collated_record.get("852"):
    for sm in collated_record['852']:
      if not(sm.get_subfields("c") == [u"SFX"] and sm.get_subfields("j")[0].startswith("lsid")):
        marks.append(sm.value())
  return marks

def get_solr_doc(collated_record):
  names = get_names(collated_record)
  pubplace, maker, pubdate = get_pub_detail(collated_record)
  doc = {'id': get_sysnum(collated_record),
         'title': get_titles(collated_record),
         'personal': names['personal'],
         'corporate': names['corporate'],
         'place': pubplace,
         'maker': maker,
         'date': pubdate,
         'physdesc': get_phys_desc(collated_record),
         'general': get_general_note(collated_record),
         'domids': get_domids(collated_record),
         'shelfmarks': get_shelfmarks(collated_record),
         'lang': get_lang(collated_record)}
  return doc
