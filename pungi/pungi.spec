%if 0%{?qubes_builder}
%define _sourcedir %(pwd)/pungi
%endif

Name:           pungi
Version:        4.0.7
Release:        1%{?dist}
Summary:        Distribution compose tool

Group:          Development/Tools
License:        GPLv2
URL:            https://pagure.io/pungi
Source0:        https://fedorahosted.org/pungi/attachment/wiki/%{version}/%{name}-%{version}.tar.bz2
Patch1:         0001-Set-repository-gpgkey-option.patch
Patch2:         0002-Verify-downloaded-packages.patch
Patch3:         disable-efi.patch
Patch4:         Hacky-way-to-pass-gpgkey-to-lorax.patch
#Patch5:         fix-recursive-partition-table-on-iso-image.patch
#Patch6:         disable-upgrade.patch
BuildRequires:  python-nose, python-nose-cov, python-mock
BuildRequires:  python-devel, python-setuptools, python2-productmd
BuildRequires:  python-lockfile, kobo, kobo-rpmlib, python-kickstart, createrepo_c
BuildRequires:  python-lxml, libselinux-python, yum-utils, lorax
BuildRequires:  yum => 3.4.3-28, createrepo >= 0.4.11

Requires:       createrepo >= 0.4.11
Requires:       yum => 3.4.3-28
Requires:       lorax >= 22.1
Requires:       repoview
Requires:       python-lockfile
Requires:       kobo
Requires:       kobo-rpmlib
Requires:       python-productmd
Requires:       python-kickstart
Requires:       libselinux-python
Requires:       createrepo_c
Requires:       python-lxml
Requires:       koji
Requires:       cvs
Requires:       yum-utils
Requires:       isomd5sum
Requires:       genisoimage
Requires:       gettext
Requires:       git

BuildArch:      noarch

%description
A tool to create anaconda based installation trees/isos of a set of rpms.

%prep
%setup -q

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
#%%patch5 -p1
#%%patch6 -p1

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%{__install} -d $RPM_BUILD_ROOT/var/cache/pungi

%check
./tests/data/specs/build.sh
%{__python} setup.py test
nosetests --exe --with-cov --cov-report html --cov-config tox.ini
#TODO: enable compose test
#cd tests && ./test_compose.sh

%files
%license COPYING GPL
%doc AUTHORS doc/*
%{python_sitelib}/%{name}
%{python_sitelib}/%{name}-%{version}-py?.?.egg-info
%{_bindir}/*
%{_datadir}/pungi
/var/cache/pungi

%changelog
* Thu Mar 03 2016 Dennis Gilmore <dennis@ausil.us> - 4.0.7-1
- Limit the variants with config option 'tree_variants' (dennis)
- [createrepo-wrapper] Fix --deltas argument (lsedlar)
- [createrepo-wrapper] Add tests (lsedlar)
- [koji-wrapper] Retry watching on connection errors (lsedlar)
- [createrepo-wrapper] Refactor code (lsedlar)
- [paths] Use variant.uid explicitly (lsedlar)
- [createrepo] Add tests (lsedlar)
- [createrepo] Refactor code (lsedlar)
- [image-build] Fix resolving git urls (lsedlar)
- [testphase] Don't run repoclosure for empty variants (lsedlar)
- [live-images] No manifest for appliances (lsedlar)

* Fri Feb 26 2016 Dennis Gilmore <dennis@ausil.us> - 4.0.6-1
- push the 4.0 docs to a 4.0 branch (dennis)
- [live-images] Rename log file (lsedlar)
- [buildinstall] Use -dvd- in volume ids instead of -boot- (lsedlar)
- [buildinstall] Hardlink boot isos (lsedlar)
- [doc] Write documentation for kickstart Git URLs (lsedlar)
- [util] Resolve branches in git urls (lsedlar)
- [live-images] Fix crash when repo_from is not a list (lsedlar)
- [buildinstall] Don't copy files for empty variants (lsedlar)

* Tue Feb 23 2016 Dennis Gilmore <dennis@ausil.us> - 4.0.5-1
- [tests] Fix wrong checks in buildinstall tests (lsedlar)
- [tests] Use temporary files for buildinstall (lsedlar)
- [tests] Do not mock open for koji wrapper tests (lsedlar)
- Merge #179 `Update makefile targets for testing` (ausil)
- Update makefile targets for testing (lsedlar)
- [live-images] Set type to raw-xz for appliances (lsedlar)
- [live-images] Correctly create format (lsedlar)
- [tests] Dummy compose is no longer private (lsedlar)
- [tests] Move buildinstall tests to new infrastructure (lsedlar)
- [tests] Use real paths module in testing (lsedlar)
- [tests] Move dummy testing compose into separate module (lsedlar)
- [live-images] Create image dir if needed (lsedlar)
- [live-images] Add images to manifest (lsedlar)
- [live-images] Fix path processing (lsedlar)
- [live-images] Move repo calculation to separate method (lsedlar)
- [koji-wrapper] Fix getting results from spin-appliance (lsedlar)
- [live-images] Filter non-image results (lsedlar)
- [live-images] Rename repos_from to repo_from (lsedlar)
- [koji-wrapper] Add test for passing release to image-build (lsedlar)
- [live-images] Automatically populate release with date and respin (lsedlar)
- [live-media] Respect release set in configuration (lsedlar)
- [live-images] Build all images specified in config (lsedlar)
- [live-media] Don't create $basedir arch (lsedlar)
- Update tests (lsedlar)
- do not ad to image build and live tasks the variant if it is empty (dennis)
- when a variant is empty do not add it to the repolist for livemedia (dennis)
- [live-media] Update tests to use $basearch (lsedlar)
- [buildinstall] Don't run lorax for empty variants (lsedlar)
- Merge #159 `use $basearch not $arch in livemedia tasks` (lubomir.sedlar)
- Merge #158 `do not uses pipes.quotes in livemedia tasks` (lubomir.sedlar)
- Add documentation for signing support that was added by previous commit
  (tmlcoch)
- Support signing of rpm wrapped live images (tmlcoch)
- Fix terminology - Koji uses sigkey not level (tmlcoch)
- use $basearch not $arch in livemedia tasks (dennis)
- do not uses pipes.quotes in livemedia tasks (dennis)
- [live-images] Don't tweak kickstarts (lsedlar)
- Allow specifying empty variants (lsedlar)
- [createrepo] Remove dead assignments (lsedlar)
- Keep empty query string in resolved git url (lsedlar)
- [image-build] Use dashes as arch separator in log (lsedlar)
- [buildinstall] Stop parsing task_id (lsedlar)
- [koji-wrapper] Get task id from failed runroot (lsedlar)
- [live-media] Pass ksurl to koji (lsedlar)
- Merge #146 `[live-media] Properly calculate iso dir` (ausil)
- [live-media] Properly calculate iso dir (lsedlar)
- [image-build] Fix tests (lsedlar)
- add image-build sections (lkocman)
- [koji-wrapper] Add tests for get_create_image_cmd (lsedlar)
- [live-images] Add support for spin-appliance (lsedlar)
- [live-media] Koji option is ksfile, not kickstart (lsedlar)
- [live-media] Use install tree from another variant (lsedlar)
- [live-media] Put images into iso dir (lsedlar)
- [image-build] Koji expects arches as a comma separated string (lsedlar)
- Merge #139 `Log more details when any deliverable fails` (ausil)
- [live-media] Version is required argument (lsedlar)
- [koji-wrapper] Only parse output on success (lsedlar)
- [koji-wrapper] Add tests for runroot wrapper (lsedlar)
- [buildinstall] Improve logging (lsedlar)
- Log more details about failed deliverable (lsedlar)
- [image-build] Fix failable tests (lsedlar)
- Merge #135 `Add live media support` (ausil)
- Merge #133 `media_split: add logger support. Helps with debugging space
  issues on dvd media` (ausil)
- [live-media] Add live media phase (lsedlar)
- [koji-wrapper] Add support for spin-livemedia (lsedlar)
- [koji-wrapper] Use more descriptive method names (lsedlar)
- [image-build] Remove dead code (lsedlar)
- media_split: add logger support. Helps with debugging space issues on dvd
  media (lkocman)
- [image-build] Allow running image build scratch tasks (lsedlar)
- [image-build] Allow dynamic release for images (lsedlar)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 20 2016 Dennis Gilmore <dennis@ausil.us> - 4.0.4-1
- 4.0.4 release (dennis)
- Merge #123 `Live images: add repo from another variant` (ausil)
- Merge #125 `[image-build] Stop creating wrong arch dirs` (ausil)
- Toggle multilib per variant (lsedlar)
- [live-images] Code cleanup (lsedlar)
- [live-images] Add documentation (lsedlar)
- [live-images] Add repos from other variants (lsedlar)
- [image-build] Stop creating wrong arch dirs (lsedlar)
- Enable identifying variants in exception traces (lsedlar)
- Store which deliverables failed (lsedlar)
- scm.py: use git clone instead git archive for http(s):// (lkocman)
- Fix filtering of system release packages (lsedlar)
- Merge #114 `Use install tree/repo from another variant for image build`
  (ausil)
- Make system release package filtering optional (lsedlar)
- [image-build] Optionally do not break whole compose (lsedlar)
- [image-build] Refactoring (lsedlar)
- [image-build] Use repo from another variant (lsedlar)
- [image-build] Take install tree from another variant (lsedlar)
- Add missing formats to volumeid and image name (lsedlar)
- [image-build] Use single koji task per variant (lsedlar)
- Fix image-build modifying config (lsedlar)
- Fix missing checksums in .treeinfo (lsedlar)
- Don't crash on generating volid without variant (lsedlar)
- Merge #99 `Add option to specify non-failing stuff` (ausil)
- Add repo from current compose (lsedlar)
- Fix getting compose topdir in CreateImage build thread (lsedlar)
- Add option to specify non-failing stuff (lsedlar)
- Allow customizing image name and volume id (lsedlar)
- Fix notifier tests (lsedlar)
- Publish a url instead of a file path. (rbean)
- Add 'topdir' to all fedmsg/notifier messages. (rbean)
- Merge #75 `Start of development guide` (ausil)
- Merge #88 `Resolve HEAD in ksurl to actual hash` (ausil)
- Merge #87 `Add support for customizing lorax options` (ausil)
- Update fedmsg notification hook to use appropriate config. (rbean)
- we need to ensure that we send all the tasks to koji on the correct arch
  (dennis)
- Resolve HEAD in ksurl to actual hash (lsedlar)
- Add support for customizing lorax options (lsedlar)
- Run lorax in separate dirs for each variant (lsedlar)
- Merge #84 `Allow specifying --installpkgs for lorax` (ausil)
- Merge #83 `Fix recently discovered bugs` (ausil)
- Merge #82 `indentation fixs correcting dvd creation` (ausil)
- Merge #69 `Move messaging into cli options and simplify it` (ausil)
- Start lorax for each variant separately (lsedlar)
- Update lorax wrapper to use --installpkgs (lsedlar)
- Allow specifying which packages to install in variants xml (lsedlar)
- Add basic tests for buildinstall phase (lsedlar)
- Fix generating checksum files (lsedlar)
- Use lowercase hashed directories (lsedlar)
- indentation fixs correcting dvd creation (dennis)
- remove glibc32 from the runroot tasks (dennis)
- fix up the pungi-fedmesg-notification script name (dennis)
- Add overview of Pungi to documentation (lsedlar)
- Move messaging into cli options (lsedlar)
- Extend contributing guide (lsedlar)
- Load multilib configuration from local dir in development (lsedlar)
- Allow running scripts with any python in PATH (lsedlar)

* Tue Aug 08 2015 Dennis Gilmore <dennis@ausil.us> 4.0.3-1
- Merge #54 `fix log_info for image_build (fails if image_build is skipped)`
  (lkocman)
- image_build: self.log_info -> self.compose.log_info (lkocman)
- Revert "Added params needed for Atomic compose to LoraxWrapper" (dennis)
- Revert "fix up if/elif in _handle_optional_arg_type" (dennis)
- Add image-build support (lkocman)
- Add translate path support. Useful for passing pungi repos to image-build
  (lkocman)
- import duplicate import of errno from buildinstall (lkocman)
- handle openning missing images.json (image-less compose re-run) (lkocman)
- compose: Add compose_label_major_version(). (lkocman)
- pungi-koji: Don't print traceback if error occurred. (pbabinca)
- More detailed message for unsigned rpms. (tkopecek)
- New config option: product_type (default is 'ga'); Set to 'updates' for
  updates composes. (dmach)
- kojiwrapper: Add get_signed_wrapped_rpms_paths() and get_build_nvrs()
  methods. (tmlcoch)
- live_images: Copy built wrapped rpms from koji into compose. (tmlcoch)
- kojiwrapper: Add get_wrapped_rpm_path() function. (tmlcoch)
- live_images: Allow custom name prefix for live ISOs. (tmlcoch)
- Do not require enabled runroot option for live_images phase. (tmlcoch)
- Support for rpm wrapped live images. (tmlcoch)
- Remove redundant line in variants wrapper. (tmlcoch)
- Merge #36 `Add params needed for Atomic compose to LoraxWrapper` (admiller)
- live_images: replace hardcoded path substition with translate_path() call
  (lkocman)
- live_images fix reference from koji to koji_wrapper (lkocman)
- fix up if/elif in _handle_optional_arg_type (admiller)
- Added params needed for Atomic compose to LoraxWrapper (admiller)
- Merge #24 `Fix empty repodata when hash directories were enabled. ` (dmach)
- createrepo: Fix empty repodata when hash directories were enabled. (dmach)

* Fri Jul 24 2015 Dennis Gilmore <dennis@ausil.us> - 4.0.2-1
- Merge #23 `fix treeinfo checksums` (dmach)
- Fix treeinfo checksums. (dmach)
- add basic setup for making arm iso's (dennis)
- gather: Implement hashed directories. (dmach)
- createiso: Add createiso_skip options to skip createiso on any variant/arch.
  (dmach)
- Fix buildinstall for armhfp. (dmach)
- Fix and document productimg phase. (dmach)
- Add armhfp arch tests. (dmach)
- Document configuration options. (dmach)
- Add dependency of 'runroot' config option on 'koji_profile'. (dmach)
- Rename product_* to release_*. (dmach)
- Implement koji profiles. (dmach)
- Drop repoclosure-%arch tests. (dmach)
- Config option create_optional_isos now defaults to False. (dmach)
- Change createrepo config options defaults. (dmach)
- Rewrite documentation to Sphinx. (dmach)
- Fix test data, improve Makefile. (dmach)
- Update GPL to latest version from https://www.gnu.org/licenses/gpl-2.0.txt
  (dmach)

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jun 11 2015 Dennis Gilmore <dennis@ausil.us> - 4.0.1-1
- wrap check for selinux enforcing in a try except (dennis)
- pull in gather.py patches from dmach for test compose (admiller)
- Add some basic testing, dummy rpm creation, and a testing README (admiller)
- pungi-koji: use logger instead of print when it's available (lkocman)
- fix incorrect reference to variable 'product_is_layered' (lkocman)
- pungi-koji: fix bad module path to verify_label() (lkocman)
- update the package Requires to ensure we have everything installed to run
  pungi-koji (dennis)
- update the package to be installed for productmd to python-productmd (dennis)

* Sun Jun 07 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.9.20150607.gitef7c78c
- update docs now devel-4-pungi is merged to master, minor spelling fixes
  (pbrobinson)
- Fix remaining productmd issues. (dmach)
- Revert "refactor metadata.py to use productmd's compose.dump for composeinfo"
  (dmach)
- Fix LoraxTreeInfo class inheritance. (dmach)
- Fix pungi -> pungi_wrapper namespace issue. (dmach)
- fix arg order for checksums.add (admiller)
- update for productmd checksums.add to TreeInfo (admiller)
- fix product -> release namespace change for productmd (admiller)
- update arch manifest.add config order for productmd api call (admiller)
- update for new productmd named args to rpms (admiller)
- fix pungi vs pungi_wrapper namespacing in method_deps.py (admiller)
- add createrepo_c Requires to pungi.spec (admiller)
- add comps_filter (admiller)
- refactor metadata.py to use productmd's compose.dump for composeinfo instead
  of pungi compose_to_composeinfo (admiller)
- Update compose, phases{buildinstall,createiso,gather/__ini__} to use correct
  productmd API calls (admiller)
- Use libselinux-python instead of subprocess (lmacken)
- Add README for contributors (admiller)

* Wed May 20 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.8.20150520.gitff77a92
- fix up bad += from early test of implementing different iso labels based on
  if there is a variant or not (dennis)

* Wed May 20 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.7.20150520.gitdc1be3e
- make sure we treat the isfinal option as a boolean when fetching it (dennis)
- if there is a variant use it in the volume id and shorten it. this will make
  each producst install tree have different volume ids for their isos (dennis)
- fix up productmd import in the executable (dennis)
- fixup productmd imports for changes with open sourcing (dennis)
- tell the scm wrapper to do an absolute import otherwise we hit a circular dep
  issue and things go wonky (dennis)
- include the dtd files in /usr/share/pungi (dennis)
- add missing ) causing a syntax error (dennis)
- fix up the productmd imports to import the function from the common module
  (dennis)
- fix up typo in getting arch for the lorax log file (dennis)

* Sat Mar 14 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.6.20150314.gitd337c34
- update the git snapshot to pick up some fixes

* Fri Mar 13 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.5.git18d4d2e
- update Requires for rename of python-productmd

* Thu Mar 12 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.4.git18d4d2e
- fix up the pungi logging by putting the arch in the log file name (dennis)
- change pypungi imports to pungi (dennis)
- spec file cleanups (dennis)

* Thu Mar 12 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.3.gita3158ec
- rename binaries (dennis)
- Add the option to pass a custom path for the multilib config files (bcl)
- Call lorax as a process not a library (bcl)
- Close child fds when using subprocess (bcl)
- fixup setup.py and MANIFEST.in to make a useable tarball (dennis)
- switch to BSD style hashes for the iso checksums (dennis)
- refactor to get better data into .treeinfo (dennis)
- Initial code merge for Pungi 4.0. (dmach)
- Initial changes for Pungi 4.0. (dmach)
- Add --nomacboot option (csieh)

* Thu Mar 12 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.2.git320724e
- update git snapshot to switch to executing lorax since it is using dnf

* Thu Mar 12 2015 Dennis Gilmore <dennis@ausil.us> - 4.0-0.1.git64b6c80
- update to the pungi 4.0 dev branch
