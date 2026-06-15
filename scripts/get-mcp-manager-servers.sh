#!/bin/bash
jq .backends.'[]|.id' < /home/ronnas/develop/personal/mcp-manager/catalog.json