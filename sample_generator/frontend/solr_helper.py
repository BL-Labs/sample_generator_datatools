import pysolr
import time, hashlib

from sample_generator.settings import SOLR_CONNECTION

solr = pysolr.Solr(SOLR_CONNECTION, timeout=10)

FACET_DICT = {'facet':'true',
              'facet.field':'year',
              'facet.mincount':'1',
              'facet.limit':'-1'}

JUST_FACET_DICT = FACET_DICT.copy()
JUST_FACET_DICT.update({'rows':1, 'fl':'score'})

FAILED_SAMPLE = 9999999999999999

def apply_year_range(filter, yearstart, yearend = None):
  if yearend:
    return u"({0}) AND year:[{1} TO {2}]".format(filter, yearstart, yearend)
  return u"({0}) AND year:{1}".format(filter, yearstart)

def apply_digital(filter):
  return u"{0} AND digital:true".format(filter)

def parse_facet(s_results, facet="year"):
  facets = s_results.facets['facet_fields']
  fdict = {}
  if facet in facets:
    for f, val in zip(facets[facet][0::2], facets[facet][1::2]):
      fdict[f] = val
  return fdict

def apply_add_q(f1, aq):
  return u"{0} AND ({1})".format(f1, aq)

def get_distribution(filter_query, yearstart=None, yearend=None, additional_query = None):
  aug_filter = apply_year_range(filter_query, yearstart, yearend)
  if additional_query:
    aug_filter = apply_add_q(aug_filter, additional_query)

  results = solr.search(aug_filter, **JUST_FACET_DICT)
  all_vals = parse_facet(results, "year")
  all_hits = results.hits

  dig_filter = apply_digital(aug_filter)
  dig_results = solr.search(dig_filter, **JUST_FACET_DICT)
  dig_vals = parse_facet(dig_results, "year")
  dig_hits = dig_results.hits

  dataset = [[u'year', u'all', u'digital only']]
  
  ys, ye = 0,0
  try:
    if yearstart:
      ys = int(yearstart)
    if yearend:
      ye = int(yearend)
  except ValueError:
    pass

  year_beginning = 1800
  year_range = 101
  if ys:
    year_range = 1
    year_beginning = ys

  if ys and ye:
    year_range = ye - ys + 1

  for year_o in range(year_range):
    year = unicode(year_beginning + year_o)
    row = [year,0,0]
    if year in all_vals: row[1] = all_vals[year]
    if year in dig_vals: row[2] = dig_vals[year]
    dataset.append(row)
  return dataset, all_hits, dig_hits

def get_max_sample_scale(q, yearstart=None, yearend=None):
  dataset, all_hits, dig_hits = get_distribution(q, yearstart, yearend)
  maxscale = 0
  for year, all, dig in dataset[1:]:
    if dig:
      scale = all/float(dig)
      if scale > maxscale:
        maxscale = scale
  
  flatten = []
  samplesize = 0
  for year, all, dig in dataset[1:]:
    if dig:
      flatten.append((year, int(all / maxscale)))
    else:
      flatten.append((year, 0))
    samplesize += flatten[-1][1]
  return samplesize, flatten, dataset, all_hits, dig_hits

def generate_chart_javascript(chartname, data, width=u"600", height=u"400", title=None):
  text_chunk = []
  text_chunk.append(u"   var data = google.visualization.arrayToDataTable([")
  text_chunk.append(u"      ['{0}'],".format(u"', '".join(data[0])))
  for row in data[1:]:
    text_chunk.append(u"      ['{0}', {1}],".format(row[0], u", ".join(map(str, row[1:]))))
  text_chunk.append(u"   ]);")
  if title:
    text_chunk.append("        var options = {{\n          title: '{0}',\n          width: {1},\n          height: {2}\n,        }};\n".format(title, width, height))
  else:
    text_chunk.append("        var options = {{\n          title: '{0}',\n          width: {1},\n          height: {2}\n,        }};\n".format(chartname, width, height))
  text_chunk.append("        var chart = new google.visualization.LineChart(document.getElementById('{0}'));".format(chartname))
  text_chunk.append("        chart.draw(data, options);")
  return u"\n".join(text_chunk)

def _generate_html(q, filename, yearstart=None, yearend=None):
  dataset, all_hits, dig_hits = get_distribution(q, yearstart, yearend)
  header = u"""
<html>
  <head>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {"""
  footer = u"""
}}
    </script>
  </head>
  <body>
    <div id="{0}" style="width: 900px; height: 500px;"></div>
  </body>
</html>"""
  middle = generate_chart_javascript("distribution", dataset, width="900", height="500", title=q)
  with open(filename, "w") as fn:
    fn.write(header.encode("utf-8"))
    fn.write(middle.encode("utf-8"))
    fn.write(footer.format("distribution").encode("utf-8"))

def group_years(dataset, start=u"1800", size=5):
  grouped = [dataset[0]]
  current = []
  cyear = int(start) + size
  for row in dataset[1:]:
    if not current:
      current = row[1:]
    else:
      for idx, value in enumerate(row[1:]):
        current[idx] += value
    if int(row[0]) == cyear:
      grouped.append([u"{0}".format(str(cyear-size))] + current)
      current = []
      cyear += size
  return grouped

def get_sample_set(filter_query, yearstart, yearend, sample_size, sample_type, digital_only, randomseed = None, add_q = None, interval = 5):
  # First, how big a set?
  if not randomseed:
    randomseed = hashlib.md5(str(time.time())).hexdigest()

  aug_filter = apply_year_range(filter_query, yearstart, yearend)
  if add_q:
    aug_filter = apply_add_q(aug_filter, add_q)

  dataset, all_hits, dig_hits = get_distribution(aug_filter, yearstart=yearstart, yearend=yearend)
  if digital_only:
    aug_filter = apply_digital(aug_filter)

  if sample_type == "random":
    # easy, just take random sample or rather, let Solr do the hard work:
    # draw from the whole thing:
    rows = 0
    try:
      ssize = float(sample_size)/ 100.0
      rows = int(ssize * int(all_hits))
      if digital_only:
        rows = int(ssize * int(dig_hits))
    except ValueError:
      print("Cock up")
    results = solr.search(aug_filter, **{ 'rows':rows,
                                          'sort':"random_{0} desc".format(randomseed),
                                        })
    counts = {}
    for doc in results.docs:
      year = doc.get("year", ["0000"])[0]
      if year not in counts:
        counts[year] = 0
      counts[year] += 1

    dataset[0] = [u'year', u'all', u'digital only', u'sample']
    for idx in range(len(dataset)-1):
      year_c = dataset[idx+1][0]
      if year_c in counts:
        dataset[idx+1].append(counts[year_c])
      else:
        dataset[idx+1].append(0)
    return results.docs, rows, randomseed, dataset, all_hits, dig_hits
  elif sample_type=="randomprop":
    grouped = group_years(dataset, yearstart, interval)
    maxratio = 0
    docs = []
    total_sample_size = 0
    for row in grouped[1:]:
      if row[2]:
        ratio = row[1]/float(row[2])
      elif row[1]:
        ratio = FAILED_SAMPLE     #  Real-world things, but zero digitised.
      if ratio > maxratio:
        maxratio = ratio
    if maxratio and maxratio != FAILED_SAMPLE:
      ssize = float(sample_size)/ 100.0
      sample_size_dict = {}
      grouped[0].append(u"sample")
      for idx, row in enumerate(grouped[1:]):
        slice_size = int(row[1]/maxratio)
        total_sample_size += slice_size
        sample_size_dict[row[0]] = slice_size
        grouped[idx+1].append(slice_size)
      for idx in range((int(yearend) - int(yearstart)) / interval):
        ys = str(int(yearstart) + idx * interval)
        ye = str(int(ys) + interval - 1)
        current_filter = apply_year_range(filter_query, ys, ye)
        if add_q:
          current_filter = apply_add_q(current_filter, add_q)
        if digital_only:
          current_filter = apply_digital(current_filter)
        rows = sample_size_dict[ys]
        
        results = solr.search(current_filter, **{ 'rows':rows,
                                                  'sort':"random_{0} desc".format(randomseed),
                                                 })
        docs.extend(results.docs)

      return docs, total_sample_size, randomseed, grouped, all_hits, dig_hits
  return [],0,"",[],0,0
