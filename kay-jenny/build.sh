#!/usr/bin/env bash
# exit on error
set -o errexit  

pip install -r requirements.txt
python sales_inventory_system/manage.py collectstatic --noinput
python sales_inventory_system/manage.py migrate
