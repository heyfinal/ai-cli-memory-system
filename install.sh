#!/bin/bash
# AI CLI Memory System - Universal Installer
# Supports macOS, Linux, and Windows (WSL)

set -e

VERSION="1.0.0"
REPO_URL="https://github.com/heyfinal/ai-cli-memory-system"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                            ║${NC}"
    echo -e "${BLUE}║         AI CLI Memory System Installer v${VERSION}          ║${NC}"
    echo -e "${BLUE}║                                                            ║${NC}"
    echo -e "${BLUE}║  Contextual persistent memory for AI CLI tools            ║${NC}"
    echo -e "${BLUE}║  • Claude Code  • Codex  • Gemini  • Aider                ║${NC}"
    echo -e "${BLUE}║                                                            ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -q Microsoft /proc/version 2>/dev/null; then
            echo "wsl"
        else
            echo "linux"
        fi
    else
        echo "unknown"
    fi
}

# Check dependencies
check_dependencies() {
    print_info "Checking dependencies..."

    local missing=()

    # Required
    command -v python3 >/dev/null 2>&1 || missing+=("python3")
    command -v git >/dev/null 2>&1 || missing+=("git")

    # Optional but recommended
    if ! command -v sqlite3 >/dev/null 2>&1; then
        print_warning "sqlite3 not found (optional but recommended)"
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        print_error "Missing required dependencies: ${missing[*]}"
        echo ""
        echo "Install instructions:"

        OS=$(detect_os)
        case "$OS" in
            macos)
                echo "  brew install python3 git sqlite"
                ;;
            linux|wsl)
                echo "  sudo apt-get install python3 python3-pip git sqlite3"
                ;;
        esac

        exit 1
    fi

    print_success "All required dependencies found"
}

# Install system
install_system() {
    INSTALL_DIR="$HOME/ai-cli-memory-system"

    print_info "Installing to $INSTALL_DIR..."

    # Create directory structure
    mkdir -p "$INSTALL_DIR"/{scripts,hooks,config,sql,docs}
    mkdir -p "$HOME/.claude/memory"
    mkdir -p "$HOME/.claude/hooks"

    # If running from cloned repo, copy files
    if [[ -f "./install.sh" ]] && [[ -d "./scripts" ]]; then
        print_info "Installing from local repository..."

        cp -r scripts/* "$INSTALL_DIR/scripts/"
        cp -r hooks/* "$INSTALL_DIR/hooks/"
        cp -r config/* "$INSTALL_DIR/config/"
        cp -r sql/* "$INSTALL_DIR/sql/"

        if [[ -f "README.md" ]]; then
            cp README.md "$INSTALL_DIR/"
        fi
    else
        # Clone from GitHub
        print_info "Cloning from GitHub..."

        if [[ -d "$INSTALL_DIR/.git" ]]; then
            print_info "Repository already exists, pulling latest..."
            cd "$INSTALL_DIR"
            git pull
        else
            git clone "$REPO_URL" "$INSTALL_DIR"
        fi
    fi

    # Make scripts executable
    chmod +x "$INSTALL_DIR/scripts/"*.py
    chmod +x "$INSTALL_DIR/hooks/"*.sh

    print_success "Files installed"

    # Initialize database
    print_info "Initializing database..."

    python3 "$INSTALL_DIR/scripts/memory_manager.py" stats &>/dev/null || true

    if [[ -f "$HOME/.claude/memory/context.db" ]]; then
        print_success "Database initialized"
    else
        print_error "Database initialization failed"
        exit 1
    fi
}

# Configure Claude Code
configure_claude() {
    print_info "Configuring Claude Code..."

    CLAUDE_SETTINGS="$HOME/.claude/settings.json"

    # Backup existing settings
    if [[ -f "$CLAUDE_SETTINGS" ]]; then
        cp "$CLAUDE_SETTINGS" "$CLAUDE_SETTINGS.backup.$(date +%s)"
        print_info "Backed up existing settings"
    fi

    # Create or update settings
    if [[ -f "$CLAUDE_SETTINGS" ]]; then
        # Update existing settings
        python3 -c "
import json
import sys

settings_file = '$CLAUDE_SETTINGS'

try:
    with open(settings_file, 'r') as f:
        settings = json.load(f)
except:
    settings = {}

# Add hooks
settings['hooks'] = {
    'pre-session': '$HOME/ai-cli-memory-system/hooks/unified_hooks.sh pre',
    'post-session': '$HOME/ai-cli-memory-system/hooks/unified_hooks.sh post'
}

with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)

print('✓ Claude Code configured')
"
    else
        # Create new settings file
        cat > "$CLAUDE_SETTINGS" << 'EOF'
{
  "hooks": {
    "pre-session": "$HOME/ai-cli-memory-system/hooks/unified_hooks.sh pre",
    "post-session": "$HOME/ai-cli-memory-system/hooks/unified_hooks.sh post"
  }
}
EOF
        # Expand $HOME
        sed -i.bak "s|\$HOME|$HOME|g" "$CLAUDE_SETTINGS"
        rm "$CLAUDE_SETTINGS.bak"
    fi

    print_success "Claude Code configured"
}

# Configure other CLI tools
configure_others() {
    print_info "Configuring other CLI tools..."

    # Codex (GitHub Copilot CLI)
    if command -v gh >/dev/null 2>&1; then
        # Add environment variable to .zshrc or .bashrc
        SHELL_RC=""
        if [[ -f "$HOME/.zshrc" ]]; then
            SHELL_RC="$HOME/.zshrc"
        elif [[ -f "$HOME/.bashrc" ]]; then
            SHELL_RC="$HOME/.bashrc"
        fi

        if [[ -n "$SHELL_RC" ]]; then
            if ! grep -q "AI_CLI_MEMORY" "$SHELL_RC"; then
                cat >> "$SHELL_RC" << 'EOF'

# AI CLI Memory System
export AI_CLI_MEMORY="$HOME/.claude/memory/context.db"
export AI_HOOKS_DIR="$HOME/ai-cli-memory-system/hooks"

# Auto-update check on shell start (async)
if [[ -f "$HOME/ai-cli-memory-system/scripts/auto_updater.py" ]]; then
    python3 "$HOME/ai-cli-memory-system/scripts/auto_updater.py" check claude codex gemini aider &> /dev/null &
fi
EOF
                print_success "Shell configuration updated"
            fi
        fi
    fi

    print_success "Other tools configured"
}

# Run tests
run_tests() {
    print_info "Running tests..."

    # Test memory manager
    if python3 "$HOME/ai-cli-memory-system/scripts/memory_manager.py" stats &>/dev/null; then
        print_success "Memory manager test passed"
    else
        print_warning "Memory manager test failed"
    fi

    # Test auto-updater
    if python3 "$HOME/ai-cli-memory-system/scripts/auto_updater.py" status &>/dev/null; then
        print_success "Auto-updater test passed"
    else
        print_warning "Auto-updater test failed"
    fi

    # Test hooks
    if bash "$HOME/ai-cli-memory-system/hooks/unified_hooks.sh" pre &>/dev/null; then
        print_success "Hooks test passed"
    else
        print_warning "Hooks test failed"
    fi
}

# Print next steps
print_next_steps() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}║              Installation Complete! 🎉                     ║${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo ""
    echo "1. Restart your terminal or run:"
    echo "   source ~/.zshrc  # or ~/.bashrc"
    echo ""
    echo "2. Start using any AI CLI tool:"
    echo "   claude"
    echo ""
    echo "3. Check memory stats:"
    echo "   python3 ~/ai-cli-memory-system/scripts/memory_manager.py stats"
    echo ""
    echo "4. Check for updates:"
    echo "   python3 ~/ai-cli-memory-system/scripts/auto_updater.py check"
    echo ""
    echo -e "${BLUE}Features:${NC}"
    echo "  ✓ Contextual memory across all sessions"
    echo "  ✓ Automatic session tracking"
    echo "  ✓ Weekly summaries"
    echo "  ✓ Auto-update checks for all CLI tools"
    echo "  ✓ Project-specific patterns and preferences"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "  $HOME/ai-cli-memory-system/README.md"
    echo ""
}

# Main installation flow
main() {
    print_header

    OS=$(detect_os)
    print_info "Detected OS: $OS"
    echo ""

    check_dependencies
    echo ""

    install_system
    echo ""

    configure_claude
    echo ""

    configure_others
    echo ""

    run_tests
    echo ""

    print_next_steps
}

# Handle interrupts
trap 'echo ""; print_error "Installation interrupted"; exit 1' INT TERM

# Run installer
main "$@"
