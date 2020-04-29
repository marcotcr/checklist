// Entry point for the unpkg bundle containing custom model definitions.
//
// It differs from the notebook bundle in that it does not need to define a
// dynamic baseURL for the static assets and may load some css that would
// already be loaded by the notebook otherwise.

// Export widget models and views, and the npm package version number.
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