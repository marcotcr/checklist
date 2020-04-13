import { TestExample, TestSentence } from "../Interface";
import { TestTag } from "./TestTag";
import { utils } from "../Utils";


export class TestCase {
    public examples: TestExample[];
    public succeed: boolean;
    public tags: TestTag[];

    constructor (examples: TestExample[], succeed: boolean, tags: string[]) {
        this.examples = examples;
        this.succeed = succeed;
        this.tags = tags.map(t => new TestTag(t));
    }

    public key(): string {
        const keyOfSentence = (t: TestSentence) => 
            t ? utils.normalizeKey(`${t.tokens.join("-")}-${t.pred}-${t.conf}`) : "";
        return this.examples.map(
            i => `old:${keyOfSentence(i.old)}-new:${keyOfSentence(i.new)}-${i.label}-${i.succeed}`).join("-");
    }
}