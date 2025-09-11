// noinspection JSUnusedGlobalSymbols,JSUnresolvedReference
// noinspection JSUnresolvedReference
class CustomCodeEditorStimulus extends window.StimulusModule.Controller {
    static targets = ['container']

    connect() {
        this.editorClass = new CustomCodeEditor(this.containerTarget);
    }

    disconnect() {
        this.editorClass.disconnect()
        this.editorClass = null;
    }

}

window.wagtail.app.register('custom-code-editor', CustomCodeEditorStimulus)