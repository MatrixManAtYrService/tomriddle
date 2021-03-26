from collections import namedtuple
from pathlib import Path
import json

import pyphen

Fragments = namedtuple("Fragments", "syllables twoshort startend")


def main(args):

    try:
        with open(args.corpus, "r") as f:
            fragments = get_fragments_from(f)
    except AttributeError:
        fragments = get_default_fragments()

    for i

    print(words[0])
    return args.input


def riddler(fragments, constraints=[]):
    """
    Iterate on angrams constructed given fragments.

    If constraints are provided, require that they appear as substrings
    and in the given order (potentially with other material in between).
    """


def clean(in_word):
    """cast to lowercase alpha-only."""
    chars = []
    for c in in_word:
        if c.isalpha():
            chars.append(c.lower())
    return "".join(chars)


def gen_default_fragments():
    """
    Writes syllabary_g.py, startend_g.py, and twoword_g.py for later import.

    Not called during normal usage, but used to generate hard-coded
    lists that are imported if the user doesn't supply a corpus of their
    """

    # get corpora
    import nltk

    nltk.download("brown")
    in_words = list(nltk.corpus.brown.words())
    nltk.download("gutenberg")
    in_words += list(nltk.corpus.gutenberg.words())

    # clean words
    words = []
    for in_word in in_words:
        word = clean(in_word)
        if word:
            words.append(word)

    # write modules
    for generated_module, func in {
        "syllables": gen_syllables,
        "twoshort": gen_twoshort,
        "startend": gen_startend,
    }:
        fname = Path(__file__).parent / f"{generated_module}_g.py"
        content = json.dumps(func(words), sort_keys=True)
        with open(fname, "w") as f:
            f.write(
                f'''
            import json

            def syllables():
                """{func.__doc__}"""
                return json.loads(\'\'\'
                    {content}
                 \'\'\')
            '''
            )


def get_default_fragments():
    """reads fragments from the files created by the function above."""
    import syllables_g as syl
    import twoshort_g as two
    import startend_g as se

    syllables = syl.get()
    twoshort = two.get()
    startend = se.get()

    return Fragments(syllables, twoshort, startend)


def get_fragments_from(open_file):
    """reads fragments from a user-supplied file."""

    lines = open_file.read.splitlines()
    words = []
    for in_word in lines.split(" "):
        word = clean(in_word)
        if word:
            words.append(word)

    syllables = gen_syllables(words)
    twoshort = gen_twoshort(words)
    startend = gen_startend(words)

    return Fragments(syllables, twoshort, startend)


def gen_syllables(corpus):
    """Short pronouncable fragments like wump, wroth, or wynd."""

    lookup = pyphen.Pyphen(lang="nl_NL")
    syllable_counts = {}
    for word in corpus:
        syllables = lookup.inserted(word).split("-")
        for syl in syllables:
            if set(syl).intersection(set("aeiouy")):
                syllable_counts.setdefault(syl, 0)
                syllable_counts[syl] += 1

    return syllable_counts


def gen_startend(corpus):
    """
    Three or four letter strings that start or end words like ant-, aard-,
    -azy, or -gist.
    """

    begins = {}
    ends = {}

    def add(store, partial_word):
        """register the partial word and keep a count."""
        store.setdefault(partial_word, 0)
        store[partial_word] += 1

    def scan(num):
        """walk the corpus, gather partial words."""
        for word in corpus:
            if len(word) > num:
                add(begins, word[:num])

    scan(3)
    scan(4)

    return (begins, ends)


def gen_twoshort(corpus):
    """Three, four, or five letter strings made of two concatenated words like
    isa, iam, goto."""
    twoshort_count = {}
    for word, nextword in zip(corpus, corpus[1:]):
        if 2 < len(word) + len(nextword) < 6:
            twoshort = "".join([word, nextword])
            twoshort_count[twoshort] += 1

    return twoshort_count


Args = namedtuple("namespace", "input")
if __name__ == "__main__":
    # main(Args("IAmLordVoldemort"))
    gen_default_fragments()
