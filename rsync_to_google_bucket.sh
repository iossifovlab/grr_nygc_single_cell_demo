#!/bin/bash

gsutil -m rsync -d -r -x ".dvc|.git|.*\.task-log" . gs://nygc-demo-grr/ 

