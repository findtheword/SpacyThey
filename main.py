import os
import re
import shutil
from collections import namedtuple

import coreferee, spacy  # don't remove coreferee
import inflect
import lemminflect
from spacy import Vocab

from tqdm import tqdm
from helpers import html_replaced_with_spaces, WordUpdater

nlp = spacy.load('en_core_web_trf')
nlp.add_pipe('coreferee')

inflector = inflect.engine()


# https://github.com/msg-systems/coreferee/issues/19#issuecomment-911522340

def translate(original_html, update_params):
    text = html_replaced_with_spaces(original_html)

    doc = nlp(text)
    p = inflect.engine()

    word_updater = WordUpdater(update_params)

    def update_name(character_name):
        if not character_name:
            return
        from_name = character_name['from']
        to_name = character_name['to']

        TokenMinimal = namedtuple('TokenMinimal', ['idx', 'text'])

        for found in re.finditer(from_name, original_html):
            found: TokenMinimal = TokenMinimal(found.start(), from_name)
            word_updater.add(found, to_name)

    update_name(update_params.get('character', None))

    def update_token(token):

        try:
            following_token = doc[token.i + 1]
        except IndexError:
            return

        if token.text.lower() in ['i', 'it', 'yourself', 'myself', 'we', 'they']:
            return

        if following_token.tag_[0:2] == 'VB' and following_token.lemma_ in ['has', 'be']:

            current_form = following_token.text
            plural_form = inflector.plural(current_form, 4)

            if plural_form == 'bes':
                plural_form = 'be'  # ffs
            elif plural_form == 'beens':
                plural_form = 'been'

            if plural_form != current_form:
                word_updater.add(following_token, plural_form)

        token_tag = token.tag_

        if token_tag[0:3] == 'PRP':  # personal pronoun
            if token.tag_ == 'PRP':  # personal pronoun
                suggested_updated = inflector.plural(token.text)
                if str(suggested_updated).lower() == 'their':
                    suggested_updated = 'them'
                word_updater.add(token, suggested_updated)
            elif token.tag_ == 'PRP$':  # possessive pronoun
                word_updater.add(token, inflector.plural(token.text))


    coref_chains = doc._.coref_chains
    # coref_chains.print()

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
        # else:
        #     print([doc[el.root_index].text for el in  chain])

    for token in found_character_tokens:
        if token.text == character:
            continue
        update_token(token)

    return word_updater.update(original_html)


dir = 'aliceInWonderland'
files = os.listdir(dir)
files = [f for f in files]
path = os.getcwd()

new_dir = dir + '_they'
if not os.path.isdir(new_dir):
    os.makedirs(new_dir, exist_ok=True)

for file in tqdm(files,  desc ="Translating"):
    if 'htm.xhtml' in file:
        html = (open(dir + '/' + file, "r", encoding='utf-8')).read()
        outcome = translate(html, update_params={'span': True, 'character': {'from': 'Alice', 'to': 'Alex'}})
        file = open(new_dir + '/' + file, 'w', encoding='utf-8')
        file.write(outcome)
        file.close()
    else:
        shutil.copyfile(path + '/' + dir + '/' + file, path + '/' + new_dir + '/' + file)



