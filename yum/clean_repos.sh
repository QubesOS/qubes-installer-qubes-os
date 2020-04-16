#!/bin/sh

createrepo=$(which createrepo_c createrepo 2>/dev/null |head -1)
if [ -z "$createrepo" ]; then
    echo "ERROR: createrepo not found"
    exit 1
fi

for repo in dom0-updates installer qubes-dom0 ; do
    echo "---> Cleaning up repo: $repo..."
    rm -f $repo/rpm/*.rpm
    rm -f $repo/repodata/*
    $createrepo -q $repo
done


