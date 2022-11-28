import re
from collections import namedtuple

html_tags_regexp = re.compile('<.*?>')


def html_replaced_with_spaces(html):
    def space_replacer(match):
        return '.' * len(match.group(0))

    html_replaced = re.sub(html_tags_regexp, space_replacer, html)

    new_lines_replaces = ' '.join(html_replaced.splitlines())

    return new_lines_replaces


CorrectOrderTuple = namedtuple('CorrectOrderTuple', ['i', 'old', 'new'])

class WordUpdater:
    updates = []
    update_params = {}

    def __init__(self, update_params) -> None:
        self.update_params = update_params
        super().__init__()

    def add(self, token, to):
        info = CorrectOrderTuple(token.idx, token.text, to)
        self.updates.append(info)

    def do_update(self, info: CorrectOrderTuple, html: str):

        to = info.new
        old = info.old

        if info.old[0].isupper():
            to = to[0].upper() + to[1:]

        if self.update_params.get('span', False):
            to = f"<span title='original: { old }' style='color: purple;'>{ to }</span>"

        return html[0: info.i] + to + html[info.i + len(old):]

    def update(self, html: str):
        self.updates.sort(key=lambda x: x.i)
        while self.updates:
            el = self.updates.pop()
            html = self.do_update(el, html)
        return html