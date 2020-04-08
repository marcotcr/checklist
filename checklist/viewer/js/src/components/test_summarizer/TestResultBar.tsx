import * as React from 'react';
import { TestStats } from '../../stores/Interface';

import { VegaLite } from 'react-vega';
import { utils } from '../../stores/Utils';

interface TestResultBarProps {
    data: TestStats;
}


export class VegaLiteViz extends React.Component<{data: any}, {}> {
    public specs: {[key: string]: any};
    public data: {
        count: number, 
        result: string;
        order: number;
        output: "success"|"fail"
    }[];
    constructor(state: TestResultBarProps, context: any) {
        super(state, context);
        this.specs = {
            "mark": "bar",
            "encoding": {
                "x": { "field": "count", "type": "quantitative"},
                "y": {"field": "slice", "type": "nominal"},
                "color": {"field": "output", "type": "nominal"}
            }
        }
        this.data = [];
    }

    public render(): JSX.Element {
        this.data = [];
        this.props.data.forEach((t: TestStats) => {

            
            this.data.push({
                count: t.nFailed, 
                output: "fail",
                order: 1,
                result: t.strResult
            });
            this.data.push({
                count: t.nTested - t.nFailed, 
                output: "success",
                order: 2,
                result: t.strResult
            });
        });
        return <VegaLite spec={this.specs} data={{myData: this.data}} />
    }
}

export class TestStatsViz extends VegaLiteViz {
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
                    domain: ["success", "fail", ], range: [ utils.color.success, utils.color.fail ]}}            
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
        this.data = [];
    }
}