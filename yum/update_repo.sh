#!/bin/sh


# $1 -- path to rpm dir
check_repo()
{
    if ! ../scripts/rpm_verify $1/*.rpm ; then
        echo "ERROR: There are unsigned RPM packages in $1 repo:"
        echo "---------------------------------------"
        rpm --checksig $1/*.rpm | grep -v pgp 
        echo "---------------------------------------"
        echo "Sign them before proceeding."
        exit 1
    fi
}


update_repo()
{
    createrepo -q -g ../../conf/comps-qubes.xml --update $1
}


for repo in dom0-updates installer qubes-dom0 ; do
    echo "---> Processing repo: $repo..."
    ls $repo/rpm/*.rpm 2>/dev/null 1>&2
    if [ $? -ne 0 ]; then
        echo "Empty repo, skipping..."
        continue
    fi
    check_repo $repo/rpm -o $repo/repodata
    update_repo $repo -o $repo/repodata
done

#yum clean metadata
