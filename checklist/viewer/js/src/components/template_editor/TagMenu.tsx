import * as React from 'react';
import { templateStore } from '../../stores/templates/TemplateStore';
import { MASK } from '../../stores/Interface';
import { Menu, Icon } from 'antd';
import { TemplateToken } from '../../stores/templates/TemplateToken';

export interface TagMenuProps {
    token: TemplateToken;
    editTemplate: () => void;
    action: "plus"|"tag",
    setTag: (rawTag: string) => void;
}


export class TagMenu extends React.Component<TagMenuProps, {}> {
    constructor (props: TagMenuProps, context: any) {
        super(props, context);
        this.onChangeTag = this.onChangeTag.bind(this);
    }


    public renderSelectIcon(source: string, version: number=null): JSX.Element {
        const isSelected = this.props.token.isSelectedTag(source) && 
            (version === null || this.props.token.version === version);
        return isSelected && this.props.action === "tag" ? 
            <Icon type="check-circle" theme="twoTone" twoToneColor="#52c41a" /> : null;
    }

    public onChangeTag(value): void {
        const [source, version_] = value.key.split(":");
        const version = Number(version_);
        const versionedTag = source ? templateStore.addNewVerion(source, version) : "";
        this.props.setTag(versionedTag);
        if (this.props.action === "tag") {
            this.props.editTemplate();
        }
    }

    public renderSubMenu(source: string): JSX.Element {
        const display = source === "" ? "[Do not tag]" : source === MASK ? "Fill with BERT" : source;
        const selectedIcon = this.renderSelectIcon(source);
        //if (source === MASK || source === "") {
        if (source === "") {
            return <Menu.Item key={`${source}:${999}`} onClick={this.onChangeTag}>{display} {selectedIcon}</Menu.Item>
        }
        const existVersion = templateStore.abstractTracker[source] || 0;
        const submenues = [...Array(existVersion+1).keys()].map((v: number) => {
            const key = `${source}:${v+1}`;
            if (v === existVersion) {
                return <Menu.Item key={key} onClick={this.onChangeTag} >Create new version</Menu.Item>;
            } else {
                const selectedIconVersion = this.renderSelectIcon(source, v);
                return <Menu.Item onClick={this.onChangeTag} key={key}>
                    { `${source}${v+1}`} {selectedIconVersion}</Menu.Item>;
            } 
        });
        return <Menu.SubMenu key={source} title={<span>{display} {selectedIcon}</span>}>
            {submenues}
        </Menu.SubMenu>
    }

    public render(): JSX.Element {
        const candidates = ["", "mask"].concat(templateStore.sources);
        return <Menu 
            key={this.props.token.key()}
            style={{maxHeight: 300, overflow: "auto"}}>
            {candidates.map(c => this.renderSubMenu(c))}
        </Menu>
    }
}