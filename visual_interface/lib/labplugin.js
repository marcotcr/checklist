var plugin = require('./index');
var base = require('@jupyter-widgets/base');

export default {
  id: 'viewer',
  requires: [base.IJupyterWidgetRegistr],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'viewer',
          version: plugin.version,
          exports: plugin
      });
  },
  autoStart: true
};