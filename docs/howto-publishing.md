# How to Set Up Publishing to PyPI

This guide covers configuring your generated project to publish packages to PyPI, TestPyPI, GitHub Packages, and GitHub Releases.

## Enable publishing during generation

When running `copier copy`, answer `yes` to the publishing questions:

```
🎤 Publish to TestPyPI?
   Yes
🎤 Publish to PyPI?
   Yes
🎤 Publish to GitHub Packages?
   Yes
🎤 Attach artifacts to GitHub release?
   Yes
```

If you already generated your project, you can re-run copier to enable publishing — see below.

## Configure PyPI trusted publishing

The generated publish workflow uses [trusted publishing](https://docs.pypi.org/trusted-publishers/) (OpenID Connect) — no API tokens needed.

### For PyPI

1. Go to [pypi.org](https://pypi.org) and create an account
2. Navigate to **Publishing** → **Add a new pending publisher**
3. Fill in:
   - **PyPI project name**: your package name (e.g., `my-awesome-project`)
   - **Owner**: your GitHub username or organization
   - **Repository name**: your GitHub repository name
   - **Workflow name**: `publish.yml`
   - **Environment name**: `publish_pypi`
4. Click **Add**

### For TestPyPI

1. Go to [test.pypi.org](https://test.pypi.org) and create an account
2. Navigate to **Publishing** → **Add a new pending publisher**
3. Fill in the same details but with:
   - **Environment name**: `publish_testpypi`
4. Click **Add**

## Configure GitHub environments

The publish workflow uses GitHub environments for deployment protection:

1. Go to your repository **Settings** → **Environments**
2. Create these environments as needed:
   - `publish_testpypi` — for TestPyPI publishing (triggered on push to main)
   - `publish_pypi` — for PyPI publishing (triggered on release)
   - `publish_github_packages` — for GitHub Packages (triggered on release)
   - `attach_to_github_release` — for release artifacts (triggered on release)
3. Optionally add required reviewers for production environments

## Trigger a publish

### TestPyPI (on every push to main)

TestPyPI publishing triggers automatically when you push to the `main` branch. Merge a PR or push directly:

```sh
git push origin main
```

### PyPI and GitHub Releases (on release)

1. Create a GitHub release using the release drafter:
   - Go to **Releases** → **Draft a new release**
   - The release drafter pre-populates notes from merged PRs
   - Choose a semantic version tag (e.g., `v1.0.0`)
   - Click **Publish release**
2. The publish workflow triggers automatically

## Re-run copier to enable publishing

If you generated your project without publishing enabled, re-run copier to add it:

```sh
copier update /path/to/your-project
```

Answer `yes` to the publishing questions you want to enable. Copier merges the new workflow configuration into your existing project.

## Verify the workflow

Check the **Actions** tab in your GitHub repository to monitor workflow runs. Each publishing destination runs as a separate job with its own environment protection.

The `build` job always runs regardless of publishing configuration — it builds the package and uploads artifacts to GitHub Actions for manual inspection.
