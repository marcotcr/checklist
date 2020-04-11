import { CandidateDict, RawSentence, RawTestCase, RawTestResult } from "./Interface";

export const testnames = ["negation", "fairness", "question", "coreference"];

export const candidateDict: CandidateDict ={
    comparative : ['better', 'worse', 'older', 'younger', 'smarter', 'stronger', 'weaker', 'happier', 'taller', 'cooler'],
    country     : ["the US", "China", ""],
    city        : ["Beijing", "Hong Kong", "Seattle", "London"],
    person      : ["Marco", "Julia", "Sherry", "Jeff", "Carlos"],
    pronun      : ["I", "you"]
};
 
// names of the candidate
export const candidateNames: string[] = Object.keys(candidateDict);

// a demo sentence
export const rawSentences: RawSentence[] = [
    {
        tokens: [ 
            "Who", "is", 
            ["taller", "{comparative1}"], 
            ",", 
            ["Mary", "{person1}"], 
            "or",
            ["Heather", "{person2}"], "?" 
        ],
        target: "Q1"
    },  {
        tokens: [ 
            "Who", "is", 
            ["taller", "{comparative1}"], 
            ",", 
            ["Heather", "{person2}"], 
            "or",
            ["Mary", "{person1}"], 
            "?" 
        ],
        target: "Q2"
    }, 
];

// test data
export const rawExamples: RawTestCase[] = [
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
                    ["Who", "is", "cooler", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "cooler", ",", "Heather", "or", "Mary", "?"]
                ],
                pred: "1",
                conf: 0.7
            },
            old: {
                tokens: [
                    ["Who", "is", "cooler", ",", "Mary", "or", "Heather", "?"],
                    ["Who", "is", "cooler", ",", "Mary", "or", "Heather", "?"]
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

export const rawTestResult: RawTestResult =  { 
    name: "Change the PERSON order",
    type: "inv",
    expect_meta: {expected: "equal"},
    tags: [
        "person1=Mary", 
        "person2=Heather", 
        "person2=Marco",
        "comparative=cooler",
        "comparative=taller"
    ],
    stats: {nfailed: 10, npassed: 20, nfiltered: 20}
 }