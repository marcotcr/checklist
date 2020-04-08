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
    /*
    ner: string; // named speech recognition
    pos: string; // part-of-speech tag in detail
    tag: string; // simplified the tag
    lemma: string; // lemma in lower case
    */
}

export type TemplateTestInstance = {
    target: string;
    text: string;
}
export type PerturbTestInstance = {
    target: string;
    text: string;
    oldText: string;
}

export type TestInstance = TemplateTestInstance|PerturbTestInstance

export type TestOutput = string;
export type TestStats = { 
    nTested: number; 
    nFailed: number;
    rate: number;
    strResult: string;
}

export type TestAuthorType = "perturb"|"template";
export type RawTestExample = { 
    instance: TestInstance[];
    pred: TestOutput;
    conf: number;
    expect: TestOutput; 
    tags: string[];
    status: "success"|"fail";
};

export type RawTestResult = { 
    name: string;
    category: string;
    authorType: TestAuthorType;
    expectationMeta: {[key: string]: string};
    tags: string[]; // ["person1", "person2", "comparative"];
    result: {"nTested" : number, "nFailed": number}
 }