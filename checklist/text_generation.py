from transformers import AutoTokenizer, AutoModelForMaskedLM
import collections
import itertools
import numpy as np
import re
from transformers import GPT2Config
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from tqdm.auto import tqdm
import torch
import torch.nn.functional as F
from pattern.en import wordnet, pluralize
import requests
import json

def all_synsets(word, pos=None):
    map = {
        'NOUN': wordnet.NOUN,
        'VERB': wordnet.VERB,
        'ADJ': wordnet.ADJECTIVE,
        'ADV': wordnet.ADVERB
        }
    if pos is None:
        pos_list = [wordnet.VERB, wordnet.ADJECTIVE, wordnet.NOUN, wordnet.ADVERB]
    else:
        pos_list = [map[pos]]
    ret = []
    for pos in pos_list:
        ret.extend(wordnet.synsets(word, pos=pos))
    return ret

def clean_senses(synsets):
    return [x for x in set(synsets) if '_' not in x]
def all_possible_synonyms(word, pos=None):
    ret = []
    for syn in all_synsets(word, pos=pos):
        # if syn.synonyms[0] != word:
        #     continue
        ret.extend(syn.senses)
    return clean_senses(ret)

def all_possible_antonyms(word, pos=None):
    ret = []
    for syn in all_synsets(word, pos=pos):
        if not syn.antonym:
            continue
        for s in syn.antonym:
            ret.extend(s.senses)
    return clean_senses(ret)

def all_possible_hypernyms(word, pos=None, depth=None):
    ret = []
    for syn in all_synsets(word, pos=pos):
        ret.extend([y for x in syn.hypernyms(recursive=True, depth=depth) for y in x.senses])
    return clean_senses(ret)
def all_possible_hyponyms(word, pos=None, depth=None):
    ret = []
    for syn in all_synsets(word, pos=pos):
        ret.extend([y for x in syn.hyponyms(recursive=True, depth=depth) for y in x.senses])
    return clean_senses(ret)
def all_possible_related(words, pos=None, depth=1):
    all_syns = [y for word in words for y in all_synsets(word, pos=pos)]
    # all_syns = [all_synsets(x, pos=pos) for x in words]
    # all_syns = [x[0] for x in all_syns if x]
    # return all_syns
    # print(all_syns)
    all_ancestors = [wordnet.ancestor(s1, s2) for s1, s2 in itertools.combinations(all_syns, 2)]
    all_ancestors = [x for x in all_ancestors if x]
    # print(all_ancestors)
    mapz = {x.lexname: x for x in all_ancestors}
    all_ancestors = list(mapz.values())
    all_descendents = [y for x in all_ancestors for y in x.hyponyms(recursive=True, depth=depth)]
    ret = [y for x in all_descendents for y in x.senses]
    return clean_senses(ret)

class TextGenerator(object):
    def __init__(self, url=None, model_name='roberta-base', prefix_sentence='', allow_word_pieces=False, **kwargs):
        self.url = url
        if url is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            # self.tokenizer = BertTokenizer.from_pretrained('bert-base-cased')
            # self.model = BertForMaskedLM.from_pretrained('bert-base-cased')
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForMaskedLM.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            self.prefix_sentence = prefix_sentence
            self.prefix_len = len(self.tokenizer.encode(prefix_sentence, add_special_tokens=False))
            self.allow_word_pieces = allow_word_pieces
            tmp = self.tokenizer.tokenize(' a')[0].split('a')
            assert len(tmp) == 2
            assert tmp[1] == ''
            self.space_prefix = tmp[0]
            if not self.allow_word_pieces:
                self.with_space = torch.tensor(np.array(list(set([i for x, i in self.tokenizer.get_vocab().items() if x.startswith(self.space_prefix)]))), device=self.device);
                self.with_space_set = set(self.with_space.cpu().numpy())
                self.special_chars = set([i for x, i in self.tokenizer.get_vocab().items() if not x.strip(self.space_prefix).isalnum()])

    def unmask_multiple(self, texts, beam_size=500, candidates=None, metric='avg', **kwargs):
        rets = []
        for text in texts:
            rets.append(self.unmask(text, beam_size, candidates))
        scores = collections.defaultdict(lambda: 0.) if metric == 'avg' else collections.defaultdict(lambda: 999999999)
        count = collections.defaultdict(lambda: 0.)
        examples = {}
        longest = max([len(x[0][0]) for x in rets])
        rets = sorted(rets, key=lambda x:len(x[0][0]), reverse=True)
        for r in rets:
            for x in r:
                tup = tuple(x[0])
                if len(tup) != longest:
                    tups = [k for k in scores if tuple(k[:len(tup)]) == tup]
                else:
                    tups = [tup]
                for tup in tups:
                    count[tup] += 1
                    examples[tup] = x[1]
                    if metric == 'avg':
                        scores[tup] += x[-1]
                    elif metric == 'min':
                        scores[tup] = min(scores[tup], x[-1])
        if metric == 'min':
            for x in count:
                # print(x, count[x])
                if count[x] != len(texts):
                    scores[x] = -999999
        else:
            for x in scores:
                scores[x] = scores[x] / len(texts)
        scores = sorted(scores.items(), key=lambda x:x[1], reverse=True)
        return [(list(x[0]), examples[x[0]], x[1]) for x in scores]



    def unmask(self, text_with_mask, beam_size=10, candidates=None):
        if self.url is not None:
            params = {'text': text_with_mask, 'beam_size': beam_size, 'candidates': candidates}
            r = requests.post(url='%s/unmask' % self.url, data={'params': json.dumps(params)})
            r = [tuple(x) for x in json.loads(r.text)]
            return r
        tokenizer = self.tokenizer
        model = self.model
        encoded = np.array(tokenizer.encode(self.prefix_sentence + text_with_mask, add_special_tokens=True))
        cands = []
        if candidates is not None:
            candidates = candidates + [self.space_prefix + x for x in candidates]
            cands = tokenizer.convert_tokens_to_ids(candidates)
            if self.allow_word_pieces:
                cands_with_space = list(set(cands))
            else:
                cands_with_space = list(set(cands).intersection(self.with_space_set))
            if not len(cands_with_space):
                return []
        input_ids = torch.tensor(encoded)
        # toks = tokenizer.tokenize('[CLS] %s [SEP]' % string)
        current_beam= [([], 0)]
        masked = (input_ids == self.tokenizer.mask_token_id).numpy().nonzero()[0]
        # print(masked)
        while len(current_beam[0][0]) != masked.shape[0]:
            current_beam = current_beam[:beam_size]
            size = len(current_beam[0][0])
            to_pred = []
            new_beam = []
            for i, current in enumerate(current_beam):
                idxs = current[0]
                c = encoded.copy()
                c[masked[:len(idxs)]] = idxs
                to_pred.append(c)
            # print('ae')
            # print('\n'.join([tokenizer.decode(x) for x in to_pred]))
            # print()
            to_pred = torch.tensor(to_pred, device=self.device).to(torch.int64)
            with torch.no_grad():
                outputs = model(to_pred)[0]
            for i, current in enumerate(current_beam):
                prev = int(to_pred[i][masked[size] - 1])
                forbid = False
                # allow tokens that don't start with space if previous is not alphanumeric
                if not self.allow_word_pieces and prev not in self.special_chars:
                    forbid = True
                    # print('Forbid Prev, current', prev,  tokenizer.decode(to_pred[i][masked[size] - 1:masked[size]+1]))
                if candidates is not None:
                    cands_to_use = cands_with_space if forbid else cands
                    scores = [outputs[i, masked[size], j] for j in cands_to_use]
                    new = [(current[0] + [int(x[0])], float(x[1]) + current[1]) for x in zip(cands_to_use, scores)]
                else:
                    if forbid:
                        v, top_preds = torch.topk(outputs[i, masked[size], self.with_space.to(torch.int64)], beam_size + 10)
                        top_preds = self.with_space[top_preds]
                    else:
                        v, top_preds = torch.topk(outputs[i, masked[size]], beam_size + 10)
                    new = [(current[0] + [int(x[0])], float(x[1]) + current[1]) for x in zip(top_preds, v)]
                new_beam.extend(new)
            current_beam = sorted(new_beam, key=lambda x:x[1], reverse=True)
        ret = []
        ret_text = []
        cop = encoded.copy()
        for idxs, score in current_beam:
            # words = tokenizer.convert_ids_to_tokens(idxs)
            words = [str(tokenizer.decode([i])).strip() for i in idxs]
            cop[masked] = idxs
            text = tokenizer.decode(cop[1 + self.prefix_len:-1])
            ret.append((words, text, score / masked.shape[0]))
        ret = sorted(ret, key=lambda x:x[2], reverse=True)
        return ret
    def fill_in_between(self, pieces, beam_size=10, candidates=None):
        text = ''
        for p in pieces[:-1]:
            text += p
            text += ' ' + self.tokenizer.mask_token
            if p != '':
                text += ' '
        text += pieces[-1]
        if pieces[-1] == '':
            text = text.rstrip()
        return self.unmask(text, beam_size=beam_size, candidates=candidates)

    def replace_word(self, text, word,  threshold=5, beam_size=100, candidates=None):
        masked = re.sub(r'\b%s\b' % re.escape(word), self.tokenizer.mask_token, text)
        if masked == text:
            return []
        if candidates is not None:
            candidates = [word] + candidates
        ret =  self.unmask(masked, beam_size=beam_size, candidates=candidates)
        non_word = [x for x in ret if np.all([y not in [self.tokenizer.unk_token, word] for y in x[0]])]
        score = [x for x in ret if np.all([y in [word, self.tokenizer.unk_token] for y in x[0]])]
        if not score:
            score = 0
        else:
            score = score[0][-1]
        escaped = re.escape(word)
        # new_ret = [(x[0], x[1], score - x[2]) for x in non_word if score - x[2] < threshold]
        try:
            new_ret = [(x[0], re.sub(r'\b%s\b' % escaped, x[0][0], text), score - x[2]) for x in non_word if score - x[2] < threshold]
        except:
            new_ret = [(x[0], x[1], score - x[2]) for x in non_word if score - x[2] < threshold]
        return new_ret

    def more_general(self, texts, word, threshold=5, pos=None, **kwargs):
        options = all_possible_hypernyms(word, pos=pos)
        # print(options)
        return self.filter_options(texts, word, options, threshold)
    def more_specific(self, texts, word, threshold=5, depth=3, pos=None, **kwargs):
        options = all_possible_hyponyms(word, depth=depth, pos=pos)
        return self.filter_options(texts, word, options, threshold)
    def related_words(self, texts, words, threshold=5, depth=3, pos=None, **kwargs):
        if type(words) != list:
            words = [words]
        if len(words) == 1:
            options = all_possible_hypernyms(words[0], pos=pos)
            ancestors = [x[0][0] for x in self.filter_options(texts, words[0], options, threshold)]
            # print(ancestors)
            options = list(set([y for x in ancestors for y in all_possible_hyponyms(x, depth=depth)]))
        else:
            options = all_possible_related(words, depth=depth)
        return self.filter_options(texts, words[0], options, threshold)
    def antonyms(self, texts, word, threshold=5, pos=None, **kwargs):
        options = all_possible_antonyms(word, pos=pos)
        return self.filter_options(texts, word, options, threshold)
    def synonyms(self, texts, word, threshold=5, pos=None, **kwargs):
        options = all_possible_synonyms(word, pos=pos)
        # print(options)
        return self.filter_options(texts, word, options, threshold)

    def filter_options(self, texts, word, options, threshold=5):
        # print(options)
        if type(texts) != list:
            texts = [texts]
        options = options + [word]
        in_all = set(options)
        orig_ret = []
        for text in texts:
            masked = re.sub(r'\b%s\b' % re.escape(word), self.tokenizer.mask_token, text)
            if masked == text:
                continue
            ret =  self.unmask(masked, beam_size=100, candidates=options)
            if not ret:
                in_all = in_all.intersection(set())
                continue
            non_word = [x for x in ret if np.all([y not in [self.tokenizer.unk_token, word] for y in x[0]])]
            score = [x for x in ret if np.all([y in [word, self.tokenizer.unk_token] for y in x[0]])][0][-1]
            new_ret = [(x[0], x[1], score - x[2]) for x in non_word if score - x[2] < threshold]
            # print(text)
            # print(new_ret)
            # print()
            if text == texts[0]:
                orig_ret = new_ret
            in_all = in_all.intersection(set([x[0][0] for x in new_ret]))
        return [x for x in orig_ret if x[0][0] in in_all]

    def antonym(self, text, word, threshold=5, synonym=False):
        options = all_possible_antonyms(word)
        print(options)
        if synonym:
            options = all_possible_synonyms(word)
        if not options:
            return []
        options = options + [word]
        masked = re.sub(r'\b%s\b' % re.escape(word), '[MASK]', text)
        if masked == text:
            return []
        ret =  self.unmask(masked, beam_size=100000000, candidates=options)
        non_word = [x for x in ret if np.all([y not in [self.tokenizer.unk_token, word] for y in x[0]])]
        score = [x for x in ret if np.all([y in [word, self.tokenizer.unk_token] for y in x[0]])][0][-1]
        new_ret = [(x[0], x[1], score - x[2]) for x in non_word if score - x[2] < threshold]
        return new_ret
    def try_all_antonyms(self, text, threshold=5, synonym=False):
        if self.url is not None:
            params = {'text': text }
            r = requests.post(url='%s/tokenize' % self.url, data={'params': json.dumps(params)})
            words = json.loads(r.text)
        else:
            words = self.tokenizer.tokenize(text)
        new_ret = []
        for word in words:
            word = word.strip(self.space_prefix)
            try:
                if synonym:
                    ret = self.synonyms(text, word, threshold)
                else:
                    ret = self.antonyms(text, word, threshold)
            except:
                print('Error', word)
                print()
                continue
            new_ret.extend(ret)
        return sorted(new_ret, key=lambda x:x[2])
