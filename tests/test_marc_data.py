#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest, pymarc, os

from utils.marcutils import *

TF1 = "tests/single.xml"

class TestMARCParsing(unittest.TestCase):
  def setUp(self):
    self.tf1 = pymarc.parse_xml_to_array(TF1)
    self.collated_tf1 = collate(self.tf1[0])

  def test_validate_testdata(self):
    self.assertEqual(len(self.tf1), 1)

  def test_collate(self):
    self.assertTrue("001" in self.collated_tf1)
    self.assertTrue("008" in self.collated_tf1)
    self.assertTrue("852" in self.collated_tf1)
    self.assertTrue("245" in self.collated_tf1)
    self.assertTrue("260" in self.collated_tf1)
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

if __name__ == '__main__':
  unittest.main()
