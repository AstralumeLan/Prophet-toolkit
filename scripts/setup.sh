#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
with_tianji=()
run_tests=true
for arg in "$@"; do
    case "$arg" in
        --with-tianji) with_tianji=(--with-tianji) ;;
        --no-tests) run_tests=false ;;
        *) echo "Unknown option: $arg" >&2; exit 2 ;;
    esac
done
if [[ ! -x .venv/bin/python ]]; then
    if command -v uv >/dev/null 2>&1; then uv venv .venv; else python3 -m venv .venv; fi
fi
if command -v uv >/dev/null 2>&1; then
    uv pip install --python .venv/bin/python -r requirements.txt
else
    .venv/bin/python -m pip install -r requirements.txt
fi
(cd eastern/ziwei/js && npm ci)
mkdir -p vendor western/data
fetch_repo() {
    local name="$1" url="$2" revision="$3"
    if [[ ! -d "vendor/$name/.git" ]]; then git clone "$url" "vendor/$name"; fi
    if ! git -C "vendor/$name" cat-file -e "$revision^{commit}" 2>/dev/null; then
        git -C "vendor/$name" fetch origin "$revision"
    fi
    if [[ -n "$(git -C "vendor/$name" status --porcelain)" ]]; then
        echo "Refusing to overwrite modified vendor/$name" >&2; exit 1
    fi
    git -C "vendor/$name" checkout --detach "$revision"
}
fetch_repo chinese-fortune https://github.com/ShousenZHANG/chinese-fortune.git 81a980a5707505468a10f596f1f19c9088457a9e
fetch_repo dashaflow https://github.com/adarshj322/dashaflow.git f8f8ead76e56b9048f80adbbbff282c007068cf7
fetch_repo ziwei-doushu https://github.com/Renhuai123/ziwei-doushu.git 495b79ecb3524b20b2edc026067d7d0b0f407319
if [[ ! -s western/data/seas_18.se1 ]]; then
    echo 'Swiss Ephemeris data: AGPL/commercial dual licence; see THIRD_PARTY_NOTICES.md.'
    tmp_ephe="$(mktemp western/data/seas_18.se1.XXXXXX)"
    trap 'rm -f "$tmp_ephe"' EXIT
    curl --fail --location --retry 3 https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/seas_18.se1 -o "$tmp_ephe"
    mv "$tmp_ephe" western/data/seas_18.se1
    trap - EXIT
fi
bin/prophet corpus build "${with_tianji[@]}"
if "$run_tests"; then bin/prophet selftest; fi
