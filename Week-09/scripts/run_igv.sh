#!/usr/bin/env bash
set -euo pipefail
: "${IGV_DIR:?Set IGV_DIR to your existing IGV Linux directory}"
batch=$1
test -f "$IGV_DIR/igv.args"
java_bin=java
if [[ -x "$IGV_DIR/jdk-21/bin/java" ]]; then
    java_bin="$IGV_DIR/jdk-21/bin/java"
fi
"$java_bin" --module-path="$IGV_DIR/lib" -Xmx2g @"$IGV_DIR/igv.args" -Dsamjdk.snappy.disable=true -Djava.net.preferIPv4Stack=true --module=org.igv/org.broad.igv.ui.Main -b "$batch"
