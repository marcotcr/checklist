import { observable } from "mobx";
import { RawTestResult, RawTestCase, TestStats } from "../Interface";
import { TestResult } from "./TestResult";
import { TestCase } from "./TestCase";
import { utils } from "../Utils";

export class TestStore {
    @observable public testResult: TestResult;
    @observable public searchTags: string[];
    public allTestcases: TestCase[];
    public candidateTestcases: TestCase[];
    @observable public testcases: TestCase[];

    @observable public testStats: TestStats;
    @observable public failCaseOnly: boolean;
    constructor () {
        this.testResult = null;
        this.searchTags = [];
        this.candidateTestcases = [];
        this.testcases = [];
        this.allTestcases = [];
        this.failCaseOnly = true;
        this.randomTestStats();
        this.fetchMoreExample = this.fetchMoreExample.bind(this);
        this.search = this.search.bind(this);
    }

    public setTest(rawTest: RawTestResult): void {
        this.testcases = [];
        this.setTestStats({nTested: 0, nFailed: 0});
        this.setSearchTags([]);
        this.failCaseOnly = true;

        if (rawTest) {
            this.testResult = new TestResult(
                rawTest.name, rawTest.type, rawTest.stats, 
                rawTest.tags, rawTest.expectationMeta);
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

    public setTestcases(testcases: RawTestCase[]): void {
        this.candidateTestcases = testcases.map(e => 
            new TestCase(e.examples, e.succeed, e.tags));
        this.allTestcases = testcases.map(e => 
            new TestCase(e.examples, e.succeed, e.tags));
        this.testcases = [];
    }

    public addMoreTestcases(testcases: RawTestCase[]): void {
        this.testcases = this.testcases.concat(testcases.map(e => 
            new TestCase(e.examples, e.succeed, e.tags)));
        console.log(testcases, this.testcases );
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
        this.candidateTestcases = this.allTestcases.filter(e => {
            const includeTags = e.tags.map(t => t.raw);
            const hasTag = (t: string) => {
                return includeTags.indexOf(t) > -1;
            }
            return (!this.failCaseOnly || !e.succeed) && this.searchTags.every(hasTag)
        });
        this.testcases = this.candidateTestcases.slice();
        // get some random stats
        this.randomTestStats();
    }
 
    public fetchMoreExample(): void {
        this.testcases = this.testcases.concat(this.candidateTestcases);
    }
    public resetFilter(): void {
        this.setSearchTags([]);
        this.failCaseOnly = true;
        this.testcases = [];
    }
}

export const testStore = new TestStore();
