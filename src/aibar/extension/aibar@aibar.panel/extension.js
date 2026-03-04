/**
 * @file extension.js
 * @brief GNOME Shell panel extension for aibar metrics.
 * @details Collects usage JSON from the aibar CLI and renders provider-specific quota/cost cards in the GNOME panel popup.
 */
import GLib from 'gi://GLib';
import St from 'gi://St';
import Gio from 'gi://Gio';
import Clutter from 'gi://Clutter';
import GObject from 'gi://GObject';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';

const REFRESH_INTERVAL_SECONDS = 300;
const ENV_FILE_PATH = GLib.get_home_dir() + '/.config/aibar/env';

/**
 * @brief Resolve aibar executable path.
 * @details Prefers PATH discovery and falls back to AIBAR_PATH from the env file.
 * @returns {string} Resolved executable path or fallback command name.
 */
function _getAiBarPath() {
    let found = GLib.find_program_in_path('aibar');
    if (found)
        return found;

    let env = _loadEnvFromFile();
    if (env.AIBAR_PATH)
        return env.AIBAR_PATH;

    return 'aibar';
}

/**
 * @brief Load key-value environment variables from aibar env file.
 * @details Parses export syntax, quoted values, and inline comments.
 * @returns {Object<string,string>} Parsed environment map.
 */
function _loadEnvFromFile() {
    let env = {};

    try {
        let [ok, contents] = GLib.file_get_contents(ENV_FILE_PATH);
        if (!ok || !contents)
            return env;

        let text;
        if (contents instanceof Uint8Array)
            text = new TextDecoder('utf-8').decode(contents);
        else
            text = contents.toString();

        let lines = text.split('\n');

        for (let line of lines) {
            let trimmed = line.trim();
            if (!trimmed || trimmed.startsWith('#'))
                continue;

            let hashIndex = trimmed.indexOf('#');
            if (hashIndex !== -1) {
                let beforeHash = trimmed.slice(0, hashIndex);
                let singleQuotes = (beforeHash.match(/'/g) || []).length;
                let doubleQuotes = (beforeHash.match(/"/g) || []).length;
                if (singleQuotes % 2 === 0 && doubleQuotes % 2 === 0)
                    trimmed = beforeHash.trim();
            }

            let match = trimmed.match(/^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$/);
            if (!match)
                continue;

            let name = match[1];
            let value = match[2].trim();

            if (value.endsWith(';'))
                value = value.slice(0, -1).trim();

            if ((value.startsWith('"') && value.endsWith('"')) ||
                (value.startsWith("'") && value.endsWith("'")))
                value = value.slice(1, -1);

            if (value)
                env[name] = value;
        }
    } catch (_e) {
        return env;
    }

    return env;
}

/**
 * @brief Map percentage usage to CSS progress severity class.
 * @param {number} pct Usage percentage.
 * @returns {string} CSS class suffix for progress state.
 */
function _getProgressClass(pct) {
    if (pct < 50)
        return 'aibar-progress-ok';
    if (pct < 80)
        return 'aibar-progress-warning';
    return 'aibar-progress-danger';
}

const AIBarIndicator = GObject.registerClass(
/** @brief Panel indicator widget that manages popup rendering and refresh lifecycle. */
class AIBarIndicator extends PanelMenu.Button {

    /**
     * @brief Execute init.
     * @details Applies init logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     */
    _init() {
        super._init(0.0, 'IABar Monitor', false);

        this._timeout = null;
        this._usageData = {};
        this._providerRows = {};
        this._providerTabs = {};
        this._lastUpdated = null;
        this._activeProvider = null;
        this._providerOrder = ['claude', 'openrouter', 'copilot', 'codex'];

        this._buildPanelButton();
        this._buildPopupMenu();
        this._refreshData();
        this._startAutoRefresh();
    }

    /**
     * @brief Execute build panel button.
     * @details Applies build panel button logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     */
    _buildPanelButton() {
        this._panelBox = new St.BoxLayout({
            style_class: 'panel-status-menu-box',
        });

        this._icon = new St.Icon({
            icon_name: 'utilities-system-monitor-symbolic',
            style_class: 'system-status-icon',
        });

        this._panelLabel = new St.Label({
            text: '...',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-label',
        });

        this._panelPercentages = new St.BoxLayout({
            vertical: false,
            style_class: 'aibar-panel-percentages',
        });

        this._panelClaudePctLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-tab-label-claude',
        });

        this._panelCopilotPctLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-tab-label-copilot',
        });

        this._panelCodexPctLabel = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style_class: 'aibar-panel-pct aibar-tab-label-codex',
        });

        this._panelClaudePctLabel.hide();
        this._panelCopilotPctLabel.hide();
        this._panelCodexPctLabel.hide();

        this._panelPercentages.add_child(this._panelClaudePctLabel);
        this._panelPercentages.add_child(this._panelCopilotPctLabel);
        this._panelPercentages.add_child(this._panelCodexPctLabel);

        this._panelBox.add_child(this._icon);
        this._panelBox.add_child(this._panelPercentages);
        this._panelBox.add_child(this._panelLabel);
        this.add_child(this._panelBox);
    }

    /**
     * @brief Execute build popup menu.
     * @details Applies build popup menu logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     */
    _buildPopupMenu() {
        let headerBox = new St.BoxLayout({
            vertical: false,
            style_class: 'aibar-header',
        });

        let headerIcon = new St.Icon({
            icon_name: 'utilities-system-monitor-symbolic',
            icon_size: 20,
        });

        let headerLabel = new St.Label({
            text: 'AIBar',
            style_class: 'aibar-header-label',
            y_align: Clutter.ActorAlign.CENTER,
        });

        headerBox.add_child(headerIcon);
        headerBox.add_child(headerLabel);

        let headerItem = new PopupMenu.PopupBaseMenuItem({reactive: false});
        headerItem.add_child(headerBox);
        this.menu.addMenuItem(headerItem);

        this._tabBar = new St.BoxLayout({
            vertical: false,
            style_class: 'aibar-tab-bar',
        });

        let tabBarItem = new PopupMenu.PopupBaseMenuItem({reactive: false});
        tabBarItem.add_child(this._tabBar);
        this.menu.addMenuItem(tabBarItem);

        let separator1 = new PopupMenu.PopupSeparatorMenuItem();
        separator1.style_class = 'aibar-separator';
        this.menu.addMenuItem(separator1);

        this._providersContainer = new St.BoxLayout({
            vertical: true,
            x_expand: true,
            style_class: 'aibar-providers',
        });

        let providersItem = new PopupMenu.PopupBaseMenuItem({reactive: false});
        providersItem.add_child(this._providersContainer);
        this.menu.addMenuItem(providersItem);

        let separator2 = new PopupMenu.PopupSeparatorMenuItem();
        separator2.style_class = 'aibar-separator';
        this.menu.addMenuItem(separator2);

        let refreshItem = new PopupMenu.PopupMenuItem('Refresh Now');
        refreshItem.connect('activate', () => {
            this._refreshData();
        });
        this.menu.addMenuItem(refreshItem);

        let openUiItem = new PopupMenu.PopupMenuItem('Open AIBar UI');
        openUiItem.connect('activate', () => {
            this._openTerminalWithCommand(`${_getAiBarPath()} ui`);
        });
        this.menu.addMenuItem(openUiItem);

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        this._lastUpdatedItem = new PopupMenu.PopupMenuItem('Last updated: Never', {
            reactive: false,
        });
        this._lastUpdatedItem.label.style_class = 'aibar-last-updated';
        this.menu.addMenuItem(this._lastUpdatedItem);
    }

    /**
     * @brief Execute create tab.
     * @details Applies create tab logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @param {any} providerName Input parameter `providerName`.
     * @returns {any} Function return value.
     */
    _createTab(providerName) {
        let tab = new St.Button({
            style_class: 'aibar-tab',
            can_focus: true,
        });

        let tabLabel = new St.Label({
            text: providerName.toUpperCase(),
            style_class: `aibar-tab-label aibar-tab-label-${providerName}`,
        });

        tab.set_child(tabLabel);
        tab.connect('clicked', () => {
            this._switchToProvider(providerName);
        });

        return {button: tab, label: tabLabel};
    }

    /**
     * @brief Execute switch to provider.
     * @details Applies switch to provider logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @param {any} providerName Input parameter `providerName`.
     * @returns {any} Function return value.
     */
    _switchToProvider(providerName) {
        if (this._activeProvider === providerName)
            return;

        this._activeProvider = providerName;

        for (let [name, tabData] of Object.entries(this._providerTabs)) {
            if (name === providerName)
                tabData.button.style_class = `aibar-tab-active aibar-tab-active-${name}`;
            else
                tabData.button.style_class = 'aibar-tab';
        }

        for (let [name, card] of Object.entries(this._providerRows)) {
            if (name === providerName) {
                card.container.show();
                if (this._usageData[name])
                    this._populateProviderCard(card, name, this._usageData[name]);
            } else {
                card.container.hide();
            }
        }
    }

    /**
     * @brief Execute update provider card.
     * @details Applies update provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @param {any} providerName Input parameter `providerName`.
     * @param {any} data Input parameter `data`.
     * @returns {any} Function return value.
     */
    _updateProviderCard(providerName, data) {
        let card = this._providerRows[providerName];

        if (!card) {
            card = this._createProviderCard(providerName);
            this._providerRows[providerName] = card;
            this._providersContainer.add_child(card.container);

            if (this._activeProvider && this._activeProvider !== providerName)
                card.container.hide();
        }

        this._populateProviderCard(card, providerName, data);
    }

    /**
     * @brief Execute create provider card.
     * @details Applies create provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @param {any} providerName Input parameter `providerName`.
     * @returns {any} Function return value.
     */
    _createProviderCard(providerName) {
        let container = new St.BoxLayout({
            vertical: true,
            x_expand: true,
            style_class: `aibar-card aibar-provider-${providerName}`,
        });

        let header = new St.Label({
            text: providerName.toUpperCase(),
        });
        header.hide();
        container.add_child(header);

        let progressContainer = new St.BoxLayout({
            vertical: false,
            x_expand: true,
            style_class: 'aibar-progress-row',
        });

        let progressBg = new St.BoxLayout({
            style_class: 'aibar-progress-bg',
            x_expand: true,
        });

        let progressFill = new St.Widget({
            style_class: 'aibar-progress-fill',
        });

        progressBg.add_child(progressFill);
        progressContainer.add_child(progressBg);

        let progressLabel = new St.Label({
            text: '',
            style_class: 'aibar-progress-label',
        });
        progressContainer.add_child(progressLabel);

        container.add_child(progressContainer);

        const createWindowBar = (labelText) => {
            let barContainer = new St.BoxLayout({
                vertical: true,
                x_expand: true,
                style_class: 'aibar-window-bar',
            });

            let row = new St.BoxLayout({
                vertical: false,
                x_expand: true,
                style_class: 'aibar-window-row',
            });

            let label = new St.Label({
                text: labelText,
                style_class: 'aibar-window-label',
            });

            let barBg = new St.BoxLayout({
                style_class: 'aibar-progress-bg',
                x_expand: true,
            });

            let barFill = new St.Widget({
                style_class: 'aibar-progress-fill',
            });

            let pctLabel = new St.Label({
                text: '',
                style_class: 'aibar-window-pct',
            });

            let resetLabel = new St.Label({
                text: '',
                style_class: 'aibar-reset-label',
            });

            barBg.add_child(barFill);
            row.add_child(label);
            row.add_child(barBg);
            row.add_child(pctLabel);
            barContainer.add_child(row);
            barContainer.add_child(resetLabel);
            barContainer.hide();

            return {container: barContainer, row, label, barBg, barFill, pctLabel, resetLabel};
        };

        let windowBars = new St.BoxLayout({
            vertical: true,
            x_expand: true,
            style_class: 'aibar-window-bars',
        });

        let fiveHourBar = createWindowBar('5h');
        let sevenDayBar = createWindowBar('7d');

        windowBars.add_child(fiveHourBar.container);
        windowBars.add_child(sevenDayBar.container);
        windowBars.hide();

        container.add_child(windowBars);

        let statsGrid = new St.BoxLayout({
            vertical: true,
            style_class: 'aibar-stats',
        });

        let costLabel = new St.Label({style_class: 'aibar-cost'});
        costLabel.clutter_text.set_use_markup(true);
        let byokLabel = new St.Label({style_class: 'aibar-stat'});
        let requestsLabel = new St.Label({style_class: 'aibar-stat'});
        let tokensLabel = new St.Label({style_class: 'aibar-stat'});
        let resetsLabel = new St.Label({style_class: 'aibar-stat-reset'});
        let errorLabel = new St.Label({style_class: 'aibar-error'});

        statsGrid.add_child(costLabel);
        statsGrid.add_child(byokLabel);
        statsGrid.add_child(requestsLabel);
        statsGrid.add_child(tokensLabel);
        statsGrid.add_child(resetsLabel);
        statsGrid.add_child(errorLabel);

        container.add_child(statsGrid);

        return {
            container,
            header,
            progressContainer,
            progressBg,
            progressFill,
            progressLabel,
            windowBars,
            fiveHourBar,
            sevenDayBar,
            costLabel,
            byokLabel,
            requestsLabel,
            tokensLabel,
            resetsLabel,
            errorLabel,
            _barData: {},
        };
    }

    /**
     * @brief Execute populate provider card.
     * @details Applies populate provider card logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @param {any} card Input parameter `card`.
     * @param {any} providerName Input parameter `providerName`.
     * @param {any} data Input parameter `data`.
     * @returns {any} Function return value.
     */
    _populateProviderCard(card, providerName, data) {
        const metrics = data.metrics || {};
        const isError = data.error !== null && data.error !== undefined;

        if (isError) {
            card.errorLabel.text = `⚠️ ${data.error}`;
            card.errorLabel.show();
            card.costLabel.text = '';
            card.byokLabel.text = '';
            card.requestsLabel.text = '';
            card.tokensLabel.text = '';
            card.resetsLabel.text = '';
            card.progressFill.style_class = 'aibar-progress-fill aibar-progress-danger';
            card.progressFill.set_width(0);
            card.progressLabel.text = '';
            card.windowBars.hide();
            card.fiveHourBar.container.hide();
            card.sevenDayBar.container.hide();
            card.progressContainer.show();
            return;
        }

        card.errorLabel.hide();

        const raw = data.raw || {};
        const fiveHourUtil = raw.five_hour && raw.five_hour.utilization !== null && raw.five_hour.utilization !== undefined
            ? raw.five_hour.utilization
            : (raw.rate_limit && raw.rate_limit.primary_window && raw.rate_limit.primary_window.used_percent !== null && raw.rate_limit.primary_window.used_percent !== undefined
                ? raw.rate_limit.primary_window.used_percent
                : null);
        const sevenDayUtil = raw.seven_day && raw.seven_day.utilization !== null && raw.seven_day.utilization !== undefined
            ? raw.seven_day.utilization
            : (raw.rate_limit && raw.rate_limit.secondary_window && raw.rate_limit.secondary_window.used_percent !== null && raw.rate_limit.secondary_window.used_percent !== undefined
                ? raw.rate_limit.secondary_window.used_percent
                : null);

        const updateWindowBar = (bar, pct, resetTime, useDays) => {
            bar.pctLabel.text = `${pct.toFixed(1)}%`;
            bar.barFill.style_class = `aibar-progress-fill ${_getProgressClass(pct)}`;

            GLib.idle_add(GLib.PRIORITY_DEFAULT_IDLE, () => {
                let barBgWidth = bar.barBg.get_width();
                if (barBgWidth > 0) {
                    let width = Math.round((pct / 100) * barBgWidth);
                    bar.barFill.set_width(width);
                }
                return GLib.SOURCE_REMOVE;
            });

            if (resetTime) {
                let resetDate;
                if (typeof resetTime === 'number')
                    resetDate = new Date(resetTime * 1000);
                else
                    resetDate = new Date(resetTime);

                let now = new Date();
                let diffMs = resetDate - now;
                if (diffMs > 0) {
                    let days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                    let hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    let mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                    if (useDays && days > 0)
                        bar.resetLabel.text = `Reset in: ${days}d ${hours}h ${mins}m`;
                    else
                        bar.resetLabel.text = `Reset in: ${days * 24 + hours}h ${mins}m`;
                    bar.resetLabel.show();
                } else {
                    bar.resetLabel.text = '';
                    bar.resetLabel.hide();
                }
            } else {
                bar.resetLabel.text = '';
                bar.resetLabel.hide();
            }

            bar.container.show();
        };

        let fiveHourReset = null;
        let sevenDayReset = null;

        if (raw.five_hour && raw.five_hour.resets_at)
            fiveHourReset = raw.five_hour.resets_at;
        if (raw.seven_day && raw.seven_day.resets_at)
            sevenDayReset = raw.seven_day.resets_at;

        if (raw.rate_limit && raw.rate_limit.primary_window && raw.rate_limit.primary_window.reset_at)
            fiveHourReset = raw.rate_limit.primary_window.reset_at;
        if (raw.rate_limit && raw.rate_limit.secondary_window && raw.rate_limit.secondary_window.reset_at)
            sevenDayReset = raw.rate_limit.secondary_window.reset_at;

        let usagePercent = metrics.usage_percent;
        if ((usagePercent === null || usagePercent === undefined) &&
            metrics.limit !== null && metrics.limit !== undefined &&
            metrics.remaining !== null && metrics.remaining !== undefined) {
            usagePercent = ((metrics.limit - metrics.remaining) / metrics.limit) * 100;
        }

        let hasWindowBars = false;
        if (providerName === 'copilot' && usagePercent !== null && usagePercent !== undefined) {
            card.fiveHourBar.label.text = '30d';
            card._barData.fiveHour = {pct: usagePercent, resetTime: metrics.reset_at || null};
            updateWindowBar(card.fiveHourBar, usagePercent, metrics.reset_at || null, true);
            card._barData.sevenDay = null;
            card.sevenDayBar.container.hide();
            hasWindowBars = true;
        } else {
            card.fiveHourBar.label.text = '5h';
            if (fiveHourUtil !== null) {
                card._barData.fiveHour = {pct: fiveHourUtil, resetTime: fiveHourReset};
                updateWindowBar(card.fiveHourBar, fiveHourUtil, fiveHourReset, false);
                hasWindowBars = true;
            } else {
                card._barData.fiveHour = null;
                card.fiveHourBar.container.hide();
            }

            if (sevenDayUtil !== null) {
                card._barData.sevenDay = {pct: sevenDayUtil, resetTime: sevenDayReset};
                updateWindowBar(card.sevenDayBar, sevenDayUtil, sevenDayReset, true);
                hasWindowBars = true;
            } else {
                card._barData.sevenDay = null;
                card.sevenDayBar.container.hide();
            }
        }

        if (hasWindowBars) {
            card.windowBars.show();
            card.progressContainer.hide();
            card.resetsLabel.hide();
        } else {
            card.windowBars.hide();
            card.progressContainer.show();
            card.resetsLabel.show();
        }

        if (!hasWindowBars) {
            if (usagePercent !== null && usagePercent !== undefined) {
                let pct = usagePercent;
                card._barData.progress = {pct};
                card.progressLabel.text = `${pct.toFixed(1)}%`;
                card.progressFill.style_class = `aibar-progress-fill ${_getProgressClass(pct)}`;

                GLib.idle_add(GLib.PRIORITY_DEFAULT_IDLE, () => {
                    let barBgWidth = card.progressBg ? card.progressBg.get_width() : 0;
                    if (barBgWidth > 0) {
                        let width = Math.round((pct / 100) * barBgWidth);
                        card.progressFill.set_width(width);
                    }
                    return GLib.SOURCE_REMOVE;
                });
            } else {
                card._barData.progress = null;
                card.progressFill.style_class = 'aibar-progress-fill aibar-progress-none';
                card.progressFill.set_width(0);
                card.progressLabel.text = '';
            }
        } else {
            card._barData.progress = null;
        }

        if (metrics.cost !== null && metrics.cost !== undefined) {
            if (providerName === 'openrouter' && metrics.limit !== null && metrics.limit !== undefined)
                card.costLabel.text = `$${metrics.cost.toFixed(4)} / $${metrics.limit.toFixed(2)}`;
            else
                card.costLabel.text = `$${metrics.cost.toFixed(4)}`;
        } else if (metrics.remaining !== null && metrics.limit !== null) {
            card.costLabel.clutter_text.set_markup(
                `Remaining credits: <b>${metrics.remaining.toFixed(1)}</b>/${metrics.limit.toFixed(1)}`
            );
        } else {
            card.costLabel.text = '';
        }

        if (providerName === 'openrouter' && raw.data) {
            let byokValue = null;
            if (data.window === '5h')
                byokValue = raw.data.byok_usage_daily;
            else if (data.window === '30d')
                byokValue = raw.data.byok_usage_monthly;
            else
                byokValue = raw.data.byok_usage_weekly;

            if (byokValue !== null && byokValue !== undefined && byokValue > 0)
                card.byokLabel.text = `BYOK: $${byokValue.toFixed(4)}`;
            else
                card.byokLabel.text = '';
        } else {
            card.byokLabel.text = '';
        }

        if (metrics.requests !== null && metrics.requests !== undefined)
            card.requestsLabel.text = `${metrics.requests.toLocaleString()} requests`;
        else
            card.requestsLabel.text = '';

        if (metrics.input_tokens !== null || metrics.output_tokens !== null) {
            let total = (metrics.input_tokens || 0) + (metrics.output_tokens || 0);
            card.tokensLabel.text = `${total.toLocaleString()} tokens`;
        } else {
            card.tokensLabel.text = '';
        }

        if (metrics.reset_at) {
            let resetDate = new Date(metrics.reset_at);
            let now = new Date();
            let diffMs = resetDate - now;
            if (diffMs > 0) {
                let days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
                let hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                let mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                if (days > 0)
                    card.resetsLabel.text = `Reset in: ${days}d ${hours}h ${mins}m`;
                else
                    card.resetsLabel.text = `Reset in: ${hours}h ${mins}m`;
            } else {
                card.resetsLabel.text = '';
            }
        } else {
            card.resetsLabel.text = '';
        }
    }

    /**
     * @brief Execute start auto refresh.
     * @details Applies start auto refresh logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     */
    _startAutoRefresh() {
        if (this._timeout)
            GLib.source_remove(this._timeout);

        this._timeout = GLib.timeout_add_seconds(
            GLib.PRIORITY_DEFAULT,
            REFRESH_INTERVAL_SECONDS,
            () => {
                this._refreshData();
                return GLib.SOURCE_CONTINUE;
            }
        );
    }

    /**
     * @brief Execute refresh data.
     * @details Applies refresh data logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     */
    _refreshData() {
        this._panelLabel.set_text('...');

        try {
            let launcher = new Gio.SubprocessLauncher({
                flags: Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE,
            });

            let envFromFile = _loadEnvFromFile();
            for (let [key, value] of Object.entries(envFromFile))
                launcher.setenv(key, value, true);

            let proc = launcher.spawnv([_getAiBarPath(), 'show', '--json']);

            proc.communicate_utf8_async(null, null, (proc, result) => {
                try {
                    let [ok, stdout, stderr] = proc.communicate_utf8_finish(result);

                    if (ok && proc.get_successful() && stdout) {
                        this._parseOutput(stdout.trim());
                        this._updateUI();
                    } else {
                        this._handleError(stderr || 'Command failed');
                    }
                } catch (e) {
                    this._handleError(e.message);
                }
            });
        } catch (e) {
            this._handleError(e.message);
        }
    }

    /**
     * @brief Execute parse output.
     * @details Applies parse output logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @param {any} output Input parameter `output`.
     * @returns {any} Function return value.
     */
    _parseOutput(output) {
        console.debug('aibar: Parsing output');

        try {
            let json = JSON.parse(output);
            this._usageData = json;
            this._lastUpdated = new Date();
            console.debug(`aibar: Parsed ${Object.keys(json).length} providers`);
        } catch (e) {
            console.debug(`aibar: JSON parse error: ${e.message}`);
            this._handleError(`Parse error: ${e.message}`);
        }
    }

    /**
     * @brief Execute update u i.
     * @details Applies update u i logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     */
    _updateUI() {
        let totalCost = 0;
        let hasCostData = false;
        let configuredProviders = 0;
        const usageLabels = {
            claude: this._panelClaudePctLabel,
            copilot: this._panelCopilotPctLabel,
            codex: this._panelCodexPctLabel,
        };

        const getPanelUsagePercent = (providerName, data) => {
            if (!data)
                return null;

            const metrics = data.metrics || {};
            const raw = data.raw || {};

            if (providerName === 'copilot') {
                if (metrics.usage_percent !== null && metrics.usage_percent !== undefined)
                    return Number(metrics.usage_percent);
                if (
                    metrics.limit !== null && metrics.limit !== undefined &&
                    metrics.remaining !== null && metrics.remaining !== undefined &&
                    Number(metrics.limit) !== 0
                ) {
                    return ((Number(metrics.limit) - Number(metrics.remaining)) / Number(metrics.limit)) * 100;
                }
                return null;
            }

            if (raw.five_hour && raw.five_hour.utilization !== null && raw.five_hour.utilization !== undefined)
                return Number(raw.five_hour.utilization);

            if (raw.rate_limit && raw.rate_limit.primary_window &&
                raw.rate_limit.primary_window.used_percent !== null &&
                raw.rate_limit.primary_window.used_percent !== undefined) {
                return Number(raw.rate_limit.primary_window.used_percent);
            }

            if (
                metrics.limit !== null && metrics.limit !== undefined &&
                metrics.remaining !== null && metrics.remaining !== undefined &&
                Number(metrics.limit) !== 0
            ) {
                return ((Number(metrics.limit) - Number(metrics.remaining)) / Number(metrics.limit)) * 100;
            }

            return null;
        };

        for (let providerName of ['claude', 'copilot', 'codex']) {
            const pct = getPanelUsagePercent(providerName, this._usageData[providerName]);
            const label = usageLabels[providerName];
            if (!label)
                continue;
            if (pct !== null && Number.isFinite(pct)) {
                label.set_text(`${pct.toFixed(1)}%`);
                label.show();
            } else {
                label.set_text('');
                label.hide();
            }
        }

        const entries = Object.entries(this._usageData).sort((a, b) => {
            const aIndex = this._providerOrder.indexOf(a[0]);
            const bIndex = this._providerOrder.indexOf(b[0]);
            const aRank = aIndex === -1 ? 999 : aIndex;
            const bRank = bIndex === -1 ? 999 : bIndex;
            if (aRank !== bRank)
                return aRank - bRank;
            return a[0].localeCompare(b[0]);
        });

        for (let [providerName] of entries) {
            if (!this._providerTabs[providerName]) {
                let tabData = this._createTab(providerName);
                this._providerTabs[providerName] = tabData;
                this._tabBar.add_child(tabData.button);
            }
        }

        let firstProvider = null;
        for (let [providerName, data] of entries) {
            if (!firstProvider)
                firstProvider = providerName;

            this._updateProviderCard(providerName, data);

            if (data.metrics && data.metrics.cost !== null && data.metrics.cost !== undefined) {
                totalCost += data.metrics.cost;
                hasCostData = true;
                configuredProviders++;
            } else if (data.metrics && (data.metrics.remaining !== null || data.metrics.limit !== null)) {
                configuredProviders++;
            }
        }

        if (!this._activeProvider && firstProvider)
            this._switchToProvider(firstProvider);

        if (hasCostData)
            this._panelLabel.set_text(`$${totalCost.toFixed(2)}`);
        else if (configuredProviders > 0)
            this._panelLabel.set_text(`${configuredProviders} active`);
        else
            this._panelLabel.set_text('N/A');

        if (this._lastUpdated) {
            let timeString = this._lastUpdated.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
            });
            this._lastUpdatedItem.label.set_text(`Last updated: ${timeString}`);
        }
    }

    /**
     * @brief Execute handle error.
     * @details Applies handle error logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @param {any} message Input parameter `message`.
     * @returns {any} Function return value.
     */
    _handleError(message) {
        console.debug(`aibar Error: ${message}`);
        this._panelClaudePctLabel.set_text('');
        this._panelCopilotPctLabel.set_text('');
        this._panelCodexPctLabel.set_text('');
        this._panelClaudePctLabel.hide();
        this._panelCopilotPctLabel.hide();
        this._panelCodexPctLabel.hide();
        this._panelLabel.set_text('Err');
        this._lastUpdatedItem.label.set_text(`Error: ${message.substring(0, 40)}`);
    }

    /**
     * @brief Execute open terminal with command.
     * @details Applies open terminal with command logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @param {any} command Input parameter `command`.
     * @returns {any} Function return value.
     */
    _openTerminalWithCommand(command) {
        try {
            Gio.Subprocess.new(
                ['gnome-terminal', '--', 'bash', '-c', command + '; read -p "Press Enter to close"'],
                Gio.SubprocessFlags.NONE
            );
        } catch (e) {
            console.debug(`aibar: Failed to open terminal: ${e.message}`);
        }
    }

    /**
     * @brief Execute destroy.
     * @details Applies destroy logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     */
    destroy() {
        if (this._timeout) {
            GLib.source_remove(this._timeout);
            this._timeout = null;
        }

        super.destroy();
    }
});

/** @brief GNOME extension lifecycle adapter for AIBarIndicator registration. */
export default class AIBarExtension {
    /**
     * @brief Execute constructor.
     * @details Applies constructor logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     */
    constructor() {
        this._indicator = null;
    }

    /**
     * @brief Execute enable.
     * @details Applies enable logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     */
    enable() {
        console.debug('aibar: Enabling extension');
        this._indicator = new AIBarIndicator();
        Main.panel.addToStatusArea('aibar', this._indicator, 0, 'right');
    }

    /**
     * @brief Execute disable.
     * @details Applies disable logic for GNOME extension runtime behavior with deterministic UI and subprocess side effects.
     * @returns {any} Function return value.
     */
    disable() {
        console.debug('aibar: Disabling extension');

        if (this._indicator) {
            this._indicator.destroy();
            this._indicator = null;
        }
    }
}
