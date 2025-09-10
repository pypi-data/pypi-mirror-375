# -*- coding: utf-8 -*-
#
# xml2dict/xml2dict.py
#
# See MIT License file.
#
"""
Convert XML to a Python dict.

"""
__docformat__ = "restructuredtext en"


import io
import re
import six
import logging
import defusedxml.ElementTree as ET


class XML2Dict(object):
    __NSPACE_REGEX = r"^\{(?P<uri>.*)\}(?P<local>.*)$"
    __NSPACE_OBJ = re.compile(__NSPACE_REGEX)
    # __PREFIX_REGEX = r"^(?P<xmlns>xmlns):?(?P<prefix>.*)?$"
    # __PREFIX_OBJ = re.compile(__PREFIX_REGEX)

    def __init__(self, empty_tags=True, rm_whitespace=True, logger_name='',
                 level=None, strip_list=False):
        if logger_name == '':
            logging.basicConfig()

        self._log = logging.getLogger(logger_name)

        if level:
            self._log.setLevel(level)

        self.__empty_tags = empty_tags
        self.__rm_whitespace = rm_whitespace
        self.__strip_list = strip_list

    def _set_file_object(self, xml):
        if isinstance(xml, io.IOBase):
            xml.seek(0)  # Make sure we're at the start of the file.
            self._xml = xml
        else:
            self._xml = six.StringIO(xml)

    def parse(self, xml, encoding=None):
        data = []
        parser = ET.DefusedXMLParser(encoding=encoding)
        self._set_file_object(xml)

        try:
            tree = ET.parse(self._xml, parser=parser, forbid_dtd=True)
            root = tree.getroot()
            self.__node(data, root)
        except ET.ParseError as e:
            self._log.error("Could not parse xml, %s", e, exc_info=True)
            raise e

        if self.__strip_list and len(data) == 1:
            data = data[0]

        self._log.debug("data: %s", data)
        return data

    def __node(self, data, node):
        child_data = {}
        data.append(child_data)
        # Process tag
        tag_name = node.tag
        nspace, name = self.__split_namespace(tag_name)
        text = self.value_hook(node.text)
        child_data['attrib'] = {k: self.value_hook(v)
                                for k, v in node.attrib.items()}
        child_data['element'] = {'nspace': nspace,
                                 'tag': name,
                                 'value': self.__tag_value(text)}
        children_data = []
        child_data['children'] = children_data
        has_findall = hasattr(node, 'findall')  # Only from 3.8 and greater.
        children = node.findall("./*") if has_findall else node.getchildren()

        for child in children:
            self.__node(children_data, child)

    def __split_namespace(self, tag):
        sre = self.__NSPACE_OBJ.search(tag)

        if sre:
            nspace = sre.group('uri')
            name = sre.group('local')
        else:
            nspace = ''
            name = tag

        return nspace, name

    def __tag_value(self, text):
        if text:
            if self.__rm_whitespace:
                text = text.strip()
        elif self.__empty_tags:
            text = ''

        return text

    def value_hook(self, value):
        """
        This hook can be overridden to convert values to Python types.
        """
        return value
