from utils.marcutils import generate_marcfiles, get_solr_doc, collate
import pysolr

from settings import SOLR

if __name__ == "__main__":
  print("Attempting Solr connection on '{0}'".format(SOLR))
  solr = pysolr.Solr(SOLR, timeout = 100)    # long timeout as the final optimize step can be long
  cname = ""
  count = 0
  cc = 1
  docs = []
  for fname, marcdoc in generate_marcfiles():
    for marcfile in marcdoc:
      if cname != fname:
        cname = fname
        cc = 1
        if count:
          print("Uploading {0} to Solr...    ({1} completed)".format(fname, str(count)))
        else:
          print("Uploading {0} to Solr...".format(fname))
      doc = get_solr_doc(collate(marcfile))
      docs.append(doc)
      count += 1
      if not(cc % 100):
        print("{0} - processed".format(str(cc)))
        solr.add(docs)
        docs = []
      cc += 1
  solr.add(docs)
  print("Job complete. {0} records uploaded to Solr".format(str(count)))
  print("Commiting records to solr and optimising")
  solr.commit()
  solr.optimize()

