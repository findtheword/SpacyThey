import re

import coreferee, spacy  # don't remove coreferee
import lemminflect
from helpers import html_replaced_with_spaces

nlp = spacy.load('en_core_web_trf')
nlp.add_pipe('coreferee')

# https://github.com/msg-systems/coreferee/issues/19#issuecomment-911522340

html = """
<?xml version='1.0' encoding='utf-8'?>

<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
<meta charset="utf-8"/><title>The Project Gutenberg eBook of Alice’s Adventures in Wonderland, by Lewis Carroll</title>
<link href="6269378934971248692_cover.jpg" rel="icon" type="image/x-cover" id="id-8875896598953579899"/>

<link href="0.css" rel="stylesheet" type="text/css"/>
<link href="1.css" rel="stylesheet" type="text/css"/>
<link href="pgepub.css" rel="stylesheet" type="text/css"/>
<meta name="generator" content="Ebookmaker 0.12.21 by Project Gutenberg"/>
</head>
<body class="x-ebookmaker x-ebookmaker-3"><div class="chapter" id="pgepubid00004">
<h2><a id="chap01"/>CHAPTER I.<br/>
Down the Rabbit-Hole</h2>
<p>
Alice was beginning to get very tired of sitting by her sister on the bank, and
of having nothing to do: once or twice she had peeped into the book her sister
was reading, but it had no pictures or conversations in it, “and what is
the use of a book,” thought Alice “without pictures or
conversations?”
</p>"""

text = html_replaced_with_spaces(html)

# t = [f"{i} {txt}" for i, txt in enumerate(text.split(' '))]
# print(' '.join(t))

doc = nlp(text)

# for token in doc:
#     print(token.i, token.text)

coref_chains = doc._.coref_chains
coref_chains.print()

# token.idx
# len(token.text)

character = 'Alice'
found_character_tokens = []
for chain in coref_chains:
    found_character = False
    for token_info in chain:
        token = doc[token_info.root_index]
        if token.text == character:
            found_character = True
            break
    if found_character:
        for token_info in chain:
            token = doc[token_info.root_index]
            found_character_tokens.append(token)

# last elements dealt with first
found_character_tokens.sort(key=lambda el: el.idx, reverse=True)


def check_lookup_solution(text):
    text = re.sub("(s)?he was", "they were", text)
    text = re.sub( "She was", "They were", text)
    text = re.sub( "He was", "They were", text)
    text = re.sub( "(s)?he has", "they have", text)
    text = re.sub( "She has", "They have", text)
    text = re.sub( "He has", "They have", text)
    text = re.sub( "He 's", "They're", text)
    text = re.sub( "She's", "They're", text)
    text = re.sub( "(s)?he's", "they're", text)
    text = re.sub( "he has", "they have", text)
    text = re.sub( "He has", "They have", text)
    text = re.sub( "He is", "They are", text)
    text = re.sub( "She is", "They are", text)
    text = re.sub( "(s)?he is", "they are", text)
    text = re.sub( "(she)([ ^]+)(s) ", "they $2", text)
    text = re.sub( "(he)([ ^]+)(s) ", "they $2", text)
    text = re.sub( "(She)([ ^]+)(s) ", "They $2", text)
    text = re.sub( "(He)([ ^]+)(s) ", "They $2", text)
    # Imperfect below - - but "her" as subject " possessive are tough
    text = re.sub( "her ", "them ", text)
    text = re.sub( " ing her", "ing them", text)
    text = re.sub( "(s)?he", "they", text)
    text = re.sub( "(s)?he", "they", text)
    text = re.sub( "He", "They", text)
    text = re.sub( "She", "They", text)
    text = re.sub( "hers", "theirs", text)
    text = re.sub( "Hers", "Theirs", text)
    text = re.sub( "him", "them", text)
    text = re.sub( "Him", "Them", text)
    text = re.sub( "His", "Their", text)
    text = re.sub( "his", "their", text)
    text = re.sub( "her", "their", text)
    text = re.sub( "Her", "Their", text)
    text = re.sub( "himself", "themselves", text)
    text = re.sub( "herself", "themselves", text)

    return text


def update_token(token):
    prev_token = doc[token.i - 1]
    following_token = doc[token.i + 1]
    # print(prev_token, token, following_token, 222, following_token.lemma_, following_token.tag_)
    to_change = ' '.join([prev_token.text, token.text, following_token.text])
    changed = check_lookup_solution(to_change)
    print(to_change, 333, changed,33)
    if to_change == changed:
        if following_token.tag_[0:2] == 'VB':
            # figure out later
            # print(following_token.tag_, 33)
            following_token._.inflect('NNS')


for token in found_character_tokens:
    if token.text == character:
        continue
    update_token(token)
