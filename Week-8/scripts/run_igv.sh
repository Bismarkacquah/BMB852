#!/usr/bin/env bash
set -euo pipefail
igv_dir=${IGV_DIR:-/opt/IGV_Linux_2.19.8}
batch=${1:-igv/five_samples.batch.txt}
test -d "$igv_dir/lib"
java_bin=java
if [[ -x "$igv_dir/jdk-21/bin/java" ]]; then
    java_bin="$igv_dir/jdk-21/bin/java"
fi
"$java_bin" --module-path="$igv_dir/lib" -Xmx2g @"$igv_dir/igv.args" -Dsamjdk.snappy.disable=true -Djava.net.preferIPv4Stack=true --module=org.igv/org.broad.igv.ui.Main -b "$batch"
