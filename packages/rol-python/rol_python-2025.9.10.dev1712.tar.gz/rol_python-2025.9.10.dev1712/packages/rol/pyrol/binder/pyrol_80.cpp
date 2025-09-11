#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_Vector.hpp>
#include <ROL_VectorWorkspace.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <ios>
#include <memory>
#include <ostream>
#include <sstream> // __str__
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

void bind_pyrol_80(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::details::VectorWorkspace file:ROL_VectorWorkspace.hpp line:64
		pybind11::class_<ROL::details::VectorWorkspace<double>, Teuchos::RCP<ROL::details::VectorWorkspace<double>>> cl(M("ROL::details"), "VectorWorkspace_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](ROL::details::VectorWorkspace<double> const &o){ return new ROL::details::VectorWorkspace<double>(o); } ) );
		cl.def( pybind11::init( [](){ return new ROL::details::VectorWorkspace<double>(); } ) );
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::details::VectorWorkspace<double>::*)(const class ROL::Vector<double> &)) &ROL::details::VectorWorkspace<double>::clone, "C++: ROL::details::VectorWorkspace<double>::clone(const class ROL::Vector<double> &) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("x"));
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::details::VectorWorkspace<double>::*)(const class Teuchos::RCP<const class ROL::Vector<double> > &)) &ROL::details::VectorWorkspace<double>::clone, "C++: ROL::details::VectorWorkspace<double>::clone(const class Teuchos::RCP<const class ROL::Vector<double> > &) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("x"));
		cl.def("copy", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::details::VectorWorkspace<double>::*)(const class ROL::Vector<double> &)) &ROL::details::VectorWorkspace<double>::copy, "C++: ROL::details::VectorWorkspace<double>::copy(const class ROL::Vector<double> &) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("x"));
		cl.def("copy", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::details::VectorWorkspace<double>::*)(const class Teuchos::RCP<const class ROL::Vector<double> > &)) &ROL::details::VectorWorkspace<double>::copy, "C++: ROL::details::VectorWorkspace<double>::copy(const class Teuchos::RCP<const class ROL::Vector<double> > &) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("x"));
		cl.def("status", (void (ROL::details::VectorWorkspace<double>::*)(std::ostream &) const) &ROL::details::VectorWorkspace<double>::status, "C++: ROL::details::VectorWorkspace<double>::status(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("assign", (class ROL::details::VectorWorkspace<double> & (ROL::details::VectorWorkspace<double>::*)(const class ROL::details::VectorWorkspace<double> &)) &ROL::details::VectorWorkspace<double>::operator=, "C++: ROL::details::VectorWorkspace<double>::operator=(const class ROL::details::VectorWorkspace<double> &) --> class ROL::details::VectorWorkspace<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
}
