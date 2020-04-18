import { observable } from "mobx";
import { RawTestResult } from "../Interface";
import { TestResult } from "./TestResult";
import { testStore } from "./TestStore";
import { rawTestResult, rawTestcases } from "../FakeData";

export class SuiteStore {
    @observable public overviewTests: TestResult[];
    
    constructor() {
        this.overviewTests = [];
        this.onSelectTest = this.onSelectTest.bind(this);
    }

    public setTestOverview(rawTests: RawTestResult[]): void {
        this.overviewTests = [];
        rawTests.forEach(rawTest => {
            this.overviewTests.push(new TestResult(
                rawTest.name, rawTest.description,
                rawTest.type, rawTest.capability,
                rawTest.stats, rawTest.tags));
        });
        // reset the test store to clear the selections
        testStore.setTest(null);
    }

    public onSelectTest(test: TestResult): void {
        // a placeholder selection function.
        console.log(`selected: ${test.key()}`)
        if (test) {
            testStore.setTest({
                name: test.name,
                description: test.description,
                capability: test.capability,
                type: test.type,
                stats: {
                    nfailed: test.testStats.nfailed,
                    npassed: test.testStats.npassed,
                    nfiltered: test.testStats.nfiltered,
                },
                tags: test.tags.map(t => t.raw),
            })
            testStore.setTestcases(rawTestcases);
            testStore.randomTestStats();
        } else {
            testStore.setTest(null);
        }
    }
}

export const suiteStore = new SuiteStore();
