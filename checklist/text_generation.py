from transformers import BertTokenizer, BertForMaskedLM, RobertaTokenizer, RobertaForMaskedLM
import collections
import itertools
import numpy as np
import re
from transformers import GPT2Config
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from tqdm.auto import tqdm
import torch
import torch.nn.functional as F
# from pattern.en import wordnet, pluralize
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
    def __init__(self, nlp=None, url=None):
        self.url = url
        if url is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.nlp = nlp
            # self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-cased')
            # self.bert = BertForMaskedLM.from_pretrained('bert-base-cased')
            self.bert_tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
            self.bert = RobertaForMaskedLM.from_pretrained('roberta-base')
            self.bert.to(self.device)
            self.bert.eval()
        # self.gpt_tokenizer = GPT2Tokenizer.from_pretrained('gpt2-large')
        # self.gpt = GPT2LMHeadModel.from_pretrained('gpt2-large')
        # self.gpt.to(self.device)
        # self.gpt.eval()

    def unmask_multiple(self, texts, beam_size=10, candidates=None, metric='avg'):
        rets = []
        for text in texts:
            rets.append(self.unmask(text, beam_size, candidates))
        scores = collections.defaultdict(lambda: 0.) if metric == 'avg' else collections.defaultdict(lambda: 999999999)
        count = collections.defaultdict(lambda: 0.)
        examples = {}
        for r in rets:
            for x in r:
                count[tuple(x[0])] += 1
                examples[tuple(x[0])] = x[1]
                if metric == 'avg':
                    scores[tuple(x[0])] += x[-1]
                elif metric == 'min':
                    scores[tuple(x[0])] = min(scores[tuple(x[0])], x[-1])
        if metric == 'min':
            for x in count:
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
        tokenizer = self.bert_tokenizer
        model = self.bert
        encoded = np.array(tokenizer.encode(text_with_mask, add_special_tokens=True))
        cands = []
        if candidates is not None:
            cands = tokenizer.convert_tokens_to_ids(candidates)
        input_ids = torch.tensor(encoded)
        # toks = tokenizer.tokenize('[CLS] %s [SEP]' % string)
        current_beam= [([], 0)]
        masked = (input_ids == tokenizer.mask_token_id).numpy().nonzero()[0]
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
            to_pred = torch.tensor(to_pred, device=self.device)
            with torch.no_grad():
                outputs = model(to_pred)[0]
            for i, current in enumerate(current_beam):
                if candidates is not None:
                    scores = [outputs[i, masked[size], j] for j in cands]
                    new = [(current[0] + [int(x[0])], float(x[1]) + current[1]) for x in zip(cands, scores)]
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
            words = [tokenizer.decode([i]).strip() for i in idxs]
            cop[masked] = idxs
            text = tokenizer.decode(cop[1:-1])
            ret.append((words, text, score / masked.shape[0]))
        ret = sorted(ret, key=lambda x:x[2], reverse=True)
        return ret
    def fill_in_between(self, pieces, beam_size=10, candidates=None):
        text = ''
        for p in pieces[:-1]:
            text += p
            text += ' [MASK]'
            if p != '':
                text += ' '
        text += pieces[-1]
        if pieces[-1] == '':
            text = text.rstrip()
        return self.unmask(text, beam_size=beam_size, candidates=candidates)

    def replace_word(self, text, word,  threshold=5, beam_size=100, candidates=None):
        masked = re.sub(r'\b%s\b' % re.escape(word), '[MASK]', text)
        if masked == text:
            return []
        if candidates is not None:
            candidates = [word] + candidates
        ret =  self.unmask(masked, beam_size=beam_size, candidates=candidates)
        non_word = [x for x in ret if np.all([y not in ['[UNK]', word] for y in x[0]])]
        score = [x for x in ret if np.all([y in [word, '[UNK]'] for y in x[0]])]
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

    def more_general(self, texts, word, threshold=5, pos=None):
        options = all_possible_hypernyms(word, pos=pos)
        return self.filter_options(texts, word, options, threshold)
    def more_specific(self, texts, word, threshold=5, depth=3, pos=None):
        options = all_possible_hyponyms(word, depth=depth, pos=pos)
        return self.filter_options(texts, word, options, threshold)
    def related_words(self, texts, words, threshold=5, depth=3, pos=None):
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
    def antonyms(self, texts, word, threshold=5, pos=None):
        options = all_possible_antonyms(word, pos=pos)
        print(options)
        return self.filter_options(texts, word, options, threshold)
    def synonyms(self, texts, word, threshold=5, pos=None):
        options = all_possible_synonyms(word, pos=pos)
        print(options)
        return self.filter_options(texts, word, options, threshold)

    def filter_options(self, texts, word, options, threshold=5):
        if type(texts) != list:
            texts = [texts]
        options = options + [word]
        in_all = set(options)
        for text in texts:
            masked = re.sub(r'\b%s\b' % re.escape(word), '[MASK]', text)
            if masked == text:
                continue
            ret =  self.unmask(masked, beam_size=100000000, candidates=options)
            non_word = [x for x in ret if np.all([y not in ['[UNK]', word] for y in x[0]])]
            score = [x for x in ret if np.all([y in [word, '[UNK]'] for y in x[0]])][0][-1]
            new_ret = [(x[0], x[1], score - x[2]) for x in non_word if score - x[2] < threshold]
            if text == texts[0]:
                orig_ret = new_ret
            break
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
        non_word = [x for x in ret if np.all([y not in ['[UNK]', word] for y in x[0]])]
        score = [x for x in ret if np.all([y in [word, '[UNK]'] for y in x[0]])][0][-1]
        new_ret = [(x[0], x[1], score - x[2]) for x in non_word if score - x[2] < threshold]
        return new_ret
    def try_all_antonyms(self, text, threshold=5, synonym=False):
        if self.url is not None:
            params = {'text': text }
            r = requests.post(url='%s/tokenize' % self.url, data={'params': json.dumps(params)})
            words = json.loads(r.text)
        else:
            words = self.bert_tokenizer.tokenize(text)
        new_ret = []
        for word in words:
            try:
                ret = self.antonym(text, word, threshold, synonym=synonym)
            except:
                print('Error', word)
                print()
                continue
            new_ret.extend(ret)
        return sorted(new_ret, key=lambda x:x[2])

    def finish_sentence(self, start):
        context_tokens = self.gpt_tokenizer.encode(start)
        stoppers = set(self.gpt_tokenizer.convert_tokens_to_ids(['?"', '?\'', '!"', '."', '.)', '.\'', '.', '?', '!', '\n', '\n\n', self.gpt_tokenizer.eos_token]))
        top_k= 0
        temperature = 1
        out = sample_sequence(
            model=self.gpt,
            context=context_tokens,
            length=50,
            temperature=temperature,
            top_k=top_k,
            top_p=1,
            device=self.device,
            is_xlnet=False,#bool(model_type == "xlnet"),
            stoppers=stoppers
            )
        # out = out[0, len(context_tokens):].tolist()
        text = self.gpt_tokenizer.decode(out[0].tolist(), clean_up_tokenization_spaces=True)
        return text





def top_k_top_p_filtering(logits, top_k=0, top_p=0.0, filter_value=-float('Inf')):
    """ Filter a distribution of logits using top-k and/or nucleus (top-p) filtering
        Args:
            logits: logits distribution shape (vocabulary size)
            top_k > 0: keep only top k tokens with highest probability (top-k filtering).
            top_p > 0.0: keep the top tokens with cumulative probability >= top_p (nucleus filtering).
                Nucleus filtering is described in Holtzman et al. (http://arxiv.org/abs/1904.09751)
        From: https://gist.github.com/thomwolf/1a5a29f6962089e871b94cbd09daf317
    """
    assert logits.dim() == 1  # batch size 1 for now - could be updated for more but the code would be less clear
    top_k = min(top_k, logits.size(-1))  # Safety check
    if top_k > 0:
        # Remove all tokens with a probability less than the last token of the top-k
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value

    if top_p > 0.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = cumulative_probs > top_p
        # Shift the indices to the right to keep also the first token above the threshold
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0

        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value
    return logits

def sample_sequence(model, length, context, num_samples=1, temperature=1, top_k=0, top_p=0.0, is_xlnet=False, device='cpu',
                   stoppers=[]):
    context = torch.tensor(context, dtype=torch.long, device=device)
    context = context.unsqueeze(0).repeat(num_samples, 1)
    generated = context
    with torch.no_grad():
        for _ in range(length):
            inputs = {'input_ids': generated}
            # if is_xlnet:
            #     # XLNet is a direct (predict same token, not next token) and bi-directional model by default
            #     # => need one additional dummy token in the input (will be masked), attention mask and target mapping (see model docstring)
            #     input_ids = torch.cat((generated, torch.zeros((1, 1), dtype=torch.long, device=device)), dim=1)
            #     perm_mask = torch.zeros((1, input_ids.shape[1], input_ids.shape[1]), dtype=torch.float, device=device)
            #     perm_mask[:, :, -1] = 1.0  # Previous tokens don't see last token
            #     target_mapping = torch.zeros((1, 1, input_ids.shape[1]), dtype=torch.float, device=device)
            #     target_mapping[0, 0, -1] = 1.0  # predict last token
            #     inputs = {'input_ids': input_ids, 'perm_mask': perm_mask, 'target_mapping': target_mapping}
            outputs = model(**inputs)  # Note: we could also use 'past' with GPT-2/Transfo-XL/XLNet (cached hidden-states)
            next_token_logits = outputs[0][0, -1, :] / temperature
            filtered_logits = top_k_top_p_filtering(next_token_logits, top_k=top_k, top_p=top_p)
            next_token = torch.multinomial(F.softmax(filtered_logits, dim=-1), num_samples=1)
            nt = int(next_token[0])
            generated = torch.cat((generated, next_token.unsqueeze(0)), dim=1)
            if nt in stoppers:
                break
#             print(nt, nt in stoppers, int(next_token[0]))
    return generated
