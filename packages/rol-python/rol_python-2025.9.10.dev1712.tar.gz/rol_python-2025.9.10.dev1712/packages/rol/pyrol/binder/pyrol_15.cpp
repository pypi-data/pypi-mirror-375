#include <ROL_Stream.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <Teuchos_any.hpp>
#include <ios>
#include <locale>
#include <memory>
#include <ostream>
#include <sstream> // __str__
#include <streambuf>
#include <string>

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

void bind_pyrol_15(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::details::basic_nullstream file:ROL_Stream.hpp line:31
		pybind11::class_<ROL::details::basic_nullstream<char,std::char_traits<char>>, Teuchos::RCP<ROL::details::basic_nullstream<char,std::char_traits<char>>>, std::ostream> cl(M("ROL::details"), "basic_nullstream_char_std_char_traits_char_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::details::basic_nullstream<char,std::char_traits<char>>(); } ) );
	}
	// ROL::details::makeStreamPtr(std::ostream &, bool) file:ROL_Stream.hpp line:39
	M("ROL::details").def("makeStreamPtr", [](std::ostream & a0) -> Teuchos::RCP<std::ostream > { return ROL::details::makeStreamPtr(a0); }, "", pybind11::arg("os"));
	M("ROL::details").def("makeStreamPtr", (class Teuchos::RCP<std::ostream > (*)(std::ostream &, bool)) &ROL::details::makeStreamPtr, "C++: ROL::details::makeStreamPtr(std::ostream &, bool) --> class Teuchos::RCP<std::ostream >", pybind11::arg("os"), pybind11::arg("noSuppressOutput"));

	// ROL::details::makeStreamPtr(class Teuchos::RCP<std::ostream >, bool) file:ROL_Stream.hpp line:47
	M("ROL::details").def("makeStreamPtr", [](class Teuchos::RCP<std::ostream > const & a0) -> Teuchos::RCP<std::ostream > { return ROL::details::makeStreamPtr(a0); }, "", pybind11::arg("os"));
	M("ROL::details").def("makeStreamPtr", (class Teuchos::RCP<std::ostream > (*)(class Teuchos::RCP<std::ostream >, bool)) &ROL::details::makeStreamPtr, "C++: ROL::details::makeStreamPtr(class Teuchos::RCP<std::ostream >, bool) --> class Teuchos::RCP<std::ostream >", pybind11::arg("os"), pybind11::arg("noSuppressOutput"));

}
