import io
import logging
import os.path
import posixpath as zip_path
import re
import tempfile
import uuid
import warnings
import zipfile
from collections import OrderedDict

import six
from bs4 import BeautifulSoup, NavigableString
from izihawa_textutils.html_processing import canonize_tags

from ._banned_sections import BANNED_SECTION_PREFIXES, BANNED_SECTIONS
from .utils import md

try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

import ebooklib
from ebooklib.utils import guess_type, parse_html_string
from lxml import etree

# Version of EPUB library
VERSION = (0, 18, 1)

NAMESPACES = {
    "XML": "http://www.w3.org/XML/1998/namespace",
    "EPUB": "http://www.idpf.org/2007/ops",
    "DAISY": "http://www.daisy.org/z3986/2005/ncx/",
    "OPF": "http://www.idpf.org/2007/opf",
    "CONTAINERNS": "urn:oasis:names:tc:opendocument:xmlns:container",
    "DC": "http://purl.org/dc/elements/1.1/",
    "XHTML": "http://www.w3.org/1999/xhtml",
}

# XML Templates

CONTAINER_PATH = "META-INF/container.xml"

CONTAINER_XML = """<?xml version="1.0" encoding="utf-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles>
    <rootfile media-type="application/oebps-package+xml" full-path="%(folder_name)s/content.opf"/>
  </rootfiles>
</container>
"""

NCX_XML = six.b(
    """<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" />"""
)

NAV_XML = six.b(
    """<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"/>"""
)

CHAPTER_XML = six.b(
    """<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"  epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/#"></html>"""
)

COVER_XML = six.b(
    """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
 <head>
  <style>
    body { margin: 0em; padding: 0em; }
    img { max-width: 100%; max-height: 100%; }
  </style>
 </head>
 <body>
   <img src="" alt="" />
 </body>
</html>"""
)
# LIST OF POSSIBLE ITEMS
ITEM_UNKNOWN = 0
ITEM_IMAGE = 1
ITEM_STYLE = 2
ITEM_SCRIPT = 3
ITEM_NAVIGATION = 4
ITEM_VECTOR = 5
ITEM_FONT = 6
ITEM_VIDEO = 7
ITEM_AUDIO = 8
ITEM_DOCUMENT = 9
ITEM_COVER = 10
ITEM_SMIL = 11

IMAGE_MEDIA_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/svg+xml"]


# TOC and navigation elements


class Section(object):
    def __init__(self, title, href=""):
        self.title = title
        self.href = href


class Link(object):
    def __init__(self, href, title, uid=None):
        self.href = href
        self.title = title
        self.uid = uid


# Exceptions


class EpubException(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


def parse_string(s):
    parser = etree.XMLParser(recover=True, resolve_entities=False)
    try:
        tree = etree.parse(io.BytesIO(s.encode("utf-8")), parser=parser)
    except Exception:
        tree = etree.parse(io.BytesIO(s), parser=parser)

    return tree


class EpubItem(object):
    """
    Base class for the items in a book.
    """

    def __init__(
        self, uid=None, file_name="", media_type="", content=six.b(""), manifest=True
    ):
        """
        :Args:
          - uid: Unique identifier for this item (optional)
          - file_name: File name for this item (optional)
          - media_type: Media type for this item (optional)
          - content: Content for this item (optional)
          - manifest: Manifest for this item (optional)
        """
        self.id = uid
        self.file_name = file_name
        self.media_type = media_type
        self.content = content
        self.is_linear = True
        self.manifest = manifest

        self.book = None

    def get_id(self):
        """
        Returns unique identifier for this item.

        :Returns:
          Returns uid number as string.
        """
        return self.id

    def get_name(self):
        """
        Returns name for this item. By default it is always file name but it does not have to be.

        :Returns:
          Returns file name for this item.
        """
        return self.file_name

    def get_type(self):
        """
        Guess type according to the file extension. Might not be the best way how to do it, but it works for now.

        Items can be of type:
          - ITEM_UNKNOWN = 0
          - ITEM_IMAGE = 1
          - ITEM_STYLE = 2
          - ITEM_SCRIPT = 3
          - ITEM_NAVIGATION = 4
          - ITEM_VECTOR = 5
          - ITEM_FONT = 6
          - ITEM_VIDEO = 7
          - ITEM_AUDIO = 8
          - ITEM_DOCUMENT = 9
          - ITEM_COVER = 10

        We map type according to the extensions which are defined in ebooklib.EXTENSIONS.

        :Returns:
          Returns type of the item as number.
        """
        _, ext = zip_path.splitext(self.get_name())
        ext = ext.lower()

        for uid, ext_list in six.iteritems(ebooklib.EXTENSIONS):
            if ext in ext_list:
                return uid

        return ebooklib.ITEM_UNKNOWN

    def __str__(self):
        return "<EpubItem:%s>" % self.id


class EpubNcx(EpubItem):
    "Represents Navigation Control File (NCX) in the EPUB."

    def __init__(self, uid="ncx", file_name="toc.ncx"):
        super(EpubNcx, self).__init__(
            uid=uid, file_name=file_name, media_type="application/x-dtbncx+xml"
        )

    def __str__(self):
        return "<EpubNcx:%s>" % self.id


class EpubCover(EpubItem):
    """
    Represents Cover image in the EPUB file.
    """

    def __init__(self, uid="cover-img", file_name=""):
        super(EpubCover, self).__init__(uid=uid, file_name=file_name)

    def get_type(self):
        return ebooklib.ITEM_COVER

    def __str__(self):
        return "<EpubCover:%s:%s>" % (self.id, self.file_name)


class EpubHtml(EpubItem):
    """
    Represents HTML document in the EPUB file.
    """

    _template_name = "chapter"

    def __init__(
        self,
        uid=None,
        file_name="",
        media_type="",
        content=None,
        title="",
        lang=None,
        direction=None,
        media_overlay=None,
        media_duration=None,
    ):
        super(EpubHtml, self).__init__(uid, file_name, media_type, content)

        self.title = title
        self.lang = lang
        self.direction = direction

        self.media_overlay = media_overlay
        self.media_duration = media_duration

        self.links = []
        self.properties = []
        self.pages = []

    def is_chapter(self):
        """
        Returns if this document is chapter or not.

        :Returns:
          Returns book value.
        """
        return True

    def get_type(self):
        """
        Always returns ebooklib.ITEM_DOCUMENT as type of this document.

        :Returns:
          Always returns ebooklib.ITEM_DOCUMENT
        """

        return ebooklib.ITEM_DOCUMENT

    def set_language(self, lang):
        """
        Sets language for this book item. By default it will use language of the book but it
        can be overwritten with this call.
        """
        self.lang = lang

    def get_language(self):
        """
        Get language code for this book item. Language of the book item can be different from
        the language settings defined globaly for book.

        :Returns:
          As string returns language code.
        """
        return self.lang

    def add_link(self, **kwgs):
        """
        Add additional link to the document. Links will be embeded only inside of this document.

        >>> add_link(href='styles.css', rel='stylesheet', type='text/css')
        """
        self.links.append(kwgs)
        if kwgs.get("type") == "text/javascript":
            if "scripted" not in self.properties:
                self.properties.append("scripted")

    def get_links(self):
        """
        Returns list of additional links defined for this document.

        :Returns:
          As tuple return list of links.
        """
        return (link for link in self.links)

    def get_links_of_type(self, link_type):
        """
        Returns list of additional links of specific type.

        :Returns:
          As tuple returns list of links.
        """
        return (link for link in self.links if link.get("type", "") == link_type)

    def add_item(self, item):
        """
        Add other item to this document. It will create additional links according to the item type.

        :Args:
          - item: item we want to add defined as instance of EpubItem
        """
        if item.get_type() == ebooklib.ITEM_STYLE:
            self.add_link(href=item.get_name(), rel="stylesheet", type="text/css")

        if item.get_type() == ebooklib.ITEM_SCRIPT:
            self.add_link(src=item.get_name(), type="text/javascript")

    def get_body_content(self):
        return BeautifulSoup(self.content, "lxml")

    def __str__(self):
        return "<EpubHtml:%s:%s>" % (self.id, self.file_name)


class EpubCoverHtml(EpubHtml):
    """
    Represents Cover page in the EPUB file.
    """

    def __init__(
        self, uid="cover", file_name="cover.xhtml", image_name="", title="Cover"
    ):
        super(EpubCoverHtml, self).__init__(uid=uid, file_name=file_name, title=title)

        self.image_name = image_name
        self.is_linear = False

    def is_chapter(self):
        """
        Returns if this document is chapter or not.

        :Returns:
          Returns book value.
        """

        return False

    def __str__(self):
        return "<EpubCoverHtml:%s:%s>" % (self.id, self.file_name)


class EpubNav(EpubHtml):
    """
    Represents Navigation Document in the EPUB file.
    """

    def __init__(
        self,
        uid="nav",
        file_name="nav.xhtml",
        media_type="application/xhtml+xml",
        title="",
    ):
        super(EpubNav, self).__init__(
            uid=uid, file_name=file_name, media_type=media_type, title=title
        )

    def is_chapter(self):
        """
        Returns if this document is chapter or not.

        :Returns:
          Returns book value.
        """

        return False

    def __str__(self):
        return "<EpubNav:%s:%s>" % (self.id, self.file_name)


class EpubImage(EpubItem):
    """
    Represents Image in the EPUB file.
    """

    def __init__(self, *args, **kwargs):
        super(EpubImage, self).__init__(*args, **kwargs)

    def get_type(self):
        return ebooklib.ITEM_IMAGE

    def __str__(self):
        return "<EpubImage:%s:%s>" % (self.id, self.file_name)


class EpubSMIL(EpubItem):
    def __init__(self, uid=None, file_name="", content=None):
        super(EpubSMIL, self).__init__(
            uid=uid,
            file_name=file_name,
            media_type="application/smil+xml",
            content=content,
        )

    def get_type(self):
        return ebooklib.ITEM_SMIL

    def __str__(self):
        return "<EpubSMIL:%s:%s>" % (self.id, self.file_name)


# EpubBook


class EpubBook(object):
    def __init__(self):
        self.EPUB_VERSION = None

        self.reset()

        # we should have options here

    def reset(self):
        "Initialises all needed variables to default values"

        self.metadata = {}
        self.items = []
        self.spine = []
        self.guide = []
        self.pages = []
        self.toc = []
        self.bindings = []

        self.IDENTIFIER_ID = "id"
        self.FOLDER_NAME = "EPUB"

        self._id_html = 0
        self._id_image = 0
        self._id_static = 0

        self.title = ""
        self.language = "en"
        self.direction = None

        self.templates = {
            "ncx": NCX_XML,
            "nav": NAV_XML,
            "chapter": CHAPTER_XML,
            "cover": COVER_XML,
        }

        self.add_metadata(
            "OPF",
            "generator",
            "",
            {
                "name": "generator",
                "content": "Ebook-lib %s" % ".".join([str(s) for s in VERSION]),
            },
        )

        # default to using a randomly-unique identifier if one is not specified manually
        self.set_identifier(str(uuid.uuid4()))

        # custom prefixes and namespaces to be set to the content.opf doc
        self.prefixes = []
        self.namespaces = {}

    def set_identifier(self, uid):
        """
        Sets unique id for this epub

        :Args:
          - uid: Value of unique identifier for this book
        """

        self.uid = uid

        self.set_unique_metadata(
            "DC", "identifier", self.uid, {"id": self.IDENTIFIER_ID}
        )

    def set_title(self, title):
        """
        Set title. You can set multiple titles.

        :Args:
          - title: Title value
        """

        self.title = title

        self.add_metadata("DC", "title", self.title)

    def set_language(self, lang):
        """
        Set language for this epub. You can set multiple languages. Specific items in the book can have
        different language settings.

        :Args:
          - lang: Language code
        """

        self.language = lang

        self.add_metadata("DC", "language", lang)

    def set_direction(self, direction):
        """
        :Args:
          - direction: Options are "ltr", "rtl" and "default"
        """

        self.direction = direction

    def set_cover(self, file_name, content, create_page=True):
        """
        Set cover and create cover document if needed.

        :Args:
          - file_name: file name of the cover page
          - content: Content for the cover image
          - create_page: Should cover page be defined. Defined as bool value (optional). Default value is True.
        """

        # as it is now, it can only be called once
        c0 = EpubCover(file_name=file_name)
        c0.content = content
        self.add_item(c0)

        if create_page:
            c1 = EpubCoverHtml(image_name=file_name)
            self.add_item(c1)

        self.add_metadata(
            None, "meta", "", OrderedDict([("name", "cover"), ("content", "cover-img")])
        )

    def add_author(self, author, file_as=None, role=None, uid="creator"):
        "Add author for this document"

        self.add_metadata("DC", "creator", author, {"id": uid})

        if file_as:
            self.add_metadata(
                None,
                "meta",
                file_as,
                {
                    "refines": "#" + uid,
                    "property": "file-as",
                    "scheme": "marc:relators",
                },
            )
        if role:
            self.add_metadata(
                None,
                "meta",
                role,
                {"refines": "#" + uid, "property": "role", "scheme": "marc:relators"},
            )

    def add_metadata(self, namespace, name, value, others=None):
        "Add metadata"

        if namespace in NAMESPACES:
            namespace = NAMESPACES[namespace]

        if namespace not in self.metadata:
            self.metadata[namespace] = {}

        if name not in self.metadata[namespace]:
            self.metadata[namespace][name] = []

        self.metadata[namespace][name].append((value, others))

    def get_metadata(self, namespace, name):
        "Retrieve metadata"

        if namespace in NAMESPACES:
            namespace = NAMESPACES[namespace]

        return self.metadata[namespace].get(name, [])

    def set_unique_metadata(self, namespace, name, value, others=None):
        "Add metadata if metadata with this identifier does not already exist, otherwise update existing metadata."

        if namespace in NAMESPACES:
            namespace = NAMESPACES[namespace]

        if namespace in self.metadata and name in self.metadata[namespace]:
            self.metadata[namespace][name] = [(value, others)]
        else:
            self.add_metadata(namespace, name, value, others)

    def add_item(self, item):
        """
        Add additional item to the book. If not defined, media type and chapter id will be defined
        for the item.

        :Args:
          - item: Item instance
        """
        if item.media_type == "":
            (has_guessed, media_type) = guess_type(item.get_name().lower())

            if has_guessed:
                if media_type is not None:
                    item.media_type = media_type
                else:
                    item.media_type = has_guessed
            else:
                item.media_type = "application/octet-stream"

        if not item.get_id():
            # make chapter_, image_ and static_ configurable
            if isinstance(item, EpubHtml):
                item.id = "chapter_%d" % self._id_html
                self._id_html += 1
                # If there's a page list, append it to the book's page list
                self.pages += item.pages
            elif isinstance(item, EpubImage):
                item.id = "image_%d" % self._id_image
                self._id_image += 1
            else:
                item.id = "static_%d" % self._id_static
                self._id_static += 1

        item.book = self
        self.items.append(item)

        return item

    def get_item_with_id(self, uid):
        """
        Returns item for defined UID.

        >>> book.get_item_with_id('image_001')

        :Args:
          - uid: UID for the item

        :Returns:
          Returns item object. Returns None if nothing was found.
        """
        for item in self.get_items():
            if item.id == uid:
                return item

        return None

    def get_item_with_href(self, href):
        """
        Returns item for defined HREF.

        >>> book.get_item_with_href('EPUB/document.xhtml')

        :Args:
          - href: HREF for the item we are searching for

        :Returns:
          Returns item object. Returns None if nothing was found.
        """
        for item in self.get_items():
            if item.get_name() == href:
                return item

        return None

    def get_items(self):
        """
        Returns all items attached to this book.

        :Returns:
          Returns all items as tuple.
        """
        return (item for item in self.items)

    def get_items_of_type(self, item_type):
        """
        Returns all items of specified type.

        >>> book.get_items_of_type(epub.ITEM_IMAGE)

        :Args:
          - item_type: Type for items we are searching for

        :Returns:
          Returns found items as tuple.
        """
        return (item for item in self.items if item.get_type() == item_type)

    def get_items_of_media_type(self, media_type):
        """
        Returns all items of specified media type.

        :Args:
          - media_type: Media type for items we are searching for

        :Returns:
          Returns found items as tuple.
        """
        return (item for item in self.items if item.media_type == media_type)

    def set_template(self, name, value):
        """
        Defines templates which are used to generate certain types of pages. When defining new value for the template
        we have to use content of type 'str' (Python 2) or 'bytes' (Python 3).

        At the moment we use these templates:
          - ncx
          - nav
          - chapter
          - cover

        :Args:
          - name: Name for the template
          - value: Content for the template
        """

        self.templates[name] = value

    def get_template(self, name):
        """
        Returns value for the template.

        :Args:
          - name: template name

        :Returns:
          Value of the template.
        """
        return self.templates.get(name)

    def add_prefix(self, name, uri):
        """
        Appends custom prefix to be added to the content.opf document

        >>> epub_book.add_prefix('bkterms', 'http://booktype.org/')

        :Args:
          - name: namespave name
          - uri: URI for the namespace
        """

        self.prefixes.append("%s: %s" % (name, uri))


class EpubWriter(object):
    DEFAULT_OPTIONS = {
        "epub2_guide": True,
        "epub3_landmark": True,
        "epub3_pages": True,
        "landmark_title": "Guide",
        "pages_title": "Pages",
        "spine_direction": True,
        "package_direction": False,
        "play_order": {"enabled": False, "start_from": 1},
    }

    def __init__(self, name, book, options=None):
        self.file_name = name
        self.book = book

        self.options = dict(self.DEFAULT_OPTIONS)
        if options:
            self.options.update(options)

        self._init_play_order()

    def _init_play_order(self):
        self._play_order = {"enabled": False, "start_from": 1}

        try:
            self._play_order["enabled"] = self.options["play_order"]["enabled"]
            self._play_order["start_from"] = self.options["play_order"]["start_from"]
        except KeyError:
            pass

    def process(self):
        # should cache this html parsing so we don't do it for every plugin
        for plg in self.options.get("plugins", []):
            if hasattr(plg, "before_write"):
                plg.before_write(self.book)

        for item in self.book.get_items():
            if isinstance(item, EpubHtml):
                for plg in self.options.get("plugins", []):
                    if hasattr(plg, "html_before_write"):
                        plg.html_before_write(self.book, item)

    def _write_container(self):
        container_xml = CONTAINER_XML % {"folder_name": self.book.FOLDER_NAME}
        self.out.writestr(CONTAINER_PATH, container_xml)

    def _write_opf_metadata(self, root):
        # This is really not needed
        # problem is uppercase/lowercase
        # for ns_name, values in six.iteritems(self.book.metadata):
        #     if ns_name:
        #         for n_id, ns_url in six.iteritems(NAMESPACES):
        #             if ns_name == ns_url:
        #                 nsmap[n_id.lower()] = NAMESPACES[n_id]

        nsmap = {"dc": NAMESPACES["DC"], "opf": NAMESPACES["OPF"]}
        nsmap.update(self.book.namespaces)

        metadata = etree.SubElement(root, "metadata", nsmap=nsmap)

        el = etree.SubElement(metadata, "meta", {"property": "dcterms:modified"})
        if "mtime" in self.options:
            mtime = self.options["mtime"]
        else:
            import datetime

            mtime = datetime.datetime.now()
        el.text = mtime.strftime("%Y-%m-%dT%H:%M:%SZ")

        for ns_name, values in six.iteritems(self.book.metadata):
            if ns_name == NAMESPACES["OPF"]:
                for values in values.values():
                    for v in values:
                        if (
                            "property" in v[1]
                            and v[1]["property"] == "dcterms:modified"
                        ):
                            continue
                        try:
                            el = etree.SubElement(metadata, "meta", v[1])
                            if v[0]:
                                el.text = v[0]
                        except ValueError:
                            logging.error("Could not create metadata.")
            else:
                for name, values in six.iteritems(values):
                    for v in values:
                        try:
                            if ns_name:
                                el = etree.SubElement(
                                    metadata, "{%s}%s" % (ns_name, name), v[1]
                                )
                            else:
                                el = etree.SubElement(metadata, "%s" % name, v[1])

                            el.text = v[0]
                        except ValueError:
                            logging.error(
                                'Could not create metadata "{}".'.format(name)
                            )

    def _write_opf_manifest(self, root):
        manifest = etree.SubElement(root, "manifest")
        _ncx_id = None

        # mathml, scripted, svg, remote-resources, and switch
        # nav
        # cover-image

        for item in self.book.get_items():
            if not item.manifest:
                continue

            if isinstance(item, EpubNav):
                etree.SubElement(
                    manifest,
                    "item",
                    {
                        "href": item.get_name(),
                        "id": item.id,
                        "media-type": item.media_type,
                        "properties": "nav",
                    },
                )
            elif isinstance(item, EpubNcx):
                _ncx_id = item.id
                etree.SubElement(
                    manifest,
                    "item",
                    {
                        "href": item.file_name,
                        "id": item.id,
                        "media-type": item.media_type,
                    },
                )

            elif isinstance(item, EpubCover):
                etree.SubElement(
                    manifest,
                    "item",
                    {
                        "href": item.file_name,
                        "id": item.id,
                        "media-type": item.media_type,
                        "properties": "cover-image",
                    },
                )
            else:
                opts = {
                    "href": item.file_name,
                    "id": item.id,
                    "media-type": item.media_type,
                }

                if hasattr(item, "properties") and len(item.properties) > 0:
                    opts["properties"] = " ".join(item.properties)

                if hasattr(item, "media_overlay") and item.media_overlay is not None:
                    opts["media-overlay"] = item.media_overlay

                if hasattr(item, "media_duration") and item.media_duration is not None:
                    opts["duration"] = item.media_duration

                etree.SubElement(manifest, "item", opts)

        return _ncx_id

    def _write_opf_spine(self, root, ncx_id):
        spine_attributes = {"toc": ncx_id or "ncx"}
        if self.book.direction and self.options["spine_direction"]:
            spine_attributes["page-progression-direction"] = self.book.direction

        spine = etree.SubElement(root, "spine", spine_attributes)

        for _item in self.book.spine:
            # this is for now
            # later we should be able to fetch things from tuple

            is_linear = True

            if isinstance(_item, tuple):
                item = _item[0]

                if len(_item) > 1:
                    if _item[1] == "no":
                        is_linear = False
            else:
                item = _item

            if isinstance(item, EpubHtml):
                opts = {"idref": item.get_id()}

                if not item.is_linear or not is_linear:
                    opts["linear"] = "no"
            elif isinstance(item, EpubItem):
                opts = {"idref": item.get_id()}

                if not item.is_linear or not is_linear:
                    opts["linear"] = "no"
            else:
                opts = {"idref": item}

                try:
                    itm = self.book.get_item_with_id(item)

                    if not itm.is_linear or not is_linear:
                        opts["linear"] = "no"
                except Exception:
                    pass

            etree.SubElement(spine, "itemref", opts)


class EpubReader(object):
    DEFAULT_OPTIONS = {"ignore_ncx": False}

    def __init__(self, epub_file_name, options=None):
        self.file_name = epub_file_name
        self.book = EpubBook()
        self.zf = None

        self.opf_file = ""
        self.opf_dir = ""

        self.options = dict(self.DEFAULT_OPTIONS)
        if options:
            self.options.update(options)

        self._check_deprecated()

    def _check_deprecated(self):
        if not self.options.get("ignore_ncx"):
            warnings.warn(
                "In the future version we will turn default option ignore_ncx to True."
            )

    def process(self):
        # should cache this html parsing so we don't do it for every plugin
        for plg in self.options.get("plugins", []):
            if hasattr(plg, "after_read"):
                plg.after_read(self.book)

        for item in self.book.get_items():
            if isinstance(item, EpubHtml):
                for plg in self.options.get("plugins", []):
                    if hasattr(plg, "html_after_read"):
                        plg.html_after_read(self.book, item)

    def load(self):
        self._load()

        return self.book

    def read_file(self, name):
        # Raises KeyError
        name = zip_path.normpath(name)
        content = self.zf.read(name)
        return content

    def _load_container(self):
        meta_inf = self.read_file("META-INF/container.xml")
        tree = parse_string(meta_inf)

        for root_file in tree.findall(
            "//xmlns:rootfile[@media-type]",
            namespaces={"xmlns": NAMESPACES["CONTAINERNS"]},
        ):
            if root_file.get("media-type") == "application/oebps-package+xml":
                self.opf_file = root_file.get("full-path")
                self.opf_dir = zip_path.dirname(self.opf_file)

    def _load_metadata(self):
        container_root = self.container.getroot()

        # get epub version
        self.book.version = container_root.get("version", None)

        # get unique-identifier
        if container_root.get("unique-identifier", None):
            self.book.IDENTIFIER_ID = container_root.get("unique-identifier")

        # get xml:lang
        # get metadata
        metadata = self.container.find("{%s}%s" % (NAMESPACES["OPF"], "metadata"))

        if metadata:
            nsmap = metadata.nsmap
            nstags = dict((k, "{%s}" % v) for k, v in six.iteritems(nsmap))
            default_ns = nstags.get(None, "")
            nsdict = dict((v, {}) for v in nsmap.values())

            def add_item(ns, tag, value, extra):
                if ns not in nsdict:
                    nsdict[ns] = {}

                values = nsdict[ns].setdefault(tag, [])
                values.append((value, extra))

            for t in metadata:
                if not etree.iselement(t) or t.tag is etree.Comment:
                    continue
                if t.tag == default_ns + "meta":
                    name = t.get("name")
                    others = dict((k, v) for k, v in t.items())

                    if name and ":" in name:
                        prefix, name = name.split(":", 1)
                    else:
                        prefix = None

                    add_item(t.nsmap.get(prefix, prefix), name, t.text, others)
                else:
                    tag = t.tag[t.tag.rfind("}") + 1 :]

                    if (t.prefix and t.prefix.lower() == "dc") and tag == "identifier":
                        _id = t.get("id", None)

                        if _id:
                            self.book.IDENTIFIER_ID = _id

                    others = dict((k, v) for k, v in t.items())
                    add_item(t.nsmap[t.prefix], tag, t.text, others)

            self.book.metadata = nsdict

            titles = self.book.get_metadata("DC", "title")
            if len(titles) > 0:
                self.book.title = titles[0][0]

            for value, others in self.book.get_metadata("DC", "identifier"):
                if others.get("id") == self.book.IDENTIFIER_ID:
                    self.book.uid = value

    def _load_manifest(self):
        for r in self.container.find("{%s}%s" % (NAMESPACES["OPF"], "manifest")):
            if r is not None and r.tag != "{%s}item" % NAMESPACES["OPF"]:
                continue

            media_type = r.get("media-type")
            _properties = r.get("properties", "")

            if _properties:
                properties = _properties.split(" ")
            else:
                properties = []

            # people use wrong content types
            if media_type == "image/jpg":
                media_type = "image/jpeg"

            if media_type == "application/x-dtbncx+xml":
                ei = EpubNcx(uid=r.get("id"), file_name=unquote(r.get("href")))

                ei.content = self.read_file(zip_path.join(self.opf_dir, ei.file_name))
            elif media_type == "application/smil+xml":
                ei = EpubSMIL(uid=r.get("id"), file_name=unquote(r.get("href")))

                ei.content = self.read_file(zip_path.join(self.opf_dir, ei.file_name))
            elif media_type == "application/xhtml+xml":
                if "nav" in properties:
                    ei = EpubNav(uid=r.get("id"), file_name=unquote(r.get("href")))

                    ei.content = self.read_file(
                        zip_path.join(self.opf_dir, r.get("href"))
                    )
                elif "cover" in properties:
                    ei = EpubCoverHtml()

                    ei.content = self.read_file(
                        zip_path.join(self.opf_dir, unquote(r.get("href")))
                    )
                else:
                    ei = EpubHtml()

                    ei.id = r.get("id")
                    ei.file_name = unquote(r.get("href"))
                    ei.media_type = media_type
                    ei.media_overlay = r.get("media-overlay", None)
                    ei.media_duration = r.get("duration", None)
                    ei.content = self.read_file(
                        zip_path.join(self.opf_dir, ei.get_name())
                    )
                    ei.properties = properties
            elif media_type in IMAGE_MEDIA_TYPES:
                if "cover-image" in properties:
                    ei = EpubCover(uid=r.get("id"), file_name=unquote(r.get("href")))

                    ei.media_type = media_type
                    ei.content = self.read_file(
                        zip_path.join(self.opf_dir, ei.get_name())
                    )
                else:
                    ei = EpubImage()

                    ei.id = r.get("id")
                    ei.file_name = unquote(r.get("href"))
                    ei.media_type = media_type
                    ei.content = self.read_file(
                        zip_path.join(self.opf_dir, ei.get_name())
                    )
            else:
                # different types
                ei = EpubItem()

                ei.id = r.get("id")
                ei.file_name = unquote(r.get("href"))
                ei.media_type = media_type

                ei.content = self.read_file(zip_path.join(self.opf_dir, ei.get_name()))

            self.book.add_item(ei)

    def _parse_ncx(self, data):
        tree = parse_string(data)
        tree_root = tree.getroot()

        nav_map = tree_root.find("{%s}navMap" % NAMESPACES["DAISY"])

        def _get_children(elems, n, nid):
            label, content = "", ""
            children = []

            for a in elems.getchildren():
                if a.tag == "{%s}navLabel" % NAMESPACES["DAISY"]:
                    label = a.getchildren()[0].text
                if a.tag == "{%s}content" % NAMESPACES["DAISY"]:
                    content = a.get("src", "")
                if a.tag == "{%s}navPoint" % NAMESPACES["DAISY"]:
                    children.append(_get_children(a, n + 1, a.get("id", "")))

            if len(children) > 0:
                if n == 0:
                    return children

                return (Section(label, href=content), children)
            else:
                return Link(content, label, nid)

        self.book.toc = _get_children(nav_map, 0, "")

    def _parse_nav(self, data, base_path, navtype="toc"):
        html_node = parse_html_string(data)
        nav_node = None
        if navtype == "toc":
            # parsing the table of contents
            if nodes := html_node.xpath("//nav[@*='toc']"):
                nav_node = nodes[0]
        else:
            # parsing the list of pages
            _page_list = html_node.xpath("//nav[@*='page-list']")
            if len(_page_list) == 0:
                return
            nav_node = _page_list[0]

        def parse_list(list_node):
            items = []

            for item_node in list_node.findall("li"):
                sublist_node = item_node.find("ol")
                link_node = item_node.find("a")

                if sublist_node is not None:
                    title = item_node[0].text
                    children = parse_list(sublist_node)

                    if link_node is not None:
                        href = zip_path.normpath(
                            zip_path.join(base_path, link_node.get("href"))
                        )
                        items.append((Section(title, href=href), children))
                    else:
                        items.append((Section(title), children))
                elif link_node is not None:
                    title = link_node.text
                    href = zip_path.normpath(
                        zip_path.join(base_path, link_node.get("href"))
                    )

                    items.append(Link(href, title))

            return items

        if navtype == "toc" and nav_node:
            self.book.toc = parse_list(nav_node.find("ol"))
        elif nav_node is not None:
            # generate the pages list if there is one
            self.book.pages = parse_list(nav_node.find("ol"))

            # generate the per-file pages lists
            # because of the order of parsing the files, this can't be done
            # when building the EpubHtml objects
            htmlfiles = dict()
            for htmlfile in self.book.items:
                if isinstance(htmlfile, EpubHtml):
                    htmlfiles[htmlfile.file_name] = htmlfile
            for page in self.book.pages:
                try:
                    (filename, idref) = page.href.split("#")
                except ValueError:
                    filename = page.href
                if filename in htmlfiles:
                    htmlfiles[filename].pages.append(page)

    def _load_spine(self):
        spine = self.container.find("{%s}%s" % (NAMESPACES["OPF"], "spine"))

        self.book.spine = [(t.get("idref"), t.get("linear", "yes")) for t in spine]

        toc = spine.get("toc", "")
        self.book.set_direction(spine.get("page-progression-direction", None))

        # should read ncx or nav file
        nav_item = next(
            (item for item in self.book.items if isinstance(item, EpubNav)), None
        )
        if toc:
            if not self.options.get("ignore_ncx") or not nav_item:
                try:
                    ncxFile = self.read_file(
                        zip_path.join(
                            self.opf_dir, self.book.get_item_with_id(toc).get_name()
                        )
                    )
                except KeyError:
                    raise EpubException(-1, "Can not find ncx file.")

                self._parse_ncx(ncxFile)

    def _load_guide(self):
        guide = self.container.find("{%s}%s" % (NAMESPACES["OPF"], "guide"))
        if guide is not None:
            self.book.guide = [
                {"href": t.get("href"), "title": t.get("title"), "type": t.get("type")}
                for t in guide
            ]

    def _load_opf_file(self):
        try:
            s = self.read_file(self.opf_file)
        except KeyError:
            raise EpubException(-1, "Can not find container file")

        self.container = parse_string(s)

        self._load_metadata()
        self._load_manifest()
        self._load_spine()
        self._load_guide()

        # read nav file if found
        #
        nav_item = next(
            (item for item in self.book.items if isinstance(item, EpubNav)), None
        )
        if nav_item:
            if self.options.get("ignore_ncx") or not self.book.toc:
                self._parse_nav(
                    nav_item.content,
                    zip_path.dirname(nav_item.file_name),
                    navtype="toc",
                )
            self._parse_nav(
                nav_item.content, zip_path.dirname(nav_item.file_name), navtype="pages"
            )

    def _load(self):
        if os.path.isdir(self.file_name):
            file_name = self.file_name

            class Directory:
                def read(self, subname):
                    with open(os.path.join(file_name, subname), "rb") as fp:
                        return fp.read()

                def close(self):
                    pass

            self.zf = Directory()
        else:
            try:
                self.zf = zipfile.ZipFile(
                    self.file_name,
                    "r",
                    compression=zipfile.ZIP_DEFLATED,
                    allowZip64=True,
                )
            except zipfile.BadZipfile:
                raise EpubException(0, "Bad Zip file")
            except zipfile.LargeZipFile:
                raise EpubException(1, "Large Zip file")

        # 1st check metadata
        self._load_container()
        self._load_opf_file()

        self.zf.close()


# WRITE


def write_epub(name, book, options=None):
    """
    Creates epub file with the content defined in EpubBook.

    >>> ebooklib.write_epub('book.epub', book)

    :Args:
      - name: file name for the output file
      - book: instance of EpubBook
      - options: extra opions as dictionary (optional)
    """
    epub = EpubWriter(name, book, options)

    epub.process()

    try:
        epub.write()
    except IOError:
        pass


# READ


def read_epub(name, options=None):
    """
    Creates new instance of EpubBook with the content defined in the input file.

    >>> book = ebooklib.read_epub('book.epub')

    :Args:
      - name: full path to the input file
      - options: extra options as dictionary (optional)

    :Returns:
      Instance of EpubBook.
    """
    reader = EpubReader(name, options)

    book = reader.load()
    reader.process()

    return book


class EpubParser:
    def __init__(
        self,
        banned_sections: set[str] = BANNED_SECTIONS,
        banned_section_prefixes: set[str] = BANNED_SECTION_PREFIXES,
        remove_notes: bool = True,
    ):
        _joined = "|".join(banned_section_prefixes)
        self._banned_section_prefixes_regexp = re.compile(
            rf"^({_joined})",
            flags=re.IGNORECASE,
        )
        if banned_sections is None:
            self.banned_sections = set()
        else:
            self.banned_sections = set(banned_sections)
        self._remove_notes = remove_notes
        if self._remove_notes:
            self.banned_sections.add("notes")

    def parse_soup(self, soup: BeautifulSoup):
        for _ in list(
            soup.select("body > .copyright-mtp, body > .halftitle, body > .book-title")
        ):
            return

        body = soup.find("body")

        if not body:
            return

        for section in list(body.find_all("section")):
            if self._remove_notes and section.attrs.get("epub:type") == "note":
                section.extract()
                break
            for child in section.children:
                child_text = child.text.lower().strip(" :,.;")
                if child.name in {
                    "header",
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "div",
                } and (
                    child_text in self.banned_sections
                    or self._banned_section_prefixes_regexp.match(child_text)
                ):
                    section.extract()
                    break

        for summary in list(body.select("details > summary.section-heading")):
            summary_text = summary.text.lower().strip(" :,.;")
            if (
                summary_text in self.banned_sections
                or self._banned_section_prefixes_regexp.match(summary_text)
            ):
                summary.parent.extract()

        for header in list(body.select("body h1")):
            header_text = header.text.lower().strip(" :,.;")
            if (
                header_text in self.banned_sections
                or self._banned_section_prefixes_regexp.match(header_text)
            ):
                header.parent.extract()

        for b_tag in list(body.select("b, i")):
            b_tag.unwrap()

        for p_tag in list(body.find_all("p")):
            sibling = p_tag.next_sibling
            while sibling == "\n":
                sibling = sibling.next_sibling
            if sibling and sibling.name == "blockquote":
                new_p_tag = soup.new_tag("p")
                new_p_tag.extend([p_tag.text, " ", sibling.text])
                p_tag.replace_with(new_p_tag)
                sibling.extract()

        for el in list(body.select(".Equation img")):
            if alt := el.attrs.get("alt"):
                wrapping_tag = soup.new_tag("div")
                new_tag = soup.new_tag("math")
                new_tag.string = alt.strip().replace("\n", " ")
                wrapping_tag.append(new_tag)
                el.replace_with(wrapping_tag)

        for el in list(body.select(".InlineEquation img")):
            if alt := el.attrs.get("alt"):
                wrapping_tag = soup.new_tag("span")
                new_tag = soup.new_tag("math")
                new_tag.string = alt.strip().replace("\n", " ")
                wrapping_tag.append(new_tag)
                el.replace_with(wrapping_tag)

        for el in list(body.select(".ListItem > .ItemContent")):
            for c in el.parent.children:
                if isinstance(c, NavigableString):
                    c.extract()

        for el in list(
            body.select(
                'table, nav, ref, formula, figure, img, [role="note"], .Affiliations, '
                ".ArticleOrChapterToc, .FM-head, .EM-copyright-text, .EM-copyright-text-space, "
                ".AuthorGroup, .ChapterContextInformation, "
                ".Contacts, .CoverFigure, .Bibliography, "
                ".BookTitlePage, .BookFrontmatter, .CopyrightPage, "
                ".FootnoteSection, .reference, .side-box-text, .thumbcaption, .ItemNumber"
            )
        ):
            el.extract()

        for el in list(body.select("a, span")):
            el.unwrap()

        text = md.convert_soup(canonize_tags(body)).strip()
        return text

    def extract_epub(self, content: bytes):
        with tempfile.NamedTemporaryFile(mode="w+b", delete=False) as t_file:
            t_file.write(content)
            file_name = t_file.name
            book = read_epub(file_name)
            items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
            texts = []
            for item in items:
                if _ := (
                    re.search(
                        "(chapter|part|notes|section)",
                        item.get_name(),
                        flags=re.IGNORECASE,
                    )
                    or re.search(
                        r"^(?!.*(photographs?|contributors|acknowledgements|content|list_figure|cover|title_page|"
                        r"title|titlePage|copyright|backmatter|dedication|epigraph|image|frontsales|adcard|insertedcopyright|toc|"
                        r"index|credits|bibliography|footnote|navdoc|frontmatter|reference|series|nav|copy|ack\.)).*$",
                        item.get_name(),
                        flags=re.IGNORECASE,
                    )
                ):
                    soup = item.get_body_content()
                    if text := self.parse_soup(soup):
                        text = re.sub("\n([a-z])", r" \g<1>", text)
                        text = text.replace("![]()", "")
                        text = re.sub(
                            r"\n\s*\n\s*$",
                            "\n\n",
                            text,
                            flags=re.DOTALL | re.MULTILINE | re.UNICODE,
                        )
                        texts.append(text)

            return "\n\n".join(texts).strip()
