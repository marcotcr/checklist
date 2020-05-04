import * as React from 'react';
import { observer } from 'mobx-react';
import { Table, Divider, Card } from 'antd';
import { suiteStore } from '../../stores/tests/SuiteStore';
import { TestType } from '../../stores/Interface';
import { utils } from '../../stores/Utils';
import { TestResult } from '../../stores/tests/TestResult';
import { TestStatsViz } from '../test_summarizer/TestResultBar';
import { testStore } from '../../stores/tests/TestStore';
import { TestSummarizer } from "../test_summarizer/TestSummarizer"; 
import { TestStats } from '../../stores/tests/TestStats';

import * as d3Scale from 'd3-scale';

interface SuiteSummarizerProps {
  	onSelect: (testname: TestResult) => void;
  	onSearch: () => void;
    onFetch: () => void;
}

type CellValue = {
  key: string;
  tests: TestResult[];
}

type CellType = {
	key: string;
  	capability: string;
	mft: CellValue;
	inv: CellValue;
	dir: CellValue;
}

const headerMapper: {[key: string]: JSX.Element} = {
	mft: <span><b>M</b>inimum <b>F</b>unctionality <b>T</b>est</span>,
	inv: <span><b>INV</b>ariance Test</span>,
	dir: <span><b>DIR</b>ectional Expectation</span>
}

@observer
export class SuiteSummarizer extends React.Component<SuiteSummarizerProps, {}> {
	public colorScale: any;
	public colorFontScale: any;
	constructor(state: SuiteSummarizerProps, context: any) {
        super(state, context);
		this.renderPerCapability = this.renderPerCapability.bind(this);
		this.colorScale = d3Scale.scaleQuantize()
			.domain([0, 1])
			.range(["#3182bd", "#9ecae1", "#bdbdbd", "#fdae6b", "#e6550d"]);
		this.colorFontScale = d3Scale.scaleQuantize()
			.domain([0, 1])
			.range(["white", "black", "black", "black", "white"]);
		this.colorScale = this.colorScale.bind(this);
		this.colorFontScale = this.colorFontScale.bind(this);
		this.renderTable = this.renderTable.bind(this);
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

	public renderPerType(tests: TestResult[], maxNameLength: number): JSX.Element {
		// first, get the types
		const sources = tests.map(t => {
			return {
				name: t.name, 
				key: t.key(), 
				test: t,
				fail_rate: t.testStats}
		});

		const columns: any[] = [
			{ 
				title: 'test name', dataIndex: 'name', key: 'name',
				className: "test-name-col",
				render: (name: string, __, _) => <pre 
					style={{ marginTop: 0, marginBottom: -1}}>{name.padEnd(maxNameLength)}</pre>
			}, { 
				title: 'failure rate', dataIndex: 'fail_rate', key: 'fail_rate', 
				className: "test-stat-col",
				render: (stats: TestStats, __, _) => <div style={{ marginTop: 0, marginBottom: -5}}>
					<pre>
						<span style={{"verticalAlign": "super", display: "inline"}}>
							<code>{stats.strRate("fail", true)}</code></span>
						<span style={{display: "inline", marginLeft: 10}}>
						<TestStatsViz data={[stats]} type={"fail"}/></span>
					</pre>
				</div>
			},
		]
		type RecordType = {name: string, key: string, test: TestResult, fail_rate: TestStats};
		//console.log(testStore.testResult)
		return <Table size="small" bordered className="full-width"
			expandedRowKeys={testStore.testResult ? [testStore.testResult.key()] : []}
			onExpand={
				(expanded: boolean, record: RecordType) => {
				//if (expanded) {
				this.props.onSelect(record.test);
				//} else {
				//	this.props.onSelect(null);
				//}
			}}
			rowKey={(row) => row.key}
			expandedRowRender={(record: {name: string, key: string, fail_rate: TestStats}) => {
				const selectedTest = testStore.testResult;
				const selectedKey = selectedTest ? selectedTest.key() : "NOT-A-KEY";
				return selectedKey === record.key ? <div
					className="full-width"
					style={{backgroundColor: "white"}}
					><TestSummarizer 
					forceSkip={selectedKey !== record.key}
					key={`${record.key} ${selectedKey}`}
					onFetch={() => {this.props.onFetch()}}
					onSearch={() => {this.props.onSearch()}} /></div> : null
			}}
			pagination={false}
			dataSource={sources} columns={columns} />;
	}

	public renderPerCapability(row: CellType): JSX.Element {
		const types: TestType[] = ["mft", "inv", "dir"];
		const maxNameLength = Math.max(...types.map(ttype => 
				Math.max(...row[ttype].tests.map(t => t.name.length))))
		return <div key={row.capability}>
		{types.map(ttype => {
			const tests = row[ttype].tests//.sort((a, b) => b.testStats.rate("fail") - a.testStats.rate("fail"));
			
			return tests.length > 0 ? <div key={ttype} className="full-width">
				<Divider ><span className="info-header">{headerMapper[ttype]}</span></Divider>
				{this.renderPerType(tests, maxNameLength)} 
			</div> : null
		})}
		</div>
	}

	public renderTable(): JSX.Element {
		const tests = suiteStore.overviewTests;
		// first, get the types
		const types: TestType[] = ["mft", "inv", "dir"];
		let capabilities: string[] = tests.map(t => t.capability).filter(utils.uniques);
		const order = ['Vocabulary', 'Taxonomy', 'Robustness', 'NER',  'Fairness', 'Temporal', 'Negation', 'Coref', 'SRL', 'Logic'];
		const testsByCaps = utils.groupBy(tests, "capability");
		const sources = [];
		const capOrder = (a: string) => order.indexOf(a) === -1 ? 200 : order.indexOf(a);
		capabilities = capabilities.sort((a, b) => capOrder(a) - capOrder(b));
		capabilities.forEach((cap: string) => {
			const localTests = cap in testsByCaps ? testsByCaps[cap] : [];
			const testsByType = utils.groupBy(localTests, "type");
			const curSource = { key: cap, capability: cap };
			types.forEach((ttype: TestType) => {
				const cellTests = ttype in testsByType ? testsByType[ttype] : [];
				curSource[ttype] = {
					key: `${ttype}-${cap}`,
					tests: cellTests,
				}
			});
			sources.push(curSource as CellType);
		})

		const columns: any[] = [{ 
			title: 'Capabilities', dataIndex: 'capability', key: 'capability',
		}]
		types.forEach(ttype => {
		columns.push({
			title: <div>
				<div>{headerMapper[ttype]}</div>
				<small><i>failure rate % (over N tests)</i></small>
			</div>, 
			dataIndex: ttype, key: ttype,
			render: (cell, row, _) => {
				const tests = cell.tests;
				const nTests = tests.length;
				const avgRate = nTests === 0 ? 0 : Math.max(...tests.map(t => t.testStats.rate("fail")));
				const rateStr = (avgRate * 100).toFixed(1) + "%";
				return {
						props: {
						  style: { 
							  background: nTests === 0 ? "white" : this.colorScale(Math.cbrt(avgRate)),
							  //boxShadow: "inset 0px 0px 0px 5px white" ,
							  //boxSizing: "border-box",
							  color: this.colorFontScale(Math.cbrt(avgRate))
							}
						},
						children: <div key={ttype}>{nTests > 0 ? `${rateStr} (${nTests})` : null}</div>
					};
				}
			})
		})
		return <Table 
			className="full-width"
			key={tests.map(t => t.key()).join("-")}
			pagination={false}
			rowKey={(row: CellType) => row.capability}
			expandedRowRender={this.renderPerCapability}
			dataSource={sources} columns={columns} />;
	}

	public render(): JSX.Element {
		console.log(testStore.testResult)
		if (!suiteStore.overviewTests) { return null; }
		return this.renderTable();
	}
}