#!/bin/bash

# script to grab all send a hug secrets from secrets manager and place them in the .secrets folder
set -e  # quit on any error
PROJECT_ID="${PROJECT_ID:=send-a-hug-staging}"
SAH_HOME="${SAH_HOME:=${HOME}/git/send-hug-backend}"
CREDS_DIR=$SAH_HOME/.secrets

for s in $(gcloud --project=$PROJECT_ID secrets list --filter="labels.type:json" | cut -f1 -d" " | sed 1d)
do
	if [[ -f "$CREDS_DIR/$s/latest.json" ]]; then
		echo "$s/latest.json already exists - delete the file if you want to replace it"
	else
		echo "Writing json key: $s/latest.json"
		mkdir -p $CREDS_DIR/$s
  		# we need --format='get(payload.data)' | tr '_-' '/+' | base64 -d because gcloud messses up £ decoding
		gcloud --project=$PROJECT_ID secrets versions access "latest" --secret="$s" --format='get(payload.data)' | tr '_-' '/+' | base64 -d > $CREDS_DIR/$s/latest.json
	fi
done
