import { TemplateToken } from "./TemplateToken";
import { RawTemplate } from "../Interface";
import { utils } from "../Utils";
import { observable } from "mobx";

export class Template {
    @observable public tokens: TemplateToken[];

    constructor (tokens: RawTemplate) {
        this.tokens = tokens.map(t => new TemplateToken(t));
    }

    public key(): string {
        return utils.normalizeKey(`${this.tokens.map(t => t.key()).join("-")}`);
    }

    public serialize(): {tokens: {[key: string]: string|number|boolean}[] } {
        return {
            tokens: this.tokens.map(t => t.serialize())
        };
    }
}