import coreferee, spacy

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

for chain in coref_chains:
    found_character = False
    for token_info in chain:

        token = doc[token_info.root_index]
        if token.text == character:
            found_character = True
            break
    if found_character:
        for token_i in chain:
            print(token.text, 222)


