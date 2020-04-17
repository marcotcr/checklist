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
        rawTests.forEach(rawTest => {
            this.overviewTests.push(new TestResult(
                rawTest.name, rawTest.description,
                rawTest.type, rawTest.capability,
                rawTest.stats, rawTest.tags));
        });
        // reset the test store to clear the selections
        testStore.setTest(null);
    }

    public onSelectTest(testname: string): void {
        // a placeholder selection function.
        console.log(`selected: ${testname}`)
        if (!testStore.testResult) {
            testStore.setTest(rawTestResult);
            testStore.setTestcases(rawTestcases);
            testStore.randomTestStats();
        } else {
            testStore.setTest(null);
        }
    }
}

export const suiteStore = new SuiteStore();
