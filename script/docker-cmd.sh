#!/bin/bash

nohup bash -c 'npm run start >> /tmp/node.log 2>&1' >& /tmp/node.log &
nohup bash -c 'flask run --host 0.0.0.0 --no-debugger >> /tmp/flask.log 2>&1' >& /tmp/flask.log &

sleep infinity
