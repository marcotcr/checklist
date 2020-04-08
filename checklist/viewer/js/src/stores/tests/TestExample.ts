import { Template} from "../templates/Template";
import { TestOutput, TestInstance } from "../Interface";
import { TestTag } from "./TestTag";

export class TestExample {
    public instance: TestInstance[];
    public expect: TestOutput;
    public pred: TestOutput;
    public is_succeed: boolean;
    public conf: number;
    public tags: TestTag[];

    constructor (instance: TestInstance[], expect: TestOutput, pred: TestOutput, conf: number, tags: string[], is_succeed: boolean) {
        this.instance = instance;
        this.pred = pred;
        this.conf = conf;
        this.expect = expect;
        this.tags = tags.map(t => new TestTag(t));
        this.is_succeed = is_succeed;
    }

    public key(): string {
        return this.instance.map(i => `${i.target}-${i.text}-${i["oldText"]}`).join("-") + this.pred + this.expect;
    }
}