import { observable } from "mobx";
import { TestResult } from "./TestResult";
import { testStore } from "./TestStore";
import { Condition } from "../Interface";

export class RateStore {
    @observable public testnames: string[];
    public reasons: string[];
    @observable public scores: number[];
    @observable public currIdx: number;
    public condition: Condition;
    public allSurveys: {[key: string]: string};
    @observable public conditionSurveys: string[];
    @observable public surveyScores: number[];
    public finalResponse: string;
    constructor () {
        this.testnames = [];
        this.scores = [];
        this.reasons = [];
        this.currIdx = 0;
        this.loadTest = this.loadTest.bind(this);
        this.onSwitchTest = this.onSwitchTest.bind(this);
        this.rateTest = this.rateTest.bind(this);
        this.submitScores = this.submitScores.bind(this);
        this.reasonRate = this.reasonRate.bind(this);
        this.allSurveys = {
            "qqp_exp": "I had spent more than 2 hours working on the Quora Question Pair dataset before this study.",
            "tests_insightful": "The tests I wrote helped me learn more about the model.",
            'aspects_helpful': 'The aspects provided helped me test the model more thoroughly.',
            'template_helpful': 'The template functionality provided helped me test the model more thoroughly.'
        }
        this.setCondition();
    }

    public setCondition(condition: Condition="C1"): void {
        this.condition = condition;
        switch(condition) {
            case "C2": 
                this.conditionSurveys = [
                    "qqp_exp", 
                    "tests_insightful", 
                    "aspects_helpful"
                ]; 
                break;
            case "C3": 
                this.conditionSurveys = [
                    "qqp_exp", 
                    "tests_insightful", 
                    "aspects_helpful", 
                    "template_helpful"
                ]; 
                break;
            case "C1": 
            default: this.conditionSurveys = ["qqp_exp", "tests_insightful"]; break;

        }
        this.surveyScores = this.conditionSurveys.map(_ => 0);
        this.finalResponse = "";
    }


    public setTestsToRate(
        testnames: string[], 
        testscores: number[]=null,
        reasons: string[]=null): void {
        this.testnames = testnames;
        this.scores = testscores ? testscores : this.testnames.map(_ => 0);
        this.reasons = reasons ? reasons : this.testnames.map(_ => "");
        this.currIdx = 0;
    }

    public loadTest(testname: string): void {
        testStore.testResult = new TestResult(
            testname,  "min_func", "template", 
            {name: "equals", value: "expected"}, []);
    }

    public onSwitchTest(delta: -1|1, isFrontendLoadTest: boolean=true): void {
        const nextIdx = this.currIdx + delta;
        if (nextIdx < 0 || nextIdx > this.testnames.length) {
            return;
        }
        if (isFrontendLoadTest && nextIdx < this.testnames.length) {
            this.loadTest(this.testnames[this.currIdx + delta]);
        }
        this.currIdx += delta;
    }

    public rateTest(score: number): void {
        this.scores[this.currIdx] = score;
    }

    public rateSurvey(score: number, idx: number): void {
        this.surveyScores[idx] = score;
    }

    public reasonRate(reason: string): void {
        this.reasons[this.currIdx] = reason;
    }
    public reasonSurvey(reason: string): void {
        this.finalResponse = reason;
    }

    public submitScores(): void {
        console.log(this.scores, this.reasons);
        console.log(this.conditionSurveys, this.surveyScores);
    }
}

export const rateStore = new RateStore();