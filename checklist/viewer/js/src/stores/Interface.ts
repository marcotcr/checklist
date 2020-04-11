export type TestType = "mft"|"dir"|"inv";

export type TestSentence = {
    tokens: string[][]; // directly input
    pred: string;
    conf: number;
}

export type TestExample = { 
    old: TestSentence;
    new: TestSentence;
    label: string; 
    succeed: boolean;
};

export type RawTestCase = { 
    examples: TestExample[];
    tags: string[];
    succeed: boolean;
};
export type RawTestResult = { 
    name: string;
    type: TestType;
    expect_meta: {[key: string]: string};
    tags: string[]; // ["person1", "person2", "comparative"];
    stats: {"nTested" : number, "nFailed": number}
}



export type RawToken = [string, string] | string;
export type CandidateDict = { [key: string]: string[] };
export type RawSentence = { target: string, tokens: RawToken[] }

export const MASK = "mask";
export const SPACE = " ";
export type Action = "tag"|"edit"|"delete"|"plus"|"unlock"|"lock";
export type Condition = "C1"|"C2"|"C3";
export type TemplateExampleToken =  {text: string; hasTag: boolean; isMask: boolean};

export interface Token {
    idx: number; // the idx of the span in doc
    text: string; // text of one word
    etype?: "add"|"remove"|"keep";
    isReplace?: boolean;
    /*
    ner: string; // named speech recognition
    pos: string; // part-of-speech tag in detail
    tag: string; // simplified the tag
    lemma: string; // lemma in lower case
    */
}

export type TestOutput = string;
export type TestStats = { 
    nTested: number; 
    nFailed: number;
    rate: number;
    strResult: string;
}



export type TestAuthorType = "perturb"|"template";


