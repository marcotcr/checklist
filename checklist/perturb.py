import numpy as np
import collections
import re
import os
import json
import pattern
from pattern.en import tenses
from .editor import recursive_apply, MunchWithAdd

def load_data():
    cur_folder = os.path.dirname(__file__)
    basic = json.load(open(os.path.join(cur_folder, 'data', 'lexicons', 'basic.json')))
    names = json.load(open(os.path.join(cur_folder, 'data', 'names.json')))
    name_set = { x:set(names[x]) for x in names }
    data = {
        'name': names,
        'name_set': name_set,
        'city': basic['city'],
        'country': basic['country'],
    }
    return data

def process_ret(ret, ret_m=None, meta=False, n=10):
    if ret:
        if len(ret) > n:
            idxs = np.random.choice(len(ret), n, replace=False)
            ret = [ret[i] for i in idxs]
            if ret_m:
                ret_m = [ret_m[i] for i in idxs]
        if meta:
            ret = (ret, ret_m)
        return ret
    return None

class Perturb:
    data = load_data()

    @staticmethod
    def perturb(data, perturb_fn, keep_original=True, nsamples=None, *args, **kwargs):
        """Perturbs data according to some function

        Parameters
        ----------
        data : list
            List of examples, could be strings, tuples, dicts, spacy docs, whatever
        perturb_fn : function
            Arguments: (example, *args, **kwargs)
            Returns: list of examples, or (examples, meta) if meta=True in **kwargs.
            Can also return None if perturbation does not apply, and it will be ignored.
        keep_original : bool
            if True, include original example (from data) in output
        nsamples : int
            number of examples in data to perturb
        meta : bool
            if True, perturb_fn returns (examples, meta), and meta is added to ret.meta

        Returns
        -------
        MunchWithAdd
            will have .data and .meta (if meta=True in **kwargs)

        """
        ret = MunchWithAdd()
        use_meta = kwargs.get('meta', False)
        ret_data = []
        meta = []
        order = list(range(len(data)))
        samples = 0
        if nsamples:
            np.random.shuffle(order)
        for i in order:
            d = data[i]
            t = []
            add = []
            if keep_original:
                org = recursive_apply(d, str)
                t.append(org)
                add.append(None)
            p = perturb_fn(d, *args, **kwargs)
            a = []
            x = []
            if not p or all([not x for x in p]):
                continue
            if use_meta:
                p, a = p
            if type(p) in [np.array, list]:
                t.extend(p)
                add.extend(a)
            else:
                t.append(p)
                add.append(a)
            ret_data.append(t)
            meta.append(add)
            samples += 1
            if nsamples and samples == nsamples:
                break
        ret.data = ret_data
        if use_meta:
            ret.meta = meta
        return ret

    @staticmethod
    def strip_punctuation(doc):
        """Removes punctuation

        Parameters
        ----------
        doc : spacy.tokens.Doc
            spacy doc

        Returns
        -------
        string
            With punctuation stripped

        """
        # doc is a spacy doc
        while len(doc) and doc[-1].pos_ == 'PUNCT':
            doc = doc[:-1]
        return doc.text

    @staticmethod
    def punctuation(doc):
        """Perturbation function which adds / removes punctuations

        Parameters
        ----------
        doc : spacy.tokens.Doc
            spacy doc

        Returns
        -------
        list(string)
            With punctuation removed and / or final stop added.

        """
        # doc is a spacy doc
        s = Perturb.strip_punctuation(doc)
        ret = []
        if s != doc.text:
            ret.append(s)
        if s + '.' != doc.text:
            ret.append(s + '.')
        return ret


    @staticmethod
    def add_typos(string, typos=1):
        """Perturbation functions, swaps random characters with their neighbors

        Parameters
        ----------
        string : str
            input string
        typos : int
            number of typos to add

        Returns
        -------
        list(string)
            perturbed strings

        """
        string = list(string)
        swaps = np.random.choice(len(string) - 1, typos)
        for swap in swaps:
            tmp = string[swap]
            string[swap] = string[swap + 1]
            string[swap + 1] = tmp
        return ''.join(string)

    @staticmethod
    def remove_negation(doc):
        """Removes negation from doc.
        This is experimental, may or may not work.

        Parameters
        ----------
        doc : spacy.token.Doc
            input

        Returns
        -------
        string
            With all negations removed

        """
        # This removes all negations in the doc. I should maybe add an option to remove just some.
        notzs = [i for i, z in enumerate(doc) if z.lemma_ == 'not' or z.dep_ == 'neg']
        new = []
        for notz in notzs:
            before = doc[notz - 1] if notz != 0 else None
            after = doc[notz + 1] if len(doc) > notz + 1 else None
            if (after and after.pos_ == 'PUNCT') or (before and before.text in ['or']):
                continue
            new.append(notz)
        notzs = new
        if not notzs:
            return None
        ret = ''
        start = 0
        for i, notz in enumerate(notzs):
            id_start = notz
            to_add = ' '
            id_end = notz + 1
            before = doc[notz - 1] if notz != 0 else None
            after = doc[notz + 1] if len(doc) > notz + 1 else None
            if before and before.lemma_ in ['will', 'can', 'do']:
                id_start = notz - 1
                tense = collections.Counter([x[0] for x in pattern.en.tenses(before.text)]).most_common(1)[0][0]
                p = pattern.en.tenses(before.text)
                params = [tense, 3]
                if p:
                    params = list(p[0])
                    params[0] = tense
                to_add = ' '+ pattern.en.conjugate(before.lemma_, *params) + ' '
            if before and after and before.lemma_ == 'do' and after.pos_ == 'VERB':
                id_start = notz - 1
                tense = collections.Counter([x[0] for x in pattern.en.tenses(before.text)]).most_common(1)[0][0]
                p = pattern.en.tenses(before.text)
                params = [tense, 3]
                if p:
                    params = list(p[0])
                    params[0] = tense
                to_add = ' '+ pattern.en.conjugate(after.text, *params) + ' '
                id_end = notz + 2
            ret += doc[start:id_start].text + to_add
            start = id_end
        ret += doc[id_end:].text
        return ret



    @staticmethod
    def add_negation(doc):
        """Adds negation to doc
        This is experimental, may or may not work. It also only works for specific parses.

        Parameters
        ----------
        doc : spacy.token.Doc
            input

        Returns
        -------
        string
            With negations added

        """
        for sentence in doc.sents:
            if len(sentence) < 3:
                continue
            root_id = [x.i for x in sentence if x.dep_ == 'ROOT'][0]
            root = doc[root_id]
            if '?' in sentence.text and sentence[0].text.lower() == 'how':
                continue
            if root.lemma_.lower() in ['thank', 'use']:
                continue
            if root.pos_ not in ['VERB', 'AUX']:
                continue
            neg = [True for x in sentence if x.dep_ == 'neg' and x.head.i == root_id]
            if neg:
                continue
            if root.lemma_ == 'be':
                if '?' in sentence.text:
                    continue
                if root.text.lower() in ['is', 'was', 'were', 'am', 'are', '\'s', '\'re', '\'m']:
                    return doc[:root_id + 1].text + ' not ' + doc[root_id + 1:].text
                else:
                    return doc[:root_id].text + ' not ' + doc[root_id:].text
            else:
                aux = [x for x in sentence if x.dep_ in ['aux', 'auxpass'] and x.head.i == root_id]
                if aux:
                    aux = aux[0]
                    if aux.lemma_.lower() in ['can', 'do', 'could', 'would', 'will', 'have', 'should']:
                        lemma = doc[aux.i].lemma_.lower()
                        if lemma == 'will':
                            fixed = 'won\'t'
                        elif lemma == 'have' and doc[aux.i].text in ['\'ve', '\'d']:
                            fixed = 'haven\'t' if doc[aux.i].text == '\'ve' else 'hadn\'t'
                        elif lemma == 'would' and doc[aux.i].text in ['\'d']:
                            fixed = 'wouldn\'t'
                        else:
                            fixed = doc[aux.i].text.rstrip('n') + 'n\'t' if lemma != 'will' else 'won\'t'
                        fixed = ' %s ' % fixed
                        return doc[:aux.i].text + fixed + doc[aux.i + 1:].text
                    return doc[:root_id].text + ' not ' + doc[root_id:].text
                else:
                    # TODO: does, do, etc. Remover return None de cima
                    subj = [x for x in sentence if x.dep_ in ['csubj', 'nsubj']]
                    params = pattern.en.tenses(root.text)
                    tense = collections.Counter([x[0] for x in pattern.en.tenses(root.text)]).most_common(1)[0][0]
                    params = [tense, 3] if not params else list(params[0])
                    params[0] = tense
                    # params = [tense, 3]
                    if root.tag_ not in ['VBG']:
                        do = pattern.en.conjugate('do', *params) + 'n\'t'
                        new_root = pattern.en.conjugate(root.text, tense='infinitive')
                    else:
                        do = 'not'
                        new_root = root.text
                    return '%s %s %s %s' % (doc[:root_id].text, do, new_root,  doc[root_id + 1:].text)

    @staticmethod
    def contractions(sentence, **kwargs):
        """Perturbation functions, contracts and expands contractions if present

        Parameters
        ----------
        sentence : str
            input

        Returns
        -------
        list
            List of strings with contractions expanded or contracted, or []

        """
        expanded = [Perturb.expand_contractions(sentence), Perturb.contract(sentence)]
        return [t for t in expanded if t != sentence]

    @staticmethod
    def expand_contractions(sentence, **kwargs):
        """Expands contractions in a sentence (if any)

        Parameters
        ----------
        sentence : str
            input string

        Returns
        -------
        string
            String with contractions expanded (if any)

        """
        contraction_map = {
            "ain't": "is not", "aren't": "are not", "can't": "cannot",
            "can't've": "cannot have", "could've": "could have", "couldn't":
            "could not", "didn't": "did not", "doesn't": "does not", "don't":
            "do not", "hadn't": "had not", "hasn't": "has not", "haven't":
            "have not", "he'd": "he would", "he'd've": "he would have",
            "he'll": "he will", "he's": "he is", "how'd": "how did", "how'd'y":
            "how do you", "how'll": "how will", "how's": "how is",
            "I'd": "I would", "I'll": "I will", "I'm": "I am",
            "I've": "I have", "i'd": "i would", "i'll": "i will",
            "i'm": "i am", "i've": "i have", "isn't": "is not",
            "it'd": "it would", "it'll": "it will", "it's": "it is", "ma'am":
            "madam", "might've": "might have", "mightn't": "might not",
            "must've": "must have", "mustn't": "must not", "needn't":
            "need not", "oughtn't": "ought not", "shan't": "shall not",
            "she'd": "she would", "she'll": "she will", "she's": "she is",
            "should've": "should have", "shouldn't": "should not", "that'd":
            "that would", "that's": "that is", "there'd": "there would",
            "there's": "there is", "they'd": "they would",
            "they'll": "they will", "they're": "they are",
            "they've": "they have", "wasn't": "was not", "we'd": "we would",
            "we'll": "we will", "we're": "we are", "we've": "we have",
            "weren't": "were not", "what're": "what are", "what's": "what is",
            "when's": "when is", "where'd": "where did", "where's": "where is",
            "where've": "where have", "who'll": "who will", "who's": "who is",
            "who've": "who have", "why's": "why is", "won't": "will not",
            "would've": "would have", "wouldn't": "would not",
            "you'd": "you would", "you'd've": "you would have",
            "you'll": "you will", "you're": "you are", "you've": "you have"
            }
        # self.reverse_contraction_map = dict([(y, x) for x, y in self.contraction_map.items()])
        contraction_pattern = re.compile(r'\b({})\b'.format('|'.join(contraction_map.keys())),
            flags=re.IGNORECASE|re.DOTALL)

        def expand_match(contraction):
            match = contraction.group(0)
            first_char = match[0]
            expanded_contraction = contraction_map.get(match, contraction_map.get(match.lower()))
            expanded_contraction = first_char + expanded_contraction[1:]
            return expanded_contraction
        return contraction_pattern.sub(expand_match, sentence)

    @staticmethod
    def contract(sentence, **kwargs):
        """Contract expanded contractions in a sentence (if any)

        Parameters
        ----------
        sentence : str
            input string

        Returns
        -------
        string
            String with contractions contracted (if any)

        """
        reverse_contraction_map = {
            'is not': "isn't", 'are not': "aren't", 'cannot': "can't",
            'could not': "couldn't", 'did not': "didn't", 'does not':
            "doesn't", 'do not': "don't", 'had not': "hadn't", 'has not':
            "hasn't", 'have not': "haven't", 'he is': "he's", 'how did':
            "how'd", 'how is': "how's", 'I would': "I'd", 'I will': "I'll",
            'I am': "I'm", 'i would': "i'd", 'i will': "i'll", 'i am': "i'm",
            'it would': "it'd", 'it will': "it'll", 'it is': "it's",
            'might not': "mightn't", 'must not': "mustn't", 'need not': "needn't",
            'ought not': "oughtn't", 'shall not': "shan't", 'she would': "she'd",
            'she will': "she'll", 'she is': "she's", 'should not': "shouldn't",
            'that would': "that'd", 'that is': "that's", 'there would':
            "there'd", 'there is': "there's", 'they would': "they'd",
            'they will': "they'll", 'they are': "they're", 'was not': "wasn't",
            'we would': "we'd", 'we will': "we'll", 'we are': "we're", 'were not':
            "weren't", 'what are': "what're", 'what is': "what's", 'when is':
            "when's", 'where did': "where'd", 'where is': "where's",
            'who will': "who'll", 'who is': "who's", 'who have': "who've", 'why is':
            "why's", 'will not': "won't", 'would not': "wouldn't", 'you would':
            "you'd", 'you will': "you'll", 'you are': "you're",
        }

        reverse_contraction_pattern = re.compile(r'\b({})\b '.format('|'.join(reverse_contraction_map.keys())),
            flags=re.IGNORECASE|re.DOTALL)
        def cont(possible):
            match = possible.group(1)
            first_char = match[0]
            expanded_contraction = reverse_contraction_map.get(match, reverse_contraction_map.get(match.lower()))
            expanded_contraction = first_char + expanded_contraction[1:] + ' '
            return expanded_contraction
        return reverse_contraction_pattern.sub(cont, sentence)

    @staticmethod
    def change_names(doc, meta=False, n=10, first_only=False, last_only=False, seed=None):
        """Replace names with other names

        Parameters
        ----------
        doc : spacy.token.Doc
            input
        meta : bool
            if True, will return list of (orig_name, new_name) as meta
        n : int
            number of names to replace original names with
        first_only : bool
            if True, will only replace first names
        last_only : bool
            if True, will only replace last names
        seed : int
            random seed

        Returns
        -------
        list(str)
            if meta=True, returns (list(str), list(tuple))
            Strings with names replaced.

        """
        if seed is not None:
            np.random.seed(seed)
        ents = [x.text for x in doc.ents if np.all([a.ent_type_ == 'PERSON' for a in x])]
        ret = []
        ret_m = []
        for x in ents:
            f = x.split()[0]
            sex = None
            if f.capitalize() in Perturb.data['name_set']['women']:
                sex = 'women'
            if f.capitalize() in Perturb.data['name_set']['men']:
                sex = 'men'
            if not sex:
                continue
            if len(x.split()) > 1:
                l = x.split()[1]
                if len(l) > 2 and l.capitalize() not in Perturb.data['name_set']['last']:
                    continue
            else:
                if last_only:
                    return None
            names = Perturb.data['name'][sex][:90+n]
            to_use = np.random.choice(names, n)
            if not first_only:
                f = x
                if len(x.split()) > 1:
                    last = Perturb.data['name']['last'][:90+n]
                    last = np.random.choice(last, n)
                    to_use = ['%s %s' % (x, y) for x, y in zip(names, last)]
                    if last_only:
                        to_use = last
                        f = x.split()[1]
            for y in to_use:
                ret.append(re.sub(r'\b%s\b' % re.escape(f), y, doc.text))
                ret_m.append((f, y))
        return process_ret(ret, ret_m=ret_m, n=n, meta=meta)

    @staticmethod
    def change_location(doc, meta=False, seed=None, n=10):
        """Change city and country names

        Parameters
        ----------
        doc : spacy.token.Doc
            input
        meta : bool
            if True, will return list of (orig_loc, new_loc) as meta
        seed : int
            random seed
        n : int
            number of locations to replace original locations with

        Returns
        -------
        list(str)
            if meta=True, returns (list(str), list(tuple))
            Strings with locations replaced.

        """
        if seed is not None:
            np.random.seed(seed)
        ents = [x.text for x in doc.ents if np.all([a.ent_type_ == 'GPE' for a in x])]
        ret = []
        ret_m = []
        for x in ents:
            if x in Perturb.data['city']:
                names = Perturb.data['city'][:100]
            elif x in Perturb.data['country']:
                names = Perturb.data['country'][:50]
            else:
                continue
            sub_re = re.compile(r'\b%s\b' % re.escape(x))
            to_use = np.random.choice(names, n)
            ret.extend([sub_re.sub(n, doc.text) for n in to_use])
            ret_m.extend([(x, n) for n in to_use])
        return process_ret(ret, ret_m=ret_m, n=n, meta=meta)

    @staticmethod
    def change_number(doc, meta=False, seed=None, n=10):
        """Change integers to other integers within 20% of the original integer
        Does not change '2' or '4' to avoid abbreviations (this is 4 you, etc)

        Parameters
        ----------
        doc : spacy.token.Doc
            input
        meta : bool
            if True, will return list of (orig_number, new_number) as meta
        seed : int
            random seed
        n : int
            number of numbers to replace original locations with

        Returns
        -------
        list(str)
            if meta=True, returns (list(str), list(tuple))
            Strings with numbers replaced.

        """
        if seed is not None:
            np.random.seed(seed)
        nums = [x.text for x in doc if x.text.isdigit()]
        ret = []
        ret_m = []
        for x in nums:
            # e.g. this is 4 you
            if x == '2' or x == '4':
                continue
            sub_re = re.compile(r'\b%s\b' % x)
            try:
                change = int(int(x) * .2) + 1
            except:
                continue
            to_sub = np.random.randint(-min(change, int(x) - 1), change + 1, n * 3)
            to_sub = ['%s' % str(int(x) + t) for t in to_sub if str(int(x) + t) != x][:n]
            ret.extend([sub_re.sub(n, doc.text) for n in to_sub])
            ret_m.extend([(x, n) for n in to_sub])
        return process_ret(ret, ret_m=ret_m, n=n, meta=meta)
