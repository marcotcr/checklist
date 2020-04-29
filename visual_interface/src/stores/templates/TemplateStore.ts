import { observable } from "mobx";
import { Template } from "./Template";
import { TagDict, RawTemplate, BertSuggest, 
    TemplateExampleSentence, TemplateExample } from "../Interface";
import { utils } from "../Utils";

export class TemplateStoreClass {
    public oriSentences: RawTemplate[];
    @observable public templates: Template[];
    @observable public bertSuggests: BertSuggest[];
    @observable public selectedSuggestIdxes: number[];
    @observable public tagDict: TagDict;
    @observable public previewExample: TemplateExampleSentence[][];
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

    public setBertSuggests(suggests: (string[]|string)[]): void {
        if (!suggests) {
            this.bertSuggests = [];
        }
        this.selectedSuggestIdxes = [];
        this.bertSuggests = suggests.map((s: string[]|string) => typeof(s) === "string" ? [s] : s);
    }

    public onChangeSelectedSuggest(idxes: number[]): void {
        this.selectedSuggestIdxes = idxes;
        this.previewExample = this.computePreviewExamples(this.templates, this.selectedSuggestIdxes);
    }

    public computePreviewExamples(templates: Template[], bertSuggestIdxes: number[]): TemplateExample[] {
        const idxes = bertSuggestIdxes.slice(0, 10);
        const examples: TemplateExample[] = [];
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
        const range = (n: number) => [...Array(n).keys()];

        type IdentifierIdx = {idx: number, identifier: string};
        const identifierDict: {[key: string]: IdentifierIdx[]} = {};
        // first, go through all the tokens for once to collect the identifiers
        templates.forEach((template: Template) => {
            template.tokens.map((t) => {
                if (t.isAbstract() && !t.isGeneralMask() && !(t.identifier in identifierDict)) {
                    const totalRange = range(t.candidates.length);
                    identifierDict[t.identifier] = utils
                        .getRandomSubarray(totalRange, 2).map(number => {
                            return { identifier: t.identifier, idx: number }
                        });
                }
            });
        });

        // then get the fill in combinations
        product<IdentifierIdx>(Object.values(identifierDict)).forEach(combine => {
            const combinedDict = {}
            combine.forEach(c => { combinedDict[c.identifier] = c.idx });
            idxes.forEach((tupleIdx: number) => {
                const suggetTuple = this.bertSuggests[tupleIdx];
                const templatesExample: TemplateExampleSentence[] = []
                templates.forEach((template: Template) => {
                    let bertIdx: number = -1;
                    const exampleSentence: TemplateExampleSentence = [];
                    template.tokens.map(t => {
                        bertIdx += t.isGeneralMask() ? 1 : 0;
                        const text = t.isGeneralMask() ? 
                            suggetTuple[bertIdx] : t.isAbstract() ? 
                                t.candidates[combinedDict[t.identifier]] : t.default;
                        if (t.needArticle) {
                            exampleSentence.push({
                                text: utils.genArticle(text), hasTag: t.isAbstract(), 
                                isArticle: true, isMask: t.isGeneralMask()
                            })
                        }
                        exampleSentence.push({
                            text: text, isArticle: false, hasTag: 
                            t.isAbstract(), isMask: t.isGeneralMask()
                        })
                    })
                    templatesExample.push(exampleSentence);
                })
                examples.push(templatesExample);
            });
        });
        return utils.getRandomSubarray(examples, 20);
    }
}

export const templateStore = new TemplateStoreClass();
