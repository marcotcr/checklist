import { TagDict, RawTemplate, RawTestCase, RawTestResult, BertSuggest } from "./Interface";

export const tagDict: TagDict = {'pos_adj': 'good', 'air_noun': 'flight', 'intens': 'very'};
// a demo template sentence
export const rawTemplates: RawTemplate[] = [
    ['It', 'is', ['good', 'a:pos_adj'], ['flight', 'air_noun'], '.'],
    ['It', ['', 'a:bert'], ['very', 'a:intens'], ['good', 'pos_adj'], ['', 'bert'],'.']
]
export const suggests: BertSuggest[] = [
    ['was', 'day'],
    ['been', 'day'],
    ['been', 'week'],
    ['was', 'time'],
    ['been', 'year'],
    ['was', 'experience'],
    ['been', 'weekend'],
    ['was', 'moment'],
    ['s', 'day'],
    ['was', 'game']
]

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