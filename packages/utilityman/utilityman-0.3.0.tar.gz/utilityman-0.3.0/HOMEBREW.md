# Homebrew Distribution Guide

This guide covers how to distribute `utilityman` via Homebrew, both through a personal tap and potentially through Homebrew Core.

## Quick Start for Users

Once set up, users will be able to install with:
```bash
# From personal tap (recommended first step)
brew tap stiles/utilityman
brew install utilityman

# Or from Homebrew Core (if accepted)
brew install utilityman
```

## Option 1: Personal Tap (Recommended Start)

### Step 1: Create the Tap Repository

1. Create a new GitHub repository named `homebrew-utilityman`
2. Clone it locally:
   ```bash
   git clone https://github.com/stiles/homebrew-utilityman.git
   cd homebrew-utilityman
   ```

3. Create the formula directory structure:
   ```bash
   mkdir Formula
   ```

### Step 2: Create a GitHub Release and Get SHA256

First, create a GitHub release:
1. Go to https://github.com/stiles/utilityman/releases
2. Click "Create a new release"
3. Tag version: `v0.3.0`
4. Release title: `v0.3.0`
5. Describe the release features
6. Publish the release

Then get the SHA256:
```bash
# Download the release tarball and get its SHA256
curl -L https://github.com/stiles/utilityman/archive/refs/tags/v0.3.0.tar.gz | shasum -a 256
```

### Step 3: Update the Formula

Copy `utilityman.rb` to `Formula/utilityman.rb` in your tap repository and update the SHA256:

```ruby
class Utilityman < Formula
  include Language::Python::Virtualenv

  desc "Follow any MLB game in your shell - live play-by-play terminal experience"
  homepage "https://github.com/stiles/utilityman"
  url "https://github.com/stiles/utilityman/archive/refs/tags/v0.3.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256_FROM_STEP_2"
  license "MIT"

  depends_on "python@3.11"

  resource "requests" do
    url "https://files.pythonhosted.org/packages/source/r/requests/requests-2.31.0.tar.gz"
    sha256 "942c5a758f98d790eaed1a29cb6eefc7ffb0d1cf7af05c3d2791656dbd6ad1e1"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "Stream MLB play-by-play", shell_output("#{bin}/utilityman --help")
  end
end
```

### Step 4: Test Locally

```bash
# Add your tap locally
brew tap stiles/utilityman /path/to/homebrew-utilityman

# Test the formula
brew audit --strict Formula/utilityman.rb
brew install --build-from-source utilityman
brew test utilityman

# Try running it
utilityman --help
```

### Step 5: Publish Your Tap

```bash
cd /path/to/homebrew-utilityman
git add Formula/utilityman.rb
git commit -m "Add utilityman formula"
git push origin main
```

Users can now install with:
```bash
brew tap stiles/utilityman
brew install utilityman
```

## Option 2: Homebrew Core Submission

### Prerequisites Check

Before submitting to Homebrew Core, verify:

- ✅ Open source with compatible license (MIT ✓)
- ✅ Stable tagged release (0.3.0 ✓)
- ✅ Useful, maintained software
- ✅ Not a duplicate of existing functionality
- ✅ Works on multiple macOS versions

### Submission Process

1. **Fork homebrew-core**:
   ```bash
   # Fork https://github.com/Homebrew/homebrew-core on GitHub
   git clone https://github.com/stiles/homebrew-core.git
   cd homebrew-core
   ```

2. **Create formula branch**:
   ```bash
   git checkout -b utilityman
   ```

3. **Add the formula**:
   ```bash
   cp /path/to/utilityman/utilityman.rb Formula/utilityman.rb
   ```

4. **Test thoroughly**:
   ```bash
   brew audit --strict --new-formula Formula/utilityman.rb
   brew install --build-from-source Formula/utilityman.rb
   brew test utilityman
   ```

5. **Commit and push**:
   ```bash
   git add Formula/utilityman.rb
   git commit -m "utilityman 0.3.0 (new formula)

   Follow MLB games live in your terminal with play-by-play updates,
   real-time scoring, and clean formatting."
   git push origin utilityman
   ```

6. **Create pull request** on GitHub with:
   - Title: `utilityman 0.3.0 (new formula)`
   - Description explaining what the tool does and why it's useful

## Updating the Formula

When you release a new version:

### For Personal Tap:
```bash
# 1. Create new GitHub release (v0.4.0)
# 2. Update version and SHA256 in Formula/utilityman.rb
# Get new SHA256:
curl -L https://github.com/stiles/utilityman/archive/refs/tags/v0.4.0.tar.gz | shasum -a 256

# 3. Update formula, commit and push
git add Formula/utilityman.rb
git commit -m "utilityman 0.4.0"
git push
```

### For Homebrew Core:
- Homebrew has automated version bump PRs for many packages
- You can also submit manual update PRs following the same process

## Testing Commands Reference

```bash
# Audit the formula for compliance
brew audit --strict Formula/utilityman.rb

# Install from source (tests build process)
brew install --build-from-source utilityman

# Run the test block
brew test utilityman

# Check for common issues
brew doctor

# Uninstall for clean testing
brew uninstall utilityman
```

## Troubleshooting

### Common Issues:

1. **SHA256 mismatch**: Download the exact tarball and recalculate
2. **Python version conflicts**: Homebrew prefers specific Python versions
3. **Test failures**: Ensure the test command works on a fresh install
4. **Dependency issues**: Use `resource` blocks for Python dependencies

### Getting Help:

- Homebrew Discussions: https://github.com/orgs/Homebrew/discussions
- Formula Cookbook: https://docs.brew.sh/Formula-Cookbook
- Style Guide: https://docs.brew.sh/Homebrew-Formulae-style-guide
