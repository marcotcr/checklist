// This file contains the javascript that is run when the notebook is loaded.
// It contains some requirejs configuration and the `load_ipython_extension`
// which is required for any notebook extension.
//
// Some static assets may be required by the custom widget javascript. The base
// url for the notebook is not known at build time and is therefore computed
// dynamically.
__webpack_public_path__ = document.querySelector('body').getAttribute('data-base-url') + 'nbextensions/viewer';


// Configure requirejs
if (window.require) {
    window.require.config({
        map: {
            "*" : {
                "viewer": "nbextensions/viewer/index",
            },
        },
        paths: {
            "Jupyter": "base/js/namespace"
        }
    });
}

// Export the required load_ipython_extension
const load_ipython_extension = function() {
    //IPython.keyboard_manager.edit_shortcuts.add_shortcuts(add_edit_shortcuts);
    console.log(__webpack_public_path__);
    Jupyter.keyboard_manager.command_shortcuts.add_shortcut('s', {
        help : 'run cell',
        help_index : 'zz',
        handler : function (event) {
            console.log(event)
            return false;
        }}
    );    
}
export default load_ipython_extension;