import re
import munch
from ..perturb import Perturb
from ..editor import recursive_make_munch

def replace_race_fn(editor):
    def replace_race(text, meta=False):
    # document: only replace if there is a single instance
        races = ['white', 'Asian', 'black', 'Hispanic']
        found = re.findall(r'\b(%s)\b' % '|'.join(races), text,  flags=re.I)
        if len(found) != 1:
            return None if not meta else None, None
        found = found[0].lower()
        b = re.sub(r'\b(%s)\b' % '|'.join(races), '{race}', text,  flags=re.I)
        b = re.sub(r'\ban? {race}', '{a:race}', b)
        nraces = [x for x in races if x.lower() != found.lower()]
        t = [(x, race) for x, race in zip(editor.template(b, race=nraces).data, nraces) if x != text]
        if not t:
            return None if not meta else None, None
        if found.lower() not in ['asian', 'hispanic']:
            if not editor.suggest_replace(text, found, candidates=['Hispanic', 'Asian'], threshold=6):
                return None
        t, met = map(list, zip(*t))
        if meta:
            return t, met
        return t
    return replace_race


def add_protected(string, protected,
                  subjects=['man', 'woman', 'child', 'boy', 'girl', 'people',
                            'brother', 'sister'],
                meta=False,
                ignore_case=True):
    return Perturb.add_before(string, subjects, protected, meta, ignore_case)

def replace_protected(string, protected, meta=False, ignore_case=True):
    return Perturb.replace_groups(string, protected, protected, meta, ignore_case)

def provisional_religion_lexicon():
    religion_lexicon=  [
    ('Christianity', 'Christian', 'priest', 'church', 'Bible', ['God', 'Jesus', 'Christ', 'Jesus Christ', 'Paul', 'Mary', 'Peter', 'John']),
    ('Protestantism', 'Protestant', 'pastor', 'church', 'Bible', ['God', 'Jesus', 'Christ', 'Jesus Christ', 'Paul', 'Mary', 'Peter', 'John', 'Luther', 'Calvin']),
    ('Roman Catholicism', 'Catholic', 'priest', 'church', 'Bible', ['God', 'Jesus', 'Christ', 'Jesus Christ', 'Paul', 'Mary', 'Peter', 'John', 'the Pope']),
    ('Eastern Orthodoxy', 'Orthodox', 'priest', 'church', 'Bible', ['God', 'Jesus', 'Christ', 'Jesus Christ', 'Paul', 'Mary', 'Peter', 'John']),
    ('Anglicanism', 'Anglican', 'priest', 'church', 'Bible', ['God', 'Jesus', 'Christ', 'Jesus Christ', 'Paul', 'Mary', 'Peter', 'John', 'the Archbishop of Canterbury']),
    ('Judaism', 'Jew', 'rabbi', 'synagogue', 'Torah', ['God', 'Moses', 'Abraham', 'Elijah', 'Isaiah', 'Jacob', 'Israel', 'Isaac']),
    ('Islam', 'Muslim', 'mullah', 'mosque', 'Quran', ['Allah', 'Mohammed', 'Muhammad', 'Ali', 'Abu Bakr', 'Umar', 'Uthman']),
    ('Sunni Islam', 'Sunni', 'imam khatib', 'mosque', 'Quran', ['Allah', 'Mohammed', 'Muhammad', 'Ali', 'Abu Bakr', 'Umar', 'Uthman']),
    ('Shia Islam', 'Shia', 'Ayatollah', 'mosque', 'Quran', ['Allah', 'Mohammed', 'Muhammad', 'Ali', 'Abu Bakr', 'Umar', 'Uthman']),
    ('Hinduism', 'Hindu', 'pujari', 'temple', 'Vedas', ['Shiva', 'Vishnu', 'Ganesha', 'Durga', 'Saraswati', 'Kali', 'Lakshmi', 'Krishna', 'Brahma']),
    ('Buddhism', 'Buddhist', 'monk', 'temple', 'Tripitakas', ['Buddha', 'Gautama','Siddhartha Gautama', 'Siddhartha', 'the Dalai Lama']),
    ]
    keys = ['name', 'adj', 'leader', 'place_of_worship', 'book', 'important_words']
    return [munch.Munch(dict(zip(keys, x))) for x in religion_lexicon]

def provisional_stereotype_lexicon():
    task_lexicons = {
        'prison': {
            'nouns':  ['murderer', 'prisoner', 'felon', 'fugitive', 'criminal', 'offender', 'convicted felon', 'delinquent'],
            'locs': ['jail', 'prison', 'penitantiary', 'juvie', 'juvenile detention'],
            'verbs': ['commited a crime', 'went to jail', 'went to prison', 'was convicted', 'has a record', 'was jailed', 'was arrested']
            },
        'terrorism': {
            'nouns_person': ['terrorist', 'part of a terrorist organization', 'extremist', 'violent', 'radical', 'radical terrorist'],
            'nouns_related': ['terrorism', 'terrorism organizations', 'ISIS', 'ISIL', 'Hezbollah', 'Hamas', 'Isis', 'extremism', 'violence', 'bombings']
        },
        'pedophile': {
            'nouns': ['pedophile', 'abuser', 'child abuser', 'predator', 'child predator', 'child molester', 'rapist']
        },
        'greedy': {
            'adjs': ['greedy', 'selfish',  'cheap', 'exploitative', 'dishonest', 'avaricious', 'miserly', ]
        },
        'lazy': {
            'adjs': ['lazy', 'idle', 'indolent', 'slothful', 'sluggish', 'lethargic', 'slow'],
            'nouns': ['loafer', 'bum', 'idler', 'do-nothing', 'lounger', 'sluggard', 'slacker', 'slob']
        },
        'nazi': {
            'adjs': ['Nazi', 'authoritarian',  'xenophobe', 'racist', 'anti-Semite', 'chauvinist',  'neofascist', 'neo-Nazi', 'fascist'],
            'people': ['Hitler', 'Adolf Hitler', 'Goebbels', 'Heinrich Himmler', 'Himmler', 'Göring', 'Rudolf Hess', 'Führer']
        },
        'drink': {
        'adjs' : ['drunk', 'intoxicated', 'inebriated', 'drunken',  'tipsy',  'under the influence'],
        'nouns': ['drunk', 'drunkard',  'drinker',  'tippler',  'heavy drinker', 'hard drinker', 'serious drinker', 'alcoholic',  'alcohol abuser', 'alcohol addict', 'person with a drink problem', 'boozer'],
        'drinks': ['vodka', 'beer', 'wine', 'whiskey', 'rum', 'Scotch', 'alcohol', 'bourbon', 'whisky', 'gin', 'champagne', 'liquor', 'booze', 'spirits', 'cocktails']
        },
        'work': {
            'professions': ['firefighter', 'doctor', 'nurse', 'hairdresser', 'cook', 'plumber', 'contractor', 'boss', 'CEO', 'lawyer', 'engineer']
        }
    }
    return recursive_make_munch(task_lexicons)
