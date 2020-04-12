import { utils } from "../Utils";
import { RawTemplateToken } from "../Interface";


export class TemplateToken {
    public default: string;
    public tag: string;
    public normalizeTag: string;
    public needArticle: boolean;

    constructor (token: RawTemplateToken) {
        if (typeof token === "string") {
            this.default = token as string;
            this.convertTag("");
        } else {
            this.default = token[0];
            this.convertTag(token[1]);
        }
    }

    public convertTag(rawTag_: string): void {
        this.needArticle = rawTag_.startsWith("a:");
        this.normalizeTag = rawTag_.split("a:")[rawTag_.split("a:").length-1];
        this.tag = rawTag_;
    }

    public key(): string {
        return utils.normalizeKey(`${this.tag}:${this.default}`);
    }

    public isGeneralMask(): boolean {
        return this.normalizeTag.replace(/\d+$/, "").toLowerCase() === "bert";
    }

    public isAbstract(): boolean {
        return this.tag && this.tag !== "" ;//&& !this.isGeneralMask();
    }

    public isEmptyMask(): boolean {
        return this.isGeneralMask() && this.default === "";
    }

    public displayStr(): string {
        return this.isEmptyMask() ? this.displayTag() : this.default;
    }

    public displayTag(useBracelet: boolean=false): string {
        if (useBracelet) {
            return this.isGeneralMask() ? `[${this.tag}]` : `{${this.tag}}`;
        } else {
            return this.tag;
        }
    }

    public serialize(): {[key: string]: string|number|boolean} {
        return {
            default: this.default,
            display_tag: this.displayTag(),
            tag: this.tag,
        };
    }
}