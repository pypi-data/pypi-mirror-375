#include <map>
#include <algorithm>
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>

#include <pybind11/pybind11.h>

using ModuleGetter = std::function< pybind11::module & (std::string const &) >;

void bind_pyrol_0(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_1(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_2(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_3(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_4(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_5(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_6(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_7(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_8(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_9(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_10(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_11(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_12(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_13(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_14(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_15(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_16(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_17(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_18(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_19(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_20(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_21(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_22(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_23(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_24(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_25(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_26(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_27(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_28(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_29(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_30(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_31(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_32(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_33(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_34(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_35(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_36(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_37(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_38(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_39(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_40(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_41(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_42(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_43(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_44(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_45(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_46(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_47(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_48(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_49(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_50(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_51(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_52(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_53(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_54(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_55(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_56(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_57(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_58(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_59(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_60(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_61(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_62(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_63(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_64(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_65(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_66(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_67(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_68(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_69(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_70(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_71(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_72(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_73(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_74(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_75(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_76(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_77(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_78(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_79(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_80(std::function< pybind11::module &(std::string const &namespace_) > &M);
void bind_pyrol_81(std::function< pybind11::module &(std::string const &namespace_) > &M);


PYBIND11_MODULE(pyrol, root_module) {
	root_module.doc() = "pyrol module";

	std::map <std::string, pybind11::module> modules;
	ModuleGetter M = [&](std::string const &namespace_) -> pybind11::module & {
		auto it = modules.find(namespace_);
		if( it == modules.end() ) throw std::runtime_error("Attempt to access pybind11::module for namespace " + namespace_ + " before it was created!!!");
		return it->second;
	};

	modules[""] = root_module;

	static std::vector<std::string> const reserved_python_words {"nonlocal", "global", };

	auto mangle_namespace_name(
		[](std::string const &ns) -> std::string {
			if ( std::find(reserved_python_words.begin(), reserved_python_words.end(), ns) == reserved_python_words.end() ) return ns;
			return ns+'_';
		}
	);

	std::vector< std::pair<std::string, std::string> > sub_modules {
		{"", "ROL"},
		{"ROL", "Elementwise"},
		{"ROL", "Exception"},
		{"ROL", "OED"},
		{"ROL::OED", "Het"},
		{"ROL::OED", "Hom"},
		{"ROL", "TRUtils"},
		{"ROL", "TypeB"},
		{"ROL", "TypeE"},
		{"ROL", "TypeG"},
		{"ROL", "TypeP"},
		{"ROL", "TypeU"},
		{"ROL", "details"},
		{"", "Teuchos"},
		{"Teuchos", "Exceptions"},
		{"Teuchos", "PtrPrivateUtilityPack"},
		{"", "std"},
	};
	for(auto &p : sub_modules ) modules[ p.first.empty() ? p.second :  p.first+"::"+p.second ] = modules[p.first].def_submodule( mangle_namespace_name(p.second).c_str(), ("Bindings for " + p.first + "::" + p.second + " namespace").c_str() );

	//pybind11::class_<std::shared_ptr<void>>(M(""), "_encapsulated_data_");

	bind_pyrol_0(M);
	bind_pyrol_1(M);
	bind_pyrol_2(M);
	bind_pyrol_3(M);
	bind_pyrol_4(M);
	bind_pyrol_5(M);
	bind_pyrol_6(M);
	bind_pyrol_7(M);
	bind_pyrol_8(M);
	bind_pyrol_9(M);
	bind_pyrol_10(M);
	bind_pyrol_11(M);
	bind_pyrol_12(M);
	bind_pyrol_13(M);
	bind_pyrol_14(M);
	bind_pyrol_15(M);
	bind_pyrol_16(M);
	bind_pyrol_17(M);
	bind_pyrol_18(M);
	bind_pyrol_19(M);
	bind_pyrol_20(M);
	bind_pyrol_21(M);
	bind_pyrol_22(M);
	bind_pyrol_23(M);
	bind_pyrol_24(M);
	bind_pyrol_25(M);
	bind_pyrol_26(M);
	bind_pyrol_27(M);
	bind_pyrol_28(M);
	bind_pyrol_29(M);
	bind_pyrol_30(M);
	bind_pyrol_31(M);
	bind_pyrol_32(M);
	bind_pyrol_33(M);
	bind_pyrol_34(M);
	bind_pyrol_35(M);
	bind_pyrol_36(M);
	bind_pyrol_37(M);
	bind_pyrol_38(M);
	bind_pyrol_39(M);
	bind_pyrol_40(M);
	bind_pyrol_41(M);
	bind_pyrol_42(M);
	bind_pyrol_43(M);
	bind_pyrol_44(M);
	bind_pyrol_45(M);
	bind_pyrol_46(M);
	bind_pyrol_47(M);
	bind_pyrol_48(M);
	bind_pyrol_49(M);
	bind_pyrol_50(M);
	bind_pyrol_51(M);
	bind_pyrol_52(M);
	bind_pyrol_53(M);
	bind_pyrol_54(M);
	bind_pyrol_55(M);
	bind_pyrol_56(M);
	bind_pyrol_57(M);
	bind_pyrol_58(M);
	bind_pyrol_59(M);
	bind_pyrol_60(M);
	bind_pyrol_61(M);
	bind_pyrol_62(M);
	bind_pyrol_63(M);
	bind_pyrol_64(M);
	bind_pyrol_65(M);
	bind_pyrol_66(M);
	bind_pyrol_67(M);
	bind_pyrol_68(M);
	bind_pyrol_69(M);
	bind_pyrol_70(M);
	bind_pyrol_71(M);
	bind_pyrol_72(M);
	bind_pyrol_73(M);
	bind_pyrol_74(M);
	bind_pyrol_75(M);
	bind_pyrol_76(M);
	bind_pyrol_77(M);
	bind_pyrol_78(M);
	bind_pyrol_79(M);
	bind_pyrol_80(M);
	bind_pyrol_81(M);

}
