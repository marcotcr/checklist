import { observable } from "mobx";
import { Template } from "./Template";
import { TagDict, RawTemplate, TemplateExampleToken, BertSuggest } from "../Interface";

export class TemplateStoreClass {
    public oriSentences: RawTemplate[];
    @observable public templates: Template[];
    @observable public bertSuggests: BertSuggest[];
    @observable public selectedSuggestIdxes: number[];
    @observable public tagDict: TagDict;
    @observable public previewExample: {[key: string]: TemplateExampleToken[]}[];
    constructor () {
        this.oriSentences = [];
        this.templates = [];
        this.tagDict = {};
        this.bertSuggests = [];
        this.selectedSuggestIdxes = [];
        this.previewExample = [];
    }

    public setTagDict(tagDict: TagDict): void {
        this.tagDict = tagDict;
    }

    public setTemplate(rawTemplates: RawTemplate[]): void {
        if (rawTemplates) {
            this.previewExample = [];
            this.templates = rawTemplates.map(rtemplate => new Template(rtemplate));
        }
    }

    public setBertSuggests(suggests: BertSuggest[]): void {
        this.bertSuggests = suggests;
    }

    public onChangeSelectedSuggest(idxes: number[]): void {
        this.selectedSuggestIdxes = idxes;
        this.previewExample = this.computePreviewExamples(this.templates, this.selectedSuggestIdxes);
    }

    public computePreviewExamples(templates: Template[], bertSuggests: number[]): 
        {[key: string]: TemplateExampleToken[]; }[] {
        return [];
        /*
        const output = [];
        const combinations = [];
        const hash = [];
        function product<T>(array: T[][]): T[][] {
            let results = [[]];
            for (var i = 0; i < array.length; i++) {
                const currentSubArray = array[i];
                const temp = [];
                for (let j = 0; j < results.length; j++) {
                    for (let k = 0; k < currentSubArray.length; k++) {
                        temp.push(results[j].concat(currentSubArray[k]));
                    }
                }
                results = temp;
            }
            return results;
        }

        Object.keys(fillInDict).map((displayTag: string) => {
            if (fillInDict && fillInDict[displayTag].length > 0) {
                const fillIns = fillInDict[displayTag];
                combinations.push(fillIns.map(f => {
                    return {displayTag: displayTag, fillIn: f} 
                }));
            }
        });
        product<{displayTag: string, fillIn: string}>(combinations).forEach(combine => {
            const combinedDict = {}
            combine.forEach(c => { combinedDict[c.displayTag] = c.fillIn });  
            const filledIn = {}        
            templates.forEach(template => {
                const tokens = template.tokens.map(t => {
                    const text = t.displayTag() in combinedDict ? 
                        combinedDict[t.displayTag()] : t.default;
                    return {text: text, hasTag: t.isAbstract(), isMask: t.isGeneralMask()}
                });
                filledIn[template.target] = tokens;

            });
            const key = Object.keys(filledIn).map(target => `target:${target}-text:${filledIn[target].map(t =>t.text).join("+")}`).join(":");
            if (hash.indexOf(key) === -1) {
                hash.push(key);
                output.push(filledIn);
            }
        });
        return utils.getRandomSubarray(output, 20);
        */
    }
}

export const templateStore = new TemplateStoreClass();
