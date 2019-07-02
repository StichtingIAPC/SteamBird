from django.urls.resolvers import get_resolver, URLPattern, URLResolver
from docutils import nodes
from sphinx.util.docutils import SphinxDirective


class DjangoUrlsNode(nodes.Admonition, nodes.Element):
    tagname = 'django-urls'


class DjangoUrlsDirective(SphinxDirective):

    def run(self):
        url_resolver = get_resolver()

        all_urls = []

        def populate_level(urls, parents=None, namespace=None):
            if parents is None:
                parents = []

            for url in urls.url_patterns:
                if isinstance(url, URLResolver):
                    populate_level(url, parents + [url.pattern], namespace=(url.namespace or namespace))
                elif isinstance(url, URLPattern):
                    path = ' '.join(map(str, parents + [url.pattern]))
                    cls = None
                    if hasattr(url.callback, 'view_class'):
                        cls = url.callback.view_class.__module__ + "." + url.callback.view_class.__name__
                    # pending_xref()
                    all_urls.append([
                        nodes.Text(path),
                        nodes.Text(namespace or '-'),
                        nodes.Text(str(url.name)),
                        nodes.Text(cls),
                    ])

        populate_level(url_resolver)

        all_urls = filter(lambda url: url[1] in ["teacher", "boecie"] or url[0] == "", all_urls)

        return [self.build_table_from_list(all_urls, ['Pattern', 'Namespace', 'Name', 'Class'])]

    @staticmethod
    def build_table_from_list(data, headers=None):
        col_widths = [100 // len(headers)] * len(headers)
        table = nodes.table()
        tgroup = nodes.tgroup(cols=len(col_widths))
        table += tgroup
        for col_width in col_widths:
            colspec = nodes.colspec(colwidth=col_width)
            tgroup += colspec

        if headers:
            head_row = nodes.row()
            for cell in headers:
                entry = nodes.entry()
                entry += nodes.Text(cell)
                head_row += entry
            thead = nodes.thead()
            thead.append(head_row)
            tgroup.append(thead)

        rows = []
        for row in data:
            row_node = nodes.row()
            for cell in row:
                entry = nodes.entry()
                entry += nodes.Text(cell)
                row_node += entry
            rows.append(row_node)
        tbody = nodes.tbody()
        tbody.extend(rows)
        tgroup.append(tbody)

        return table


def setup(app):
    # app.add_node(DjangoUrlsNode)

    app.add_directive('django-urls', DjangoUrlsDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
