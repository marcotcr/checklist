import { TemplateToken } from "./TemplateToken";
import { RawToken, Action } from "../Interface";
import { utils } from "../Utils";
import { observable } from "mobx";
import { testStore } from "../tests/TestStore";
import { templateStore } from "./TemplateStore";

export class Template {
    @observable public tokens: TemplateToken[];
    public target: string;

    constructor (tokens: RawToken[], target: string) {
        this.tokens = tokens.map(t => new TemplateToken(t));
        this.target = target;
        this.editTemplate = this.editTemplate.bind(this);
    }

    public editTemplate(idx: number, content: string, tag: string, action: Action, templates: Template[]): void {
        const newToken = new TemplateToken([content, tag]);
        let nextTokens = this.tokens.slice();
        if (action === "plus") {
            nextTokens = nextTokens.slice(0, idx+1)
                .concat([newToken])
                .concat(nextTokens.slice(idx+1));
        } else if (action === "delete") {
            nextTokens.splice(idx, 1);
        } else {
            nextTokens[idx] = newToken;
        }

        if (action !== "delete" && newToken.isAbstract()) {
            templates.forEach((template: Template) => {
                if (template.key() !== this.key()) {
                    template.tokens = template.tokens.map(
                        t => t.displayTag() === newToken.displayTag() ? 
                        new TemplateToken([content, tag]) : t);
                }
            })
        }
        //this.props.onChangeMask(nextTokens);
        this.tokens = nextTokens;
        templateStore.previewExample = templateStore.computePreviewExamples(
            templateStore.templates, templateStore.fillInDict);
    }

    public key(): string {
        return utils.normalizeKey(`${this.target}:${this.tokens.map(t => t.key()).join("-")}`);
    }

    public serialize(): {tokens: {[key: string]: string|number|boolean}[], target: string } {
        return {
            target: this.target,
            tokens: this.tokens.map(t => t.serialize())
        };
    }
}