import { observable } from "mobx";
import { TemplateToken } from "./TemplateToken";
import { Template } from "./Template";
import { CandidateDict, RawSentence, MASK, TemplateExampleToken } from "../Interface";
import { candidateDict } from "../FakeData";
import { utils } from "../Utils";

export class TemplateStoreClass {
    public oriSentences: RawSentence[];
    @observable public isReset: boolean;
    @observable public sources: string[];
    @observable public abstractTracker: { [key: string]: number };
    @observable public templates: Template[];
    @observable public suggestDict: CandidateDict;
    @observable public fillInDict: CandidateDict;
    @observable public isLink: boolean;
    @observable public previewExample: {[key: string]: TemplateExampleToken[]}[];
    @observable public expectedValue: string;
    constructor () {
        this.oriSentences = [];
        this.sources = [];
        this.templates = [];
        this.abstractTracker = {};
        this.fillInDict = {};
        this.suggestDict = {};
        this.isLink = false;
        this.isReset = false;
        this.previewExample = [];
        this.expectedValue = "0";
    }

    public setOriToken(sentences: RawSentence[]): void {
        if (sentences) {
            this.oriSentences = sentences;
            this.previewExample = [];
            this.resetSourceMeta();
            this.resetTemplates();
        }
    }

    public setSources(sources: string[]): void {
        if (sources) {
            this.sources = sources;
            this.previewExample = [];
            this.resetSourceMeta();
        }
    }

    public reset(): void {
        this.resetSourceMeta();
        this.resetTemplates();
        this.isReset = !this.isReset;
    }

    public resetSourceMeta(): void {
        // reset everything to nothing created
        const abstractTracker = {};
        this.sources.forEach((s: string) => {
            abstractTracker[s] = 0;
        });
        // also add the MASK versioning
        abstractTracker[MASK] = 0;
        this.abstractTracker = abstractTracker;
        // also reset the fill in dict
        this.fillInDict = {};
        // reset the suggest dict
        this.suggestDict = {};
    }

    public resetTemplates(): void {
        // create the templates
        this.templates = this.oriSentences.map(t => {
            const template = new Template(t.tokens, t.target);
            template.tokens.forEach(token => {
                // set the fill-in dict
                this.fillInDict[token.displayTag()] = [];
                if (token.isAbstract()) {
                    const currVersion = this.abstractTracker[token.tag] || 0;
                    this.abstractTracker[token.tag] = Math.max(token.version, currVersion);
                }
            })
            return template;
        });
    }

    public addNewVerion(source: string, inputVersion: number): string {
        if (!(source in this.abstractTracker)) {
            // add a new version
            this.abstractTracker[source] = 0;
        }
        let version = inputVersion;
        const existingVersion = this.abstractTracker[source];
        let tagVersion = `${source}${version}`;

        if (inputVersion > existingVersion) {
            this.abstractTracker[source] += 1;
            version = this.abstractTracker[source];
            tagVersion = `${source}${version}`;
            this.fillInDict[tagVersion] = [];
        } 
        tagVersion = source === MASK ? `[${tagVersion}]` : `{${tagVersion}}`;
        // return the constructed tag string
        return tagVersion;
    }

    public onChangeFillInDict(token: TemplateToken, fillIns: string[]): void {
        if (token.isAbstract()) {
            this.fillInDict[token.displayTag()] = fillIns;
        }
        this.previewExample = this.computePreviewExamples(this.templates, this.fillInDict);
    }

    public genFakeSuggestions(): void {
        const suggest = {};
        this.templates.forEach(template => {
            template.tokens.forEach((t: TemplateToken, idx: number) => {
                if (t.isAbstract() && !t.isLock) {
                    const tag = t.tag.toLowerCase();
                    suggest[t.displayTag()] = !t.isGeneralMask() && tag in candidateDict ? 
                        candidateDict[tag] : [1,2,3].map(s => `suggest-${s}`);
                }
            });
        });
        this.suggestDict = suggest;
    }

    public computePreviewExamples(templates: Template[], fillInDict: CandidateDict): 
        {[key: string]: TemplateExampleToken[]; }[] {
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
    }
}

export const templateStore = new TemplateStoreClass();
