import * as React from 'react';
import { observer } from 'mobx-react';

import { Row } from 'antd';
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
    }

    public render(): JSX.Element {
        let bertIdx: number = 0;
        console.log(templateStore.bertSuggests)
        return <Row style={{display: "flex", flexWrap: "wrap"}}>
            {this.template.tokens.map((t: TemplateToken, idx: number) => {
                const options = t.isGeneralMask() ? 
                    templateStore.bertSuggests.map(b => b[bertIdx]) : [];
                bertIdx += t.isGeneralMask() ? 1 : 0;
                return <TokenSpan 
                    key={`${t.key()}-${idx}-${t.displayTag()}`}
                    options={options}
                    token={t}
                    onExtendWordList={this.props.onExtendWordList} />
            } )}
        </Row>
        
    }
}