import * as React from 'react';
import { Layout, Card } from 'antd';
import { candidateNames, rawSentences, rawTestResult, rawExamples, testnames } from '../stores/FakeData';
import { TemplateEditor } from './template_editor/TemplateEditor';
import { observer } from 'mobx-react';
import { templateStore } from '../stores/templates/TemplateStore';
import { testStore } from '../stores/tests/TestStore';
import { TestSummarizer } from './test_summarizer/TestSummarizer';
import { rateStore } from '../stores/tests/RateStore';
import { TestRatePanel } from './test_rater/TestRatePanel';

@observer
export class App extends React.Component<{}, {}> {

    public async componentWillMount(): Promise<void> {
        templateStore.setSources(candidateNames);
        templateStore.setOriToken(rawSentences);
        testStore.setTest(rawTestResult);
        testStore.setExamples(rawExamples);
        testStore.randomTestStats();
        rateStore.setTestsToRate(testnames);
    }
    
    public render(): JSX.Element {
        return (
            <Layout>
                <Layout.Content style={{ padding: '50px 50px' }}>
                <Card>
                <TestRatePanel
                    onSwitchTest={rateStore.onSwitchTest}
                    onSubmit={rateStore.submitScores}
                    onFetch={testStore.fetchMoreExample}
                    onSearch={testStore.search} />
                </Card>
                <Card>
                <TemplateEditor key={`${templateStore.isReset}`}
                    onExtendWordList={null}
                    onReset={() => { templateStore.reset() }}
                    onGetSuggestion={() => {
                        templateStore.genFakeSuggestions();
                    }}
                    onConfirmFillIn={() => { console.log("onConfirmFillIn", templateStore.fillInDict) }} />
                </Card>

                <Card>
                <TestSummarizer 
                    key={`${testStore.testResult ? testStore.testResult.key() : ""}`}
                    onFetch={ () => {testStore.fetchMoreExample ()}}
                    onSearch={() => { testStore.search() }} />
                </Card>
                </Layout.Content>
            </Layout>
        );
    }
}