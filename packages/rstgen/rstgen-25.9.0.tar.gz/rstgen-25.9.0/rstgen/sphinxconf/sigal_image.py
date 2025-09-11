# -*- coding: utf-8 -*-
# Copyright 2014-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Defines the :rst:dir:`sigal_image` directive.

.. rst:directive:: sigal_image

.. _picsel: https://github.com/lsaffre/picsel
.. _Shotwell: https://en.wikipedia.org/wiki/Shotwell_%28software%29
.. _digiKam: https://www.digikam.org/
.. _Sigal: http://sigal.saimon.org/en/latest/

This creates a bridge between a photo collection managed with
Shotwell_ or digiKam_ and a blog generated with Sphinx.  All photos
remain in the single central file tree managed by Shotwell_ or
digiKam_.  From within Shotwell_ or digiKam_ you use a tag "blog" to
mark all photos that are to be available for your Sphinx blog.  Then
you use picsel_ to extract those images to a separate directory.  This
tree serves as input for Sigal_ which will generate a static html
gallery.  An example of a Sigal gallery is `here
<http://sigal.saffre-rumma.net/>`__.  The :rst:dir:`sigal_image`
directive was the last missing part of this publishing bridge: it
allows you to integrate your pictures into blog entries.

Usage::

  .. sigal_image:: partial/path/to/photo.jpg[|title_or_options]


For example, if `sigal_base_url` in your :xfile:`conf.py` is set to
``"http://sigal.saffre-rumma.net"``, the following directive in your
rst source file::

  .. sigal_image:: 2014/04/10/img_6617.jpg

will insert the following rst code::

    .. raw:: html

      <a href="http://sigal.saffre-rumma.net/2014/04/10/img_6617.jpg">
      <img
      src="http://sigal.saffre-rumma.net/2014/04/10/thumbnails/img_6617.jpg"/>
    </a>


The file name can contain **formatting instructions** inspired by
`Wikipedia pictures
<https://en.wikipedia.org/wiki/Wikipedia:Picture_tutorial>`_ which
uses a variable number of pipe characters. For example:


>>> print(line2html("foo.jpg"))
<a href="http://example.com/foo.jpg"  data-lightbox="image-1" data-title="foo.jpg"/><img src="http://example.com/thumbnails/foo.jpg" style="padding:4px; max-width:100%; max-height:20ex" title="foo.jpg"/></a>

>>> print(line2html("foo.jpg|This is a nice picture"))
<a href="http://example.com/foo.jpg"  data-lightbox="image-1" data-title="This is a nice picture"/><img src="http://example.com/thumbnails/foo.jpg" style="padding:4px; max-width:100%; max-height:20ex" title="This is a nice picture"/></a>

>>> print(line2html("foo.jpg|thumb|This is a nice picture"))
<a href="http://example.com/foo.jpg"  data-lightbox="image-1" data-title="This is a nice picture"/><img src="http://example.com/thumbnails/foo.jpg" style="padding:4px; max-width:100%; float:right; max-height:20ex" title="This is a nice picture"/></a>

>>> print(line2html("foo.jpg|thumb|left|This is a nice picture"))
<a href="http://example.com/foo.jpg"  data-lightbox="image-1" data-title="This is a nice picture"/><img src="http://example.com/thumbnails/foo.jpg" style="padding:4px; max-width:100%; float:left; max-height:20ex" title="This is a nice picture"/></a>

>>> print(line2html("foo.jpg|wide|This is a wide picture"))
<a href="http://example.com/foo.jpg"  data-lightbox="image-1" data-title="This is a wide picture"/><img src="http://example.com/thumbnails/foo.jpg" style="padding:4px; max-width:100%; max-height:30ex" title="This is a wide picture"/></a>

>>> print(line2html("foo.jpg | thumb | left | This is a nice picture"))
<a href="http://example.com/foo.jpg"  data-lightbox="image-1" data-title="This is a nice picture"/><img src="http://example.com/thumbnails/foo.jpg" style="padding:4px; max-width:100%; float:left; max-height:20ex" title="This is a nice picture"/></a>


The generated HTML also includes attributes for `lightbox
<http://lokeshdhakar.com/projects/lightbox2/>`_.  In order to activate
this feature you must add the content of the lighbox :file:`dist`
directory somewhere to your web server and then change your
`layout.html` template to something like this::

    {%- block extrahead %}
      {{ super() }}
    <script src="/data/lightbox/js/lightbox-plus-jquery.min.js"></script>
    <link href="/data/lightbox/css/lightbox.css" rel="stylesheet" />
    {% endblock %}
"""

import os
from rstgen.sphinxconf.insert_input import InsertInputDirective

TEMPLATE1 = """

.. raw:: html

    <a href="%(target)s"><img src="%(src)s" style="padding:4px"/></a>

"""

# TEMPLATE = """<a href="%(target)s" style="%(style)s" %(class)s data-lightbox="image-1" data-title="%(caption)s"/><img src="%(src)s" style="padding:4px" title="%(caption)s"/></a>"""

TEMPLATE = """<a href="%(target)s" %(class)s data-lightbox="image-1" data-title="%(caption)s"/><img src="%(src)s" style="%(style)s" title="%(caption)s"/></a>"""


class Format(object):
    padding = "4px"
    width = None
    height = None
    float = None

    def __init__(self, caption, **context):
        context.update(caption=caption.strip())
        if not 'style' in context:
            styles = []
            for k in ('padding', 'width', 'float', 'height'):
                v = context.get(k, getattr(self, k, None))
                if v:
                    sk = k
                    if k in ('width', 'height'):
                        sk = "max-" + k
                    styles.append("{}:{}".format(sk, v))
                    # if k == "max_height":
                    #     styles.append("max-width:100%")
                    # styles.append("box-sizing: border-box;")

            context.update(style="; ".join(styles))
        self.context = context


class Standard(Format):
    height = "20ex"
    width = "100%"


class Thumb(Standard):

    float = "right"

    def __init__(self, caption, **context):
        chunks = caption.split('|', 1)
        if len(chunks) == 2:
            # raise Exception("20230408 {} {} {}".format(
            #     self.__class__.__name__, text, self.float))
            align, caption = chunks
            align = align.strip()
            if not align in ("right", "left"):
                raise Exception("Invalid alignment '{0}'".format(align))
            context.update(float=align)
            # tplkw['style'] = "padding:4px; float:{0}; height:{1};".format(align, self.height)
        super().__init__(caption, **context)

        # tplkw.update(caption=caption)


class Tiny(Standard):
    height = "15ex"
    width = "25%"


class Wide(Standard):
    width = "100%"
    height = "30ex"


class Solo(Standard):
    width = "100%"
    height = "60ex"


class Duo(Standard):
    width = "45%"


class Trio(Standard):
    width = "30%"


FORMATS = dict()
FORMATS[None] = Standard
# FORMATS['height10em'] = Height10em
FORMATS['thumb'] = Thumb
FORMATS['tiny'] = Tiny
FORMATS['wide'] = Wide
FORMATS['solo'] = Solo
FORMATS['duo'] = Duo
FORMATS['trio'] = Trio


def parse_image_spec(caption, **context):
    """
    Parse an image specification that can contain optional formatting
    instructions inspired by `Wikipedia pictures
    <https://en.wikipedia.org/wiki/Wikipedia:Picture_tutorial>`_, which uses a
    variable number of pipe characters.

    This is also being used by :mod:`lino.modlib.uploads`. See
    :ref:`dg.projects.noi2`

    """
    fmt = FORMATS[None]
    if caption:
        chunks = caption.split('|', 1)
        if len(chunks) == 2:
            fmtname, caption = chunks
            fmtname = fmtname.strip()
            # raise Exception("20230408 b {} {}".format(fmtname, ctx))
            fmt = FORMATS.get(fmtname, None)
            if fmt is None:
                raise Exception(
                    "Invalid format name '{}' (allowed names are {}).".format(
                        fmtname, tuple(filter(None, FORMATS.keys()))))
        # else:
        #     raise Exception("20230408 c {} {}".format(chunks, ctx))
        caption = caption.strip()
    return fmt(caption or "", **context)


def buildurl(*parts):
    return 'http://example.com' + ('/'.join(parts))


def line2html(name, buildurl=buildurl, **kw):
    name = name.strip()
    if not name:
        return ''
    caption = name
    chunks = caption.split('|', 1)
    if len(chunks) == 2:
        name, caption = chunks
        name = name.strip()
        caption = caption.strip()
    fmt = parse_image_spec(caption)
    kw.update(fmt.context)
    # kw.update(caption=caption)

    # kw = dict(caption='')  # style="padding:4px")
    kw['class'] = ''
    # kw['style'] = "padding:4px; height:10em;"
    if ' ' in name:
        raise Exception("Invalid filename. Spaces not allowed.")

    head, tail = os.path.split(name)
    kw.update(target=buildurl(head, tail))
    kw.update(src=buildurl(head, 'thumbnails', tail))
    return TEMPLATE % kw


class SigalImage(InsertInputDirective):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False

    # option_spec = {
    #     'style': directives.unchanged,
    #     'class': directives.unchanged,
    # }

    def get_rst(self):
        env = self.state.document.settings.env
        base_url = env.config.sigal_base_url

        def buildurl(*parts):
            return base_url + '/' + '/'.join(parts)

        s = ''
        for name in self.content:
            s += line2html(name, buildurl)

        if s:
            s = "\n\n.. raw:: html\n\n  {0}\n\n".format(s)

        return s

    def get_headers(self):
        return ['title', 'author', 'date']

    def format_entry(self, e):
        cells = []
        # text = ''.join([unicode(c) for c in e.title.children])
        # cells.append(":doc:`%s <%s>`" % (text, e.docname))
        cells.append(":doc:`%s`" % e.docname)
        cells.append(str(e.meta.get('author', '')))
        cells.append(str(e.meta.get('date', '')))
        return cells


def setup(app):
    app.add_config_value('sigal_base_url', 'http://sigal.saffre-rumma.net',
                         True)
    app.add_directive('sigal_image', SigalImage)
    # app.add_role(str('rref'), ReferingRefRole(
    #     lowercase=True,
    #     innernodeclass=nodes.emphasis,
    #     warn_dangling=True))
