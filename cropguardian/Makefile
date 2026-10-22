# Crop Guardian - Makefile (spec 19.7). Recipes use bash (Git Bash on Windows, sh on Linux/macOS).
SHELL := bash
PY ?= $(if $(wildcard backend/.venv/Scripts/python.exe),backend/.venv/Scripts/python.exe,$(if $(wildcard backend/.venv/bin/python),backend/.venv/bin/python,python3))
PHASE ?= $(shell cat .phase 2>/dev/null || echo 0)
COMPOSE := docker compose
TEST_COMPOSE := docker compose -f docker-compose.test.yml
export TEST_SUPER_DATABASE_URL ?= postgresql://postgres:test-only-password@127.0.0.1:55432/cropguardian
export TEST_API_DATABASE_URL ?= postgresql://cg_api:dev-api-pw@127.0.0.1:55432/cropguardian
export MIGRATION_DATABASE_URL ?= postgresql://cg_migrator:dev-migrator-pw@127.0.0.1:55432/cropguardian

.PHONY: budgets a11y visual visual-update lighthouse gallery help env certs up down logs up-prod migrate test test-unit test-backend test-frontend security \
        gate lock wheelhouse openapi lint fmt test-db test-db-down deps-update stubs

help: ## list targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-16s %s\n",$$1,$$2}'

env: ## generate .env with strong random secrets (never overwrites)
	@$(PY) backend/scripts/make_env.py

certs: ## dev TLS certs (mkcert if installed, else openssl via docker)
	@bash infra/nginx/make-certs.sh

up: env certs ## start the dev stack (nginx on https://localhost)
	@test -d frontend/dist || mkdir -p frontend/dist
	$(COMPOSE) up -d --build postgres redis minio minio-init api nginx
	@echo "migrating..." && $(COMPOSE) --profile tools run --rm migrate
	@echo "open https://localhost  (health: curl -k https://localhost/health)"

down: ## stop the dev stack
	$(COMPOSE) down

logs: ## follow logs
	$(COMPOSE) logs -f --tail=100

up-prod: env certs ## production reference stack: api x3 + worker x2 behind nginx
	$(COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up -d --build --scale api=3 --scale worker=2

migrate: ## apply migrations (needs MIGRATION_DATABASE_URL)
	cd backend && PYTHONPATH=. ../$(PY) -m alembic upgrade head

test-db: ## throwaway test Postgres with migrations applied
	$(TEST_COMPOSE) up -d --wait postgres redis
	$(MAKE) migrate

test-db-down: ## remove the test database
	$(TEST_COMPOSE) down -v

test-unit test-backend: ## backend tests (unit + api); integration needs `make test-db`
	cd backend && PYTHONPATH=. ../$(PY) -m pytest -q -m "not integration"

test: ## all tests that can run here (backend incl. integration if the test DB is up, then frontend)
	cd backend && PYTHONPATH=. ../$(PY) -m pytest -q
	@if [ -d frontend/node_modules ]; then cd frontend && npm test --silent; else echo "frontend not installed (npm ci)"; fi

test-frontend: ## frontend tests
	cd frontend && npm test --silent

lint: ## ruff + mypy
	cd backend && ../$(PY) -m ruff check . && ../$(PY) -m ruff format --check . && ../$(PY) -m mypy

fmt: ## format
	cd backend && ../$(PY) -m ruff format .

security: ## static security scans (bandit, forbidden, layers, honesty, pip-audit)
	cd backend && ../$(PY) -m bandit -q -r app -ll
	cd backend && ../$(PY) scripts/check_forbidden.py && ../$(PY) scripts/check_layers.py && ../$(PY) scripts/check_honesty.py
	cd backend && ../$(PY) -m pip_audit -r requirements.txt --progress-spinner off

openapi: ## regenerate backend/openapi.json
	cd backend && PYTHONPATH=. ../$(PY) scripts/export_openapi.py

lock: ## hash-locked requirements (Python 3.12 environment recommended)
	cd backend && ../$(PY) -m piptools compile --generate-hashes -o requirements.lock requirements.txt

wheelhouse: ## download Linux/py3.12 wheels on the host so `docker build` works behind TLS interception
	rm -rf backend/wheelhouse && cd backend && ../$(PY) -m pip download -r requirements.txt uvloop --dest wheelhouse 	  --only-binary=:all: --python-version 3.12 --implementation cp --abi cp312 	  --platform manylinux2014_x86_64 --platform manylinux_2_17_x86_64 --platform manylinux_2_28_x86_64 --platform any

gate: ## make gate PHASE=N [GATE_FLAGS=--offline]
	cd backend && PYTHONPATH=. ../$(PY) scripts/phase_gate.py --phase $(PHASE) $(GATE_FLAGS)

edge: ## verify nginx headers/redirect/limits (stack must be up): bash infra/nginx/verify.sh
	bash infra/nginx/verify.sh

e2e: ## Playwright journeys through nginx (stack must be up)
	cd e2e && npx playwright test

deps-update: ## show outdated pins (review, then edit requirements.txt)
	cd backend && ../$(PY) -m pip list --outdated

# Phase 2 (spec 19.7): the accessibility, visual, performance and gallery targets. Playwright ones need
# the stack up (`make up`); `visual` compares against committed baselines (`visual-update` rewrites them).
E2E_WIDTHS := --project=w360 --project=w768 --project=w1366

budgets: ## bundle budgets (spec 15.9) on a fresh production build
	cd frontend && npm run build --silent

a11y: ## axe on every built screen at 360/768/1366, both themes and languages (stack must be up)
	cd e2e && npx playwright test a11y $(E2E_WIDTHS)

visual: ## visual regression against the committed baselines (stack must be up)
	@test -f e2e/journeys/visual.spec.ts || { echo "make visual: not built yet (Phase 2 Block 3)"; exit 2; }
	cd e2e && npx playwright test visual --project=w360 --project=w1366

visual-update: ## rewrite the visual baselines after an intended design change (review the diff!)
	@test -f e2e/journeys/visual.spec.ts || { echo "make visual-update: not built yet (Phase 2 Block 3)"; exit 2; }
	cd e2e && npx playwright test visual --project=w360 --project=w1366 --update-snapshots

lighthouse: ## Lighthouse on the production build of the landing page (spec 15.11 thresholds)
	@test -f frontend/scripts/lighthouse.mjs || { echo "make lighthouse: not built yet (Phase 2 Block 3)"; exit 2; }
	cd frontend && node scripts/lighthouse.mjs

gallery: ## runs/demos/gallery.html: every built screen, light/dark, 390 and 1440, bn and en
	@test -f e2e/journeys/gallery.spec.ts || { echo "make gallery: not built yet (Phase 2 Block 3)"; exit 2; }
	cd e2e && npx playwright test gallery --project=w360 --project=w1366

# Targets from spec 19.7 that belong to later phases fail loudly instead of pretending to work.
STUB_TARGETS := seed seed-demo demo-reset create-admin fuzz zap load chaos \
                readiness advice-warm kb-ingest rag-eval ml-prepare ml-train ml-eval \
                ml-export ml-cards register-model geo backup restore-drill docs
.PHONY: $(STUB_TARGETS)
$(STUB_TARGETS):
	@echo "make $@: not implemented yet (belongs to a later phase; see docs/plans/ and spec 19.7)"; exit 2
