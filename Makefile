install:
	@poetry install

cli:
	@poetry run python ideation_cli/cli.py

black:
	@echo "Formatting with black..."
	@poetry run black .

# Check-in code after formatting
checkin: ## Perform a check-in after formatting the code
    ifndef COMMIT_MESSAGE
		$(eval COMMIT_MESSAGE := $(shell bash -c 'read -e -p "Commit message: " var; echo $$var'))
    endif
	@git add --all; \
	  git commit -m "$(COMMIT_MESSAGE)"; \
	  git push

# Check code formatting using Black
check-black: ## Check code formatting with Black
	@echo "Checking code formatting with Black..."
	@poetry run black --check .

# Source directories for tests
TESTS_SOURCE:=tests/

# Detailed pytest target with coverage and cache clear
test: ## Run pytest with coverage and clear cache
	@echo "Running pytest with coverage and cache clear..."
	@PYTHONPATH=src/ poetry run pytest \
		--cache-clear \
		--cov=. \
		$(TESTS_SOURCE) \
		--cov-report=term \
		--cov-report=html

