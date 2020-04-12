import collections
import itertools
import string
import numpy as np
import re
import copy
import os
import json
import munch

from .viewer import TemplateEditor

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

def replace_bert(obj):
    bert_finder = re.compile(r'\{((?:[^\}]*:)?bert\d*)\}')
    # bert_finder = re.compile(r'\{(bert\d*)\}')
    i = 0
    while bert_finder.search(obj):
        obj = bert_finder.sub(r'{\1[%d]}' % i, obj, 1)
        i += 1
    return obj

def add_article(noun):
    return 'an %s' % noun if noun[0].lower() in ['a', 'e', 'i', 'o', 'u'] else 'a %s' % noun

def find_all_keys(obj):
    strings = get_all_strings(obj)
    ret = set()
    for s in strings:
        f = string.Formatter()
        for x in f.parse(s):
            r = x[1] if not x[2] else '%s:%s' % (x[1], x[2])
            ret.add(r)
    return set([x for x in ret if x])

def get_bert_index(obj):
    strings = get_all_strings(obj)
    # ?: after parenthesis makes group non-capturing
    bert_finder = re.compile(r'\{(?:[^\}]*:)?bert\d*\}')
    bert_rep = re.compile(r'[\{\}]')
    find_options = re.compile(r'.*:')
    ret = collections.defaultdict(lambda: [])
    options = collections.defaultdict(lambda: '')
    for s in strings:
        berts = bert_finder.findall(s)
        nooptions = [bert_rep.sub('', find_options.sub('', x)) for x in berts]
        ops = [find_options.search(bert_rep.sub('', x)) for x in berts]
        ops = [x.group().strip(':') for x in ops if x]
        if len(set(nooptions)) > 1:
            raise Exception('Can only have one bert index per template string')
        if nooptions:
            ret[nooptions[0]].append(s)
            options[nooptions[0]] += ''.join(ops)
    return ret, options

def get_all_strings(obj):
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
    def __init__(self):
        cur_folder = os.path.dirname(__file__)
        folder = os.path.abspath(os.path.join(cur_folder, os.pardir, "data", 'lexicons'))
        self.lexicons = {}
        self.data = {}
        for f in os.listdir(folder):
            self.lexicons.update(json.load(open(os.path.join(folder, f))))
        make_munch = lambda x: munch.Munch(x) if type(x) == dict else x
        for x in self.lexicons:
            self.lexicons[x] = [make_munch(x) for x in self.lexicons[x]]
        self.data['names'] = json.load(open(os.path.join(cur_folder, os.pardir, 'data', 'names.json')))
        self.data['names'] = {x:set(self.data['names'][x]) for x in self.data['names']}

        self.temp_selects = []

    def __getattr__(self, attr):
        if attr == 'tg':
            from .text_generation import TextGenerator
            self.tg = TextGenerator()
            return self.tg
        else:
            raise AttributeError

    def suggest_replace(self, text, word, full_sentences=False, words_and_sentences=False, **kwargs):
        ret = self.tg.replace_word(text, word, **kwargs)
        if kwargs.get('verbose', False):
            print('\n'.join(['%6s %s' % ('%.2f' % x[2], x[1]) for x in ret[:5]]))
        if words_and_sentences:
            return [(tuple(x[0]), x[1]) if len(x[0]) > 1 else (x[0][0], x[1]) for x in ret]
        if full_sentences:
            return [x[1] for x in ret]
        else:
            return [tuple(x[0]) if len(x[0]) > 1 else x[0][0] for x in ret]

    def suggest(self, templates, **kwargs):
        # if replace:
        #     replace_with_bert = lambda x: re.sub(r'\b%s\b'% re.escape(replace), '{bert}', x)
        #     templates = recursive_apply(templates, replace_with_bert)
        bert_index, ops = get_bert_index(templates)
        #print(templates)
        #print(self.template(templates, **kwargs, bert_only=True))
        if not bert_index:
            return []
        if len(bert_index) != 1:
            raise Exception('Only one bert index is allowed')
        ret = self.template(templates, **kwargs, bert_only=True)
        xs = [tuple(x[0]) if len(x[0]) > 1 else x[0][0] for x in ret]
        if kwargs.get('verbose', False):
            print('\n'.join(['%6s %s' % ('%.2f' % x[2], x[1]) for x in ret[:5]]))
        return xs

    def _set_temp_selects(self, bert_suggests):
        self.temp_selects = bert_suggests
        return self.temp_selects


    def visual_suggest(self, templates, **kwargs):
        tagged_keys = find_all_keys(templates)
        template_strs = get_all_strings_ordered(templates)
        items = self._get_fillin_items(tagged_keys, max_count=5, **kwargs)
        kwargs["verbose"] = False
        bert_suggests = self.suggest(templates, **kwargs)

        if not bert_suggests:
            raise Exception('No valid suggestions for the given template!')
        self.temp_selects = []
        return template_strs, tagged_keys, items, bert_suggests
        return TemplateEditor(
            template_strs=template_strs,
            tagged_keys=tagged_keys,
            tag_dict=items,
            bert_suggests=bert_suggests[:50],
            format_fn=recursive_format,
            select_suggests_fn=self._set_temp_selects
        )

    def add_lexicon(self, name, values, overwrite=False):
        # words can be strings, dictionarys, and other objects
        if name in self.lexicons and not overwrite:
            raise Exception('%s already in lexicons. Call with overwrite=True to overwrite' % name)
        self.lexicons[name] = values

    def _get_fillin_items(self, all_keys, max_count=None, **kwargs):
        items = {}
        bert_match = re.compile(r'bert\d*')
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
            if bert_match.match(k):
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

    def template(self, templates, return_meta=False, nsamples=None,
                 product=True, remove_duplicates=False, bert_only=False,
                 unroll=False, save=False, **kwargs):
    # 1. go through object, find every attribute inside brackets
    # 2. check if they are in kwargs and self.attributes
    # 3. generate keys and vals
    # 4. go through object, generate
        templates = copy.deepcopy(templates)
        saved = templates
        all_keys = find_all_keys(templates)
        items = self._get_fillin_items(all_keys, **kwargs)
        bert_index, bert_options = get_bert_index(templates)

        for bert, strings in bert_index.items():
            # ks = {re.sub(r'.*?:', '', a): '{%s}' % a for a in all_keys}
            ks = {}
            tok = 'VERYLONGTOKENTHATWILLNOTEXISTEVER'
            ks[bert] = tok
            a_tok = 'thisisaratherlongtokenthatwillnotexist'
            # print(bert)
            # print('options:', bert_options[bert])
            top = 100
            find_top = re.search(r't(\d+)', bert_options[bert])
            if find_top:
                top = int(find_top.group(1))
            sub_a = lambda x: re.sub(r'{[^:}]*a[^:}]*:(%s)}' % bert, r'{%s} {\1}' % a_tok, x)
            # print(strings)
            strings = recursive_apply(strings, sub_a)
            ks[a_tok] = '{%s}' % a_tok
            # print(strings)
            ts = recursive_format(strings, ks, ignore_missing=True)
            np.random.seed(1)
            samp = self.template(ts, nsamples=10, remove_duplicates=remove_duplicates, # **kwargs)
                                 thisisaratherlongtokenthatwillnotexist=['a', 'an'], **kwargs)
            samp = [x.replace(tok, self.tg.bert_tokenizer.mask_token) for y in samp for x in y][:20]
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
            items[bert] = v
            if bert_only:
                return options
        if save:
            return (saved, items)
        templates = recursive_apply(templates, replace_bert)
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
        ret = []
        ret_maps = []
        for v in vals:
            # print(v)
            if remove_duplicates and len(v) != len(set([str(x) for x in v])):
                continue
            mapping = dict(zip(keys, v))
            # print(templates)
            # print(mapping)
            ret.append(recursive_format(templates, mapping))
            ret_maps.append(mapping)
        if unroll and ret and type(ret[0]) in [list, np.array, tuple]:
            ret = [x for y in ret for x in y]
            ret_maps = [x for y in ret_maps for x in y]
        if return_meta:
            return ret, ret_maps
        return ret
