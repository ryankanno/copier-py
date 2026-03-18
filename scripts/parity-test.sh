#!/usr/bin/env bash
set -euo pipefail

# Parity test: generates projects from both copier-py and cookiecutter-py
# and diffs the output to verify they produce identical artifacts.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COPIER_TEMPLATE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

OUTPUT_DIR="${1:-/tmp/copier-py-parity-test}"

COPIER_OUT="${OUTPUT_DIR}/copier-out"
COOKIECUTTER_OUT="${OUTPUT_DIR}/cookiecutter-out"

# Shared template values
AUTHOR_NAME="Ryan Kanno"
AUTHOR_EMAIL="ryankanno@localkinegrinds.com"
PROJECT_NAME="Foobar"
PROJECT_SHORT_DESCRIPTION="A foobar project"
PROJECT_URL="https://github.com/ryankanno/foobar"
PROJECT_LICENSE="MIT"
GITHUB_REPOSITORY_OWNER="ryankanno"
PACKAGE_NAME="foobar"
VERSION="0.0.0"
PYTHON_VERSION="3.12"
SUPPORTED_PYTHON_VERSIONS="3.11, 3.12, 3.13, pypy3.11"
UV_VERSION="0.7.3"
TOX_VERSION="4.25.0"
SPHINX_THEME="furo"
SHOULD_USE_DIRENV="y"
SHOULD_CREATE_AUTHOR_FILES="y"
SHOULD_INSTALL_GITHUB_DEPENDABOT="y"
SHOULD_AUTOMERGE_AUTOAPPROVE_GITHUB_DEPENDABOT="y"
SHOULD_INSTALL_GITHUB_ACTIONS="y"
SHOULD_UPLOAD_COVERAGE_TO_CODECOV="n"
SHOULD_PUBLISH_TO_TESTPYPI="y"
SHOULD_PUBLISH_TO_PYPI="y"
SHOULD_PUBLISH_TO_GITHUB_PACKAGES="n"
SHOULD_ATTACH_TO_GITHUB_RELEASE="n"

# Clean up
rm -rf "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}"

echo "=== Generating copier-py project ==="
uvx copier copy --trust --defaults \
    --data "author_name=${AUTHOR_NAME}" \
    --data "author_email=${AUTHOR_EMAIL}" \
    --data "project_name=${PROJECT_NAME}" \
    --data "project_short_description=${PROJECT_SHORT_DESCRIPTION}" \
    --data "project_url=${PROJECT_URL}" \
    --data "project_license=${PROJECT_LICENSE}" \
    --data "github_repository_owner=${GITHUB_REPOSITORY_OWNER}" \
    --data "package_name=${PACKAGE_NAME}" \
    --data "version=${VERSION}" \
    --data "python_version=${PYTHON_VERSION}" \
    --data "supported_python_versions=${SUPPORTED_PYTHON_VERSIONS}" \
    --data "uv_version=${UV_VERSION}" \
    --data "tox_version=${TOX_VERSION}" \
    --data "sphinx_theme=${SPHINX_THEME}" \
    --data "should_use_direnv=true" \
    --data "should_create_author_files=true" \
    --data "should_install_github_dependabot=true" \
    --data "should_automerge_autoapprove_github_dependabot=true" \
    --data "should_install_github_actions=true" \
    --data "should_upload_coverage_to_codecov=false" \
    --data "should_publish_to_testpypi=true" \
    --data "should_publish_to_pypi=true" \
    --data "should_publish_to_github_packages=false" \
    --data "should_attach_to_github_release=false" \
    "${COPIER_TEMPLATE_DIR}" "${COPIER_OUT}"

echo ""
echo "=== Generating cookiecutter-py project ==="
uv run --with cruft cruft create --no-input \
    --output-dir "${COOKIECUTTER_OUT}" \
    --extra-context "{
        \"author_name\": \"${AUTHOR_NAME}\",
        \"author_email\": \"${AUTHOR_EMAIL}\",
        \"project_name\": \"${PROJECT_NAME}\",
        \"project_short_description\": \"${PROJECT_SHORT_DESCRIPTION}\",
        \"project_url\": \"${PROJECT_URL}\",
        \"project_license\": \"${PROJECT_LICENSE}\",
        \"github_repository_owner\": \"${GITHUB_REPOSITORY_OWNER}\",
        \"package_name\": \"${PACKAGE_NAME}\",
        \"version\": \"${VERSION}\",
        \"python_version\": \"${PYTHON_VERSION}\",
        \"supported_python_versions\": \"${SUPPORTED_PYTHON_VERSIONS}\",
        \"uv_version\": \"${UV_VERSION}\",
        \"tox_version\": \"${TOX_VERSION}\",
        \"sphinx_theme\": \"${SPHINX_THEME}\",
        \"should_use_direnv\": \"${SHOULD_USE_DIRENV}\",
        \"should_create_author_files\": \"${SHOULD_CREATE_AUTHOR_FILES}\",
        \"should_install_github_dependabot\": \"${SHOULD_INSTALL_GITHUB_DEPENDABOT}\",
        \"should_automerge_autoapprove_github_dependabot\": \"${SHOULD_AUTOMERGE_AUTOAPPROVE_GITHUB_DEPENDABOT}\",
        \"should_install_github_actions\": \"${SHOULD_INSTALL_GITHUB_ACTIONS}\",
        \"should_upload_coverage_to_codecov\": \"${SHOULD_UPLOAD_COVERAGE_TO_CODECOV}\",
        \"should_publish_to_testpypi\": \"${SHOULD_PUBLISH_TO_TESTPYPI}\",
        \"should_publish_to_pypi\": \"${SHOULD_PUBLISH_TO_PYPI}\",
        \"should_publish_to_github_packages\": \"${SHOULD_PUBLISH_TO_GITHUB_PACKAGES}\",
        \"should_attach_to_github_release\": \"${SHOULD_ATTACH_TO_GITHUB_RELEASE}\"
    }" \
    https://github.com/ryankanno/cookiecutter-py

echo ""
echo "=== Diffing output ==="
echo ""

# cookiecutter nests output in a package_name directory
DIFF_OUTPUT=$(diff -rq "${COPIER_OUT}" "${COOKIECUTTER_OUT}/${PACKAGE_NAME}" \
    --exclude='.git' \
    --exclude='.cruft.json' \
    --exclude='.copier-answers.yml' \
    2>&1 || true)

if [ -z "${DIFF_OUTPUT}" ]; then
    echo "PASS: No differences found."
elif [ "${DIFF_OUTPUT}" = "Files ${COPIER_OUT}/.dockerignore and ${COOKIECUTTER_OUT}/${PACKAGE_NAME}/.dockerignore differ" ]; then
    echo "PASS: Only expected difference found (.copier-answers.yml vs .cruft.json in .dockerignore)"
    echo ""
    diff "${COPIER_OUT}/.dockerignore" "${COOKIECUTTER_OUT}/${PACKAGE_NAME}/.dockerignore"
else
    echo "FAIL: Unexpected differences found:"
    echo "${DIFF_OUTPUT}"
    echo ""
    echo "Detailed diffs:"
    diff -r "${COPIER_OUT}" "${COOKIECUTTER_OUT}/${PACKAGE_NAME}" \
        --exclude='.git' \
        --exclude='.cruft.json' \
        --exclude='.copier-answers.yml' \
        || true
    exit 1
fi
