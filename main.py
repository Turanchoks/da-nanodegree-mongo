#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import codecs
import json
import re
import collections
import phonenumbers
from urlparse import urlparse
"""
Clean contacts data

A node has to have one dictionary 'contacts'
that has all the contact information.

The problem is that the markup is not unified.
Most of the tag keys start with 'contact:' prefix
but there are still a lot of nodes
that are tagged with just 'phone' or just 'website'
without the prefix.

Moreover, the markup of contact tag values
is not unifiend either.
For example, some websites are missing a protocol type
(http:// or https:// prefix)
Some of them have a trailing slash, others don't
Also, formats of phone numbers are not similar
across the database

There is another big problem:
if a node has multiple websites or phone numbers,
this might be declared as a single tag,
where values are separated by a semicolon.
But there are cases
when a node has multiple tags for a contact type.
Their keys usually look like 'contact:website2'.
"""

# Regexp to detect 'contact' tags
re_contact = re.compile(r"(?:contact:([a-zA-Z]+)|website|phone)(\d+)?")

def format_phone(phone):
    """
    If a number starts with an 8,
    we must change it to 7
    as it is a proper Russia Code
    8 is used only in inter-city calls
    within a country
    """
    if phone.startswith('8'):
        phone = '7' + phone[1:]

    """
    If a number starts with an 8,
    we must change it to 7
    as it is a proper Russia Code
    8 is used only in inter-city calls
    within a country
    """
    if not phone.startswith('+'):

        """
        Some phones has a prefix
        and a valid number goes after prefix.
        Try to find a start of a valid number
        and remove the prefix.
        """
        plus_seven_pos = phone.find('+7')

        if plus_seven_pos != -1:
            phone = phone[plus_seven_pos:]
        else:
            phone = '+' + phone

    try:
        # I use phonenumbers module
        # which is a python version of Google's libphonenumber

        phone = phonenumbers.parse(phone, None)
        phone = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except phonenumbers.phonenumberutil.NumberParseException:
        # Log invalid phonenumbers
        print phone
    finally:
        return phone

def format_website(website):
    """
    I use urlparse to parse
    and then get url back.
    This basically does nothing for valid urls
    but it helps detecting invalid ones.
    """

    website = urlparse(website).geturl()
    return website

def shape_element(element):
    if element.tag == "node" or element.tag == "way":

        node = {}

        # I preserve id, uid of a user and tag type
        node['id'] = element.attrib['id']
        node['uid'] = element.attrib['uid']
        node['type'] = element.tag

        # Contacts is a dict of lists for each contact type.
        # I use defaultdict here so I append to the lists safely
        # without checking if this contact type already exists.
        node['contacts'] = collections.defaultdict(list)

        # Tags will be filled with non-contact tags
        node['tags'] = {}


        for tag in element.iter('tag'):
            k = tag.attrib['k']
            v = tag.attrib['v']

            # Match contact tags
            match = re_contact.match(k)

            if match:
                # As there can be tag keys without 'contact:' prefix
                # that are equal to 'phone' or 'website',
                # then the whole key will match and we need the zero-th group
                type = match.group(1) or match.group(0)

                # Sometimes phones and websites
                # are separated by a semicolon or a comma
                v = [v.strip() for v in re.split('[;,]', v)]

                # Format phones and websites
                if type == 'phone':
                    v = map(format_phone, v)
                elif type == 'website':
                    v = map(format_website, v)

                # Extend the appropriate contact type with the new values
                # defaultdict helps not cause a missing error.
                node['contacts'][type].extend(v)
            else:
                # If tag is not a contact,
                # just add to the tags dict
                node['tags'][k] = v

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
