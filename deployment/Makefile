all: deploy

deploy:;
	@docker compose down;
	@docker compose up --build --remove-orphans -d mariadb;
	@echo "Waiting for MariaDB to initialize...";
	@sleep 30;
	@echo "Starting  wifi_portal...";
	@docker compose up --build --remove-orphans -d wifi;
	@echo "Starting nginx...";
	@docker compose up --build --remove-orphans -d nginx;

.PHONY: all deploy
