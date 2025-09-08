.PHONY: install prerequisites reset

default:
	@$(MAKE) --no-print-directory install

install:
	@if command -v uv > /dev/null; then uv sync --dev; else $(MAKE) prerequisites; uv sync --dev; fi

prerequisites:
	@# Remove .venv se existir (falha se estiver em uso)
	@if [ -d .venv ]; then \
		echo "🧹 Removendo .venv local..."; \
		rm -rf .venv || echo "⚠️ Não foi possível remover .venv (talvez esteja ativa)"; \
	fi

	@if command -v pipx > /dev/null; then \
		pipx install uv; \
	else \
		python -m pip install pipx; \
		pipx install uv; \
	fi
reset:
	@git reset --hard HEAD
	@git clean -fd