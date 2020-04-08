/**
 * Main table for viewing clusters
 */

import * as React from 'react';
import { observer } from 'mobx-react';
import { Row, Radio, Button, Divider, Modal, Alert, Input } from 'antd';
import { TestSummarizer } from '../test_summarizer/TestSummarizer';
import { testStore } from '../../stores/tests/TestStore';
import { rateStore } from '../../stores/tests/RateStore';
import { observable } from 'mobx';


@observer
export class SurveyPanel extends React.Component<{}, {}> {
    constructor(props: any, context: any) {
        super(props, context);
    }

    public componentDidMount() {
        if ((window as any).Jupyter) {
            (window as any).Jupyter.keyboard_manager.disable();
        }
    }
    public componentDidUpdate() {
        if ((window as any).Jupyter) {
            (window as any).Jupyter.keyboard_manager.disable();
        }
    }

    public renderRate(idx: number): JSX.Element {
        return <Radio.Group size="small" className="full-width"
            key={idx}
            onChange={(e) => {
                rateStore.rateSurvey(e.target.value, idx);
            }}
            defaultValue={rateStore.surveyScores[idx] === 0 ? 
                null : rateStore.scores[idx] }
            name="radiogroup">
            {[1,2,3,4,5].map(score => 
                <Radio 
                    style={{whiteSpace: "normal"}}
                    value={score}>{score}</Radio>)}
        </Radio.Group>
    }

    public renderInput(): JSX.Element {
        // this function should collect raw text from the user.
        // Afterwards, it sends the text to the backend
        // Alternatively: can directly set the raw text in store. 
        // so it can be read from backend as well.
        // NOT GOING TO DO THIS FOR NOW because templates can be directly input into changes.
        return <Input 
                className="full-width"
                defaultValue={rateStore.finalResponse}
                onChange={(e) => { rateStore.reasonSurvey(e.target.value); }}
                placeholder="Your final thoughts!" />
    }

    public renderOneQuestion(idx: number) {
        return <Row>
            <Divider className="compact-divider"/>
            <Row>{rateStore.allSurveys[ rateStore.conditionSurveys[idx] ]}</Row>
            <Row>{this.renderRate(idx)}</Row>
        </Row>
    }

    public render(): JSX.Element {
        return <Row>
            <h3>Rate your experience: To what extend do you agree with the following statements?</h3>
            <h4>(from <i>1 - Strongly disagree</i> to <i>5 - Strongly agree</i>)</h4>
            {rateStore.conditionSurveys.map((_, idx: number) => this.renderOneQuestion(idx))}
            <h3 style={{marginTop: 20}}>Do you have any feedback for us?</h3>
                {this.renderInput()}
        </Row>
    }
}
