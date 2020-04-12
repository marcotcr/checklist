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
    onChangeSelected: (idxes: number[]) => void;
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
        if ((window as any).Jupyter) {
            (window as any).Jupyter.keyboard_manager.disable();
        }
        $('.checklist').scroll(function(){
            $('.checklist').scrollTop($(this).scrollTop());    
        })
    }
    public componentDidUpdate() {
        if ((window as any).Jupyter) {
            (window as any).Jupyter.keyboard_manager.disable();
        }
        $('.checklist').scroll(function(){
            $('.checklist').scrollTop($(this).scrollTop());    
        })
    }


    public setContent(content: string): void {
        this.content = content;
    }
    
    public onSelectSuggests (checkIdxes: number[]): void {
        templateStore.onChangeSelectedSuggest(checkIdxes);
        if (this.props.onChangeSelected) {
            this.props.onChangeSelected(templateStore.selectedSuggestIdxes);
        }
    };

    public onCheckAllChange (e): void {
        const checkedList = e.target.checked ? this.options.map((o, i) => i) : [];
        this.onSelectSuggests (checkedList.slice());
    };


    public colorToken(): JSX.Element {
        const colorClass = this.token.isGeneralMask() ? 
            "mask-token" : 
            this.token.isAbstract() ? "abstract-token": "";
        const token = <span 
            className={`template-token ${this.token.isEmptyMask() ? colorClass : ""}`}>
            {this.token.needArticle && !this.token.isEmptyMask() ?
                <span className="article-token">
                {`${utils.genArticle(this.token.default)} `}</span> : null}
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
        $('.checklist').scroll(function(){
            $('.checklist').scrollTop($(this).scrollTop());    
        })
        return <div 
            key={this.props.token.displayTag() + this.props.token.key()}
            className="full-width">
            <div><b className='info-header'>Fill in with...</b></div>
            <div style={{ borderBottom: '1px solid #E9E9E9' }}>
            <Checkbox
                indeterminate={
                    templateStore.selectedSuggestIdxes.length && 
                    templateStore.selectedSuggestIdxes.length < this.options.length}
                onChange={this.onCheckAllChange}
                checked={this.options.length && 
                templateStore.selectedSuggestIdxes.length === this.options.length}>
                <i>Check All</i>
            </Checkbox>
            </div>
            <div 
                onScroll={() => {
                    $('.checklist').scroll(function(){
                        $('.checklist').scrollTop($(this).scrollTop());    
                    })
                }}
                style={{height: 100}} className="checklist full-width overflow-y">
            <Checkbox.Group 
                value={templateStore.selectedSuggestIdxes} 
                onChange={this.onSelectSuggests}>
            <Row>
                {this.options.map((s, idx: number) => 
                    <Row key={`${s}${idx}`}><Checkbox value={idx}>
                        <span className="ellipsis">
                            {this.token.needArticle ?
                                <span className="article-token">{`${utils.genArticle(s)} `}</span> : null}
                            {s}
                        </span>
                    </Checkbox></Row>)}
            </Row>
            </Checkbox.Group>
            </div>
      </div>
    }


    public TagCandidate(): JSX.Element {
        if (this.options.length === 0) {
            return null;
        }
        return <div 
            key={this.props.token.displayTag() + this.props.token.key()}
            className="full-width">
            <div><b className='info-header tag-candidate-token'>More Samples</b></div>
            <div style={{height: 121}} className="full-width overflow-y">
            <Row>
                {this.options.map((s, idx: number) => 
                    <Row key={`${s}${idx}`}>
                        <span className="ellipsis tag-candidate-token">
                            {this.token.needArticle ?
                                <span className="article-token">{`${utils.genArticle(s)} `}</span> : null}
                            {s}
                        </span></Row>)}
            </Row>
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
        $('.checklist').scroll(function(){
            $('.checklist').scrollTop($(this).scrollTop());    
        })
        return <div className="template-token-box" key={`${this.token.key()}`}>
            {this.colorToken()}
            <Row>{ this.token.isGeneralMask() ? this.SuggestChecklist() : this.TagCandidate()}</Row>
        </div>
    }
}
