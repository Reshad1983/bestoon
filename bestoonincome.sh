#!/bin/bash
mytoken=12345678
curl --data "token=$mytoken&amount=$1&text=$2" http://localhost:8009/submit/expense/
