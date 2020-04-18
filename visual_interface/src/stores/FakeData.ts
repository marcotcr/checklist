import { TagDict, RawTemplate, RawTestCase, RawTestResult, BertSuggest } from "./Interface";

export const tagDict: TagDict = {'pos_adj': 'good', 'air_noun': 'flight', 'intens': 'very'};
// a demo template sentence
export const rawTemplates: RawTemplate[] = [
    [
        [
            [
                'Michael','Michael','Michael','Michael','Michael',
                'Jennifer','Jennifer','Jennifer','Jennifer','Jennifer',
                'Christopher','Christopher','Christopher','Christopher','Christopher',
                'Jessica','Jessica','Jessica','Jessica','Jessica',
                'Matthew','Matthew','Matthew','Matthew','Matthew'
            ], 
            'first_name', 'first_name'
        ],
        'is',
        [
            [
                'bigger','warmer','colder','poorer','richer',
                'bigger','warmer','colder','poorer','richer',
                'bigger','warmer','colder','poorer','richer',
                'bigger','warmer','colder','poorer','richer',
                'bigger','warmer','colder','poorer','richer',
            ],
            'comp[0]',
            'comp'
        ],
        'than',
        [[], 'bert', 'bert'],
        '.'
    ],[
        'Who',
        'is',
        [
            [
                'smaller','colder','warmer','richer','poorer',
                'smaller','colder','warmer','richer','poorer',
                'smaller','colder','warmer','richer','poorer',
                'smaller','colder','warmer','richer','poorer',
                'smaller','colder','warmer','richer','poorer'
            ],
            'comp[1]', 'comp'
        ],
        '?'
    ],[
        [
            [
                'Michael','Michael','Michael','Michael','Michael',
                'Jennifer','Jennifer','Jennifer','Jennifer','Jennifer',
                'Christopher','Christopher','Christopher','Christopher','Christopher',
                'Jessica','Jessica','Jessica','Jessica','Jessica',
                'Matthew','Matthew','Matthew','Matthew','Matthew'
            ],
            'first_name', 'first_name'
        ]
    ]
]
export const suggests: (string|string[])[] = [
    'an International',
    'a unconventionally',
    'a Christian',
'Protestant',
'Roman Catholic',
'Eastern Orthodox' ,
'Anglican',
'Jew',
'Orthodox Jew',
'Muslim',
'Sunni',
"Shi'a",
'Ahmadiyya',
'Buddhist',
'Zoroastrian',
'Hindu',
'Sikh',
'Shinto',
"Baha'i",
'Taoist',
'Confucian',
'Jain',
'Atheist',
'Agnostic']

// test data
export const rawTestcases: RawTestCase[] = [
    {
        examples: [{
            new: {
                tokens: [
                    ["Who", "is", "taller", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "taller", ",", "Heather", "or", "Mary", "?"]
                ],
                pred: "1",
                conf: 0.7
            },
            old: null,
            label: "1",
            succeed: false,
        }],
        tags: ["person1=Mary", "person2=Heather", "comparative=taller"],
        succeed: false,
    }, {
        examples: [{
            new: {
                tokens: [
                    ["Who", "is", "taller", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "taller", ",", "Heather", "or", "Mary", "?"]
                ],
                pred: "1",
                conf: 0.7
            },
            old: null,
            label: "1",
            succeed: true,
        }, {
            new: {
                tokens: [
                    ["Who", "is", "cooler", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "cooler", ",", "Heather", "or", "Mary", "?"]
                ],
                pred: "1",
                conf: 0.7
            },
            old: null,
            label: "1",
            succeed: true,
        }],
        tags: ["person1=Mary", "person2=Heather", "comparative=taller", "comparative=cooler"],
        succeed: true,
    }, {
        examples: [{
            new: {
                tokens: [
                    ["Who", "is", "taller", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "taller", ",", "Heather", "or", "Mary", "?"]
                ],
                pred: "0",
                conf: 0.9
            },
            old: {
                tokens: [
                    ["Who", "is", "taller", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "taller", ",", "Mary", "or", "Heather", "?"]
                ],
                pred: "1",
                conf: 0.7
            },
            succeed: false,
            label: null,
        }, {
            new: {
                tokens: [
                    ["That", "is", "an", "amazingly", "sad", "staff", "."],
                ],
                pred: "1",
                conf: 0.7
            },
            old: {
                tokens: [
                    ["That", "is", "a", "sad", "staff", "."],
                ],
                pred: "0",
                conf: 0.8
            },
            label: null,
            succeed: false,
        }],
        succeed: false,
        tags: ["person1=Mary", "person2=Heather", "comparative=cooler", "comparative=taller"]
    }
]

export const rawTestResults: RawTestResult[] = [{
    'name': 'single positive words single positive words single positive words single positive words',
'description': '',
'capability': 'Vocabulary',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 6, 'npassed': 28, 'nfiltered': 0}},
{'name': 'single negative words',
'description': '',
'capability': 'Vocabulary',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 3, 'npassed': 32, 'nfiltered': 0}},
{'name': 'single neutral words',
'description': 'TODO_DESCRIPTION',
'capability': 'Vocabulary',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 8, 'npassed': 5, 'nfiltered': 0}},
{'name': 'Sentiment-laden words in context',
'description': 'Use positive and negative verbs and adjectives with airline nouns such as seats, pilot, flight, etc. E.g. "This was a bad flight"',
'capability': 'Vocabulary',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 2, 'npassed': 8656, 'nfiltered': 0}},
{'name': 'neutral words in context',
'description': 'Use neutral verbs and adjectives with airline nouns such as seats, pilot, flight, etc. E.g. "The pilot is American"',
'capability': 'Vocabulary',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 165, 'npassed': 1551, 'nfiltered': 0}},
{'name': 'intensifiers',
'description': 'Test is composed of pairs of sentences (x1, x2), where we add an intensifier\nsuch as "really",or "very" to x2 and expect the confidence to NOT go down (with tolerance=0.1). e.g.:\nx1 = "That was a good flight"\nx2 = "That was a very good flight"\nWe disregard cases where the prediction of x1 is neutral.\n',
'capability': 'Vocabulary',
'type': 'dir',
'tags': [],
'stats': {'nfailed': 8, 'npassed': 1992, 'nfiltered': 0}},
{'name': 'reducers',
'description': 'Test is composed of pairs of sentences (x1, x2), where we add a reducer\nsuch as "somewhat", or "kinda" to x2 and expect the confidence to NOT go up (with tolerance=0.1). e.g.:\nx1 = "The cabin crew was good."\nx2 = "The cabin crew was somewhat good."\nWe disregard cases where the prediction of x1 is neutral.\n',
'capability': 'Vocabulary',
'type': 'dir',
'tags': [],
'stats': {'nfailed': 0, 'npassed': 1803, 'nfiltered': 197}},
{'name': 'change neutral words with BERT',
'description': 'Change a set of neutral words with other context-appropriate neutral words (using BERT).',
'capability': 'Vocabulary',
'type': 'inv',
'tags': [],
'stats': {'nfailed': 43, 'npassed': 457, 'nfiltered': 0}},
{'name': 'add positive phrases',
'description': 'Add very positive phrases (e.g. I love you) to the end of sentences, expect probability of positive to NOT go down (tolerance=0.1)',
'capability': 'Vocabulary',
'type': 'dir',
'tags': [],
'stats': {'nfailed': 2, 'npassed': 498, 'nfiltered': 0}},
{'name': 'add negative phrases',
'description': 'Add very negative phrases (e.g. I hate you) to the end of sentences, expect probability of positive to NOT go up (tolerance=0.1)',
'capability': 'Vocabulary',
'type': 'dir',
'tags': [],
'stats': {'nfailed': 20, 'npassed': 480, 'nfiltered': 0}},
{'name': 'add random urls and handles',
'description': 'add randomly generated urls and handles to the start or end of sentence',
'capability': 'Robustness',
'type': 'inv',
'tags': [],
'stats': {'nfailed': 37, 'npassed': 463, 'nfiltered': 0}},
{'name': 'punctuation',
'description': 'strip punctuation and / or add "."',
'capability': 'Robustness',
'type': 'inv',
'tags': [],
'stats': {'nfailed': 17, 'npassed': 483, 'nfiltered': 0}},
{'name': 'typos',
'description': 'Add one typo to input by swapping two adjacent characters',
'capability': 'Robustness',
'type': 'inv',
'tags': [],
'stats': {'nfailed': 23, 'npassed': 477, 'nfiltered': 0}},
{'name': '2 typos',
'description': 'Add two typos to input by swapping two adjacent characters twice',
'capability': 'Robustness',
'type': 'inv',
'tags': [],
'stats': {'nfailed': 42, 'npassed': 458, 'nfiltered': 0}},
{'name': 'contractions',
'description': "Contract or expand contractions, e.g. What is -> What's",
'capability': 'Robustness',
'type': 'inv',
'tags': [],
'stats': {'nfailed': 14, 'npassed': 621, 'nfiltered': 0}},
{'name': 'change names',
'description': 'Replace names with other common names',
'capability': 'NER',
'type': 'inv',
'tags': [],
'stats': {'nfailed': 25, 'npassed': 632, 'nfiltered': 0}},
{'name': 'change locations',
'description': 'Replace city or country names with other cities or countries',
'capability': 'NER',
'type': 'inv',
'tags': [],
'stats': {'nfailed': 22, 'npassed': 121, 'nfiltered': 0}},
{'name': 'change numbers',
'description': 'Replace integers with random integers within a 20% radius of the original',
'capability': 'NER',
'type': 'inv',
'tags': [],
'stats': {'nfailed': 9, 'npassed': 351, 'nfiltered': 0}},
{'name': 'used to, but now',
'description': 'Have two conflicing statements, one about the past and one about the present.\nExpect the present to carry the sentiment. Examples:\nI used to love this airline, now I hate it -> should be negative\nI love this airline, although I used to hate it -> should be positive\n',
'capability': 'Temporal',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 57, 'npassed': 7943, 'nfiltered': 0}},
{'name': '"used to" should reduce',
'description': 'A model should not be more confident on "I used to think X" when compared to "X", e.g. "I used to love this airline" should have less confidence than "I love this airline"',
'capability': 'Temporal',
'type': 'dir',
'tags': [],
'stats': {'nfailed': 1, 'npassed': 4170, 'nfiltered': 197}},
{'name': 'protected: race',
'description': 'Prediction should be the same for various adjectives within a protected class',
'capability': 'Fairness',
'type': 'inv',
'tags': [],
'stats': {'nfailed': 83, 'npassed': 517, 'nfiltered': 0}},
{'name': 'protected: sexual',
'description': 'Prediction should be the same for various adjectives within a protected class',
'capability': 'Fairness',
'type': 'inv',
'tags': [],
'stats': {'nfailed': 146, 'npassed': 454, 'nfiltered': 0}},
{'name': 'protected: religion',
'description': 'Prediction should be the same for various adjectives within a protected class',
'capability': 'Fairness',
'type': 'inv',
'tags': [],
'stats': {'nfailed': 171, 'npassed': 429, 'nfiltered': 0}},
{'name': 'protected: nationality',
'description': 'Prediction should be the same for various adjectives within a protected class',
'capability': 'Fairness',
'type': 'inv',
'tags': [],
'stats': {'nfailed': 32, 'npassed': 568, 'nfiltered': 0}},
{'name': 'simple negations: negative',
'description': 'Very simple negations of positive statements',
'capability': 'Negation',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 34, 'npassed': 6284, 'nfiltered': 0}},
{'name': 'simple negations: not negative',
'description': 'Very simple negations of negative statements. Expectation requires prediction to NOT be negative (i.e. neutral or positive)',
'capability': 'Negation',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 84, 'npassed': 6702, 'nfiltered': 0}},
{'name': 'simple negations: not neutral is still neutral',
'description': 'Negating neutral statements should still result in neutral predictions',
'capability': 'Negation',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 155, 'npassed': 2341, 'nfiltered': 0}},
{'name': 'simple negations: I thought x was positive, but it was not (should be negative)',
'description': '',
'capability': 'Negation',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 25, 'npassed': 1967, 'nfiltered': 0}},
{'name': 'simple negations: I thought x was negative, but it was not (should be neutral or positive)',
'description': '',
'capability': 'Negation',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 174, 'npassed': 1950, 'nfiltered': 0}},
{'name': 'simple negations: but it was not (neutral) should still be neutral',
'description': '',
'capability': 'Negation',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 200, 'npassed': 604, 'nfiltered': 0}},
{'name': 'Hard: Negation of positive with neutral stuff in the middle (should be negative)',
'description': '',
'capability': 'Negation',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 0, 'npassed': 1000, 'nfiltered': 0}},
{'name': 'Hard: Negation of negative with neutral stuff in the middle (should be positive or neutral)',
'description': '',
'capability': 'Negation',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 200, 'npassed': 800, 'nfiltered': 0}},
{'name': 'negation of neutral with neutral in the middle, should still neutral',
'description': '',
'capability': 'Negation',
'type': 'mft',
'tags': [],
'stats': {'nfailed': 200, 'npassed': 800, 'nfiltered': 0}}]

export const rawTestResult: RawTestResult = rawTestResults[0]