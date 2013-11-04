FILE_TEMPLATE = "19C_{0:05d}.xml"

header = """<?xml version="1.0" encoding="UTF-8" ?><marc:collection xmlns:marc="http://www.loc.gov/MARC21/slim" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
"""

footer = "</marc:collection>\n"

CHUNKSIZE = 1000
chunk = 1
records = []
with open("19C.xml", "r") as xmlblob:
  count = 0
  records.append(xmlblob.next())  
  for rawline in xmlblob:
    line = rawline.decode("utf-8")
    if line.startswith("<marc:record>"):
      count += 1
    if count == CHUNKSIZE:
      # store file
      print("Storing file - {0}".format(chunk))
      with open(FILE_TEMPLATE.format(chunk), "w") as chunkfile:
        for item in records:
          chunkfile.write(item.encode("utf-8"))
        chunkfile.write(footer.encode("utf-8"))
        
      records = [header]
      chunk += 1
      count = 0
    records.append(line)

