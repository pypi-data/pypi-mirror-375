###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Generic XMLParser used to convert a XML file into more pythonic style.

A tree ox XMLNodes.
"""
import xml.dom.minidom

################################################################################


class XMLNode:
    """XMLNodes represent XML elements.

    May have attributes. They have either children or value ( exclusive-
    or).
    """

    def __init__(self, name):
        self.name = name
        self.attributes = {}
        self.children = None
        self.value = None

    def childrens(self, name):
        """return children."""
        return [child for child in self.children if child.name == name]

    def __repr__(self):
        return f"< {self.name} >"


################################################################################


class XMLTreeParser:
    """XMLTreeParser converts an XML file or a string into a tree of XMLNodes. It
    does not validate the XML.

    Elements that are the only child of an element and are of text or
    cdata type are considered to be the value of their parent.
    """

    def __init__(self):
        self.tree = None

    def parse(self, xmlFile):
        """parse the XML."""
        domXML = xml.dom.minidom.parse(xmlFile)
        self.__handleXML(domXML)
        return self.tree

    def parseString(self, xmlString):
        """parse the XML."""
        domXML = xml.dom.minidom.parseString(xmlString)
        self.__handleXML(domXML)
        return self.tree

    ################################################################################
    # AUXILIAR FUNCTIONS
    ################################################################################

    def __handleXML(self, domXML):
        """handles first child."""
        self.tree = self.__handleElement([domXML.firstChild])

    def __handleElement(self, elements):
        """treat each element."""
        nodes = []

        for el in elements:
            if el.nodeType == el.TEXT_NODE:
                continue

            node = XMLNode(el.localName)
            node.attributes = self.__getAttributesDict(el)

            if len(el.childNodes) == 1:
                childNode = el.childNodes[0]
                if childNode.nodeType == childNode.TEXT_NODE or childNode.nodeType == childNode.CDATA_SECTION_NODE:
                    node.value = self.__handleTextElement(el.childNodes[0])
                else:
                    node.children = self.__handleElement(el.childNodes)
            else:
                node.children = self.__handleElement(el.childNodes)

            nodes.append(node)

        return nodes

    @staticmethod
    def __getAttributesDict(element):
        """get the attributes in a dictionary."""
        dictionary = {}
        if element.attributes:
            for attr in element.attributes.values():
                dictionary[attr.name] = attr.value
        return dictionary

    def __handleTextElement(self, textElement):
        """treat the Text element."""
        return self.__getText(textElement)

    @staticmethod
    def __getText(node):
        """get the TEXT."""
        data = ""
        if node.nodeType == node.TEXT_NODE or node.nodeType == node.CDATA_SECTION_NODE:
            data = node.data
        return data
