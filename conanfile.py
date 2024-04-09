import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.microsoft import is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment
from conan.tools.scm import Git, Version

required_conan_version = ">=2.0"


class PackageConan(ConanFile):
    name = "eprosima-xtypes"
    description = "Header-only OMG DDS-XTYPES standard implementation"
    license = "Apache-2.0"
    url = "https://github.com/sintef-ocean/conan-xtypes"
    homepage = "https://github.com/eProsima/xtypes"
    topics = ("dds-xtypes", "omg standard", "dds")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = False  # True if no patch
    options = {
        "with_exceptions": [True, False],
        "with_tools": [True, False],
    }
    default_options = {
        "with_exceptions": True,
        "with_tools": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "msvc": "14.2",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    @property
    def _build_tests(self):
        return not self.conf.get("tools.build:skip_test", default=True)

    @property
    def _build_needed(self):
        return self.options.with_tools or self._build_tests

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpp-peglib/1.8.4", transitive_headers=True)

    def package_id(self):
        if not self.info.options.with_tools:
            self.info.settings.compiler.clear()
        else:
            self.info.settings.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        if self._build_tests:
            self.test_requires("gtest/1.13.0")
        if self._build_needed:
            if is_msvc(self):
                self.tool_requires("cmake/[>=3.22.0 <4]")
            else:
                self.tool_requires("cmake/[>=3.16.0 <4]")

    def source(self):
        git = Git(self)
        git.clone(self.conan_data["sources"][self.version]["url"], target=".")
        git.checkout(self.conan_data["sources"][self.version]["commit"])

    def generate(self):

        if not self._build_needed:
            return

        tc = CMakeToolchain(self)
        tc.variables["XTYPES_EXCEPTIONS"] = self.options.with_exceptions
        tc.variables["XTYPES_BUILD_TOOLS"] = self.options.with_tools
        tc.variables["XTYPES_BUILD_TESTS"] = self._build_tests
        tc.variables["XTYPES_EXAMPLES"] = False
        tc.variables["XTYPES_PEGLIB_VERSION"] = f"v{str(self.dependencies['cpp-peglib'].ref.version)}"
        tc.generate()

        deps = CMakeDeps(self)
        if self._build_tests:
            deps.build_context_activated = ["gtest"]

        deps.generate()

    def build(self):
        apply_conandata_patches(self)

        if not (self.options.with_tools or self._build_tests):
            return

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        if self._build_tests:
            env = Environment()
            env.define("CTEST_OUTPUT_ON_FAILURE", "ON")
            with env.vars(self).apply():
                cmake.test()

    def package(self):

        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="xtypes_idl_validator*",
            dst=os.path.join(self.package_folder, "bin"),
            src=self.build_folder,
            keep_path=False
        )
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
            keep_path=True
        )

    def package_info(self):
        self.cpp_info.bindirs = ["bin"] if self.options.with_tools else []
        self.cpp_info.libdirs = []

        if self.options.with_exceptions:
            self.cpp_info.defines.append("XTYPES_EXCEPTIONS")

        self.cpp_info.set_property("cmake_file_name", "xtypes")
        self.cpp_info.set_property("cmake_target_name", "eprosima::xtypes")

        # Missing: set_target_properties(xtypes PROPERTIES INTERFACE_COMPILE_FEATURES "cxx_std_17;cxx_variadic_macros")
        # TODO: how to handle this properly. Add own cmake module, which is auto-included with find_package?

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
            self.cpp_info.cxxflags.append("-pthread")
            self.cpp_info.exelinkflags.append("-pthread")
            self.cpp_info.sharedlinkflags.append("-pthread")
        if is_msvc(self):
            self.cpp_info.cxxflags.append("/Zc:__cplusplus")
            self.cpp_info.cxxflags.append("/Zc:preprocessor /execution-charset:UTF-8")
