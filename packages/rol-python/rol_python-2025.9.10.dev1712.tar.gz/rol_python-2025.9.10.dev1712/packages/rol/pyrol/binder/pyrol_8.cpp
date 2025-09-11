#include <Teuchos_Ptr.hpp>
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

void bind_pyrol_8(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	// Teuchos::PtrPrivateUtilityPack::throw_null(const std::string &) file:Teuchos_Ptr.hpp line:22
	M("Teuchos::PtrPrivateUtilityPack").def("throw_null", (void (*)(const std::string &)) &Teuchos::PtrPrivateUtilityPack::throw_null, "C++: Teuchos::PtrPrivateUtilityPack::throw_null(const std::string &) --> void", pybind11::arg("type_name"));

}
