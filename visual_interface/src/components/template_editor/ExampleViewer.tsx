import * as React from 'react';
import { observer } from 'mobx-react';

import { List } from 'antd';
import { TemplateExampleToken, TemplateExample, TemplateExampleSentence } from '../../stores/Interface';
import { utils } from '../../stores/Utils';

interface ExampleViewProps {
    example: TemplateExample;
}

@observer
export class ExampleView extends React.Component<ExampleViewProps, {}> {
    constructor(state: ExampleViewProps, context: any) {
        super(state, context);
    }

    public renderToken(token: TemplateExampleToken): JSX.Element {
        if (!token || !token.text) {
            return null;
        }
        const color = token.isMask ? "token-mask" : token.hasTag ? "token-abstract" : "";
        const article = token.isArticle ? "article-token" : "";
        return <span className={`token-example ${color} ${article}`}>{token.text} </span>
    }

    public renderTemplate(sentence: TemplateExampleSentence): JSX.Element {
        return <div >
            <div className="display-table-cell">
                <span className="sentence-mark-token">></span></div>
            <div className="display-table-cell">
                {sentence.map((t: TemplateExampleToken, idx: number) => {
                    // generate the current class for the token
                    const curClass = `${utils.genStrId(t.text)}:${idx}`;
                    const color = t.isMask ? "mask-token" : t.hasTag ? "abstract-token" : "";
                    const article = t.isArticle ? "article-token" : "";
                    const curSpan = <span key={curClass}>
                        <span className={`example-token ${color} ${article}`}>{t.text}</span>
                        <span>{" "}</span>
                    </span>
                    return curSpan;
                })}
            </div>
        </div>
    }

    public render(): JSX.Element {
        if (!this.props.example) { return null; }
        return <List.Item className="full-width">
            <List.Item.Meta
                description={
                <div>{this.props.example.map(
                    (sentence: TemplateExampleSentence, idx: number) => 
                        <div key={idx}>
                            {this.renderTemplate(sentence)}
                        </div>
                    )}
                </div>}/>
        </List.Item>
        
        
        
    }
}