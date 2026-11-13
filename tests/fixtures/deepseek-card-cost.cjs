/**
 * @file
 * @brief Execute the DeepSeek provider card against isolated GNOME 50 APIs.
 * @details HDT Level 1 fixture. Replaces GI, Shell and subprocess boundaries with
 * in-memory actors, feeds one DeepSeek payload whose `metrics.cost` is `null`
 * (the balance endpoint exposes no cost basis), and asserts the provider card
 * hides its cost row instead of rendering an unpopulated `Costs:` value.
 * @satisfies REQ-246, REQ-252, TST-112
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

/** @brief Captured actors, asynchronous callbacks, timers and CLI argv. */
const state = {actors: [], pending: [], timers: new Map(), commands: [], nextId: 1};

/**
 * @brief Minimal actor boundary for extension behavior execution.
 * @details Stores properties and ownership in memory; O(children) storage.
 */
class Actor {
    /** @brief Construct actor state.
     * @details Rejects removed property contracts; O(1) bookkeeping.
     * @param {Object} props Initial widget properties.
     * @return {Actor} Initialized actor.
     */
    constructor(props = {}) {
        if (typeof props === 'string')
            props = {text: props};
        assert.equal('vertical' in props, false, 'Use GNOME 50 orientation');
        Object.assign(this, {visible: true, text: '', width: 240}, props);
        this.children = [];
        this.signals = new Map();
        this.clutter_text = this;
        state.actors.push(this);
    }
    /** @brief Attach child. @details Mutates ownership; O(1).
     * @param {Actor} child Child actor. @return {void} None. */
    add_child(child) { this.children.push(child); }
    /** @brief Set sole child. @details Replaces ownership; O(1).
     * @param {Actor} child Child actor. @return {void} None. */
    set_child(child) { this.children = [child]; }
    /** @brief Attach menu item. @details Mutates menu; O(1).
     * @param {Actor} child Menu item. @return {void} None. */
    addMenuItem(child) { this.add_child(child); }
    /** @brief Register signal. @details Stores callback; O(1).
     * @param {string} name Signal name. @param {Function} callback Handler.
     * @return {void} None. */
    connect(name, callback) { this.signals.set(name, callback); }
    /** @brief Set text. @details Mutates text; O(1).
     * @param {string} text Label value. @return {void} None. */
    set_text(text) { this.text = text; }
    /** @brief Set markup. @details Stores text; O(1).
     * @param {string} text Markup value. @return {void} None. */
    set_markup(text) { this.text = text; }
    /** @brief Set style. @details Stores CSS; O(1).
     * @param {string} style CSS value. @return {void} None. */
    set_style(style) { this.style = style; }
    /** @brief Set width. @details Stores geometry; O(1).
     * @param {number} width Pixel width. @return {void} None. */
    set_width(width) { this.width = width; }
    /** @brief Get width. @details Read-only; O(1). @return {number} Width. */
    get_width() { return this.width; }
    /** @brief Get height. @details Fixed allocation; O(1).
     * @return {number[]} Minimum and natural height. */
    get_preferred_height() { return [0, 100]; }
    /** @brief Show actor. @details Mutates visibility; O(1). @return {void} None. */
    show() { this.visible = true; }
    /** @brief Hide actor. @details Mutates visibility; O(1). @return {void} None. */
    hide() { this.visible = false; }
    /** @brief Destroy actor. @details Marks teardown; O(1). @return {void} None. */
    destroy() { this.destroyed = true; }
    /** @brief Accept policy. @details No rendering; O(1). @return {void} None. */
    set_policy() {}
    /** @brief Accept markup mode. @details No rendering; O(1). @return {void} None. */
    set_use_markup() {}
    /** @brief Accept class addition. @details No CSS engine; O(1). @return {void} None. */
    add_style_class_name() {}
    /** @brief Accept class removal. @details No CSS engine; O(1). @return {void} None. */
    remove_style_class_name() {}
    /** @brief Accept focus reset. @details No CSS engine; O(1). @return {void} None. */
    remove_style_pseudo_class() {}
}

/** @brief PanelMenu initialization boundary. @details Owns menu actor. */
class PanelButton extends Actor {
    /** @brief Initialize menu. @details Allocates menu; O(1). @return {void} None. */
    _init() { this.menu = new Actor(); }
}

/**
 * @brief In-memory CLI JSON payload with one DeepSeek balance-only provider.
 * @details Mirrors the normalized DeepSeek result contract: `metrics.remaining`
 * carries the total balance while `metrics.cost`, `metrics.limit`, and every
 * usage counter stay `null` because the endpoint exposes no cost basis.
 */
const payload = {
    deepseek: {
        provider: 'deepseek',
        window: '30d',
        metrics: {
            cost: null,
            total_cost: null,
            requests: null,
            input_tokens: null,
            output_tokens: null,
            remaining: 12.5,
            limit: null,
            reset_at: null,
            currency_symbol: '$',
        },
        raw: {
            is_available: true,
            deepseek_balance_infos: [{
                currency: 'USD',
                currency_symbol: '$',
                total_balance: 12.5,
                granted_balance: 2.5,
                topped_up_balance: 10.0,
            }],
        },
        updated_at: '2026-01-01T00:00:00Z',
    },
};

/** @brief Fake Gio launcher. @details Records argv; defers asynchronous completion. */
class Launcher {
    /** @brief Accept environment. @details No OS mutation; O(1). @return {void} None. */
    setenv() {}
    /** @brief Capture command and expose asynchronous completion.
     * @details Enqueues callback; returns fixed JSON; O(1) queue mutation.
     * @param {string[]} argv CLI arguments. @return {Object} Subprocess boundary.
     */
    spawnv(argv) {
        state.commands.push(argv);
        return {
            communicate_utf8_async(_input, _cancel, callback) {
                state.pending.push(() => callback(this, {}));
            },
            communicate_utf8_finish() {
                return [true, JSON.stringify({payload}), ''];
            },
            get_successful() { return true; },
        };
    }
}

/** @brief Mock GNOME module bindings; no real desktop or subprocess access. */
const context = {
    console: {debug() {}}, TextDecoder,
    St: {BoxLayout: Actor, Icon: Actor, Label: Actor, Widget: Actor,
        Button: Actor, ScrollView: Actor, PolicyType: {NEVER: 0, AUTOMATIC: 1}},
    Clutter: {ActorAlign: {CENTER: 0, END: 1},
        Orientation: {HORIZONTAL: 0, VERTICAL: 1}},
    PanelMenu: {Button: PanelButton},
    PopupMenu: {PopupBaseMenuItem: Actor, PopupSeparatorMenuItem: Actor,
        PopupMenuItem: Actor},
    GObject: {registerClass: cls => class extends cls {
        constructor() { super(); this._init(); }
    }},
    Extension: class {},
    Main: {panel: {addToStatusArea(_uuid, indicator) { state.indicator = indicator; }}},
    Gio: {SubprocessLauncher: Launcher, SubprocessFlags: {STDOUT_PIPE: 1, STDERR_PIPE: 2}},
    GLib: {
        get_home_dir: () => '/synthetic-home', find_program_in_path: () => 'aibar',
        file_get_contents: () => [false, null],
        SOURCE_REMOVE: false, SOURCE_CONTINUE: true,
        idle_add(_priority, callback) { state.pending.push(callback); return state.nextId++; },
        timeout_add_seconds(_priority, seconds, callback) {
            const id = state.nextId++;
            state.timers.set(id, {seconds, callback});
            return id;
        },
        source_remove(id) { state.timers.delete(id); },
    },
};

/** @brief Flush deterministic async queue. @details O(N) callbacks; no clock.
 * @return {void} None. */
function flush() {
    while (state.pending.length)
        state.pending.shift()();
}

/** @brief Load real extension implementation with only import boundaries replaced. */
const source = fs.readFileSync(process.argv[2], 'utf8')
    .replace(/^import .*;\n/gm, '')
    .replace('export default class AIBarExtension', 'class AIBarExtension');
vm.createContext(context);
vm.runInContext(`${source}\nglobalThis.extension = new AIBarExtension();`, context);
context.extension.enable();
flush();

const card = state.indicator._providerRows.deepseek;
assert.ok(card, 'DeepSeek card MUST exist');

/** @brief Assert the unpopulated cost row is not rendered. */
assert.equal(card.costLabel.visible, false, 'DeepSeek cost row MUST be hidden');
assert.equal(card.costLabel.text, '', 'DeepSeek cost row MUST be empty');
assert.equal(String(card.costLabel.text).includes('Costs:'), false,
    'DeepSeek card MUST NOT render a cost row');

/** @brief Assert the balance rows still render. */
assert.equal(card.byokLabel.visible, true, 'DeepSeek balance rows MUST render');
assert.ok(String(card.byokLabel.text).includes('Balance:'),
    'DeepSeek card MUST render the Balance row');
assert.ok(String(card.byokLabel.text).includes('Topped up:'),
    'DeepSeek card MUST render the Topped up row');
assert.ok(String(card.byokLabel.text).includes('Granted:'),
    'DeepSeek card MUST render the Granted row');

console.log('DeepSeek card cost suppression: hidden cost row, visible balance rows PASS');
