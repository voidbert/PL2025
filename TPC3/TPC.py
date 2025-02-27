#!/usr/bin/env python3

import itertools
import re
import sys

def md_highlights_to_html(md: str) -> str:
    md = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', md, flags=re.DOTALL)
    md = re.sub(r'\*(.*?)\*', r'<i>\1</i>', md, flags=re.DOTALL)
    return md

def md_to_html(md: str) -> str:
    def replace_header(match) -> str:
        length = len(match.group(1))
        content = match.group(2)
        return f'<h{length}>{content}</h{length}>'

    md = re.sub(r'^(#{1,6}) (.*)', replace_header, md, flags=re.MULTILINE)

    def replace_list(match) -> str:
        numbers = [int(s) for s in re.findall(r'^\d+', match.group(0), flags=re.MULTILINE)]
        deltas = [ (b - a) == 1 for a, b in zip(numbers, numbers[1:]) ]
        if numbers[0] != 1 or not all(deltas):
            return match.group(0)

        html = re.sub(r'^\d+\. (.*)', r'<li>\1</li>', match.group(0), flags=re.MULTILINE)
        return f'{match.group(1)}<ol>{html}\n</ol>'

    md = re.sub(r'(?:(^|\n)\d+\. .*)+', replace_list, md)

    md_parts = re.split(r'(!?)\[(.*)?\]\((.*)?\)', md)
    md = ''
    for tup in itertools.batched(md_parts, n=4):
        if len(tup) < 4:
            md += md_highlights_to_html(tup[0])
        else:
            before, excl, desc, link = tup
            md += md_highlights_to_html(before)

            if excl:
                desc = desc.replace('"', '&quot;')
                md += f'<img src="{link}" alt="{desc}"/>'
            else:
                link = link.replace('"', ' ') # Invalid URL character
                md += f'<a href="{link}">{md_highlights_to_html(desc)}</a>'

    return md

if __name__ == '__main__':
    md = sys.stdin.read()
    print(md_to_html(md), end='')
