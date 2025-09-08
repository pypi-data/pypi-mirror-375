# expressive

A library for quickly applying symbolic expressions to NumPy arrays

Enabling callers to front-load and validate sample data, developers can move the runtime cost of Numba's JIT to applications' initial loading and avoid `exec` during user-interactable runtime (otherwise needed when "lambdifying" SymPy expressions) .. additionally, Expressive can identify and handle indexing (`x[i]`, `x[i-1]`) during input parsing, which allows expressions to have offset data references, which can be annoying and isn't automatically handled by SymPy's `parse_expr()` et al.

Inspired in part by this Stack Overflow Question [Using numba.autojit on a lambdify'd sympy expression](https://stackoverflow.com/questions/22793601/using-numba-autojit-on-a-lambdifyd-sympy-expression)

Internally this relies heavily on [SymPy](https://www.sympy.org), [NumPy](https://numpy.org), and [Numba](https://numba.pydata.org), along with [coverage.py](https://coverage.readthedocs.io) to maintain its 100% coverage test suite and [MathJax](https://www.mathjax.org) ([jsDelivr CDN](https://www.jsdelivr.com)) for LaTeX rendering in Notebooks

#### major features

* feedback and result seeding via result array passing and referencing `a[n] + result[n-1]`
* automatic indexer detection and offsetting `a[i+1] + b[i-1]` (`i -> Idx('i')` and `result[0]` and `[-1]` ignored)
* result array type discovery and creation if not passed
* support for unevaluated summation function `Sum(f(x), (x, start, end))` (both via loop codegen and attempted algebraic decomposition)
* global and per-instance config tunables (detailed in [`src/exressive/config.py`](https://gitlab.com/expressive-py/expressive/-/blob/main/src/expressive/config.py))
* expr pretty print display in Notebooks
* validation to help discover type overflowing and more during builds - optionally sample data results from NumPy, SymPy, and build expr are compared, which slows the initial build, but provides good coverage, especially if data extremas are included

## installation

install via pip https://pypi.org/project/expressive/

```shell
pip install expressive
```

## usage

refer to tests for examples for now

when using, follow a workflow like
* create instance `E = Expressive("log(a + log(b))")`
* build instance `E.build(sample_data)`
* directly use callable `E(full_data)`

`data` should be provided as dict of NumPy arrays and the types and shapes of sample data must match the expected runtime data

 ```python
data_sample = {  # simplified data to build and test expr
    "a": numpy.array([1,2,3,4], dtype="int64"),
    "b": numpy.array([4,3,2,1], dtype="int64"),
}
data = {  # real data user wants to process
    "a": numpy.array(range(1_000_000), dtype="int64"),
    "b": numpy.array(range(1_000_000), dtype="int64"),
}
E = Expressive(expr)  # string or SymPy expr
E.build(data_sample)  # types used to compile a fast version
E(data)  # very fast callable
```

simple demo

```python
import time
import contextlib
import numpy
import matplotlib.pyplot as plt
from expressive import Expressive

# simple projectile motion in a plane
E_position = Expressive("y = v0*t*sin(a0) + 1/2(g*t^2)")

# expr is built early in the process runtime by user
def build():
    # create some sample data and build with it
    # the types are used to compile a fast version for full data
    data_example = {
        "v0": 100,  # initial velocity m/s
        "g": -9.81, # earth gravity m/s/s
        "a0": .785,  # starting angle ~45° in radians
        "t": numpy.linspace(0, 15, dtype="float64"),  # 15 seconds is probably enough
    }
    assert len(data_example["t"]) == 50  # linspace default
    time_start = time.perf_counter()
    E_position.build(data_example)  # verify is implied with little data
    time_run = time.perf_counter() - time_start

    # provide some extra display details
    count = len(data_example["t"])
    print(f"built in {time_run*1000:.2f}ms on {count:,} points")
    print(f"  {E_position}")

def load_data(
    point_count=10**8,  # 100 million points (*count of angles), maybe 4GiB here
    initial_velocity=100,  # m/s
):
    # manufacture lots of data, which would be loaded in a real example
    time_array = numpy.linspace(0, 15, point_count, dtype="float64")
    # collect the results
    data_collections = []
    # process much more data than the build sample
    for angle in (.524, .785, 1.047):  # initial angles (30°, 45°, 60°)
        data = {  # data is just generated in this case
            "v0": initial_velocity,  # NOTE type must match example data
            "g": -9.81, # earth gravity m/s/s
            "a0": angle,  # radians
            "t": time_array,  # just keep re-using the times for this example
        }
        data_collections.append(data)

    # data collections are now loaded (created)
    return data_collections

# later during the process runtime
# user calls the object directly with new data
def runtime(data_collections):
    """ whatever the program is normally up to """

    # create equivalent function for numpy compare
    def numpy_cmp(v0, g, a0, t):
        return v0*t*numpy.sin(a0) + 1/2*(g*t**2)

    # TODO also compare numexpr demo

    # call already-built object directly on each data
    results = []
    for data in data_collections:
        # expressive run
        t_start_e = time.perf_counter()  # just to show time, prefer timeit for perf
        results.append(E_position(data))
        t_run_e = time.perf_counter() - t_start_e

        # simple numpy run
        t_start_n = time.perf_counter()
        result_numpy = numpy_cmp(**data)
        t_run_n = time.perf_counter() - t_start_n

        # provide some extra display details
        angle = data["a0"]
        count = len(data["t"])
        t_run_e = t_run_e * 1000  # convert to ms
        t_run_n = t_run_n * 1000
        print(f"initial angle {angle}rad ran in {t_run_e:.2f}ms on {count:,} points (numpy:{t_run_n:.2f}ms)")

    # decimate to avoid very long matplotlib processing
    def sketchy_downsample(ref, count=500):
        offset = len(ref) // count
        return ref[::offset]

    # display results to show it worked
    for result, data in zip(results, data_collections):
        x = sketchy_downsample(data["t"])
        y = sketchy_downsample(result)
        plt.scatter(x, y)
    plt.xlabel("time (s)")
    plt.ylabel("position (m)")
    plt.show()

def main():
    build()
    data_collections = load_data()
    runtime(data_collections)

main()
```

![](https://gitlab.com/expressive-py/docs/-/raw/d1e43411242fda9cc81ced55484f9e7575acb6c3/img/expressive_examples_2d_motion.png)

## compatibility matrix

generally this strives to only rely on high-level support from SymPy and Numba, though Numba has stricter requirements for NumPy and llvmlite

| Python | Numba | NumPy | SymPy | commit | coverage | ran |
| --- | --- | --- | --- | --- | --- | --- |
| 3.7.17 | 0.56.4 | 1.21.6 | 1.6 | d2a9e76 | {'codegen.py': '🟠 99% m 487,518,533'} 🟢 100% (12path) | 140s |
| 3.8.20 | 0.58.1 | 1.24.4 | 1.7 | d2a9e76 | {'codegen.py': '🟠 99% m 487,518,533'} 🟢 100% (12path) | 138s |
| 3.9.19 | 0.53.1 | 1.23.5 | 1.7 | d2a9e76 | {'codegen.py': '🟠 99% m 487,518,533'} 🟢 100% (12path) | 139s |
| 3.9.19 | 0.60.0 | 2.0.1 | 1.13.2 | d2a9e76 | {'codegen.py': '🟠 99% m 487,533'} 🟢 100% (12path) | 140s |
| 3.10.16 | 0.61.2 | 2.2.6 | 1.14.0 | d2a9e76 | {'codegen.py': '🟠 99% m 487,533'} 🟢 100% (12path) | 141s |
| 3.11.11 | 0.61.2 | 2.2.6 | 1.14.0 | d2a9e76 | {'codegen.py': '🟠 99% m 487,533'} 🟢 100% (12path) | 147s |
| 3.12.7 | 0.59.1 | 1.26.4 | 1.13.1 | d2a9e76 | {'codegen.py': '🟠 99% m 487,533', 'test.py': '🟠 99% m 1414'} 🟢 100% (11path) | 120s |
| 3.12.8 | 0.61.2 | 2.2.6 | 1.14.0 | d2a9e76 | {'codegen.py': '🟠 99% m 487,533'} 🟢 100% (12path) | 157s |
| 3.13.1 | 0.61.2 | 2.2.6 | 1.14.0 | d2a9e76 | {'codegen.py': '🟠 99% m 487,533'} 🟢 100% (12path) | 162s |
| 3.13.1 | 0.61.2 | 2.2.6 | 1.14.0 | d2a9e76 | {'codegen.py': '🟠 99% m 487,533'} 🟢 100% (12path) | 162s |

NOTE differences in test run times are not an indicator of built expr speed, more likely the opposite and _more_ time spent represents additional build step effort, likely improving runtime execution! please consider the values arbitrary and just for development reasons

#### further compatibility notes

these runs build the package themselves internally, while my publishing environment is currently Python 3.11.2

though my testing indicates that this works under a wide variety of quite old versions of Python/Numba/SymPy, upgrading to the highest dependency versions you can will generally be best
* Python 3 major version status https://devguide.python.org/versions/
* https://numba.readthedocs.io/en/stable/release-notes-overview.html

NumPy 1.x and 2.0 saw some major API changes, so older environments may need to adjust or discover working combinations themselves
* some versions of Numba rely on `numpy.MachAr`, which has been [deprecated since at least NumPy 1.22](https://numpy.org/doc/stable/release/1.22.0-notes.html#the-np-machar-class-has-been-deprecated) and may result in warnings

TBD publish multi-version test tool

## testing

Only `docker` and `docker-buildx` are required in the host and used to generate and host testing

Currently expressive builds fine without buildx https://docs.docker.com/reference/cli/docker/build-legacy/, but beware that support for building without it may be silently lost in the future as installing buildx overrides `docker build` with an alias of `docker buildx build` making it frustrating for me to test with the legacy `docker build` at all

```shell
sudo apt install docker.io docker-buildx  # debian/ubuntu
sudo usermod -aG docker $USER
sudo su -l $USER  # login shell to self (reboot for all shells)
```

Run the test script from the root of the repository and it will build the docker test environment and run itself inside it automatically

```shell
./test/runtests.sh
```

## build + install locally

Follows the generic build and publish process
* https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives
* build (builder) https://pypi.org/project/build/

```shell
python3 -m build
python3 -m pip install ./dist/*.whl
```

## contributing

The development process is currently private (though most fruits are available here!), largely due to this being my first public project with the potential for other users than myself, and so the potential for more public gaffes is far greater

Please refer to [CONTRIBUTING.md](https://gitlab.com/expressive-py/expressive/-/blob/main/CONTRIBUTING.md) and [LICENSE.txt](https://gitlab.com/expressive-py/expressive/-/blob/main/LICENSE.txt) and feel free to provide feedback, bug reports, etc. via [Issues](https://gitlab.com/expressive-py/expressive/-/issues), subject to the former

#### additional future intentions for contributing
* ~~improve internal development history as time, popularity, and practicality allows~~
* ~~move to parallel, multi-version CI over all-in-1, single-version dev+test container~~
* ~~greatly relax dependency version requirements to improve compatibility~~
* publish majority of ticket ("Issue") history
* add a workflow for importing handwritten expressions

## version history

##### v3.10.20250908
* block using `prange` for self-referential exprs (uses offsets of the result array) as it can (will) result in incomplete or invalid result arrays

##### v3.9.20250819
* greatly improved modulo parsing support, allowing operator `mod` -> `%`
* new warning when using the name `mod` as a Symbol
* when creating an Expressive instance, a passed `config` argument can now be another config object (`E._config`) or any other valid `UserDict`, previously only `dict` was accepted
* new test script args to provide fastfail (end on first non-passing) and verbose to `unittest`

##### v3.8.20250807
* warn when input string atoms separated by whitespace can become joined like `a cos(b)` -> `acos(b)` instead of their intention (probably multiplication)

##### v3.7.20250801
* dynamic result arrays (user did not provide result array) are created in a Python-space wrapper rather than the (compiled) JIT'd function
* config changes now have a schema checker and global changes can be applied to `expressive.CONFIG` (affects new instances)
* passing data which is not used warns instead of always raising (`TypeError: expressive_wrapper() got an unexpected keyword argument 'm'`), controlled by the new config option `data.runtime.unused_data_callback` accepting "warn" (default), "raise", or "ignore"
* testing now relies on [docker-buildx](https://docs.docker.com/reference/cli/docker/buildx/build/) from [`build`](https://docs.docker.com/reference/cli/docker/build-legacy/)
* testing has a new helper for managing the global `CONFIG`, `modify_config_global()`

##### v3.6.20250717
* support for modulo `%` and `Mod`
* new string functions `p%q` or `mod(p,q)` are transformed to `Mod(p,q)`, while existing non-function name `mod` are left unchanged
* fixed a bug where the internal result array builder could choose a name from `extend` or another 0-dim Symbol when determining its length

##### v3.5.20250711
* support for `Sum` to `Piecewise` transforms, ideally avoiding an additional loop for each row
* initial support for adding additional values or functions via new `extend` arg (`dict` mapping `{str: number or function}`)
  * numbers can be any reasonable number-like, while functions must be strings or callables
  * all functions are embedded into the template as closures, with callables stringified via `inspect.getsource()`, even if they're some Numba instance via `.py_func` (for now)

##### v3.4.20250523
* basic/experimental version of `native_threadpool` parallelization model
* `Sum` simplifications which results in `Piecewise` are ignored (for now)

##### v3.3.20250508
* improved README with major features and links to major dependency projects
* explicitly name `translate_simplify.build.sum.try_algebraic_convert` tunable in stuck `Sum()` builder condition warning

##### v3.2.20250425
* improved smaller types handling
  * automatic dtype determination with `Pow()` is improved
  * give a dedicated warning when an exception related to setting `dtype_result` to a type with a small width that a function (such as `Pow()`) automatically promotes occurs
* improve autobuilding experience with new config tunables
  * easily enable autobuild globally `builder.autobuild.allow_autobuild`
  * option to disable build-time usage warning `builder.autobuild.usage_warn_nag`
* minor version is now a datestamp

[complete at CHANGELOG.md](https://gitlab.com/expressive-py/expressive/-/blob/main/CHANGELOG.md)
