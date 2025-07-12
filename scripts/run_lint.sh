#!/bin/bash

log() {
    echo -e "\n👾 $1"
}

success() {
    echo -e "\n✅ $1\n"
}

run_lint() {
    log "👾 fixing links in html files..."
    node scripts/fix_links.js
    
    log "👾 formatting html files..."
    npx prettier --write --config .github/workflows/.prettierrc.json "index.html" "chapters/*.html" "shared/*.html"
    
    log "👾 linting html files..."
    npx html-validate --config "$(pwd)/.github/workflows/.htmlvalidate.json" "index.html" "chapters/*.html" "shared/*.html"
    
    success "✅ linting completed"
}

export -f log success run_lint 
