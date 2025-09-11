// noinspection JSUnusedGlobalSymbols,JSUnresolvedReference,DuplicatedCode
/* global, ClipboardJS, AceEditor */
// Credited to https://stackoverflow.com/a/56612753
class ClassEventsES6 {
    constructor() {
        this.listeners = new Map();
        this.onceListeners = new Map();
        this.triggerdLabels = new Map();
    }

    // help-function for onReady and onceReady
    // the callbackfunction will execute,
    // if the label has already been triggerd with the last called parameters
    _fCheckPast(label, callback) {
        if (this.triggerdLabels.has(label)) {
            callback(this.triggerdLabels.get(label));
            return true;
        } else {
            return false;
        }
    }

    // execute the callback everytime the label is trigger
    on(label, callback, checkPast = false) {
        this.listeners.has(label) || this.listeners.set(label, []);
        this.listeners.get(label).push(callback);
        if (checkPast)
            this._fCheckPast(label, callback);
    }

    // execute the callback everytime the label is trigger
    // check if the label had been already called
    // and if so excute the callback immediately
    onReady(label, callback) {
        this.on(label, callback, true);
    }

    // execute the callback onetime the label is trigger
    once(label, callback, checkPast = false) {
        this.onceListeners.has(label) || this.onceListeners.set(label, []);
        if (!(checkPast && this._fCheckPast(label, callback))) {
            // label wurde nocht nicht aufgerufen und
            // der callback in _fCheckPast nicht ausgeführt
            this.onceListeners.get(label).push(callback);
    }
    }
    // execute the callback onetime the label is trigger
    // or execute the callback if the label had been called already
    onceReady(label, callback) {
        this.once(label, callback, true);
    }

    // remove the callback for a label
    off(label, callback = true) {
        if (callback === true) {
            // remove listeners for all callbackfunctions
            this.listeners.delete(label);
            this.onceListeners.delete(label);
        } else {
            // remove listeners only with match callbackfunctions
            let _off = (inListener) => {
                let listeners = inListener.get(label);
                if (listeners) {
                    inListener.set(label, listeners.filter((value) => !(value === callback)));
                }
            };
            _off(this.listeners);
            _off(this.onceListeners);
        }
    }

    // trigger the event with the label
    trigger(label, ...args) {
        let res = false;
        this.triggerdLabels.set(label, ...args); // save all triggerd labels for onready and onceready
        let _trigger = (inListener, label, ...args) => {
            let listeners = inListener.get(label);
            if (listeners && listeners.length) {
                listeners.forEach((listener) => {
                    listener(...args);
                });
                res = true;
            }
        };
        _trigger(this.onceListeners, label, ...args);
        _trigger(this.listeners, label, ...args);
        this.onceListeners.delete(label); // callback for once executed, so delete it.
        return res;
    }
}

/**
 * Custom Code Editor Class
 * @class
 * @constructor
 * @public
 * @property {{ theme: string, defaultMode: string, modes: Array, options: Array, saveValue: Object }} ace
 * @property {ace} editor
 * @property {HTMLTextAreaElement} textarea
 * @property {HTMLElement} switchButtonContainer
 * @property {HTMLButtonElement} switchButton
 * @property {{ code: string, mode: string }} originalValue
 * @property {boolean} active
 * @property {number} notificationTimeout
 */
class CustomCodeEditor extends ClassEventsES6{
    originalValue;
    notificationTimeout = 1500;
    active = false;

    constructor(container){
        super();
        this.on('switchMode', this.switchModeState.bind(this));
        this.container = container;
        this.textarea = this.container.querySelector('textarea')
        this.switchButtonContainer = this.container.querySelector('.switch-container');
        this.switchButton = this.container.querySelector('.switch');

        this.themeValue = this.container.dataset.themeValue;
        this.modeValue = this.container.dataset.modeValue;
        this.modesValue = JSON.parse(this.container.dataset.modesValue) || [];
        this.editorValue = {
            "fontSize": this.container.dataset.fontSize.length > 0 ? this.container.dataset.fontSize : null,
            "height": this.container.dataset.heightValue.length > 0 ? this.container.dataset.heightValue : null,
            "width": this.container.dataset.widthValue.length > 0 ? this.container.dataset.widthValue : null
        }
        this.optionsValue = JSON.parse(this.container.dataset.optionsValue) || [];
        this.dropdownConfigValue = JSON.parse(this.container.dataset.dropdownConfigValue) || {};
        this.readOnlyConfigValue = JSON.parse(this.container.dataset.readOnlyConfigValue) || {};
        this.saveCommandConfigValue = JSON.parse(this.container.dataset.saveCommandConfigValue) || {};
        this.originalOptionsValue = JSON.parse(this.container.dataset.originalOptionsValue) || {};

        this.ace = {
            theme: this.themeValue,
            defaultMode: this.modeValue,
            modes: this.modesValue,
            options: this.optionsValue,
            saveCommandConfig: this.saveCommandConfigValue,
            saveOptions: {},
            saveValue: null
        }

        let that = this;

        this.originalValue = {
            saveCode: null,
            get code(){
                let value = JSON.parse(that.textarea.value)

                return value.code
            },

            get mode(){
                let value = JSON.parse(that.textarea.value)

                return value.mode
            },

            set code(val) {
                this.saveCode = val;
            },

            reset() {
                this.saveCode = null;
            }
        }

        /**
         * Copy Button Element
         * @type {HTMLButtonElement} copyTarget
         */
        this.copyTarget = this.container.querySelector('.copy-options');
        /**
         * Undo Button Element
         * @type {HTMLButtonElement} undoTarget
         */
        this.undoTarget = this.container.querySelector('.undo-options');

        if(this.copyTarget) {
            new ClipboardJS(this.container.querySelector('.copy-options'));
        } else if(this.copyTarget && !ClipboardJS.isSupported()) {
            this.container.querySelector('.button-container').style.display = 'none'
        }

        // Before initialize
        this.beforeInit();

        // Initialize
        this.init();

        // Initialize all events
        this.allEvents();

        // Set Editor Commands
        this.commands();

        // Set Theme
        this.setTheme(this.ace.theme)

        // Set After Init
        this.afterInit();
    }

    /**
     * To let user extend beforeInit method
     */
    beforeInit(){
        const beforeInitEvent = new CustomEvent('customCodeEditor:beforeInit', {
            detail: this
        });
        window.dispatchEvent(beforeInitEvent);
    }

    /**
     * To let user extend afterInit method
     */
    afterInit(){
        const afterInitEvent = new CustomEvent('customCodeEditor:afterInit', {
            detail: this
        });
        window.dispatchEvent(afterInitEvent);
    }

    /**
     * Initialize Custom Code Editor
     */
    init(){
        this.textarea.style.display = 'none';

        this.editor = ace.edit(this.container.querySelector('.editor'));

        if(this.container.querySelector('button.button-dropdown.result')){
            this.container.querySelector('.text-mode').innerText = this.getValue() ? this.getModeTitle(this.getValue().mode) : this.getModeTitle(this.originalValue.mode);
        }

        this.editorConfig();

        if(this.container.querySelectorAll('input.input-options').length > 0){
            this.checkOptions();
        }

        // Set original value
        if(this.originalValue.code){
            this.trigger('switchMode', false);
            this.setValue(this.originalValue.mode, this.originalValue.code)
            this.editor.clearSelection();
        }

        // Set default value if modes available and originalValue is not available
        if (this.ace.modes.length > 0 && !this.getValue() || (!this.getValue().code || this.getValue().code.length === 0)) {
            this.trigger('switchMode', true);
            this.editorMode(this.ace.defaultMode)
            this.editor.clearSelection();
        }

        // If `enable_modes=False`. Let editor start typing when changing modes is disabled.
        if (!this.container.querySelector('.dropdown#switch-modes')) {
            this.trigger('switchMode', false);
        }

        this.active = true;

        if(this.container.querySelector('.dropdown')) {
            this.dropdownConfig();
            this.readOnlyConfig();
        }

    }

    /**
     * Bind all events
     */
    allEvents(){
        let that = this;
        // Editor Session
        this.editor.session.on('change', this.onChange.bind(this));
        // Checkbox on change
        Array.from(this.container.querySelectorAll('input[type="checkbox"]')).forEach(input => input.addEventListener("change", that.checkboxOnChange.bind(that)))
        // Dropdown on change
        Array.from(this.container.querySelectorAll('select.dropdownOnChange')).forEach(input => input.addEventListener('change', that.dropdownOnChange.bind(that)))
        // Dropdown object on change
        Array.from(this.container.querySelectorAll('select.dropdownObjectOnChange')).forEach(input => input.addEventListener('change', that.dropdownOnChange.bind(that)))
        // Range slider on change
        Array.from(this.container.querySelectorAll('input.range-slider__range')).forEach(input => input.addEventListener('change', that.sliderOnChange.bind(that)))
        // Number on change
        Array.from(this.container.querySelectorAll('input.number[type="number"]')).forEach(input => input.addEventListener('change', that.numberOnChange.bind(that)))
        // Button options
        this.container.querySelector('.button-options').addEventListener('click', this.toggleOptions.bind(this));
        // Toggle Modes
        if(this.container.querySelector('button.button-dropdown.result')) {
            this.container.querySelector('button.button-dropdown.result').addEventListener('click', this.toggleModes.bind(this));
            // Search Mode
            this.container.querySelector('input[type="text"].search-bar.mode-search').addEventListener('input', this.searchMode.bind(this));
            // Set Mode
            this.setModeClick()
        }
        if(this.container.querySelector('div.switch-container')) {
            // Confirm Mode
            this.container.querySelector('button.switch').addEventListener('click', this.confirmMode.bind(this));
        }
        if(this.container.querySelector('div.options-config')) {
            // Search Options
            this.container.querySelector('input[type="text"].search-bar.my-options').addEventListener('input', this.searchOptions.bind(this));
            // Copy to clipboard
            this.container.querySelector('button.copy-options').addEventListener('click', this.copyToClipboard.bind(this));
            // Reset Options
            this.container.querySelector('button.undo-options').addEventListener('click', this.resetOptions.bind(this));
        }
    }

    disconnectAllEvents(){
        let that = this;
        // Editor Session
        this.editor.session.off('change', this.onChange.bind(this));
        // Checkbox on change
        Array.from(this.container.querySelectorAll('input[type="checkbox"]')).forEach(input => input.removeEventListener("change", that.checkboxOnChange.bind(that)))
        // Dropdown on change
        Array.from(this.container.querySelectorAll('select.dropdownOnChange')).forEach(input => input.removeEventListener('change', that.dropdownOnChange.bind(that)))
        // Dropdown object on change
        Array.from(this.container.querySelectorAll('select.dropdownObjectOnChange')).forEach(input => input.removeEventListener('change', that.dropdownOnChange.bind(that)))
        // Range slider on change
        Array.from(this.container.querySelectorAll('input.range-slider__range')).forEach(input => input.removeEventListener('change', that.sliderOnChange.bind(that)))
        // Number on change
        Array.from(this.container.querySelectorAll('input.number[type="number"]')).forEach(input => input.removeEventListener('change', that.numberOnChange.bind(that)))
        // Button options
        this.container.querySelector('.button-options').removeEventListener('click', this.toggleOptions.bind(this));
        // Toggle Modes
        if(this.container.querySelector('button.button-dropdown.result')) {
            this.container.querySelector('button.button-dropdown.result').removeEventListener('click', this.toggleModes.bind(this));
            // Search Mode
            this.container.querySelector('input[type="text"].search-bar.mode-search').removeEventListener('input', this.searchMode.bind(this));
            // remove Mode
            Array.from(this.container.querySelectorAll('li.modes-lists')).forEach((list) => {
                list.removeEventListener('click', that.listOnClick.bind(that));
            })
        }
        if(this.container.querySelector('div.switch-container')) {
            // Confirm Mode
            this.container.querySelector('button.switch').removeEventListener('click', this.confirmMode.bind(this));
        }
        if(this.container.querySelector('div.options-config')) {
            // Search Options
            this.container.querySelector('input[type="text"].search-bar.my-options').removeEventListener('input', this.searchOptions.bind(this));
            // Copy to clipboard
            this.container.querySelector('button.copy-options').removeEventListener('click', this.copyToClipboard.bind(this));
            // Reset Options
            this.container.querySelector('button.undo-options').removeEventListener('click', this.resetOptions.bind(this));
        }
    }

    switchModeState(switchState = false) {
        if (switchState) {
            this.active = false;
            this.editor.setReadOnly(true)
            if(this.switchButtonContainer){
                this.switchButtonContainer.style.display = "flex";
            }
        } else {
            this.active = true;
            this.editor.setReadOnly(false)
            if(this.switchButtonContainer) {
                this.switchButtonContainer.style.display = "none";
            }
        }
    }

    /**
     * Get Snippet Value
     * @param name
     * @returns {string}
     */
    getSnippet(name) {
        let valueMatch = this.ace.modes.filter((val) => val.name === name)[0];
        return valueMatch && !CustomCodeEditor.has(valueMatch, 'disableSnippet') && CustomCodeEditor.has(valueMatch, 'snippet') ? valueMatch.snippet : ""
    }

    /**
     * Set Bubble
     * @param {HTMLInputElement} range
     * @param {HTMLElement} bubble
     */
    setBubble(range, bubble) {
        const val = range.value;
        const min = range.min ? range.min : 0;
        const max = range.max ? range.max : 100;
        const newVal = Number(((val - min) * 100) / (max - min));

        // Sorta magic numbers based on size of the native UI thumb
        bubble.style.left = `calc(${newVal}% + (${(23 / 6) - newVal * 0.2}px - ${23 / 2}px))`;
    }

    /**
     * Checkbox On Change
     * @param {Event} event
     */
    checkboxOnChange(event){
        if(event.currentTarget.checked){
            this.editor.setOption(event.currentTarget.name, true)
        } else {
            this.editor.setOption(event.currentTarget.name, false)
        }
    }

    /**
     * Dropdown On Change
     * @param {Event} event
     */
    dropdownOnChange(event){
        this.editor.setOption(event.currentTarget.name, event.currentTarget.value);
    }

    /**
     * Dropdown Object On Change
     * @param {Event} event
     */
    dropdownObjectOnChange(event) {
        let value = typeof event.currentTarget.value === 'string' ? JSON.parse(event.currentTarget.value) : event.currentTarget.value;
        this.editor.setOption(event.currentTarget.name, value);
    }

    /**
     * Slider on change
     * @param {Event} event
     */
    sliderOnChange(event){
        let output = event.currentTarget.nextElementSibling;
        event.target.setAttribute('value', event.currentTarget.value)
        this.setBubble(event.currentTarget, output);
        output.innerText = event.currentTarget.value
        output.style.display = 'block'
        this.editor.setOption(event.currentTarget.name, event.currentTarget.value)
    }

    /**
     * Slider focus out
     * @param {Event} event
     */
    sliderOnFocusOut(event){
        let output = event.currentTarget.nextElementSibling;
        output.style.display = 'none'
    }

    /**
     * Number input on change
     * @param {Event} event
     */
    numberOnChange(event) {
        this.editor.setOption(event.target.name, event.target.value)
    }

    /**
     * Toggle options on click
     * @param {Event} event
     */
    toggleOptions(event) {
        event.preventDefault();
        event.stopPropagation();
        if (this.container.querySelector('.options-container').style.display === 'none') {
            this.container.querySelector('.options-container').style.removeProperty('display')
        } else {
            this.container.querySelector('.options-container').style.display = 'none'
        }
    }

    /**
     * To toggle modes on click
     * @param {Event} event
     */
    toggleModes(event) {
        event.preventDefault();
        event.stopPropagation();
        if (this.container.querySelector('.dropdown-content').style.display === 'none') {
            this.container.querySelector('.dropdown-content').style.removeProperty('display')
        } else {
            this.container.querySelector('.dropdown-content').style.display = 'none'
        }
    }

    /**
     * Trigger confirm mode on click
     * @param {Event} event
     */
    confirmMode(event) {
        event.preventDefault();
        event.stopPropagation();
        this.trigger('switchMode', false);
        let val = this.getValue();
        this.setValue(val.mode, val.code);
        // Reset save code if any
        this.originalValue.reset();
    }

    /**
     * Search Mode
     * @param {Event} event
     */
    searchMode(event){
        let search = event.currentTarget.value;

        Array.from(this.container.querySelectorAll('li.modes-lists')).forEach((mode) => {

            // Get name
            let name = mode.dataset.name.toUpperCase().indexOf(search.toUpperCase());

            // Channel to each conditions
            switch (true) {
                case mode.dataset.title && mode.dataset.title.toUpperCase().indexOf(search.toUpperCase()) > -1:
                    mode.style.removeProperty('display');
                    break;

                case !mode.dataset.title && name > -1:
                    mode.style.removeProperty('display');
                    break;

                default:
                    mode.style.display = 'none'
            }
        })
    }

    /**
     * Search options when input
     * @param {Event} event
     */
    searchOptions(event){
        let search = event.currentTarget.value;

        Array.from(this.container.querySelectorAll('.lists-inputs')).forEach((option) => {
            let name = CustomCodeEditor.camelCaseToWords(option.id);

            if (name.toUpperCase().indexOf(search.toUpperCase()) > -1) {
                option.style.removeProperty('display');
            } else {
                option.style.display = 'none'
            }
        })
    }

    editorMode(name){
        this.editor.session.setMode('ace/mode/' + name);
        let snippet = this.getSnippet(name);
        let selected = null

        /**
         * Disable Snippet Array
         * @type {Any[]}
         */
        let checkDisableSnippet = this.ace.modes.filter(val => val.disableSnippet === name);

        if(checkDisableSnippet.length === 0) {
            this.beautifyCode(snippet)
        }

        // Find the template for replace the code area
        const find = this.editor.find('@code-here', {
            backwards: false,
            wrap: true,
            caseSensitive: true,
            wholeWord: true,
            regExp: false
        });

        // If changing mode got existing codes , replace the value
        if (this.editor.getSelectedText().length > 0) {
            selected = this.editor.replace(this.editor.getSelectedText());
        }

        // If found
        if (find && selected && (this.originalValue.saveCode || this.originalValue.code)) {
            this.editor.replace(this.originalValue.saveCode || this.originalValue.code);
        } else {
            this.editor.replace('');
        }
    }

    /**
     * Set mode on click
     */
    setModeClick(){
        let that = this;
        Array.from(this.container.querySelectorAll('li.modes-lists')).forEach((list) => {
            list.addEventListener('click', that.listOnClick.bind(that))
        })
    }

    /**
     * List on click event
     * @param {Event} event
     */
    listOnClick(event){
        event.stopPropagation();
        this.trigger('switchMode', true)
        let name = event.currentTarget.dataset.name;
        this.container.querySelector('.text-mode').innerText = this.getModeTitle(name);
        this.editorMode(name);
    }

    /**
     * Set snippet value to editor
     * @param {string} code
     */
    beautifyCode(code){
        let beautify = ace.require('ace/ext/beautify');
        this.editor.setValue(code);
        beautify.beautify(this.editor.session);
    }

    /**
     * To check options on initialize
     */
    checkOptions(){
        /**
         * Collect all inputs
         * @type {HTMLInputElement[]}
         */
        let inputs = Array.from(this.container.querySelectorAll('input.input-options,select.input-options'))
        let that = this;
        inputs.forEach((input) => {
            let value = null;
            switch (true) {
                case (/select/g).test(input.type):
                    if (that.editor.getOptions().hasOwnProperty(input.name)) {
                        Array.from(input.children).forEach((option) => {
                            let defaultVal = input.dataset["defaultValue"]
                            // Option Value Cleaning
                            switch (option.value) {
                                case "true":
                                    option.value = true;
                                    break;

                                case "false":
                                    option.value = false;
                                    break;
                            }
                            // Default Value Cleaning
                            switch (defaultVal) {
                                case "true":
                                    defaultVal = true;
                                    break;

                                case "false":
                                    defaultVal = false;
                                    break
                            }
                            if (!input.hasAttribute('data-default-value') && option.value === that.editor.getOptions()[input.name].toString()) {
                                option.setAttribute('selected', true.toString())
                                that.ace.saveOptions[input.name] = option.value.toString()
                            } else if (input.hasAttribute('data-default-value')) {
                                input.value = defaultVal;
                                that.ace.saveOptions[input.name] = defaultVal.toString();
                                that.editor.setOption(input.name, defaultVal)
                            }
                        })
                    }
                    break;

                case (/range/g).test(input.type):
                    value = (that.editor.getOptions().hasOwnProperty(input.name)) ? that.editor.getOptions()[input.name] : 0
                    if (!input.hasAttribute('data-default-value')) {
                        input.setAttribute('value', value);
                        that.ace.saveOptions[input.name] = Number(that.editor.getOptions()[input.name]);
                    } else if (input.hasAttribute('data-default-value')) {
                        input.setAttribute('value', input.dataset["defaultValue"]);
                        that.ace.saveOptions[input.name] = Number(input.dataset["defaultValue"]);
                        that.editor.setOption(input.name, Number(input.dataset["defaultValue"]));
                    }
                    break;

                case (/number/g).test(input.type):
                    value = (that.editor.getOptions().hasOwnProperty(input.name)) ? that.editor.getOptions()[input.name] : 0;
                    if (!input.hasAttribute('data-default-value')) {
                        input.setAttribute('value', value);
                        that.ace.saveOptions[input.name] = parseFloat(that.editor.getOptions()[input.name]);
                    } else if (input.hasAttribute('data-default-value')) {
                        input.setAttribute('value', input.dataset["defaultValue"]);
                        that.ace.saveOptions[input.name] = parseFloat(input.dataset["defaultValue"]);
                        that.editor.setOption(input.name, parseFloat(input.dataset["defaultValue"]));
                    }
                    break;

                case (/checkbox/g).test(input.type):
                    if (!input.hasAttribute('data-default-value') && that.editor.getOptions().hasOwnProperty(input.name) && Boolean(that.editor.getOptions()[input.name])) {
                        input.setAttribute('checked', Boolean(that.editor.getOptions()[input.name]).toString())
                        that.ace.saveOptions[input.name] = Boolean(that.editor.getOptions()[input.name])
                        return;
                    } else if (input.hasAttribute('data-default-value')) {
                        if (JSON.parse(input.dataset["defaultValue"])) {
                            input.setAttribute('checked', JSON.parse(input.dataset["defaultValue"]))
                        }
                        that.ace.saveOptions[input.name] = JSON.parse(input.dataset["defaultValue"])
                        that.editor.setOption(input.name, JSON.parse(input.dataset["defaultValue"]))
                    } else {
                        that.ace.saveOptions[input.name] = Boolean(that.editor.getOptions()[input.name])
                    }
                    break;
            }
        })
    }

    /**
     * Copy to clipboard event
     * @param {Event} event
     */
    copyToClipboard(event){
        event.preventDefault();
        let value = {}
        let that = this;
        Array.from(this.container.querySelectorAll('input.input-options,select.input-options')).forEach((dom) => {
            switch (true) {
                case (/checkbox/g).test(dom.type):
                    if (JSON.parse(dom.checked) !== that.ace.saveOptions[dom.name]) {
                        value[dom.name] = dom.checked
                    }
                    break;

                case (/range/g).test(dom.type):
                    if (parseFloat(dom.value) !== that.ace.saveOptions[dom.name]) {
                        value[dom.name] = parseFloat(dom.value)
                    }
                    break;

                case (/select/g).test(dom.type):
                    let getValue = dom.options[dom.selectedIndex].value;
                    if (getValue !== that.ace.saveOptions[dom.name]) {
                        value[dom.name] = getValue;
                    }
                    break;

                case (/number/g).test(dom.type):
                    if (parseFloat(dom.value) !== that.ace.saveOptions[dom.name]) {
                        value[dom.name] = parseFloat(dom.value)
                    }
                    break;
            }
        })

        // Run Copy to clipboard if value is more than one
        if (Object.keys(value).length > 0) {
            if (Object.keys(this.originalOptionsValue).length > 0) {
                value = {
                    ...this.originalOptionsValue,
                    ...value
                }
            }
            this.container.querySelector('.copy-options').dataset.clipboardText = JSON.stringify(JSON.stringify(value))
            this.container.querySelector('.copy-options').click()
            this.#outputNotification(Object.keys(value).length + ` item${Object.keys(value).length > 0 ? 's' : ''} copied`);
        } else {
            this.#outputNotification('No changes');
        }
    }

    /**
     * Output notification on change
     * @param {string} text
     */
    #outputNotification(text) {
        this.container.querySelector('.changes-copy').style.removeProperty('display');
        this.container.querySelector('.changes-copy').innerText = text;
        let that = this;
        setTimeout(() => {
            that.container.querySelector('.changes-copy').style.display = 'none';
        }, that.notificationTimeout)
    }

    /**
     * Reset options event
     * @param {Event} event
     */
    resetOptions(event){
        event.preventDefault();
        let that = this;
        Array.from(this.container.querySelectorAll('input.input-options,select.input-options')).forEach((dom) => {
            switch (true) {
                case (/checkbox/g).test(dom.type):
                    if (JSON.parse(dom.checked) !== that.ace.saveOptions[dom.name]) {
                        dom.checked = JSON.parse(that.ace.saveOptions[dom.name])
                        that.editor.setOption(dom.name, dom.checked)
                    }
                    break;

                case (/range/g).test(dom.type):
                    if (parseFloat(dom.value) !== that.ace.saveOptions[dom.name]) {
                        dom.value = that.ace.saveOptions[dom.name]
                        that.editor.setOption(dom.name, dom.value)
                    }
                    break;

                case (/select/g).test(dom.type):
                    let getValue = dom.options[dom.selectedIndex].value;
                    if (getValue !== that.ace.saveOptions[dom.name]) {
                        // Set Editor Option Value
                        switch (this.ace.saveOptions[dom.name]) {
                            case "true":
                                that.editor.setOption(dom.name, JSON.parse(that.ace.saveOptions[dom.name]))
                                break;

                            case "false":
                                that.editor.setOption(dom.name, JSON.parse(that.ace.saveOptions[dom.name]))
                                break;

                            default:
                                that.editor.setOption(dom.name, that.ace.saveOptions[dom.name])
                        }
                        // Set default on select html
                        dom.selectedIndex = Array.from(dom.options).filter(val => val.value === that.ace.saveOptions[dom.name]).reduce((val, next) => next, -1).index

                    }
                    break;

                case (/number/g).test(dom.type):
                    if (parseFloat(dom.value) !== that.ace.saveOptions[dom.name]) {
                        dom.value = that.ace.saveOptions[dom.name]
                        that.editor.setOption(dom.name, that.ace.saveOptions[dom.name])
                    }
                    break;
            }
        })
        this.#outputNotification('Changes reset');
    }

    /**
     * Set Dropdown configurations
     */
    dropdownConfig() {
        if (CustomCodeEditor.has(this.dropdownConfigValue, 'position.top')) {
            this.container.querySelector('.dropdown').style.top = this.dropdownConfigValue.position.top
        }

        if (CustomCodeEditor.has(this.dropdownConfigValue, 'position.left')) {
            this.container.querySelector('.dropdown').style.left = this.dropdownConfigValue.position.left
        }

        if (CustomCodeEditor.has(this.dropdownConfigValue, 'position.right')) {
            this.container.querySelector('.dropdown').style.right = this.dropdownConfigValue.position.right
        }

        if (CustomCodeEditor.has(this.dropdownConfigValue, 'position.bottom')) {
            this.container.querySelector('.dropdown').style.bottom = this.dropdownConfigValue.position.bottom
        }

        if (CustomCodeEditor.has(this.dropdownConfigValue, 'height')) {
            this.container.querySelector('.dropdown').style.height = this.dropdownConfigValue.height
        }

        if (CustomCodeEditor.has(this.dropdownConfigValue, 'borderRadius')) {
            this.container.querySelector('.dropdown').style.borderRadius = this.dropdownConfigValue.borderRadius
        }

        if (CustomCodeEditor.has(this.dropdownConfigValue, 'boxShadow')) {
            this.container.querySelector('.dropdown').style.boxShadow = this.dropdownConfigValue.boxShadow
        }

        if (CustomCodeEditor.has(this.dropdownConfigValue, 'width')) {
            this.container.querySelector('.dropdown').style.width = this.dropdownConfigValue.width
        }

        if (CustomCodeEditor.has(this.dropdownConfigValue, 'backgroundColor')) {
            this.container.querySelector('.dropdown').style.backgroundColor = this.dropdownConfigValue.backgroundColor
        }

    }

    /**
     * Set Read Only Container configurations
     */
    readOnlyConfig() {
        if (CustomCodeEditor.has(this.readOnlyConfigValue, 'position.top')) {
            this.container.querySelector('.switch').style.top = this.readOnlyConfigValue.position.top
        }

        if (CustomCodeEditor.has(this.readOnlyConfigValue, 'position.left')) {
            this.container.querySelector('.switch').style.left = this.readOnlyConfigValue.position.left
        }

        if (CustomCodeEditor.has(this.readOnlyConfigValue, 'position.right')) {
            this.container.querySelector('.switch').style.right = this.readOnlyConfigValue.position.right
        }

        if (CustomCodeEditor.has(this.readOnlyConfigValue, 'position.bottom')) {
            this.container.querySelector('.switch').style.bottom = this.readOnlyConfigValue.position.bottom
        }

        if (CustomCodeEditor.has(this.readOnlyConfigValue, 'height')) {
            this.container.querySelector('.switch').style.height = this.readOnlyConfigValue.height
        }

        if (CustomCodeEditor.has(this.readOnlyConfigValue, 'borderRadius')) {
            this.container.querySelector('.switch').style.borderRadius = this.readOnlyConfigValue.borderRadius
        }

        if (CustomCodeEditor.has(this.readOnlyConfigValue, 'boxShadow')) {
            this.container.querySelector('.switch').style.boxShadow = this.readOnlyConfigValue.boxShadow
        }

        if (CustomCodeEditor.has(this.readOnlyConfigValue, 'width')) {
            this.container.querySelector('.switch').style.width = this.readOnlyConfigValue.width
        }

        if (CustomCodeEditor.has(this.readOnlyConfigValue, 'backgroundColor')) {
            this.container.querySelector('.switch').style.backgroundColor = this.readOnlyConfigValue.backgroundColor
        }

    }

    /**
     * Set Editor configurations
     */
    editorConfig(){
        if (CustomCodeEditor.has(this.editorValue, 'fontSize')) {
            this.editor.setOptions({
                "fontSize": this.editorValue.fontSize
            })
        }

        if (CustomCodeEditor.has(this.editorValue, 'height')) {
            this.container.querySelector('.code-snippet-wrapper').style.height = this.editorValue.height;
        }

        if (CustomCodeEditor.has(this.editorValue, 'width')) {
            this.container.querySelector('.code-snippet-wrapper').style.width = this.editorValue.width;
        }
    }

    /**
     * Set Editor Mode
     * @param {string} mode
     */
    setMode(mode){
        this.editor.session.setMode('ace/mode/' + mode);
    }

    /**
     * Get Editor Mode
     * @returns {string}
     */
    getMode(){
        return this.editor.session.getMode().$id.match(/(?!([\/\\]))\w*$/g)[0]
    }

    /**
     * Get Mode Title
     * @param {string} name
     * @returns {string}
     */
    getModeTitle(name) {
        let mode = this.ace.modes.filter((val) => val.name === name)

        if(mode.length > 0 && mode[0].title) {
            return mode[0].title
        } else {
            return CustomCodeEditor.capitalize(mode.name || name);
        }
    }

    /**
     * Set Editor Theme
     * @param {string} name
     */
    setTheme(name) {
        this.editor.setTheme('ace/theme/' + name);
    }

    /**
     * Set Editor Value
     * @param {string} mode
     * @param {string | null} code
     */
    setValue(mode, code){
        this.setMode(mode)
        this.editor.setValue(code || '');
        this.textarea.value = this.stringifyJSON({
            mode,
            code: code || ''
        })
    }

    /**
     * Get Editor Object
     * @returns {ace}
     */
    get getEditor(){
        return this.editor
    }

    /**
     * Set Editor Commands
     */
    commands() {
        // Save new value when press save command
        const that = this;
        this.editor.commands.addCommand({
            name: 'saveNewCode',
            bindKey: {
                win: (CustomCodeEditor.has(this.ace, 'saveCommandConfig.win')) ? this.ace["saveCommandConfig"].win : 'Alt-Shift-S',
                mac: (CustomCodeEditor.has(this.ace, 'saveCommandConfig.mac')) ? this.ace["saveCommandConfig"].mac : 'Option-Shift-S'
            },
            exec: function (editor) {
                that.originalValue.code = editor.getSelectedText();
            },
            readOnly: false
        });
    }

    /**
     * Editor on change events
     * @param {Event} _event
     */
    onChange(_event){
        let value = this.getValue()

        if(value && this.active){
            this.textarea.value = this.stringifyJSON({
                mode: value.mode,
                code: value.code
            })
        }
    }

    /**
     * Get current value from Editor
     * @returns {{mode: string, code: string}|null}
     */
    getValue(){
        let mode = this.editor.session.getMode().$id.match(/(?!([\/\\]))\w*$/g)[0]
        if(this.editor.getValue().length > 0) {
            return {
                mode: mode,
                code: this.editor.getValue()
            }
        }

        return null;
    }

    /**
     * Trim any contents
     * @param str
     * @returns {string}
     */
    trim(str) {
        return str.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g, '');
    };

    /**
     * Stringify JSON
     * @param {string} mode
     * @param {string | null} code
     * @returns {string}
     */
    stringifyJSON({mode, code}){
        return JSON.stringify({
            mode,
            code: code ? this.trim(code) : code,
        })
    }

    /**
     * Set from camelCase to word
     * @param {string} str
     * @returns {string}
     */
    static camelCaseToWords(str) {
        const result = str.replace(/([A-Z])/g, ' $1');
        return result.charAt(0).toUpperCase() + result.slice(1);
    }

    /**
     * To clone any objects
     * @param {Object} obj
     * @returns {*}
     */
    static cloneDeep(obj) {
        return JSON.parse(JSON.stringify(obj));
    }

    /**
     * Check if array
     * @param {*} item
     * @returns {boolean}
     */
    static isArray(item) {
        if (!item) {
            return false;
        }
        // check if got object in it
        for (let i = 0; i < item.length; i++) {
            if (item[i].constructor === Object) {
                return false
            }
        }
        return item && typeof item === 'object' && item.constructor === Array;
    }

    /**
     * Check if object
     * @param {*} item
     * @returns {boolean}
     */
    static isObject(item) {
        if (!item) {
            return false;
        }
        return item && typeof item === 'object' && item.constructor === Object;
    }

    /**
     * Check if string
     * @param {*} item
     * @returns {boolean}
     */
    static isString(item) {
        if (!item) {
            return false;
        }
        return typeof item === 'string' && typeof item.length === 'number'
    }

    /**
     * Check if array of objects
     * @param {*} item
     * @returns {boolean}
     */
    static isArrayOfObject(item) {
        if (!item) {
            return false;
        }

        // check if got object in it
        for (let i = 0; i < item.length; i++) {
            if (item[i].constructor !== Object) {
                return false
            }
        }

        // Also check if the item is not a string
        return !this.isString(item);
    }

    /**
     * Replace lodash _.has()
     * @param {Object} object
     * @param {string} path
     * @returns {*}
     */
    static has(object, path) {
        let curObj = object;
        let pathArr = path.match(/([^.[\]]+)/g);
        for (let p in pathArr) {
            if (curObj === undefined || curObj === null) return curObj; // should probably test for object/array instead
            curObj = curObj[pathArr[p]];
        }
        return curObj;
    }

    /**
     * Capitalize String
     * @param {string} str
     * @returns {string}
     */
    static capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    // Widget Adapter Functions
    setState(value) {
        if(typeof value === "string") {
            value = JSON.parse(value);
        }
        this.setValue(value.mode, value.code)
    }

    getState() {
        return this.getValue();
    }

    focus(soft) {
        if(soft){
            this.editor.focus();
        }
    }

    disconnect() {
        this.editor.destroy();
        this.disconnectAllEvents();
        this.off('switchMode', this.switchModeState.bind(this))
    }
}