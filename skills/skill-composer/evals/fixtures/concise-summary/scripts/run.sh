#!/bin/sh
set -eu

claude --print "Summarize the project at $1 in exactly five factual bullets."
