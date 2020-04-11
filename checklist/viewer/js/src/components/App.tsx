import * as React from 'react';
import { Layout, Card } from 'antd';
import { candidateNames, rawSentences, rawTestResult, rawExamples as rawTestcases } from '../stores/FakeData';
import { TemplateEditor } from './template_editor/TemplateEditor';
import { observer } from 'mobx-react';
import { templateStore } from '../stores/templates/TemplateStore';
import { testStore } from '../stores/tests/TestStore';
import { TestSummarizer } from './test_summarizer/TestSummarizer';

@observer
export class App extends React.Component<{}, {}> {

    public async componentWillMount(): Promise<void> {
        templateStore.setSources(candidateNames);
        templateStore.setOriToken(rawSentences);
        testStore.setTest(rawTestResult);
        testStore.setTestcases(rawTestcases);
        testStore.randomTestStats();
    }
    
    public render(): JSX.Element {
        return (
            <Layout>
                <Layout.Content style={{ padding: '50px 50px' }}>
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