import { RawTestStats, TestType } from "../Interface";
import { utils } from "../Utils";
import { TestTag } from "./TestTag";
import { testStore } from "./TestStore";
import { observable } from "mobx";
import { TestStats } from "./TestStats";

export class TestResult {
    public name: string;
    public description: string;
    public type: TestType;
    public capability: string;
    public tags: TestTag[];//{[key: string]: string[]};
    @observable public testStats: TestStats;

    constructor (
        name: string,
        description: string,
        type: TestType,
        capability: string,
        stats: RawTestStats={npassed: 0, nfailed: 0, nfiltered: 0},
        tags: string[]=[]) {
        this.name = name;
        this.type = type;
        this.description = description;
        this.capability = capability;
        //this.parseRawTag(tags);
        this.tags = tags.map(t => new TestTag(t));
        this.setGlobalTestStat(stats);
    }
    public setGlobalTestStat(rawStats: RawTestStats): void {
        this.testStats = testStore.setTestStats(rawStats);
    }

    public key(): string {
        return utils.normalizeKey(`name:${this.name}-description:${this.description}-type:${this.type}-capability:${this.capability}`)
    }
}