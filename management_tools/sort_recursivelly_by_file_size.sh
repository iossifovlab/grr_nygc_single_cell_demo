#!/bin/bash

find . \( -type f -o -type l \) -print0 | while IFS= read -r -d '' f; do     stat -Lc '%s	%n' -- "$f"; done | sort -n
