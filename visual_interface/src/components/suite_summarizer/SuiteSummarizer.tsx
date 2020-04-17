import * as React from 'react';
import { observer } from 'mobx-react';
import { Table } from 'antd';
import { suiteStore } from '../../stores/tests/SuiteStore';
import { TestType } from '../../stores/Interface';
import { utils } from '../../stores/Utils';


interface SuiteSummarizerProps {
    onSelect: (testname: string) => void;
}

@observer
export class SuiteSummarizer extends React.Component<SuiteSummarizerProps, {}> {
    public renderTable(): JSX.Element {
        const tests = suiteStore.overviewTests;
        // first, get the types
        const types: TestType[] = ["mft", "inv", "dir"];
        const capabilities: string[] = tests.map(t => t.capability).filter(utils.uniques);

        const testsByCaps = utils.groupBy(tests, "capabilities");

        const sources = [];

        capabilities.forEach((cap: string) => {
            const localTests = cap in testsByCaps ? testsByCaps[cap] : [];
            const testsByType = utils.groupBy(localTests, "capability");
            const curSource = { "capability": cap };
            types.forEach((ttype: TestType) => {
                const cellTests = ttype in testsByType ? testsByType[ttype] : [];
                curSource[ttype] = {
                    tests: cellTests,
                }
            });
            sources.push(curSource);
        })
        console.log(sources);

        const dataSource = [
            {
              key: '1',
              name: 'Mike',
              age: 32,
              address: '10 Downing Street',
            },
            {
              key: '2',
              name: 'John',
              age: 42,
              address: '10 Downing Street',
            },
          ];
          
          const columns = [
            {
              title: 'Name',
              dataIndex: 'name',
              key: 'name',
            },
            {
              title: 'Age',
              dataIndex: 'age',
              key: 'age',
            },
            {
              title: 'Address',
              dataIndex: 'address',
              key: 'address',
            },
          ];
          
        return <Table dataSource={dataSource} columns={columns} />;
    }

    public render(): JSX.Element {
        if (!suiteStore.overviewTests) { return null; }
        return this.renderTable();
    }
}