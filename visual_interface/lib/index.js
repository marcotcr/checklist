
// Export widget models and views, and the npm package version number.
//module.exports = require('./viewer.js');
//module.exports['version'] = require('../package.json').version;

export var version =  require('../package.json').version;

import * as TemplateEditor from '../src/components/template_editor/viewer.tsx';
export var TemplateEditorModel = TemplateEditor.Model;
export var TemplateEditorView = TemplateEditor.View;

import * as TestSummarizer from '../src/components/test_summarizer/viewer.tsx';
export var TestSummarizerModel = TestSummarizer.Model;
export var TestSummarizerView = TestSummarizer.View;

import * as SuiteSummarizer from '../src/components/suite_summarizer/viewer.tsx';
export var SuiteSummarizerModel = SuiteSummarizer.Model;
export var SuiteSummarizerView = SuiteSummarizer.View;