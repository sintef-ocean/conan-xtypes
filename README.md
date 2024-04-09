[![Linux GCC](https://github.com/sintef-ocean/conan-xtypes/workflows/Linux%20GCC/badge.svg)](https://github.com/sintef-ocean/conan-xtypes/actions?query=workflow%3A"Linux+GCC")
[![Windows MSVC](https://github.com/sintef-ocean/conan-xtypes/workflows/Windows%20MSVC/badge.svg)](https://github.com/sintef-ocean/conan-xtypes/actions?query=workflow%3A"Windows+MSVC")

[Conan.io](https://conan.io) recipe for [eprosima xtypes](https://github.com/eProsima/xtypes).

## How to use this package

1. Add remote to conan's package [remotes](https://docs.conan.io/2/reference/commands/remote.html)

   ```bash
   $ conan remote add sintef https://artifactory.smd.sintef.no/artifactory/api/conan/conan-local
   ```

2. Using [*conanfile.txt*](https://docs.conan.io/2/reference/conanfile_txt.html) and *cmake* in your project.

   Add *conanfile.txt*:
   ```
   [requires]
   eprosima-xtypes/cci.20230615@sintef/stable

   [options]
   eprosima-xtypes:with_tools=True

   [tool_requires]
   cmake/[>=3.25.0]

   [layout]
   cmake_layout

   [generators]
   CMakeDeps
   CMakeToolchain
   VirtualBuildEnv

   ```
   Insert into your *CMakeLists.txt* something like the following lines:
   ```cmake
   cmake_minimum_required(VERSION 3.15)
   project(TheProject CXX)

   find_package(xtypes REQUIRED)

   add_executable(the_executor code.cpp)
   target_link_libraries(the_executor eprosima::xtypes)
   ```
   Install and build e.g. a Release configuration (linux):
   ```bash
   $ conan install . -s build_type=Release -pr:b=default
   $ source build/Release/generators/conanbuild.sh
   $ cmake --preset conan-release
   $ cmake --build build/Release
   $ source build/Release/generators/deactivate_conanbuild.sh
   ```

## Package options

| Option                          | Allowed values    | Default |
|---------------------------------|-------------------|---------|
| with_exceptions                 | [True, False]     | True    |
| with_tools                      | [True, False]     | False   |

To build and run tests, set `tools.build:skip_test=False` in `global.conf`, in `[conf]` or
`--conf` as part of `conan install`.

## Known recipe issues
