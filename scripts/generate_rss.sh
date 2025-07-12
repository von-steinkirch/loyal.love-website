#!/bin/bash

log() {
    echo -e "\n👾 $1"
}

success() {
    echo -e "\n✅ $1\n"
}

generate_rss() {
    log "generating rss feed..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        python3 scripts/generate_rss.py
        deactivate
    else
        log "❌ virtual environment not found. please run 'make install' first"
        exit 1
    fi
    success "✅ rss feed generated at rss.xml"
}

export -f log success generate_rss 
