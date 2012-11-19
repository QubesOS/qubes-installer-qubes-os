for repo in dom0-updates installer qubes-dom0 ; do
    echo "---> Cleaning up repo: $repo..."
    rm -f $repo/rpm/*.rpm
    rm -f $repo/repodata/*
    createrepo -q $repo
done


