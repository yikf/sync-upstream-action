#!/bin/bash
# Code style check and fix script using Ruff
set -e

show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  check    Run code style checks"
    echo "  fix      Auto-fix issues and format code"
    echo "  help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 check    # Check code style"
    echo "  $0 fix      # Auto-fix and format"
}

case "${1:-}" in
    check)
        echo "🚀 Running Ruff code style checks..."
        uv run ruff check .
        echo "✅ All checks passed!"
        ;;
    fix)
        echo "🔧 Running Ruff auto-fixes..."
        uv run ruff check --fix .
        echo "✨ Running Ruff formatting..."
        uv run ruff format .
        echo "✅ Fixes and formatting complete!"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Error: Invalid command"
        echo ""
        show_help
        exit 1
        ;;
esac
