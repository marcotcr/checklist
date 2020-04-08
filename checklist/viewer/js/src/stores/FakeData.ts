import { CandidateDict, RawSentence, RawTestExample, RawTestResult } from "./Interface";

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
export const rawExamples: RawTestExample[] = [
    {
        instance: [
            {target: "Q1", text: "Who is taller, Mary or Heather?"},
            {target: "Q2", text: "Who is taller, Heather or Mary?"}
        ], 
        pred: "1",
        expect: "0",
        conf: 0.7,
        status: "fail",
        tags: ["person1=Mary", "person2=Heather", "comparative=taller"]
    }, {
        instance: [
            {target: "Q1", text: "Who is cooler, Mary or Heather?"},
            {target: "Q2", text: "Who is cooler, Heather or Mary?"}
        ], 
        pred: "1",
        conf: 0.7,
        expect: "0",
        status: "success",
        tags: ["person1=Mary", "person2=Heather", "comparative=cooler"]
    }, {
        instance: [
            {target: "Q1", text: "Who is cooler, Mary or Marco?"},
            {target: "Q2", text: "Who is cooler, Marco or Mary?"}
        ], 
        pred: "0",
        expect: "0",
        conf: 0.7,
        status: "success",
        tags: ["person1=Mary", "person2=Marco", "comparative=cooler"]
    }, {
        instance: [
            {target: "Q1", text: "Who is taller, Mary or Marco?"},
            {target: "Q2", text: "Who is taller, Marco or Mary?"}
        ], 
        pred: "0",
        expect: "0",
        conf: 0.7,
        status: "fail",
        tags: ["person1=Mary", "person2=Marco", "comparative=taller"]
    }, {
        instance: [
            {
                target: "Q1", 
                text: "Who is taller, Mary or Heather?",
                oldText: "Who is cooler, Mary or Heather?"
            },{
                target: "Q2", 
                text: "Who is taller, Heather or Mary?",
                oldText: "Who is cooler, Heather or Mary?"
            }
        ], 
        pred: "1",
        expect: "0",
        status: "fail",
        conf: 0.7,
        tags: ["person1=Mary", "person2=Heather", "comparative=taller"]
    }, {
        instance: [
            {
                target: "Q1", 
                text: "Who is cooler, Heather or Mary?",
                oldText: "Who is cooler, Mary or Heather?"
            },{
                target: "Q2", 
                text: "Who is cooler, Heather or Mary?",
                oldText: "Who is cooler, Heather or Mary?"
            }
        ], 
        pred: "1",
        expect: "0",
        status: "fail",
        conf: 0.7,
        tags: ["person1=Mary", "person2=Heather", "comparative=cooler"]
    }
]

export const rawTestResult: RawTestResult =  { 
    name: "Change the PERSON order",
    category: "invariance",
    authorType: "template",
    expectationMeta: {expected: "equal"},
    tags: [
        "person1=Mary", 
        "person2=Heather", 
        "person2=Marco",
        "comparative=cooler",
        "comparative=taller"
    ],
    result: {nFailed: 10, nTested: 20}
 }