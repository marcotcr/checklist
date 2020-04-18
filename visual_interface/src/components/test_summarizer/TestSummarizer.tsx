import * as React from 'react';
import { observer } from 'mobx-react';
import { observable } from "mobx";

import { Row, Col, Divider, Switch, Input, Spin, List, Select, Descriptions } from 'antd';
import { TestResult } from "../../stores/tests/TestResult";

import { TestStatsViz } from './TestResultBar';
import { testStore } from '../../stores/tests/TestStore';
import { TestcaseView as TestExampleView } from './ExampleViewer';
import { TestTag } from '../../stores/tests/TestTag';
import InfiniteScroll from 'react-infinite-scroller';
import { TestExample } from '../../stores/Interface';
import { TestCase } from '../../stores/tests/TestCase';
import { utils } from '../../stores/Utils';
import { TestStats } from '../../stores/tests/TestStats';


interface TestSummarizerProps {
    forceSkip?: boolean;
    onSearch: () => void;
    onFetch: () => void;
}

@observer
export class TestSummarizer extends React.Component<TestSummarizerProps, {}> {
    @observable public loading: boolean;
    constructor(state: TestSummarizerProps, context: any) {
        super(state, context);
        this.loading = true;
        this.handleInfiniteOnLoad = this.handleInfiniteOnLoad.bind(this);
    }

    public renderVizPart(part: "all cases"|"filtered slice", stats: TestStats): JSX.Element {
        return <Row key={stats.key()}>
            {part === "all cases" && stats.nfiltered > 0?
                <div>
                     <div className="info-header">Testcases that pass filtering</div>
                    <span style={{"verticalAlign": "super"}}>
                    <code>{stats.strRate("filter")}</code></span>
                    <span style={{display: "inline"}}>
                        <TestStatsViz data={[stats]} type={"filter"}/></span>
                </div>: null
            }
            <div className="info-header">Failure rate on {part}</div>
            <span style={{"verticalAlign": "super"}}>
            <code>{stats.strRate("fail")}</code></span>
            <span style={{display: "inline"}}>
                <TestStatsViz data={[stats]} type={"fail"}/></span>
        </Row>
    }

    public renderDescription(): JSX.Element {
        const result = testStore.testResult;
        const metas = [];
        const name = result.name;
        const type = result.type.toUpperCase();
        const description = result.description;
        const capability = result.capability ? result.capability.toUpperCase() : "";

        metas.push({
            key: "Test", 
            value: <code>
                <b>{`[${type}] `}</b>
                {capability ? <span>on <b>{`[${capability}] `}</b><br /></span> : null}
                {name ? <span>{name}</span> : null}
            </code>
        });
        if (description) {
            metas.push({key: "Describe", value: <code style={{fontSize: "small"}}>{description}</code>});
        }
        metas.push({
            key: "Result", 
            value: <Row>
                {this.renderVizPart("all cases", testStore.testResult.testStats)}
                <br />
                <Row>{this.renderSearch()}</Row>
                { testStore.testStats.strRate("fail") === testStore.testResult.testStats.strRate("fail") 
                    //|| testStore.searchTags.length === 0 
                ? null :
                    this.renderVizPart("filtered slice", testStore.testStats)}
                </Row>
        })
        
        return <Row>
            <h4 className="header">Test Summary</h4>
            {metas.map(desc => {
                return <Row key={desc.key} gutter={10}>
                    <Col span={5} className={`test-desc title`}>{desc.key}</Col>
                    <Col span={19}  className={`test-desc content`}>{desc.value}</Col>
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
        this.loading = false;
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
        if (!testStore.testResult || this.props.forceSkip) { return null; }
        let baseWidth = 200;
        const increment = 30;
        if (testStore.testResult.testStats.nfiltered) { baseWidth += 50};
        for (let key of ["name", "capability"]) {
            baseWidth += testStore.testResult[key] ? increment : 0;
        }
        const description = testStore.testResult["description"]
        baseWidth += description ? increment * description.split(" ").length / 10  : 0;
        return <Row gutter={30} className="test-summarizer-panel">
            <Col span={10}>{ this.renderDescription() }</Col>
            <Col span={14}>
                <h4 className="header">Examples {this.renderValidChecker()}</h4>
                <Spin spinning={this.loading}>
                <div 
                //key={testStore.testResult.key() + testStore.searchTags.join("-") + `${testStore.failCaseOnly}`}
                style={{maxHeight: baseWidth, overflow: "auto"}}>
                <InfiniteScroll
                    initialLoad={false}
                    pageStart={0}
                    loader={<Spin spinning={this.loading}/>}
                    loadMore={this.handleInfiniteOnLoad}
                    hasMore={!this.loading}
                    useWindow={false}>
                <List itemLayout="horizontal" 
                    size="small"
                    split={true}
                    //key={testStore.testResult.key() + testStore.searchTags.join("-") + `${testStore.failCaseOnly}`}
                    className="compact full-width overflow-y"
                    dataSource={testStore.testcases}
                    renderItem={(testcase: TestCase, idx: number) => {
                        const key = testcase.key();
                        return <List itemLayout="horizontal" 
                        size="small" split={false} key={key}
                        className="testcase-block full-width"
                        style={{ borderColor: testcase.succeed ? utils.color.success : utils.color.fail }}
                        dataSource={testcase.examples}
                        renderItem={(example: TestExample, i: number) => <TestExampleView example={example} />} />
                }}/>
                </InfiniteScroll>
                </div>
                </Spin>
            </Col>
        </Row>
    }
}