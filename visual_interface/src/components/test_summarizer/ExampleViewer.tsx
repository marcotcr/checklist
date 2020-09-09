import * as React from 'react';
import { observer } from 'mobx-react';

import { Row, Tag, List, Col, Icon } from 'antd';
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
        return showDisplay ? <div className="example-token wrap rewrite-arrow">→</div> : null;
    }

    public renderToken(token: TemplateToken): JSX.Element {
        return <span className="token-example">{token.default} </span>
    }

    public renderExamples(example: TestExample): JSX.Element {
        const newTokens = example.new.tokens;
        const oldTokens = example.old ? example.old.tokens : example.new.tokens;
        return <div >
            {newTokens.map((newToken: string[], idx: number) => (
                <div key={idx}>
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

    public renderTags(): JSX.Element {
        const tagWrapper = (text: string) => <span 
            style={{
                margin: "2px 4px",
                padding: "2px 4px",
                fontWeight: "bold",
                backgroundColor: "#f3f3f3", color: "grey"}}>
                {text}</span>
        const wrapper = (text: string) => <div className="wrap example-token">{text}</div>
        const newobj = this.props.example.new;
        const oldobj = this.props.example.old;
        const isSuccess = this.props.example.succeed;
        const expectIcon = this.props.example.label === "" || this.props.example.label === null || this.props.example.label === undefined ? 
            null: <span>
                {tagWrapper("Expect")}
                {wrapper(this.props.example.label)}
                <span style={{color: "lightgray", fontWeight: "bold"}}>{` | `}</span>
                </span>;
        const confStr = newobj.conf ? ` (${newobj.conf.toFixed(2)})` : "";
    
        let predTag = <div className="pred-tag">
            {expectIcon}
            {tagWrapper("Pred")}
            {wrapper(newobj.pred + confStr)}
            </div>;
        if (oldobj !== null) {
            const replaceArrow = this.replaceArrow(oldobj !== null);
            const confStrOld = oldobj.conf ? ` (${oldobj.conf.toFixed(2)})` : "";
            predTag = <div className="pred-tag">
                {tagWrapper("Pred")}
                <div className="wrap example-token rewrite-remove">{oldobj.pred}{confStrOld}</div>
                {replaceArrow}
                <div className="wrap example-token rewrite-add">{newobj.pred}{confStr}</div>
            </div>
        }

        return <span>
            {predTag}
            <Icon style={{ fontSize: 16, verticalAlign: "middle"}}
                type={isSuccess ? "check-circle" : "close-circle"}
                theme="twoTone" 
                twoToneColor={isSuccess ? utils.color.success : utils.color.fail} />
        </span>;
    }

    public render(): JSX.Element {
        if (!this.props.example) { return null; }
        return <Row>
            <Col sm={24} md={24} lg={24} xl={13}>
                {this.renderExamples(this.props.example)}
            </Col>
            <Col sm={24} md={24} lg={24} xl={11}
                style={{textAlign: "right"}}>
                {this.renderTags()}
            </Col>
        </Row>
    }
}