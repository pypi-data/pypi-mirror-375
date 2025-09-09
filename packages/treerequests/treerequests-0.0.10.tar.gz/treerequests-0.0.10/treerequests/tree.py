def bs4(text, url, obj=None, **kwargs):
    func = None
    if obj is None:
        from bs4 import BeautifulSoup

        func = BeautifulSoup
    else:
        func = obj

    k = {"markup": text, "features": "html.parser"}
    k.update(kwargs)

    return func(**k)


def html5_parser(text, url, obj=None, **kwargs):
    func = None
    if obj is None:
        from html5_parser import parse

        func = parse
    else:
        func = obj

    return func(text, **kwargs)


def modest(text, url, obj=None, **kwargs):
    func = None
    if obj is None:
        from selectolax.parser import HTMLParser

        func = HTMLParser
    else:
        func = obj

    return func(text, **kwargs)


def lexbor(text, url, obj=None, **kwargs):
    func = None
    if obj is None:
        from selectolax.parser import LexborHTMLParser

        func = LexborHTMLParser
    else:
        func = obj

    return func(text, **kwargs)


def lxml(text, url, obj=None, **kwargs):
    func = None
    if obj is None:
        from lxml.html import fromstring

        func = fromstring
    else:
        func = obj

    k = {"base_url": url}
    k.update(kwargs)

    return func(text, **k)


def reliq(text, url, obj=None, **kwargs):
    func = None
    if obj is None:
        from reliq import reliq as reliq_tree

        func = reliq_tree
    else:
        func = obj

    k = {"html": text, "ref": url}
    k.update(kwargs)

    return func(**k)
