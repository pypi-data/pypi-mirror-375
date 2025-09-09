define([
    'base/js/namespace',
    'base/js/events'
], function(Jupyter, events) {
    var ran = false;

    events.on('kernel_ready.Kernel', function() {
        if (ran) return;
        ran = true;

        // Turn line numbers on by default
        var cell = Jupyter.notebook.get_selected_cell();
        var config = cell.config;
        var patch = {
            CodeCell: {
                cm_config:{lineNumbers:true}
            }
        };
        config.update(patch);

        // Add 'Run all' button to toolbar
        Jupyter.toolbar.add_buttons_group([
            {
                'label' : 'run',
                'icon': 'fa-play',
                'callback' : function() { Jupyter.notebook.execute_all_cells() }
            }
        ]);

        // Add global keyboard shortcut to run all (Cmd/Ctrl+R)
        Jupyter.keyboard_manager.actions._actions['jupyter-notebook:run-all-cells'] = {
            handler: function(env) { env.notebook.execute_all_cells() }
        };
        Jupyter.keyboard_manager.command_shortcuts.add_shortcut(
            'cmdtrl-r', 'jupyter-notebook:run-all-cells'
        );
        Jupyter.keyboard_manager.edit_shortcuts.add_shortcut(
            'cmdtrl-r', 'jupyter-notebook:run-all-cells'
        );
    });
});
