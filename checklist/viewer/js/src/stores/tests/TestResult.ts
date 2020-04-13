import { RawTestStats } from "../Interface";
import { utils } from "../Utils";
import { TestTag } from "./TestTag";
import { testStore } from "./TestStore";
import { observable } from "mobx";
import { TestStats } from "./TestStats";

export class TestResult {
    public name: string;
    public type: string; // min functionality, invariance, monotonicity, fairness
    public tags: TestTag[];//{[key: string]: string[]};
    public expectationMeta: {[key: string]: string};
    @observable public testStats: TestStats;

    constructor (
        name: string,
        type: string,
        stats: RawTestStats={npassed: 0, nfailed: 0, nfiltered: 0},
        tags: string[]=[],
        expectationMeta: {[key: string]: string}={}) {
        this.name = name;
        this.type = type;
        this.expectationMeta = expectationMeta;
        //this.parseRawTag(tags);
        this.tags = tags.map(t => new TestTag(t));
        this.setGlobalTestStat(stats);
    }
    public setGlobalTestStat(rawStats: RawTestStats): void {
        this.testStats = testStore.setTestStats(rawStats);
    }

    public key(): string {
        return utils.normalizeKey(`name:${this.name}-category:${this.type}`)
    }
}