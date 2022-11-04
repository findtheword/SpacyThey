import re

html_tags_regexp = re.compile('<.*?>')


def html_replaced_with_spaces(html):
    def space_replacer(match):
        return '.' * len(match.group(0))

    return re.sub(html_tags_regexp, space_replacer, html)
