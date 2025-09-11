#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_FunctionBindings.hpp>
#include <ROL_Vector.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <functional>
#include <ios>
#include <iterator>
#include <memory>
#include <ostream>
#include <streambuf>
#include <string>
#include <vector>

#include <functional>
#include <pybind11/pybind11.h>
#include <string>
#include <Teuchos_RCP.hpp>


#ifndef BINDER_PYBIND11_TYPE_CASTER
	#define BINDER_PYBIND11_TYPE_CASTER
	PYBIND11_DECLARE_HOLDER_TYPE(T, Teuchos::RCP<T>, false)
	PYBIND11_DECLARE_HOLDER_TYPE(T, T*, false)
	PYBIND11_MAKE_OPAQUE(Teuchos::RCP<void>)
#endif

void bind_pyrol_18(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	// ROL::details::fix_direction(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> &, const class ROL::Vector<double> &) file:ROL_FunctionBindings.hpp line:39
	M("ROL::details").def("fix_direction", (class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)> (*)(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> &, const class ROL::Vector<double> &)) &ROL::details::fix_direction<double>, "C++: ROL::details::fix_direction(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> &, const class ROL::Vector<double> &) --> class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)>", pybind11::arg("f"), pybind11::arg("v"));

}
