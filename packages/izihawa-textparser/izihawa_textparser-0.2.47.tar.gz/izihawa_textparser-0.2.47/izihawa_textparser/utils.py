import re

import markdownify
import six


class MarkdownConverter(markdownify.MarkdownConverter):
    convert_b = markdownify.abstract_inline_conversion(lambda self: "**")
    convert_i = markdownify.abstract_inline_conversion(lambda self: "__")
    convert_em = markdownify.abstract_inline_conversion(lambda self: "__")

    def process_tag(self, node, parent_tags=None):
        # For the top-level element, initialize the parent context with an empty set.
        if parent_tags is None:
            parent_tags = set()

        # Collect child elements to process, ignoring whitespace-only text elements
        # adjacent to the inner/outer boundaries of block elements.
        should_remove_inside = markdownify.should_remove_whitespace_inside(node)

        def _can_ignore(el):
            if isinstance(el, markdownify.Tag):
                # Tags are always processed.
                return False
            elif isinstance(el, (markdownify.Comment, markdownify.Doctype)):
                # Comment and Doctype elements are always ignored.
                # (subclasses of NavigableString, must test first)
                return True
            elif isinstance(el, markdownify.NavigableString):
                if six.text_type(el).strip() != '':
                    # Non-whitespace text nodes are always processed.
                    return False
                elif should_remove_inside and (not el.previous_sibling or not el.next_sibling):
                    # Inside block elements (excluding <pre>), ignore adjacent whitespace elements.
                    return True
                elif markdownify.should_remove_whitespace_outside(el.previous_sibling) or markdownify.should_remove_whitespace_outside(el.next_sibling):
                    # Outside block elements (including <pre>), ignore adjacent whitespace elements.
                    return True
                else:
                    return False
            elif el is None:
                return True
            else:
                raise ValueError('Unexpected element type: %s' % type(el))

        children_to_convert = [el for el in node.children if not _can_ignore(el)]

        # Create a copy of this tag's parent context, then update it to include this tag
        # to propagate down into the children.
        parent_tags_for_children = set(parent_tags)
        parent_tags_for_children.add(node.name)

        # if this tag is a heading or table cell, add an '_inline' parent pseudo-tag
        if (
            markdownify.html_heading_re.match(node.name) is not None  # headings
            or node.name in {'td', 'th'}  # table cells
        ):
            parent_tags_for_children.add('_inline')

        # if this tag is a preformatted element, add a '_noformat' parent pseudo-tag
        if node.name in {'pre', 'code', 'kbd', 'samp', 'math'}:
            parent_tags_for_children.add('_noformat')

        # Convert the children elements into a list of result strings.
        child_strings = [
            self.process_element(el, parent_tags=parent_tags_for_children)
            for el in children_to_convert
        ]

        # Remove empty string values.
        child_strings = [s for s in child_strings if s]

        # Collapse newlines at child element boundaries, if needed.
        if node.name == 'pre' or node.find_parent('pre'):
            # Inside <pre> blocks, do not collapse newlines.
            pass
        else:
            # Collapse newlines at child element boundaries.
            updated_child_strings = ['']  # so the first lookback works
            for child_string in child_strings:
                # Separate the leading/trailing newlines from the content.
                leading_nl, content, trailing_nl = markdownify.extract_newlines_re.match(child_string).groups()

                # If the last child had trailing newlines and this child has leading newlines,
                # use the larger newline count, limited to 2.
                if updated_child_strings[-1] and leading_nl:
                    prev_trailing_nl = updated_child_strings.pop()  # will be replaced by the collapsed value
                    num_newlines = min(2, max(len(prev_trailing_nl), len(leading_nl)))
                    leading_nl = '\n' * num_newlines

                # Add the results to the updated child string list.
                updated_child_strings.extend([leading_nl, content, trailing_nl])

            child_strings = updated_child_strings

        # Join all child text strings into a single string.
        text = ''.join(child_strings)

        # apply this tag's final conversion function
        convert_fn_name = "convert_%s" % re.sub(r"[\[\]:-]", "_", node.name)
        convert_fn = getattr(self, convert_fn_name, None)
        if convert_fn and self.should_convert_tag(node.name):
            text = convert_fn(node, text, parent_tags=parent_tags)

        return text

    def process_text(self, el, parent_tags):
        if parent_tags is None:
            parent_tags = set()

        text = six.text_type(el) or ""

        # dont remove any whitespace when handling pre or code in pre
        if not (
            el.parent.name == "pre"
            or el.parent.name == "math"
            or (el.parent.name == "code" and el.parent.parent.name == "pre")
        ):
            text = markdownify.whitespace_re.sub(" ", text)

        if '_noformat' not in parent_tags:
            text = self.escape(text)

        # remove trailing whitespaces if any of the following condition is true:
        # - current text node is the last node in li
        # - current text node is followed by an embedded list
        if el.parent.name == "li" and (
            not el.next_sibling or el.next_sibling.name in ["ul", "ol"]
        ):
            text = text.rstrip()

        return text

    def convert_header(self, el, text, parent_tags):
        return self.convert_hn(2, el, text, parent_tags)

    def convert_math(self, el, text, parent_tags):
        return text

    def convert_title(self, el, text, parent_tags):
        return self.convert_hn(2, el, text, parent_tags)

    def convert_soup(self, soup):
        r = super().convert_soup(soup)
        return re.sub(r"\n{2,}", "\n\n", r).replace("\r\n", "").strip()

    def convert_td(self, el, text, parent_tags):
        return " " + text.strip().replace("\n", "  ") + " |"

    def convert_th(self, el, text, parent_tags):
        return super().convert_th(
            el, text.strip().replace("\n", "  "), parent_tags
        )

    def convert_li(self, el, text, parent_tags):
        parent = el.parent
        is_inside_table = False
        grand_parent = parent

        while grand_parent is not None:
            if grand_parent.name in ("tr", "th", "tbody", "table", "td"):
                is_inside_table = True
                break
            grand_parent = grand_parent.parent

        if parent is not None and parent.name == "ol":
            if parent.get("start"):
                start = int(parent.get("start"))
            else:
                start = 1
            bullet = "%s." % (start + parent.index(el))
        else:
            depth = -1
            while el:
                if el.name == "ul":
                    depth += 1
                el = el.parent
            bullets = self.options["bullets"]
            bullet = bullets[depth % len(bullets)]

        text = (text or "").strip()
        if is_inside_table:
            text = text.replace("\n", " ")
        return "%s %s\n" % (bullet, text)

    def convert_tr(self, el, text, parent_tags):
        cells = el.find_all(["td", "th"])
        is_headrow = (
            all([cell.name == "th" for cell in cells])
            or (not el.previous_sibling and el.parent.name != "tbody")
            or (
                not el.previous_sibling
                and el.parent.name == "tbody"
                and len(el.parent.parent.find_all(["thead"])) < 1
            )
        )
        overline = ""
        underline = ""
        if is_headrow and not el.previous_sibling:
            # first row and is headline: print headline underline
            underline += "| " + " | ".join(["---"] * len(cells)) + " |" + "\n"
        elif not el.previous_sibling and (
            el.parent.name == "table"
            or (el.parent.name == "tbody" and not el.parent.previous_sibling)
        ):
            # first row, not headline, and:
            # - the parent is table or
            # - the parent is tbody at the beginning of a table.
            # print empty headline above this row
            overline += "| " + " | ".join([""] * len(cells)) + " |" + "\n"
            overline += "| " + " | ".join(["---"] * len(cells)) + " |" + "\n"
        return overline + "|" + text.strip().replace("\n", "  ") + "\n" + underline

    def convert_blockquote(self, el, text, parent_tags):
        if '_inline' in parent_tags:
            return text

        return (
            "\n" + (markdownify.line_beginning_re.sub("> ", text.strip()) + "\n\n")
            if text
            else ""
        )

    def convert_hn(self, n, el, text, parent_tags):
        if '_inline' in parent_tags:
            return text

        style = self.options["heading_style"].lower()
        text = text.replace("\n", " ")
        text = re.sub(r"\s{2,}", " ", text)
        if style == markdownify.UNDERLINED and n <= 2:
            line = "=" if n == 1 else "-"
            return self.underline(text, line)
        hashes = "#" * n
        if style == markdownify.ATX_CLOSED:
            return "%s %s %s\n\n" % (hashes, text, hashes)
        return "\n%s %s\n\n" % (hashes, text)


md = MarkdownConverter(
    sub_symbol="~",
    sup_symbol="^",
    heading_style=markdownify.ATX,
    autolinks=False,
)
