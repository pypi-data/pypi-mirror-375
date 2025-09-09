(building-pyzmq)=

# Building pyzmq

pyzmq publishes around a hundred wheels for each release, so hopefully very few folks need to build pyzmq from source.

pyzmq 26 has a whole new build system using CMake via [scikit-build-core].

~all options can be specified via environment variables with the same name, in order to play nicely with pip.

## Installing from source

When compiling pyzmq, it is generally recommended that zeromq be installed separately, via homebrew, apt, yum, etc:

```bash
# Debian-based
sudo apt-get install libzmq3-dev

# Fedora-based
sudo yum install libzmq3-devel

# homebrew
brew install zeromq
```

You can install pyzmq from source with `pip` by telling it `--no-binary pyzmq`:

```
python3 -m pip install pyzmq --no-binary pyzmq
```

or an editable install from a local checkout:

```
python3 -m pip install -e .
```

Building from source uses CMake via scikit-build-core.
CMake >= 3.28 is required.
scikit-build-core will attempt to download cmake if a satisfactory version is not found.

## Examples

First, some quick examples of influencing pyzmq's build.

Build a wheel against already-installed libzmq:

```bash
export ZMQ_PREFIX=/usr/local
python3 -m pip install pyzmq --no-binary pyzmq
```

Force building bundled libzmq with the draft API:

```bash
export ZMQ_PREFIX=bundled
export ZMQ_BUILD_DRAFT=1
python3 -m pip install pyzmq --no-binary pyzmq
```

## Finding libzmq

First, pyzmq tries to find libzmq to link against it.

pyzmq will first try to search using standard CMake methods, followed by pkg-config.

You can pass through arguments to the build system via the CMAKE_ARGS environment variable.
e.g.

```bash
CMAKE_ARGS="-DCMAKE_PREFIX_PATH=/path/to/something"
```

or

```bash
PKG_CONFIG_PATH="$PREFIX/lib/pkgconfig"
```

If pyzmq doesn't find your libzmq via the default search, or you want to skip the search and tell pyzmq exactly where to look, set ZMQ_PREFIX (this skips cmake/pkgconfig entirely):

```bash
ZMQ_PREFIX=/path/to/zmq  # should contain 'include', 'lib', etc.
```

You may also need to add:

```bash
export LDFLAGS="-Wl,-rpath,${ZMQ_PREFIX}/lib"
```

to make sure that your libzmq is found at _runtime_.

### Disabling bundled build fallback

You may want to keep the default search,
which will import targets from CMake, pkg-config, etc.,
but make _sure_ libzmq is found.

To do this, set PYZMQ_NO_BUNDLE.
If you set only this, pyzmq will still search via standard means, but _fail_ if libzmq is not found, rather than falling back on the bundled static library.

```bash
-DPYZMQ_NO_BUNDLE=ON
```

## Building bundled libzmq

If pyzmq doesn't find a libzmq to link to, it will fall back on building libzmq itself.
You can tell pyzmq to skip searching for libzmq and always build the bundled version with `ZMQ_PREFIX=bundled`.

When building a bundled libzmq, pyzmq downloads and builds libzmq and libsodium as static libraries.
These static libraries are then linked to by the pyzmq extension and discarded.

Bundled libzmq is supported on a best-effort basis, and isn't expected to work everywhere with zero configuration.
If you have trouble building bundled libzmq, please do [report it](https://github.com/zeromq/pyzmq/issues).
But the best solution is usually to install libzmq yourself via the appropriate mechanism _before_ building pyzmq.

### Building bundled libsodium

libsodium is built first, with `configure` most places:

```bash
./configure --enable-static --disable-shared --with-pic
make
make install
```

or `msbuild` on Windows:

```bat
msbuild /m /v:n /p:Configuration=StaticRelease /pPlatform=x64 builds/msvc/vs2022/libsodium.sln
```

You can _add_ arguments to configure with a semicolon-separated list, by specifying `PYZMQ_LIBSODIUM_CONFIGURE_ARGS` variable:

```bash
PYZMQ_LIBSODIUM_CONFIGURE_ARGS="--without-pthread --enable-minimal"
# or
CMAKE_ARGS="-DPYZMQ_LIBSODIUM_CONFIGURE_ARGS=--without-pthread;--enable-minimal"
```

and `PYZMQ_LIBSODIUM_MSBUILD_ARGS` on Windows:

```bash
PYZMQ_LIBSODIUM_MSBUILD_ARGS="/something /else"
# or
CMAKE_ARGS="-DPYZMQ_LIBSODIUM_MSBUILD_ARGS=/something;/else"
```

```{note}
command-line arguments from environment variables are expected to be space-separated (`-a -b`),
while CMake variables are expected to be CMake lists (semicolon-separated) (`-a;-b`).
```

### Building bundled libzmq

The `libzmq-static` static library target is imported via [FetchContent], which means the libzmq CMake build is used on all platforms.
This means that configuring the build of libzmq itself is done directly via CMAKE_ARGS,
and all of libzmq's cmake flags should be available.
See [libzmq's install docs](https://github.com/zeromq/libzmq/blob/HEAD/INSTALL) for more.

For example, to enable OpenPGM:

```bash
CMAKE_ARGS="-DWITH_OPENPGM=ON"
```

### Specifying bundled versions

You can specify which version of libsodium/libzmq to bundle with:

```
-DPYZMQ_LIBZMQ_VERSION=4.3.5
-DPYZMQ_LIBSODIUM_VERSION=1.0.20
```

or the specify the full URL to download (e.g. to test bundling an unreleased version):

```
-DPYZMQ_LIBZMQ_URL="https://github.com/zeromq/libzmq/releases/download/v4.3.5/zeromq-4.3.5.tar.gz"
-DPYZMQ_LIBSODIUM_URL="https://download.libsodium.org/libsodium/releases/libsodium-1.0.20.tar.gz"
```

```{warning}
Only the default versions are supported and there is no guarantee that bundling versions will work, but you are welcome to try!
```

### Windows notes

I'm not at all confident in building things on Windows, but so far things work in CI.
I've done my best to expose options to allow users to override things if they don't work,
but it's not really meant to be customizable; it's meant to allow you to workaround my mistakes without waiting for a release.

libsodium ships several solutions for msbuild, identified by `/builds/msvc/vs{year}/libsodium.sln`.
pyzmq tries to guess which solution to use based on the MSVC_VERSION CMake variable,
but you can skip the guess by specifying `-D PYZMQ_LIBSODIUM_VS_VERSION=2022` to explicitly use the vs2022 solution.

## Passing arguments

pyzmq has a few CMake options to influence the build. All options are settable as environment variables, as well.
Other than `ZMQ_PREFIX` and `ZMQ_DRAFT_API` which have been around forever, environment variables for building pyzmq have the prefix `PYZMQ_`.

The `_ARGS` variables that are meant to pass-through command-line strings accept standard command-line format from environment, or semicolon-separated lists when specified directly to cmake.

So

```bash
export ZMQ_PREFIX=bundled
export PYZMQ_LIBZMQ_VERSION=4.3.4
export PYZMQ_LIBSODIUM_CONFIGURE_ARGS=--disable-pie --minimal

python3 -m build .
```

is equivalent to

```bash
export CMAKE_ARGS="-DZMQ_PREFIX=bundled -DPYZMQ_LIBZMQ_VERSION=4.3.4 -DPYZMQ_LIBSODIUM_CONFIGURE_ARGS=--disable-pie;--minimal"
python3 -m build .
```

Most cmake options can be seen below:

% regenerate with python tools/collect_cmake.py

<details>
<summary>

`cmake -LH` output for pyzmq, which can be passed via `CMAKE_ARGS`.
Most of these can also be specified via environment variables.

</summary>

```bash
# Path to a program.
CYTHON:FILEPATH=$PREFIX/bin/cython

# semicolon-separated list of arguments to pass to ./configure for bundled libsodium
PYZMQ_LIBSODIUM_CONFIGURE_ARGS:STRING=

# semicolon-separated list of arguments to pass to msbuild for bundled libsodium
PYZMQ_LIBSODIUM_MSBUILD_ARGS:STRING=

# full URL to download bundled libsodium
PYZMQ_LIBSODIUM_URL:STRING=

# libsodium version when bundling
PYZMQ_LIBSODIUM_VERSION:STRING=1.0.20

# Visual studio solution version for bundled libsodium (default: detect from MSVC_VERSION)
PYZMQ_LIBSODIUM_VS_VERSION:STRING=

# full URL to download bundled libzmq
PYZMQ_LIBZMQ_URL:STRING=

# libzmq version when bundling
PYZMQ_LIBZMQ_VERSION:STRING=4.3.5

# Prohibit building bundled libzmq. Useful for repackaging, to allow default search for libzmq and requiring it to succeed.
PYZMQ_NO_BUNDLE:BOOL=OFF

# whether to build the libzmq draft API
ZMQ_DRAFT_API:BOOL=OFF

# libzmq installation prefix or 'bundled'
ZMQ_PREFIX:STRING=auto

# The directory containing a CMake configuration file for ZeroMQ.
ZeroMQ_DIR:PATH=$PREFIX/lib/cmake/ZeroMQ
```

</details>

<details>
<summary>

`cmake -LH` output for libzmq, showing additional arguments
that can be passed to CMAKE_ARGS when building bundled libzmq

</summary>

```bash
# Path to a program.
A2X_EXECUTABLE:FILEPATH=A2X_EXECUTABLE-NOTFOUND

# Choose polling system for zmq_poll(er)_*. valid values are
# poll or select [default=poll unless POLLER=select]
API_POLLER:STRING=

# Whether or not to build the shared object
BUILD_SHARED:BOOL=ON

# Whether or not to build the static archive
BUILD_STATIC:BOOL=ON

# Whether or not to build the tests
BUILD_TESTS:BOOL=ON

# Build with static analysis(make take very long)
ENABLE_ANALYSIS:BOOL=OFF

# Build with address sanitizer
ENABLE_ASAN:BOOL=OFF

# Run tests that require sudo and capsh (for cap_net_admin)
ENABLE_CAPSH:BOOL=OFF

# Include Clang
ENABLE_CLANG:BOOL=ON

# Enables cpack rules
ENABLE_CPACK:BOOL=ON

# Enable CURVE security
ENABLE_CURVE:BOOL=OFF

# Build and install draft classes and methods
ENABLE_DRAFTS:BOOL=ON

# Enable/disable eventfd
ENABLE_EVENTFD:BOOL=OFF

# Build using compiler intrinsics for atomic ops
ENABLE_INTRINSICS:BOOL=OFF

# Automatically close libsodium randombytes. Not threadsafe without getrandom()
ENABLE_LIBSODIUM_RANDOMBYTES_CLOSE:BOOL=ON

# Build with empty ZMQ_EXPORT macro, bypassing platform-based automated detection
ENABLE_NO_EXPORT:BOOL=OFF

# Enable precompiled headers, if possible
ENABLE_PRECOMPILED:BOOL=ON

# Use radix tree implementation to manage subscriptions
ENABLE_RADIX_TREE:BOOL=ON

# Build with thread sanitizer
ENABLE_TSAN:BOOL=OFF

# Build with undefined behavior sanitizer
ENABLE_UBSAN:BOOL=OFF

# Enable WebSocket transport
ENABLE_WS:BOOL=ON

#
LIBZMQ_PEDANTIC:BOOL=ON

#
LIBZMQ_WERROR:BOOL=OFF

# Choose polling system for I/O threads. valid values are
# kqueue, epoll, devpoll, pollset, poll or select [default=autodetect]
POLLER:STRING=

# Path to a library.
RT_LIBRARY:FILEPATH=RT_LIBRARY-NOTFOUND

# Build html docs
WITH_DOCS:BOOL=ON

# Use libbsd instead of builtin strlcpy
WITH_LIBBSD:BOOL=ON

# Use libsodium
WITH_LIBSODIUM:BOOL=OFF

# Use static libsodium library
WITH_LIBSODIUM_STATIC:BOOL=OFF

# Enable militant assertions
WITH_MILITANT:BOOL=OFF

# Build with support for NORM
WITH_NORM:BOOL=OFF

# Use NSS instead of builtin sha1
WITH_NSS:BOOL=OFF

# Build with support for OpenPGM
WITH_OPENPGM:BOOL=OFF

# Build with perf-tools
WITH_PERF_TOOL:BOOL=ON

# Use TLS for WSS support
WITH_TLS:BOOL=ON

# Build with support for VMware VMCI socket
WITH_VMCI:BOOL=OFF

# install path for ZeroMQConfig.cmake
ZEROMQ_CMAKECONFIG_INSTALL_DIR:STRING=lib/cmake/ZeroMQ

# ZeroMQ library
ZEROMQ_LIBRARY:STRING=libzmq

# Build as OS X framework
ZMQ_BUILD_FRAMEWORK:BOOL=OFF

# Build the tests for ZeroMQ
ZMQ_BUILD_TESTS:BOOL=ON

# Choose condition_variable_t implementation. Valid values are
# stl11, win32api, pthreads, none [default=autodetect]
ZMQ_CV_IMPL:STRING=stl11

# Output zmq library base name
ZMQ_OUTPUT_BASENAME:STRING=zmq
```

</details>

## Cross-compiling pyzmq

Cross-compiling Python extensions is tricky!

To cross-compile pyzmq, in general you need:

- Python built for the 'build' machine
- Python built for the 'host' machine (identical version)
- cross-compiling toolchain (e.g. `aarch64-linux-gnu-gcc`)
- Python setup to cross-compile ([crossenv] is the popular tool these days, and includes lots of info for cross-compiling for Python, but pyzmq makes no assumptions)

It is probably a good idea to build libzmq/libsodium separately and link them with ZMQ_PREFIX,
as cross-compiling bundled libzmq is not guaranteed to work.

I don't have a lot of experience cross-compiling,
but we have two example Dockerfiles that appear to work to cross-compile pyzmq.
These aren't official or supported, but they appear to work and may be useful as reference to get you started.

<details>

<summary>Dockerfile for building x86_64 on aarch64</summary>

```{literalinclude} cross.Dockerfile
---
language: Dockerfile
---
```

</details>

<details>

<summary>Dockerfile for building for android-aarch64 on x86_64</summary>

```{literalinclude} cross-android.Dockerfile
---
language: Dockerfile
---
```

</details>

[crossenv]: https://crossenv.readthedocs.io/
[fetchcontent]: https://cmake.org/cmake/help/latest/module/FetchContent.html
[scikit-build-core]: https://scikit-build-core.readthedocs.io
