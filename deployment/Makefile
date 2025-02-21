build:
	@docker build -f dockerfile -t wifi_portal_image ..;


deploy:
	@docker compose down
	@docker compose up -d mariadb
	@echo "Waiting for MariaDB to initialize..."
	@sleep 10
	@echo "Waiting additional 30 seconds before starting wifi_portal..."
	@sleep 30
	@docker compose up -d wifi-portal

