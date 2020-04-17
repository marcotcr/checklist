export class TestStats {
    public npassed: number;
    public nfailed: number;
    public nfiltered: number;

    constructor(npassed: number, nfailed: number, nfiltered: number) {
        this.npassed = npassed;
        this.nfailed = nfailed;
        this.nfiltered = nfiltered;
    }

    public key(): string {
        return `${this.nfailed}-${this.npassed}-$${this.nfiltered}`;
    }

    public strRate(type: "fail"|"filter"): string {
        const subset = type === "fail" ? 
            this.nfailed : this.npassed + this.nfailed;
        const total = type === "fail" ? 
        this.nfailed + this.npassed : this.npassed + this.nfailed + this.nfiltered;
        const rate = total ? subset / total : 0;
        const rateStr = (rate * 100).toFixed(1) + "%";
        return `${subset} / ${total} = ${rateStr}`
    }
}