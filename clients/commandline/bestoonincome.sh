#!/bin/bash
TOKEN = 12345678
BASE_URL = http://localhost:8009
curl --data "token=$TOKEN&amount=$1&text=$2" $BASE_URL/submit/income/