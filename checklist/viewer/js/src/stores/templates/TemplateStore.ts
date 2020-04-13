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
        const idxes = bertSuggestIdxes.slice(0, 20);
        const examples: TemplateExample[] = [];

        idxes.forEach((tupleIdx: number) => {
            const suggetTuple = this.bertSuggests[tupleIdx];
            const templatesExample: TemplateExampleSentence[] = []
            templates.forEach((template: Template) => {
                let bertIdx: number = -1;
                const exampleSentence: TemplateExampleSentence = [];
                template.tokens.map(t => {
                    bertIdx += t.isGeneralMask() ? 1 : 0;
                    const text = t.isGeneralMask() ? suggetTuple[bertIdx] : t.default;
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
        
        return examples;
    }
}

export const templateStore = new TemplateStoreClass();
