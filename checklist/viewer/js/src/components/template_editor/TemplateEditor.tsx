import * as React from 'react';
import { observer } from 'mobx-react';
import { observable } from 'mobx';

import { Row, Avatar, Button, Icon, Divider, List, Col, Modal, Checkbox, Switch } from 'antd';
import { Template } from "../../stores/templates/Template";
import { PerTemplateEditor } from './PerTemplateEditor';
import { templateStore } from '../../stores/templates/TemplateStore';
import { utils } from '../../stores/Utils';
import { TemplateExampleToken } from '../../stores/Interface';
import { ExampleView } from './ExampleViewer';

interface TemplateEditorProps {
    onReset: () => void;
    onExtendWordList: (name: string, wordList: string[]) => void;
    onGetSuggestion: () => void;
    onConfirmFillIn: () => void;
    allowSetExpect?: boolean;
}


@observer
export class TemplateEditor extends React.Component<TemplateEditorProps, {}> {
    @observable public modalVisible: boolean;
    public expectValue: string;
    constructor(state: TemplateEditorProps, context: any) {
        super(state, context);
        this.modalVisible = false;
        this.expectValue = null;
    }

    public renderCtrlBtn(): JSX.Element {
        return <Button.Group size="small">
            <Button onClick={() => { this.props.onReset() }}
                type="primary" href={null} >
                <Icon type="undo"/>Reset</Button>
            <Button onClick={() => { 
                templateStore.tagDict = {};
                // reset the suggest dict
                this.props.onGetSuggestion() }}
                type="primary" href={null} >
                <Icon type="diff"/>Get suggestions</Button>
            {/*
            <Button 
                disabled={Object.values(templateStore.fillInDict).map(f => f.length).reduce((a, b) => a + b, 0) === 0}
                onClick={() => { this.props.onConfirmFillIn(); this.modalVisible = true; }}
                type="primary" href={null} >
                <Icon type="check"/>Confirm testing</Button>
            */}
        </Button.Group>
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

    public confirmModal(): JSX.Element {

        if ((window as any).Jupyter) {
            (window as any).Jupyter.keyboard_manager.disable();
        }

        return <Modal
          visible={this.modalVisible}
          onOk={() => {this.modalVisible = false;}}
          onCancel={null}
          cancelButtonProps={{style: {display: "none"}}}>
          <p>Success! See your <code>suite.raw_examples</code> and <code>suite.raw_tags</code> for 
          the generated ones.</p>
        </Modal>
    }


    public render(): JSX.Element {
        return <Row key={templateStore.templates.map(t => t.key()).join("-")} gutter={30}>
            <Col span={17}>
                <Row>
                    {this.renderCtrlBtn()}
                </Row>
                <Divider className="compact-divider"/>
                <List
                    itemLayout="horizontal"
                    dataSource={templateStore.templates}
                    renderItem={(template: Template, idx: number) => (
                        <List.Item key={template.key()}>
                            <List.Item.Meta
                            avatar={<Avatar style={{backgroundColor: "#f56a00", verticalAlign: "middle"}} size="small">
                                ></Avatar>}
                            title={<PerTemplateEditor
                                onConfirmFillIn={this.props.onConfirmFillIn}
                                onReset={this.props.onReset}
                                onExtendWordList={this.props.onExtendWordList}
                                template={template} /> }
                            />
                        </List.Item>
                    )}
                />
            </Col>
            <Col span={7}>
                <h4 className="header">Preview</h4>
                <div 
                key={templateStore.templates.map(t => t.key()).join("-")}
                style={{maxHeight: 400, overflow: "auto"}}>
                <List
                    itemLayout="horizontal"
                    size="small"
                    dataSource={templateStore.previewExample}
                    renderItem={(preview: {[key: string]: TemplateExampleToken[]}, idx: number) => (
                        <ExampleView key={idx} example={preview} />
                    )}
                />
                </div>
            </Col>
            {/*this.confirmModal()*/}
        </Row>
        
    }
}