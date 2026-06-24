name: Stateful Dependency Update Guard

on:
  pull_request:
    paths:
      - "package.json"
      - "package-lock.json"
      - "pnpm-lock.yaml"
      - "yarn.lock"
      - "requirements*.txt"
      - "pyproject.toml"
      - "poetry.lock"
      - "Pipfile.lock"
      - ".github/workflows/**"

jobs:
  classify-dependency-update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Classify stateful package changes
        shell: bash
        run: |
          set -euo pipefail
          git fetch origin "${{ github.base_ref }}" --depth=1
          git diff --name-only "origin/${{ github.base_ref }}"...HEAD > changed-files.txt
          echo "Changed files:"
          cat changed-files.txt
          STATEFUL_PATTERN='sqlalchemy|django|redis|alembic|psycopg|pymongo|@prisma|prisma|typeorm|sequelize|mongoose|ioredis|express-session|next-auth|better-sqlite3|sqlite3|pg'
          if git diff "origin/${{ github.base_ref }}"...HEAD -- package.json package-lock.json pnpm-lock.yaml yarn.lock requirements*.txt pyproject.toml poetry.lock Pipfile.lock 2>/dev/null | grep -Eiq "$STATEFUL_PATTERN"; then
            echo "::warning::Stateful dependency update detected. Review persistence, migrations, sessions, caches, and rollback behavior before merge."
            echo "stateful_update=true" >> "$GITHUB_ENV"
          else
            echo "stateful_update=false" >> "$GITHUB_ENV"
          fi
      - name: Production gate summary
        shell: bash
        run: |
          echo "Stateful update: ${stateful_update:-false}"
          echo "Stateless updates may proceed after normal CI. Stateful updates require manual production review."
