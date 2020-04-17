//var widgets = require('@jupyter-widgets/base');
//var _ = require('lodash');
import * as widgets from '@jupyter-widgets/base';
import * as _ from 'lodash';

import * as React from 'react';
import * as ReactDOM from 'react-dom';

import { TemplateEditor } from './TemplateEditor';
import '../../style.css';
import { templateStore } from '../../stores/templates/TemplateStore';
import  $ from 'jquery';


// Custom Model. Custom widgets models must at least provide default values
// for model attributes, including
//
//  - `_view_name`
//  - `_view_module`
//  - `_view_module_version`
//
//  - `_model_name`
//  - `_model_module`
//  - `_model_module_version`
//
//  when different from the base class.

// When serialiazing the entire widget state for embedding, only values that
// differ from the defaults will be specified.
export const Model = widgets.DOMWidgetModel.extend({
    defaults: _.extend(_.result(this, 'widgets.DOMWidgetModel.prototype.defaults'), {
    //defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
        _model_name : 'TemplateEditorModel',
        _view_name : 'TemplateEditorView',
        _model_module : 'viewer',
        _view_module : 'viewer',
        _model_module_version : '0.1.0',
        _view_module_version : '0.1.0',
    })
});

// Custom View. Renders the widget model.
export const View = widgets.DOMWidgetView.extend({
    /*
    initialize: function() {
        const backbone = this;
        const $app = document.createElement("div");
        ReactDOM.render(<App />, $app);
        backbone.$el.append($app);
    },
    */
    // to get data from the backend
    onSuggestChanged: function(redraw: boolean=false): void {
        templateStore.setBertSuggests(this.model.get("bert_suggests"));
        //if (redraw) { this.renderApp(); }
    },
    onTagDictChanged: function(redraw: boolean=false): void {
        templateStore.setTagDict(this.model.get("tag_dict"))
        //templateStore.setSources(this.model.get("sources"));
        //templateStore.setOriToken(this.model.get("masked_tokens"));
        
        //if (redraw) { this.renderApp(); }
    },
    onTemplatesChanged: function(redraw: boolean=false): void {
        templateStore.setTemplate(this.model.get("templates"))
        //templateStore.setSources(this.model.get("sources"));
        //templateStore.setOriToken(this.model.get("masked_tokens"));
        
        //if (redraw) { this.renderApp(); }
    },

    onChangeSelected: function(selected_idxes: string[]): void {
        this.send({event: 'select_suggests', idxes: selected_idxes});
        //this.renderApp();
    },

    renderApp: function() {
        if (document.getElementById("app-wrapper")) {
            document.getElementById("app-wrapper").remove();
        }
        const $app = document.createElement("div");
        $app.setAttribute("id", "app-wrapper");
        
        const wrapper = <TemplateEditor onChangeSelected={this.onChangeSelected} />
    
        ReactDOM.render(wrapper, $app);
        this.el.appendChild($app);
        $('.checklist').scroll(function(){
            $('.checklist').scrollTop($(this).scrollTop());    
        })
    },

    render: function() {
        this.onSuggestChanged = this.onSuggestChanged.bind(this);
        this.onTagDictChanged = this.onTagDictChanged.bind(this);
        this.onTemplatesChanged = this.onTemplatesChanged.bind(this);

        this.renderApp = this.renderApp.bind(this);
        this.onChangeSelected = this.onChangeSelected.bind(this);

        // init the value
        this.onTagDictChanged(false);
        this.onSuggestChanged(false);
        this.onTemplatesChanged(false);
        this.renderApp();

        // Python -> JavaScript update
        this.listenTo(this.model, 'change:tag_dict', this.onTagDictChanged, this);
        this.listenTo(this.model, 'change:bert_suggests', this.onSuggestChanged, this);
        this.listenTo(this.model, 'change:templates', this.onTemplatesChanged, this);

    }
});