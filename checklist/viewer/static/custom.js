require(['base/js/namespace', 'base/js/events'], function(Jupyter, events) {
    for (var i = 32; i < 127; i++) { 
        try {
            Jupyter.keyboard_manager.command_shortcuts.remove_shortcut(String.fromCharCode(i))
        } catch {}
    } 
});