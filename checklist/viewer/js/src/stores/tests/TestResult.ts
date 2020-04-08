import { TestAuthorType, TestStats } from "../Interface";
import { utils } from "../Utils";
import { TestTag } from "./TestTag";
import { testStore } from "./TestStore";
import { observable } from "mobx";

export class TestResult {
    public name: string;
    public category: string; // min functionality, invariance, monotonicity, fairness
    public authorType: TestAuthorType;
    public tags: TestTag[];//{[key: string]: string[]};
    public expectationMeta: {[key: string]: string};
    @observable public testStats: TestStats;

    constructor (
        name: string,
        category: string,
        authorType: TestAuthorType,
        expectationMeta: {[key: string]: string},
        tags: string[],
        stats: {nTested: number, nFailed: number}={nTested: 0, nFailed: 0}) {
        this.name = name;
        this.category = category;
        this.authorType = authorType;
        this.expectationMeta = expectationMeta;
        //this.parseRawTag(tags);
        this.tags = tags.map(t => new TestTag(t));
        this.setGlobalTestStat(stats);
    }
    public setGlobalTestStat(rawState: {nTested: number, nFailed: number}): void {
        this.testStats = testStore.setTestStats(rawState);
    }

    public key(): string {
        return utils.normalizeKey(`name:${this.name}-author:${this.authorType}-category:${this.category}`)
    }
}