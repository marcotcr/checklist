import { TestStats } from "../Interface";
import { utils } from "../Utils";
import { TestTag } from "./TestTag";
import { testStore } from "./TestStore";
import { observable } from "mobx";

export class TestResult {
    public name: string;
    public type: string; // min functionality, invariance, monotonicity, fairness
    public tags: TestTag[];//{[key: string]: string[]};
    public expectationMeta: {[key: string]: string};
    @observable public testStats: TestStats;

    constructor (
        name: string,
        type: string,
        stats: {nTested: number, nFailed: number}={nTested: 0, nFailed: 0},
        tags: string[]=[],
        expectationMeta: {[key: string]: string}={}) {
        this.name = name;
        this.type = type;
        this.expectationMeta = expectationMeta;
        //this.parseRawTag(tags);
        this.tags = tags.map(t => new TestTag(t));
        this.setGlobalTestStat(stats);
    }
    public setGlobalTestStat(rawState: {nTested: number, nFailed: number}): void {
        this.testStats = testStore.setTestStats(rawState);
    }

    public key(): string {
        return utils.normalizeKey(`name:${this.name}-category:${this.type}`)
    }
}