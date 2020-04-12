import * as React from 'react';
import { Layout, Card } from 'antd';
import { rawTestResult, rawTestcases, tagDict, rawTemplates, suggests } from '../stores/FakeData';
import { TemplateEditor } from './template_editor/TemplateEditor';
import { observer } from 'mobx-react';
import { templateStore } from '../stores/templates/TemplateStore';
import { testStore } from '../stores/tests/TestStore';
import { TestSummarizer } from './test_summarizer/TestSummarizer';

@observer
export class App extends React.Component<{}, {}> {

    public async componentWillMount(): Promise<void> {
        templateStore.setTagDict(tagDict);
        templateStore.setBertSuggests(suggests);
        templateStore.setTemplate(rawTemplates);
        testStore.setTest(rawTestResult);
        testStore.setTestcases(rawTestcases);
        testStore.randomTestStats();
    }
    
    public render(): JSX.Element {
        return (
            <Layout>
                <Layout.Content style={{ padding: '50px 50px' }}>
                <Card>
                <TemplateEditor onChangeSelected={(idx: number[]) => {console.log(idx)}} />
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