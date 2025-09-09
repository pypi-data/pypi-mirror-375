=====================
 slapos.recipe.build
=====================

.. contents::

The default recipe can be used to execute ad-hoc Python code at
init/install/update phases. `install` must create the path pointed to by
`location` (default is ${buildout:parts-directory}/${:_buildout_section_name_})
and any other file system change is not tracked by buildout. `install` defaults
to `update`, in which case `location` is ignored.

Example that installs software::

  [buildout]
  parts =
    script

  [script]
  recipe = slapos.recipe.build
  slapos_promise =
    directory:include
    file:share/man/man1/foo.1
    statlib:lib/libfoo.a
    statlib:lib/libfoo.la
    dynlib:bin/foo linked:libbar.so.1,libc.so.6,libfoo.so.1 rpath:${bar:location}/lib,!/lib
  url = http://host/path/foo.tar.gz
  md5sum = ...
  install =
    extract_dir = self.extract(self.download())
    self.copyTree(guessworkdir(extract_dir), location)
    ${:update}
  update =
    ...

Using the init option::

  [section-one]
  recipe = slapos.recipe.build
  init =
    import platform
    options['foo'] = platform.uname()[4]

  [section-two]
  bar = ${section-one:foo}

In case of error, a proper traceback is displayed and nothing is installed::

  >>> write(sample_buildout, 'buildout.cfg', """
  ... [buildout]
  ... parts = script
  ...
  ... [script]
  ... recipe = slapos.recipe.build
  ... install =
  ...   import os
  ...   os.mkdir(location)
  ...   print(1 / 0.) # this is an error !
  ... """)

  >>> print(system(buildout))
  Installing script.
  While:
    Installing script.
  <BLANKLINE>
  An internal error occurred due to a bug in either zc.buildout or in a
  recipe being used:
  Traceback (most recent call last):
  ...
    File "script", line 3, in <module>
      print(1 / 0.) # this is an error !
            ~~^~~~
  ZeroDivisionError: float division by zero

  >>> ls(sample_buildout, 'parts')
  <BLANKLINE>

option: environment
-------------------

Customizing environment variables can be easier with the this option.
Values are expanded with Python %-dict formatting, using ``os.environ``. The
resulting environ dict is computed on first access of ``self.environ``.
Environment variables can be either inlined::

  >>> base = """
  ... [buildout]
  ... parts = script
  ...
  ... [script]
  ... recipe = slapos.recipe.build
  ... update =
  ...   import os
  ...   os.environ["FOO"] = "1"
  ...   print("%(FOO)s %(BAR)s" % self.environ)
  ...   os.environ["FOO"] = "2"
  ...   print("%(FOO)s %(BAR)s" % self.environ)
  ... """
  >>> write(sample_buildout, 'buildout.cfg', base + """
  ... environment =
  ...   BAR=%(FOO)s:%%
  ... """)
  >>> print(system(buildout))
  Installing script.
  script: [ENV] BAR = 1:%
  1 1:%
  1 1:%

or put inside a separate section::

  >>> write(sample_buildout, 'buildout.cfg', base + """
  ... environment = env
  ... [env]
  ... BAR=%(FOO)s:%%
  ... """)
  >>> print(system(buildout))
  Uninstalling script.
  Installing script.
  script: [ENV] BAR = 1:%
  1 1:%
  1 1:%

This option works the same way in other recipes that support it, in which case
the resulting environ dict is computed at install/update.

option: shared
--------------

Boolean (``false`` by default, or ``true``), this option specifies that the
part can be installed in a shared mode. This is enabled if paths are listed in
the ``shared-part-list`` option of the ``[buildout]`` section: the location of
the part is ``<one of shared-part-list>/<part name>/<hash of options>`` and
it contains a signature file ``.buildout-shared.json``.

`install` option is required::

  >>> del MD5SUM[:]
  >>> import os
  >>> os.mkdir('shared1')
  >>> os.chmod('shared1', 0o555)
  >>> os.mkdir('shared2')
  >>> os.mkdir('shared3')
  >>> base = """
  ... [buildout]
  ... parts = script
  ... shared-part-list =
  ...   ${:directory}/shared1
  ...   ${:directory}/shared2
  ...   ${:directory}/shared3
  ...
  ... [script]
  ... recipe = slapos.recipe.build
  ... shared = true
  ... """
  >>> write(sample_buildout, 'buildout.cfg', base + """
  ... init = pass
  ... """)
  >>> print(system(buildout))
  script: will be shared at .../shared2/script/<MD5SUM:0> (needs to build)
  While:
    Installing.
    Getting section script.
    Initializing section script.
  Error: When shared=true, option 'install' must be set
  <BLANKLINE>

`update` option is incompatible::

  >>> base += """
  ... install =
  ...   import os
  ...   os.makedirs(os.path.join(location, 'foo'))
  ...   print("directory created")
  ... """
  >>> write(sample_buildout, 'buildout.cfg', base)
  >>> print(system(buildout + ' script:update=pass'))
  script: will be shared at .../shared2/script/<MD5SUM:1> (needs to build)
  While:
    Installing.
    Getting section script.
    Initializing section script.
  Error: When shared=true, option 'update' can't be set
  <BLANKLINE>

A shared part is installed in the first writable folder that is listed by
``shared-part-list``::

  >>> print(system(buildout))
  script: will be shared at .../shared2/script/<MD5SUM:2> (needs to build)
  Uninstalling script.
  Installing script.
  directory created
  <BLANKLINE>
  >>> shared = 'shared2/script/' + MD5SUM[2]
  >>> ls(shared)
  -  .buildout-shared.json
  d  foo
  <BLANKLINE>

``.buildout-shared.signature`` is only there for backward compatibility.

Uninstalling the part leaves the shared part available::

  >>> print(system(buildout + ' buildout:parts='))
  Uninstalling script.
  Section `buildout` contains unused option(s): 'shared-part-list'.
  This may be an indication for either a typo in the option's name or a bug in the used recipe.
  <BLANKLINE>
  >>> ls(shared)
  -  .buildout-shared.json
  d  foo
  <BLANKLINE>

And reinstalling is instantaneous::

  >>> print(system(buildout))
  script: shared at .../shared2/script/<MD5SUM:2> (already built)
  Installing script.
  script: shared part is already installed
  <BLANKLINE>

Setting `location` option is incompatible::

  >>> write(sample_buildout, 'buildout.cfg', base + """
  ... init =
  ...   import os
  ...   options['location'] = os.path.join(
  ...     self.buildout['buildout']['parts-directory'], 'foo')
  ... """)
  >>> print(system(buildout))
  script: will be shared at .../shared2/script/<MD5SUM:3> (needs to build)
  While:
    Installing.
    Getting section script.
    Initializing section script.
  Error: When shared=true, option 'location' can't be set
  <BLANKLINE>

option: location
----------------

If empty or unset, the value is initialized automatically according to rules
defined above (`shared` option), and before the `init` code is executed.
This way, it's possible to initialize other values of the section depending
on the actual value of location.

If not shared, the value can be customized in `init`. This is actually the
only way to empty location, which is useful if there's nothing file/directory
to track but you need to distinguish install from update::

  >>> write(sample_buildout, 'buildout.cfg', """
  ... [buildout]
  ... parts = script
  ...
  ... [script]
  ... recipe = slapos.recipe.build
  ... init =
  ...   options['location'] = ''
  ... install =
  ...   print("install")
  ... update =
  ...   print("update")
  ... """)

  >>> print(system(buildout))
  Uninstalling script.
  Installing script.
  install
  >>> print(system(buildout))
  Updating script.
  update
  >>> cat('.installed.cfg')
  [buildout]
  ...
  [script]
  __buildout_installed__ =
  __buildout_signature__ = ...

If install & update run the same code, `install` can be unset (or empty)
and you can ignore `location`.


=============================
 slapos.recipe.build:download
=============================

Simplest usage is to only specify a URL::

  >>> base = """
  ... [buildout]
  ... parts = download
  ...
  ... [download]
  ... recipe = slapos.recipe.build:download
  ... url = https://lab.nexedi.com/nexedi/slapos.recipe.build/raw/master/MANIFEST.in
  ... """
  >>> write(sample_buildout, 'buildout.cfg', base)
  >>> print(system(buildout))
  Uninstalling script.
  Installing download.
  Downloading ...
  >>> ls('parts/download')
  -  download

The file is downloaded to ``parts/<section_name>/<section_name>``.

Because the destination file may be hardlinked (e.g. download from cache
or from local file), it shall not be modified in-place without first making
sure that ``st_nlink`` is 1.

option: filename
----------------

In the part folder, the filename can be customized::

  >>> write(sample_buildout, 'buildout.cfg', base + """
  ... filename = somefile
  ... """)
  >>> print(system(buildout))
  Uninstalling download.
  Installing download.
  Downloading ...
  >>> ls('parts/download')
  -  somefile

When an MD5 checksum is not given, updating the part downloads the file again::

  >>> remove('parts/download/somefile')
  >>> print(system(buildout))
  Updating download.
  Downloading ...
  >>> ls('parts/download')
  -  somefile

option: destination
-------------------

Rather than having a file inside a part folder, a full path can be given::

  >>> write(sample_buildout, 'buildout.cfg', base + """
  ... destination = ${buildout:parts-directory}/somepath
  ... """)
  >>> print(system(buildout))
  Uninstalling download.
  Installing download.
  Downloading ...
  >>> ls('parts')
  -  somepath

option: target
--------------

In any case, path to download file is exposed by the ``target`` option::

  >>> cat('.installed.cfg')
  [buildout]
  ...
  [download]
  __buildout_installed__ = .../parts/somepath
  __buildout_signature__ = ...
  destination = .../parts/somepath
  recipe = slapos.recipe.build:download
  target = .../parts/somepath
  url = ...

option: md5sum
--------------

An MD5 checksum can be specified to check the contents::

  >>> base += """
  ... md5sum = b90c12a875df544907bc84d9c7930653
  ... """
  >>> write(sample_buildout, 'buildout.cfg', base)
  >>> print(system(buildout))
  Uninstalling download.
  Installing download.
  Downloading ...
  >>> ls('parts/download')
  -  download

In such case, updating the part does nothing::

  >>> remove('parts/download/download')
  >>> print(system(buildout))
  Updating download.
  >>> ls('parts/download')

In case of checksum mismatch::

  >>> print(system(buildout
  ... + ' download:md5sum=00000000000000000000000000000000'
  ... ))
  Uninstalling download.
  Installing download.
  Downloading ...
  While:
    Installing download.
  Error: MD5 checksum mismatch downloading '...'
  >>> ls('parts')

option: offline
---------------

Boolean option that can be specified to override `${buildout:offline}`.


option: alternate-url
---------------------

Alternate URL. If supported by Buildout, it is used as fallback if the main
URL (`url` option) fails at HTTP level.

Useful when a version of a resource can only be downloaded with a temporary
URL as long as it's the last version, and this version is then moved to a
permanent place when a newer version is released: `url` shall be the final URL
and `alternate-url` the temporary one.

option: shared
--------------

Works like the default recipe. Constraints on options are:

- ``md5sum`` option is required
- ``destination`` option is incompatible

Example::

  >>> del MD5SUM[4:] # drop added values since previous shared test
  >>> write(sample_buildout, 'buildout.cfg', base + """
  ... shared = true
  ...
  ... [buildout]
  ... shared-part-list =
  ...   ${:directory}/shared2
  ... """)
  >>> print(system(buildout))
  download: will be shared at .../shared2/download/<MD5SUM:4> (needs to build)
  Installing download.
  Downloading ...
  >>> shared = 'shared2/download/' + MD5SUM[4]
  >>> ls(shared)
  -  .buildout-shared.json
  -  download


=======================================
 slapos.recipe.build:download-unpacked
=======================================

Downloads and extracts an archive. In addition to format that setuptools is
able to extract, XZ & lzip compression are also supported if ``xzcat`` &
``lunzip`` executables are available.

By default, the archive is extracted to ``parts/<section_name>`` and a single
directory at the root of the archive is stripped::

  >>> URL = "https://lab.nexedi.com/nexedi/slapos.recipe.build/-/archive/master/slapos.recipe.build-master.tar.gz?path=slapos/recipe/build"
  >>> base = """
  ... [buildout]
  ... download-cache = download-cache
  ... parts = download
  ...
  ... [download]
  ... recipe = slapos.recipe.build:download-unpacked
  ... url = %s
  ... """ % URL
  >>> write(sample_buildout, 'buildout.cfg', base)
  >>> print(system(buildout))
  Creating directory '.../download-cache'.
  Uninstalling download.
  Installing download.
  Downloading ...
  >>> ls('parts/download')
  d  slapos

The download cache will avoid to download the same tarball several times.

option: destination
-------------------

Similar to ``download`` recipe::

  >>> write(sample_buildout, 'buildout.cfg', base + """
  ... destination = ${buildout:parts-directory}/somepath
  ... """)
  >>> print(system(buildout))
  Uninstalling download.
  Installing download.
  >>> ls('parts/somepath')
  d  slapos

option: target
--------------

Like for ``download`` recipe, the installation path of the part is exposed by
the ``target`` option::

  >>> cat('.installed.cfg')
  [buildout]
  ...
  [download]
  __buildout_installed__ = .../parts/somepath
  __buildout_signature__ = ...
  destination = .../parts/somepath
  recipe = slapos.recipe.build:download-unpacked
  target = .../parts/somepath
  url = ...

option: strip-top-level-dir
---------------------------

Stripping can be enforced::

  >>> print(system(buildout + ' download:strip-top-level-dir=true'))
  Uninstalling download.
  Installing download.
  >>> ls('parts/somepath')
  d  slapos

Or disabled::

  >>> print(system(buildout + ' download:strip-top-level-dir=false'))
  Uninstalling download.
  Installing download.
  >>> ls('parts/somepath')
  d  slapos.recipe.build-master-slapos-recipe-build

option: md5sum
--------------

An MD5 checksum can be specified to check the downloaded file, like for the
``download`` recipe. However, if unset, updating the part does nothing.

option: alternate-url
---------------------

See the ``download`` recipe.

option: environment
-------------------

Like for the default recipe, environment variables can be customized, here
for ``xzcat`` & ``lunzip`` subprocesses (e.g. PATH).

option: shared
--------------

Works like the default recipe. The only constraint on options is that
the ``destination`` option is incompatible.

Example::

  >>> del MD5SUM[5:] # drop added values since previous shared test
  >>> write(sample_buildout, 'buildout.cfg', """
  ... [buildout]
  ... download-cache = download-cache
  ... parts = download
  ... shared-part-list = ${:directory}/shared2
  ...
  ... [download]
  ... recipe = slapos.recipe.build:download-unpacked
  ... url = %s
  ... shared = true
  ... """ % URL)
  >>> print(system(buildout))
  download: will be shared at .../shared2/download/<MD5SUM:5> (needs to build)
  Uninstalling download.
  Installing download.


==============================
 slapos.recipe.build:gitclone
==============================

Checkout a git repository and its submodules by default.
Supports slapos.libnetworkcache if present, and if boolean 'use-cache' option
is true.

Examples
--------

Those examples use slapos.recipe.build repository as an example.

Simple clone
~~~~~~~~~~~~

Only `repository` parameter is required. For each buildout run,
the recipe will pick up the latest commit on the remote master branch::

  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = https://lab.nexedi.com/nexedi/slapos.recipe.build.git
  ... use-cache = true
  ... """)

This will clone the git repository in `parts/git-clone` directory.
Then let's run the buildout::

  >>> print(system(buildout))
  Uninstalling download.
  Installing git-clone.
  Cloning into '/sample-buildout/parts/git-clone'...

Let's take a look at the buildout parts directory now::

  >>> ls(sample_buildout, 'parts')
  d git-clone

When updating, it will do a "git fetch; git reset @{upstream}"::

  >>> print(system(buildout))
  Updating git-clone.
  Fetching origin
  HEAD is now at ...

Specific branch
~~~~~~~~~~~~~~~

You can specify a specific branch using `branch` option. For each
run it will take the latest commit on this remote branch::

  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = https://lab.nexedi.com/nexedi/slapos.recipe.build.git
  ... branch = build_remove_downloaded_files
  ... """)

Then let's run the buildout::

  >>> print(system(buildout))
  Uninstalling git-clone.
  Running uninstall recipe.
  Installing git-clone.
  Cloning into '/sample-buildout/parts/git-clone'...

Let's take a look at the buildout parts directory now::

  >>> ls(sample_buildout, 'parts')
  d git-clone

And let's see that current branch is "build"::

  >>> import subprocess
  >>> cd('parts', 'git-clone')
  >>> print(subprocess.check_output(['git', 'branch'], universal_newlines=True))
  * build_remove_downloaded_files

When updating, it will do a "git fetch; git reset build"::

  >>> cd(sample_buildout)
  >>> print(system(buildout))
  Updating git-clone.
  Fetching origin
  HEAD is now at ...

Specific revision
~~~~~~~~~~~~~~~~~

You can specify a specific commit hash or tag using `revision` option.
This option has priority over the "branch" option::

  >>> cd(sample_buildout)
  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = https://lab.nexedi.com/nexedi/slapos.recipe.build.git
  ... revision = 2566127
  ... """)

Then let's run the buildout::

  >>> print(system(buildout))
  Uninstalling git-clone.
  Running uninstall recipe.
  Installing git-clone.
  Cloning into '/sample-buildout/parts/git-clone'...
  HEAD is now at 2566127 ...

Let's take a look at the buildout parts directory now::

  >>> ls(sample_buildout, 'parts')
  d git-clone

And let's see that current revision is "2566127"::

  >>> import subprocess
  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print(subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], universal_newlines=True))
  2566127

When updating, it shouldn't do anything as revision is mentioned::

  >>> cd(sample_buildout)
  >>> print(system(buildout))
  Updating git-clone.

Empty revision/branch
~~~~~~~~~~~~~~~~~~~~~

Specifying an empty revision or an empty branch will make buildout
ignore those values as if it was not present at all (allowing to easily
extend an existing section specifying a branch)::

  >>> cd(sample_buildout)
  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone-with-branch]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = https://lab.nexedi.com/nexedi/slapos.recipe.build.git
  ... revision = 2566127
  ...
  ... [git-clone]
  ... <= git-clone-with-branch
  ... revision =
  ... branch = master
  ... """)

  >>> print(system(buildout))
  Uninstalling git-clone.
  Running uninstall recipe.
  Installing git-clone.
  Cloning into '/sample-buildout/parts/git-clone'...

  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print(system('git branch'))
  * master

Revision/branch priority
~~~~~~~~~~~~~~~~~~~~~~~~

If both revision and branch parameters are set, revision parameters is used
and branch parameter is ignored::

  >>> cd(sample_buildout)
  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = https://lab.nexedi.com/nexedi/slapos.recipe.build.git
  ... branch = mybranch
  ... revision = 2566127
  ... """)

  >>> print(system(buildout))
  Uninstalling git-clone.
  Running uninstall recipe.
  Installing git-clone.
  Warning: "branch" parameter with value "mybranch" is ignored. Checking out to revision 2566127...
  Cloning into '/sample-buildout/parts/git-clone'...
  HEAD is now at 2566127 ...

  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print(system('git branch'))
  * master

Setup a "develop" repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to setup a repository that will be manually altered over time for
development purposes, you need to make sure buildout will NOT alter it and NOT
erase your local modifications by specifying the "develop" flag::

  [buildout]
  parts = git-clone

  [git-clone]
  recipe = slapos.recipe.build:gitclone
  repository = https://example.net/example.git/
  develop = true

  >>> cd(sample_buildout)
  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = https://lab.nexedi.com/nexedi/slapos.recipe.build.git
  ... develop = true
  ... """)

  >>> print(system(buildout))
  Uninstalling git-clone.
  Running uninstall recipe.
  Installing git-clone.
  Cloning into '/sample-buildout/parts/git-clone'...

Buildout will then keep local modifications, instead of resetting the
repository::

  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print(system('echo foo > setup.py'))

  >>> cd(sample_buildout)
  >>> print(system(buildout))
  Updating git-clone.

  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print(system('cat setup.py'))
  foo

Then, when update occurs, nothing is done::

  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print(system('echo kept > local_change'))

  >>> print(system('git remote add broken http://git.erp5.org/repos/nowhere'))
  ...

  >>> cd(sample_buildout)
  >>> print(system(buildout))
  Updating git-clone.

  >>> cd(sample_buildout, 'parts', 'git-clone')
  >>> print(system('cat local_change'))
  kept

In case of uninstall, buildout will keep the repository directory::

  >>> cd(sample_buildout)
  >>> write(sample_buildout, 'buildout.cfg',
  ... """
  ... [buildout]
  ... parts = git-clone
  ...
  ... [git-clone]
  ... recipe = slapos.recipe.build:gitclone
  ... repository = https://lab.nexedi.com/nexedi/slapos.recipe.build.git
  ... develop = true
  ... # Triggers uninstall/install because of section signature change
  ... foo = bar
  ... """)

  >>> print(system(buildout))
  Uninstalling git-clone.
  Running uninstall recipe.
  You have uncommitted changes in /sample-buildout/parts/git-clone. This folder will be left as is.
  Installing git-clone.
  destination directory already exists.
  ...
  <BLANKLINE>

Specific git binary
~~~~~~~~~~~~~~~~~~~

The default git command is `git`, if for a any reason you don't
have git in your path, you can specify git binary path with `git-command`
option.

Ignore SSL certificate
~~~~~~~~~~~~~~~~~~~~~~

By default, when remote server use SSL protocol git checks if the SSL
certificate of the remote server is valid before executing commands.
You can force git to ignore this check using `ignore-ssl-certificate`
boolean option::

  [buildout]
  parts = git-clone

  [git-clone]
  recipe = slapos.recipe.build:gitclone
  repository = https://example.net/example.git/
  ignore-ssl-certificate = true

Ignore cloning submodules
~~~~~~~~~~~~~~~~~~~~~~~~~

By default, cloning the repository will clone its submodules also. You can force
git to ignore cloning submodules by defining `ignore-cloning-submodules` boolean
option to 'true'::

  [buildout]
  parts = git-clone

  [git-clone]
  recipe = slapos.recipe.build:gitclone
  repository = https://lab.nexedi.com/tiwariayush/test_erp5
  ignore-cloning-submodules = true

Other options
~~~~~~~~~~~~~

depth
    Clone with ``--depth=<depth>`` option. See ``git-clone`` command.

shared
    Clone with ``--shared`` option if true. See ``git-clone`` command.

sparse-checkout
    The value of the `sparse-checkout` option is written to the
    ``$GITDIR/info/sparse-checkout`` file, which is used to populate the working
    directory sparsely. See the `SPARSE CHECKOUT` section of ``git-read-tree``
    command. This feature is disabled if the value is empty or unset.

Full example
~~~~~~~~~~~~

::

  [buildout]
  parts = git-clone

  [git-binary]
  recipe = hexagonit.recipe.cmmi
  url = http://git-core.googlecode.com/files/git-1.7.12.tar.gz

  [git-clone]
  recipe = slapos.recipe.build:gitclone
  repository = http://example.net/example.git/
  git-command = ${git-binary:location}/bin/git
  revision = 0123456789abcdef


==========================
 slapos.recipe.build:vm.*
==========================

This is a set of recipes to build Virtual Machine images and execute commands
inside them. They rely on QEMU and OpenSSH: executables are found via the PATH
environment variable. They do nothing on update.

Common options
--------------

location
    Folder where the recipe stores any produced file.
    Default: ${buildout:parts-directory}/<section_name>

environment
    Extra environment to spawn executables. See the default recipe.

mem
    Python expression evaluating to an integer that specifies the
    RAM size in MB for the VM.

smp
    Number of CPUs for the VM. Default: 1

Example
~~~~~~~

::

  [vm-run-environment]
  PATH = ${openssh:location}/bin:${qemu:location}/bin:%(PATH)s

  [vm-run-base]
  recipe = slapos.recipe.build:vm.run
  environment = vm-run-environment
  mem = 256 * (${:smp} + 1)
  smp = 4

slapos.recipe.build:vm.install-debian
-------------------------------------

Install Debian from an ISO image. Additional required binaries:

- ``7z`` (from 7zip), to extract kernel/initrd from the ISO;
- ``file``, which is used to test that the VM image is bootable.

Currently, it only produces `raw` images, in `discard` mode (see ``-drive``
QEMU option): combined the use of ``discard`` mount option, this minimizes
the used space on disk.

Options
~~~~~~~

location
    Produced files: ``<dist>.img`` (1 for each token of `dists`), ``passwd``
    and optionally ``ssh.key``

arch
    QEMU architecture (the recipe runs the ``qemu-system-<arch>`` executable).
    It is also used to select the ISO in the sections refered by `dists`.
    Default to host architecture.

dists
    List of VMs to build: each token refers to a buildout section name that
    describes the ISOs to use. See `ISO sections`_ below.
    Tokens can't contain `'.'` characters.

size
    Size of the VM image. This must be an integer, optionally followed by a
    IEC or SI suffix.

mem
    Default: 384

[<dist>/]preseed.<preseed>
    Set the <preseed> value for the installation. The recipe has many default
    preseed values: you can see the list in the ``InstallDebianRecipe.preseed``
    class attribute (file ``slapos/recipe/vm.py``). Aliases are recognized
    (but the recipe includes a mapping that may be out-of-date.).
    Any value except ``passwd/*`` can optionally be prefixed so that they only
    apply for a particular VM.

[<dist>/]debconf.<owner>
    List of debconf value for <owner> (usually a package name),
    each line with 2 whitespace-separated parts: <key> <value>.
    Like for preseed.* values, they can be specific to <dist>.

late-command
    Shell commands to execute at the end of the installation. They are run
    inside the target system. This is a reliable alternative to the
    ``preseed.preseed/late_command`` option. The ``DIST`` shell variable is
    set to the VM being built.

packages
    Extra packages to install.
    Like for `late-command`, do not use ``preseed.pkgsel/include``.
    If you want to install packages only for some specific <dist>, you can do
    it in ``late-command``, by testing ``$DIST`` and using
    ``apt-get install -y``.

vm.run
    Boolean value that is `true` by default, to configure the VM for use with
    the `slapos.recipe.build:vm.run`_ recipe:

    - make sure that the `ssh` and `sudo` packages are installed
    - an SSH key is automatically created with ``ssh-keygen``, and it can be
      used to connect as `root`

ISO sections
~~~~~~~~~~~~

<arch>.iso
    Name of the section that provides the ISO image, for example by downloading
    it. This section must define 2 options: `location` is the folder
    containing the ISO, and `filename` is the file name of the ISO.

<arch>.kernel
    Path to kernel image inside the ISO.

<arch>.initrd
    Path to initrd image inside the ISO.

User setup
~~~~~~~~~~

By default, there's no normal user created. Another rule is that a random
password is automatically generated if there is no password specified.

You have nothing to do if you only plan to use the VM with `vm.run`.

For more information about the ``passwd/*`` preseed values, you can look at
the ``user-setup-udeb`` package at
https://anonscm.debian.org/cgit/d-i/user-setup.git/tree/
and in particular the ``user-setup-ask`` and ``user-setup-apply`` scripts.

Example
~~~~~~~

::

  [vm-install-environment]
  # vm-run-environment refers to the section in common options
  PATH = ${file:location}/bin:${p7zip:location}/bin:${vm-run-environment:PATH}

  [vm-debian]
  recipe = slapos.recipe.build:vm.install-debian
  environment = vm-install-environment
  dists = debian-jessie debian-stretch
  size = 2Gi
  late-command =
  # rdnssd causes too much trouble with QEMU 2.7, because the latter acts as
  # a DNS proxy on both IPv4 and IPv6 without translating queries to what the
  # host supports.
    dpkg -P rdnssd
  debconf.debconf =
    debconf/frontend noninteractive
    debconf/priority critical
  # minimal size
  preseed.apt-setup/enable-source-repositories = false
  preseed.recommends = false
  preseed.tasks =

  [debian-jessie]
  x86_64.iso = debian-amd64-netinst.iso
  x86_64.kernel = install.amd/vmlinuz
  x86_64.initrd = install.amd/initrd.gz

  [debian-stretch]
  <= debian-jessie
  x86_64.iso = debian-amd64-testing-netinst.iso

  [debian-amd64-netinst.iso]
  ...

slapos.recipe.build:vm.run
--------------------------

Execute shell commands inside a VM, in snapshot mode (the VM image is not
modified).

``${buildout:directory}`` is always mounted as `/mnt/buildout` inside the VM.

Mount points use the 9p file-system. Make sure that:

- QEMU is built with --enable-virtfs;
- the VM runs a kernel that is recent enough (Debian Squeeze kernel 2.6.32 is
  known to fail, and you'd have to use the one from squeeze-backports).

Options
~~~~~~~

location
    Folder where to store any produce file. Inside the guest, it is pointed to
    by the PARTDIR environment variable. It is also used as temporary storage
    for changes to the VM image.

vm
    Folder containing the VM images and the `ssh.key`` file. See the `location`
    option of the `vm.install-*` recipes.

dist
    VM image to use inside the `vm` folder.

drives
    Extra drives. Each line is passed with -drive

commands
    List of <command> options, each one being a shell script to execute via
    SSH. They are processed in sequence. This is usually only required if you
    want to reboot the VM. Default: command

mount.<name>
    Extra mount point. The value is a host folder that is mounted as
    ``/mnt/<name>``.

stop-ssh
    Tell `reboot` function how to stop SSH (see Helpers_).
    Default: systemctl stop ssh

user
    Execute commands with this user. The value can be ``root``. By default,
    it is empty and it means that:

    - a ``slapos`` user is created with the same uid/gid than the user using
      this recipe on the host, which can help accessing mount points;
    - sudo must be installed and the created user is allowed to become root
      without password.

    In any case, SSH connects as root.

wait-ssh
    Time to wait for (re)boot. The recipe fails if it can't connect to the SSH
    server after this number of seconds. Default: 60

Helpers
~~~~~~~

Before commands are executed, all `mount.<name>` are mounted
and a few helpers are set to make scripting easier.

set -e
    This is done before anything else, to make buildout abort if any untested
    command fails.

reboot
    Function to safely reboot the guest. The next command in `commands` will be
    executed once the SSH server is back.

map <host_path>
    Function to map a folder inside ``${buildout:directory}``.

PARTDIR
    Folder where to store any produced file. Inside the guest, it actually
    maps to `location` on the host. This is useful because you can't write
    ``PARTDIR=`map ${:location}``` if you don't explicitly set `location`.

Example
~~~~~~~

::

  [vm-run-base]
  # extends above example in common options
  vm = ${vm-debian:location}
  dist = debian-jessie

  [vm-debian]
  # extends above example in vm.install-debian
  packages += build-essential devscripts equivs git

  [userhosts-repository]
  recipe = slapos.recipe.build:gitclone
  repository = https://lab.nexedi.com/nexedi/userhosts.git
  # we don't need a working directory on the host
  sparse-checkout = /.gitignore

  [build-userhosts-map]
  <= vm-run-base
  repository = `map ${userhosts-repository:location}`
  command =
    git clone -s ${:repository} userhosts
    cd userhosts
    mk-build-deps -irs sudo -t 'apt-get -y'
    dpkg-buildpackage -uc -b -jauto
    cd ..
    mv *.changes *.deb $PARTDIR

  # Alternate way, which is required if [userhosts-repository] is extended
  # in such way that the repository is outside ${buildout:directory}.
  [build-userhosts-mount]
  <= build-userhosts-map
  mount.userhosts = ${userhosts-repository:location}
  repository = /mnt/userhosts

  [test-reboot]
  <= vm-run-base
  commands = hello world
  hello =
    uptime -s
    echo Hello ...
    reboot
  world =
    uptime -s
    echo ... world!


================================
 slapos.recipe.build:mkdirectory
================================

mkdirectory loops on its options and create the directory joined

Example that create 2 directories foo and bar::

  [buildout]
  parts =
    directory

  [directory]
  recipe = slapos.recipe.build:mkdirectory
  foo = ${buildout:directory}/foo
  bar = ${buildout:directory}/sub/dir/bar

Use a slash ``/`` as directory separator. Don't use system dependent separator.
The slash will be parsed and replace by the operating system right separator.

Only use relative directory to the buildout root directory.

The created directory won't be added to path list.
