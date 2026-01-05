# Variables for easy updates
SERVER_HOST = ballesteros
USER = lemon
REMOTE_SCRIPT = /usr/local/bin/deploy_mealplanner.sh

.PHONY: deploy

deploy:
	@echo "--- Starting Deployment to $(SERVER_IP) ---"
	ssh -t $(SERVER_HOST) "sudo $(REMOTE_SCRIPT)"
	@echo "--- Deployment Complete ---"
