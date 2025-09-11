// noinspection JSUnresolvedReference

(function(){
    function CustomCodeEditorWidget(html, id, ace) {
        this.html = html;
        this.id = id;
        this.ace = ace;
        this.codeEditor = null;
    }

    CustomCodeEditorWidget.prototype.render = function(placeholder, name, id, initialState){
        // eslint-disable-next-line no-param-reassign
        placeholder.innerHTML = this.html.replace(/__NAME__/g, name).replace(/__ID__/g, id);

        let initial = JSON.parse(initialState);

        // Set default value on textarea as hacky way
        if(initial.code && initial.code.length > 0){
            placeholder.querySelector('textarea#'+ id + '[name="' + name + '"]').innerText = initialState
        }

        // eslint-disable-next-line no-undef
        this.codeEditor = new CustomCodeEditor(placeholder.querySelector('div.editor-' + id));

        if(initial.code && initial.code.length > 0){
            this.codeEditor.setState(initial);
            this.codeEditor.editor.clearSelection();
        }

        return this.codeEditor;
    };

    window.telepath.register('wagtail_custom_code_editor.widgets.CustomCodeEditor', CustomCodeEditorWidget);
})()