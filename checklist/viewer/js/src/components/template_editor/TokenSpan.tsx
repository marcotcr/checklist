import * as React from 'react';
import { Badge, Row, Checkbox } from 'antd';
import { TemplateToken } from '../../stores/templates/TemplateToken';
import { observer } from 'mobx-react';
import { observable } from 'mobx';
import { templateStore } from '../../stores/templates/TemplateStore';
import { utils } from '../../stores/Utils';
import  $ from 'jquery';

interface TokenProps {
    token: TemplateToken;
    options: string[];
    onExtendWordList: (name: string, wordList: string[]) => void;
}

@observer
export class TokenSpan extends React.Component<TokenProps, {}> {
    private token: TemplateToken;
    public options: string[];

    @observable public modalVisible: boolean;

    public content: string;
    constructor (props: TokenProps, context: any) {
        super(props, context);
        this.token = this.props.token;
        this.options = this.props.options;
        this.modalVisible = false;
        this.onSelectSuggests = this.onSelectSuggests.bind(this);
        this.onCheckAllChange = this.onCheckAllChange.bind(this);
    }

    public componentDidMount() {
        $('.checklist').scroll(function(){
            $('.checklist').scrollTop($(this).scrollTop());    
        })

        if ((window as any).Jupyter) {
            (window as any).Jupyter.keyboard_manager.disable();
        }
    }
    public componentDidUpdate() {
        $('.checklist').scroll(function(){
            $('.checklist').scrollTop($(this).scrollTop());    
        })
        if ((window as any).Jupyter) {
            (window as any).Jupyter.keyboard_manager.disable();
        }
    }


    public setContent(content: string): void {
        this.content = content;
    }
    
    public onSelectSuggests (checkIdxes: number[]): void {
        console.log(checkIdxes);
        templateStore.onChangeSelectedSuggest(checkIdxes);
    };

    public onCheckAllChange (e): void {
        const checkedList = e.target.checked ? this.options.map((o, i) => i) : [];
        this.onSelectSuggests (checkedList.slice());
    };


    public colorToken(): JSX.Element {
        let colorClass = "";
        if (this.token.isGeneralMask()) {
            colorClass = "token-mask";
        } else if (this.token.isAbstract()) {
            colorClass = "token-abstract";
        }
        const token = <span className={`token ${colorClass}`}>
            {this.token.needArticle && !this.token.isEmptyMask() ?
                <span className="token-article">{`${utils.genArticle(this.token.default)} `}</span> : null}
            {this.token.displayStr()}
        </span>;

        if (this.token.isAbstract() && !this.token.isEmptyMask()) {
            return <Badge 
                //style={{backgroundColor: color, top: -15, opacity: 0.8}}
                count={this.token.displayTag()} className={`${colorClass} badge`}>
                {token}</Badge>
        } else {
            return token;
        }
    }

    public SuggestChecklist(): JSX.Element {
        if (this.options.length === 0) {
            return null;
        }
        return <div 
            key={this.props.token.displayTag() + this.props.token.key()}
            className="full-width">
            <div><b className='info-header'>Fill in with...</b></div>
            <div style={{ borderBottom: '1px solid #E9E9E9' }}>
            <Checkbox
                indeterminate={
                    this.options.length && 
                    templateStore.selectedSuggestIdxes.length < this.options.length}
                onChange={this.onCheckAllChange}
                checked={this.options.length && 
                templateStore.selectedSuggestIdxes.length === this.options.length}>
                <i>Check All</i>
            </Checkbox>
            </div>
            <div style={{height: 100}} className="checklist full-width overflow-y">
            <Checkbox.Group value={this.options} onChange={this.onSelectSuggests}>
            <Row>
                {this.options.map((s, idx: number) => 
                    <Row key={s}><Checkbox value={idx}>
                        <span className="ellipsis">
                            {this.token.needArticle ?
                                <span className="token-article">{`${utils.genArticle(s)} `}</span> : null}
                            {s}
                        </span>
                    </Checkbox></Row>)}
            </Row>
            </Checkbox.Group>
            </div>
      </div>
    }

    public render(): JSX.Element {
        /*
        return <Popover title={null}
            content={this.editMaskBtns()}>
            { this.colorToken() }
        </Popover>
        */
        return <div className="token-box" 
            key={`${this.token.key()}`}>
            {this.colorToken()}
            <Row>{this.SuggestChecklist()}</Row>
        </div>
    }
}
