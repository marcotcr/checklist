import { observable } from "mobx";
import { RawTestResult, RawTestExample, TestStats } from "../Interface";
import { TestResult } from "./TestResult";
import { TestExample } from "./TestExample";
import { utils } from "../Utils";

export class TestStore {
    @observable public testResult: TestResult;
    @observable public searchTags: string[];
    public allExamples: TestExample[];
    public candidateExample: TestExample[];
    @observable public examples: TestExample[];

    @observable public testStats: TestStats;
    @observable public failCaseOnly: boolean;
    constructor () {
        this.testResult = null;
        this.searchTags = [];
        this.candidateExample = [];
        this.examples = [];
        this.allExamples = [];
        this.failCaseOnly = true;
        this.randomTestStats();
        this.fetchMoreExample = this.fetchMoreExample.bind(this);
        this.search = this.search.bind(this);
    }

    public setTest(rawTest: RawTestResult): void {
        this.examples = [];
        this.setTestStats({nTested: 0, nFailed: 0});
        this.setSearchTags([]);
        this.failCaseOnly = true;

        if (rawTest) {
            this.testResult = new TestResult(
                rawTest.name, rawTest.category, rawTest.authorType, 
                rawTest.expectationMeta, rawTest.tags,rawTest.result);
        } else {
            this.testResult = null;
        }
    }

    public togglefailCaseFilter(): void {
        this.failCaseOnly = !this.failCaseOnly;
    }

    public setTestStats(stats: { nTested: number, nFailed: number }): TestStats {
        const rate = stats.nTested ? stats.nFailed / stats.nTested : 0;
        const rateStr = (rate * 100).toFixed(1) + "%";
        this.testStats = {
            nTested: stats.nTested,
            nFailed: stats.nFailed,
            rate: rate,
            strResult: `${stats.nFailed} / ${stats.nTested} = ${rateStr}`
        }
        return this.testStats;
    }

    public setExamples(examples: RawTestExample[]): void {

        this.candidateExample = examples.map(e => 
            new TestExample(e.instance, e.expect, e.pred, e.conf, e.tags, e.status === "success"));
        this.allExamples = examples.map(e => 
            new TestExample(e.instance, e.expect, e.pred, e.conf, e.tags, e.status === "success"));
        this.examples = [];
    }

    public addMoreExample(examples: RawTestExample[]): void {
        this.examples = this.examples.concat(examples.map(e => 
            new TestExample(e.instance, e.expect, e.pred, e.conf, e.tags, e.status === "success")));
        console.log(examples, this.examples );
    }

    public setSearchTags(tag: string[]): void {
        this.searchTags = tag || [];
    }

    public randomTestStats(): void {
        this.setTestStats({
            nFailed: utils.getRandomArbitrary(0, 30),
            nTested: utils.getRandomArbitrary(30, 50)
        });
    }

    public search(): void {
        // get the examples
        this.candidateExample = this.allExamples.filter(e => {
            const includeTags = e.tags.map(t => t.raw);
            const hasTag = (t: string) => {
                return includeTags.indexOf(t) > -1;
            }
            return (!this.failCaseOnly || !e.is_succeed) && this.searchTags.every(hasTag)
        });
        this.examples = this.candidateExample.slice();
        // get some random stats
        this.randomTestStats();
    }
 
    public fetchMoreExample(): void {
        this.examples = this.examples.concat(this.candidateExample);
    }
    public resetFilter(): void {
        this.setSearchTags([]);
        this.failCaseOnly = true;
        this.examples = [];
    }
}

export const testStore = new TestStore();
