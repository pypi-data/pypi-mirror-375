=========
 Changes
=========

0.61 (2025-09-08)
-----------------

- vm: add support for Python 3
- vm: fix install of recent Debian
- vm: use lowmem/low=note instead of fb=false

0.60 (2025-06-13)
-----------------

- shared: use the first writable shared directory for the efficiency
- fix make_read_only

0.59 (2025-05-12)
-----------------

- setup.py: add six as explicit dependency

0.58 (2025-01-27)
-----------------

- mkdirectory: move this recipe from slapos.cookbook

0.57 (2024-03-19)
-----------------

- move non-trivial code from namespace __init__.py

0.56 (2022-11-10)
-----------------

- drop slapos.recipe.build:npm
- gitclone: support git 2.38.1 when using submodules

0.55 (2022-06-07)
-----------------

- downloadunpacked: fix extraction of symlinks when using an external
  decompressor

0.54 (2022-02-11)
-----------------

- default: allow 'install' to install no file/dir
- default: fix case where 'location' does not contain any directory separator

0.53 (2022-01-11)
-----------------

- default: execute 'init' after the 'location' option is automatically set.
- Drop multiarch support: see new 'multiarch' value in conditional configuration
  sections since SlapOS fork of zc.buildout version 2.7.1+slapos015.
- default: make 'self.download' use url&md5sum options if called without url.
- default: add support for xz/lz archives to 'self.extract'.
- download*: new 'offline' option to override ${buildout:offline}.

0.52 (2021-12-10)
-----------------

* default, download-unpacked: improve multiarch support
  (for the default recipe, multiarch() replaces guessPlatform()).
* shared: fix trailing whitespace in signature file on Python 2.

0.51 (2021-12-08)
-----------------

* download: only take basename of 'filename' when the latter is used to calculate destination path
* download: drop 'mode' option
* gitclone: new 'depth' option

0.50 (2021-11-29)
-----------------

* download-unpacked: drop unused `environment-section` option

0.49 (2021-10-04)
-----------------

* download-unpacked: fix `strip-top-level-dir` if unset
  and nothing should be stripped.
* Work around circular imports inside slapos.buildout.
* default: preserve symlinks in `copyTree()` & `extract()`.
* default: fix error handling in `pipeCommand()`.
* shared: change JSON serialization of signature to indent with 2 spaces
  (instead of 0) and to save non-ascii chars as utf-8 (rather than escaped).

0.48 (2021-09-25)
-----------------

* New API to share parts:

  - new `Shared` class that should be used by recipes to make a part shared;
  - the signature file is in JSON format and
    it is named `.buildout-shared.signature`.

* download*: fix `shared=true` using new `Shared` class.
* download*: new `alternate-url` option.
* download-unpacked: decompress directly within target folder to avoid copies
  accross different file systems.
* default: add support for shared parts.
* download-unpacked: `environment-section` option is deprecated.
* download-unpacked: `extract-directory` option is dropped.
* For some boolean options, the value must be either 'false' or 'true'.

0.47 (2021-07-26)
-----------------

* default: Include current line in the tracebacks on error

0.46 (2020-09-11)
-----------------

* gitclone: let errors on update propagate

0.45 (2020-04-20)
-----------------

* default: only set default 'location' option if there's an install script

0.44 (2020-03-20)
-----------------

This release contains several backward-incompatible changes.

* default: remove useless globals & 'self' methods
* default: 'script' renamed to 'install', new 'update', clean up globals/locals
* default: remove 'format' option
* default: check that 'install' script creates 'location'
* default: do not warn if slapos_promise is not set
* default: update doc

0.43 (2020-02-28)
-----------------

* default: new 'init' option.
* default: do not strip 'url', 'md5sum', 'path' automatically
  (these options are not used by the recipe).
* default: drop workaround for script starting with indentation.
* shared: don't touch symlink targets when making read-only recursively.
* vm: no empty floppy/cdrom drives.
* vm: always use GPT.
* vm: switch to XFS.

0.42 (2019-10-16)
-----------------

* vm: use virtio-rng with host's /dev/urandom to fix boot delays with recent OS
* vm.run: use -cpu host
* vm.run: new 'drives' option

0.41 (2019-06-19)
-----------------

* gitclone: add support for submodules, enabled by default.

0.40 (2018-10-29)
-----------------

* shared: fix signature test under Python 3.

0.39 (2018-10-26)
-----------------

* More Py3 fixes.

0.38 (2018-09-13)
-----------------

* download: fix regression in 0.37 breaking support for Python 3

0.37 (2018-08-27)
-----------------

* Drop slapos.recipe.build:cpan, use ``perl-CPAN-package`` macro instead.
* downloadunpacked, download: add shared feature.


0.36 (2017-06-29)
-----------------

* Do not depend on slapos.libnetworkcache, which is optional.

0.35 (2017-06-21)
-----------------

* download: fix default permission of installed files.
* download: do nothing on update if we're sure that the source hasn't changed.

0.34 (2017-06-05)
-----------------

* downloadunpacked: make compatible with Python 2.6, now that
  slapos.recipe.cmmi uses it, and we still want to bootstrap
  SlapOS on old OS.
* downloadunpacked: fix clean up of temporary files
* gitclone: assume unclean on uninstall when git-executable cannot be found.
* Add support for Python 3, at least to bootstrap SlapOS from Python 3.

0.33 (2017-04-07)
-----------------

* download, downloadunpacked: remove downloaded files after unpacking.

0.32 (2017-03-08)
-----------------

* downloadunpacked: fix an issue in extracting hard links.

0.31 (2017-03-08)
-----------------

* downloadunpacked: support .xz and .lz archives.
* downloadunpacked: extract symlinks in a tar archive as symlinks.

0.30 (2017-02-23)
-----------------

* script option: fix IndentationError with buildout 2, if some lines are indented.

0.28 (2016-11-08)
-----------------

* vm.run: workaround for old versions of mount

* vm.install-debian:

  - No more limit on the number of preseed parameters, by placing a preseed.cfg
    file inside the initrd, instead of passing them all via the command line.
    The kernel is usually limited to 32 parameters and it panics when there are
    too many.
  - Dist-specific options.
  - Recognize preseed aliases.
  - late-command is run with '/bin/sh -e' and it must exit with EX_OK (0),
    otherwise the installer stops.

0.27 (2016-10-30)
-----------------

* vm: change how commands can be easily run with a normal user account on the guest

0.26 (2016-10-29)
-----------------

* gitclone: new 'shared' option.
* vm.install-debian: workaround for spurious "No network interfaces detected"
* vm: use a normal user account by default

0.25 (2016-10-23)
-----------------

* gitclone: new 'sparse-checkout' option.
* New vm.* recipes to build VM images and execute commands inside them.

0.24 (2016-10-10)
-----------------

Improvements to default recipe:

* Remove `location` if `script` fails.
* If `location` already exists at install, warn instead of failing.
* `location` can be a file. Similarly, the use of `self.cleanup_dir_list` &
  `self.cleanup_file_list` in `script` is deprecated in favor of
  `self.cleanup_list`.

0.23 (2015-10-22)
-----------------

* gitclone: We don't have to fetch, if revision is already present in local git repository

0.22 (2015-10-19)
-----------------

* Support zc.buildout 2.

0.21 (2015-04-10)
-----------------

* Restore support for build scripts

0.20 (2015-03-06)
-----------------

* rerelease because "missing release" was cached in shacache

0.19 (2015-03-06)
-----------------

* gitclone: REVERT "when update(), if repository has local changes, don't do anything but warn user."
  With this commit, test nodes would not update the repository if it has local changes (eg. from pyc files)


0.18 (2015-02-05)
-----------------

* gitclone: don't do anything at update() if develop=true.
* gitclone: develop is false by default.
* gitclone: don't raise when uninstall if location does not exist.
* gitclone: when update(), if repository has local changes, don't do anything but warn user.

0.17 (2015-02-02)
-----------------

* gitclone: keep local changes when there is an error during update

0.16 (2015-01-12)
-----------------

* gitclone: fix option name for git-executable

0.15 (2014-11-28)
-----------------

* build: Fixup! Remove downloaded files at the end.

0.14 (2014-10-23)
-----------------

* build: Remove downloaded files at the end.

0.13 (2014-10-08)
-----------------

* gitclone: do not delete the working copy if develop is set.
* gitclone: revision has priority over branch.
* gitclone: empty parameter equals no parameter.

0.12 (2013-09-05)
-----------------

* gitclone: Do not upload to cache by default. 'use-cache' option replaces 'forbid-download-cache' and must be explicitely set in order to use cache.
* gitclone: Do not cache working copy, which just duplicate `.git` folder.
* gitclone: do not force to use 'master' branch when not specified.
* gitclone: add git 'ignore-ssl-certificate' option.
* gitclone: if directory is no longer present, install, never update.

0.11.6 (2013-02-25)
-------------------

* Cleanup pyc and pyo files when updating git repository
  [Sebastien Robin]

0.11.5 (2012-10-01)
-------------------

* Use @{upstream} git magic value, allow to fix update bugs.
  [Cedric de Saint Martin]

0.11.4 (2012-09-11)
-------------------

* libnetworkcache is added back as a dependency. gitclone has no sense without
  it in SlapOS context. [Cedric de Saint Martin]

0.11.3 (2012-09-10)
-------------------

* Removed explicit dependency of slapos.libnetworkcache. If not present, it
  will gracefully degrade. [Cedric de Saint Martin]

0.11.2 (2012-09-05)
-------------------

* Add location to Buildout "options" dict, so that it is exposed to other
  Buildout parts. [Cedric de Saint Martin]

0.11.1 (2012-09-05)
-------------------

* Add forbid-download-cache parameter, forbidding to fetch git from cache.
  [Cedric de Saint Martin]
* Sanitize instance attributes. [Cedric de Saint Martin]

0.11 (2012-09-04)
-----------------

* Add slapos.recipe.build:gitclone recipe. [Cedric de Saint Martin]

0.10.2 (2012-08-02)
-------------------

* Update manifest to include readme.rst [Cedric de Saint Martin]

0.10.1 (2012-08-02)
-------------------

* Minor fix in ReST documentation formatting. [Cedric de Saint Martin]

0.10 (2012-07-02)
-----------------

* Add ``format = yes|no`` option. [Antoine Catton]

0.9 (2012-06-07)
----------------

* Revert accidental release about upcoming version of slapos.recipe.build

0.8 (2012-06-07)
----------------

* Add support for "path" argument [Cedric de Saint Martin]
* Cleanup of download entry point [Vincent Pelletier]
* Add npm and cpan entry points [Cedric de Saint Martin]

0.7 (2011-11-8)
---------------

* Generic: Remove directory when needed, and only if it is wanted.
  [Cedric de Saint Martin]
* Add slapos.recipe.downloadunpacked script [Alain Takoudjou]

0.6 (2011-09-08)
----------------

* Cmmi: Support more compatibility with other recipes to build, especially
  hexagonit.recipe.cmmi. [Łukasz Nowak]
* Generic: A lot of small improvements (like supporting values with = in
  environment) [Łukasz Nowak]
* Generic: Use shlex to parse some options. [Antoine Catton]
* Generic: Fix patch, it was not working, as not using stdin. [Antoine Catton]

0.5 (2011-09-06)
----------------

* Download: Expose location too for compatiblity. [Łukasz Nowak]

0.4 (2011-09-06)
----------------

* Cmmi: Provide more features to control build process. [Łukasz Nowak]

0.3 (2011-09-05)
----------------

* Provide slapos.recipe.build:download utility. [Łukasz Nowak]

0.2 (2011-09-05)
----------------

* Bugfix: Support buildout's download cache during downlading. [Łukasz Nowak]
* Bugfix: Honour correctly passed md5sum to download method. [Łukasz Nowak]
* Feature: Utility methods pipeCommand and failIfPathExists. [Łukasz Nowak]
* Bugfix: Rename promisee to promise. [Łukasz Nowak]
* Feature: Just warn in case of lack of promise. [Łukasz Nowak]

0.1 (2011-08-26)
----------------

* Add copyTree method to recursively copy [Cedric de Saint Martin]
* add guessPlatform function to guess architecture in case of
  multi-architecture installation [Cedric de Saint Martin]
