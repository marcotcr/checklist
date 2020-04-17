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

    public rate(type: "fail"|"filter"="fail"): number {
        const subset = type === "fail" ? 
            this.nfailed : this.npassed + this.nfailed;
        const total = type === "fail" ? 
        this.nfailed + this.npassed : this.npassed + this.nfailed + this.nfiltered;
        const rate = total ? subset / total : 0;
        return rate;
    }

    public strRate(type: "fail"|"filter", isPad: boolean=false): string {
        const subset = type === "fail" ? 
            this.nfailed : this.npassed + this.nfailed;
        const total = type === "fail" ? 
        this.nfailed + this.npassed : this.npassed + this.nfailed + this.nfiltered;
        const rate = total ? subset / total : 0;
        const rateStr = (rate * 100).toFixed(1) + "%";
        return `${String(subset).padStart(isPad?4:0)} / ${String(total).padStart(isPad?4:0)} = ${rateStr.padStart(isPad?5:0)}`
    }
}