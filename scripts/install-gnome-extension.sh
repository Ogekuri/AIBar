#!/usr/bin/env bash
# @file install-gnome-extension.sh
# @brief Installs AIBar GNOME Shell extension to the user's local extensions directory.
# @details Resolves git project root via `git rev-parse --show-toplevel` to locate
# extension source files under `src/aibar/extension/aibar@aibar.panel/`. Copies all
# files preserving attributes to `~/.local/share/gnome-shell/extensions/aibar@aibar.panel/`.
# Validates prerequisites (git, project root, source directory, metadata.json) and exits
# non-zero with descriptive error on failure. Produces colored ANSI terminal output.
# @satisfies PRJ-008, REQ-025, REQ-026, REQ-027, REQ-028, REQ-029, REQ-030

set -euo pipefail

# --- ANSI Color Definitions ---
readonly C_RESET='\033[0m'
readonly C_BOLD='\033[1m'
readonly C_RED='\033[1;31m'
readonly C_GREEN='\033[1;32m'
readonly C_YELLOW='\033[1;33m'
readonly C_BLUE='\033[1;34m'
readonly C_CYAN='\033[1;36m'
readonly C_DIM='\033[2m'

# --- Output Helpers ---

## @brief Prints a formatted header banner.
## @param $1 {string} Header text.
print_header() {
    echo ""
    echo -e "${C_BLUE}╔══════════════════════════════════════════════════╗${C_RESET}"
    echo -e "${C_BLUE}║${C_BOLD}  AIBar GNOME Extension Installer                 ${C_RESET}${C_BLUE}║${C_RESET}"
    echo -e "${C_BLUE}╚══════════════════════════════════════════════════╝${C_RESET}"
    echo ""
}

## @brief Prints an informational message.
## @param $* {string} Message text.
info() {
    echo -e "  ${C_CYAN}[INFO]${C_RESET}  $*"
}

## @brief Prints a success message.
## @param $* {string} Message text.
success() {
    echo -e "  ${C_GREEN}[  OK]${C_RESET}  $*"
}

## @brief Prints a warning message.
## @param $* {string} Message text.
warn() {
    echo -e "  ${C_YELLOW}[WARN]${C_RESET}  $*"
}

## @brief Prints an error message to stderr and exits with status 1.
## @param $* {string} Error text.
## @return Does not return; exits with code 1.
die() {
    echo -e "  ${C_RED}[FAIL]${C_RESET}  $*" >&2
    echo ""
    exit 1
}

## @brief Prints a step progress marker.
## @param $1 {string} Step number.
## @param $2 {string} Step description.
step() {
    echo -e "  ${C_BOLD}[$1]${C_RESET} $2"
}

# --- Constants ---
readonly EXT_UUID="aibar@aibar.panel"
readonly EXT_SRC_REL="src/aibar/extension/${EXT_UUID}"
readonly EXT_TARGET_DIR="${HOME}/.local/share/gnome-shell/extensions/${EXT_UUID}"

# --- Main ---

## @brief Main installation function.
## @details Executes sequential prerequisite checks (git availability, project root
## resolution, source directory validation, metadata.json presence), creates the
## target directory if absent, and copies all extension files preserving attributes.
## @return Exit 0 on success; exit 1 on any prerequisite failure.
main() {
    print_header

    # Step 1: Check git availability
    step "1/5" "Checking git availability..."
    if ! command -v git >/dev/null 2>&1; then
        die "git is not installed or not in PATH."
    fi
    success "git found: $(git --version)"

    # Step 2: Resolve project root
    step "2/5" "Resolving project root..."
    local project_root
    if ! project_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
        die "Not inside a git repository. Run this script from within the AIBar project."
    fi
    success "Project root: ${C_DIM}${project_root}${C_RESET}"

    # Step 3: Validate source directory
    step "3/5" "Validating extension source..."
    local src_dir="${project_root}/${EXT_SRC_REL}"
    if [[ ! -d "${src_dir}" ]]; then
        die "Source directory not found: ${src_dir}"
    fi
    if [[ ! -f "${src_dir}/metadata.json" ]]; then
        die "metadata.json not found in source directory: ${src_dir}"
    fi
    local file_count
    file_count=$(find "${src_dir}" -maxdepth 1 -type f | wc -l)
    if [[ "${file_count}" -eq 0 ]]; then
        die "Source directory is empty: ${src_dir}"
    fi
    success "Source valid: ${C_DIM}${src_dir}${C_RESET} (${file_count} files)"

    # Step 4: Create target directory
    step "4/5" "Preparing target directory..."
    if [[ -d "${EXT_TARGET_DIR}" ]]; then
        info "Target directory already exists: ${C_DIM}${EXT_TARGET_DIR}${C_RESET}"
    else
        mkdir -p "${EXT_TARGET_DIR}"
        success "Created: ${C_DIM}${EXT_TARGET_DIR}${C_RESET}"
    fi

    # Step 5: Copy files
    step "5/5" "Installing extension files..."
    cp -a "${src_dir}/"* "${EXT_TARGET_DIR}/"
    success "Copied ${file_count} files to target"

    # Summary
    echo ""
    echo -e "${C_GREEN}╔══════════════════════════════════════════════════╗${C_RESET}"
    echo -e "${C_GREEN}║${C_BOLD}  Installation complete!                           ${C_RESET}${C_GREEN}║${C_RESET}"
    echo -e "${C_GREEN}╚══════════════════════════════════════════════════╝${C_RESET}"
    echo ""
    info "Extension UUID : ${C_BOLD}${EXT_UUID}${C_RESET}"
    info "Installed to   : ${C_DIM}${EXT_TARGET_DIR}${C_RESET}"
    echo ""
    warn "Restart GNOME Shell to load the extension:"
    info "  - Wayland : Log out and log back in"
    info "  - X11     : Press ${C_BOLD}Alt+F2${C_RESET}, type ${C_BOLD}r${C_RESET}, press Enter"
    echo ""
}

main "$@"
