#!/usr/bin/env bash
set -euo pipefail

# Parity test: generates projects from both copier-py and cookiecutter-py,
# compares the output, and produces a detailed report of all differences.
#
# Usage:
#   ./scripts/parity-test.sh [options]
#
# Options:
#   --copier-ref REF        Git ref (tag/branch/sha) for copier-py (default: local working tree)
#   --cookiecutter-ref REF  Git ref (tag/branch/sha) for cookiecutter-py (default: latest remote HEAD)
#   --output-dir DIR        Output directory (default: /tmp/copier-py-parity-test)
#   --help                  Show this help message
#
# Examples:
#   ./scripts/parity-test.sh
#   ./scripts/parity-test.sh --copier-ref v1.0.0 --cookiecutter-ref v2.3.0
#   ./scripts/parity-test.sh --copier-ref HEAD --cookiecutter-ref abc1234
#   ./scripts/parity-test.sh --output-dir /tmp/my-test

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COPIER_TEMPLATE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# --- Defaults ---
OUTPUT_DIR="/tmp/copier-py-parity-test"
COPIER_REF=""
COOKIECUTTER_REF=""
COOKIECUTTER_REPO="gh:ryankanno/cookiecutter-py"

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --copier-ref)
            COPIER_REF="$2"
            shift 2
            ;;
        --cookiecutter-ref)
            COOKIECUTTER_REF="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --help)
            head -17 "$0" | tail -15
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Run with --help for usage." >&2
            exit 1
            ;;
    esac
done

REPORT_FILE="${OUTPUT_DIR}/parity-report.txt"
COPIER_OUT="${OUTPUT_DIR}/copier-out"
COOKIECUTTER_OUT="${OUTPUT_DIR}/cookiecutter-out"

# --- Resolve copier source ---
# If a ref is given, we need to point copier at the repo URL with that ref.
# If no ref, use the local working tree.
if [ -n "${COPIER_REF}" ]; then
    COPIER_SOURCE="${COPIER_TEMPLATE_DIR}"
    COPIER_VCS_REF_ARG="--vcs-ref=${COPIER_REF}"
    COPIER_LABEL="copier-py @ ${COPIER_REF}"
else
    COPIER_SOURCE="${COPIER_TEMPLATE_DIR}"
    COPIER_VCS_REF_ARG="--vcs-ref=HEAD"
    COPIER_LABEL="copier-py @ local working tree (HEAD)"
fi

# --- Resolve cookiecutter source ---
if [ -n "${COOKIECUTTER_REF}" ]; then
    COOKIECUTTER_CHECKOUT="${COOKIECUTTER_REF}"
    COOKIECUTTER_LABEL="cookiecutter-py @ ${COOKIECUTTER_REF}"
else
    COOKIECUTTER_CHECKOUT=""
    COOKIECUTTER_LABEL="cookiecutter-py @ latest"
fi

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

section() {
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
}

# Clean up
rm -rf "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}"

# --- Generate projects ---

section "Generating copier-py project (${COPIER_LABEL})"
uvx copier copy --trust --defaults \
    ${COPIER_VCS_REF_ARG} \
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
    "${COPIER_SOURCE}" "${COPIER_OUT}"

section "Generating cookiecutter-py project (${COOKIECUTTER_LABEL})"
CRUFT_ARGS=(
    --no-input
    --output-dir "${COOKIECUTTER_OUT}"
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
        \"should_use_direnv\": \"y\",
        \"should_create_author_files\": \"y\",
        \"should_install_github_dependabot\": \"y\",
        \"should_automerge_autoapprove_github_dependabot\": \"y\",
        \"should_install_github_actions\": \"y\",
        \"should_upload_coverage_to_codecov\": \"n\",
        \"should_publish_to_testpypi\": \"y\",
        \"should_publish_to_pypi\": \"y\",
        \"should_publish_to_github_packages\": \"n\",
        \"should_attach_to_github_release\": \"n\"
    }"
)

if [ -n "${COOKIECUTTER_CHECKOUT}" ]; then
    CRUFT_ARGS+=(--checkout "${COOKIECUTTER_CHECKOUT}")
fi

uv run --with cruft cruft create "${CRUFT_ARGS[@]}" \
    https://github.com/ryankanno/cookiecutter-py

COOKIECUTTER_PROJECT="${COOKIECUTTER_OUT}/${PACKAGE_NAME}"

# --- Generate report ---

section "Parity Report"

{
    echo "Parity Test Report"
    echo "Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo ""
    echo "Left:  ${COPIER_LABEL}"
    echo "Right: ${COOKIECUTTER_LABEL}"
    echo ""

    # --- 1. File inventory ---
    echo "─── File Inventory ───"
    echo ""

    COPIER_FILES=$(cd "${COPIER_OUT}" && find . -type f ! -path './.git/*' | sort)
    COOKIECUTTER_FILES=$(cd "${COOKIECUTTER_PROJECT}" && find . -type f ! -path './.git/*' | sort)

    COPIER_ONLY=$(comm -23 <(echo "${COPIER_FILES}") <(echo "${COOKIECUTTER_FILES}"))
    COOKIECUTTER_ONLY=$(comm -13 <(echo "${COPIER_FILES}") <(echo "${COOKIECUTTER_FILES}"))
    COMMON_FILES=$(comm -12 <(echo "${COPIER_FILES}") <(echo "${COOKIECUTTER_FILES}"))

    COPIER_COUNT=$(echo "${COPIER_FILES}" | wc -l | tr -d ' ')
    COOKIECUTTER_COUNT=$(echo "${COOKIECUTTER_FILES}" | wc -l | tr -d ' ')
    COMMON_COUNT=$(echo "${COMMON_FILES}" | wc -l | tr -d ' ')

    echo "copier-py files:       ${COPIER_COUNT}"
    echo "cookiecutter-py files: ${COOKIECUTTER_COUNT}"
    echo "common files:          ${COMMON_COUNT}"
    echo ""

    if [ -n "${COPIER_ONLY}" ]; then
        echo "Files only in copier-py:"
        echo "${COPIER_ONLY}" | sed 's/^/  /'
        echo ""
    fi

    if [ -n "${COOKIECUTTER_ONLY}" ]; then
        echo "Files only in cookiecutter-py:"
        echo "${COOKIECUTTER_ONLY}" | sed 's/^/  /'
        echo ""
    fi

    # --- 2. Content differences ---
    echo "─── Content Differences ───"
    echo ""

    DIFF_COUNT=0
    IDENTICAL_COUNT=0
    WHITESPACE_ONLY_COUNT=0
    WHITESPACE_ONLY_FILES=""

    while IFS= read -r file; do
        file_diff=$(diff -u "${COPIER_OUT}/${file}" "${COOKIECUTTER_PROJECT}/${file}" \
            --label "copier-py:${file}" --label "cookiecutter-py:${file}" 2>/dev/null || true)

        if [ -z "${file_diff}" ]; then
            IDENTICAL_COUNT=$((IDENTICAL_COUNT + 1))
            continue
        fi

        # Check if the diff is whitespace/line-ending only
        ws_diff=$(diff -u --ignore-all-space --ignore-blank-lines \
            "${COPIER_OUT}/${file}" "${COOKIECUTTER_PROJECT}/${file}" 2>/dev/null || true)

        if [ -z "${ws_diff}" ]; then
            WHITESPACE_ONLY_COUNT=$((WHITESPACE_ONLY_COUNT + 1))
            WHITESPACE_ONLY_FILES="${WHITESPACE_ONLY_FILES}  ${file}\n"
            continue
        fi

        DIFF_COUNT=$((DIFF_COUNT + 1))
        echo "--- ${file} ---"
        echo "${file_diff}" | sed 's/^/  /'
        echo ""
    done <<< "${COMMON_FILES}"

    if [ "${DIFF_COUNT}" -eq 0 ]; then
        echo "(no content differences in common files)"
        echo ""
    fi

    if [ "${WHITESPACE_ONLY_COUNT}" -gt 0 ]; then
        echo "Whitespace/line-ending only differences (${WHITESPACE_ONLY_COUNT} files):"
        echo -e "${WHITESPACE_ONLY_FILES}"
    fi

    # --- 3. Summary ---
    echo "─── Summary ───"
    echo ""
    echo "Identical files:       ${IDENTICAL_COUNT}"
    echo "Files with diffs:      ${DIFF_COUNT}"
    echo "Whitespace-only diffs: ${WHITESPACE_ONLY_COUNT}"

    COPIER_ONLY_COUNT=0
    COOKIECUTTER_ONLY_COUNT=0
    if [ -n "${COPIER_ONLY}" ]; then
        COPIER_ONLY_COUNT=$(echo "${COPIER_ONLY}" | wc -l | tr -d ' ')
    fi
    if [ -n "${COOKIECUTTER_ONLY}" ]; then
        COOKIECUTTER_ONLY_COUNT=$(echo "${COOKIECUTTER_ONLY}" | wc -l | tr -d ' ')
    fi

    echo "Only in copier-py:     ${COPIER_ONLY_COUNT}"
    echo "Only in cookiecutter:  ${COOKIECUTTER_ONLY_COUNT}"
    echo ""

    TOTAL_DIFFS=$((DIFF_COUNT + COPIER_ONLY_COUNT + COOKIECUTTER_ONLY_COUNT))
    if [ "${TOTAL_DIFFS}" -eq 0 ] && [ "${WHITESPACE_ONLY_COUNT}" -eq 0 ]; then
        echo "RESULT: IDENTICAL"
    elif [ "${TOTAL_DIFFS}" -eq 0 ]; then
        echo "RESULT: IDENTICAL (ignoring ${WHITESPACE_ONLY_COUNT} whitespace-only difference(s))"
    else
        echo "RESULT: ${TOTAL_DIFFS} difference(s) found (+${WHITESPACE_ONLY_COUNT} whitespace-only)"
    fi

    echo ""
    echo "Generated output preserved at:"
    echo "  copier-py:       ${COPIER_OUT}"
    echo "  cookiecutter-py: ${COOKIECUTTER_PROJECT}"
    echo "  report:          ${REPORT_FILE}"

} | tee "${REPORT_FILE}"
