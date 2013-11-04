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
