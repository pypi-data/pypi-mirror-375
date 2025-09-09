#!/bin/bash
# Homebrew setup helper script for utilityman

set -e

VERSION="0.3.0"
PACKAGE_URL="https://github.com/stiles/utilityman/archive/refs/tags/v${VERSION}.tar.gz"

echo "🍺 Homebrew Setup Helper for utilityman"
echo "========================================"

# Get SHA256 for the package
echo "📦 Getting SHA256 for version ${VERSION}..."
SHA256=$(curl -sL "$PACKAGE_URL" | shasum -a 256 | cut -d' ' -f1)
echo "SHA256: $SHA256"

# Update the formula file
if [ -f "utilityman.rb" ]; then
    echo "🔧 Updating SHA256 in utilityman.rb..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed
        sed -i '' "s/NEEDS_ACTUAL_SHA256_FROM_GITHUB_RELEASE/$SHA256/g" utilityman.rb
    else
        # Linux sed
        sed -i "s/NEEDS_ACTUAL_SHA256_FROM_GITHUB_RELEASE/$SHA256/g" utilityman.rb
    fi
    echo "✅ Formula updated!"
else
    echo "❌ utilityman.rb not found. Run this script from the project root."
    exit 1
fi

echo ""
echo "🧪 Next steps:"
echo "1. Test the formula locally:"
echo "   brew audit --strict utilityman.rb"
echo "   brew install --build-from-source utilityman.rb"
echo "   brew test utilityman"
echo ""
echo "2. For personal tap, create homebrew-utilityman repo and copy Formula/utilityman.rb"
echo "3. For Homebrew Core, follow the submission guide in HOMEBREW.md"
echo ""
echo "📝 Formula ready with SHA256: $SHA256"
