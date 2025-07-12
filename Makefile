.PHONY: install optimize-images precompress server clean all setup rss validate-rss lint post post-post server-prod

PORT ?= 8000
VENV = venv
PYTHON = $(VENV)/bin/python3

install:
	pip3 install -r requirements.txt

optimize-images:
	@echo "optimizing images for web performance..."
	python3 scripts/optimize-images.py --directory imgs --quality 85 --webp-quality 80
	@echo "image optimization complete!"

precompress:
	@echo "pre-compressing static files..."
	python3 scripts/server.py --precompress
	@echo "pre-compression complete!"

server-prod:
	@echo "starting production server with optimizations..."
	python3 scripts/server.py --port 8000 --precompress

clean:
	@echo "cleaning generated files..."
	find . -name "*.gz" -delete
	find imgs -name "*_optimized.*" -delete
	find imgs -name "*_webp.webp" -delete
	@echo "clean complete!"

all: install optimize-images precompress
	@echo "all optimizations complete!"

setup: install all
	@echo "setup complete! run 'make serve' to start the server."

rss:
	@bash -c 'source scripts/generate_rss.sh && generate_rss'

validate-rss:
	$(PYTHON) scripts/validate_rss.py rss.xml

server:
	@echo "👾 starting local server on port $(PORT)..."
	python3 scripts/server.py --port $(PORT)

lint:
	@echo "\n👾 running lint..."
	@bash -c 'source scripts/run_lint.sh && run_lint'

post:
	python3 scripts/generate_post.py

post-post:
	make lint
	make rss
	make validate-rss
