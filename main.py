#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import codecs
import json

def shape_element(element):
    if element.tag == "node" or element.tag == "way":

        tags = {}

        for tag in element.iter('tag'):
            tags[tag.attrib['k']] = tag.attrib['v']

        node = {
            "id": element.attrib['id'],
            "uid": element.attrib['uid'],
            "type": element.tag
        }

        if len(tags) > 0:
            node['tags'] = tags

        return node

    else:
        return None

def process_map(file_in):
    file_out = "{0}.json".format(file_in)
    with codecs.open(file_out, "w", "utf-8") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                fo.write(json.dumps(el) + "\n")
                # element.clear()

if __name__ == "__main__":
    process_map('sochi_russia.osm')
