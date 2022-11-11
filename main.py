import re
from collections import namedtuple

import coreferee, spacy  # don't remove coreferee
import inflect
import lemminflect
from spacy import Vocab

from helpers import html_replaced_with_spaces

nlp = spacy.load('en_core_web_trf')
nlp.add_pipe('coreferee')

inflector = inflect.engine()

# https://github.com/msg-systems/coreferee/issues/19#issuecomment-911522340

html = (open("aliceInWonderland/4560944924381563385_11-h-2.htm.xhtml", "r", encoding='utf-8')).read()
html2 = '''
<p>
“I won’t indeed!” said Alice, in a great hurry to change the
subject of conversation. “Are you—are you fond—of—of
dogs?” The Mouse did not answer, so Alice went on eagerly: “There
is such a nice little dog near our house I should like to show you! A little
bright-eyed terrier, you know, with oh, such long curly brown hair! And
it’ll fetch things when you throw them, and it’ll sit up and beg
for its dinner, and all sorts of things—I can’t remember half of
them—and it belongs to a farmer, you know, and he says it’s so
useful, it’s worth a hundred pounds! He says it kills all the rats
and—oh dear!” cried Alice in a sorrowful tone, “I’m
afraid I’ve offended it again!” For the Mouse was swimming away
from her as hard as it could go, and making quite a commotion in the pool as it
went.
</p>
<p>
So she called softly after it, “Mouse dear! Do come back again, and we
won’t talk about cats or dogs either, if you don’t like
them!” When the Mouse heard this, it turned round and swam slowly back to
her: its face was quite pale (with passion, Alice thought), and it said in a
low trembling voice, “Let us get to the shore, and then I’ll tell
you my history, and you’ll understand why it is I hate cats and
dogs.”
</p>
<p>
It was high time to go, for the pool was getting quite crowded with the birds
and animals that had fallen into it: there were a Duck and a Dodo, a Lory and
an Eaglet, and several other curious creatures. Alice led the way, and the
whole party swam to the shore.
</p>
<h2><a id="chap01"/>CHAPTER I.<br/>
Down the Rabbit-Hole</h2>
<p>
Alice was beginning to get very tired of sitting by her sister on the bank, and
of having nothing to do: once or twice she had peeped into the book her sister
was reading, but it had no pictures or conversations in it, “and what is
the use of a book,” thought Alice “without pictures or
conversations?”
</p>
'''

text = html_replaced_with_spaces(html)

# t = [f"{i} {txt}" for i, txt in enumerate(text.split(' '))]
# print(' '.join(t))

doc = nlp(text)

# for token in doc:
#     print(token.i, token.text)

coref_chains = doc._.coref_chains
# coref_chains.print()

p = inflect.engine()

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

CorrectOrderTuple = namedtuple('CorrectOrderTuple', ['i', 'old', 'new'])


class WordUpdater:
    updates = []

    def add(self, token, to):
        info = CorrectOrderTuple(token.idx, token.text, to)
        self._do_update(info)
        #self.updates.append(info)

    def _do_update(self, info: CorrectOrderTuple):
        global html

        to = info.new

        if info.old[0].isupper():
            to = to[0].upper() + to[1:]

        html = html[0: info.i] + to + html[info.i + len(info.old):]

    def update(self):
        self.updates.sort(key=lambda x: x.i)
        while self.updates:
            self._do_update(self.updates.pop())


word_updater = WordUpdater()


def update_token(token):
    prev_token = doc[token.i - 1]
    following_token = doc[token.i + 1]
    # print(list(token.children),3333)
    # print(prev_token, token, following_token, 222, following_token.lemma_, following_token.tag_)
    to_change = ' '.join([prev_token.text, token.text, following_token.text])

    updates = []

    # MUST be before other modders
    if following_token.tag_[0:2] == 'VB' and following_token.lemma_ in ['has', 'be']:
        current_form = following_token.text
        plural_form = inflector.plural(current_form)
        if plural_form != current_form:
            word_updater.add(following_token, plural_form)

    if token.tag_ == 'PRP':  # personal pronoun
        suggested_updated = inflector.plural(token.text)
        if str(suggested_updated).lower() == 'their':
            suggested_updated = 'them'
        word_updater.add(token, suggested_updated)
    elif token.tag_ == 'PRP$':  # possessive pronoun
        word_updater.add(token, inflector.plural(token.text))

    # print('is vb', following_token.tag_, a, following_token.text, '---', to_change, '-----', inflector.plural(following_token.text))

    # token.morph: Case=Nom|Gender=Fem|Number=Sing|Person=3|PronType=Prs
    # print(token.tag_, token.text, 222, token.morph)
    # print(token.morph, token._.inflect(following_token.tag_, ))
    # tag = Penn Treebank tag,


for token in found_character_tokens:
    if token.text == character:
        continue
    update_token(token)

word_updater.update()

print(html)
