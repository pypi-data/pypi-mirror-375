#include <PyROL_Teuchos_Custom.hpp>
#include <Teuchos_TestForException.hpp>
#include <Teuchos_TypeNameTraits.hpp>
#include <iterator>
#include <memory>
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

void bind_pyrol_4(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	// Teuchos::demangleName(const std::string &) file:Teuchos_TypeNameTraits.hpp line:45
	M("Teuchos").def("demangleName", (std::string (*)(const std::string &)) &Teuchos::demangleName, "Demangle a C++ name if valid.\n\n The name must have come from typeid(...).name() in order to be\n valid name to pass to this function.\n\n \n\n \n\nC++: Teuchos::demangleName(const std::string &) --> std::string", pybind11::arg("mangledName"));

	// Teuchos::TestForException_incrThrowNumber() file:Teuchos_TestForException.hpp line:29
	M("Teuchos").def("TestForException_incrThrowNumber", (void (*)()) &Teuchos::TestForException_incrThrowNumber, "Increment the throw number.  \n\nC++: Teuchos::TestForException_incrThrowNumber() --> void");

	// Teuchos::TestForException_getThrowNumber() file:Teuchos_TestForException.hpp line:32
	M("Teuchos").def("TestForException_getThrowNumber", (int (*)()) &Teuchos::TestForException_getThrowNumber, "Increment the throw number.  \n\nC++: Teuchos::TestForException_getThrowNumber() --> int");

	// Teuchos::TestForException_break(const std::string &, int) file:Teuchos_TestForException.hpp line:36
	M("Teuchos").def("TestForException_break", (void (*)(const std::string &, int)) &Teuchos::TestForException_break, "The only purpose for this function is to set a breakpoint.\n    \n\n\nC++: Teuchos::TestForException_break(const std::string &, int) --> void", pybind11::arg("msg"), pybind11::arg("throwNumber"));

	// Teuchos::TestForException_setEnableStacktrace(bool) file:Teuchos_TestForException.hpp line:41
	M("Teuchos").def("TestForException_setEnableStacktrace", (void (*)(bool)) &Teuchos::TestForException_setEnableStacktrace, "Set at runtime if stacktracing functionality is enabled when *\n    exceptions are thrown.  \n\n\nC++: Teuchos::TestForException_setEnableStacktrace(bool) --> void", pybind11::arg("enableStrackTrace"));

	// Teuchos::TestForException_getEnableStacktrace() file:Teuchos_TestForException.hpp line:45
	M("Teuchos").def("TestForException_getEnableStacktrace", (bool (*)()) &Teuchos::TestForException_getEnableStacktrace, "Get at runtime if stacktracing functionality is enabled when\n exceptions are thrown. \n\nC++: Teuchos::TestForException_getEnableStacktrace() --> bool");

	// Teuchos::TestForTermination_terminate(const std::string &) file:Teuchos_TestForException.hpp line:48
	M("Teuchos").def("TestForTermination_terminate", (void (*)(const std::string &)) &Teuchos::TestForTermination_terminate, "Prints the message to std::cerr and calls std::terminate. \n\nC++: Teuchos::TestForTermination_terminate(const std::string &) --> void", pybind11::arg("msg"));

}
