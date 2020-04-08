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
import { SurveyPanel } from './SurveyPanel';

interface TestRaterProps {
    onSwitchTest: (step: -1|1) => void;
    onSubmit: () => void;
    onSearch: () => void;
    onFetch: () => void;
}

@observer
export class TestRatePanel extends React.Component<TestRaterProps, {}> {

    @observable public modalVisible: boolean;
    public annotation: {[key: number]: string};
    constructor(props: any, context: any) {
        super(props, context);
        this.modalVisible = false;

        this.annotation = {
            1: 'The model does not fail on this test enough for me to consider it a bug.',
            2: 'It fails enough that I think this is a minor bug.',
            3: 'This is a bug that is worth investigating and fixing.',
            4: 'This is a severe bug. I may consider not using this model in production due to this.',
            5: 'This is so severe that no model with this bug should be in production.'
        }
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
    public componentWillUnmount(): void {
        if ((window as any).Jupyter) {
            (window as any).Jupyter.keyboard_manager.enable();
        }
    }

    public renderRate(): JSX.Element {
        return <Radio.Group size="large" className="full-width"
            key={rateStore.currIdx}
            onChange={(e) => {
                rateStore.rateTest(e.target.value);
            }}
            defaultValue={rateStore.scores[rateStore.currIdx] === 0 ? 
                null : rateStore.scores[rateStore.currIdx] }
            name="radiogroup">
            {[1,2,3,4,5].map(score => 
                <Radio 
                    style={{display: "block", whiteSpace: "normal"}}
                    value={score}>
                    <b>{score}</b>{` - ${this.annotation[score]}`}</Radio>)}
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
                defaultValue={rateStore.reasons[rateStore.currIdx]}
                onChange={(e) => {
                    rateStore.reasonRate(e.target.value);
                }}
                placeholder="Please provide a reason for the above rating!" />
    }

    public renderChangeTestBtn() {
        const selectedScore = rateStore.scores[rateStore.currIdx];
        const numOfTests = rateStore.testnames.length;
        return <Button.Group
            style={{textAlign: 'center', width: "100%", marginTop: 20}}>
        {rateStore.currIdx <= numOfTests -1 ?
            <Button  
                // once reach the end, cannot go back.
                disabled={rateStore.currIdx === 0 || rateStore.currIdx === numOfTests}
                onClick={() => this.props.onSwitchTest(-1)}>Previous</Button> : null}
        {rateStore.currIdx <= numOfTests -1 ?
            <Button 
                type="primary" 
                disabled={selectedScore === 0}
                onClick={() => this.props.onSwitchTest(1)}>Next</Button> : null}
        {rateStore.currIdx === numOfTests ?
            <Button type="primary" 
                disabled={rateStore.surveyScores.filter(i => i === 0).length > 0}
                onClick={() => {this.props.onSubmit(); this.modalVisible = true}}
            >Submit</Button> : null}
    </Button.Group>
    }
    public confirmModal(): JSX.Element {
        return <Modal
          visible={this.modalVisible}
          onOk={() => {this.modalVisible = false; }}
          onCancel={null}
          cancelButtonProps={{style: {display: "none"}}}>
          <p>You have completed the survey! Thanks 
              for your participation. You can now close the notebook.</p>
        </Modal>
    }

    public render(): JSX.Element {
        const numOfTests = rateStore.testnames.length;
        let survey = null
        if (rateStore.currIdx < numOfTests) {
            survey = <div>
                <h3>Rate the model given the results for this particular test. What is the severity of this result? </h3>
                <h4>({rateStore.currIdx+1}/{numOfTests} tests in total)</h4>
                {this.renderRate()}
                
                <h3 style={{marginTop: 20}}>Could you explain your rating?</h3>
                {this.renderInput()}
            </div>
        } else {
            survey = <SurveyPanel />
        }
        return <Row>
            {rateStore.currIdx < numOfTests ? 
                <TestSummarizer 
                onFetch={this.props.onFetch}
                onSearch={this.props.onSearch}/> : null}
            <Divider />
            <Alert 
                message={<div>
                    {survey}
                    {this.renderChangeTestBtn()}
                </div>}
            />
            {this.confirmModal()}
        </Row>
    }
}
