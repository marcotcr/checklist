import * as React from 'react';

import { VegaLite } from 'react-vega';
import { utils } from '../../stores/Utils';
import { TestStats } from '../../stores/tests/TestStats';

interface TestResultBarProps {
    type: "fail"|"filter";
    data: TestStats[];
}

export class TestStatsViz extends React.Component<TestResultBarProps, {}> {
    public specs: {[key: string]: any};
    public data: {
        count: number, 
        result: string;
        order: number;
        output: "success"|"fail"|"kept"|"filter"
    }[];
    constructor(state: TestResultBarProps, context: any) {
        super(state, context);
        this.specs = {
            "mark": "bar",
            "width": 40,
            "height": 15,
            "data": {name: "myData"},
            "view": {"stroke": null},
            "encoding": {
                "x": { field: "count", type: "quantitative", axis: null},
                "y": {field: "result", type: "nominal", axis: null},
                "order": {field: "order", "type": "quantitative"},
                "color": {field: "output", type: "nominal", legend: null, scale: {
                    domain: ["success", "fail", "kept", "filter"], 
                    range: [ utils.color.success, utils.color.fail, utils.color.kept, utils.color.filter ]
                }}            
            },
            background: null,
            "config": {
                "axis":{"grid":false},
                "axisY": {
                    "minExtent": 70,
                    "maxExtent": 120
                }
            },
        }
        this.data = []

        this.props.data.forEach((t: TestStats) => {
            if (this.props.type === "fail") {
                this.data.push({count: t.nfailed, output: "fail", order: 1, result: t.strRate("fail")});
                this.data.push({count: t.npassed, output: "success",order: 2,result: t.strRate("fail")});
            } else {
                this.data.push({count: t.nfailed, output: "kept", order: 1, result: t.strRate("fail")});
                this.data.push({count: t.npassed, output: "filter",order: 2,result: t.strRate("fail")});
            }
            
        });
    }

    public render(): JSX.Element {        
        return <VegaLite spec={this.specs} data={{myData: this.data}} />
    }
}