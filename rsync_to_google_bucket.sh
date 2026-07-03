#!/bin/bash

gsutil -m rsync -n -d -r -x ".dvc|.git|.*\.task-log" . gs://nygc-demo-grr/ 

