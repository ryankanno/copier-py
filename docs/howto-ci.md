# How to Configure CI with GitHub Actions

This guide covers customizing the GitHub Actions workflows that come with your generated project.

## Enable GitHub Actions during generation

When running `copier copy`, answer `yes` to the GitHub Actions question:

```
🎤 Install GitHub Actions workflows?
   Yes
```

This generates the following workflows in `.github/workflows/`:

- `ci.yml` — runs tests, linting, and type checking
- `publish.yml` — builds and publishes packages
- `codeql.yml` — CodeQL security analysis
- `hadolint.yml` — Dockerfile linting
- `commitlint.yml` — commit message validation
- `trufflehog.yml` — secret scanning
- `docs.yml` — documentation publishing
- `release-drafter.yml` — automated release notes
- `pr-size-labeling.yml` — PR size classification
- `pr-labeler.yml` — automated PR labeling

## Enable Codecov integration

To upload test coverage to [Codecov](https://codecov.io):

1. Answer `yes` to "Upload coverage to Codecov?" during generation
2. Sign up at [codecov.io](https://codecov.io) and add your repository
3. For public repositories, no token is needed
4. For private repositories, add your Codecov token as a repository secret named `CODECOV_TOKEN`

## Configure Dependabot auto-merge

To auto-approve and auto-merge Dependabot PRs:

1. Answer `yes` to both:
   - "Install GitHub Dependabot configuration?"
   - "Auto-approve and auto-merge Dependabot PRs?"
2. Create version tags for PR classification:
   ```sh
   git tag major && git push origin major
   git tag minor && git push origin minor
   git tag patch && git push origin patch
   ```
3. The workflow auto-merges `minor` and `patch` updates but blocks `major` version bumps for manual review

## Customize the CI matrix

The CI workflow tests across the Python versions you specified during generation. To change the matrix, edit `.github/workflows/ci.yml`:

```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12", "3.13"]
```

Update `tox.ini` and `pyproject.toml` to match if you add or remove Python versions.

## Add repository secrets

Some workflows require secrets. Add them in **Settings** → **Secrets and variables** → **Actions**:

| Secret | Used by | Required when |
|--------|---------|---------------|
| `CODECOV_TOKEN` | CI workflow | Private repos with Codecov |
| `PAT` | Auto-approve workflow | Dependabot auto-merge enabled |

## Publish documentation to GitHub Pages

The `docs` workflow publishes each version to `<owner>.github.io/<repo>/<version>/`. It creates the `gh-pages` branch on the first deploy.

Before the first push to `main`:

1. Go to **Settings** → **Pages** and set **Source** to **GitHub Actions**. Without this setting, the deploy job fails.
2. Go to **Settings** → **Environments** → **github-pages**. If it is not listed, select **New environment** and name it `github-pages`. Under **Deployment branches and tags**, add a tag rule that matches your release tags, such as `v*`. Without this rule, GitHub rejects deploys from releases. Make sure the rules also allow `main`, because a new environment has no branch rule.

A push to `main` publishes to `latest`. A release publishes to a directory named after its tag. The version selector lists `latest` and tags such as `1.2.3` or `v1.2.3`. Pull request runs build the docs and skip the deploy job.

To backfill a released version, run the workflow manually with **Run workflow**:

- `ref`: the branch, tag, or SHA to build. The default is the branch that you run the workflow from.
- `version`: the destination directory, such as `v1.2.3`. Set it for a backfill, because the default is `latest`.

The deploy accepts only `latest` or a version such as `1.2.3`, `v1.2.3`, or `v1.2.3-rc1`. This applies to release tags too, so a release tagged `1.2` fails its docs deploy.

A run from a tag or from a branch other than the default also needs an allowed rule in the `github-pages` environment.

## Monitor workflow runs

Check the **Actions** tab in your GitHub repository. Each workflow runs on its configured trigger:

- **CI**: runs on every push and pull request
- **CodeQL**: runs on push to main and on a weekly schedule
- **Publish**: runs on push to main (TestPyPI) and on release (PyPI)
- **Docs**: runs on push to main, on pull requests, on release, and on manual dispatch
