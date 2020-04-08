import * as React from 'react';
import { observer } from 'mobx-react';

import { Row } from 'antd';
import { Action } from "../../stores/Interface";
import { Template } from "../../stores/templates/Template";
import { TemplateToken } from '../../stores/templates/TemplateToken';

import { TokenSpan } from './TokenSpan';
import { templateStore } from '../../stores/templates/TemplateStore';

interface PerTemplateEditorProps {
    template: Template;
    onReset: () => void;
    onConfirmFillIn: () => void;
    onExtendWordList: (name: string, wordList: string[]) => void;
}

@observer
export class PerTemplateEditor extends React.Component<PerTemplateEditorProps, {}> {
    public template: Template;
    public isLink: boolean;

    constructor(state: PerTemplateEditorProps, context: any) {
        super(state, context);
        this.template = this.props.template;
        this.editTemplate = this.editTemplate.bind(this);
    }

    public editTemplate(idx: number, content: string, tag: string, action: Action): void {
        this.props.template.editTemplate(idx, content, tag, action, templateStore.templates);
    }

    public render(): JSX.Element {
        return <Row style={{display: "flex", flexWrap: "wrap"}}>
            {this.template.tokens.map((t: TemplateToken, idx: number) => <TokenSpan 
                key={`${t.key()}-${idx}-${t.displayTag()}`}
                idx={idx}
                token={t}
                onConfirmFillIn={this.props.onConfirmFillIn}
                onExtendWordList={this.props.onExtendWordList}
                onReset={this.props.onReset}
                EditTemplate={this.editTemplate} /> )}
        </Row>
        
    }
}