from ..perturb import process_ret
import os
import csv
import collections
import numpy as np
import re
import random
from itertools import zip_longest

def get_data_path():
    cur_folder = os.path.dirname(__file__)
    return os.path.join(os.path.split(os.path.join(cur_folder))[0], 'data')

class Names:
    def __init__(self):
        self.load_names()

    def load_names(self):
        # first names from https://www.nature.com/articles/sdata201825
        # last names from fivithirtyeight-data github repo
        name_path = os.path.join(get_data_path(), 'names')
        surnames = csv.DictReader(open(os.path.join(name_path, 'surnames.csv')))
        ret = []
        self.names = {}
        # self.names['by_race'] = {}
        # self.names['by_sex'] = {}
        self.names['first'] = collections.defaultdict(lambda: collections.defaultdict(lambda: 0.))
        self.names['last'] = collections.defaultdict(lambda: collections.defaultdict(lambda: 0.))
        to_float = lambda x: float(x) if x != '(S)' else 0
        mapz = {'pctblack': 'black', 'pctwhite': 'white', 'pcthispanic': 'hispanic', 'pctapi': 'asian', 'count': 'count'}
        for x in surnames:
            name = x['name'].capitalize()
            for key in ['pctblack', 'pctwhite', 'pcthispanic', 'pctapi', 'count']:
                self.names['last'][name][mapz[key]] = to_float(x[key])

        first_file = os.path.join(name_path, 'census_data_by_year.txt')
        women = collections.defaultdict(lambda: 0.)
        men = collections.defaultdict(lambda: 0.)
        all_first = collections.defaultdict(lambda: 0.)
        for l in open(first_file):
            name, g, count = l.strip().split(',')
            name = name.capitalize()
            self.names['first'][name]['count'] += int(count)
            self.names['first'][name][g] += int(count)
        for name in self.names['first']:
            if self.names['first'][name]['M'] / self.names['first'][name]['count'] > .9:
                self.names['first'][name]['sex'] = 'M'
            elif self.names['first'][name]['F'] / self.names['first'][name]['count'] > .9:
                self.names['first'][name]['sex'] = 'F'
            else:
                self.names['first'][name]['sex'] = 'A'

            # self.names['first'][name]['sex'] = 'M' if self.names['first'][name]['M'] > self.names['first'][name]['F'] else 'F'
            # del self.names['first'][name]['M']
            # del self.names['first'][name]['F']
        first_race = csv.DictReader(open(os.path.join(name_path, 'firstnames.csv')))
        ret = []
        for x in first_race:
            name = x['firstname'].capitalize()
            for key in ['pctblack', 'pctwhite', 'pcthispanic', 'pctapi']:
                # if name not in self.names['first']:
                #     continue
                self.names['first'][name][mapz[key]] = to_float(x[key])
        self.names['first_sorted'] = sorted(self.names['first'], key=lambda x: self.names['first'][x]['count'], reverse=True)
        self.names['last_sorted'] = sorted(self.names['last'], key=lambda x: self.names['last'][x]['count'], reverse=True)

    def is_sex(self, name, sex):
        name = name.capitalize()
        return True if sex is None else self.names['first'][name].get('sex', None) == sex

    def is_race(self, name, race, race_prop=50, last=False):
        name = name.capitalize()
        fkey = 'first' if last == False else 'last'
        return True if race is None else self.names[fkey][name].get(race, 0) > race_prop

    def first_names(self, sex=None, race=None, n=20, race_prop=50):
        out = []
        t = 0
        # In loop form because self.names['first_sorted'] is really large, and we don't want to iterate over all of it only to get N afterwards
        for x in self.names['first_sorted']:
            if self.is_sex(x, sex) and self.is_race(x, race, race_prop):
                out.append(x)
                t += 1
            if t == n:
                break
        return out

        # return [x for x in self.names['first_sorted'] if self.is_sex(x, sex) and self.is_race(x, race, race_prop)][:n]
    def last_names(self, race=None, n=20, race_prop=50):
        out = []
        t = 0
        # In loop form because self.names['first_sorted'] is really large, and we don't want to iterate over all of it only to get N afterwards
        for x in self.names['last_sorted']:
            if self.is_race(x, race, race_prop, last=True):
                out.append(x)
                t += 1
            if t == n:
                break
        return out
        # return [x for x in self.names['last_sorted'] if self.is_race(x, race, race_prop, last=True)][:n]
    def is_name(self, name, sex=None, race=None, last=False, min_freq=30, race_prop=50):
        name = name.capitalize()
        if last:
            return name in self.names['last'] and self.names['last'][name]['count'] > min_freq
        return name in self.names['first'] and self.names['first'][name]['count'] > min_freq and self.is_sex(name, sex) and self.is_race(name, race, race_prop)

    def change_names(self, doc, meta=False, n=10, first_only=False, last_only=False,
                    sex=None, race_from=None, race_to=None, seed=None, change_in_all=True):
        """Replace names with other names

        Parameters
        ----------
        doc : spacy.token.Doc or list / tuple of spacy.token.docs
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
        change_in_all: bool
            if True and doc is list / tuple, only change name that are present in all
        Returns
        -------
        list(str)
            if meta=True, returns (list(str), list(tuple))
            Strings with names replaced.

        """
        if seed is not None:
            np.random.seed(seed)
        doc_type = type(doc)
        docs = [doc] if type(doc) not in [list, tuple] else doc

        ents = [[x.text for x in doc.ents if np.all([a.ent_type_ == 'PERSON' for a in x])] for doc in docs]
        all_ents = list(set([y for x in ents for y in x]))
        ents = all_ents if not change_in_all else [x for x in all_ents if all([x in y for y in ents])]
        ret = []
        ret_m = []
        for x in ents:
            f = x.split()[0].capitalize()
            if not self.is_name(f, sex=sex, race=race_from):
                continue
            source_sex = 'M' if self.is_sex(f, 'M') else 'F'
            if len(x.split()) > 1:
                l = x.split()[1]
                if len(l) > 2 and not self.is_name(f, race=race_from, last=True):
                    continue
            else:
                if last_only:
                    continue
            names = self.first_names(sex=source_sex, race=race_to, n=90+n)
            # names = ['a', 'b', 'c']
            # to_use = random.sample(names, min(n, len(names)))
            to_use = np.random.choice(names, min(n, len(names)), replace=False)
            # to_use = names[:n]
            if not first_only:
                f = x
                if len(x.split()) > 1:
                    last = self.last_names(race=race_to, n=90+n)
                    # last = random.sample(last, min(n, len(last)))
                    last = np.random.choice(last, min(n, len(last)), replace=False)
                    # last = last[:n]
                    to_use = ['%s %s' % (x, y) for x, y in zip(to_use, last)]
                    if last_only:
                        to_use = last
                        f = x.split()[1]
            for y in to_use:
                ret.append([re.sub(r'\b%s\b' % re.escape(f), y, doc.text) for doc in docs])
                ret_m.append((f, y))
        if doc_type in [tuple, list]:
            if doc_type == tuple:
                ret = [doc_type(x) for x in ret]
        else:
            ret = [x[0] for x in ret]
        return process_ret(ret, ret_m=ret_m, n=n, meta=meta)

    def replace_pronouns(self, doc, to_male=True):
        mappings = {
        'to_male':
            {
                ('her', 'PRP$'): 'his',
                ('her', 'PRP'): 'him',
                ('hers', 'PRP'): 'his'
            },
        'to_female':
            {
                ('his', 'PRP$'): 'her',
                ('his', 'PRP'): 'hers',
                ('him', 'PRP'): 'her'
            }
        }
        mapz = mappings['to_male'] if to_male else mappings['to_female']
        replace_idxs = []
        replace_toks = []
        for i, x in enumerate(doc):
            text, tag = x.text, x.tag_
            text = text.lower()
            if (text, tag) in mapz:
                replace_idxs.append(i)
                r = mapz[(text, tag)]
                if x.text_with_ws.endswith(' '):
                    r += ' '
                if x.text[0].isupper():
                    r = r[0].upper() + r[1:]
                replace_toks.append(r)

        if not replace_idxs:
            return doc.text
        start = 0
        ret_text = ''
        for i, r in zip(replace_idxs, replace_toks):
            if i > start:
                ret_text += doc[start:i].text_with_ws
            ret_text += r
            start = i + 1
        if start < len(doc):
            ret_text += doc[start:].text
        return ret_text

    def replace_sex(self, doc, meta=False, n_male=5, n_female=5):
        # TODO: him / her / his / hers, use .tag_
        pairs = [('man', 'woman'), ('men', 'women'), ('he',  'she'),   ('father', 'mother'), ('son', 'daughter'), ('brother', 'sister')]
        mf = dict(pairs)
        fm = dict([(x[1], x[0]) for x in pairs])
        def mysub_fn(dictionary):
            def mysub(match):
                m = match.group()
                ret = dictionary[m.lower()]
                if m[0].isupper():
                    ret = ret[0].upper() + ret[1:]
                return ret
            return mysub
        mysub_m = mysub_fn(mf)
        mysub_f = mysub_fn(fm)
        all_f_sentence = self.replace_pronouns(doc, to_male=False)
        all_m_sentence = self.replace_pronouns(doc, to_male=True)
        all_f_sentence = re.sub(r'\b(%s)\b' % ('|'.join([x[0] for x in pairs])), mysub_m, all_f_sentence, flags=re.I)
        all_m_sentence = re.sub(r'\b(%s)\b' % ('|'.join([x[1] for x in pairs])), mysub_f, all_m_sentence, flags=re.I)
        ents = [x[0].text for x in doc.ents if np.all([a.ent_type_ == 'PERSON' for a in x])]
        male_names = [x for x in ents if self.is_name(x, sex='M')]
        female_names = [x for x in ents if self.is_name(x, sex='F')]
        mnames = self.first_names(sex='M', n=max(100, (n_male  + n_female) * len(male_names)))
        fnames = self.first_names(sex='F', n=max(100, (n_male + n_female) * len(female_names)))
        def reshapez(input, ncols):
            return [] if input.shape[0] == 0 else input.reshape(-1, ncols)
            if not input:
                return []
            else:
                retur
        to_use_mm = reshapez(np.random.choice(mnames, n_male * len(male_names), replace=False), len(male_names))
        to_use_fm = reshapez(np.random.choice(mnames, n_male * len(female_names), replace=False), len(female_names))
        to_use_mf = reshapez(np.random.choice(fnames, n_female * len(male_names), replace=False), len(male_names))
        to_use_ff = reshapez(np.random.choice(fnames, n_female * len(female_names), replace=False), len(female_names))
        # All male: replace all male names to other male names, and all female names with male names
        rmeta = []
        ret = []
        rep_names = [x.lower() for x in male_names + female_names]
        if not rep_names:
            if n_male and all_m_sentence != doc.text:
                ret.append(all_m_sentence)
                rmeta.append('M')
            if n_female and all_f_sentence != doc.text:
                ret.append(all_f_sentence)
                rmeta.append('F')
        for new_m, new_f in zip_longest(to_use_mm, to_use_fm, fillvalue=[]):
            new_m = list(new_m)
            new_f = list(new_f)
            d = dict(zip(rep_names, new_m + new_f))
            mysub = mysub_fn(d)
            r = re.sub(r'\b(%s)\b' % ('|'.join(male_names+female_names)), mysub, all_m_sentence, flags=re.I)
            ret.append(r)
            rmeta.append('M')
        for new_m, new_f in zip_longest(to_use_mf, to_use_ff, fillvalue=[]):
            new_m = list(new_m)
            new_f = list(new_f)
            d = dict(zip(rep_names, new_m + new_f))
            mysub = mysub_fn(d)
            r = re.sub(r'\b(%s)\b' % ('|'.join(male_names+female_names)), mysub, all_f_sentence, flags=re.I)
            ret.append(r)
            rmeta.append('F')

        return process_ret(ret, ret_m=rmeta, n=n_male+n_female, meta=meta)
            # names = ['a', 'b', 'c']
            # to_use = random.sample(names, min(n, len(names)))
        # female_names = [x for x in doc if x.ent_type_ == 'PERSON' and self.is_name(x.text, sex='F')]
        print(all_f_sentence)
        print(all_m_sentence)
        print('Male', male_names)
        print('Female', female_names)
        # deal with his / hers / him / her
