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
            'first_name'
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
            'comp[0]'
        ],
        'than',
        [[], 'bert'],
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
            'comp[1]'
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
            'first_name'
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

export const rawTestResults: RawTestResult[] = [
    {
        'name': 'Sentiment-laden words in context',
        'description': 'Use positive and negative verbs and adjectives with airline nouns such as seats, pilot, flight, etc. E.g. "This was a bad flight"',
        'capability': 'Vocabulary',
        'type': 'mft',
        'tags': [],
        'stats': {'nfailed': 1, 'npassed': 2963, 'nfiltered': 0}
    },
    {
        'name': 'intensifiers',
        'description': 'Test is composed of pairs of sentences (x1, x2), where we add an intensifier\nsuch as "really",or "very" to x2 and expect the confidence to NOT go down (with tolerance=0.1). e.g.:\nx1 = "That was a good flight"\nx2 = "That was a very good flight"\nWe disregard cases where the prediction of x1 is neutral.\n',
        'capability': 'Vocabulary',
        'type': 'dir',
        'tags': [],
        'stats': {'nfailed': 88, 'npassed': 1909, 'nfiltered': 3}
    },
    {
        'name': 'intensifiers1',
        'description': 'Test is composed of pairs of sentences (x1, x2), where we add an intensifier\nsuch as "really",or "very" to x2 and expect the confidence to NOT go down (with tolerance=0.1). e.g.:\nWe disregard cases where the prediction of x1 is neutral.\n',
        'capability': 'Vocabulary',
        'type': 'dir',
        'tags': [],
        'stats': {'nfailed': 82, 'npassed': 1910, 'nfiltered': 8}
    }

]

export const rawTestResult: RawTestResult = rawTestResults[0]