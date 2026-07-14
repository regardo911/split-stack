# split-stack — the toolkit from *Claude Fable 5: Turn One Model Into a Team*.
#
# There is no `make demo` on purpose. A demo that prints numbers it was born
# holding proves nothing. Install the router and point it at real code instead:
#   ./install.sh  →  cd demo/invoicing-api  →  /architect <a real task>
.DEFAULT_GOAL := help
PY ?= python3

.PHONY: help install test lint clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-9s\033[0m %s\n", $$1, $$2}'

install: ## Install /architect + the executor sub-agent into ~/.claude/
	./install.sh

test: ## Run the tool tests and the checker tests (stdlib only, no network)
	$(PY) -m unittest discover -s tests -v
	bash tests/test_checkers.sh

lint: ## Syntax-check every script (no linter to install)
	$(PY) -m compileall -q chapters tests
	node --check chapters/06-handoff/contract-lint.js
	bash -n chapters/08-review/gate.sh chapters/08-review/needs-senior.sh
	bash -n chapters/05-write-a-plan/plan-check.sh install.sh

clean: ## Remove Python caches
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
