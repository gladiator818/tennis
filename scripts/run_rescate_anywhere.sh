#!/usr/bin/env bash
set -euo pipefail

find_repo_dir() {
  # 1) If current dir is already repo root
  if [ -f "pyproject.toml" ] && [ -f "README.md" ] && [ -d "src/tennis_analytics" ]; then
    pwd
    return 0
  fi

  # 2) If we are inside the repo, walk up parents
  local d
  d="$(pwd)"
  while [ "$d" != "/" ]; do
    if [ -f "$d/pyproject.toml" ] && [ -f "$d/README.md" ] && [ -d "$d/src/tennis_analytics" ]; then
      echo "$d"
      return 0
    fi
    d="$(dirname "$d")"
  done

  # 3) Search common user directories for a folder named tennis with this project signature
  local base
  for base in "$HOME" "$HOME/Desktop" "$HOME/Documents"; do
    [ -d "$base" ] || continue
    local hit
    hit="$(find "$base" -maxdepth 4 -type f -name pyproject.toml 2>/dev/null | sed 's|/pyproject.toml$||' | while read -r candidate; do
      if [ -f "$candidate/README.md" ] && [ -d "$candidate/src/tennis_analytics" ]; then
        echo "$candidate"
        break
      fi
    done)"
    if [ -n "$hit" ]; then
      echo "$hit"
      return 0
    fi
  done

  return 1
}

REPO_DIR="$(find_repo_dir || true)"

if [ -z "$REPO_DIR" ]; then
  echo "❌ No encuentro el repositorio 'tennis' en este Mac." >&2
  echo "" >&2
  echo "Haz esto:" >&2
  echo "1) Descarga o clona el proyecto." >&2
  echo "2) Entra a la carpeta donde esté README.md y src/tennis_analytics." >&2
  echo "3) Vuelve a ejecutar: bash scripts/run_rescate_anywhere.sh" >&2
  exit 1
fi

echo "✅ Repo encontrado en: $REPO_DIR"
cd "$REPO_DIR"

if [ ! -f "scripts/quickstart_rescate.sh" ]; then
  echo "❌ Falta scripts/quickstart_rescate.sh dentro del repo." >&2
  exit 1
fi

bash scripts/quickstart_rescate.sh
