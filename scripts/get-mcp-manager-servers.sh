#!/bin/bash
jq .backends.'[]|.id' < $HOME/develop/personal/mcp-manager/catalog.json
