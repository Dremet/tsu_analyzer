#!/bin/bash

# Hole das aktuelle Jahr und den aktuellen Monat im Format YYYYMM
CURRENT_DATE=$(date +"%Y%m")

for file in ${CURRENT_DATE}*; do
    if [ -f "$file" ] && [ $(find "$file" -mmin -60) ]; then
        echo "Uploading $file..."
        curl -v -T "$file" --ftp-create-dirs -u user:password ftp://ftp.infinityfree.com/htdocs/tsu_stats/"$file"
    else
        echo "$file is either not a regular file or not modified within the last hour, skipping..."
    fi
done

