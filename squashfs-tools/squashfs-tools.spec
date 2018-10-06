Summary: Utility for the creation of squashfs filesystems
Name: squashfs-tools
Version: 4.3
Release: 16%{?dist}
License: GPLv2+
Group: System Environment/Base
URL: http://squashfs.sourceforge.net/
Source0: http://downloads.sourceforge.net/squashfs/squashfs%{version}.tar.gz
# manpages from http://ftp.debian.org/debian/pool/main/s/squashfs-tools/squashfs-tools_4.2+20121212-1.debian.tar.xz
# The man pages have been modified for 4.3 for Fedora.
Source1: mksquashfs.1
Source2: unsquashfs.1
# From master branch (55f7ba830d40d438f0b0663a505e0c227fc68b6b).
# 32 bit process can use too much memory when using PAE or 64 bit kernels
Patch0:  PAE.patch
# From master branch (604b607d8ac91eb8afc0b6e3d917d5c073096103).
# Prevent overflows when using the -mem option.
Patch1:  mem-overflow.patch
# From squashfs-devel@lists.sourceforge.net by Guan Xin <guanx.bac@gmail.com>
# For https://bugzilla.redhat.com/show_bug.cgi?id=1141206
Patch2:  2gb.patch
# From https://github.com/gcanalesb/sasquatch/commit/6777e08cc38bc780d27c69c1d8c272867b74524f
# Which is forked from Phillip's squashfs-tools, though it looks like 
# the issue applies to us.
Patch3:  cve-2015-4645.patch
# Update formats to match changes in cve-2015-4645.patch
Patch4:  local-cve-fix.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: zlib-devel
BuildRequires: xz-devel
BuildRequires: lzo-devel
BuildRequires: libattr-devel
BuildRequires: lz4-devel

%description
Squashfs is a highly compressed read-only filesystem for Linux.  This package
contains the utilities for manipulating squashfs filesystems.

%prep
%setup -q -n squashfs%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p0
%patch3 -p1
%patch4 -p0

%build
pushd squashfs-tools
CFLAGS="%{optflags}" XZ_SUPPORT=1 LZO_SUPPORT=1 LZMA_XZ_SUPPORT=1 LZ4_SUPPORT=1 make %{?_smp_mflags}

%install
mkdir -p %{buildroot}%{_sbindir} %{buildroot}%{_mandir}/man1
install -m 755 squashfs-tools/mksquashfs %{buildroot}%{_sbindir}/mksquashfs
install -m 755 squashfs-tools/unsquashfs %{buildroot}%{_sbindir}/unsquashfs
install -m 644 %{SOURCE1} %{buildroot}%{_mandir}/man1/mksquashfs.1
install -m 644 %{SOURCE2} %{buildroot}%{_mandir}/man1/unsquashfs.1

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README ACKNOWLEDGEMENTS DONATIONS PERFORMANCE.README README-4.3 CHANGES pseudo-file.example COPYING

%doc README
%{_mandir}/man1/*

%{_sbindir}/mksquashfs
%{_sbindir}/unsquashfs

%changelog
* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.3-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.3-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.3-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.3-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 4.3-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jun 23 2015 Bruno Wolff III <bruno@wolff.to> - 4.3-10
- Fix for CVE 2015-4645/4646

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.3-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Sep 13 2014 Bruno Wolff III <bruno@wolff.to> 4.3-8
- Fix for files >= 2gb rhbz #1141206

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jun 13 2014 Bruno Wolff III <bruno@wolff.to> 4.3-6
- Apply a couple of upstream patches.
- Fixes issue issue with too much memory use under PAE kernels

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 14 2014 Bruno Wolff III <bruno@wolff.to> 4.3-4
- Even more man page fixes

* Wed May 14 2014 Bruno Wolff III <bruno@wolff.to> 4.3-3
- More mksquashfs man page fixes

* Tue May 13 2014 Bruno Wolff III <bruno@wolff.to> 4.3-2
- Add missed option to the mksquashfs man page

* Tue May 13 2014 Bruno Wolff III <bruno@wolff.to> 4.3-1
- Update to real 4.3 release
- Added support for lz4 since the stable snapshot
- Added support for alternate zlib compression strategies

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.3-0.19.gitaae0aff4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sat Jun 22 2013 Bruno Wolff III <bruno@wolff.to> - 4.3-0.18.gitaae0aff4
- Latest pre 4.3 stable snapshot
- A few minor bug fixes
- Improvements in getting status info while running unsquashfs

* Tue Jun 04 2013 Bruno Wolff III <bruno@wolff.to> - 4.3-0.17.git5c6f0024
- Latest pre 4.3 snapshot
- Includes fix for mksquashfs hangs
- Switch to get pre-release updates from the stable branch at kernel.org

* Thu May 23 2013 Bruno Wolff III <bruno@wolff.to> - 4.3-0.16.git84d8ae5c
- Latest pre 4.3 snapshot
- Fix for a rare race condition

* Sun May 19 2013 Bruno Wolff III <bruno@wolff.to> - 4.3-0.15.git27d7c14b
- Latest pre 4.3 snapshot
- queue fragment and empty file buffers directly to main thread

* Wed May 15 2013 Bruno Wolff III <bruno@wolff.to> - 4.3-0.14.git8ce5585e
- Latest pre 4.3 snapshot
- Includes upstream bugfix introduced with the sequential queue change

* Sat May 11 2013 Bruno Wolff III <bruno@wolff.to> - 4.3-0.13.gitc2362556
- Latest pre 4.3 snapshot
- Sequential queue change

* Mon May 06 2013 Bruno Wolff III <bruno@wolff.to> - 4.3-0.12.git9353c998
- Latest pre 4.3 snapshot

* Sun Mar 31 2013 Bruno Wolff III <bruno@wolff.to> - 4.3-0.11.git8228a3e8
- Latest pre 4.3 snapshot
- SIGQUIT now displays the file being squashed

* Wed Mar 06 2013 Bruno Wolff III <bruno@wolff.to> - 4.3-0.10.git6a103792
- Latest pre 4.3 snapshot
- Pick up some more error handling improvements

* Sun Mar 03 2013 Kyle McMartin <kmcmarti@redhat.com>
- Move mksquashfs to /usr/sbin, as per UsrMove.

* Sun Mar 03 2013 Kyle McMartin <kmcmarti@redhat.com>
- Add mksquashfs.1 and unsquashfs.1 manpages from Debian.

* Mon Feb 18 2013 Bruno Wolff III <bruno@wolff.to> - 4.3-0.9.git3ec9c8f7
- Latest pre 4.3 snapshot
- Better error handling when space runs out

* Wed Feb 13 2013 Bruno Wolff III <bruno@wolff.to> - 4.3-0.8.gitca6a1c90
- Latest pre 4.3 snapshot
- New option to display compression options used
- Some error message improvements

* Fri Feb 01 2013 Bruno Wolff III <bruno@wolff.to> - 4.3-0.7.gitb10063a9
- Latest pre 4.3 snapshot
- More checks for bad data

* Sun Jan 13 2013 Bruno Wolff III <bruno@wolff.to> - 4.3-0.6.git6c0f229d
- Latest pre 4.3 snapshot
- Quote and backslash parsing for lexical analyzer

* Mon Dec 31 2012 Bruno Wolff III <bruno@wolff.to> - 4.3-0.5.gitc11af515
- Latest pre 4.3 snapshot
- A few memory leak fixes
- Additional checks for handling bad data

* Sun Dec 23 2012 Bruno Wolff III <bruno@wolff.to> - 4.3-0.4.git99a009c8
- Better checking of data in psuedo files

* Fri Dec 21 2012 Bruno Wolff III <bruno@wolff.to> - 4.3-0.3.git7ec6bd7a
- Better checking of data in sort, extract and exclude files

* Thu Dec 13 2012 Bruno Wolff III <bruno@wolff.to> - 4.3-0.2.git54719971
- Pick up a few more changes to better handle bad data

* Sat Dec 01 2012 Bruno Wolff III <bruno@wolff.to> - 4.3-0.1.git0be606be
- Pre-release of 4.3 to get early testing
- This update includes a bit of internal code infrastructure changes
- There are lots of fixes to better handle bad data
- The final release is expected sometime in December
- Until the release only the README doc file is available

* Sun Nov 25 2012 Bruno Wolff III <bruno@wolff.to> - 4.2-5
- Backported fix for bz 842460 (CVE-2012-4025)

* Thu Nov 22 2012 Bruno Wolff III <bruno@wolff.to> - 4.2-4
- Backported fix for bz 842458 (CVE-2012-4024)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Mar 01 2011 Bruno Wolff III <bruno@wolff.to> - 4.2-1
- 4.2 is released.
- Bugfix for bad data causing crash.
- Include doc files added for release.
- Big endian patch is now upstream.
- Buildroot tag isn't needed any more.
- We can now specify CFLAGS on the make call.
- Compressor options are now passed with the make call.

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2-0.4.20101231
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Jan 11 2011 Dan Horák <dan[at]danny.cz> - 4.2-0.3.20101231
- Add fixes for big-endian machines

* Sat Jan 01 2011 Bruno Wolff III <bruno@wolff.to> - 4.2-0.2.20101231
- Pull latest upstream snapshot
- Includes check for matching compression type when adding to an existing image
- Sample cvs command now includes timezone and specifies when on the date to use for the snapshot

* Fri Dec 24 2010 Bruno Wolff III <bruno@wolff.to> - 4.2-0.1.20101223
- Switch to 4.2 development snapshot to get new XZ support
- LZMA and XZ (LZMA2) support are now different

* Wed Oct 27 2010 Bruno Wolff III <bruno@wolff.to> - 4.1-3
- Rebuild for xz soname bump

* Wed Sep 29 2010 jkeating - 4.1-2
- Rebuilt for gcc bug 634757

* Tue Sep 21 2010 Bruno Wolff III <bruno@wolff.to> - 4.1-1
- Update to 4.1 final.
- Byte swap patch is now upstream.
- LZO compression type is now supported.

* Mon Sep 6 2010 Dan Horák <dan[at]danny.cz> - 4.1-0.5.20100827
- Add fixes for big-endian machines

* Sat Aug 28 2010 Bruno Wolff III <bruno@wolff.to> - 4.1-0.4.20100827
- Rebase to latest upstream.
- The main reason is to pick up a fix for large xattr similar to the large inode fix. This doesn't need to get backported as 4.0 doesn't have xattr support.
- An option was added to build without xattr support.
- Various source cleanups have been done as well.

* Tue Aug 03 2010 Bruno Wolff III <bruno@wolff.to> - 4.1-0.3.20100803
- Rebase to latest upstream
- Prevent warning message for xattr for virtual directory
- Fix issue with large inodes - BZ 619020

* Tue Jul 27 2010 Bruno Wolff III <bruno@wolff.to> - 4.1-0.2.20100727
- Rebase to latest upstream devel state. Mostly xattr fixes and cleanup.

* Tue Jun 08 2010 Bruno Wolff III <bruno@wolff.to> - 4.1-0.1.20100607
- Rebase to 4.1 prerelease with xz wrapper
- Provides lzma compression as an option.
- squashfs-fix-unsquashing-v3.patch is part of the 4.1 prerelease

* Wed May 5 2010 Kyle McMartin <kyle@redhat.com> 4.0-4
- squashfs-fix-unsquashing-v3.patch: pull in fix from cvs. Thanks pkl!
  (rhbz#523504)

* Thu Feb 18 2010 Kyle McMartin <kyle@redhat.com> 4.0-3
- Update to release tarball as opposed to cvs snapshot.
- Add dist tag.

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Apr 05 2009 Kyle McMartin <kyle@redhat.com> - 4.0-1
- Update to release 4.0

* Mon Mar 16 2009 Kyle McMartin <kyle@redhat.com> - 4.0-0.20090316
- update to cvs snap from 2009-03-16.

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0-0.20090126
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Jan 26 2009 Kyle McMartin <kyle@redhat.com> - 4.0-0.20090125
- update to cvs snap that should unbreak big endian machines creating
  little endian fs.

* Mon Jan 12 2009  <katzj@redhat.com> - 4.0-0.20090112
- update to cvs snap that generates v4.0 images

* Tue Sep 30 2008 Jeremy Katz <katzj@redhat.com> - 3.4-1
- update to 3.4

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.3-2
- Autorebuild for GCC 4.3

* Fri Dec 14 2007 Jeremy Katz <katzj@redhat.com> - 3.3-1
- Update to 3.3

* Wed Sep  5 2007 Jeremy Katz <katzj@redhat.com> - 3.2-2
- fixes from package review (#226430)

* Tue Mar 20 2007 Jeremy Katz <katzj@redhat.com> - 3.2-1
- update to 3.2r2

* Sun Oct 01 2006 Jesse Keating <jkeating@redhat.com> - 3.0-4
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Mon Sep 18 2006 Jeremy Katz <katzj@redhat.com> - 3.0-3
- updated fragment size patch (#204638)

* Wed Aug 16 2006 Jeremy Katz <katzj@redhat.com> - 3.0-2
- add upstream patch for fragment size problem (#202663)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 3.0-1.1
- rebuild

* Fri Jun 23 2006 Jeremy Katz <katzj@redhat.com> - 3.0-1
- update to 3.0
- include unsquashfs

* Tue May 16 2006 Jeremy Katz <katzj@redhat.com> 
- add BR on zlib-devel (Andreas Thienemann, #191880)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.2r2-2.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.2r2-2.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Dec  1 2005 Jeremy Katz <katzj@redhat.com> - 2.2r2-1
- Initial build

