# Create your views here.

from django.http import HttpResponse
from django.template import RequestContext, loader

from frontend.solr_helper import *

from django.shortcuts import redirect

def index(request):
  if request.method == "GET":
    filter_query = "*:*"
    dataset, all_hits, dig_hits = get_distribution(filter_query, "1800", "1900")
    c = {'all_hits': all_hits,
           'dig_hits': dig_hits,
           'chart': generate_chart_javascript(u"distribution", dataset, title=u"Total works"),
           'query': filter_query,
           'yearstart': "1800",
           'yearend': "1900"}
    
    template = loader.get_template("frontend/index.html")
    context = RequestContext(request, c)
    return HttpResponse(template.render(context))

  elif request.method == "POST":
    filter_query = request.POST.get("query", "*:*")
    additional_query = request.POST.get("additional_query", request.GET.get("additional_query", ""))
    digital_only = request.POST.get("digital", False)
    yearstart = request.POST.get("yearstart", "1800")
    yearend = request.POST.get("yearend", "1900")
    dataset, all_hits, dig_hits = get_distribution(filter_query, yearstart=yearstart, yearend=yearend, additional_query=additional_query)
    template = loader.get_template("frontend/index.html")
    c = {'all_hits': all_hits,
         'dig_hits': dig_hits,
         'chart': generate_chart_javascript(u"distribution", dataset, title=filter_query),
         'query': filter_query,
         'additional_query': additional_query,
         'yearstart': yearstart,
         'yearend': yearend}
    context = RequestContext(request, c)
    return HttpResponse(template.render(context))

def samplegenerate(request):
  if request.method == "POST" or (request.method == "GET" and request.GET.get("query", None)):
    filter_query = request.POST.get("query", request.GET.get("query", ""))
    additional_query = request.POST.get("additional_query", request.GET.get("additional_query", ""))
    digital_only = request.POST.get("digital_only", request.GET.get("digital_only", False))
    if digital_only and (digital_only=="false" or digital_only=="False"):
      digital_only = False
    yearstart = request.POST.get("yearstart", request.GET.get("yearstart", "1800"))
    yearend = request.POST.get("yearend", request.GET.get("yearend", "1900"))
    randomseed = request.POST.get("randomseed", request.GET.get("randomseed", None))
    sample_size = request.POST.get("sample_size", request.GET.get("sample_size"))
    sample_type = request.POST.get("sample_type", request.GET.get("sample_type"))
    viewtype = request.POST.get("viewtype", request.GET.get("viewtype", None))
    # Generate sample:
    sample_set, doc_number, randomseed, dataset, all_hits, dig_hits  = get_sample_set(filter_query, yearstart, yearend, sample_size, sample_type, digital_only, randomseed, additional_query)
    if viewtype and viewtype == "tsv":
      header = [u"id", u"title", u"personal", u"corporate", u"place", u"maker", u"date", u"general", u"physdesc", u"lang", u"domids", u"shelfmarks"]
      tsv_output = []
      tsv_output.append(header)
      for doc in sample_set:
        row = []
        for key in header:
          item = doc.get(key, u"")
          if item and isinstance(item, list):
            row.append(u" | ".join(item))
          else:
            row.append(item)
        tsv_output.append(row)
      output_file = u""
      for row in tsv_output:
        output_file += u"\t".join(row)
        output_file += u"\n"
      return HttpResponse(output_file.encode("utf-8"), mimetype="text/tab-separated-values; charset=utf-8")
    else:
      template = loader.get_template("frontend/sample.html")
      c = {
           'query': filter_query,
           'additional_query': additional_query,
           'yearstart': yearstart,
           'yearend': yearend,
           'digital_only': digital_only,
           'sample_size': sample_size,
           'sample_type': sample_type,
           'doc_number': doc_number,
           'randomseed': randomseed,
          }
      geturl = "/sample/?{0}".format(u"&".join([u"{0}={1}".format(k,v) for k,v in c.iteritems()]))
      geturl_tsv = "/sample/?{0}&viewtype=tsv".format(u"&".join([u"{0}={1}".format(k,v) for k,v in c.iteritems()]))
      c["geturl"] = geturl
      c["geturl_tsv"] = geturl_tsv
      c["chart"] = generate_chart_javascript(u"distribution", dataset, title=filter_query, width="800")
      c['sample_set'] = sample_set
      context = RequestContext(request, c)
      return HttpResponse(template.render(context))
  else:
    return redirect("index")
  return HttpResponse("Soon")
