import * as React from 'react';
import { observer } from 'mobx-react';
import { observable } from "mobx";

import { Row, Col, Divider, Switch, Input, Icon, List, Select, Descriptions } from 'antd';
import { TestResult } from "../../stores/tests/TestResult";

import { TestStatsViz } from './TestResultBar';
import { testStore } from '../../stores/tests/TestStore';
import { TestExample } from '../../stores/tests/TestExample';
import { ExampleView } from './ExampleViewer';
import { TestTag } from '../../stores/tests/TestTag';
import InfiniteScroll from 'react-infinite-scroller';
import { TestStats } from '../../stores/Interface';


interface TestSummarizerProps {
    onSearch: () => void;
    onFetch: () => void;
}

@observer
export class TestSummarizer extends React.Component<TestSummarizerProps, {}> {
    @observable public loading: boolean;
    constructor(state: TestSummarizerProps, context: any) {
        super(state, context);
        this.loading = false;
        this.handleInfiniteOnLoad = this.handleInfiniteOnLoad.bind(this);
    }

    public renderVizPart(part: "all cases"|"filtered slice", stats: TestStats): JSX.Element {
        return <Row key={stats.strResult}>
            <div className="info-header">Failure rate on {part}</div>
            <span style={{"verticalAlign": "super"}}>
            <code>{stats.strResult}</code></span>
            <span style={{display: "inline"}}>
                <TestStatsViz data={[stats]}/></span>
        </Row>
    }

    public renderDescription(): JSX.Element {
        const description = [
            {key: "Name", value: <code>{testStore.testResult.name}</code>},
            //{key: "Category", value: <code>{testStore.testResult.category}</code>},
            //{key: "AuthorType", value: <code>{testStore.testResult.authorType}</code>},
            //{key: "Expect", value: <Descriptions column={1}>
            //    {Object.keys(testStore.testResult.expectationMeta).map((key: string) => 
            //        <Descriptions.Item label={key} key={key}>{testStore.testResult.expectationMeta[key]}</Descriptions.Item>)}
            //</Descriptions>},
            {key: "Result", 
            value: <Row>
                {this.renderVizPart("all cases", testStore.testResult.testStats)}
                <br />
                <Row>{this.renderSearch()}</Row>
                { testStore.testStats.strResult === testStore.testResult.testStats.strResult 
                    //|| testStore.searchTags.length === 0 
                ? null :
                    this.renderVizPart("filtered slice", testStore.testStats)}
                </Row>
            }
        ];
        
        return <Row>
            <h4 className="header">Test Summary</h4>
            {description.map(desc => {
                return <Row key={desc.key} gutter={30}>
                    <Col span={6} className={`test-desc title`}>{desc.key}</Col>
                    <Col span={18}  className={`test-desc content`}>{desc.value}</Col>
                    <Divider className="compact-divider"/>
                </Row>
            })}
        </Row>
        /*
       return <Descriptions title="Test description" size="small" column={1}>
            {description.map(desc => {
                return <Descriptions.Item key={desc.key} label={desc.key}>{desc.value}</Descriptions.Item>
            })}
            </Descriptions>
            */
    }

    public renderSearch(): JSX.Element {
        const tags: {[key: string]: TestTag[]} = {};
        testStore.testResult.tags.forEach(t => {
            if (!(t.key in tags)) {
                tags[t.key] = []
            }
            tags[t.key].push(t);
        });
        return <Input.Group 
            key={testStore.testResult.tags.length}
            size="small" style={{width: "100%", maxHeight: 50, verticalAlign:"middle"}}>
        <div className="info-header">Filter test cases</div>
        <Select
            maxTagTextLength={10}
            mode="tags"
            placeholder={testStore.testResult.tags.length > 0 ? "Select tags or input free text" : "Input free text and enter"}
            size="small"
            showSearch={true}
            dropdownStyle={testStore.testResult.tags.length > 0 ? null : {display: "none"}}
            optionFilterProp="value"
            optionLabelProp="value"
            className="overflow-y"
            //suffixIcon={<Icon type="filter" onClick={() => {testStore.search()}}></Icon>}
            style={{width: "100%", maxHeight: 45}}
            defaultValue={testStore.searchTags}
            onChange={(v) => {
                testStore.setSearchTags(v as string[]);
                this.props.onSearch();
            }}>
            {Object.keys(tags).map(key => <Select.OptGroup key={key}>
                {tags[key].map(t => <Select.Option value={t.raw} key={t.raw}>{t.value}</Select.Option>)}
            </Select.OptGroup>)}
        </Select>
        {/*<Icon  style={{paddingLeft: 5, verticalAlign:"super"}} type="filter" 
            onClick={(e) => {e.preventDefault(); this.props.onSearch()}}></Icon>*/}
        </Input.Group> 
    }

    public renderValidChecker(): JSX.Element {
        return <span>
        <Switch
                size="small"
                onChange={() => { 
                    testStore.togglefailCaseFilter();
                    this.props.onSearch();
                }}
                checkedChildren={<span>Failed cases only</span>}
                unCheckedChildren={<span>Sample all cases</span>}
                checked={testStore.failCaseOnly}/>
        </span>
    }

    public handleInfiniteOnLoad(): void {
        this.loading = true;
        this.props.onFetch();
        this.loading = false;
    }
    public componentDidMount() {
        this.props.onFetch();
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

    public render(): JSX.Element {
        if (!testStore.testResult) { return null; }
        return <Row gutter={50}>
            <Col span={10}>{ this.renderDescription() }</Col>
            <Col span={14}>
                <h4 className="header">Examples {this.renderValidChecker()}</h4>
                <div 
                //key={testStore.testResult.key() + testStore.searchTags.join("-") + `${testStore.failCaseOnly}`}
                style={{maxHeight: 200, overflow: "auto"}}>
                <InfiniteScroll
                    initialLoad={false}
                    pageStart={0}
                    loadMore={this.handleInfiniteOnLoad}
                    hasMore={!this.loading}
                    useWindow={false}>
                <List itemLayout="horizontal" 
                    size="small"
                    //key={testStore.testResult.key() + testStore.searchTags.join("-") + `${testStore.failCaseOnly}`}
                    className="compact full-width overflow-y"
                    dataSource={testStore.examples}
                    renderItem={(example: TestExample) =>
                        <List.Item key={example.key()}>
                            <ExampleView example={example} />
                        </List.Item>} />
                </InfiniteScroll>
                </div>
            </Col>
        </Row>
    }
}