#!/bin/bash
# Simple crawler runner

if [ -z "$1" ]; then
    echo "Usage:"
    echo "  ./run.sh crawl [name]  - Run crawler(s)"
    echo "  ./run.sh merge         - Merge data"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Run command
case "$1" in
    crawl)
        if [ -z "$2" ]; then
            # Run all crawlers
            for dir in src/crawl/*/; do
                if [ -f "${dir}crawler.py" ]; then
                    python3 "${dir}crawler.py"
                fi
            done
        else
            # Run specific crawler
            python3 "src/crawl/$2/crawler.py"
        fi
        ;;
    merge)
        python3 src/merge_data.py
        ;;
    *)
        echo "Unknown command: $1"
        exit 1
        ;;
esac
