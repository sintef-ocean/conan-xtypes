from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.microsoft import is_msvc
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if is_msvc(self):
            self.tool_requires("cmake/[>=3.22.0 <4]")
        else:
            self.tool_requires("cmake/[>=3.16.0 <4]")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")

            if self.dependencies["eprosima-xtypes"].options.get_safe("with_tools", False):
                sfx = ".exe" if self.settings.os == "Windows" else ""
                self.run(f'xtypes_idl_validator{sfx} "struct InnerType {{ uint32 im1; float im2; }};"')
