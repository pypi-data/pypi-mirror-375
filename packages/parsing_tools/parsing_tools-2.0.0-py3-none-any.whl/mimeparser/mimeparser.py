# -*- coding: utf-8 -*-
#
# mimeparser/mimeparser.py
#
# See MIT License file.
#
"""
Parse MIME types that are usually found in HTTP headers.

Parsing `Accept` headers correctly has become very important with the
ubiquitus use of RESTful web services because, versioning of the service
is often defined in the MIME type.

For reference see the following RFCs:

https://tools.ietf.org/html/rfc4288#section-3.2 (Vendor spec)
https://tools.ietf.org/html/rfc7231#section-3.1.1.1 (Media Type)
https://tools.ietf.org/html/rfc7231#section-5.3.1 (quality spec)
https://tools.ietf.org/html/rfc6839 (Suffix spec)

The basic idea of this code I got from Joe Gregorio,
https://github.com/jcgregorio/mimeparse

Entry point:
 - best_match() -- Primary method to find the mime type derived from the
                   closest match to the available mime types.
 - parse_mime() -- Returns a parsed mime type into it's parts.
"""
__docformat__ = "restructuredtext en"

from collections import OrderedDict
from decimal import Decimal, InvalidOperation, getcontext


class MIMEParser(object):

    def __init__(self, parm_val_lower=True):
        self._parm_val_lower = parm_val_lower
        getcontext().prec = 4

    def best_match(self, available_mtypes, header_mtypes):
        """
        Return the best match from `header_mtypes` based on the
        `available_mtypes`.

        mtype is a value driectly from any header where mime types can be
        found. ie. Content-Type, Accept

        Examples:
          >>> best_match(['text/html', 'application/xbel+xml'],
                  'text/*;q=0.3, text/html;q=0.7, text/html;level=1,'
                  ' text/html;level=2;q=0.4, */*;q=0.5')
          'text/html'

          >>> best_match(['application/xbel+xml', 'text/xml'],
                         'text/*;q=0.5,*/*; q=0.1')
          'text/xml'
        """
        weighted_matches = self._best_weighted_matches(available_mtypes,
                                                       header_mtypes)
        return weighted_matches[0][4]

    def _best_weighted_matches(self, available_mtypes, header_mtypes):
        weighted_matches = []
        header_mtypes = [self.parse_mime(mt)
                         for mt in header_mtypes.split(',')]

        for pos, mtype in enumerate(available_mtypes):
            parsed_mtype = self.parse_mime(mtype)
            fit_and_q = self._fitness_and_quality(parsed_mtype, header_mtypes)
            fit_and_q.append(pos)
            fit_and_q.append(mtype)
            weighted_matches.append(fit_and_q)

        weighted_matches.sort(reverse=True)
        # [best_fit, best_params, best_fit_q, pos, mime]
        return weighted_matches

    def parse_mime(self, mtype):
        """
        Parses a mime-type into its component parts.

        Works with a single mime type and returns it's component parts in
        a tuple as in (type, subtype, suffix, params), where params is a
        dict of all the optional parameters of the mime type.

        For example, 'application/xhtml+xml;q=0.5;ver=1' would result in:

        ('application', 'xhtml', 'xml', {'q': Decimal(0.5),
                                         'ver': Decimal(1)}
        )

        All numeric values to any parameter are returned as a python
        Decimal object.
        """
        parts = mtype.split(';')
        params = OrderedDict()

        # Split parameters and convert numeric values to a Decimal object.
        for k, v in [param.split('=', 1) for param in parts[1:]]:
            k = k.strip().lower()
            v = v.strip().strip('\'"')

            if self._parm_val_lower:
                v = v.lower()

            try:
                v = Decimal(v)
            except InvalidOperation:
                if k == 'q':
                    v = Decimal("1.0")

            params[k] = v

        # Add/fix quality values.
        quality = params.get('q')

        if ('q' not in params
            or quality > Decimal("1.0")
            or quality < Decimal("0.0")):
            params['q'] = Decimal("1.0")

        full_type = parts[0].strip().lower()

        # Fix non-standard single asterisk.
        if full_type == '*':
            full_type = '*/*'

        type, sep, subtype = full_type.partition('/')

        if '+' in subtype:
            idx = subtype.rfind('+')
            suffix = subtype[idx+1:].strip()
            subtype = subtype[:idx]
        else:
            suffix = ''

        return type.strip(), subtype.strip(), suffix, params

    def _fitness_and_quality(self, available_mtype, header_mtypes):
        """
        Find the best match for a pre-parsed header_mtype within
        pre-parsed ranges.

        available_mtype - One of a list of available preparsed mimetypes.
        header_mtypes   - Available preparsed mimetypes.

        Returns a tuple of the fitness value and the value of the 'q'
        (quality) parameter of the best match, or (-1, Decimal("0.0")) if
        no match was found.
        """
        best_fit = -1
        best_fit_q = Decimal("0.0")
        best_params = 0
        (target_type, target_subtype,
         target_suffix, target_params) = available_mtype

        for mtype, subtype, suffix, params in header_mtypes:
            # type_match = (mtype == target_type or mtype == '*'
            #               or target_type == '*')
            # subtype_match = (subtype == target_subtype or subtype == '*'
            #                  or target_subtype == '*')
            # suffix_match = (suffix == target_suffix or not suffix
            #                 or not target_suffix)
            fitness = 0

            if mtype == target_type:
                fitness += int(bin(4), 2)

            if subtype == target_subtype:
                fitness += int(bin(2), 2)

            if suffix == target_suffix:
                fitness += int(bin(1), 2)

            # Give weight to a suffix equal to a subtype.
            if suffix == target_subtype:
                fitness += int(bin(2), 2)

            best_params = sum(
                [1 for key, value in target_params.items()
                 if key != 'q' and key in params
                 and value == params[key]], 0)

            if fitness > best_fit:
                best_fit = fitness
                best_fit_q = params.get('q', Decimal("0"))

        return [best_fit, best_params, best_fit_q]
