import * as React from 'react';
import { observer } from 'mobx-react';

import { Tag, List, Icon } from 'antd';
import { Token, TestInstance } from '../../stores/Interface';
import { TestExample } from '../../stores/tests/TestExample';
import { TemplateToken } from '../../stores/templates/TemplateToken';
import { utils } from '../../stores/Utils';

interface ExampleViewProps {
    example: TestExample;
}

@observer
export class ExampleView extends React.Component<ExampleViewProps, {}> {
    constructor(state: ExampleViewProps, context: any) {
        super(state, context);
    }

    public renderToken(token: TemplateToken): JSX.Element {
        return <span className="token-example">{token.default} </span>
    }

    public renderTemplate(template: TestInstance): JSX.Element {
        return <div >
            <div className="display-table-cell"><span className="token-target">{template.target}</span></div>
            <div className="display-table-cell">
                {this.renderTokens(template["oldText"] || template.text, template.text)}
            </div>
        </div>
    }

    public renderTokens(oldText: string, newText: string): JSX.Element {
        const tokens = utils.computeRewriteStr(oldText, newText);
        return <div>{tokens.map((t: Token, idx: number) => {
            // generate the current class for the token
            const editClass = `token-rewrite-${t.etype}`;
            const curClass = `${utils.genStrId(t.text)}:${t.etype}${t.idx}`;
            // get the current span
            const curSpan: JSX.Element = <span key={ curClass }
                className={`token-example ${editClass}`}>{t.text} </span>;
            return curSpan;
        })}</div>
    }

    public renderTags(): JSX.Element[] {
        const isSuccess = this.props.example.is_succeed;
        const expectIcon = this.props.example.expect === "" || this.props.example.expect === null || this.props.example.expect === undefined ? 
            null: <Tag>Expect: {this.props.example.expect}</Tag>;
        const confStr = this.props.example.conf ? ` (${this.props.example.conf.toFixed(2)})` : "";
        const icons = [expectIcon,
            <Tag>Pred: {this.props.example.pred}{confStr}</Tag>,
            <Icon style={{ fontSize: 20}}
                type={isSuccess ? "check-circle" : "close-circle"}
                theme="twoTone" 
                twoToneColor={isSuccess ? utils.color.success : utils.color.fail} />
        ];
        return icons[0] ? icons : icons.slice(1);
    }

    public render(): JSX.Element {
        if (!this.props.example) { return null; }
        return <List.Item 
            key={this.props.example.key()} className="full-width"
            actions={this.renderTags()}>
            <List.Item.Meta
                description={<div>{this.props.example.instance.map((i, idx) => 
                    <div key={idx}>{this.renderTemplate(i)}</div>)}</div>}/>
        </List.Item>   
    }
}