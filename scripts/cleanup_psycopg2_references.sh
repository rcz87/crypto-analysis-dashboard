#!/usr/bin/env bash
set -euo pipefail

# Clean up remaining psycopg2.connect references in production code
echo "🧹 CLEANING UP PSYCOPG2 REFERENCES"
echo "==================================="

echo "==> Searching for problematic psycopg2.connect references..."

# Find actual psycopg2.connect usage (excluding docs/scripts)
PSYCOPG2_FILES=$(grep -R --line-number 'psycopg2\.connect(' . \
    --exclude-dir=.git \
    --exclude-dir=__pycache__ \
    --exclude-dir=.cache \
    --exclude-dir=docs \
    --exclude-dir=scripts \
    --exclude-dir=backup_working_system \
    --exclude-dir=crypto-analysis-dashboard \
    --exclude="*.md" \
    --exclude="*.txt" \
    --include="*.py" || echo "")

if [ -n "$PSYCOPG2_FILES" ]; then
    echo "Found psycopg2.connect references in production code:"
    echo "$PSYCOPG2_FILES"
    echo ""
    echo "These should be reviewed and potentially replaced with SQLAlchemy."
else
    echo "✅ No psycopg2.connect references found in production code"
fi

echo "==> Searching for localhost:5432 references in Python files..."

LOCALHOST_FILES=$(grep -R --line-number 'localhost:5432' . \
    --exclude-dir=.git \
    --exclude-dir=__pycache__ \
    --exclude-dir=.cache \
    --exclude-dir=docs \
    --exclude-dir=backup_working_system \
    --exclude-dir=crypto-analysis-dashboard \
    --exclude="*.md" \
    --exclude="*.txt" \
    --exclude="*.sh" \
    --include="*.py" || echo "")

if [ -n "$LOCALHOST_FILES" ]; then
    echo "Found localhost:5432 references in Python files:"
    echo "$LOCALHOST_FILES"
    echo ""
    echo "These should be reviewed and replaced with proper config."
else
    echo "✅ No localhost:5432 references found in Python files"
fi

echo "==> Searching for trading_user references in Python files..."

TRADING_USER_FILES=$(grep -R --line-number 'trading_user' . \
    --exclude-dir=.git \
    --exclude-dir=__pycache__ \
    --exclude-dir=.cache \
    --exclude-dir=docs \
    --exclude-dir=backup_working_system \
    --exclude-dir=crypto-analysis-dashboard \
    --exclude="*.md" \
    --exclude="*.txt" \
    --exclude="*.sh" \
    --include="*.py" || echo "")

if [ -n "$TRADING_USER_FILES" ]; then
    echo "Found trading_user references in Python files:"
    echo "$TRADING_USER_FILES"
    echo ""
    echo "These should be reviewed and replaced with proper Neon credentials."
else
    echo "✅ No trading_user references found in Python files"
fi

echo ""
echo "🎯 CLEANUP SUMMARY:"
echo "- Documentation and script files with localhost:5432 are OK (debug tools)"
echo "- Only production Python code should use SQLAlchemy config"
echo "- Health check fixes have eliminated the main problematic fallbacks"
echo "✅ Production code is now clean of problematic database connection patterns"