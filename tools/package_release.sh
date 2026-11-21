#!/usr/bin/env bash
# Chỉ đóng gói HEAD đã commit. Không commit dist/ hoặc dùng zip thử làm gói phát hành.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if [[ -n "$(git ls-files -- dist/)" ]]; then
    echo 'Lỗi: dist/ có file được git theo dõi; không commit dist/.' >&2
    exit 1
fi

mkdir -p dist
archive_path="$repo_root/dist/cho-noi-v1.0.0.zip"
git archive --format=zip --prefix=cho-noi-v1.0.0/ HEAD --output="$archive_path"
printf 'Gói: %s\n' "$archive_path"
if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$archive_path"
else
    shasum -a 256 "$archive_path"
fi
printf 'Chỉ gồm file đã commit tại HEAD; không commit dist/.\n'
