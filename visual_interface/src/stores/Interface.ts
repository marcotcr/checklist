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
export type RawTestStats = { 
    npassed: number; 
    nfailed: number;
    nfiltered: number;
}
export type RawTestResult = { 
    name: string;
    description: string;
    capability: string;
    type: TestType;
    tags: string[]; // ["person1", "person2", "comparative"];
    stats: RawTestStats
}

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

export type BertSuggest = string[];
export type RawTemplateToken = [string[], string] | string;
export type TagDict = { [key: string]: string };
export type RawTemplate = RawTemplateToken[];

export const SPACE = " ";
export type TemplateExampleToken =  {
    text: string; hasTag: boolean; isMask: boolean; isArticle: boolean;
};
export type TemplateExampleSentence = TemplateExampleToken[];
export type TemplateExample = TemplateExampleSentence[];



