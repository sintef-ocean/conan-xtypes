#include "xtypes/xtypes.hpp"
#include "xtypes/idl/idl.hpp"

#include <cstdlib>
#include <iostream>

using namespace eprosima::xtypes;

int main()
{
  try {
    std::string idl_spec = "struct InnerType { uint32 im1; float im2; };";

    idl::Context context;
    context.print_log(true);
    context.preprocess = false; // Preprocessor requires build environment with access to cl, not needed here
    context.log_level(eprosima::xtypes::idl::log::LogLevel::xDEBUG);

    context = idl::parse(idl_spec, context);

    if(!context.success) { throw std::runtime_error("Unable to parse idl spec"); }

    StructType inner = context.module().structure("InnerType");

    StructType outer("OuterType");
    outer.add_member("om1", StringType());

    idl::Module root;
    idl::Module& submod_a = root.create_submodule("a");
    idl::Module& submod_b = root.create_submodule("b");
    idl::Module& submod_aa = submod_a.create_submodule("a");
    submod_aa.structure(outer);
    submod_b.structure(inner);

    /*
      root
      \_a
      |  \_ a _ OuterType
      |
      \_b _ InnerType
    */

    std::cout << std::boolalpha;
    std::cout << "Does a::a::OuterType exists?: " << root.has_structure("a::a::OuterType") << std::endl;
    std::cout << "Does ::InnerType exists?: " << root.has_structure("::InnerType") << std::endl;
    std::cout << "Does InnerType exists?: " << root.has_structure("InnerType") << std::endl;
    std::cout << "Does OuterType exists?: " << root.has_structure("OuterType") << std::endl;
    std::cout << "Does ::b::InnerType exists?: " << root.has_structure("::b::InnerType") << std::endl;
    std::cout << "Does b::InnerType exists?: " << root.has_structure("b::InnerType") << std::endl;

    DynamicData outer_data(root["a"]["a"].structure("OuterType")); // ::a::a::OuterType
    outer_data["om1"] = "This is a string.";

    std::string scope_inner_type = inner.name(); // b::InnerType
    DynamicData inner_data(root.structure(scope_inner_type));
    inner_data["im1"] = 32u;
    inner_data["im2"] = 3.14159265f;
  } catch (const std::runtime_error& err) {
    std::cerr << "Caught exception: " << err.what() << std::endl;
    return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}
