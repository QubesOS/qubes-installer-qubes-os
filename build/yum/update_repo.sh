#!/bin/sh


# $1 -- path to rpm dir
check_repo()
{
    if ! [ $(ls -A "$1/*.rpm"  2>/dev/null) ] ; then
        echo -n "Repo $1 is empty!"
        return
    fi
    if rpm --checksig $1/*.rpm | grep -v pgp > /dev/null ; then
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
    createrepo --update $1
}


for repo in * ; do
    echo "--> Processing repo: $repo..."
    check_repo $repo/rpm -o $repo/repodata
    update_repo $repo -o $repo/repodata
done

#yum clean metadata
