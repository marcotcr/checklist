import * as jsdiff from 'diff';
import { Token } from "./Interface";

class UtilsClass {
    public color: {success: string, fail: string, kept: string, filter: string};

    constructor() {
        this.color = {
            success: "#1f77b4", fail: "#ff7f0e", kept: "#969696", filter: "#d9d9d9"
        };
    }

    public genArticle(noun: string): string {
        const cases = ['a', 'e', 'i', 'o', 'u'];
        if (noun) {
            return cases.indexOf(noun[0].toLowerCase())> -1 ? "an" : "a";
        } else {
            return ''
        }
    }

    public getRandomArbitrary(min: number, max: number): number {
        return Math.floor(Math.random() * (max - min) + min); 
    }

    public getRandomSubarray<T>(arr: T[], size: number): T[] {
        var shuffled = arr.slice(0), i = arr.length, temp, index;
        while (i--) {
            index = Math.floor((i + 1) * Math.random());
            temp = shuffled[index];
            shuffled[index] = shuffled[i];
            shuffled[i] = temp;
        }
        return shuffled.slice(0, size);
    }

    /**
     * Compute the rewrites.
     * @param {Token[]} oldToken the token series before rewritting
     * @param {Token[]} newToken the token series after rewritting
     * @return get the rewritten serives.
     */
    public computeRewrite(oldToken: (string|Token)[], newToken: (string|Token)[]): Token[] {
        const oldArr = oldToken.map((t: string|Token) => typeof(t) === "string" ? t : t.text);
        const newArr = newToken.map((t: string|Token) => typeof(t) === "string" ? t : t.text);
        const rawDiff = jsdiff.diffArrays(oldArr, newArr);
        // construct the tokenDatum
        let newIdx = 0;
        let oldIdx = 0;
        const tokens: Token[] = [];
        let lastTokenEtype: string = null;
        rawDiff.forEach((diff: {added: boolean, count: number, removed: boolean, value: string[]}) => {
            diff.value.forEach((t: string) => {
                const idx = diff.removed ? oldIdx : newIdx;
                const curT = diff.removed ? oldArr[idx] : newArr[idx];
                const etype: "add"|"keep"|"remove" = diff.removed ? 'remove' : diff.added ? 'add' : 'keep';
                const isReplace = etype === "add" && lastTokenEtype === "remove";
                const curToken = { text: curT, etype: etype, idx: idx, isReplace: isReplace};
                tokens.push(curToken);
                newIdx = diff.removed ? newIdx : newIdx + 1;
                oldIdx = diff.added ? oldIdx : oldIdx + 1;
                lastTokenEtype = etype;
            });
        });
        return tokens;
    }

    public getAttr(obj: any, name: string, defaultReturn: any=null) {
        if ((name in obj)) { return obj[name]; }
        else { return defaultReturn; }
    }

    public objEqual( x: object, y: object): boolean {
        if ( x === y ) { return true; };
        // if both x and y are null or undefined and exactly the same
        if ( !( x instanceof Object ) || !( y instanceof Object ) )  { return false };
        // if they are not strictly equal, they both need to be Objects
        if ( x.constructor !== y.constructor ) { return false; }
        // they must have the exact same prototype chain, the closest we can do is
        // test there constructor.
        // tslint:disable-next-line:no-for-in
        for (let i = 0; i < Object.keys(x).length; i++) {
            const p = Object.keys(x)[i];
            if ( ! x.hasOwnProperty( p ) ) { continue; }
            // other properties were tested using x.constructor === y.constructor
            if ( ! y.hasOwnProperty( p ) ) { return false; }
            // allows to compare x[ p ] and y[ p ] when set to undefined
            if ( x[ p ] === y[ p ] ) { continue; }
            // if they have the same strict value or identity then they are equal
            if ( typeof( x[ p ] ) !== 'object' ) { return false; }
            // Numbers, Strings, Functions, Booleans must be strictly equal
            if ( ! this.objEqual( x[ p ],  y[ p ] ) ) { return false; }
            // Objects and Arrays must be tested recursively
        }
        Object.keys(y).forEach(p => {
            if ( y.hasOwnProperty( p ) && ! x.hasOwnProperty( p ) ) { return false; }
            // allows x[ p ] to be set to undefined
        });
        return true;
    }

    /**
     * Filter and find unique instances in an array
     * Only used to be put in the filter.
     */
    public uniques(value: any, index: any, self: any[]): boolean {
        return self.indexOf(value) === index;
    }

    // group array into hash list by a key
    public groupBy<T> (xs: T[], key: string): {[key: string]: T[]} {
        return xs.reduce((rv, x) => {
            (rv[x[key]] = rv[x[key]] || []).push(x);
            return rv;
        // tslint:disable-next-line:align
        }, { });
    };
    /**
     * Return all permutations of 'length' elements from array:
     * This is a generator function
     * @param array <any[]> just a given array
     * @param length <number> the number the elements in the returned permutations.
     */
    public* permute(array: any[], length: number): any {
        if (length < 1) {
            yield [];
        } else {
            for (const element of array) {
                for (const combination of this.permute(array, length - 1)) {
                    yield combination.concat(element);
                }
            }
        }
    }



    /**
     * Generate all bit combinations for a given number [[true, true, true], ...]
     * Mostly used to generate which model is included when building error intersections.
     * @param count <int> the number of bits needed.
     */
    public genBits(count: number): boolean[][] {
        // tslint:disable-next-line:no-bitwise
        const bool2d: boolean[][] = [];
        // tslint:disable-next-line:no-bitwise
        for (let i = 0; i < (1 << count); i++) {
            const boolArr: boolean[] = [];
            //Increasing or decreasing depending on which direction
            //you want your array to represent the binary number
            for (let j = count - 1; j >= 0; j--) {
                // tslint:disable-next-line:no-bitwise
                boolArr.push(Boolean(i & (1 << j)));
            }
            bool2d.push(boolArr);
        }
        return bool2d;
    }
    public genStrId (key: string|number): string {
        if (typeof key === 'string') {
            return key.replace(/[^a-zA-Z1-9]/g, '-');
        } else {
            return 'number';
        }
    }

    public transpose (a: any[]): any[] {
        return a && a.length && a[0].map && a[0].map((_: any, c: any) => a.map(r => r[c]) || []);
    }
    public argMax(array: number[]) {
        return array.map((x, i) => [x, i]).reduce((r, a) => (a[0] > r[0] ? a : r))[1];
    }

    public clone(obj) {
        let copy;

        // Handle the 3 simple types, and null or undefined
        if (null == obj || "object" != typeof obj) return obj;

        // Handle Date
        if (obj instanceof Date) {
            copy = new Date();
            copy.setTime(obj.getTime());
            return copy;
        }

        // Handle Array
        if (obj instanceof Array) {
            copy = [];
            for (var i = 0, len = obj.length; i < len; i++) {
                copy[i] = this.clone(obj[i]);
            }
            return copy;
        }

        // Handle Object
        if (obj instanceof Object) {
            copy = {};
            for (let attr in obj) {
                if (obj.hasOwnProperty(attr)) copy[attr] = this.clone(obj[attr]);
            }
            return copy;
        }

        throw new Error("Unable to copy obj! Its type isn't supported.");
    }

    public normalizeKey (key: string): string {
        return key.replace(/[^a-zA-Z0-9]/g, '-');
    }

    public intersection(multi_array: any[][]): any[] {
        var result = [];
      var lists = multi_array;
      
      for(var i = 0; i < lists.length; i++) {
          var currentList = lists[i];
          for(var y = 0; y < currentList.length; y++) {
            var currentValue = currentList[y];
          if(result.indexOf(currentValue) === -1) {
            var existsInAll = true;
            for(var x = 0; x < lists.length; x++) {
              if(lists[x].indexOf(currentValue) === -1) {
                existsInAll = false;
                break;
              }
            }
            if(existsInAll) {
              result.push(currentValue);
            }
          }
        }
      }
      return result;
    }

    public pad(num, size): string {
        var s = num+"";
        while (s.length < size) s = "0" + s;
        return s;
    }
}

export const utils = new UtilsClass();
