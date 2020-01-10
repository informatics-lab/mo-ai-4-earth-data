#! /usr/bin/env bash

set -ex

source .env

cd __app__

func azure functionapp publish $APP_NAME --publish-local-settings -y