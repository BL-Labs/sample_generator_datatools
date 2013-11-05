#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest, pymarc, os

from utils.marcutils import *

TF1 = "tests/single.xml"
TF2 = "tests/multiple.xml"

class TestMARCParsing(unittest.TestCase):
  def setUp(self):
    self.tf1 = pymarc.parse_xml_to_array(TF1)
    self.collated_tf1 = collate(self.tf1[0])
    self.tf2 = pymarc.parse_xml_to_array(TF2)
    self.collated_tf2 = collate(self.tf2[0])

  def test_validate_testdata(self):
    self.assertEqual(len(self.tf1), 1)
    self.assertEqual(len(self.tf2), 8)

  def test_collate(self):
    self.assertTrue("001" in self.collated_tf1)
    self.assertTrue("008" in self.collated_tf1)
    self.assertTrue("852" in self.collated_tf1)
    self.assertTrue("245" in self.collated_tf1)
    self.assertTrue("260" in self.collated_tf1)
    self.assertTrue("001" in self.collated_tf2)
    self.assertTrue("008" in self.collated_tf2)
    self.assertTrue("852" in self.collated_tf2)
    self.assertTrue("245" in self.collated_tf2)
    self.assertTrue(len(self.collated_tf1['852']), 2)
    
  def test_tf1_001(self):
    # 000000523
    self.assertTrue(len(self.collated_tf1["001"]) == 1 and self.collated_tf1["001"][0].value() == "000000523")

  def test_tf1_get_sysnum(self):
    self.assertTrue(len(self.collated_tf1["001"]) == 1 and get_sysnum(self.collated_tf1) == "000000523")

  def test_tf1_008_lang(self):
    self.assertTrue(len(self.collated_tf1["008"]) == 1 and self.collated_tf1["008"][0].value()[35:38] == "|||")

  def test_tf1_get_lang(self):
    self.assertTrue(len(self.collated_tf1["008"]) == 1 and get_lang(self.collated_tf1) == "|||")

  def test_tf1_100(self):
    self.assertTrue(len(self.collated_tf1["100"]) == 1 and self.collated_tf1["100"][0].get_subfields("a")[0] == u"A., F. G.")

  def test_tf1_get_names(self):
    expected = {'personal': [u"author/A., F. G."], 'corporate': []}
    self.assertTrue(len(self.collated_tf1["100"]) == 1 and get_names(self.collated_tf1) == expected)

  def test_tf1_get_facetnames(self):
    expected = {'personal': [u"author/A.,_F._G."], 'corporate': []}
    self.assertTrue(len(self.collated_tf1["100"]) == 1 and get_names(self.collated_tf1, facet = True) == expected)

  def test_tf1_245(self):
    expected = u'Tres Imposibles Vencidos, o\u0301 tres inventos del siglo. La direccion de los globos. El movimiento continuo. La cuadratura del ci\u0301rculo. Resolucion y demostracion cienti\u0301fica de estos tres problemas. [The dedication signed: F. G. A. With diagrams.]'
    self.assertTrue(len(self.collated_tf1['245']) == 1 and self.collated_tf1["245"][0].get_subfields("a")[0] == expected)

  def test_tf1_get_titles(self):
    expected = [u'Tres Imposibles Vencidos, o\u0301 tres inventos del siglo. La direccion de los globos. El movimiento continuo. La cuadratura del ci\u0301rculo. Resolucion y demostracion cienti\u0301fica de estos tres problemas. [The dedication signed: F. G. A. With diagrams.]']
    self.assertTrue(len(self.collated_tf1['245']) == 1 and get_titles(self.collated_tf1) == expected)

  def test_tf1_get_pub_detail(self):
    expected = [u"p/Barcelona,", u"", u"p/1864."]
    self.assertTrue(len(self.collated_tf1['260']) == 1 and get_pub_detail(self.collated_tf1) == expected) 

  def test_tf1_get_phys_desc(self):
    expected = [u'55 p. ;', u'8\xba.']
    self.assertTrue(len(self.collated_tf1['300']) == 1 and get_phys_desc(self.collated_tf1) == expected)
  
  def test_tf1_get_general_note(self):
    expected = []
    self.assertTrue(len(self.collated_tf1['500']) == 0 and get_general_note(self.collated_tf1) == expected)

  def test_tf1_get_domids(self):
    expected = []
    self.assertTrue(len(self.collated_tf1['852']) == 1 and get_domids(self.collated_tf1) == expected)

  def test_tf1_get_shelfmarks(self):
    expected = [u'British Library HMNTS 8706.ee.21.(4.)']
    self.assertTrue(len(self.collated_tf1['852']) == 1 and get_shelfmarks(self.collated_tf1) == expected)

  def test_tf2_001(self):
    # 000000523
    self.assertTrue(len(self.collated_tf2["001"]) == 1 and self.collated_tf2["001"][0].value() == u'014811575')

  def test_tf2_get_sysnum(self):
    self.assertTrue(len(self.collated_tf2["001"]) == 1 and get_sysnum(self.collated_tf2) == u'014811575')

  def test_tf2_008_lang(self):
    self.assertTrue(len(self.collated_tf2["008"]) == 1 and self.collated_tf2["008"][0].value()[35:38] == u"und")

  def test_tf2_get_lang(self):
    self.assertTrue(len(self.collated_tf2["008"]) == 1 and get_lang(self.collated_tf2) == u"und")

  def test_tf2_get_names(self):
    expected = {'personal': [u'author/Gibbon, Charles, 1843-1890.'], 'corporate': []}
    self.assertTrue(len(self.collated_tf2["100"]) == 1 and get_names(self.collated_tf2) == expected)

  def test_tf2_get_facetnames(self):
    expected = {'personal': [u'author/Gibbon,_Charles,__1843-1890.'], 'corporate': []}
    self.assertTrue(len(self.collated_tf2["100"]) == 1 and get_names(self.collated_tf2, facet = True) == expected)

  def test_tf2_get_titles(self):
    expected = [u'Dangerous Connexions. A novel. [electronic resource]']
    self.assertTrue(len(self.collated_tf2['245']) == 1 and get_titles(self.collated_tf2) == expected)

  def test_tf2_get_pub_detail(self):
    expected = [u'p/London,', u'', u'p/1864.']
    self.assertTrue(len(self.collated_tf2['260']) == 1 and get_pub_detail(self.collated_tf2) == expected) 

  def test_tf2_get_phys_desc(self):
    expected = [u'3 vol. ;', u'8\xba.']
    self.assertTrue(len(self.collated_tf2['300']) == 1 and get_phys_desc(self.collated_tf2) == expected)
  
  def test_tf2_get_general_note(self):
    expected = [u'Testing General Note']
    self.assertTrue(len(self.collated_tf2['500']) == 1 and get_general_note(self.collated_tf2) == expected)

  def test_tf2_get_domids(self):
    expected = [u'lsidyv3b0a7b28', u'lsidyv3aee4429', u'lsidyv3aee4b76']
    self.assertTrue(len(self.collated_tf2['852']) == 3 and get_domids(self.collated_tf2) == expected)

  def test_tf2_get_shelfmarks(self):
    expected = []
    self.assertTrue(len(self.collated_tf2['852']) == 3 and get_shelfmarks(self.collated_tf2) == expected)

if __name__ == '__main__':
  unittest.main()
