import { RawToken, MASK } from "../Interface";
import { utils } from "../Utils";
import { observable } from 'mobx';
import { version } from "moment";
import { Template } from "./Template";
import { templateStore } from "./TemplateStore";


export class TemplateToken {
    @observable public isLock: boolean;
    @observable public default: string;
    @observable public tag: string;
    @observable public version: number;

    constructor (token: RawToken) {
        if (typeof token === "string") {
            this.default = token as string;
            this.convertTag("");
        } else {
            this.default = token[0];
            this.convertTag(token[1]);
        }
        // lock all the unnecessary actions
        this.isLock = this.tag === "";
    }

    public toggleLock(templates: Template[]): void {
        if (!this.isLock) {
            this.isLock = true
            if (this.displayTag() in templateStore.fillInDict) {
                delete templateStore.fillInDict[this.displayTag()];
            }
        } else if (this.isLock && this.tag !== "") {
            this.isLock = false;
        }
        templates.forEach((template: Template) => {
            template.tokens.forEach(t => {
                if (t.displayTag() === this.displayTag()) {
                    t.isLock = this.isLock;
                }
            });
        })
        templateStore.previewExample = templateStore.computePreviewExamples(
            templateStore.templates, templateStore.fillInDict);
    }

    public convertTag(rawTag_: string): void {
        const regex = /[\{|\[]*([\D]+)(\d*)[\}|\]]*/;
        const [rawTag, tag, version] = regex.exec(rawTag_) || [rawTag_, rawTag_, 1];
        this.version = Number(version);
        this.tag = (tag as string).toLowerCase();
    }

    public isSelectedTag(tag: string): boolean {
        tag = tag.toLowerCase();
        return tag === this.tag || (tag && this.tag.includes(tag));
    }

    public key(): string {
        return utils.normalizeKey(`${this.tag}-${this.version}:${this.default}`);
    }

    public isGeneralMask(): boolean {
        return this.tag === MASK;
    }

    public isAbstract(): boolean {
        return this.tag && this.tag !== "" ;//&& !this.isGeneralMask();
    }

    public displayTag(useBracelet: boolean=false): string {
        if (!this.isAbstract()) {
            return "";
        }
        let tagVersion = `${this.tag}${this.version}`;
        if (useBracelet) {
            tagVersion = this.isGeneralMask() ? `[${tagVersion}]` : `{${tagVersion}}`;
        }
        return tagVersion;
    }

    public serialize(): {[key: string]: string|number|boolean} {
        return {
            default: this.default,
            version: this.version,
            display_tag: this.displayTag(),
            tag: this.tag,
            is_lock: this.isLock
        };
    }
}