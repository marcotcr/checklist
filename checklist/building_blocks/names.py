from ..perturb import process_ret
import os
import csv
import collections
import numpy as np
import re
import random

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
            self.names['first'][name]['sex'] = 'M' if self.names['first'][name]['M'] > self.names['first'][name]['F'] else 'F'
            del self.names['first'][name]['M']
            del self.names['first'][name]['F']
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
                    sex=None, race_from=None, race_to=None, seed=None):
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
                ret.append(re.sub(r'\b%s\b' % re.escape(f), y, doc.text))
                ret_m.append((f, y))
        return process_ret(ret, ret_m=ret_m, n=n, meta=meta)
