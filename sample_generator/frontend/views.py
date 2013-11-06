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
           'query': "",
           'yearstart': "1800",
           'yearend': "1900"}
    
    template = loader.get_template("frontend/index.html")
    context = RequestContext(request, c)
    return HttpResponse(template.render(context))

  elif request.method == "POST":
    filter_query = request.POST.get("query", "*:*")
    digital_only = request.POST.get("digital", False)
    yearstart = request.POST.get("yearstart", "1800")
    yearend = request.POST.get("yearend", "1900")
    dataset, all_hits, dig_hits = get_distribution(filter_query, yearstart=yearstart, yearend=yearend)
    template = loader.get_template("frontend/index.html")
    c = {'all_hits': all_hits,
         'dig_hits': dig_hits,
         'chart': generate_chart_javascript(u"distribution", dataset, title=filter_query),
         'query': filter_query,
         'yearstart': yearstart,
         'yearend': yearend}
    context = RequestContext(request, c)
    return HttpResponse(template.render(context))
    
