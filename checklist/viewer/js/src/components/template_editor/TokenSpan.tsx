import * as React from 'react';
import { Action, MASK } from "../../stores/Interface";
import { Badge, Icon, Popover, Modal, Row, Checkbox, Input, Dropdown, Menu, Select, Button, Tag, Divider } from 'antd';
import { TemplateToken } from '../../stores/templates/TemplateToken';
import { observer } from 'mobx-react';
import { observable } from 'mobx';
import { threadId } from 'worker_threads';
import { templateStore } from '../../stores/templates/TemplateStore';
import { TagMenu } from './TagMenu';

interface TokenProps {
    token: TemplateToken;
    idx: number;
    onConfirmFillIn: () => void;
    onReset: () => void;
    onExtendWordList: (name: string, wordList: string[]) => void;
    EditTemplate: (idx: number, content: string, tag: string, action: Action) => void;
}

@observer
export class TokenSpan extends React.Component<TokenProps, {}> {
    private token: TemplateToken;
    public suggestOptions: string[];
    public newWordListName: string;

    @observable public status: "default"|"editing"|"adding";
    @observable public modalVisible: boolean;

    @observable public rawTag: string;
    public action: Action;
    public content: string;
    constructor (props: TokenProps, context: any) {
        super(props, context);
        this.token = this.props.token;
        this.suggestOptions = [];
        this.status = "default";
        this.newWordListName = "";
        this.modalVisible = false;


        this.rawTag = null;
        this.content = null;
        this.action = null;

        this.onSelectSuggests = this.onSelectSuggests.bind(this);
        this.onCheckAllChange = this.onCheckAllChange.bind(this);
        this.setContent = this.setContent.bind(this);
        this.setTag = this.setTag.bind(this);
        this.editTemplate = this.editTemplate.bind(this);
        this.resetStatus = this.resetStatus.bind(this);
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

    public resetStatus(): void {
        this.status = "default";
        if (this.action === "plus") {
            this.action = null;
        }
    }

    public setContent(content: string): void {
        this.content = content;
    }

    public setTag(tag: string): void {
        this.rawTag = tag;
    }
    
    public onSelectSuggests (checkedList: string[]): void {
        templateStore.onChangeFillInDict(this.token, checkedList);
        this.props.onConfirmFillIn();
    };

    public onCheckAllChange (e): void {
        const checkedList = e.target.checked ? this.suggestOptions : [];
        this.onSelectSuggests (checkedList.slice());
    };

    public editTemplate(): void {
        this.props.EditTemplate(this.props.idx, this.content, this.rawTag, this.action);
    }

    public editMaskBtn(action: Action): JSX.Element {
        let text = "";
        switch(action) {
            case "edit": 
                text = `Change to ${MASK}`; break;
            case "tag": 
                text = `Change tag`; break;
            case "delete": 
                text = `Remove`; break;
            case "lock": 
                text = `Lock to default`; break;
            case "unlock": 
                text = `Unlock for suggestions`; break;
            case "plus": 
            default:
                text = `Add ${MASK}`; break;
        }
        /*
        return <Button 
            type="primary" 
            href={null} 
            onClick={() => {this.props.onEditMask(this.props.idx, action)}}
            key={action}>
            <Icon type={icon} />{text}</Button>
        */
       const iconRender= <Icon type={action} title={text}
            onClick={() => {
                this.action = action;
                if (action === "lock" || action === "unlock") {
                    this.token.toggleLock(templateStore.templates);
                } else if (action === "edit") {
                    this.setTag(this.token.displayTag());
                    this.setContent(this.token.default); 
                    this.status = "editing";
                }  else if (action === "tag") {
                    this.setContent(this.token.default); 
                    console.log(this.content)
                } else if (action === "plus") {
                    this.setContent("");
                    this.setTag("");
                    this.status = "adding";
                } else if (action === "delete") {
                   this.editTemplate();
                }
            }} />;
        if (action === "tag") {
            return <Dropdown 
                onVisibleChange={ () => {this.setContent(this.token.default)} }
                overlay={<TagMenu 
                    action="tag" 
                    setTag={this.setTag}token={this.token} editTemplate={this.editTemplate}/>} 
                trigger={["hover"]}>{iconRender}</Dropdown>;
        } else {
            return iconRender;
        }
    }

    public renderAddInput(): JSX.Element {
        const display = this.rawTag === "" ? "Null" : this.rawTag === MASK ? "BERT mask" : this.rawTag;
        return <Input.Group compact style={{textAlign: "center"}} >
            <Input 
                onChange={(event) => { this.setContent(event.target.value as any);}}
                placeholder="Default string" style={{width: "30%"}}/>
            <Dropdown trigger={["click"]}
                overlay={<TagMenu 
                    action="plus"
                    setTag={this.setTag}token={this.token} editTemplate={this.editTemplate}/>}>
                <Button key={display}>Tag (current: <Tag color={this.rawTag === "" ? "#d9d9d9" : this.rawTag.includes(MASK) ? "#1890ff" : "#52c41a"}>{display}</Tag>)
                <Icon type="down" /></Button></Dropdown>
            <Button 
                type="primary" href={null} onClick={() => {this.editTemplate(); this.resetStatus()}}><Icon type="check"/></Button>
            <Button type="danger" href={null} onClick={() => {this.resetStatus();}}><Icon type="close"/></Button>
      </Input.Group>
    }

    public renderEditInput(): JSX.Element {
        return <Input.Search
            placeholder="The default value."
            defaultValue={this.token.default ? this.token.default : null}
            enterButton="Confirm"
            size="small"
            onSearch={(value) => { 
                this.setContent(value as string);
                this.resetStatus();
                this.editTemplate();
            }}
        />
    }

    public editMaskBtns(): JSX.Element {
        if (this.status === "editing") {
            return this.renderEditInput();
        } else if (this.status === "adding") {
            return this.renderAddInput();
        }
        let allowedActions: Action[] = ["edit", "tag", "plus", "delete"];
        if (this.token.isAbstract()) {
            const lockAction = this.token.isLock ? "unlock" : "lock";
            allowedActions.push(lockAction);
        }
        /*
        return <Button.Group size="small">
            {allowedActions.map(action => this.editMaskBtn(action))}
        </Button.Group>;
        */
        return <span>{allowedActions.map(action => 
            <span key={action}>{` `}{this.editMaskBtn(action)}{` `}</span>)}</span>
    }

    public colorToken(): JSX.Element {
        let colorClass = "";
        if (this.token.isLock) {
            colorClass = "token-lock";
        } else if (this.token.isGeneralMask()) {
            colorClass = "token-mask";
        } else if (this.token.isAbstract()) {
            colorClass = "token-abstract";
        }
        const token = <Dropdown 
            onVisibleChange={ () => {this.setContent(this.token.default)} }
            overlay={<TagMenu 
                action="tag" 
                setTag={this.setTag}token={this.token} editTemplate={this.editTemplate}/>} 
            trigger={["hover"]}><span 
                
                className="token">{`${this.token.default} `}</span></Dropdown>;
        if (this.token.isAbstract()) {
            return <Badge 
                //style={{backgroundColor: color, top: -15, opacity: 0.8}}
                count={this.token.displayTag()} className={`${colorClass} badge`}>
                <span style={{backgroundColor: "#eee"}}>{token}</span></Badge>
        } else {
            return token;
        }
    }

    public SuggestChecklist(): JSX.Element {
        if (this.suggestOptions.length === 0) {
            return null;
        }
        const checkedList = templateStore.fillInDict[this.props.token.displayTag()] || [];
        return <div 
            key={this.props.token.displayTag() + this.props.token.key()}
            className="full-width">
            <div><b className='info-header'>Fill in with...</b></div>
            <div style={{ borderBottom: '1px solid #E9E9E9' }}>
            <Checkbox
                indeterminate={checkedList.length && checkedList.length < this.suggestOptions.length}
                onChange={this.onCheckAllChange}
                checked={this.suggestOptions.length && checkedList.length === this.suggestOptions.length}>
                <i>Check All</i>
            </Checkbox>
            </div>
            <div style={{height: 100}} className="full-width overflow-y">
            <Checkbox.Group
                value={checkedList}
                onChange={this.onSelectSuggests}>
            <Row>
                {this.suggestOptions.map(s => 
                    <Row key={s}><Checkbox value={s}><span className="ellipsis">{s}</span></Checkbox></Row>)}
            </Row>
            </Checkbox.Group>
            </div>
      </div>
    }

    public renderInput(): JSX.Element {
        // this function should collect raw text from the user.
        // Afterwards, it sends the text to the backend
        // Alternatively: can directly set the raw text in store. 
        // so it can be read from backend as well.
        // NOT GOING TO DO THIS FOR NOW because templates can be directly input into changes.
        if ((window as any).Jupyter) {
            (window as any).Jupyter.keyboard_manager.disable();
        }
        return <Input.Group compact style={{textAlign: "center", width: 200}} >
            <Input 
                style={{width:120}}
                onChange={(event) => {
                    
                    this.newWordListName = event.target.value as any; }}
                placeholder="New candidate" />
            <Button type="primary" href={null} 
                onClick={() => {
                    const wordList = templateStore.fillInDict[this.token.displayTag()].slice();
                    //this.props.onReset();
                    this.props.onExtendWordList(this.newWordListName, wordList);
                    this.modalVisible = true;
                }}>
                <Icon type="check"/></Button>
      </Input.Group>
    }

    public confirmModal(): JSX.Element {
        return <Modal
          visible={this.modalVisible}
          onOk={() => {this.modalVisible = false; this.props.onReset()}}
          onCancel={null}
          cancelButtonProps={{style: {display: "none"}}}>
          <p>Successfully created the new word list! You can now query it.</p>
        </Modal>
    }

    public renderSaveMaskBtn(): JSX.Element {
        if (!this.props.onExtendWordList || 
            this.token.isLock || 
            !this.token.isGeneralMask()) {
            return null;
        }
        
        return <Popover 
            placement="top"
            trigger="click"
            destroyTooltipOnHide={true}
            onVisibleChange={() => {
                if ((window as any).Jupyter) {
                    (window as any).Jupyter.keyboard_manager.disable();
                }
            }}
            content={ this.renderInput()}>
            <Button 
                onClick={() => {
                    if ((window as any).Jupyter) {
                        (window as any).Jupyter.keyboard_manager.disable();
                    }
                }}
                disabled={this.suggestOptions.length === 0}
                style={{marginTop: 10, marginBottom: 10}}
                type="dashed" size="small" href={null} >
                <Icon type="plus" />New tag</Button>
            </Popover>
    }

    public render(): JSX.Element {
        /*
        return <Popover title={null}
            content={this.editMaskBtns()}>
            { this.colorToken() }
        </Popover>
        */
        const saveBtn = this.renderSaveMaskBtn();
        const suggestList = !this.token.isLock && this.token.displayTag() in templateStore.suggestDict ? 
            templateStore.suggestDict[this.token.displayTag()] : [];
        this.suggestOptions = suggestList;
        return <div className="token-box" 
            key={`${this.token.key()}`}>
            {/*
                <Row><Popover 
                    trigger="click"
                    content={this.editMaskBtns()} placement="top">{ this.colorToken() }</Popover></Row>
            */
            }
            {this.colorToken()}
            <Row key={suggestList.length}>
            {this.SuggestChecklist()}</Row>
            <Row style={{textAlign: "center"}}>{saveBtn}</Row>
            {this.confirmModal()}
        </div>
    }
}
