#include <ios>
#include <locale>
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

void bind_pyrol_0(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // std::basic_ostream file:bits/ostream.tcc line:345
		pybind11::class_<std::ostream, Teuchos::RCP<std::ostream>> cl(M("std"), "ostream", "", pybind11::module_local());
		cl.def("put", (std::ostream & (std::ostream::*)(char)) &std::ostream::put, "C++: std::ostream::put(char) --> std::ostream &", pybind11::return_value_policy::automatic, pybind11::arg("__c"));
		cl.def("write", (std::ostream & (std::ostream::*)(const char *, long)) &std::ostream::write, "C++: std::ostream::write(const char *, long) --> std::ostream &", pybind11::return_value_policy::automatic, pybind11::arg("__s"), pybind11::arg("__n"));
		cl.def("flush", (std::ostream & (std::ostream::*)()) &std::ostream::flush, "C++: std::ostream::flush() --> std::ostream &", pybind11::return_value_policy::automatic);

		{ // std::ostream::sentry file:ostream line:104
			auto & enclosing_class = cl;
			pybind11::class_<std::ostream::sentry, Teuchos::RCP<std::ostream::sentry>> cl(enclosing_class, "sentry", "", pybind11::module_local());
			cl.def( pybind11::init<std::ostream &>(), pybind11::arg("__os") );

		}

	}
}
