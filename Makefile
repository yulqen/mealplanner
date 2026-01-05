# Variables for easy updates
TAILWIND = ./tailwindcss
CSS_INPUT = core/static/core/css/input.css
CSS_OUTPUT = core/static/core/css/styles.css

SERVER_HOST = ballesteros
USER = lemon
REMOTE_SCRIPT = /usr/local/bin/deploy_mealplanner.sh

.PHONY: deploy css css-watch

deploy:
	@echo "--- Starting Deployment to $(SERVER_IP) ---"
	ssh -t $(SERVER_HOST) "sudo $(REMOTE_SCRIPT)"
	@echo "--- Deployment Complete ---"

css:
	$(TAILWIND) -i $(CSS_INPUT) -o $(CSS_OUTPUT) --minify

css-watch:
	$(TAILWIND) -i $(CSS_INPUT) -o $(CSS_OUTPUT) --watch
