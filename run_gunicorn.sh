#!/bin/bash
source /root/SQL_Tester_final/venv/bin/activate
exec gunicorn -w 3 -b 0.0.0.0:8000 app:app