.PHONY: server fix-links install clean

PORT ?= 8000

server:
	@echo "👾 starting local server on port $(PORT)..."
	python3 -m http.server $(PORT)

lint:
	@echo "👾 fixing links in HTML files..."
	node .github/workflows/fix-links.js
	@echo "👾 formatting HTML files..."
	npx prettier --write --config .github/workflows/.prettierrc "index.html" "chapters/*.html"
	@echo "Linting HTML files..."
	npx html-validate --config $(shell pwd)/.github/workflows/.htmlvalidate.json "index.html" "chapters/*.html"

install:
	@echo "👾 installing dependencies..."
	npm install

clean:
	@echo "👾 leaning up..."
	rm -rf node_modules/
	rm -f .DS_Store
