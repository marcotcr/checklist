import * as React from 'react';
import { observer } from 'mobx-react';

import { List } from 'antd';
import { TemplateExampleToken } from '../../stores/Interface';
import { utils } from '../../stores/Utils';

interface ExampleViewProps {
    example: {[key: string]: TemplateExampleToken[]};
}

@observer
export class ExampleView extends React.Component<ExampleViewProps, {}> {
    constructor(state: ExampleViewProps, context: any) {
        super(state, context);
    }

    public renderToken(token: {text: string; hasTag: boolean; isMask: boolean}): JSX.Element {
        const color = token.isMask ? "token-mask" : token.hasTag ? "token-abstract" : "";
        return <span className={`token-example ${color}`}>{token.text} </span>
    }

    public renderTemplate(target: string, tokens: TemplateExampleToken[]): JSX.Element {
        return <div >
            <div className="display-table-cell"><span className="token-target">{target}</span></div>
            <div className="display-table-cell">
                {this.renderTokens(tokens)}
            </div>
        </div>
    }

    public renderTokens(tokens: TemplateExampleToken[]): JSX.Element {
        return <div>{tokens.map((t: TemplateExampleToken, idx: number) => {
            // generate the current class for the token
            const curClass = `${utils.genStrId(t.text)}:${idx}`;
            const color = t.isMask ? "token-mask" : t.hasTag ? "token-abstract" : "";
            const curSpan = <span key={curClass} className={`token-example ${color}`}>{t.text} </span>
            return curSpan;
        })}</div>
    }

    public render(): JSX.Element {
        if (!this.props.example) { return null; }
        return <List.Item className="full-width">
            <List.Item.Meta
                description={
                <div>{Object.keys(this.props.example).map(
                    (target: string, idx) => 
                        <div key={idx}>
                            {this.renderTemplate(target, this.props.example[target])}
                        </div>
                    )}
                </div>}/>
        </List.Item>
        
        
        
    }
}