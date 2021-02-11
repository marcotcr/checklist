import collections
import itertools
import string
import numpy as np
import re
import copy
import os
import json
import munch
import pickle

from .viewer.template_editor import TemplateEditor
from .multilingual import multilingual_params, get_language_code

class MunchWithAdd(munch.Munch):
    def __add__(self, other):
        temp = copy.deepcopy(self)
        for k in self:
            try:
                temp[k] = temp[k] + other[k]
            except KeyError:
                raise Exception('Both Munches must have the same keys')
        return temp

    def __iadd__(self, other):
        for k in self:
            self[k] = self[k] + other[k]
        return self

class SafeFormatter(string.Formatter):
    def vformat(self, format_string, args, kwargs):
        args_len = len(args)  # for checking IndexError
        tokens = []
        for (lit, name, spec, conv) in self.parse(format_string):
            # re-escape braces that parse() unescaped
            lit = lit.replace('{', '{{').replace('}', '}}')
            # only lit is non-None at the end of the string
            if name is None:
                tokens.append(lit)
            else:
                # but conv and spec are None if unused
                conv = '!' + conv if conv else ''
                spec = ':' + spec if spec else ''
                # name includes indexing ([blah]) and attributes (.blah)
                # so get just the first part
                fp = name.split('[')[0].split('.')[0]
                # treat as normal if fp is empty (an implicit
                # positional arg), a digit (an explicit positional
                # arg) or if it is in kwargs
                if not fp or fp.isdigit() or fp in kwargs:
                    tokens.extend([lit, '{', name, conv, spec, '}'])
                # otherwise escape the braces
                else:
                    tokens.extend([lit, '{{', name, conv, spec, '}}'])
        format_string = ''.join(tokens)  # put the string back together
        # finally call the default formatter
        return string.Formatter.vformat(self, format_string, args, kwargs)

def recursive_format(obj, mapping, ignore_missing=False):
    """Formats all strings within an object, using mapping

    Parameters
    ----------
    obj : string, tuple, list, or dict
        Object (leaves must be strings, regardless of type)
    mapping : dict
        format dictionary, maps keys to values
    ignore_missing : bool
        If True, will not throw exception if a string contains a tag not
        present in mapping, and will keep the tag instead.

    Returns
    -------
    string, tuple, list, or dict
        Object of the same type as obj, with strings formatted (tags replaced
        by their value)

    """
    def formatfn(x, mapping):
        fmt = SafeFormatter()
        formatz = lambda x, m: x.format(**m) if not ignore_missing else fmt.format(x, **m)
        options = re.compile(r'{([^}]+):([^}]+)}')
        def mysub(match):
            options, thing = match.group(1, 2)
            ret = ''
            if 'a' in options:
                if ignore_missing and thing not in mapping:
                    return match.group()
                else:
                    word = formatz('{%s}' % thing, mapping)
                    ret += '%s ' % add_article(word).split()[0]
            ret += '{%s}' % thing
            return ret
        x = options.sub(mysub, x)
        return formatz(x, mapping)
    return recursive_apply(obj, formatfn, mapping)

def recursive_apply(obj, fn, *args, **kwargs):
    """Recursively applies a function to an obj

    Parameters
    ----------
    obj : string, tuple, list, or dict
        Object (leaves must be strings, regardless of type)
    fn : function
        function to be applied to the leaves (strings)

    Returns
    -------
    string, tuple, list, or dict
        Object of the same type as obj, with fn applied to leaves

    """
    if type(obj) in [str, bytes]:
        return fn(obj, *args, **kwargs)#obj.format(**(mapping))
    elif type(obj) == tuple:
        return tuple(recursive_apply(list(obj), fn, *args, **kwargs))
    elif type(obj) == list:
        return [recursive_apply(o, fn, *args, **kwargs) for o in obj]
    elif type(obj) == dict:
        return {k: recursive_apply(v, fn, *args, **kwargs) for k, v in obj.items()}
    else:
        return fn(obj, *args, **kwargs)
        # return obj

def replace_mask(text):
    """Replaces multiple instances of mask with indexed versions.

    Parameters
    ----------
    text : string
        masked input, e.g. "This is a {mask} {mask} and {mask}"

    Returns
    -------
    string
        multiple instances of the same mask are replaced with indexed versions
        e.g. "This is a {mask[0]} {mask[1]} and {mask[2]}

    """
    mask_finder = re.compile(r'\{((?:[^\}]*:)?mask\d*)\}')
    i = 0
    while mask_finder.search(text):
        text = mask_finder.sub(r'{\1[%d]}' % i, text, 1)
        i += 1
    return text

def add_article(noun):
    return 'an %s' % noun if noun[0].lower() in ['a', 'e', 'i', 'o', 'u'] else 'a %s' % noun

def find_all_keys(obj):
    """Finds all tag keys in object

    Parameters
    ----------
    obj : string, tuple, list, or dict
        Object (leaves must be strings, regardless of type)

    Returns
    -------
    set
        Set of all keys (with options)

    """
    strings = get_all_strings(obj)
    ret = set()
    for s in strings:
        f = string.Formatter()
        for x in f.parse(s):
            r = x[1] if not x[2] else '%s:%s' % (x[1], x[2])
            ret.add(r)
    return set([x for x in ret if x])

def get_mask_index(obj):
    """Find all masked strings in obj and index them by mask id

    Parameters
    ----------
    obj : string, tuple, list, or dict
        Object (leaves must be strings, regardless of type)

    Returns
    -------
    tuple(dict, dict)
        First dict is a map from mask id to list of strings
        Second dict is a map from mask id to options

    """
    strings = get_all_strings(obj)
    # ?: after parenthesis makes group non-capturing
    mask_finder = re.compile(r'\{(?:[^\}]*:)?mask\d*\}')
    mask_rep = re.compile(r'[\{\}]')
    find_options = re.compile(r'.*:')
    ret = collections.defaultdict(lambda: [])
    options = collections.defaultdict(lambda: '')
    for s in strings:
        masks = mask_finder.findall(s)
        nooptions = [mask_rep.sub('', find_options.sub('', x)) for x in masks]
        ops = [find_options.search(mask_rep.sub('', x)) for x in masks]
        ops = [x.group().strip(':') for x in ops if x]
        if len(set(nooptions)) > 1:
            raise Exception('Can only have one mask index per template string')
        if nooptions:
            ret[nooptions[0]].append(s)
            options[nooptions[0]] += ''.join(ops)
    return ret, options

def get_all_strings(obj):
    """Returns all strings in obj

    Parameters
    ----------
    obj : string, tuple, list, or dict
        Object (leaves must be strings, regardless of type)

    Returns
    -------
    set
        All strings in obj leaves.

    """
    ret = set()
    if type(obj) in [str, bytes]:
        ret.add(obj)
    elif type(obj) in [tuple, list, dict]:
        if type(obj) == dict:
            obj = obj.values()
        k = [get_all_strings(x) for x in obj]
        k = [x for x in k if x]
        for x in k:
            ret = ret.union(x)
    return set([x for x in ret if x])

def get_all_strings_ordered(obj):
    ret = list()
    if type(obj) in [str, bytes]:
        ret.append(obj)
    elif type(obj) in [tuple, list, dict]:
        if type(obj) == dict:
            obj = obj.values()
        k = [get_all_strings(x) for x in obj]
        for x in k:
            ret += x
    return [x for x in ret if x]

def wrapped_random_choice(x, *args, **kwargs):
    try:
        return np.random.choice(x, *args, **kwargs)
    except:
        idxs = np.random.choice(len(x), *args, **kwargs)
        return type(x)([x[i] for i in idxs])

class Editor(object):
    def __init__(self, language='english', model_name=None):
        self.lexicons = {}
        self.data = {}
        self.tg_params = {
            'language': language,
        }
        if model_name is not None:
            self.tg_params['model_name'] = model_name
        self._load_lexicons(language)
        self.selected_suggestions = []

    def _load_lexicons(self, language):
        cur_folder = os.path.dirname(__file__)
        folder = os.path.abspath(os.path.join(cur_folder, "data", 'lexicons'))
        for f in os.listdir(folder):
            self.lexicons.update(json.load(open(os.path.join(folder, f))))
        self.data['names'] = json.load(open(os.path.join(cur_folder, 'data', 'names.json')))
        self.data['names'] = {x:set(self.data['names'][x]) for x in self.data['names']}
        make_munch = lambda x: munch.Munch(x) if type(x) == dict else x
        for x in self.lexicons:
            self.lexicons[x] = [make_munch(x) for x in self.lexicons[x]]

        language = get_language_code(language)
        wikidata = pickle.load(open(os.path.join(cur_folder, 'data', 'wikidata.pkl'), 'rb'))
        get_ln = lambda d: d.get(language, d.get('en'))
        self.lexicons['male'] = get_ln(wikidata.mnames)
        self.lexicons['female'] = get_ln(wikidata.fnames)
        self.lexicons['first_name'] = [y for x in zip(self.lexicons['male'], self.lexicons['female']) for y in x]
        self.lexicons['last_name'] = get_ln(wikidata.lnames)
        self.lexicons['country'] =  [get_ln(x.label) for x in wikidata.countries]
        # united states by default
        self.lexicons['city'] =  [get_ln(x.label) for x in wikidata.countries[2].cities]
        # Most populous country that has language as official language
        for country in wikidata.countries:
            if country.primary_lang == language:
                self.lexicons['city'] = [get_ln(x.label) for x in country.cities]
                break
        self.lexicons['country_city'] = munch.Munch()
        for country in wikidata.countries:
            l = country.label.en.replace(' ', '_')
            self.lexicons['country_city'][l] = [get_ln(x.label) for x in country.cities]
        self.lexicons['male_from'] = wikidata.male_by_country
        self.lexicons['female_from'] = wikidata.female_by_country
        self.lexicons['last_from'] = wikidata.last_by_country
        self.lexicons = munch.Munch(self.lexicons)



    def __getattr__(self, attr):
        if attr == 'tg':
            from .text_generation import TextGenerator
            params = multilingual_params(**self.tg_params)
            self.tg = TextGenerator(**params)
            return self.tg
        else:
            raise AttributeError

    def suggest_replace(self, text, word, full_sentences=False, words_and_sentences=False, **kwargs):
        """Masked language model suggestion for replacing word in sentence

        Parameters
        ----------
        text : str
            context
        word : str
            word to be replaced
        full_sentences : bool
            If True, returns full sentences with replaced suggestions
        words_and_sentences : bool
            If True, returns tuples of (replacement word, full_sentence)

        Returns
        -------
        list
            Default: list of strings, suggestions for replacements
            If full_sentences or words_and_sentences: see documentation above.

        """
        ret = self.tg.replace_word(text, word, **kwargs)
        if kwargs.get('verbose', False):
            print('\n'.join(['%6s %s' % ('%.2f' % x[2], x[1]) for x in ret[:5]]))
        if words_and_sentences:
            return [(tuple(x[0]), x[1]) if len(x[0]) > 1 else (x[0][0], x[1]) for x in ret]
        if full_sentences:
            return [x[1] for x in ret]
        else:
            return [tuple(x[0]) if len(x[0]) > 1 else x[0][0] for x in ret]

    def _wordnet_stuff(self, templates, word, type, threshold=5, depth=3, pos=None, **kwargs):
        texts = self.template(templates, unroll=True, **kwargs).data
        idxs = np.random.choice(len(texts), min(10, len(texts)), replace=False)
        texts = [texts[i] for i in idxs]
        if type != 'related' and any([word not in x for x in texts]):
            raise Exception('word %s must be in all templates' % word)
        fn = {'antonyms': self.tg.antonyms,
         'synonyms': self.tg.synonyms,
         'related': self.tg.related_words,
         'hypernyms': self.tg.more_general,
         'hyponyms': self.tg.more_specific,
        }[type]
        return [x[0][0] for x in fn(texts, word, threshold=threshold, pos=pos, depth=depth)]

    def antonyms(self, templates, word, threshold=5, **kwargs):
        """Find antonyms of word that fit in templates

        Parameters
        ----------
        templates : str, list, tuple, or dict
            On leaves: templates with {tags}, which will be substituted for mapping in **kwargs
        word : str
            Word for which we want antonyms
        threshold : float
            Maximum allowed log likelihood difference between word and antonym in context

        Returns
        -------
        list
            List of antonyms that fit the given templates

        """
        return self._wordnet_stuff(templates, word, 'antonyms', threshold=threshold, **kwargs)

    def synonyms(self, templates, word, threshold=5, **kwargs):
        """Find synonyms of word that fit in templates

        Parameters
        ----------
        templates : str, list, tuple, or dict
            On leaves: templates with {tags}, which will be substituted for mapping in **kwargs
        word : str
            Word for which we want synonyms
        threshold : float
            Maximum allowed log likelihood difference between word and antonym in context

        Returns
        -------
        list
            List of synonyms that fit the given templates

        """
        return self._wordnet_stuff(templates, word, 'synonyms', threshold=threshold, **kwargs)

    def related_words(self, templates, word, threshold=5, **kwargs):
        """Find words that are related to word that fit in templates
        By related words, we mean hyponyms of the word's hypernyms

        Parameters
        ----------
        templates : str, list, tuple, or dict
            On leaves: templates with {tags}, which will be substituted for mapping in **kwargs
        word : str
            Word for which we want related words
        threshold : float
            Maximum allowed log likelihood difference between word and antonym in context

        Returns
        -------
        list
            List of related words that fit the given templates

        """
        return self._wordnet_stuff(templates, word, 'related', threshold=threshold, **kwargs)

    def hypernyms(self, templates, word, threshold=5, **kwargs):
        """Find hypernyms of word that fit in templates

        Parameters
        ----------
        templates : str, list, tuple, or dict
            On leaves: templates with {tags}, which will be substituted for mapping in **kwargs
        word : str
            Word for which we want hypernyms
        threshold : float
            Maximum allowed log likelihood difference between word and antonym in context

        Returns
        -------
        list
            List of hypernyms that fit the given templates

        """
        return self._wordnet_stuff(templates, word, 'hypernyms', threshold=threshold, **kwargs)

    def hyponyms(self, templates, word, threshold=5, **kwargs):
        """Find hyponyms of word that fit in templates

        Parameters
        ----------
        templates : str, list, tuple, or dict
            On leaves: templates with {tags}, which will be substituted for mapping in **kwargs
        word : str
            Word for which we want hyponyms
        threshold : float
            Maximum allowed log likelihood difference between word and antonym in context

        Returns
        -------
        list
            List of hyponyms that fit the given templates

        """
        return self._wordnet_stuff(templates, word, 'hyponyms', threshold=threshold, **kwargs)

    def suggest(self, templates, return_score=False, **kwargs):
        """Suggests fill-ins based on a masked language model

        Parameters
        ----------
        templates : str, list, tuple, or dict
            On leaves: templates with {tags}, which will be substituted for mapping in **kwargs
            Must have at least one {mask}. Cannot have {mask} and {mask1}, but can have multiple {mask}s
        return_score : bool
            If True, returns tuples of (word, score)
        **kwargs : type
            See documentation for function 'template'

        Returns
        -------
        list(str or tuple)
            list of fill-in suggestions, sorted by likelihood
            (with likelihood if return_score=True)

        """
        mask_index, ops = get_mask_index(templates)
        if not mask_index:
            return []
        if len(mask_index) != 1:
            raise Exception('Only one mask index is allowed')
        ret = self.template(templates, **kwargs, mask_only=True)
        xs = [tuple(x[0]) if len(x[0]) > 1 else x[0][0] for x in ret]
        if return_score:
            scores = [x[2] for x in ret]
            xs = list(zip(xs, scores))
        if kwargs.get('verbose', False):
            print('\n'.join(['%6s %s' % ('%.2f' % x[2], x[1]) for x in ret[:5]]))
        return xs

    def _set_selected_suggestions(self, mask_suggests):
        self.selected_suggestions = mask_suggests
        return self.selected_suggestions


    def visual_suggest(self, templates, **kwargs):
        """Spawns a jupyter visualization for masked language model suggestions

        Parameters
        ----------
        templates : str, list, tuple, or dict
            On leaves: templates with {tags}, which will be substituted for mapping in **kwargs
            Must have at least one {mask}. Cannot have {mask} and {mask1}, but can have multiple {mask}s
        **kwargs : type
            See documentation for function 'template'

        Returns
        -------
        TemplateEditor
            visualization. Selected suggestions will be in self.selected_suggestions

        """
        tagged_keys = find_all_keys(templates)
        template_strs = get_all_strings_ordered(templates)
        items = self._get_fillin_items(tagged_keys, max_count=5, **kwargs)

        kwargs["verbose"] = False
        mask_suggests = self.suggest(templates, **kwargs)
        if not mask_suggests:
            raise Exception('No valid suggestions for the given template!')
        self.selected_suggestions = []
        return TemplateEditor(
            template_strs=template_strs,
            tagged_keys=tagged_keys,
            tag_dict=items,
            mask_suggests=mask_suggests[:50],
            format_fn=recursive_format,
            select_suggests_fn=self._set_selected_suggestions,
            tokenizer=self.tg.tokenizer
        )

    def add_lexicon(self, name, values, overwrite=False, append=False, remove_duplicates=False):
        """Add tag to lexicon

        Parameters
        ----------
        name : str
            Tag name.
        values : list(str)
            Tag values.
        overwrite : bool
            If True, replaces tag with the same name if it already exists
        append : bool
            If True, adds values to current lexicon with name
        remove_duplicates: bool
            If append=True and remove_duplicates=True, remove duplicate values
            from lexicon after appending
        """
        # words can be strings, dictionarys, and other objects
        if overwrite == True and append == True:
            raise Exception('Either overwrite or append must be False')
        if append == True:
            if name not in self.lexicons:
                self.lexicons[name] = values
            else:
                self.lexicons[name].extend(values)
            if remove_duplicates == True:
                self.lexicons[name] = list(set(self.lexicons[name]))
            return
        if name in self.lexicons and not overwrite:
            raise Exception('%s already in lexicons. Call with overwrite=True to overwrite' % name)
        self.lexicons[name] = values

    def _get_fillin_items(self, all_keys, max_count=None, **kwargs):
        items = {}
        mask_match = re.compile(r'mask\d*')
        for k in kwargs:
            if re.search(r'\d+$', k):
                raise(Exception('Error: keys cannot end in integers, we use that to index multiple copies of the same key (offending key: "%s")' % k))
        for k in all_keys:
            # TODO: process if ends in number
            # TODO: process if is a:key to add article
            k = re.sub(r'\..*', '', k)
            k = re.sub(r'\[.*\]', '', k)
            k = re.sub(r'.*?:', '', k)
            newk = re.sub(r'\d+$', '', k)
            if mask_match.match(k):
                continue
            if newk in kwargs:
                items[k] = kwargs[newk]
            elif newk in self.lexicons:
                items[k] = self.lexicons[newk]
            else:
                raise(Exception('Error: key "%s" not in items or lexicons' % newk))
            if max_count:
                items[k] = items[k][:max_count]
        return items

    def template(self, templates, nsamples=None,
                 product=True, remove_duplicates=False, mask_only=False,
                 unroll=False, labels=None, meta=False,  save=False, **kwargs):
        """Fills in templates

        Parameters
        ----------
        templates : str, list, tuple, or dict
            On leaves: templates with {tags}, which will be substituted for mapping in **kwargs
            Can have {mask} tags, which will be replaced by a masked language model.
            Other tags can be numbered for distinction, e.g. {person} and {person1} will be considered
            separate tags, but both will use fill-ins for 'person'
        nsamples : int
            Number of samples
        product : bool
            If true, take cartesian product
        remove_duplicates : bool
            If True, will not generate any strings where two or more fill-in values are duplicates.
        mask_only : bool
            If True, return only fill-in values for {mask} tokens
        unroll : bool
            If True, returns list of strings regardless of template type (i.e. unrolls)
        labels : int or object with strings on leaves
            If int, all generated strings will have the same label. Otherwise, can refer
            to tags, or be strings, etc. Output will be in ret.meta
        meta : bool
            If True, ret.meta will contain a dict of fill in values for each item in ret.data
        save : bool
            If True, ret.templates will contain all parameters and fill-in lists
        **kwargs : type
            Must include fill-in lists for every tag not in editor.lexicons

        Returns
        -------
        MunchWithAdd
            Returns ret, a glorified dict, which will have the filled in templates in ret.data.
            It may contain ret.labels, ret.templates and ret.meta (depending on parameters as noted above)
            You can add or += two MunchWithAdd, which will concatenate values

        """

    # 1. go through object, find every attribute inside brackets
    # 2. check if they are in kwargs and self.attributes
    # 3. generate keys and vals
    # 4. go through object, generate
        params = locals()
        ret = MunchWithAdd()
        del params['kwargs']
        del params['self']
        templates = copy.deepcopy(templates)
        added_labels = False
        if labels is not None and type(labels) != int:
            added_labels = True
            templates = (templates, labels)
        all_keys = find_all_keys(templates)
        items = self._get_fillin_items(all_keys, **kwargs)
        mask_index, mask_options = get_mask_index(templates)

        for mask, strings in mask_index.items():
            # ks = {re.sub(r'.*?:', '', a): '{%s}' % a for a in all_keys}
            ks = {}
            tok = 'VERYLONGTOKENTHATWILLNOTEXISTEVER'
            ks[mask] = tok
            a_tok = 'thisisaratherlongtokenthatwillnotexist'
            # print(mask)
            # print('options:', mask_options[mask])
            top = 100
            find_top = re.search(r't(\d+)', mask_options[mask])
            if find_top:
                top = int(find_top.group(1))
            sub_a = lambda x: re.sub(r'{[^:}]*a[^:}]*:(%s)}' % mask, r'{%s} {\1}' % a_tok, x)
            # print(strings)
            strings = recursive_apply(strings, sub_a)
            ks[a_tok] = '{%s}' % a_tok
            # print(strings)
            ts = recursive_format(strings, ks, ignore_missing=True)
            np.random.seed(1)
            samp = self.template(ts, nsamples=5, remove_duplicates=remove_duplicates,
                                 thisisaratherlongtokenthatwillnotexist=['a'], **kwargs).data
            samp += self.template(ts, nsamples=5, remove_duplicates=remove_duplicates,
                                 thisisaratherlongtokenthatwillnotexist=['an'], **kwargs).data
            # print(samp)
            # print(len([x for x in samp if ' an ' in x[0]]))
            samp = [x.replace(tok, self.tg.tokenizer.mask_token) for y in samp for x in y][:20]
            samp = list(set(samp))
            # print(samp)
            if 'beam_size' not in kwargs:
                kwargs['beam_size'] = 100
            # beam_size = kwargs.get('beam_size', 100)
            # kwargs.
            options = self.tg.unmask_multiple(samp, **kwargs)
            # print(options)
            # print(top)
            v = [x[0] for x in options][:top]
            items[mask] = v
            if mask_only:
                return options[:nsamples]
        if save:
            ret.templates = [(params, items)]
        templates = recursive_apply(templates, replace_mask)
        # print(templates)
        keys = [x[0] for x in items.items()]
        vals = [[x[1]] if type(x[1]) not in [list, tuple] else x[1] for x in items.items()]
        if nsamples is not None:
            # v = [np.random.choice(x, nsamples) for x in vals]
            v = [wrapped_random_choice(x, nsamples) for x in vals]
            if not v:
                vals = [[]]
            else:
                vals = zip(*v)
            # print(list(vals))
        else:
            if not product:
                vals = zip(*vals)
            else:
                vals = itertools.product(*vals)
        data = []
        use_meta = meta
        meta = []
        for v in vals:
            # print(v)
            if remove_duplicates and len(v) != len(set([str(x) for x in v])):
                continue
            mapping = dict(zip(keys, v))
            # print(templates)
            # print(mapping)
            data.append(recursive_format(templates, mapping))
            meta.append(mapping)
        if unroll and data and type(data[0]) in [list, np.array, np.ndarray, tuple]:
            meta = [z for y, z in zip(data, meta) for x in y]
            data = [x for y in data for x in y]
        if use_meta:
            ret.meta = meta
        if added_labels:
            data, labels = map(list, zip(*data))
            ret.labels = labels
        if labels is not None and type(labels) == int:
            ret.labels = [labels for _ in range(len(data))]
        ret.data = data
        return ret
