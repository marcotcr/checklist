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
        function keyPerSentence(sentence: TestSentence) {
            if (!sentence) {
                return "";
            }
            let key = sentence.tokens.map(tokens => tokens.join("-")).join("-");
            key += String(sentence.pred) + String(sentence.pred);
            return key;
        }

        return this.examples.map(
            i => `old:${keyPerSentence(i.old)}-new:${keyPerSentence(i.new)}-${i.label}-${i.succeed}`).join("-");
    }
}