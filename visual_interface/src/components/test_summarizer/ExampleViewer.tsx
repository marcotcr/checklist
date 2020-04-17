import * as React from 'react';
import { observer } from 'mobx-react';

import { Tag, List, Icon } from 'antd';
import { Token, TestExample } from '../../stores/Interface';
import { TemplateToken } from '../../stores/templates/TemplateToken';
import { utils } from '../../stores/Utils';

interface TestcaseViewProps {
    example: TestExample;
}

@observer
export class TestcaseView extends React.Component<TestcaseViewProps, {}> {
    constructor(state: TestcaseViewProps, context: any) {
        super(state, context);
    }

    public replaceArrow(showDisplay: boolean): JSX.Element {
        return showDisplay ? <span className="token rewrite-arrow">→</span> : null;
    }

    public renderToken(token: TemplateToken): JSX.Element {
        return <span className="token-example">{token.default} </span>
    }

    public renderExamples(example: TestExample): JSX.Element {
        const newTokens = example.new.tokens;
        const oldTokens = example.old ? example.old.tokens : example.new.tokens;
        return <div >
            {newTokens.map((newToken: string[], idx: number) => (
                <div>
                <div className="display-table-cell">
                    <span className="sentence-mark-token">></span></div>
                <div className="display-table-cell">
                    {this.renderTokens(oldTokens[idx], newTokens[idx])}
                </div>
                </div>
            ))}
            
        </div>
    }

    public renderTokens(oldTokens: string[], newTokens: string[]): JSX.Element {
        const tokens = utils.computeRewrite(oldTokens, newTokens);
        return <div>{tokens.map((t: Token, idx: number) => {
            // generate the current class for the token
            const replaceClass = t.isReplace ? "" : "no-replace";
            const editClass = `example-token rewrite-${t.etype} ${replaceClass}`;
            const curClass = `${utils.genStrId(t.text)}:${t.etype}${t.idx}`;
            // get the current span
            const curSpan: JSX.Element = <span key={ curClass }>
                <span className={`example-token ${editClass}`}>{t.text}</span>
                <span>{this.replaceArrow(t.isReplace)} </span>                
            </span>;
            return curSpan;
        })}</div>
    }

    public renderTags(): JSX.Element[] {
        const newobj = this.props.example.new;
        const oldobj = this.props.example.old;
        const isSuccess = this.props.example.succeed;
        const expectIcon = this.props.example.label === "" || this.props.example.label === null || this.props.example.label === undefined ? 
            null: <Tag>Expect: {this.props.example.label}</Tag>;
        const confStr = newobj.conf ? ` (${newobj.conf.toFixed(2)})` : "";
        
        let predTag = <Tag>Pred: {newobj.pred}{confStr}</Tag>;
        if (oldobj !== null) {
            const replaceArrow = this.replaceArrow(oldobj !== null);
            const confStrOld = oldobj.conf ? ` (${oldobj.conf.toFixed(2)})` : "";
            predTag = <Tag>
                Pred: <span className="example-token rewrite-remove">{newobj.pred}{confStr}</span>
                {replaceArrow}
                <span className="example-token rewrite-add">{oldobj.pred}{confStrOld}</span>
            </Tag>
        }

        const icons = [expectIcon,
            predTag,
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
            key={1} className="full-width"
            actions={this.renderTags()}>
            <List.Item.Meta description={<div>{this.renderExamples(this.props.example)}</div>}/>
        </List.Item>
    }
}