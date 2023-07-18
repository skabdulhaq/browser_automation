#!/bin/bash
hostname=$(hostname)
webhook_url="http://localhost:5000/container/"
delete_key="e1981379aa1f4f55bf595191be5d6ba0089661ab1fed47f08ee0351cb2e276bf"
date
echo "curl -X DELETE '${webhook_url}${hostname}?delete_key=${delete_key}'" | at now +60 minutes