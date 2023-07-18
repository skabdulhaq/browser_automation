#!/bin/bash
webhook_url="https://your-webhook-url"
payload='{"key1": "value1", "key2": "value2"}'
one_hour_from_now=$(date -d '+1 hour' +'%H:%M')
echo "curl -X POST -H 'Content-Type: application/json' -d '$payload' '$webhook_url'" | at $one_hour_from_now
