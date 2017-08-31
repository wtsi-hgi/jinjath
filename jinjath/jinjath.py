#!/usr/bin/env python3
################################################################################
# Copyright (c) 2017 Genome Research Ltd.
#
# Author: Joshua C. Randall <jcrandall@alum.mit.edu>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
################################################################################

import sys

from argparse import Action

from jinja2 import Template
from jinja2 import exceptions as jinja_exc

_template_kwargs = {}

def set_template_kwargs(template_kwargs):
    global _template_kwargs
    _template_kwargs = template_kwargs

class TemplateWithSourceSyntaxError(Exception):
    """
    A Jinja TemplateSyntaxError which also reports the template source that triggered the error
    """

class TemplateWithSource(Template, **kwargs):
    def __new__(cls, source):
        try:
            rv = super().__new__(cls, source, **_template_kwargs, **kwargs)
        except jinja_exc.TemplateSyntaxError as e:
            raise TemplateWithSourceSyntaxError("Syntax error in template. Template source was '%s'" % (source)) from e
        rv._source = source
        return rv

    def source(self):
        return self._source

class JinjaTemplateAction(Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)
    def __call__(self, parser, namespace, source, option_string=None):
        try:
            template = TemplateWithSource(source)
        except TemplateWithSourceSyntaxError as e:
            raise TemplateWithSourceSyntaxError("Syntax error in template specified by %s." % (option_string)) from e
        setattr(namespace, self.dest, template)
