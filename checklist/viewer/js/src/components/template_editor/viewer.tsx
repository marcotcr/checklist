//var widgets = require('@jupyter-widgets/base');
//var _ = require('lodash');
import * as widgets from '@jupyter-widgets/base';
import * as _ from 'lodash';

import * as React from 'react';
import * as ReactDOM from 'react-dom';

import { TemplateEditor } from './TemplateEditor';
import '../../style.css';
import { templateStore } from '../../stores/templates/TemplateStore';
 

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
        templateStore.bertSuggests = this.model.get("suggest_dict");
        //if (redraw) { this.renderApp(); }
    },
    onCandidateChanged: function(redraw: boolean=false): void {
        //templateStore.setSources(this.model.get("sources"));
        //templateStore.setOriToken(this.model.get("masked_tokens"));
        
        //if (redraw) { this.renderApp(); }
    },
    onSentenceChanged: function(redraw: boolean=false): void {
        //templateStore.setSources(this.model.get("sources"));
        //templateStore.setOriToken(this.model.get("masked_tokens"));
        
        //if (redraw) { this.renderApp(); }
    },

    // frontend value.
    onReset: function(): void {
        //templateStore.reset();
        this.renderApp();
    },

    onGetSuggestion: function(): void {
        // save the masked token list to the backend
        const maskedTokens = templateStore.templates.map(t => t.serialize())
        this.send({event: 'get_suggest', masked_tokens: maskedTokens});
        this.renderApp();
    },

    onConfirmFillIn: function(): void {
        console.log(templateStore.tagDict);
        const maskedTokens = templateStore.templates.map(t => t.serialize())
        this.send({event: 'confirm_fillin', fillin_dict: templateStore.tagDict, masked_tokens: maskedTokens});
        //this.renderApp();
    },

    onAddNewWordList: function(name: string, wordList: string[]): void {
        this.send({event: 'add_new_wordlist', name: name, word_list: wordList});
        //this.renderApp();
    },

    renderApp: function() {
        if (document.getElementById("app-wrapper")) {
            document.getElementById("app-wrapper").remove();
        }
        const $app = document.createElement("div");
        $app.setAttribute("id", "app-wrapper");
        /*
        const wrapper = <TemplateEditor 
            onReset={this.onReset}
            onExtendWordList={this.onAddNewWordList}
            onGetSuggestion={this.onGetSuggestion}
            onConfirmFillIn={this.onConfirmFillIn}/>
        */
       const wrapper = null;
        ReactDOM.render(wrapper, $app);
        this.el.appendChild($app);
    },

    render: function() {
        // bind functions
        //this.savedChanged = this.savedChanged.bind(this);
        //this.onChangeMask = this.onChangeMask.bind(this);
        this.onReset = this.onReset.bind(this);
        this.onAddNewWordList = this.onAddNewWordList.bind(this);
        this.onSentenceChanged = this.onSentenceChanged.bind(this);
        this.onSuggestChanged = this.onSuggestChanged.bind(this);
        this.onCandidateChanged = this.onCandidateChanged.bind(this);
        this.onConfirmFillIn = this.onConfirmFillIn.bind(this);
        this.onGetSuggestion = this.onGetSuggestion.bind(this);
        this.renderApp = this.renderApp.bind(this);
        // init the value
        this.onSentenceChanged(false);
        this.onSuggestChanged(false);
        this.onCandidateChanged(false);
        this.renderApp();

        // Python -> JavaScript update
        this.listenTo(this.model, 'change:suggest_dict', this.onSuggestChanged, this);
        this.listenTo(this.model, 'change:masked_tokens', this.onMaskTokenChanged, this);
        this.listenTo(this.model, 'change:sources', this.onCandidateChanged, this);

    }
});