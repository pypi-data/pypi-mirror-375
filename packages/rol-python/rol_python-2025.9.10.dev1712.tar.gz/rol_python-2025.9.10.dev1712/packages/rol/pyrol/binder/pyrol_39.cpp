#include <Teuchos_ParameterListExceptions.hpp>
#include <iterator>
#include <memory>
#include <sstream> // __str__
#include <stdexcept>
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

// Teuchos::Exceptions::InvalidArgument file:Teuchos_ParameterListExceptions.hpp line:22
struct PyCallBack_Teuchos_Exceptions_InvalidArgument : public Teuchos::Exceptions::InvalidArgument {
	using Teuchos::Exceptions::InvalidArgument::InvalidArgument;

	const char * what() const throw() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::Exceptions::InvalidArgument *>(this), "what");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const char *>::value) {
				static pybind11::detail::override_caster_t<const char *> caster;
				return pybind11::detail::cast_ref<const char *>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const char *>(std::move(o));
		}
		return logic_error::what();
	}
};

// Teuchos::Exceptions::InvalidParameter file:Teuchos_ParameterListExceptions.hpp line:28
struct PyCallBack_Teuchos_Exceptions_InvalidParameter : public Teuchos::Exceptions::InvalidParameter {
	using Teuchos::Exceptions::InvalidParameter::InvalidParameter;

	const char * what() const throw() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::Exceptions::InvalidParameter *>(this), "what");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const char *>::value) {
				static pybind11::detail::override_caster_t<const char *> caster;
				return pybind11::detail::cast_ref<const char *>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const char *>(std::move(o));
		}
		return logic_error::what();
	}
};

// Teuchos::Exceptions::InvalidParameterName file:Teuchos_ParameterListExceptions.hpp line:34
struct PyCallBack_Teuchos_Exceptions_InvalidParameterName : public Teuchos::Exceptions::InvalidParameterName {
	using Teuchos::Exceptions::InvalidParameterName::InvalidParameterName;

	const char * what() const throw() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::Exceptions::InvalidParameterName *>(this), "what");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const char *>::value) {
				static pybind11::detail::override_caster_t<const char *> caster;
				return pybind11::detail::cast_ref<const char *>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const char *>(std::move(o));
		}
		return logic_error::what();
	}
};

// Teuchos::Exceptions::InvalidParameterType file:Teuchos_ParameterListExceptions.hpp line:40
struct PyCallBack_Teuchos_Exceptions_InvalidParameterType : public Teuchos::Exceptions::InvalidParameterType {
	using Teuchos::Exceptions::InvalidParameterType::InvalidParameterType;

	const char * what() const throw() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::Exceptions::InvalidParameterType *>(this), "what");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const char *>::value) {
				static pybind11::detail::override_caster_t<const char *> caster;
				return pybind11::detail::cast_ref<const char *>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const char *>(std::move(o));
		}
		return logic_error::what();
	}
};

// Teuchos::Exceptions::InvalidParameterValue file:Teuchos_ParameterListExceptions.hpp line:46
struct PyCallBack_Teuchos_Exceptions_InvalidParameterValue : public Teuchos::Exceptions::InvalidParameterValue {
	using Teuchos::Exceptions::InvalidParameterValue::InvalidParameterValue;

	const char * what() const throw() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::Exceptions::InvalidParameterValue *>(this), "what");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const char *>::value) {
				static pybind11::detail::override_caster_t<const char *> caster;
				return pybind11::detail::cast_ref<const char *>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const char *>(std::move(o));
		}
		return logic_error::what();
	}
};

void bind_pyrol_39(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // Teuchos::Exceptions::InvalidArgument file:Teuchos_ParameterListExceptions.hpp line:22
		pybind11::class_<Teuchos::Exceptions::InvalidArgument, Teuchos::RCP<Teuchos::Exceptions::InvalidArgument>, PyCallBack_Teuchos_Exceptions_InvalidArgument> cl(M("Teuchos::Exceptions"), "InvalidArgument", ".\n \n\n\n ", pybind11::module_local());
		cl.def( pybind11::init<const std::string &>(), pybind11::arg("what_arg") );

		cl.def( pybind11::init( [](PyCallBack_Teuchos_Exceptions_InvalidArgument const &o){ return new PyCallBack_Teuchos_Exceptions_InvalidArgument(o); } ) );
		cl.def( pybind11::init( [](Teuchos::Exceptions::InvalidArgument const &o){ return new Teuchos::Exceptions::InvalidArgument(o); } ) );
		cl.def("assign", (class Teuchos::Exceptions::InvalidArgument & (Teuchos::Exceptions::InvalidArgument::*)(const class Teuchos::Exceptions::InvalidArgument &)) &Teuchos::Exceptions::InvalidArgument::operator=, "C++: Teuchos::Exceptions::InvalidArgument::operator=(const class Teuchos::Exceptions::InvalidArgument &) --> class Teuchos::Exceptions::InvalidArgument &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // Teuchos::Exceptions::InvalidParameter file:Teuchos_ParameterListExceptions.hpp line:28
		pybind11::class_<Teuchos::Exceptions::InvalidParameter, Teuchos::RCP<Teuchos::Exceptions::InvalidParameter>, PyCallBack_Teuchos_Exceptions_InvalidParameter> cl(M("Teuchos::Exceptions"), "InvalidParameter", ".\n \n\n\n ", pybind11::module_local());
		cl.def( pybind11::init<const std::string &>(), pybind11::arg("what_arg") );

		cl.def( pybind11::init( [](PyCallBack_Teuchos_Exceptions_InvalidParameter const &o){ return new PyCallBack_Teuchos_Exceptions_InvalidParameter(o); } ) );
		cl.def( pybind11::init( [](Teuchos::Exceptions::InvalidParameter const &o){ return new Teuchos::Exceptions::InvalidParameter(o); } ) );
		cl.def("assign", (class Teuchos::Exceptions::InvalidParameter & (Teuchos::Exceptions::InvalidParameter::*)(const class Teuchos::Exceptions::InvalidParameter &)) &Teuchos::Exceptions::InvalidParameter::operator=, "C++: Teuchos::Exceptions::InvalidParameter::operator=(const class Teuchos::Exceptions::InvalidParameter &) --> class Teuchos::Exceptions::InvalidParameter &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // Teuchos::Exceptions::InvalidParameterName file:Teuchos_ParameterListExceptions.hpp line:34
		pybind11::class_<Teuchos::Exceptions::InvalidParameterName, Teuchos::RCP<Teuchos::Exceptions::InvalidParameterName>, PyCallBack_Teuchos_Exceptions_InvalidParameterName, Teuchos::Exceptions::InvalidParameter> cl(M("Teuchos::Exceptions"), "InvalidParameterName", ".\n \n\n\n ", pybind11::module_local());
		cl.def( pybind11::init<const std::string &>(), pybind11::arg("what_arg") );

		cl.def("assign", (class Teuchos::Exceptions::InvalidParameterName & (Teuchos::Exceptions::InvalidParameterName::*)(const class Teuchos::Exceptions::InvalidParameterName &)) &Teuchos::Exceptions::InvalidParameterName::operator=, "C++: Teuchos::Exceptions::InvalidParameterName::operator=(const class Teuchos::Exceptions::InvalidParameterName &) --> class Teuchos::Exceptions::InvalidParameterName &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // Teuchos::Exceptions::InvalidParameterType file:Teuchos_ParameterListExceptions.hpp line:40
		pybind11::class_<Teuchos::Exceptions::InvalidParameterType, Teuchos::RCP<Teuchos::Exceptions::InvalidParameterType>, PyCallBack_Teuchos_Exceptions_InvalidParameterType, Teuchos::Exceptions::InvalidParameter> cl(M("Teuchos::Exceptions"), "InvalidParameterType", ".\n \n\n\n ", pybind11::module_local());
		cl.def( pybind11::init<const std::string &>(), pybind11::arg("what_arg") );

		cl.def( pybind11::init( [](PyCallBack_Teuchos_Exceptions_InvalidParameterType const &o){ return new PyCallBack_Teuchos_Exceptions_InvalidParameterType(o); } ) );
		cl.def( pybind11::init( [](Teuchos::Exceptions::InvalidParameterType const &o){ return new Teuchos::Exceptions::InvalidParameterType(o); } ) );
		cl.def("assign", (class Teuchos::Exceptions::InvalidParameterType & (Teuchos::Exceptions::InvalidParameterType::*)(const class Teuchos::Exceptions::InvalidParameterType &)) &Teuchos::Exceptions::InvalidParameterType::operator=, "C++: Teuchos::Exceptions::InvalidParameterType::operator=(const class Teuchos::Exceptions::InvalidParameterType &) --> class Teuchos::Exceptions::InvalidParameterType &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // Teuchos::Exceptions::InvalidParameterValue file:Teuchos_ParameterListExceptions.hpp line:46
		pybind11::class_<Teuchos::Exceptions::InvalidParameterValue, Teuchos::RCP<Teuchos::Exceptions::InvalidParameterValue>, PyCallBack_Teuchos_Exceptions_InvalidParameterValue, Teuchos::Exceptions::InvalidParameter> cl(M("Teuchos::Exceptions"), "InvalidParameterValue", ".\n \n\n\n ", pybind11::module_local());
		cl.def( pybind11::init<const std::string &>(), pybind11::arg("what_arg") );

		cl.def( pybind11::init( [](PyCallBack_Teuchos_Exceptions_InvalidParameterValue const &o){ return new PyCallBack_Teuchos_Exceptions_InvalidParameterValue(o); } ) );
		cl.def( pybind11::init( [](Teuchos::Exceptions::InvalidParameterValue const &o){ return new Teuchos::Exceptions::InvalidParameterValue(o); } ) );
		cl.def("assign", (class Teuchos::Exceptions::InvalidParameterValue & (Teuchos::Exceptions::InvalidParameterValue::*)(const class Teuchos::Exceptions::InvalidParameterValue &)) &Teuchos::Exceptions::InvalidParameterValue::operator=, "C++: Teuchos::Exceptions::InvalidParameterValue::operator=(const class Teuchos::Exceptions::InvalidParameterValue &) --> class Teuchos::Exceptions::InvalidParameterValue &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
}
