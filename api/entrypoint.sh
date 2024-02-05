#!/bin/sh

python app/migration.py
uvicorn app.main:app --host 0.0.0.0 --port 80
