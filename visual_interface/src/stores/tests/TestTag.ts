export class TestTag {
    public raw: string;
    public key: string;
    public value: string;

    constructor(rawTag: string) {
        this.raw = rawTag;
        if (rawTag.includes("=")) {
            const [key, value] = rawTag.split("=");
            this.key = key;
            this.value = value;
        } else {
            this.key = "";
            this.value = "";
        }
    }

    public serialize(): {[key: string]: string} {
        return {
            raw: this.raw, key: this.key, value: this.value
        };
    }
}