# Publishing Guide

This guide covers the complete publishing process for the oasis-rofl-client-py-rube package.

## Automatic Versioning

This package uses **dynamic versioning** from git tags. The version is automatically determined:
- **Tagged releases**: `v1.0.0` → Version `1.0.0`
- **Development builds**: Between tags → Version like `1.0.1.dev5+g2345678`

No need to manually update version numbers!

## Automated Publishing with GitHub Actions

This project includes a GitHub Actions workflow that **automatically publishes** to PyPI when you create a new release!

### How It Works

1. **Push a tag** starting with `v`:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **GitHub Actions automatically**:
   - Builds the package with the version from your tag
   - Publishes to TestPyPI (for all tags)
   - Publishes to PyPI (for releases)

### Setup Required

Configure Trusted Publishing (Recommended):

#### For TestPyPI
1. Go to [test.pypi.org](https://test.pypi.org) → Account settings → Publishing
2. Click "Add a new pending publisher"
3. Fill in:
   - **Repository owner**: rube-de
   - **Repository name**: oasis-rofl-client-py
   - **Workflow name**: `publish.yml`
   - **Environment**: `testpypi`
4. Click "Add"

#### For PyPI
1. Go to [PyPI.org](https://pypi.org) → Account settings → Publishing
2. Click "Add a new pending publisher"
3. Fill in:
   - **Repository owner**: rube-de
   - **Repository name**: oasis-rofl-client-py
   - **Workflow name**: `publish.yml`
   - **Environment**: `pypi`
4. Click "Add"

## Manual Publishing with uv

### Building the Package

To build the package, run:

```bash
uv build
```

This will create distribution files in the `dist/` directory:
- Source distribution (`.tar.gz`)
- Wheel distribution (`.whl`)

### Publish to TestPyPI

```bash
# Set the TestPyPI URL
export UV_PUBLISH_URL="https://test.pypi.org/legacy/"

# Publish with API token
export UV_PUBLISH_TOKEN="pypi-YOUR_TOKEN_HERE"
uv publish
```

### Publish to PyPI

```bash
# Using API token
export UV_PUBLISH_TOKEN="pypi-YOUR_TOKEN_HERE"
uv publish
```

**Note**: Create API tokens at:
- TestPyPI: [test.pypi.org](https://test.pypi.org/manage/account/#api-tokens)
- PyPI: [pypi.org](https://pypi.org/manage/account/#api-tokens)

## Testing the Uploaded Package

To test your uploaded package from TestPyPI:

```bash
# Create a test environment
uv venv test-env
source test-env/bin/activate  # Windows: test-env\Scripts\activate

# Install from TestPyPI
uv pip install --index-url https://test.pypi.org/simple/ \
               --extra-index-url https://pypi.org/simple/ \
               oasis-rofl-client-py-rube

# Test the package
uv run python -c "from oasis_rofl_client import Client; print(Client().ping())"
```

## Releasing a New Version

### Automated Release (Recommended)

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

2. **Create and push a version tag**:
   ```bash
   git tag v1.0.0
   git push origin main --tags
   ```

3. **GitHub Actions handles the rest**:
   - Automatically builds with version `1.0.0`
   - Publishes to TestPyPI
   - To publish to PyPI: Go to GitHub → Releases → "Draft a new release" → Choose tag `v1.0.0` → Publish release

### Manual Release

If you prefer manual control:

1. **Tag your release**:
   ```bash
   git tag v1.0.0
   ```

2. **Build the package** (version comes from tag):
   ```bash
   uv build
   ```

3. **Upload to PyPI**:
   ```bash
   # With token as environment variable
   export UV_PUBLISH_TOKEN="pypi-YOUR_TOKEN_HERE"
   uv publish
   ```

**Note**: Each version can only be uploaded once. The version is automatically set from your git tag - no manual editing needed!

## Important Notes

- You CANNOT delete or overwrite PyPI releases
- Use post-releases for hotfixes: `v1.0.0.post1`
- Always use trusted publishing (no API tokens)
- Protect your main branch
- Test with TestPyPI first

Always verify on TestPyPI first:
```bash
uv pip install --index-url https://test.pypi.org/simple/ \
               --extra-index-url https://pypi.org/simple/ \
               oasis-rofl-client-py-rube
```