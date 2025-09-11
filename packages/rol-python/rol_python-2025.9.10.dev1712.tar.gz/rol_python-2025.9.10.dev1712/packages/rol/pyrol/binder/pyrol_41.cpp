#include <PyROL_Teuchos_Custom.hpp>
#include <Teuchos_Array.hpp>
#include <Teuchos_ArrayView.hpp>
#include <Teuchos_ArrayViewDecl.hpp>
#include <Teuchos_Describable.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_FancyOStream.hpp>
#include <Teuchos_FilteredIterator.hpp>
#include <Teuchos_InvalidDependencyException.hpp>
#include <Teuchos_LabeledObject.hpp>
#include <Teuchos_ParameterEntry.hpp>
#include <Teuchos_ParameterEntryValidator.hpp>
#include <Teuchos_ParameterList.hpp>
#include <Teuchos_ParameterListModifier.hpp>
#include <Teuchos_PtrDecl.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <Teuchos_StringIndexedOrderedValueObjectContainer.hpp>
#include <Teuchos_Utils.hpp>
#include <Teuchos_VerbosityLevel.hpp>
#include <Teuchos_XMLObject.hpp>
#include <Teuchos_XMLObjectImplem.hpp>
#include <Teuchos_any.hpp>
#include <deque>
#include <functional>
#include <ios>
#include <iterator>
#include <locale>
#include <map>
#include <memory>
#include <ostream>
#include <sstream> // __str__
#include <stdexcept>
#include <streambuf>
#include <string>
#include <typeinfo>
#include <utility>
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

// Teuchos::basic_FancyOStream_buf file:Teuchos_FancyOStream.hpp line:31
struct PyCallBack_Teuchos_basic_FancyOStream_buf_char_std_char_traits_char_t : public Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>> {
	using Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::basic_FancyOStream_buf;

	long xsputn(const char * a0, long a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>> *>(this), "xsputn");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<long>::value) {
				static pybind11::detail::override_caster_t<long> caster;
				return pybind11::detail::cast_ref<long>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<long>(std::move(o));
		}
		return basic_FancyOStream_buf::xsputn(a0, a1);
	}
	int overflow(int a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>> *>(this), "overflow");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return basic_FancyOStream_buf::overflow(a0);
	}
	void imbue(const class std::locale & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>> *>(this), "imbue");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return basic_streambuf::imbue(a0);
	}
	int sync() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>> *>(this), "sync");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return basic_streambuf::sync();
	}
	long showmanyc() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>> *>(this), "showmanyc");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<long>::value) {
				static pybind11::detail::override_caster_t<long> caster;
				return pybind11::detail::cast_ref<long>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<long>(std::move(o));
		}
		return basic_streambuf::showmanyc();
	}
	long xsgetn(char * a0, long a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>> *>(this), "xsgetn");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<long>::value) {
				static pybind11::detail::override_caster_t<long> caster;
				return pybind11::detail::cast_ref<long>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<long>(std::move(o));
		}
		return basic_streambuf::xsgetn(a0, a1);
	}
	int underflow() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>> *>(this), "underflow");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return basic_streambuf::underflow();
	}
	int uflow() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>> *>(this), "uflow");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return basic_streambuf::uflow();
	}
	int pbackfail(int a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>> *>(this), "pbackfail");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return basic_streambuf::pbackfail(a0);
	}
};

// Teuchos::LabeledObject file:Teuchos_LabeledObject.hpp line:37
struct PyCallBack_Teuchos_LabeledObject : public Teuchos::LabeledObject {
	using Teuchos::LabeledObject::LabeledObject;

	void setObjectLabel(const std::string & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::LabeledObject *>(this), "setObjectLabel");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LabeledObject::setObjectLabel(a0);
	}
	std::string getObjectLabel() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::LabeledObject *>(this), "getObjectLabel");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<std::string>::value) {
				static pybind11::detail::override_caster_t<std::string> caster;
				return pybind11::detail::cast_ref<std::string>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<std::string>(std::move(o));
		}
		return LabeledObject::getObjectLabel();
	}
};

// Teuchos::InvalidArrayStringRepresentation file:Teuchos_Array.hpp line:36
struct PyCallBack_Teuchos_InvalidArrayStringRepresentation : public Teuchos::InvalidArrayStringRepresentation {
	using Teuchos::InvalidArrayStringRepresentation::InvalidArrayStringRepresentation;

	const char * what() const throw() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::InvalidArrayStringRepresentation *>(this), "what");
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

// Teuchos::EmptyXMLError file:Teuchos_XMLObject.hpp line:23
struct PyCallBack_Teuchos_EmptyXMLError : public Teuchos::EmptyXMLError {
	using Teuchos::EmptyXMLError::EmptyXMLError;

	const char * what() const throw() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::EmptyXMLError *>(this), "what");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const char *>::value) {
				static pybind11::detail::override_caster_t<const char *> caster;
				return pybind11::detail::cast_ref<const char *>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const char *>(std::move(o));
		}
		return runtime_error::what();
	}
};

// Teuchos::ParameterEntryValidator file:Teuchos_ParameterEntryValidator.hpp line:31
struct PyCallBack_Teuchos_ParameterEntryValidator : public Teuchos::ParameterEntryValidator {
	using Teuchos::ParameterEntryValidator::ParameterEntryValidator;

	const std::string getXMLTypeName() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterEntryValidator *>(this), "getXMLTypeName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const std::string>::value) {
				static pybind11::detail::override_caster_t<const std::string> caster;
				return pybind11::detail::cast_ref<const std::string>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const std::string>(std::move(o));
		}
		pybind11::pybind11_fail("Tried to call pure virtual function \"ParameterEntryValidator::getXMLTypeName\"");
	}
	void printDoc(const std::string & a0, std::ostream & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterEntryValidator *>(this), "printDoc");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		pybind11::pybind11_fail("Tried to call pure virtual function \"ParameterEntryValidator::printDoc\"");
	}
	class Teuchos::RCP<const class Teuchos::Array<std::string > > validStringValues() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterEntryValidator *>(this), "validStringValues");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<class Teuchos::RCP<const class Teuchos::Array<std::string > >>::value) {
				static pybind11::detail::override_caster_t<class Teuchos::RCP<const class Teuchos::Array<std::string > >> caster;
				return pybind11::detail::cast_ref<class Teuchos::RCP<const class Teuchos::Array<std::string > >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class Teuchos::RCP<const class Teuchos::Array<std::string > >>(std::move(o));
		}
		pybind11::pybind11_fail("Tried to call pure virtual function \"ParameterEntryValidator::validStringValues\"");
	}
	void validate(const class Teuchos::ParameterEntry & a0, const std::string & a1, const std::string & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterEntryValidator *>(this), "validate");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		pybind11::pybind11_fail("Tried to call pure virtual function \"ParameterEntryValidator::validate\"");
	}
	void validateAndModify(const std::string & a0, const std::string & a1, class Teuchos::ParameterEntry * a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterEntryValidator *>(this), "validateAndModify");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ParameterEntryValidator::validateAndModify(a0, a1, a2);
	}
	std::string description() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterEntryValidator *>(this), "description");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<std::string>::value) {
				static pybind11::detail::override_caster_t<std::string> caster;
				return pybind11::detail::cast_ref<std::string>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<std::string>(std::move(o));
		}
		return Describable::description();
	}
	void describe(class Teuchos::basic_FancyOStream<char> & a0, const enum Teuchos::EVerbosityLevel a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterEntryValidator *>(this), "describe");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Describable::describe(a0, a1);
	}
	void setObjectLabel(const std::string & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterEntryValidator *>(this), "setObjectLabel");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LabeledObject::setObjectLabel(a0);
	}
	std::string getObjectLabel() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterEntryValidator *>(this), "getObjectLabel");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<std::string>::value) {
				static pybind11::detail::override_caster_t<std::string> caster;
				return pybind11::detail::cast_ref<std::string>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<std::string>(std::move(o));
		}
		return LabeledObject::getObjectLabel();
	}
};

// Teuchos::ParameterListModifier file:Teuchos_ParameterListModifier.hpp line:36
struct PyCallBack_Teuchos_ParameterListModifier : public Teuchos::ParameterListModifier {
	using Teuchos::ParameterListModifier::ParameterListModifier;

	void modify(class Teuchos::ParameterList & a0, class Teuchos::ParameterList & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterListModifier *>(this), "modify");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ParameterListModifier::modify(a0, a1);
	}
	void reconcile(class Teuchos::ParameterList & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterListModifier *>(this), "reconcile");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ParameterListModifier::reconcile(a0);
	}
	std::string description() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterListModifier *>(this), "description");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<std::string>::value) {
				static pybind11::detail::override_caster_t<std::string> caster;
				return pybind11::detail::cast_ref<std::string>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<std::string>(std::move(o));
		}
		return Describable::description();
	}
	void describe(class Teuchos::basic_FancyOStream<char> & a0, const enum Teuchos::EVerbosityLevel a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterListModifier *>(this), "describe");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Describable::describe(a0, a1);
	}
	void setObjectLabel(const std::string & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterListModifier *>(this), "setObjectLabel");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LabeledObject::setObjectLabel(a0);
	}
	std::string getObjectLabel() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::ParameterListModifier *>(this), "getObjectLabel");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<std::string>::value) {
				static pybind11::detail::override_caster_t<std::string> caster;
				return pybind11::detail::cast_ref<std::string>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<std::string>(std::move(o));
		}
		return LabeledObject::getObjectLabel();
	}
};

// Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError file:Teuchos_StringIndexedOrderedValueObjectContainer.hpp line:119
struct PyCallBack_Teuchos_StringIndexedOrderedValueObjectContainerBase_InvalidOrdinalIndexError : public Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError {
	using Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError::InvalidOrdinalIndexError;

	const char * what() const throw() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError *>(this), "what");
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

// Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError file:Teuchos_StringIndexedOrderedValueObjectContainer.hpp line:123
struct PyCallBack_Teuchos_StringIndexedOrderedValueObjectContainerBase_InvalidKeyError : public Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError {
	using Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError::InvalidKeyError;

	const char * what() const throw() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError *>(this), "what");
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

// Teuchos::InvalidDependencyException file:Teuchos_InvalidDependencyException.hpp line:19
struct PyCallBack_Teuchos_InvalidDependencyException : public Teuchos::InvalidDependencyException {
	using Teuchos::InvalidDependencyException::InvalidDependencyException;

	const char * what() const throw() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const Teuchos::InvalidDependencyException *>(this), "what");
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

void bind_pyrol_41(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // Teuchos::basic_FancyOStream_buf file:Teuchos_FancyOStream.hpp line:31
		pybind11::class_<Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>, Teuchos::RCP<Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>>, PyCallBack_Teuchos_basic_FancyOStream_buf_char_std_char_traits_char_t> cl(M("Teuchos"), "basic_FancyOStream_buf_char_std_char_traits_char_t", "", pybind11::module_local());
		cl.def( pybind11::init<const class Teuchos::RCP<std::ostream > &, const std::string &, const int, const bool, const int, const bool, const bool>(), pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"), pybind11::arg("maxLenLinePrefix"), pybind11::arg("showTabCount"), pybind11::arg("showProcRank") );

		cl.def("initialize", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)(const class Teuchos::RCP<std::ostream > &, const std::string &, const int, const bool, const int, const bool, const bool)) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::initialize, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::initialize(const class Teuchos::RCP<std::ostream > &, const std::string &, const int, const bool, const int, const bool, const bool) --> void", pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"), pybind11::arg("maxLenLinePrefix"), pybind11::arg("showTabCount"), pybind11::arg("showProcRank"));
		cl.def("getOStream", (class Teuchos::RCP<std::ostream > (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)()) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getOStream, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getOStream() --> class Teuchos::RCP<std::ostream >");
		cl.def("setTabIndentStr", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)(const std::string &)) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setTabIndentStr, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setTabIndentStr(const std::string &) --> void", pybind11::arg("tabIndentStr"));
		cl.def("getTabIndentStr", (const std::string & (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getTabIndentStr, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getTabIndentStr() const --> const std::string &", pybind11::return_value_policy::automatic);
		cl.def("setShowLinePrefix", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)(const bool)) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setShowLinePrefix, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setShowLinePrefix(const bool) --> void", pybind11::arg("showLinePrefix"));
		cl.def("getShowLinePrefix", (bool (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getShowLinePrefix, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getShowLinePrefix() const --> bool");
		cl.def("setMaxLenLinePrefix", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)(const int)) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setMaxLenLinePrefix, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setMaxLenLinePrefix(const int) --> void", pybind11::arg("maxLenLinePrefix"));
		cl.def("getMaxLenLinePrefix", (int (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getMaxLenLinePrefix, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getMaxLenLinePrefix() const --> int");
		cl.def("setShowTabCount", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)(const bool)) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setShowTabCount, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setShowTabCount(const bool) --> void", pybind11::arg("showTabCount"));
		cl.def("getShowTabCount", (bool (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getShowTabCount, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getShowTabCount() const --> bool");
		cl.def("setShowProcRank", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)(const bool)) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setShowProcRank, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setShowProcRank(const bool) --> void", pybind11::arg("showProcRank"));
		cl.def("getShowProcRank", (bool (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getShowProcRank, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getShowProcRank() const --> bool");
		cl.def("setProcRankAndSize", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)(const int, const int)) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setProcRankAndSize, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setProcRankAndSize(const int, const int) --> void", pybind11::arg("procRank"), pybind11::arg("numProcs"));
		cl.def("getProcRank", (int (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getProcRank, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getProcRank() const --> int");
		cl.def("getNumProcs", (int (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getNumProcs, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getNumProcs() const --> int");
		cl.def("setOutputToRootOnly", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)(const int)) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setOutputToRootOnly, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::setOutputToRootOnly(const int) --> void", pybind11::arg("rootRank"));
		cl.def("getOutputToRootOnly", (int (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getOutputToRootOnly, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getOutputToRootOnly() const --> int");
		cl.def("pushTab", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)(const int)) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::pushTab, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::pushTab(const int) --> void", pybind11::arg("tabs"));
		cl.def("getNumCurrTabs", (int (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getNumCurrTabs, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getNumCurrTabs() const --> int");
		cl.def("popTab", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)()) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::popTab, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::popTab() --> void");
		cl.def("pushLinePrefix", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)(const std::string &)) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::pushLinePrefix, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::pushLinePrefix(const std::string &) --> void", pybind11::arg("linePrefix"));
		cl.def("popLinePrefix", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)()) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::popLinePrefix, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::popLinePrefix() --> void");
		cl.def("getTopLinePrefix", (const std::string & (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getTopLinePrefix, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::getTopLinePrefix() const --> const std::string &", pybind11::return_value_policy::automatic);
		cl.def("pushDisableTabbing", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)()) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::pushDisableTabbing, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::pushDisableTabbing() --> void");
		cl.def("popDisableTabbing", (void (Teuchos::basic_FancyOStream_buf<char,std::char_traits<char>>::*)()) &Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::popDisableTabbing, "C++: Teuchos::basic_FancyOStream_buf<char, std::char_traits<char>>::popDisableTabbing() --> void");
	}
	{ // Teuchos::basic_FancyOStream file:Teuchos_FancyOStream.hpp line:349
		pybind11::class_<Teuchos::basic_FancyOStream<char,std::char_traits<char>>, Teuchos::RCP<Teuchos::basic_FancyOStream<char,std::char_traits<char>>>, std::ostream> cl(M("Teuchos"), "basic_FancyOStream_char_std_char_traits_char_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](const class Teuchos::RCP<std::ostream > & a0){ return new Teuchos::basic_FancyOStream<char,std::char_traits<char>>(a0); } ), "doc" , pybind11::arg("oStream"));
		cl.def( pybind11::init( [](const class Teuchos::RCP<std::ostream > & a0, const std::string & a1){ return new Teuchos::basic_FancyOStream<char,std::char_traits<char>>(a0, a1); } ), "doc" , pybind11::arg("oStream"), pybind11::arg("tabIndentStr"));
		cl.def( pybind11::init( [](const class Teuchos::RCP<std::ostream > & a0, const std::string & a1, const int & a2){ return new Teuchos::basic_FancyOStream<char,std::char_traits<char>>(a0, a1, a2); } ), "doc" , pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"));
		cl.def( pybind11::init( [](const class Teuchos::RCP<std::ostream > & a0, const std::string & a1, const int & a2, const bool & a3){ return new Teuchos::basic_FancyOStream<char,std::char_traits<char>>(a0, a1, a2, a3); } ), "doc" , pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"));
		cl.def( pybind11::init( [](const class Teuchos::RCP<std::ostream > & a0, const std::string & a1, const int & a2, const bool & a3, const int & a4){ return new Teuchos::basic_FancyOStream<char,std::char_traits<char>>(a0, a1, a2, a3, a4); } ), "doc" , pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"), pybind11::arg("maxLenLinePrefix"));
		cl.def( pybind11::init( [](const class Teuchos::RCP<std::ostream > & a0, const std::string & a1, const int & a2, const bool & a3, const int & a4, const bool & a5){ return new Teuchos::basic_FancyOStream<char,std::char_traits<char>>(a0, a1, a2, a3, a4, a5); } ), "doc" , pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"), pybind11::arg("maxLenLinePrefix"), pybind11::arg("showTabCount"));
		cl.def( pybind11::init<const class Teuchos::RCP<std::ostream > &, const std::string &, const int, const bool, const int, const bool, const bool>(), pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"), pybind11::arg("maxLenLinePrefix"), pybind11::arg("showTabCount"), pybind11::arg("showProcRank") );

		cl.def("initialize", [](Teuchos::basic_FancyOStream<char,std::char_traits<char>> &o, const class Teuchos::RCP<std::ostream > & a0) -> void { return o.initialize(a0); }, "", pybind11::arg("oStream"));
		cl.def("initialize", [](Teuchos::basic_FancyOStream<char,std::char_traits<char>> &o, const class Teuchos::RCP<std::ostream > & a0, const std::string & a1) -> void { return o.initialize(a0, a1); }, "", pybind11::arg("oStream"), pybind11::arg("tabIndentStr"));
		cl.def("initialize", [](Teuchos::basic_FancyOStream<char,std::char_traits<char>> &o, const class Teuchos::RCP<std::ostream > & a0, const std::string & a1, const int & a2) -> void { return o.initialize(a0, a1, a2); }, "", pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"));
		cl.def("initialize", [](Teuchos::basic_FancyOStream<char,std::char_traits<char>> &o, const class Teuchos::RCP<std::ostream > & a0, const std::string & a1, const int & a2, const bool & a3) -> void { return o.initialize(a0, a1, a2, a3); }, "", pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"));
		cl.def("initialize", [](Teuchos::basic_FancyOStream<char,std::char_traits<char>> &o, const class Teuchos::RCP<std::ostream > & a0, const std::string & a1, const int & a2, const bool & a3, const int & a4) -> void { return o.initialize(a0, a1, a2, a3, a4); }, "", pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"), pybind11::arg("maxLenLinePrefix"));
		cl.def("initialize", [](Teuchos::basic_FancyOStream<char,std::char_traits<char>> &o, const class Teuchos::RCP<std::ostream > & a0, const std::string & a1, const int & a2, const bool & a3, const int & a4, const bool & a5) -> void { return o.initialize(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"), pybind11::arg("maxLenLinePrefix"), pybind11::arg("showTabCount"));
		cl.def("initialize", (void (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)(const class Teuchos::RCP<std::ostream > &, const std::string &, const int, const bool, const int, const bool, const bool)) &Teuchos::basic_FancyOStream<char>::initialize, "C++: Teuchos::basic_FancyOStream<char>::initialize(const class Teuchos::RCP<std::ostream > &, const std::string &, const int, const bool, const int, const bool, const bool) --> void", pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"), pybind11::arg("maxLenLinePrefix"), pybind11::arg("showTabCount"), pybind11::arg("showProcRank"));
		cl.def("getOStream", (class Teuchos::RCP<std::ostream > (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)()) &Teuchos::basic_FancyOStream<char>::getOStream, "C++: Teuchos::basic_FancyOStream<char>::getOStream() --> class Teuchos::RCP<std::ostream >");
		cl.def("setTabIndentStr", (class Teuchos::basic_FancyOStream<char> & (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)(const std::string &)) &Teuchos::basic_FancyOStream<char>::setTabIndentStr, "C++: Teuchos::basic_FancyOStream<char>::setTabIndentStr(const std::string &) --> class Teuchos::basic_FancyOStream<char> &", pybind11::return_value_policy::automatic, pybind11::arg("tabIndentStr"));
		cl.def("getTabIndentStr", (const std::string & (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream<char>::getTabIndentStr, "C++: Teuchos::basic_FancyOStream<char>::getTabIndentStr() const --> const std::string &", pybind11::return_value_policy::automatic);
		cl.def("setShowAllFrontMatter", (class Teuchos::basic_FancyOStream<char> & (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)(const bool)) &Teuchos::basic_FancyOStream<char>::setShowAllFrontMatter, "C++: Teuchos::basic_FancyOStream<char>::setShowAllFrontMatter(const bool) --> class Teuchos::basic_FancyOStream<char> &", pybind11::return_value_policy::automatic, pybind11::arg("showAllFrontMatter"));
		cl.def("setShowLinePrefix", (class Teuchos::basic_FancyOStream<char> & (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)(const bool)) &Teuchos::basic_FancyOStream<char>::setShowLinePrefix, "C++: Teuchos::basic_FancyOStream<char>::setShowLinePrefix(const bool) --> class Teuchos::basic_FancyOStream<char> &", pybind11::return_value_policy::automatic, pybind11::arg("showLinePrefix"));
		cl.def("setMaxLenLinePrefix", (class Teuchos::basic_FancyOStream<char> & (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)(const int)) &Teuchos::basic_FancyOStream<char>::setMaxLenLinePrefix, "C++: Teuchos::basic_FancyOStream<char>::setMaxLenLinePrefix(const int) --> class Teuchos::basic_FancyOStream<char> &", pybind11::return_value_policy::automatic, pybind11::arg("maxLenLinePrefix"));
		cl.def("setShowTabCount", (class Teuchos::basic_FancyOStream<char> & (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)(const bool)) &Teuchos::basic_FancyOStream<char>::setShowTabCount, "C++: Teuchos::basic_FancyOStream<char>::setShowTabCount(const bool) --> class Teuchos::basic_FancyOStream<char> &", pybind11::return_value_policy::automatic, pybind11::arg("showTabCount"));
		cl.def("setShowProcRank", (class Teuchos::basic_FancyOStream<char> & (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)(const bool)) &Teuchos::basic_FancyOStream<char>::setShowProcRank, "C++: Teuchos::basic_FancyOStream<char>::setShowProcRank(const bool) --> class Teuchos::basic_FancyOStream<char> &", pybind11::return_value_policy::automatic, pybind11::arg("showProcRank"));
		cl.def("setProcRankAndSize", (class Teuchos::basic_FancyOStream<char> & (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)(const int, const int)) &Teuchos::basic_FancyOStream<char>::setProcRankAndSize, "C++: Teuchos::basic_FancyOStream<char>::setProcRankAndSize(const int, const int) --> class Teuchos::basic_FancyOStream<char> &", pybind11::return_value_policy::automatic, pybind11::arg("procRank"), pybind11::arg("numProcs"));
		cl.def("setOutputToRootOnly", (class Teuchos::basic_FancyOStream<char> & (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)(const int)) &Teuchos::basic_FancyOStream<char>::setOutputToRootOnly, "C++: Teuchos::basic_FancyOStream<char>::setOutputToRootOnly(const int) --> class Teuchos::basic_FancyOStream<char> &", pybind11::return_value_policy::automatic, pybind11::arg("rootRank"));
		cl.def("getOutputToRootOnly", (int (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream<char>::getOutputToRootOnly, "C++: Teuchos::basic_FancyOStream<char>::getOutputToRootOnly() const --> int");
		cl.def("copyAllOutputOptions", (void (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)(const class Teuchos::basic_FancyOStream<char> &)) &Teuchos::basic_FancyOStream<char>::copyAllOutputOptions, "C++: Teuchos::basic_FancyOStream<char>::copyAllOutputOptions(const class Teuchos::basic_FancyOStream<char> &) --> void", pybind11::arg("oStream"));
		cl.def("pushTab", [](Teuchos::basic_FancyOStream<char,std::char_traits<char>> &o) -> void { return o.pushTab(); }, "");
		cl.def("pushTab", (void (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)(const int)) &Teuchos::basic_FancyOStream<char>::pushTab, "C++: Teuchos::basic_FancyOStream<char>::pushTab(const int) --> void", pybind11::arg("tabs"));
		cl.def("getNumCurrTabs", (int (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream<char>::getNumCurrTabs, "C++: Teuchos::basic_FancyOStream<char>::getNumCurrTabs() const --> int");
		cl.def("popTab", (void (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)()) &Teuchos::basic_FancyOStream<char>::popTab, "C++: Teuchos::basic_FancyOStream<char>::popTab() --> void");
		cl.def("pushLinePrefix", (void (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)(const std::string &)) &Teuchos::basic_FancyOStream<char>::pushLinePrefix, "C++: Teuchos::basic_FancyOStream<char>::pushLinePrefix(const std::string &) --> void", pybind11::arg("linePrefix"));
		cl.def("popLinePrefix", (void (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)()) &Teuchos::basic_FancyOStream<char>::popLinePrefix, "C++: Teuchos::basic_FancyOStream<char>::popLinePrefix() --> void");
		cl.def("getTopLinePrefix", (const std::string & (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)() const) &Teuchos::basic_FancyOStream<char>::getTopLinePrefix, "C++: Teuchos::basic_FancyOStream<char>::getTopLinePrefix() const --> const std::string &", pybind11::return_value_policy::automatic);
		cl.def("pushDisableTabbing", (void (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)()) &Teuchos::basic_FancyOStream<char>::pushDisableTabbing, "C++: Teuchos::basic_FancyOStream<char>::pushDisableTabbing() --> void");
		cl.def("popDisableTabbing", (void (Teuchos::basic_FancyOStream<char,std::char_traits<char>>::*)()) &Teuchos::basic_FancyOStream<char>::popDisableTabbing, "C++: Teuchos::basic_FancyOStream<char>::popDisableTabbing() --> void");
		cl.def("put", (std::ostream & (std::ostream::*)(char)) &std::ostream::put, "C++: std::ostream::put(char) --> std::ostream &", pybind11::return_value_policy::automatic, pybind11::arg("__c"));
		cl.def("write", (std::ostream & (std::ostream::*)(const char *, long)) &std::ostream::write, "C++: std::ostream::write(const char *, long) --> std::ostream &", pybind11::return_value_policy::automatic, pybind11::arg("__s"), pybind11::arg("__n"));
		cl.def("flush", (std::ostream & (std::ostream::*)()) &std::ostream::flush, "C++: std::ostream::flush() --> std::ostream &", pybind11::return_value_policy::automatic);
	}
	// Teuchos::fancyOStream(const class Teuchos::RCP<std::ostream > &, const std::string &, const int, const bool, const int, const bool, const bool) file:Teuchos_FancyOStream.hpp line:565
	M("Teuchos").def("fancyOStream", [](const class Teuchos::RCP<std::ostream > & a0) -> Teuchos::RCP<class Teuchos::basic_FancyOStream<char> > { return Teuchos::fancyOStream(a0); }, "", pybind11::arg("oStream"));
	M("Teuchos").def("fancyOStream", [](const class Teuchos::RCP<std::ostream > & a0, const std::string & a1) -> Teuchos::RCP<class Teuchos::basic_FancyOStream<char> > { return Teuchos::fancyOStream(a0, a1); }, "", pybind11::arg("oStream"), pybind11::arg("tabIndentStr"));
	M("Teuchos").def("fancyOStream", [](const class Teuchos::RCP<std::ostream > & a0, const std::string & a1, const int & a2) -> Teuchos::RCP<class Teuchos::basic_FancyOStream<char> > { return Teuchos::fancyOStream(a0, a1, a2); }, "", pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"));
	M("Teuchos").def("fancyOStream", [](const class Teuchos::RCP<std::ostream > & a0, const std::string & a1, const int & a2, const bool & a3) -> Teuchos::RCP<class Teuchos::basic_FancyOStream<char> > { return Teuchos::fancyOStream(a0, a1, a2, a3); }, "", pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"));
	M("Teuchos").def("fancyOStream", [](const class Teuchos::RCP<std::ostream > & a0, const std::string & a1, const int & a2, const bool & a3, const int & a4) -> Teuchos::RCP<class Teuchos::basic_FancyOStream<char> > { return Teuchos::fancyOStream(a0, a1, a2, a3, a4); }, "", pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"), pybind11::arg("maxLenLinePrefix"));
	M("Teuchos").def("fancyOStream", [](const class Teuchos::RCP<std::ostream > & a0, const std::string & a1, const int & a2, const bool & a3, const int & a4, const bool & a5) -> Teuchos::RCP<class Teuchos::basic_FancyOStream<char> > { return Teuchos::fancyOStream(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"), pybind11::arg("maxLenLinePrefix"), pybind11::arg("showTabCount"));
	M("Teuchos").def("fancyOStream", (class Teuchos::RCP<class Teuchos::basic_FancyOStream<char> > (*)(const class Teuchos::RCP<std::ostream > &, const std::string &, const int, const bool, const int, const bool, const bool)) &Teuchos::fancyOStream, "Dynamically allocate a FancyOStream and return it wrapped in an RCP\n object.\n\n Returns a null object if the input stream is null.\n\n \n\n \n\nC++: Teuchos::fancyOStream(const class Teuchos::RCP<std::ostream > &, const std::string &, const int, const bool, const int, const bool, const bool) --> class Teuchos::RCP<class Teuchos::basic_FancyOStream<char> >", pybind11::arg("oStream"), pybind11::arg("tabIndentStr"), pybind11::arg("startingTab"), pybind11::arg("showLinePrefix"), pybind11::arg("maxLenLinePrefix"), pybind11::arg("showTabCount"), pybind11::arg("showProcRank"));

	// Teuchos::getFancyOStream(const class Teuchos::RCP<std::ostream > &) file:Teuchos_FancyOStream.hpp line:597
	M("Teuchos").def("getFancyOStream", (class Teuchos::RCP<class Teuchos::basic_FancyOStream<char> > (*)(const class Teuchos::RCP<std::ostream > &)) &Teuchos::getFancyOStream, "Get a FancyOStream from an std::ostream object.\n\n If the object already is a FancyOStream, then nothing has to be done.\n Otherwise, a temp FancyOStream is created for this purpose. If\n out.get()==NULL then return.get()==NULL on return also!\n\n \n\n \n\nC++: Teuchos::getFancyOStream(const class Teuchos::RCP<std::ostream > &) --> class Teuchos::RCP<class Teuchos::basic_FancyOStream<char> >", pybind11::arg("out"));

	{ // Teuchos::LabeledObject file:Teuchos_LabeledObject.hpp line:37
		pybind11::class_<Teuchos::LabeledObject, Teuchos::RCP<Teuchos::LabeledObject>, PyCallBack_Teuchos_LabeledObject> cl(M("Teuchos"), "LabeledObject", "Base class for objects that contain a std::string label.\n\n The object label std::string objectLabel set in\n setObjectLabel() should be a simple one-line label given to an\n object to differentiate it from all other objects.  A subclass\n implementation can define a default label in some cases but typically this\n label is designed for end users to set to give the object a name that is\n meaningful to the user.  The label should not contain any information about\n the actual type of the object.  Adding type information is appropriate in\n the Describable interface, which inherits from this interface.\n\n This base class provides a default implementation for the functions\n setObjectLabel() and getObjectLabel() as well as private\n data to hold the label.  Subclasses can override these functions but\n general, there should be no need to do so.\n\n \n\n ", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::LabeledObject(); }, [](){ return new PyCallBack_Teuchos_LabeledObject(); } ) );
		cl.def( pybind11::init( [](PyCallBack_Teuchos_LabeledObject const &o){ return new PyCallBack_Teuchos_LabeledObject(o); } ) );
		cl.def( pybind11::init( [](Teuchos::LabeledObject const &o){ return new Teuchos::LabeledObject(o); } ) );
		cl.def("setObjectLabel", (void (Teuchos::LabeledObject::*)(const std::string &)) &Teuchos::LabeledObject::setObjectLabel, "Set the object label (see LabeledObject). \n\nC++: Teuchos::LabeledObject::setObjectLabel(const std::string &) --> void", pybind11::arg("objectLabel"));
		cl.def("getObjectLabel", (std::string (Teuchos::LabeledObject::*)() const) &Teuchos::LabeledObject::getObjectLabel, "Get the object label (see LabeledObject). \n\nC++: Teuchos::LabeledObject::getObjectLabel() const --> std::string");
		cl.def("assign", (class Teuchos::LabeledObject & (Teuchos::LabeledObject::*)(const class Teuchos::LabeledObject &)) &Teuchos::LabeledObject::operator=, "C++: Teuchos::LabeledObject::operator=(const class Teuchos::LabeledObject &) --> class Teuchos::LabeledObject &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // Teuchos::DescribableStreamManipulatorState file:Teuchos_Describable.hpp line:143
		pybind11::class_<Teuchos::DescribableStreamManipulatorState, Teuchos::RCP<Teuchos::DescribableStreamManipulatorState>> cl(M("Teuchos"), "DescribableStreamManipulatorState", "", pybind11::module_local());
		cl.def( pybind11::init( [](Teuchos::DescribableStreamManipulatorState const &o){ return new Teuchos::DescribableStreamManipulatorState(o); } ) );
		cl.def_readonly("verbLevel", &Teuchos::DescribableStreamManipulatorState::verbLevel);

		cl.def("__str__", [](Teuchos::DescribableStreamManipulatorState const &o) -> std::string { std::ostringstream s; using namespace Teuchos; s << o; return s.str(); } );
	}
	{ // Teuchos::Utils file:Teuchos_Utils.hpp line:27
		pybind11::class_<Teuchos::Utils, Teuchos::RCP<Teuchos::Utils>> cl(M("Teuchos"), "Utils", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::Utils(); } ) );
		cl.def_static("chop", (double (*)(const double &)) &Teuchos::Utils::chop, "Set a number to zero if it is less than\n getChopVal(). \n\nC++: Teuchos::Utils::chop(const double &) --> double", pybind11::arg("x"));
		cl.def_static("getChopVal", (double (*)()) &Teuchos::Utils::getChopVal, "Get the chopping value, below which numbers are considered to\n be zero. \n\nC++: Teuchos::Utils::getChopVal() --> double");
		cl.def_static("setChopVal", (void (*)(double)) &Teuchos::Utils::setChopVal, "Set the chopping value, below which numbers are considered to\n be zero. \n\nC++: Teuchos::Utils::setChopVal(double) --> void", pybind11::arg("chopVal"));
		cl.def_static("isWhiteSpace", (bool (*)(const char)) &Teuchos::Utils::isWhiteSpace, "Determine if a char is whitespace or not. \n\nC++: Teuchos::Utils::isWhiteSpace(const char) --> bool", pybind11::arg("c"));
		cl.def_static("trimWhiteSpace", (std::string (*)(const std::string &)) &Teuchos::Utils::trimWhiteSpace, "Trim whitespace from beginning and end of std::string. \n\nC++: Teuchos::Utils::trimWhiteSpace(const std::string &) --> std::string", pybind11::arg("str"));
		cl.def_static("toString", (std::string (*)(const double &)) &Teuchos::Utils::toString, "Write a double as a std::string. \n\nC++: Teuchos::Utils::toString(const double &) --> std::string", pybind11::arg("x"));
		cl.def_static("toString", (std::string (*)(const int &)) &Teuchos::Utils::toString, "Write an int as a std::string. \n\nC++: Teuchos::Utils::toString(const int &) --> std::string", pybind11::arg("x"));
		cl.def_static("toString", (std::string (*)(const long long &)) &Teuchos::Utils::toString, "Write a long long as a std::string. \n\nC++: Teuchos::Utils::toString(const long long &) --> std::string", pybind11::arg("x"));
		cl.def_static("toString", (std::string (*)(const unsigned int &)) &Teuchos::Utils::toString, "Write an unsigned int as a std::string. \n\nC++: Teuchos::Utils::toString(const unsigned int &) --> std::string", pybind11::arg("x"));
		cl.def_static("pi", (double (*)()) &Teuchos::Utils::pi, "C++: Teuchos::Utils::pi() --> double");
		cl.def_static("getParallelExtension", []() -> std::string { return Teuchos::Utils::getParallelExtension(); }, "");
		cl.def_static("getParallelExtension", [](int const & a0) -> std::string { return Teuchos::Utils::getParallelExtension(a0); }, "", pybind11::arg("procRank"));
		cl.def_static("getParallelExtension", (std::string (*)(int, int)) &Teuchos::Utils::getParallelExtension, "Get a parallel file name extention . \n\nC++: Teuchos::Utils::getParallelExtension(int, int) --> std::string", pybind11::arg("procRank"), pybind11::arg("numProcs"));
	}
	{ // Teuchos::InvalidArrayStringRepresentation file:Teuchos_Array.hpp line:36
		pybind11::class_<Teuchos::InvalidArrayStringRepresentation, Teuchos::RCP<Teuchos::InvalidArrayStringRepresentation>, PyCallBack_Teuchos_InvalidArrayStringRepresentation> cl(M("Teuchos"), "InvalidArrayStringRepresentation", ".\n\n \n\n ", pybind11::module_local());
		cl.def( pybind11::init<const std::string &>(), pybind11::arg("what_arg") );

		cl.def( pybind11::init( [](PyCallBack_Teuchos_InvalidArrayStringRepresentation const &o){ return new PyCallBack_Teuchos_InvalidArrayStringRepresentation(o); } ) );
		cl.def( pybind11::init( [](Teuchos::InvalidArrayStringRepresentation const &o){ return new Teuchos::InvalidArrayStringRepresentation(o); } ) );
		cl.def("assign", (class Teuchos::InvalidArrayStringRepresentation & (Teuchos::InvalidArrayStringRepresentation::*)(const class Teuchos::InvalidArrayStringRepresentation &)) &Teuchos::InvalidArrayStringRepresentation::operator=, "C++: Teuchos::InvalidArrayStringRepresentation::operator=(const class Teuchos::InvalidArrayStringRepresentation &) --> class Teuchos::InvalidArrayStringRepresentation &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // Teuchos::Array file:Teuchos_Array.hpp line:162
		pybind11::class_<Teuchos::Array<Teuchos::XMLObject>, Teuchos::RCP<Teuchos::Array<Teuchos::XMLObject>>> cl(M("Teuchos"), "Array_Teuchos_XMLObject_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::Array<Teuchos::XMLObject>(); } ) );
		cl.def( pybind11::init( [](long const & a0){ return new Teuchos::Array<Teuchos::XMLObject>(a0); } ), "doc" , pybind11::arg("n"));
		cl.def( pybind11::init<long, const class Teuchos::XMLObject &>(), pybind11::arg("n"), pybind11::arg("value") );

		cl.def( pybind11::init( [](Teuchos::Array<Teuchos::XMLObject> const &o){ return new Teuchos::Array<Teuchos::XMLObject>(o); } ) );
		cl.def("assign", (class Teuchos::Array<class Teuchos::XMLObject> & (Teuchos::Array<Teuchos::XMLObject>::*)(const class Teuchos::Array<class Teuchos::XMLObject> &)) &Teuchos::Array<Teuchos::XMLObject>::operator=, "C++: Teuchos::Array<Teuchos::XMLObject>::operator=(const class Teuchos::Array<class Teuchos::XMLObject> &) --> class Teuchos::Array<class Teuchos::XMLObject> &", pybind11::return_value_policy::automatic, pybind11::arg("a"));
		cl.def("assign", (void (Teuchos::Array<Teuchos::XMLObject>::*)(long, const class Teuchos::XMLObject &)) &Teuchos::Array<Teuchos::XMLObject>::assign, "C++: Teuchos::Array<Teuchos::XMLObject>::assign(long, const class Teuchos::XMLObject &) --> void", pybind11::arg("n"), pybind11::arg("val"));
		cl.def("size", (long (Teuchos::Array<Teuchos::XMLObject>::*)() const) &Teuchos::Array<Teuchos::XMLObject>::size, "C++: Teuchos::Array<Teuchos::XMLObject>::size() const --> long");
		cl.def("max_size", (long (Teuchos::Array<Teuchos::XMLObject>::*)() const) &Teuchos::Array<Teuchos::XMLObject>::max_size, "C++: Teuchos::Array<Teuchos::XMLObject>::max_size() const --> long");
		cl.def("resize", [](Teuchos::Array<Teuchos::XMLObject> &o, long const & a0) -> void { return o.resize(a0); }, "", pybind11::arg("new_size"));
		cl.def("resize", (void (Teuchos::Array<Teuchos::XMLObject>::*)(long, const class Teuchos::XMLObject &)) &Teuchos::Array<Teuchos::XMLObject>::resize, "C++: Teuchos::Array<Teuchos::XMLObject>::resize(long, const class Teuchos::XMLObject &) --> void", pybind11::arg("new_size"), pybind11::arg("x"));
		cl.def("capacity", (long (Teuchos::Array<Teuchos::XMLObject>::*)() const) &Teuchos::Array<Teuchos::XMLObject>::capacity, "C++: Teuchos::Array<Teuchos::XMLObject>::capacity() const --> long");
		cl.def("empty", (bool (Teuchos::Array<Teuchos::XMLObject>::*)() const) &Teuchos::Array<Teuchos::XMLObject>::empty, "C++: Teuchos::Array<Teuchos::XMLObject>::empty() const --> bool");
		cl.def("reserve", (void (Teuchos::Array<Teuchos::XMLObject>::*)(long)) &Teuchos::Array<Teuchos::XMLObject>::reserve, "C++: Teuchos::Array<Teuchos::XMLObject>::reserve(long) --> void", pybind11::arg("n"));
		cl.def("__getitem__", (class Teuchos::XMLObject & (Teuchos::Array<Teuchos::XMLObject>::*)(long)) &Teuchos::Array<Teuchos::XMLObject>::operator[], "C++: Teuchos::Array<Teuchos::XMLObject>::operator[](long) --> class Teuchos::XMLObject &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("at", (class Teuchos::XMLObject & (Teuchos::Array<Teuchos::XMLObject>::*)(long)) &Teuchos::Array<Teuchos::XMLObject>::at, "C++: Teuchos::Array<Teuchos::XMLObject>::at(long) --> class Teuchos::XMLObject &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("front", (class Teuchos::XMLObject & (Teuchos::Array<Teuchos::XMLObject>::*)()) &Teuchos::Array<Teuchos::XMLObject>::front, "C++: Teuchos::Array<Teuchos::XMLObject>::front() --> class Teuchos::XMLObject &", pybind11::return_value_policy::automatic);
		cl.def("back", (class Teuchos::XMLObject & (Teuchos::Array<Teuchos::XMLObject>::*)()) &Teuchos::Array<Teuchos::XMLObject>::back, "C++: Teuchos::Array<Teuchos::XMLObject>::back() --> class Teuchos::XMLObject &", pybind11::return_value_policy::automatic);
		cl.def("push_back", (void (Teuchos::Array<Teuchos::XMLObject>::*)(const class Teuchos::XMLObject &)) &Teuchos::Array<Teuchos::XMLObject>::push_back, "C++: Teuchos::Array<Teuchos::XMLObject>::push_back(const class Teuchos::XMLObject &) --> void", pybind11::arg("x"));
		cl.def("pop_back", (void (Teuchos::Array<Teuchos::XMLObject>::*)()) &Teuchos::Array<Teuchos::XMLObject>::pop_back, "C++: Teuchos::Array<Teuchos::XMLObject>::pop_back() --> void");
		cl.def("swap", (void (Teuchos::Array<Teuchos::XMLObject>::*)(class Teuchos::Array<class Teuchos::XMLObject> &)) &Teuchos::Array<Teuchos::XMLObject>::swap, "C++: Teuchos::Array<Teuchos::XMLObject>::swap(class Teuchos::Array<class Teuchos::XMLObject> &) --> void", pybind11::arg("x"));
		cl.def("clear", (void (Teuchos::Array<Teuchos::XMLObject>::*)()) &Teuchos::Array<Teuchos::XMLObject>::clear, "C++: Teuchos::Array<Teuchos::XMLObject>::clear() --> void");
		cl.def("append", (class Teuchos::Array<class Teuchos::XMLObject> & (Teuchos::Array<Teuchos::XMLObject>::*)(const class Teuchos::XMLObject &)) &Teuchos::Array<Teuchos::XMLObject>::append, "C++: Teuchos::Array<Teuchos::XMLObject>::append(const class Teuchos::XMLObject &) --> class Teuchos::Array<class Teuchos::XMLObject> &", pybind11::return_value_policy::automatic, pybind11::arg("x"));
		cl.def("remove", (void (Teuchos::Array<Teuchos::XMLObject>::*)(int)) &Teuchos::Array<Teuchos::XMLObject>::remove, "C++: Teuchos::Array<Teuchos::XMLObject>::remove(int) --> void", pybind11::arg("i"));
		cl.def("length", (int (Teuchos::Array<Teuchos::XMLObject>::*)() const) &Teuchos::Array<Teuchos::XMLObject>::length, "C++: Teuchos::Array<Teuchos::XMLObject>::length() const --> int");
		cl.def("toString", (std::string (Teuchos::Array<Teuchos::XMLObject>::*)() const) &Teuchos::Array<Teuchos::XMLObject>::toString, "C++: Teuchos::Array<Teuchos::XMLObject>::toString() const --> std::string");
		cl.def_static("hasBoundsChecking", (bool (*)()) &Teuchos::Array<Teuchos::XMLObject>::hasBoundsChecking, "C++: Teuchos::Array<Teuchos::XMLObject>::hasBoundsChecking() --> bool");
		cl.def("getRawPtr", (class Teuchos::XMLObject * (Teuchos::Array<Teuchos::XMLObject>::*)()) &Teuchos::Array<Teuchos::XMLObject>::getRawPtr, "C++: Teuchos::Array<Teuchos::XMLObject>::getRawPtr() --> class Teuchos::XMLObject *", pybind11::return_value_policy::automatic);
		cl.def("data", (class Teuchos::XMLObject * (Teuchos::Array<Teuchos::XMLObject>::*)()) &Teuchos::Array<Teuchos::XMLObject>::data, "C++: Teuchos::Array<Teuchos::XMLObject>::data() --> class Teuchos::XMLObject *", pybind11::return_value_policy::automatic);

		cl.def("__str__", [](Teuchos::Array<Teuchos::XMLObject> const &o) -> std::string { std::ostringstream s; using namespace Teuchos; s << o; return s.str(); } );
	}
	{ // Teuchos::Array file:Teuchos_Array.hpp line:162
		pybind11::class_<Teuchos::Array<std::string>, Teuchos::RCP<Teuchos::Array<std::string>>> cl(M("Teuchos"), "Array_std_string_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::Array<std::string>(); } ) );
		cl.def( pybind11::init( [](long const & a0){ return new Teuchos::Array<std::string>(a0); } ), "doc" , pybind11::arg("n"));
		cl.def( pybind11::init<long, const std::string &>(), pybind11::arg("n"), pybind11::arg("value") );

		cl.def( pybind11::init( [](Teuchos::Array<std::string> const &o){ return new Teuchos::Array<std::string>(o); } ) );
		cl.def("assign", (class Teuchos::Array<std::string > & (Teuchos::Array<std::string>::*)(const class Teuchos::Array<std::string > &)) &Teuchos::Array<std::string>::operator=, "C++: Teuchos::Array<std::string>::operator=(const class Teuchos::Array<std::string > &) --> class Teuchos::Array<std::string > &", pybind11::return_value_policy::automatic, pybind11::arg("a"));
		cl.def("assign", (void (Teuchos::Array<std::string>::*)(long, const std::string &)) &Teuchos::Array<std::string>::assign, "C++: Teuchos::Array<std::string>::assign(long, const std::string &) --> void", pybind11::arg("n"), pybind11::arg("val"));
		cl.def("size", (long (Teuchos::Array<std::string>::*)() const) &Teuchos::Array<std::string>::size, "C++: Teuchos::Array<std::string>::size() const --> long");
		cl.def("max_size", (long (Teuchos::Array<std::string>::*)() const) &Teuchos::Array<std::string>::max_size, "C++: Teuchos::Array<std::string>::max_size() const --> long");
		cl.def("resize", [](Teuchos::Array<std::string> &o, long const & a0) -> void { return o.resize(a0); }, "", pybind11::arg("new_size"));
		cl.def("resize", (void (Teuchos::Array<std::string>::*)(long, const std::string &)) &Teuchos::Array<std::string>::resize, "C++: Teuchos::Array<std::string>::resize(long, const std::string &) --> void", pybind11::arg("new_size"), pybind11::arg("x"));
		cl.def("capacity", (long (Teuchos::Array<std::string>::*)() const) &Teuchos::Array<std::string>::capacity, "C++: Teuchos::Array<std::string>::capacity() const --> long");
		cl.def("empty", (bool (Teuchos::Array<std::string>::*)() const) &Teuchos::Array<std::string>::empty, "C++: Teuchos::Array<std::string>::empty() const --> bool");
		cl.def("reserve", (void (Teuchos::Array<std::string>::*)(long)) &Teuchos::Array<std::string>::reserve, "C++: Teuchos::Array<std::string>::reserve(long) --> void", pybind11::arg("n"));
		cl.def("__getitem__", (std::string & (Teuchos::Array<std::string>::*)(long)) &Teuchos::Array<std::string>::operator[], "C++: Teuchos::Array<std::string>::operator[](long) --> std::string &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("at", (std::string & (Teuchos::Array<std::string>::*)(long)) &Teuchos::Array<std::string>::at, "C++: Teuchos::Array<std::string>::at(long) --> std::string &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("front", (std::string & (Teuchos::Array<std::string>::*)()) &Teuchos::Array<std::string>::front, "C++: Teuchos::Array<std::string>::front() --> std::string &", pybind11::return_value_policy::automatic);
		cl.def("back", (std::string & (Teuchos::Array<std::string>::*)()) &Teuchos::Array<std::string>::back, "C++: Teuchos::Array<std::string>::back() --> std::string &", pybind11::return_value_policy::automatic);
		cl.def("push_back", (void (Teuchos::Array<std::string>::*)(const std::string &)) &Teuchos::Array<std::string>::push_back, "C++: Teuchos::Array<std::string>::push_back(const std::string &) --> void", pybind11::arg("x"));
		cl.def("pop_back", (void (Teuchos::Array<std::string>::*)()) &Teuchos::Array<std::string>::pop_back, "C++: Teuchos::Array<std::string>::pop_back() --> void");
		cl.def("swap", (void (Teuchos::Array<std::string>::*)(class Teuchos::Array<std::string > &)) &Teuchos::Array<std::string>::swap, "C++: Teuchos::Array<std::string>::swap(class Teuchos::Array<std::string > &) --> void", pybind11::arg("x"));
		cl.def("clear", (void (Teuchos::Array<std::string>::*)()) &Teuchos::Array<std::string>::clear, "C++: Teuchos::Array<std::string>::clear() --> void");
		cl.def("append", (class Teuchos::Array<std::string > & (Teuchos::Array<std::string>::*)(const std::string &)) &Teuchos::Array<std::string>::append, "C++: Teuchos::Array<std::string>::append(const std::string &) --> class Teuchos::Array<std::string > &", pybind11::return_value_policy::automatic, pybind11::arg("x"));
		cl.def("remove", (void (Teuchos::Array<std::string>::*)(int)) &Teuchos::Array<std::string>::remove, "C++: Teuchos::Array<std::string>::remove(int) --> void", pybind11::arg("i"));
		cl.def("length", (int (Teuchos::Array<std::string>::*)() const) &Teuchos::Array<std::string>::length, "C++: Teuchos::Array<std::string>::length() const --> int");
		cl.def("toString", (std::string (Teuchos::Array<std::string>::*)() const) &Teuchos::Array<std::string>::toString, "C++: Teuchos::Array<std::string>::toString() const --> std::string");
		cl.def_static("hasBoundsChecking", (bool (*)()) &Teuchos::Array<std::string>::hasBoundsChecking, "C++: Teuchos::Array<std::string>::hasBoundsChecking() --> bool");
		cl.def("getRawPtr", (std::string * (Teuchos::Array<std::string>::*)()) &Teuchos::Array<std::string>::getRawPtr, "C++: Teuchos::Array<std::string>::getRawPtr() --> std::string *", pybind11::return_value_policy::automatic);
		cl.def("data", (std::string * (Teuchos::Array<std::string>::*)()) &Teuchos::Array<std::string>::data, "C++: Teuchos::Array<std::string>::data() --> std::string *", pybind11::return_value_policy::automatic);

		cl.def("__str__", [](Teuchos::Array<std::string> const &o) -> std::string { std::ostringstream s; using namespace Teuchos; s << o; return s.str(); } );
	}
	{ // Teuchos::Array file:Teuchos_Array.hpp line:162
		pybind11::class_<Teuchos::Array<double>, Teuchos::RCP<Teuchos::Array<double>>> cl(M("Teuchos"), "Array_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::Array<double>(); } ) );
		cl.def( pybind11::init( [](long const & a0){ return new Teuchos::Array<double>(a0); } ), "doc" , pybind11::arg("n"));
		cl.def( pybind11::init<long, const double &>(), pybind11::arg("n"), pybind11::arg("value") );

		cl.def( pybind11::init( [](Teuchos::Array<double> const &o){ return new Teuchos::Array<double>(o); } ) );
		cl.def( pybind11::init<const class Teuchos::ArrayView<const double> &>(), pybind11::arg("a") );

		cl.def( pybind11::init<const class std::vector<double> &>(), pybind11::arg("v") );

		cl.def("assign", (class Teuchos::Array<double> & (Teuchos::Array<double>::*)(const class Teuchos::Array<double> &)) &Teuchos::Array<double>::operator=, "C++: Teuchos::Array<double>::operator=(const class Teuchos::Array<double> &) --> class Teuchos::Array<double> &", pybind11::return_value_policy::automatic, pybind11::arg("a"));
		cl.def("assign", (void (Teuchos::Array<double>::*)(long, const double &)) &Teuchos::Array<double>::assign, "C++: Teuchos::Array<double>::assign(long, const double &) --> void", pybind11::arg("n"), pybind11::arg("val"));
		cl.def("size", (long (Teuchos::Array<double>::*)() const) &Teuchos::Array<double>::size, "C++: Teuchos::Array<double>::size() const --> long");
		cl.def("max_size", (long (Teuchos::Array<double>::*)() const) &Teuchos::Array<double>::max_size, "C++: Teuchos::Array<double>::max_size() const --> long");
		cl.def("resize", [](Teuchos::Array<double> &o, long const & a0) -> void { return o.resize(a0); }, "", pybind11::arg("new_size"));
		cl.def("resize", (void (Teuchos::Array<double>::*)(long, const double &)) &Teuchos::Array<double>::resize, "C++: Teuchos::Array<double>::resize(long, const double &) --> void", pybind11::arg("new_size"), pybind11::arg("x"));
		cl.def("capacity", (long (Teuchos::Array<double>::*)() const) &Teuchos::Array<double>::capacity, "C++: Teuchos::Array<double>::capacity() const --> long");
		cl.def("empty", (bool (Teuchos::Array<double>::*)() const) &Teuchos::Array<double>::empty, "C++: Teuchos::Array<double>::empty() const --> bool");
		cl.def("reserve", (void (Teuchos::Array<double>::*)(long)) &Teuchos::Array<double>::reserve, "C++: Teuchos::Array<double>::reserve(long) --> void", pybind11::arg("n"));
		cl.def("__getitem__", (double & (Teuchos::Array<double>::*)(long)) &Teuchos::Array<double>::operator[], "C++: Teuchos::Array<double>::operator[](long) --> double &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("at", (double & (Teuchos::Array<double>::*)(long)) &Teuchos::Array<double>::at, "C++: Teuchos::Array<double>::at(long) --> double &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("front", (double & (Teuchos::Array<double>::*)()) &Teuchos::Array<double>::front, "C++: Teuchos::Array<double>::front() --> double &", pybind11::return_value_policy::automatic);
		cl.def("back", (double & (Teuchos::Array<double>::*)()) &Teuchos::Array<double>::back, "C++: Teuchos::Array<double>::back() --> double &", pybind11::return_value_policy::automatic);
		cl.def("push_back", (void (Teuchos::Array<double>::*)(const double &)) &Teuchos::Array<double>::push_back, "C++: Teuchos::Array<double>::push_back(const double &) --> void", pybind11::arg("x"));
		cl.def("pop_back", (void (Teuchos::Array<double>::*)()) &Teuchos::Array<double>::pop_back, "C++: Teuchos::Array<double>::pop_back() --> void");
		cl.def("swap", (void (Teuchos::Array<double>::*)(class Teuchos::Array<double> &)) &Teuchos::Array<double>::swap, "C++: Teuchos::Array<double>::swap(class Teuchos::Array<double> &) --> void", pybind11::arg("x"));
		cl.def("clear", (void (Teuchos::Array<double>::*)()) &Teuchos::Array<double>::clear, "C++: Teuchos::Array<double>::clear() --> void");
		cl.def("append", (class Teuchos::Array<double> & (Teuchos::Array<double>::*)(const double &)) &Teuchos::Array<double>::append, "C++: Teuchos::Array<double>::append(const double &) --> class Teuchos::Array<double> &", pybind11::return_value_policy::automatic, pybind11::arg("x"));
		cl.def("remove", (void (Teuchos::Array<double>::*)(int)) &Teuchos::Array<double>::remove, "C++: Teuchos::Array<double>::remove(int) --> void", pybind11::arg("i"));
		cl.def("length", (int (Teuchos::Array<double>::*)() const) &Teuchos::Array<double>::length, "C++: Teuchos::Array<double>::length() const --> int");
		cl.def("toString", (std::string (Teuchos::Array<double>::*)() const) &Teuchos::Array<double>::toString, "C++: Teuchos::Array<double>::toString() const --> std::string");
		cl.def_static("hasBoundsChecking", (bool (*)()) &Teuchos::Array<double>::hasBoundsChecking, "C++: Teuchos::Array<double>::hasBoundsChecking() --> bool");
		cl.def("getRawPtr", (double * (Teuchos::Array<double>::*)()) &Teuchos::Array<double>::getRawPtr, "C++: Teuchos::Array<double>::getRawPtr() --> double *", pybind11::return_value_policy::automatic);
		cl.def("data", (double * (Teuchos::Array<double>::*)()) &Teuchos::Array<double>::data, "C++: Teuchos::Array<double>::data() --> double *", pybind11::return_value_policy::automatic);
		cl.def("toVector", (class std::vector<double> (Teuchos::Array<double>::*)() const) &Teuchos::Array<double>::toVector, "C++: Teuchos::Array<double>::toVector() const --> class std::vector<double>");
		cl.def("assign", (class Teuchos::Array<double> & (Teuchos::Array<double>::*)(const class std::vector<double> &)) &Teuchos::Array<double>::operator=, "C++: Teuchos::Array<double>::operator=(const class std::vector<double> &) --> class Teuchos::Array<double> &", pybind11::return_value_policy::automatic, pybind11::arg("v"));

		cl.def("__str__", [](Teuchos::Array<double> const &o) -> std::string { std::ostringstream s; using namespace Teuchos; s << o; return s.str(); } );
	}
	// Teuchos::fromStringToArray(const std::string &) file:Teuchos_Array.hpp line:1662
	M("Teuchos").def("fromStringToArray", (class Teuchos::Array<double> (*)(const std::string &)) &Teuchos::fromStringToArray<double>, "C++: Teuchos::fromStringToArray(const std::string &) --> class Teuchos::Array<double>", pybind11::arg("arrayStr"));

	// Teuchos::getArrayTypeNameTraitsFormat() file:Teuchos_Array.hpp line:719
	M("Teuchos").def("getArrayTypeNameTraitsFormat", (std::string (*)()) &Teuchos::getArrayTypeNameTraitsFormat, "Get the format that is used for the specialization of the TypeName\n traits class for Array.\n\n The string returned will contain only one\n \"*\" character. The \"*\" character should then be replaced with the actual\n template type of the array.\n \n\n\n \n\nC++: Teuchos::getArrayTypeNameTraitsFormat() --> std::string");

	{ // Teuchos::XMLObjectImplem file:Teuchos_XMLObjectImplem.hpp line:30
		pybind11::class_<Teuchos::XMLObjectImplem, Teuchos::RCP<Teuchos::XMLObjectImplem>> cl(M("Teuchos"), "XMLObjectImplem", "The XMLObjectImplem class takes care of the low-level implementation\n details of XMLObject", pybind11::module_local());
		cl.def( pybind11::init<const std::string &>(), pybind11::arg("tag") );

		cl.def( pybind11::init( [](Teuchos::XMLObjectImplem const &o){ return new Teuchos::XMLObjectImplem(o); } ) );
		cl.def("deepCopy", (class Teuchos::XMLObjectImplem * (Teuchos::XMLObjectImplem::*)() const) &Teuchos::XMLObjectImplem::deepCopy, "Deep copy\n\nC++: Teuchos::XMLObjectImplem::deepCopy() const --> class Teuchos::XMLObjectImplem *", pybind11::return_value_policy::automatic);
		cl.def("addAttribute", (void (Teuchos::XMLObjectImplem::*)(const std::string &, const std::string &)) &Teuchos::XMLObjectImplem::addAttribute, "Add a [name, value] attribute\n\nC++: Teuchos::XMLObjectImplem::addAttribute(const std::string &, const std::string &) --> void", pybind11::arg("name"), pybind11::arg("value"));
		cl.def("addChild", (void (Teuchos::XMLObjectImplem::*)(const class Teuchos::XMLObject &)) &Teuchos::XMLObjectImplem::addChild, "Add a child XMLObject\n\nC++: Teuchos::XMLObjectImplem::addChild(const class Teuchos::XMLObject &) --> void", pybind11::arg("child"));
		cl.def("addContent", (void (Teuchos::XMLObjectImplem::*)(const std::string &)) &Teuchos::XMLObjectImplem::addContent, "Add a content line\n\nC++: Teuchos::XMLObjectImplem::addContent(const std::string &) --> void", pybind11::arg("contentLine"));
		cl.def("getTag", (const std::string & (Teuchos::XMLObjectImplem::*)() const) &Teuchos::XMLObjectImplem::getTag, "Return the tag std::string\n\nC++: Teuchos::XMLObjectImplem::getTag() const --> const std::string &", pybind11::return_value_policy::automatic);
		cl.def("hasAttribute", (bool (Teuchos::XMLObjectImplem::*)(const std::string &) const) &Teuchos::XMLObjectImplem::hasAttribute, "Determine whether an attribute exists\n\nC++: Teuchos::XMLObjectImplem::hasAttribute(const std::string &) const --> bool", pybind11::arg("name"));
		cl.def("getAttribute", (const std::string & (Teuchos::XMLObjectImplem::*)(const std::string &) const) &Teuchos::XMLObjectImplem::getAttribute, "Look up an attribute by name\n\nC++: Teuchos::XMLObjectImplem::getAttribute(const std::string &) const --> const std::string &", pybind11::return_value_policy::automatic, pybind11::arg("name"));
		cl.def("numChildren", (int (Teuchos::XMLObjectImplem::*)() const) &Teuchos::XMLObjectImplem::numChildren, "Return the number of children\n\nC++: Teuchos::XMLObjectImplem::numChildren() const --> int");
		cl.def("getChild", (const class Teuchos::XMLObject & (Teuchos::XMLObjectImplem::*)(int) const) &Teuchos::XMLObjectImplem::getChild, "Look up a child by its index\n\nC++: Teuchos::XMLObjectImplem::getChild(int) const --> const class Teuchos::XMLObject &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("numContentLines", (int (Teuchos::XMLObjectImplem::*)() const) &Teuchos::XMLObjectImplem::numContentLines, "Get the number of content lines\n\nC++: Teuchos::XMLObjectImplem::numContentLines() const --> int");
		cl.def("getContentLine", (const std::string & (Teuchos::XMLObjectImplem::*)(int) const) &Teuchos::XMLObjectImplem::getContentLine, "Look up a content line by index\n\nC++: Teuchos::XMLObjectImplem::getContentLine(int) const --> const std::string &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("appendContentLine", (void (Teuchos::XMLObjectImplem::*)(const unsigned long &, const std::string &)) &Teuchos::XMLObjectImplem::appendContentLine, "Add string at the the end of a content line\n\nC++: Teuchos::XMLObjectImplem::appendContentLine(const unsigned long &, const std::string &) --> void", pybind11::arg("i"), pybind11::arg("str"));
		cl.def("removeContentLine", (void (Teuchos::XMLObjectImplem::*)(const unsigned long &)) &Teuchos::XMLObjectImplem::removeContentLine, "Remove content line by index\n\nC++: Teuchos::XMLObjectImplem::removeContentLine(const unsigned long &) --> void", pybind11::arg("i"));
		cl.def("print", (void (Teuchos::XMLObjectImplem::*)(std::ostream &, int) const) &Teuchos::XMLObjectImplem::print, "Print to stream with the given indentation level. Output will be well-formed XML.\n\nC++: Teuchos::XMLObjectImplem::print(std::ostream &, int) const --> void", pybind11::arg("os"), pybind11::arg("indent"));
		cl.def("toString", (std::string (Teuchos::XMLObjectImplem::*)() const) &Teuchos::XMLObjectImplem::toString, "Write as a std::string. Output may be ill-formed XML.\n\nC++: Teuchos::XMLObjectImplem::toString() const --> std::string");
		cl.def("header", [](Teuchos::XMLObjectImplem const &o) -> std::string { return o.header(); }, "");
		cl.def("header", (std::string (Teuchos::XMLObjectImplem::*)(bool) const) &Teuchos::XMLObjectImplem::header, "Write the header\n\nC++: Teuchos::XMLObjectImplem::header(bool) const --> std::string", pybind11::arg("strictXML"));
		cl.def("terminatedHeader", [](Teuchos::XMLObjectImplem const &o) -> std::string { return o.terminatedHeader(); }, "");
		cl.def("terminatedHeader", (std::string (Teuchos::XMLObjectImplem::*)(bool) const) &Teuchos::XMLObjectImplem::terminatedHeader, "Write the header terminated as <Header/>\n\nC++: Teuchos::XMLObjectImplem::terminatedHeader(bool) const --> std::string", pybind11::arg("strictXML"));
		cl.def("footer", (std::string (Teuchos::XMLObjectImplem::*)() const) &Teuchos::XMLObjectImplem::footer, "Write the footer\n\nC++: Teuchos::XMLObjectImplem::footer() const --> std::string");
		cl.def("assign", (class Teuchos::XMLObjectImplem & (Teuchos::XMLObjectImplem::*)(const class Teuchos::XMLObjectImplem &)) &Teuchos::XMLObjectImplem::operator=, "C++: Teuchos::XMLObjectImplem::operator=(const class Teuchos::XMLObjectImplem &) --> class Teuchos::XMLObjectImplem &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // Teuchos::EmptyXMLError file:Teuchos_XMLObject.hpp line:23
		pybind11::class_<Teuchos::EmptyXMLError, Teuchos::RCP<Teuchos::EmptyXMLError>, PyCallBack_Teuchos_EmptyXMLError> cl(M("Teuchos"), "EmptyXMLError", "Thrown when attempting to parse an empty XML std::string.", pybind11::module_local());
		cl.def( pybind11::init<const std::string &>(), pybind11::arg("what_arg") );

		cl.def( pybind11::init( [](PyCallBack_Teuchos_EmptyXMLError const &o){ return new PyCallBack_Teuchos_EmptyXMLError(o); } ) );
		cl.def( pybind11::init( [](Teuchos::EmptyXMLError const &o){ return new Teuchos::EmptyXMLError(o); } ) );
		cl.def("assign", (class Teuchos::EmptyXMLError & (Teuchos::EmptyXMLError::*)(const class Teuchos::EmptyXMLError &)) &Teuchos::EmptyXMLError::operator=, "C++: Teuchos::EmptyXMLError::operator=(const class Teuchos::EmptyXMLError &) --> class Teuchos::EmptyXMLError &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // Teuchos::XMLObject file:Teuchos_XMLObject.hpp line:30
		pybind11::class_<Teuchos::XMLObject, Teuchos::RCP<Teuchos::XMLObject>> cl(M("Teuchos"), "XMLObject", "Representation of an XML data tree. XMLObject is a ref-counted\n handle to a XMLObjectImplem object, allowing storage by reference.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::XMLObject(); } ) );
		cl.def( pybind11::init<const std::string &>(), pybind11::arg("tag") );

		cl.def( pybind11::init<class Teuchos::XMLObjectImplem *>(), pybind11::arg("ptr") );

		cl.def( pybind11::init( [](Teuchos::XMLObject const &o){ return new Teuchos::XMLObject(o); } ) );
		cl.def("getRequired", (bool (Teuchos::XMLObject::*)(const std::string &) const) &Teuchos::XMLObject::getRequired<bool>, "C++: Teuchos::XMLObject::getRequired(const std::string &) const --> bool", pybind11::arg("name"));
		cl.def("getRequired", (int (Teuchos::XMLObject::*)(const std::string &) const) &Teuchos::XMLObject::getRequired<int>, "C++: Teuchos::XMLObject::getRequired(const std::string &) const --> int", pybind11::arg("name"));
		cl.def("getRequired", (double (Teuchos::XMLObject::*)(const std::string &) const) &Teuchos::XMLObject::getRequired<double>, "C++: Teuchos::XMLObject::getRequired(const std::string &) const --> double", pybind11::arg("name"));
		cl.def("getRequired", (std::string (Teuchos::XMLObject::*)(const std::string &) const) &Teuchos::XMLObject::getRequired<std::string>, "C++: Teuchos::XMLObject::getRequired(const std::string &) const --> std::string", pybind11::arg("name"));
		cl.def("addAttribute", (void (Teuchos::XMLObject::*)(const std::string &, std::string)) &Teuchos::XMLObject::addAttribute<std::string>, "C++: Teuchos::XMLObject::addAttribute(const std::string &, std::string) --> void", pybind11::arg("name"), pybind11::arg("value"));
		cl.def("addAttribute", (void (Teuchos::XMLObject::*)(const std::string &, const std::string &)) &Teuchos::XMLObject::addAttribute<const std::string &>, "C++: Teuchos::XMLObject::addAttribute(const std::string &, const std::string &) --> void", pybind11::arg("name"), pybind11::arg("value"));
		cl.def("deepCopy", (class Teuchos::XMLObject (Teuchos::XMLObject::*)() const) &Teuchos::XMLObject::deepCopy, "Make a deep copy of this object\n\nC++: Teuchos::XMLObject::deepCopy() const --> class Teuchos::XMLObject");
		cl.def("getTag", (const std::string & (Teuchos::XMLObject::*)() const) &Teuchos::XMLObject::getTag, "Return the tag of the current node\n\nC++: Teuchos::XMLObject::getTag() const --> const std::string &", pybind11::return_value_policy::automatic);
		cl.def("hasAttribute", (bool (Teuchos::XMLObject::*)(const std::string &) const) &Teuchos::XMLObject::hasAttribute, "Find out if the current node has an attribute of the specified name\n\nC++: Teuchos::XMLObject::hasAttribute(const std::string &) const --> bool", pybind11::arg("name"));
		cl.def("getAttribute", (const std::string & (Teuchos::XMLObject::*)(const std::string &) const) &Teuchos::XMLObject::getAttribute, "Return the value of the attribute with the specified name\n\nC++: Teuchos::XMLObject::getAttribute(const std::string &) const --> const std::string &", pybind11::return_value_policy::automatic, pybind11::arg("name"));
		cl.def("getRequired", (const std::string & (Teuchos::XMLObject::*)(const std::string &) const) &Teuchos::XMLObject::getRequired, "Get an attribute, throwing an std::exception if it is not found\n\nC++: Teuchos::XMLObject::getRequired(const std::string &) const --> const std::string &", pybind11::return_value_policy::automatic, pybind11::arg("name"));
		cl.def("getRequiredDouble", (double (Teuchos::XMLObject::*)(const std::string &) const) &Teuchos::XMLObject::getRequiredDouble, "Get a required attribute, returning it as a double\n\nC++: Teuchos::XMLObject::getRequiredDouble(const std::string &) const --> double", pybind11::arg("name"));
		cl.def("getRequiredInt", (int (Teuchos::XMLObject::*)(const std::string &) const) &Teuchos::XMLObject::getRequiredInt, "Get a required attribute, returning it as an int\n\nC++: Teuchos::XMLObject::getRequiredInt(const std::string &) const --> int", pybind11::arg("name"));
		cl.def("getRequiredBool", (bool (Teuchos::XMLObject::*)(const std::string &) const) &Teuchos::XMLObject::getRequiredBool, "Get a required attribute, returning it as a bool\n\nC++: Teuchos::XMLObject::getRequiredBool(const std::string &) const --> bool", pybind11::arg("name"));
		cl.def("numChildren", (int (Teuchos::XMLObject::*)() const) &Teuchos::XMLObject::numChildren, "Return the number of child nodes owned by this node\n\nC++: Teuchos::XMLObject::numChildren() const --> int");
		cl.def("getChild", (const class Teuchos::XMLObject & (Teuchos::XMLObject::*)(int) const) &Teuchos::XMLObject::getChild, "Return the i-th child node\n\nC++: Teuchos::XMLObject::getChild(int) const --> const class Teuchos::XMLObject &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("findFirstChild", (int (Teuchos::XMLObject::*)(std::string) const) &Teuchos::XMLObject::findFirstChild, "Returns the index of the first child found with the given tag name.\n Returns -1 if no child is found.\n\nC++: Teuchos::XMLObject::findFirstChild(std::string) const --> int", pybind11::arg("tagName"));
		cl.def("numContentLines", (int (Teuchos::XMLObject::*)() const) &Teuchos::XMLObject::numContentLines, "Return the number of lines of character content stored in this node\n\nC++: Teuchos::XMLObject::numContentLines() const --> int");
		cl.def("getContentLine", (const std::string & (Teuchos::XMLObject::*)(int) const) &Teuchos::XMLObject::getContentLine, "Return the i-th line of character content stored in this node\n\nC++: Teuchos::XMLObject::getContentLine(int) const --> const std::string &", pybind11::return_value_policy::automatic, pybind11::arg("i"));
		cl.def("toString", (std::string (Teuchos::XMLObject::*)() const) &Teuchos::XMLObject::toString, "Represent this node and its children as a std::string\n\nC++: Teuchos::XMLObject::toString() const --> std::string");
		cl.def("print", (void (Teuchos::XMLObject::*)(std::ostream &, int) const) &Teuchos::XMLObject::print, "Print this node and its children to stream with the given indentation\n\nC++: Teuchos::XMLObject::print(std::ostream &, int) const --> void", pybind11::arg("os"), pybind11::arg("indent"));
		cl.def("header", (std::string (Teuchos::XMLObject::*)() const) &Teuchos::XMLObject::header, "Write the header for this object to a std::string\n\nC++: Teuchos::XMLObject::header() const --> std::string");
		cl.def("terminatedHeader", (std::string (Teuchos::XMLObject::*)() const) &Teuchos::XMLObject::terminatedHeader, "Write the header for this object to a std::string\n\nC++: Teuchos::XMLObject::terminatedHeader() const --> std::string");
		cl.def("footer", (std::string (Teuchos::XMLObject::*)() const) &Teuchos::XMLObject::footer, "Write the footer for this object to a std::string\n\nC++: Teuchos::XMLObject::footer() const --> std::string");
		cl.def("isEmpty", (bool (Teuchos::XMLObject::*)() const) &Teuchos::XMLObject::isEmpty, "Find out if a node is empty\n\nC++: Teuchos::XMLObject::isEmpty() const --> bool");
		cl.def("checkTag", (void (Teuchos::XMLObject::*)(const std::string &) const) &Teuchos::XMLObject::checkTag, "Check that a tag is equal to an expected std::string\n\nC++: Teuchos::XMLObject::checkTag(const std::string &) const --> void", pybind11::arg("expected"));
		cl.def("addDouble", (void (Teuchos::XMLObject::*)(const std::string &, double)) &Teuchos::XMLObject::addDouble, "Add a double as an attribute\n\nC++: Teuchos::XMLObject::addDouble(const std::string &, double) --> void", pybind11::arg("name"), pybind11::arg("val"));
		cl.def("addInt", (void (Teuchos::XMLObject::*)(const std::string &, int)) &Teuchos::XMLObject::addInt, "Add an int as an attribute\n\nC++: Teuchos::XMLObject::addInt(const std::string &, int) --> void", pybind11::arg("name"), pybind11::arg("val"));
		cl.def("addBool", (void (Teuchos::XMLObject::*)(const std::string &, bool)) &Teuchos::XMLObject::addBool, "Add a bool as an attribute\n\nC++: Teuchos::XMLObject::addBool(const std::string &, bool) --> void", pybind11::arg("name"), pybind11::arg("val"));
		cl.def("addChild", (void (Teuchos::XMLObject::*)(const class Teuchos::XMLObject &)) &Teuchos::XMLObject::addChild, "Add a child node to the node\n\nC++: Teuchos::XMLObject::addChild(const class Teuchos::XMLObject &) --> void", pybind11::arg("child"));
		cl.def("addContent", (void (Teuchos::XMLObject::*)(const std::string &)) &Teuchos::XMLObject::addContent, "Add a line of character content\n\nC++: Teuchos::XMLObject::addContent(const std::string &) --> void", pybind11::arg("contentLine"));
		cl.def("appendContentLine", (void (Teuchos::XMLObject::*)(const unsigned long &, const std::string &)) &Teuchos::XMLObject::appendContentLine, "C++: Teuchos::XMLObject::appendContentLine(const unsigned long &, const std::string &) --> void", pybind11::arg("i"), pybind11::arg("str"));
		cl.def("removeContentLine", (void (Teuchos::XMLObject::*)(const unsigned long &)) &Teuchos::XMLObject::removeContentLine, "C++: Teuchos::XMLObject::removeContentLine(const unsigned long &) --> void", pybind11::arg("i"));
		cl.def("assign", (class Teuchos::XMLObject & (Teuchos::XMLObject::*)(const class Teuchos::XMLObject &)) &Teuchos::XMLObject::operator=, "C++: Teuchos::XMLObject::operator=(const class Teuchos::XMLObject &) --> class Teuchos::XMLObject &", pybind11::return_value_policy::automatic, pybind11::arg(""));

		cl.def("__str__", [](Teuchos::XMLObject const &o) -> std::string { std::ostringstream s; using namespace Teuchos; s << o; return s.str(); } );
	}
	// Teuchos::toString(const class Teuchos::XMLObject &) file:Teuchos_XMLObject.hpp line:229
	M("Teuchos").def("toString", (std::string (*)(const class Teuchos::XMLObject &)) &Teuchos::toString, "Write XMLObject to std::string.\n\n \n\n \n\nC++: Teuchos::toString(const class Teuchos::XMLObject &) --> std::string", pybind11::arg("xml"));

	{ // Teuchos::ParameterEntryValidator file:Teuchos_ParameterEntryValidator.hpp line:31
		pybind11::class_<Teuchos::ParameterEntryValidator, Teuchos::RCP<Teuchos::ParameterEntryValidator>, PyCallBack_Teuchos_ParameterEntryValidator> cl(M("Teuchos"), "ParameterEntryValidator", "Abstract interface for an object that can validate a\n  ParameterEntry's value.\n\n Not only can a validator validate and entry but it can also help to set\n and/or adjust the default value.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new PyCallBack_Teuchos_ParameterEntryValidator(); } ) );
		cl.def(pybind11::init<PyCallBack_Teuchos_ParameterEntryValidator const &>());
		cl.def("getXMLTypeName", (const std::string (Teuchos::ParameterEntryValidator::*)() const) &Teuchos::ParameterEntryValidator::getXMLTypeName, "Get a string that should be used as a value of the type attribute\n when serializing it to XML.\n\n \n a string that should be used as a tag for this validator\n when serializing it to XML.\n\nC++: Teuchos::ParameterEntryValidator::getXMLTypeName() const --> const std::string");
		cl.def("printDoc", (void (Teuchos::ParameterEntryValidator::*)(const std::string &, std::ostream &) const) &Teuchos::ParameterEntryValidator::printDoc, "Print documentation for this parameter.\n\n \n [in] (Multi-line) documentation std::string.\n\n \n [out] The std::ostream used for the output\n\n The purpose of this function is to augment what is\n in docString\n with some description of what valid values this parameter\n validator will accept.\n\nC++: Teuchos::ParameterEntryValidator::printDoc(const std::string &, std::ostream &) const --> void", pybind11::arg("docString"), pybind11::arg("out"));
		cl.def("validStringValues", (class Teuchos::RCP<const class Teuchos::Array<std::string > > (Teuchos::ParameterEntryValidator::*)() const) &Teuchos::ParameterEntryValidator::validStringValues, "Return an array of strings of valid values if applicable.\n\n If there is no such array of std::string values that makes since, just return\n return.get()==NULL.\n\n The returned strings must not contain any newlines (i.e. no ''\n characters) and must be short enough to fit on one line and be readable.\n\nC++: Teuchos::ParameterEntryValidator::validStringValues() const --> class Teuchos::RCP<const class Teuchos::Array<std::string > >");
		cl.def("validate", (void (Teuchos::ParameterEntryValidator::*)(const class Teuchos::ParameterEntry &, const std::string &, const std::string &) const) &Teuchos::ParameterEntryValidator::validate, "Validate a parameter entry value and throw std::exception (with a\n great error message) if validation fails.\n\n \n\n            [in] The ParameterEntry who's type and value is being validated\n \n\n\n            [in] The name of the ParameterEntry that is used to build error messages.\n \n\n\n            [in] The name of the ParameterList that paramName exists in\n            that is used to build error messages.\n\nC++: Teuchos::ParameterEntryValidator::validate(const class Teuchos::ParameterEntry &, const std::string &, const std::string &) const --> void", pybind11::arg("entry"), pybind11::arg("paramName"), pybind11::arg("sublistName"));
		cl.def("validateAndModify", (void (Teuchos::ParameterEntryValidator::*)(const std::string &, const std::string &, class Teuchos::ParameterEntry *) const) &Teuchos::ParameterEntryValidator::validateAndModify, "Validate and perhaps modify a parameter entry's value.\n\n \n [in] The name of the ParameterEntry that is used to\n build error messages.\n\n \n [in] The name of the ParameterList that\n paramName exists in that is used to build error messages.\n\n \n [in/out] The ParameterEntry who's type and value is being\n validated and perhaps even changed as a result of calling this function.\n\n The default implementation simply calls this->validate().\n\nC++: Teuchos::ParameterEntryValidator::validateAndModify(const std::string &, const std::string &, class Teuchos::ParameterEntry *) const --> void", pybind11::arg("paramName"), pybind11::arg("sublistName"), pybind11::arg("entry"));
		cl.def("convertStringToDouble", (double (Teuchos::ParameterEntryValidator::*)(std::string) const) &Teuchos::ParameterEntryValidator::convertStringToDouble, "C++: Teuchos::ParameterEntryValidator::convertStringToDouble(std::string) const --> double", pybind11::arg("str"));
		cl.def("convertStringToInt", (int (Teuchos::ParameterEntryValidator::*)(std::string) const) &Teuchos::ParameterEntryValidator::convertStringToInt, "C++: Teuchos::ParameterEntryValidator::convertStringToInt(std::string) const --> int", pybind11::arg("str"));
		cl.def("convertStringToLongLong", (int (Teuchos::ParameterEntryValidator::*)(std::string) const) &Teuchos::ParameterEntryValidator::convertStringToLongLong, "C++: Teuchos::ParameterEntryValidator::convertStringToLongLong(std::string) const --> int", pybind11::arg("str"));
		cl.def("assign", (class Teuchos::ParameterEntryValidator & (Teuchos::ParameterEntryValidator::*)(const class Teuchos::ParameterEntryValidator &)) &Teuchos::ParameterEntryValidator::operator=, "C++: Teuchos::ParameterEntryValidator::operator=(const class Teuchos::ParameterEntryValidator &) --> class Teuchos::ParameterEntryValidator &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // Teuchos::ParameterListModifier file:Teuchos_ParameterListModifier.hpp line:36
		pybind11::class_<Teuchos::ParameterListModifier, Teuchos::RCP<Teuchos::ParameterListModifier>, PyCallBack_Teuchos_ParameterListModifier> cl(M("Teuchos"), "ParameterListModifier", "Abstract interface for an object that can modify both a\n  parameter list and the parameter list being used during the\n  validation stage.\n\n A parameter (sub)list modifier can be used to process optional fields and\n dependent fields before validation.  It can also be used after validation\n to reconcile parameters that may have dependencies on other parameters.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ParameterListModifier(); }, [](){ return new PyCallBack_Teuchos_ParameterListModifier(); } ) );
		cl.def( pybind11::init<const std::string &>(), pybind11::arg("name") );

		cl.def( pybind11::init( [](PyCallBack_Teuchos_ParameterListModifier const &o){ return new PyCallBack_Teuchos_ParameterListModifier(o); } ) );
		cl.def( pybind11::init( [](Teuchos::ParameterListModifier const &o){ return new Teuchos::ParameterListModifier(o); } ) );
		cl.def("setName", (class Teuchos::ParameterListModifier & (Teuchos::ParameterListModifier::*)(const std::string &)) &Teuchos::ParameterListModifier::setName, "Set the name of *this modifier.\n\nC++: Teuchos::ParameterListModifier::setName(const std::string &) --> class Teuchos::ParameterListModifier &", pybind11::return_value_policy::automatic, pybind11::arg("name"));
		cl.def("getName", (const std::string & (Teuchos::ParameterListModifier::*)() const) &Teuchos::ParameterListModifier::getName, "Get the name of *this modifier.\n\nC++: Teuchos::ParameterListModifier::getName() const --> const std::string &", pybind11::return_value_policy::automatic);
		cl.def("printDoc", (void (Teuchos::ParameterListModifier::*)(const std::string &, std::ostream &) const) &Teuchos::ParameterListModifier::printDoc, "Print documentation for this parameter list modifier.\n\n \n [in] (Multi-line) documentation std::string.\n\n \n [out] The std::ostream used for the output\n\n The purpose of this function is to augment what is\n in docString\n with some description of what happens during the modification and\n reconciliation stages of this modifier.\n\nC++: Teuchos::ParameterListModifier::printDoc(const std::string &, std::ostream &) const --> void", pybind11::arg("docString"), pybind11::arg("out"));
		cl.def("findMatchingBaseNames", [](Teuchos::ParameterListModifier const &o, const class Teuchos::ParameterList & a0, const std::string & a1) -> Teuchos::Array<std::string > { return o.findMatchingBaseNames(a0, a1); }, "", pybind11::arg("paramList"), pybind11::arg("baseName"));
		cl.def("findMatchingBaseNames", [](Teuchos::ParameterListModifier const &o, const class Teuchos::ParameterList & a0, const std::string & a1, const bool & a2) -> Teuchos::Array<std::string > { return o.findMatchingBaseNames(a0, a1, a2); }, "", pybind11::arg("paramList"), pybind11::arg("baseName"), pybind11::arg("findParameters"));
		cl.def("findMatchingBaseNames", (class Teuchos::Array<std::string > (Teuchos::ParameterListModifier::*)(const class Teuchos::ParameterList &, const std::string &, const bool &, const bool &) const) &Teuchos::ParameterListModifier::findMatchingBaseNames, "Find the parameters and/or sublists with matching base names.\n\n \n [in] Modified parameter list to search.\n\n \n [out] Search through parameters\n\n \n [out] Search through sublists (not recursive)\n\n This convenience function makes it easy to search through the current level of\n a given parameter list and find all parameters and/or sublists that begin with a\n given name.\n\nC++: Teuchos::ParameterListModifier::findMatchingBaseNames(const class Teuchos::ParameterList &, const std::string &, const bool &, const bool &) const --> class Teuchos::Array<std::string >", pybind11::arg("paramList"), pybind11::arg("baseName"), pybind11::arg("findParameters"), pybind11::arg("findSublists"));
		cl.def("modify", (void (Teuchos::ParameterListModifier::*)(class Teuchos::ParameterList &, class Teuchos::ParameterList &) const) &Teuchos::ParameterListModifier::modify, "Modify a parameter list and/or the valid parameter list being used to validate\n it and throw std::exception (with a great error message) if modification fails.\n\n \n\n            [in] The parameter list that needs to be validated\n \n\n\n            [in] The parameter list being used as a template for validation.\n\n This function is usually called before the validation step begins in order to create optional\n parameters and/or sublists.\n\nC++: Teuchos::ParameterListModifier::modify(class Teuchos::ParameterList &, class Teuchos::ParameterList &) const --> void", pybind11::arg("paramList"), pybind11::arg("validParamList"));
		cl.def("reconcile", (void (Teuchos::ParameterListModifier::*)(class Teuchos::ParameterList &) const) &Teuchos::ParameterListModifier::reconcile, "Reconcile a parameter list and/or the valid parameter list being used to validate\n it and throw std::exception (with a great error message) if reconciliation fails.\n\n \n\n            [in,out] The parameter list that needs to be validated\n \n\n\n            [in,out] The parameter list being used as a template for validation.\n\n This function is usually called after the validation step begins in order to check that\n dependencies between multiple parameters are satisfied.\n\nC++: Teuchos::ParameterListModifier::reconcile(class Teuchos::ParameterList &) const --> void", pybind11::arg("paramList"));
		cl.def("expandParameters", [](Teuchos::ParameterListModifier const &o, const std::string & a0, class Teuchos::ParameterList & a1, class Teuchos::ParameterList & a2) -> int { return o.expandParameters(a0, a1, a2); }, "", pybind11::arg("paramTemplateName"), pybind11::arg("paramList"), pybind11::arg("validParamList"));
		cl.def("expandParameters", (int (Teuchos::ParameterListModifier::*)(const std::string &, class Teuchos::ParameterList &, class Teuchos::ParameterList &, const class Teuchos::Array<std::string > &) const) &Teuchos::ParameterListModifier::expandParameters, "Create parameters in the valid parameter list using a template parameter from the valid\n  parameter list and the names of parameters in the list being validated.\n\n  \n [in] The name of the parameter template in \n\n  \n [in] The parameter list that needs to be validated\n\n  \n [in,out] The parameter list that is being used as a template for validation\n\n  \n [in] An optional list of parameter names to exclude\n\n   \n\nC++: Teuchos::ParameterListModifier::expandParameters(const std::string &, class Teuchos::ParameterList &, class Teuchos::ParameterList &, const class Teuchos::Array<std::string > &) const --> int", pybind11::arg("paramTemplateName"), pybind11::arg("paramList"), pybind11::arg("validParamList"), pybind11::arg("excludeParameters"));
		cl.def("expandSublists", [](Teuchos::ParameterListModifier const &o, const std::string & a0, class Teuchos::ParameterList & a1, class Teuchos::ParameterList & a2) -> int { return o.expandSublists(a0, a1, a2); }, "", pybind11::arg("sublistTemplateName"), pybind11::arg("paramList"), pybind11::arg("validParamList"));
		cl.def("expandSublists", (int (Teuchos::ParameterListModifier::*)(const std::string &, class Teuchos::ParameterList &, class Teuchos::ParameterList &, const class Teuchos::Array<std::string > &) const) &Teuchos::ParameterListModifier::expandSublists, "Create sublists in the valid parameter list using a template parameter from the valid\n  parameter list and the names of sublists in the list being validated.\n\n  \n [in] The name of the sublist template in \n\n  \n [in] The parameter list that needs to be validated\n\n  \n [in,out] The parameter list that is being used as a template for validation\n\n  \n [in] An optional list of sublist names to exclude\n\n   \n\nC++: Teuchos::ParameterListModifier::expandSublists(const std::string &, class Teuchos::ParameterList &, class Teuchos::ParameterList &, const class Teuchos::Array<std::string > &) const --> int", pybind11::arg("sublistTemplateName"), pybind11::arg("paramList"), pybind11::arg("validParamList"), pybind11::arg("excludeSublists"));
		cl.def("setDefaultsInSublists", [](Teuchos::ParameterListModifier const &o, const std::string & a0, class Teuchos::ParameterList & a1, const class Teuchos::Array<std::string > & a2) -> int { return o.setDefaultsInSublists(a0, a1, a2); }, "", pybind11::arg("paramName"), pybind11::arg("paramList"), pybind11::arg("sublistNames"));
		cl.def("setDefaultsInSublists", (int (Teuchos::ParameterListModifier::*)(const std::string &, class Teuchos::ParameterList &, const class Teuchos::Array<std::string > &, const bool) const) &Teuchos::ParameterListModifier::setDefaultsInSublists, "Copy a parameter into desired sublists.\n\n \n [in] The name of the parameter to be copied.\n\n \n [in,out] The parameter list with \n\n \n [in] The names of any sublists in  to set the defaults in\n using parameter \n\n \n [in] Remove  from  after defaults are set in sublists.\n\nC++: Teuchos::ParameterListModifier::setDefaultsInSublists(const std::string &, class Teuchos::ParameterList &, const class Teuchos::Array<std::string > &, const bool) const --> int", pybind11::arg("paramName"), pybind11::arg("paramList"), pybind11::arg("sublistNames"), pybind11::arg("removeParam"));
		cl.def("expandSublistsUsingBaseName", [](Teuchos::ParameterListModifier const &o, const std::string & a0, class Teuchos::ParameterList & a1, class Teuchos::ParameterList & a2) -> int { return o.expandSublistsUsingBaseName(a0, a1, a2); }, "", pybind11::arg("baseName"), pybind11::arg("paramList"), pybind11::arg("validParamList"));
		cl.def("expandSublistsUsingBaseName", (int (Teuchos::ParameterListModifier::*)(const std::string &, class Teuchos::ParameterList &, class Teuchos::ParameterList &, const bool &) const) &Teuchos::ParameterListModifier::expandSublistsUsingBaseName, "Create sublists in the valid parameter list using a base name and the corresponding sublists\n  in the parameter list being validated.\n\n  \n [in] The root name of the sublists to look for and create\n\n  \n [in] The parameter list that needs to be validated\n\n  \n [in,out] The parameter list that is being used as a template for validation\n\n  \n [in] Allow the parameter list  to contain a parameter with the same name\n    as base_name.\n\n   \n\nC++: Teuchos::ParameterListModifier::expandSublistsUsingBaseName(const std::string &, class Teuchos::ParameterList &, class Teuchos::ParameterList &, const bool &) const --> int", pybind11::arg("baseName"), pybind11::arg("paramList"), pybind11::arg("validParamList"), pybind11::arg("allowBaseName"));
		cl.def("assign", (class Teuchos::ParameterListModifier & (Teuchos::ParameterListModifier::*)(const class Teuchos::ParameterListModifier &)) &Teuchos::ParameterListModifier::operator=, "C++: Teuchos::ParameterListModifier::operator=(const class Teuchos::ParameterListModifier &) --> class Teuchos::ParameterListModifier &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // Teuchos::ParameterEntry file:Teuchos_ParameterEntry.hpp line:34
		pybind11::class_<Teuchos::ParameterEntry, Teuchos::RCP<Teuchos::ParameterEntry>> cl(M("Teuchos"), "ParameterEntry", "This object is held as the \"value\" in the Teuchos::ParameterList std::map.\n\n    This structure holds a  value and information on the status of this\n    parameter (isUsed, isDefault, etc.).  The type of parameter is chosen through the\n    templated Set/Get methods.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ParameterEntry(); } ) );
		cl.def( pybind11::init( [](Teuchos::ParameterEntry const &o){ return new Teuchos::ParameterEntry(o); } ) );
		cl.def("getValue", (std::string & (Teuchos::ParameterEntry::*)(std::string *) const) &Teuchos::ParameterEntry::getValue<std::string>, "C++: Teuchos::ParameterEntry::getValue(std::string *) const --> std::string &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("getValue", (bool & (Teuchos::ParameterEntry::*)(bool *) const) &Teuchos::ParameterEntry::getValue<bool>, "C++: Teuchos::ParameterEntry::getValue(bool *) const --> bool &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("getValue", (int & (Teuchos::ParameterEntry::*)(int *) const) &Teuchos::ParameterEntry::getValue<int>, "C++: Teuchos::ParameterEntry::getValue(int *) const --> int &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("getValue", (double & (Teuchos::ParameterEntry::*)(double *) const) &Teuchos::ParameterEntry::getValue<double>, "C++: Teuchos::ParameterEntry::getValue(double *) const --> double &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("getValue", (class Teuchos::ParameterList & (Teuchos::ParameterEntry::*)(class Teuchos::ParameterList *) const) &Teuchos::ParameterEntry::getValue<Teuchos::ParameterList>, "C++: Teuchos::ParameterEntry::getValue(class Teuchos::ParameterList *) const --> class Teuchos::ParameterList &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("isType", (bool (Teuchos::ParameterEntry::*)() const) &Teuchos::ParameterEntry::isType<std::string>, "C++: Teuchos::ParameterEntry::isType() const --> bool");
		cl.def("assign", (class Teuchos::ParameterEntry & (Teuchos::ParameterEntry::*)(const class Teuchos::ParameterEntry &)) &Teuchos::ParameterEntry::operator=, "Replace the current parameter entry with \n\nC++: Teuchos::ParameterEntry::operator=(const class Teuchos::ParameterEntry &) --> class Teuchos::ParameterEntry &", pybind11::return_value_policy::automatic, pybind11::arg("source"));
		cl.def("setAnyValue", [](Teuchos::ParameterEntry &o, const class Teuchos::any & a0) -> void { return o.setAnyValue(a0); }, "", pybind11::arg("value"));
		cl.def("setAnyValue", (void (Teuchos::ParameterEntry::*)(const class Teuchos::any &, bool)) &Teuchos::ParameterEntry::setAnyValue, "Set the value as an any object.\n\n This wipes all other data including documentation strings.\n\n Warning! Do not use function ths to set a sublist!\n\nC++: Teuchos::ParameterEntry::setAnyValue(const class Teuchos::any &, bool) --> void", pybind11::arg("value"), pybind11::arg("isDefault"));
		cl.def("setValidator", (void (Teuchos::ParameterEntry::*)(const class Teuchos::RCP<const class Teuchos::ParameterEntryValidator> &)) &Teuchos::ParameterEntry::setValidator, "Set the validator. \n\nC++: Teuchos::ParameterEntry::setValidator(const class Teuchos::RCP<const class Teuchos::ParameterEntryValidator> &) --> void", pybind11::arg("validator"));
		cl.def("setDocString", (void (Teuchos::ParameterEntry::*)(const std::string &)) &Teuchos::ParameterEntry::setDocString, "Set the documentation std::string. \n\nC++: Teuchos::ParameterEntry::setDocString(const std::string &) --> void", pybind11::arg("docString"));
		cl.def("setList", [](Teuchos::ParameterEntry &o) -> Teuchos::ParameterList & { return o.setList(); }, "", pybind11::return_value_policy::automatic);
		cl.def("setList", [](Teuchos::ParameterEntry &o, bool const & a0) -> Teuchos::ParameterList & { return o.setList(a0); }, "", pybind11::return_value_policy::automatic, pybind11::arg("isDefault"));
		cl.def("setList", (class Teuchos::ParameterList & (Teuchos::ParameterEntry::*)(bool, const std::string &)) &Teuchos::ParameterEntry::setList, "Create a parameter entry that is an empty list.\n\nC++: Teuchos::ParameterEntry::setList(bool, const std::string &) --> class Teuchos::ParameterList &", pybind11::return_value_policy::automatic, pybind11::arg("isDefault"), pybind11::arg("docString"));
		cl.def("getAny", [](Teuchos::ParameterEntry &o) -> Teuchos::any & { return o.getAny(); }, "", pybind11::return_value_policy::automatic);
		cl.def("getAny", (class Teuchos::any & (Teuchos::ParameterEntry::*)(bool)) &Teuchos::ParameterEntry::getAny, "Direct access to the Teuchos::any data value underlying this\n  object. The bool argument  (default: true) indicates that the \n  call to getAny() will set the isUsed() value of the ParameterEntry to true.\n\nC++: Teuchos::ParameterEntry::getAny(bool) --> class Teuchos::any &", pybind11::return_value_policy::automatic, pybind11::arg("activeQry"));
		cl.def("isUsed", (bool (Teuchos::ParameterEntry::*)() const) &Teuchos::ParameterEntry::isUsed, "Return whether or not the value has been used; i.e., whether or not the value has been retrieved via a get function.\n\nC++: Teuchos::ParameterEntry::isUsed() const --> bool");
		cl.def("isList", (bool (Teuchos::ParameterEntry::*)() const) &Teuchos::ParameterEntry::isList, "Return whether or not the value itself is a list.\n\nC++: Teuchos::ParameterEntry::isList() const --> bool");
		cl.def("isArray", (bool (Teuchos::ParameterEntry::*)() const) &Teuchos::ParameterEntry::isArray, "Test if the type of data being contained is a Teuchos::Array.\n\nC++: Teuchos::ParameterEntry::isArray() const --> bool");
		cl.def("isTwoDArray", (bool (Teuchos::ParameterEntry::*)() const) &Teuchos::ParameterEntry::isTwoDArray, "Test if the type of data being contained is a Teuchos::TwoDArray.\n\nC++: Teuchos::ParameterEntry::isTwoDArray() const --> bool");
		cl.def("isDefault", (bool (Teuchos::ParameterEntry::*)() const) &Teuchos::ParameterEntry::isDefault, "Indicate whether this entry takes on the default value.\n\nC++: Teuchos::ParameterEntry::isDefault() const --> bool");
		cl.def("docString", (std::string (Teuchos::ParameterEntry::*)() const) &Teuchos::ParameterEntry::docString, "Return the (optional) documentation std::string\n\nC++: Teuchos::ParameterEntry::docString() const --> std::string");
		cl.def("validator", (class Teuchos::RCP<const class Teuchos::ParameterEntryValidator> (Teuchos::ParameterEntry::*)() const) &Teuchos::ParameterEntry::validator, "Return the (optional) validator object\n\nC++: Teuchos::ParameterEntry::validator() const --> class Teuchos::RCP<const class Teuchos::ParameterEntryValidator>");
		cl.def("leftshift", [](Teuchos::ParameterEntry const &o, std::ostream & a0) -> std::ostream & { return o.leftshift(a0); }, "", pybind11::return_value_policy::automatic, pybind11::arg("os"));
		cl.def("leftshift", (std::ostream & (Teuchos::ParameterEntry::*)(std::ostream &, bool) const) &Teuchos::ParameterEntry::leftshift, "Output a non-list parameter to the given output stream.  \n\n      The parameter is followed by \"[default]\" if it is the default value given through a \n      Set method.  Otherwise, if the parameter was unused (not accessed through a Get method), \n      it will be followed by \"[unused]\".  This function is called by the \"std::ostream& operator<<\". \n\nC++: Teuchos::ParameterEntry::leftshift(std::ostream &, bool) const --> std::ostream &", pybind11::return_value_policy::automatic, pybind11::arg("os"), pybind11::arg("printFlags"));
		cl.def_static("getTagName", (const std::string & (*)()) &Teuchos::ParameterEntry::getTagName, "Get the string that should be used as the tag name for all parameters when they are serialized\n to xml.\n\nC++: Teuchos::ParameterEntry::getTagName() --> const std::string &", pybind11::return_value_policy::automatic);

		cl.def("__str__", [](Teuchos::ParameterEntry const &o) -> std::string { std::ostringstream s; using namespace Teuchos; s << o; return s.str(); } );
	}
	// Teuchos::getValue(const class Teuchos::ParameterEntry &) file:Teuchos_ParameterEntry.hpp line:236
	M("Teuchos").def("getValue", (bool & (*)(const class Teuchos::ParameterEntry &)) &Teuchos::getValue<bool>, "C++: Teuchos::getValue(const class Teuchos::ParameterEntry &) --> bool &", pybind11::return_value_policy::automatic, pybind11::arg("entry"));

	// Teuchos::getValue(const class Teuchos::ParameterEntry &) file:Teuchos_ParameterEntry.hpp line:236
	M("Teuchos").def("getValue", (int & (*)(const class Teuchos::ParameterEntry &)) &Teuchos::getValue<int>, "C++: Teuchos::getValue(const class Teuchos::ParameterEntry &) --> int &", pybind11::return_value_policy::automatic, pybind11::arg("entry"));

	// Teuchos::getValue(const class Teuchos::ParameterEntry &) file:Teuchos_ParameterEntry.hpp line:236
	M("Teuchos").def("getValue", (double & (*)(const class Teuchos::ParameterEntry &)) &Teuchos::getValue<double>, "C++: Teuchos::getValue(const class Teuchos::ParameterEntry &) --> double &", pybind11::return_value_policy::automatic, pybind11::arg("entry"));

	// Teuchos::getValue(const class Teuchos::ParameterEntry &) file:Teuchos_ParameterEntry.hpp line:236
	M("Teuchos").def("getValue", (std::string & (*)(const class Teuchos::ParameterEntry &)) &Teuchos::getValue<std::string>, "C++: Teuchos::getValue(const class Teuchos::ParameterEntry &) --> std::string &", pybind11::return_value_policy::automatic, pybind11::arg("entry"));

	// Teuchos::getValue(const class Teuchos::ParameterEntry &) file:Teuchos_ParameterEntry.hpp line:236
	M("Teuchos").def("getValue", (class Teuchos::ParameterList & (*)(const class Teuchos::ParameterEntry &)) &Teuchos::getValue<Teuchos::ParameterList>, "C++: Teuchos::getValue(const class Teuchos::ParameterEntry &) --> class Teuchos::ParameterList &", pybind11::return_value_policy::automatic, pybind11::arg("entry"));

	{ // Teuchos::StringIndexedOrderedValueObjectContainerBase file:Teuchos_StringIndexedOrderedValueObjectContainer.hpp line:26
		pybind11::class_<Teuchos::StringIndexedOrderedValueObjectContainerBase, Teuchos::RCP<Teuchos::StringIndexedOrderedValueObjectContainerBase>> cl(M("Teuchos"), "StringIndexedOrderedValueObjectContainerBase", "Base types for StringIndexedOrderedValueObjectContainer.", pybind11::module_local());
		cl.def( pybind11::init( [](Teuchos::StringIndexedOrderedValueObjectContainerBase const &o){ return new Teuchos::StringIndexedOrderedValueObjectContainerBase(o); } ) );
		cl.def( pybind11::init( [](){ return new Teuchos::StringIndexedOrderedValueObjectContainerBase(); } ) );
		cl.def_static("getInvalidOrdinal", (long (*)()) &Teuchos::StringIndexedOrderedValueObjectContainerBase::getInvalidOrdinal, "Return the value for invalid ordinal. \n\nC++: Teuchos::StringIndexedOrderedValueObjectContainerBase::getInvalidOrdinal() --> long");
		cl.def("assign", (class Teuchos::StringIndexedOrderedValueObjectContainerBase & (Teuchos::StringIndexedOrderedValueObjectContainerBase::*)(const class Teuchos::StringIndexedOrderedValueObjectContainerBase &)) &Teuchos::StringIndexedOrderedValueObjectContainerBase::operator=, "C++: Teuchos::StringIndexedOrderedValueObjectContainerBase::operator=(const class Teuchos::StringIndexedOrderedValueObjectContainerBase &) --> class Teuchos::StringIndexedOrderedValueObjectContainerBase &", pybind11::return_value_policy::automatic, pybind11::arg(""));

		{ // Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex file:Teuchos_StringIndexedOrderedValueObjectContainer.hpp line:43
			auto & enclosing_class = cl;
			pybind11::class_<Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex, Teuchos::RCP<Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex>> cl(enclosing_class, "OrdinalIndex", "A safe ordinal index type that default initializes to a special\n value.", pybind11::module_local());
			cl.def( pybind11::init( [](){ return new Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex(); } ) );
			cl.def( pybind11::init<const long>(), pybind11::arg("idx_in") );

			cl.def( pybind11::init( [](Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex const &o){ return new Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex(o); } ) );
			cl.def_readwrite("idx", &Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex::idx);
			cl.def("assign", (class Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex & (Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex::*)(const class Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex &)) &Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex::operator=, "C++: Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex::operator=(const class Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex &) --> class Teuchos::StringIndexedOrderedValueObjectContainerBase::OrdinalIndex &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		}

		{ // Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair file:Teuchos_StringIndexedOrderedValueObjectContainer.hpp line:73
			auto & enclosing_class = cl;
			pybind11::class_<Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>, Teuchos::RCP<Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>>> cl(enclosing_class, "KeyObjectPair_Teuchos_ParameterEntry_t", "", pybind11::module_local());
			cl.def( pybind11::init( [](){ return new Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>(); } ) );
			cl.def( pybind11::init( [](Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry> const &o){ return new Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>(o); } ) );
			cl.def_readwrite("second", &Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>::second);
			cl.def_readwrite("key", &Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>::key);
			cl.def("assign", (class Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<class Teuchos::ParameterEntry> & (Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>::*)(const class Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<class Teuchos::ParameterEntry> &)) &Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>::operator=, "C++: Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>::operator=(const class Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<class Teuchos::ParameterEntry> &) --> class Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<class Teuchos::ParameterEntry> &", pybind11::return_value_policy::automatic, pybind11::arg("kop"));
			cl.def_static("makeInvalid", (class Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<class Teuchos::ParameterEntry> (*)()) &Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>::makeInvalid, "C++: Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>::makeInvalid() --> class Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<class Teuchos::ParameterEntry>");
			cl.def("isActive", (bool (Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>::*)() const) &Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>::isActive, "C++: Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<Teuchos::ParameterEntry>::isActive() const --> bool");
		}

		{ // Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive file:Teuchos_StringIndexedOrderedValueObjectContainer.hpp line:112
			auto & enclosing_class = cl;
			pybind11::class_<Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<Teuchos::ParameterEntry>, Teuchos::RCP<Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<Teuchos::ParameterEntry>>> cl(enclosing_class, "SelectActive_Teuchos_ParameterEntry_t", "", pybind11::module_local());
			cl.def( pybind11::init( [](Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<Teuchos::ParameterEntry> const &o){ return new Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<Teuchos::ParameterEntry>(o); } ) );
			cl.def( pybind11::init( [](){ return new Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<Teuchos::ParameterEntry>(); } ) );
			cl.def("__call__", (bool (Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<Teuchos::ParameterEntry>::*)(const class Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<class Teuchos::ParameterEntry> &) const) &Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<Teuchos::ParameterEntry>::operator(), "C++: Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<Teuchos::ParameterEntry>::operator()(const class Teuchos::StringIndexedOrderedValueObjectContainerBase::KeyObjectPair<class Teuchos::ParameterEntry> &) const --> bool", pybind11::arg("key_and_obj"));
			cl.def("assign", (class Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<class Teuchos::ParameterEntry> & (Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<Teuchos::ParameterEntry>::*)(const class Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<class Teuchos::ParameterEntry> &)) &Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<Teuchos::ParameterEntry>::operator=, "C++: Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<Teuchos::ParameterEntry>::operator=(const class Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<class Teuchos::ParameterEntry> &) --> class Teuchos::StringIndexedOrderedValueObjectContainerBase::SelectActive<class Teuchos::ParameterEntry> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		}

		{ // Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError file:Teuchos_StringIndexedOrderedValueObjectContainer.hpp line:119
			auto & enclosing_class = cl;
			pybind11::class_<Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError, Teuchos::RCP<Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError>, PyCallBack_Teuchos_StringIndexedOrderedValueObjectContainerBase_InvalidOrdinalIndexError, Teuchos::ExceptionBase> cl(enclosing_class, "InvalidOrdinalIndexError", "Thrown if an invalid ordinal index is passed in. ", pybind11::module_local());
			cl.def( pybind11::init<const std::string &>(), pybind11::arg("what_arg") );

			cl.def( pybind11::init( [](PyCallBack_Teuchos_StringIndexedOrderedValueObjectContainerBase_InvalidOrdinalIndexError const &o){ return new PyCallBack_Teuchos_StringIndexedOrderedValueObjectContainerBase_InvalidOrdinalIndexError(o); } ) );
			cl.def( pybind11::init( [](Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError const &o){ return new Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError(o); } ) );
			cl.def("assign", (class Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError & (Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError::*)(const class Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError &)) &Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError::operator=, "C++: Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError::operator=(const class Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError &) --> class Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidOrdinalIndexError &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		}

		{ // Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError file:Teuchos_StringIndexedOrderedValueObjectContainer.hpp line:123
			auto & enclosing_class = cl;
			pybind11::class_<Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError, Teuchos::RCP<Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError>, PyCallBack_Teuchos_StringIndexedOrderedValueObjectContainerBase_InvalidKeyError, Teuchos::ExceptionBase> cl(enclosing_class, "InvalidKeyError", "Thrown if an invalid string is passed in. ", pybind11::module_local());
			cl.def( pybind11::init<const std::string &>(), pybind11::arg("what_arg") );

			cl.def( pybind11::init( [](PyCallBack_Teuchos_StringIndexedOrderedValueObjectContainerBase_InvalidKeyError const &o){ return new PyCallBack_Teuchos_StringIndexedOrderedValueObjectContainerBase_InvalidKeyError(o); } ) );
			cl.def( pybind11::init( [](Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError const &o){ return new Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError(o); } ) );
			cl.def("assign", (class Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError & (Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError::*)(const class Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError &)) &Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError::operator=, "C++: Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError::operator=(const class Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError &) --> class Teuchos::StringIndexedOrderedValueObjectContainerBase::InvalidKeyError &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		}

	}
	{ // Teuchos::StringIndexedOrderedValueObjectContainer file:Teuchos_StringIndexedOrderedValueObjectContainer.hpp line:151
		pybind11::class_<Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>, Teuchos::RCP<Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>>> cl(M("Teuchos"), "StringIndexedOrderedValueObjectContainer_Teuchos_ParameterEntry_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>(); } ) );
		cl.def( pybind11::init( [](Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry> const &o){ return new Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>(o); } ) );
		cl.def("setObj", (long (Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::*)(const std::string &, class Teuchos::ParameterEntry &)) &Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::setObj<Teuchos::ParameterEntry &,void>, "C++: Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::setObj(const std::string &, class Teuchos::ParameterEntry &) --> long", pybind11::arg("key"), pybind11::arg("obj"));
		cl.def("numObjects", (long (Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::*)() const) &Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::numObjects, "C++: Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::numObjects() const --> long");
		cl.def("numStorage", (long (Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::*)() const) &Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::numStorage, "C++: Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::numStorage() const --> long");
		cl.def("getObjOrdinalIndex", (long (Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::*)(const std::string &) const) &Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::getObjOrdinalIndex, "C++: Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::getObjOrdinalIndex(const std::string &) const --> long", pybind11::arg("key"));
		cl.def("getNonconstObjPtr", (class Teuchos::Ptr<class Teuchos::ParameterEntry> (Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::*)(const long &)) &Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::getNonconstObjPtr, "C++: Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::getNonconstObjPtr(const long &) --> class Teuchos::Ptr<class Teuchos::ParameterEntry>", pybind11::arg("idx"));
		cl.def("getObjPtr", (class Teuchos::Ptr<const class Teuchos::ParameterEntry> (Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::*)(const long &) const) &Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::getObjPtr, "C++: Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::getObjPtr(const long &) const --> class Teuchos::Ptr<const class Teuchos::ParameterEntry>", pybind11::arg("idx"));
		cl.def("getNonconstObjPtr", (class Teuchos::Ptr<class Teuchos::ParameterEntry> (Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::*)(const std::string &)) &Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::getNonconstObjPtr, "C++: Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::getNonconstObjPtr(const std::string &) --> class Teuchos::Ptr<class Teuchos::ParameterEntry>", pybind11::arg("key"));
		cl.def("getObjPtr", (class Teuchos::Ptr<const class Teuchos::ParameterEntry> (Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::*)(const std::string &) const) &Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::getObjPtr, "C++: Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::getObjPtr(const std::string &) const --> class Teuchos::Ptr<const class Teuchos::ParameterEntry>", pybind11::arg("key"));
		cl.def("removeObj", (void (Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::*)(const long &)) &Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::removeObj, "C++: Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::removeObj(const long &) --> void", pybind11::arg("idx"));
		cl.def("removeObj", (void (Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::*)(const std::string &)) &Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::removeObj, "C++: Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::removeObj(const std::string &) --> void", pybind11::arg("key"));
		cl.def("assign", (class Teuchos::StringIndexedOrderedValueObjectContainer<class Teuchos::ParameterEntry> & (Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::*)(const class Teuchos::StringIndexedOrderedValueObjectContainer<class Teuchos::ParameterEntry> &)) &Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::operator=, "C++: Teuchos::StringIndexedOrderedValueObjectContainer<Teuchos::ParameterEntry>::operator=(const class Teuchos::StringIndexedOrderedValueObjectContainer<class Teuchos::ParameterEntry> &) --> class Teuchos::StringIndexedOrderedValueObjectContainer<class Teuchos::ParameterEntry> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	// Teuchos::EValidateUsed file:Teuchos_ParameterList.hpp line:37
	pybind11::enum_<Teuchos::EValidateUsed>(M("Teuchos"), "EValidateUsed", pybind11::arithmetic(), "Validation used enum.\n \n\n\n ", pybind11::module_local())
		.value("VALIDATE_USED_ENABLED", Teuchos::VALIDATE_USED_ENABLED)
		.value("VALIDATE_USED_DISABLED", Teuchos::VALIDATE_USED_DISABLED)
		.export_values();

;

	// Teuchos::EValidateDefaults file:Teuchos_ParameterList.hpp line:49
	pybind11::enum_<Teuchos::EValidateDefaults>(M("Teuchos"), "EValidateDefaults", pybind11::arithmetic(), "Validation defaults enum.\n \n\n\n ", pybind11::module_local())
		.value("VALIDATE_DEFAULTS_ENABLED", Teuchos::VALIDATE_DEFAULTS_ENABLED)
		.value("VALIDATE_DEFAULTS_DISABLED", Teuchos::VALIDATE_DEFAULTS_DISABLED)
		.export_values();

;

	{ // Teuchos::ParameterList file:Teuchos_ParameterList.hpp line:101
		pybind11::class_<Teuchos::ParameterList, Teuchos::RCP<Teuchos::ParameterList>> cl(M("Teuchos"), "ParameterList", "A list of parameters of arbitrary type.\n\n  \n\n  A ParameterList is a map from parameter name (a string) to its\n  value.  The value may have any type with value semantics (see\n  explanation and examples below).  This includes another\n  ParameterList, which allows a ParameterList to encode a hierarchy of\n  parameters.  Different entries in the same ParameterList may have\n  values of different types.\n\n  Users may add a parameter using one of the get() methods, and\n  retrieve its value (given the parameter's name) using one of the\n  set() methods.  If the compiler gets confused when you use one of\n  the templated methods, you might have to help it by specifying the\n  type explicitly, or by casting the input object (using e.g.,\n  static_cast).  There are also methods for iterating through\n  all the parameters in a list, and for validating parameters using\n  validators that you may define for each parameter.\n\n  \n\n  A type has value semantics when it can be passed around as a\n  value.  This means that it has an assignment operator and a copy\n  constructor, and that the latter creates \"new objects\" (rather than\n  references that modify a single object).  Types with value semantics\n  include     and similar\n  types.\n\n  Paradoxically, pointers like double* also have value\n  semantics.  While the pointer is a reference to an object (e.g., an\n  array of double), the pointer itself is a value (an address\n  in memory).  The same holds for Teuchos' reference-counted pointer\n  and array classes (RCP resp. ArrayRCP).  While it is valid to store\n  pointers (\"raw\" or reference-counted) in a ParameterList, be aware\n  that this hinders serialization.  For example, a double*\n  could encode a single  or an array of   The\n  pointer itself does not encode the length of the array.  A\n  ParameterList serializer has no way to know what the\n  double* means.  ParameterList does not forbid you from\n  storing objects that cannot be correctly serialized, so you have to\n  know whether or not this concerns you.", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new Teuchos::ParameterList(); } ) );
		cl.def( pybind11::init( [](const std::string & a0){ return new Teuchos::ParameterList(a0); } ), "doc" , pybind11::arg("name"));
		cl.def( pybind11::init<const std::string &, const class Teuchos::RCP<const class Teuchos::ParameterListModifier> &>(), pybind11::arg("name"), pybind11::arg("modifier") );

		cl.def( pybind11::init( [](Teuchos::ParameterList const &o){ return new Teuchos::ParameterList(o); } ) );
		cl.def("getPtr", (const std::string * (Teuchos::ParameterList::*)(const std::string &) const) &Teuchos::ParameterList::getPtr<std::string>, "C++: Teuchos::ParameterList::getPtr(const std::string &) const --> const std::string *", pybind11::return_value_policy::automatic, pybind11::arg("name_in"));
		cl.def("setName", (class Teuchos::ParameterList & (Teuchos::ParameterList::*)(const std::string &)) &Teuchos::ParameterList::setName, "Set the name of *this list.\n\nC++: Teuchos::ParameterList::setName(const std::string &) --> class Teuchos::ParameterList &", pybind11::return_value_policy::automatic, pybind11::arg("name"));
		cl.def("assign", (class Teuchos::ParameterList & (Teuchos::ParameterList::*)(const class Teuchos::ParameterList &)) &Teuchos::ParameterList::operator=, "Replace the current parameter list with \n\n \n This also replaces the name returned by this->name()\n\nC++: Teuchos::ParameterList::operator=(const class Teuchos::ParameterList &) --> class Teuchos::ParameterList &", pybind11::return_value_policy::automatic, pybind11::arg("source"));
		cl.def("setModifier", (void (Teuchos::ParameterList::*)(const class Teuchos::RCP<const class Teuchos::ParameterListModifier> &)) &Teuchos::ParameterList::setModifier, "C++: Teuchos::ParameterList::setModifier(const class Teuchos::RCP<const class Teuchos::ParameterListModifier> &) --> void", pybind11::arg("modifier"));
		cl.def("setParameters", (class Teuchos::ParameterList & (Teuchos::ParameterList::*)(const class Teuchos::ParameterList &)) &Teuchos::ParameterList::setParameters, "Set the parameters in source.\n\n This function will set the parameters and sublists from\n source into *this, but will not remove\n parameters from *this.  Parameters in *this\n with the same names as those in source will be\n overwritten.\n\nC++: Teuchos::ParameterList::setParameters(const class Teuchos::ParameterList &) --> class Teuchos::ParameterList &", pybind11::return_value_policy::automatic, pybind11::arg("source"));
		cl.def("setParametersNotAlreadySet", (class Teuchos::ParameterList & (Teuchos::ParameterList::*)(const class Teuchos::ParameterList &)) &Teuchos::ParameterList::setParametersNotAlreadySet, "Set the parameters in source that are not already set in\n *this.\n\n Note, this function will set the parameters and sublists from\n source into *this but will not result in parameters\n being removed from *this or in parameters already set in\n *this being overrided.  Parameters in *this with the\n same names as those in source will not be overwritten.\n\nC++: Teuchos::ParameterList::setParametersNotAlreadySet(const class Teuchos::ParameterList &) --> class Teuchos::ParameterList &", pybind11::return_value_policy::automatic, pybind11::arg("source"));
		cl.def("disableRecursiveValidation", (class Teuchos::ParameterList & (Teuchos::ParameterList::*)()) &Teuchos::ParameterList::disableRecursiveValidation, "Disallow recusive validation when this sublist is used in a valid\n parameter list.\n\n This function should be called when setting a sublist in a valid\n parameter list which is broken off to be passed to another object.\n The other object should validate its own list.\n\nC++: Teuchos::ParameterList::disableRecursiveValidation() --> class Teuchos::ParameterList &", pybind11::return_value_policy::automatic);
		cl.def("disableRecursiveModification", (class Teuchos::ParameterList & (Teuchos::ParameterList::*)()) &Teuchos::ParameterList::disableRecursiveModification, "Disallow recursive modification when this sublist is used in a modified\n parameter list.\n\n This function should be called when setting a sublist in a modified\n parameter list which is broken off to be passed to another object.\n The other object should modify its own list.  The parameter list can\n still be modified using a direct call to its modify method.\n\nC++: Teuchos::ParameterList::disableRecursiveModification() --> class Teuchos::ParameterList &", pybind11::return_value_policy::automatic);
		cl.def("disableRecursiveReconciliation", (class Teuchos::ParameterList & (Teuchos::ParameterList::*)()) &Teuchos::ParameterList::disableRecursiveReconciliation, "Disallow recursive reconciliation when this sublist is used in a\n reconciled parameter list.\n\n This function should be called when setting a sublist in a reconciled\n parameter list which is broken off to be passed to another object.\n The other object should reconcile its own list.  The parameter list can\n still be reconciled using a direct call to its reconcile method.\n\nC++: Teuchos::ParameterList::disableRecursiveReconciliation() --> class Teuchos::ParameterList &", pybind11::return_value_policy::automatic);
		cl.def("disableRecursiveAll", (class Teuchos::ParameterList & (Teuchos::ParameterList::*)()) &Teuchos::ParameterList::disableRecursiveAll, "Disallow all recursive modification, validation, and reconciliation when\n this sublist is used in a parameter list.\n\n This function should be called when setting a sublist in a\n parameter list which is broken off to be passed to another object.\n The other object should handle its own list.\n\nC++: Teuchos::ParameterList::disableRecursiveAll() --> class Teuchos::ParameterList &", pybind11::return_value_policy::automatic);
		cl.def("getEntry", (class Teuchos::ParameterEntry & (Teuchos::ParameterList::*)(const std::string &)) &Teuchos::ParameterList::getEntry, "Retrieves an entry with the name name.\n\n Throws Exceptions::InvalidParameterName if this parameter does\n not exist.\n\nC++: Teuchos::ParameterList::getEntry(const std::string &) --> class Teuchos::ParameterEntry &", pybind11::return_value_policy::automatic, pybind11::arg("name"));
		cl.def("getEntryPtr", (class Teuchos::ParameterEntry * (Teuchos::ParameterList::*)(const std::string &)) &Teuchos::ParameterList::getEntryPtr, "Retrieves the pointer for an entry with the name name if\n  it exists. \n\nC++: Teuchos::ParameterList::getEntryPtr(const std::string &) --> class Teuchos::ParameterEntry *", pybind11::return_value_policy::automatic, pybind11::arg("name"));
		cl.def("getEntryRCP", (class Teuchos::RCP<class Teuchos::ParameterEntry> (Teuchos::ParameterList::*)(const std::string &)) &Teuchos::ParameterList::getEntryRCP, "Retrieves the RCP for an entry with the name name if\n  it exists. \n\nC++: Teuchos::ParameterList::getEntryRCP(const std::string &) --> class Teuchos::RCP<class Teuchos::ParameterEntry>", pybind11::arg("name"));
		cl.def("getModifier", (class Teuchos::RCP<const class Teuchos::ParameterListModifier> (Teuchos::ParameterList::*)() const) &Teuchos::ParameterList::getModifier, "Return the optional modifier object\n\nC++: Teuchos::ParameterList::getModifier() const --> class Teuchos::RCP<const class Teuchos::ParameterListModifier>");
		cl.def("remove", [](Teuchos::ParameterList &o, const std::string & a0) -> bool { return o.remove(a0); }, "", pybind11::arg("name"));
		cl.def("remove", (bool (Teuchos::ParameterList::*)(const std::string &, bool)) &Teuchos::ParameterList::remove, "Remove a parameter (does not depend on the type of the\n parameter).\n\n \n (in) The name of the parameter to remove\n\n \n (in) If true then if the parameter with\n the name name does not exist then a std::exception will be\n thrown!\n\n \n Returns true if the parameter was removed, and\n false if the parameter was not removed (false return\n value possible only if throwIfNotExists==false).\n\nC++: Teuchos::ParameterList::remove(const std::string &, bool) --> bool", pybind11::arg("name"), pybind11::arg("throwIfNotExists"));
		cl.def("name", (const std::string & (Teuchos::ParameterList::*)() const) &Teuchos::ParameterList::name, "The name of this ParameterList.\n\nC++: Teuchos::ParameterList::name() const --> const std::string &", pybind11::return_value_policy::automatic);
		cl.def("isParameter", (bool (Teuchos::ParameterList::*)(const std::string &) const) &Teuchos::ParameterList::isParameter, "Whether the given parameter exists in this list.\n\n Return true if a parameter with name  exists in this\n list, else return false.\n\nC++: Teuchos::ParameterList::isParameter(const std::string &) const --> bool", pybind11::arg("name"));
		cl.def("isSublist", (bool (Teuchos::ParameterList::*)(const std::string &) const) &Teuchos::ParameterList::isSublist, "Whether the given sublist exists in this list.\n\n Return true if a parameter with name  exists in this\n list, and is itself a ParameterList.  Otherwise, return false.\n\nC++: Teuchos::ParameterList::isSublist(const std::string &) const --> bool", pybind11::arg("name"));
		cl.def("numParams", (long (Teuchos::ParameterList::*)() const) &Teuchos::ParameterList::numParams, "Get the number of stored parameters.\n\nC++: Teuchos::ParameterList::numParams() const --> long");
		cl.def("print", (void (Teuchos::ParameterList::*)() const) &Teuchos::ParameterList::print, "Print function to use in debugging in a debugger.\n\n Prints to *VerboseObjectBase::getDefaultOStream() so it will print well\n in parallel.\n\nC++: Teuchos::ParameterList::print() const --> void");
		cl.def("print", (std::ostream & (Teuchos::ParameterList::*)(std::ostream &, const class Teuchos::ParameterList::PrintOptions &) const) &Teuchos::ParameterList::print, "Printing method for parameter lists which takes an print options\n  object.\n\nC++: Teuchos::ParameterList::print(std::ostream &, const class Teuchos::ParameterList::PrintOptions &) const --> std::ostream &", pybind11::return_value_policy::automatic, pybind11::arg("os"), pybind11::arg("printOptions"));
		cl.def("print", [](Teuchos::ParameterList const &o, std::ostream & a0) -> std::ostream & { return o.print(a0); }, "", pybind11::return_value_policy::automatic, pybind11::arg("os"));
		cl.def("print", [](Teuchos::ParameterList const &o, std::ostream & a0, int const & a1) -> std::ostream & { return o.print(a0, a1); }, "", pybind11::return_value_policy::automatic, pybind11::arg("os"), pybind11::arg("indent"));
		cl.def("print", [](Teuchos::ParameterList const &o, std::ostream & a0, int const & a1, bool const & a2) -> std::ostream & { return o.print(a0, a1, a2); }, "", pybind11::return_value_policy::automatic, pybind11::arg("os"), pybind11::arg("indent"), pybind11::arg("showTypes"));
		cl.def("print", [](Teuchos::ParameterList const &o, std::ostream & a0, int const & a1, bool const & a2, bool const & a3) -> std::ostream & { return o.print(a0, a1, a2, a3); }, "", pybind11::return_value_policy::automatic, pybind11::arg("os"), pybind11::arg("indent"), pybind11::arg("showTypes"), pybind11::arg("showFlags"));
		cl.def("print", (std::ostream & (Teuchos::ParameterList::*)(std::ostream &, int, bool, bool, bool) const) &Teuchos::ParameterList::print, "Printing method for parameter lists.  Indenting is used to indicate\n    parameter list hierarchies. \n\nC++: Teuchos::ParameterList::print(std::ostream &, int, bool, bool, bool) const --> std::ostream &", pybind11::return_value_policy::automatic, pybind11::arg("os"), pybind11::arg("indent"), pybind11::arg("showTypes"), pybind11::arg("showFlags"), pybind11::arg("showDefault"));
		cl.def("unused", (void (Teuchos::ParameterList::*)(std::ostream &) const) &Teuchos::ParameterList::unused, "Print out unused parameters in the ParameterList.\n\nC++: Teuchos::ParameterList::unused(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("currentParametersString", (std::string (Teuchos::ParameterList::*)() const) &Teuchos::ParameterList::currentParametersString, "Create a single formated std::string of all of the zero-level parameters in this list\n\nC++: Teuchos::ParameterList::currentParametersString() const --> std::string");
		cl.def("validateParameters", [](Teuchos::ParameterList const &o, const class Teuchos::ParameterList & a0) -> void { return o.validateParameters(a0); }, "", pybind11::arg("validParamList"));
		cl.def("validateParameters", [](Teuchos::ParameterList const &o, const class Teuchos::ParameterList & a0, const int & a1) -> void { return o.validateParameters(a0, a1); }, "", pybind11::arg("validParamList"), pybind11::arg("depth"));
		cl.def("validateParameters", [](Teuchos::ParameterList const &o, const class Teuchos::ParameterList & a0, const int & a1, const enum Teuchos::EValidateUsed & a2) -> void { return o.validateParameters(a0, a1, a2); }, "", pybind11::arg("validParamList"), pybind11::arg("depth"), pybind11::arg("validateUsed"));
		cl.def("validateParameters", (void (Teuchos::ParameterList::*)(const class Teuchos::ParameterList &, const int, const enum Teuchos::EValidateUsed, const enum Teuchos::EValidateDefaults) const) &Teuchos::ParameterList::validateParameters, "Validate the parameters in this list given valid selections in\n the input list.\n\n \n [in] This is the list that the parameters and\n sublist in *this are compared against.\n\n \n [in] Determines the number of levels of depth that the\n validation will recurse into.  A value of depth=0 means that\n only the top level parameters and sublists will be checked.  Default:\n depth = large number.\n\n \n [in] Determines if parameters that have been used are\n checked against those in validParamList.  Default:\n validateDefaults = VALIDATE_DEFAULTS_ENABLED.\n\n \n [in] Determines if parameters set at their\n default values using get(name,defaultVal) are checked against\n those in validParamList.  Default: validateDefaults =\n VALIDATE_DEFAULTS_ENABLED.\n\n If a parameter in *this is not found in validParamList\n then an std::exception of type\n Exceptions::InvalidParameterName will be thrown which will\n contain an excellent error message returned by excpt.what().  If\n the parameter exists but has the wrong type, then an std::exception type\n Exceptions::InvalidParameterType will be thrown.  If the\n parameter exists and has the right type, but the value is not valid then\n an std::exception type Exceptions::InvalidParameterValue will be\n thrown.\n\n Recursive validation stops when:\n\n The maxinum depth is reached\n\n A sublist note in validParamList has been marked with the\n disableRecursiveValidation() function, or\n\n There are not more parameters or sublists left in *this\n\n \n\n A breath-first search is performed to validate all of the parameters in\n one sublist before moving into nested subslist.\n\nC++: Teuchos::ParameterList::validateParameters(const class Teuchos::ParameterList &, const int, const enum Teuchos::EValidateUsed, const enum Teuchos::EValidateDefaults) const --> void", pybind11::arg("validParamList"), pybind11::arg("depth"), pybind11::arg("validateUsed"), pybind11::arg("validateDefaults"));
		cl.def("validateParametersAndSetDefaults", [](Teuchos::ParameterList &o, const class Teuchos::ParameterList & a0) -> void { return o.validateParametersAndSetDefaults(a0); }, "", pybind11::arg("validParamList"));
		cl.def("validateParametersAndSetDefaults", (void (Teuchos::ParameterList::*)(const class Teuchos::ParameterList &, const int)) &Teuchos::ParameterList::validateParametersAndSetDefaults, "Validate the parameters in this list given valid selections in\n the input list and set defaults for those not set.\n\n \n [in] This is the list that the parameters and\n sublist in *this are compared against.\n\n \n [in] Determines the number of levels of depth that the\n validation will recurse into.  A value of depth=0 means that\n only the top level parameters and sublists will be checked.  Default:\n depth = large number.\n\n If a parameter in *this is not found in validParamList\n then an std::exception of type Exceptions::InvalidParameterName will\n be thrown which will contain an excellent error message returned by\n excpt.what().  If the parameter exists but has the wrong type,\n then an std::exception type Exceptions::InvalidParameterType will be\n thrown.  If the parameter exists and has the right type, but the value is\n not valid then an std::exception type\n Exceptions::InvalidParameterValue will be thrown.  If a\n parameter in validParamList does not exist in *this,\n then it will be set at its default value as determined by\n validParamList.\n\n Recursive validation stops when:\n\n The maxinum depth is reached\n\n A sublist note in validParamList has been marked with the\n disableRecursiveValidation() function, or\n\n There are not more parameters or sublists left in *this\n\n \n\n A breath-first search is performed to validate all of the parameters in\n one sublist before moving into nested subslist.\n\nC++: Teuchos::ParameterList::validateParametersAndSetDefaults(const class Teuchos::ParameterList &, const int) --> void", pybind11::arg("validParamList"), pybind11::arg("depth"));
		cl.def("modifyParameterList", [](Teuchos::ParameterList &o, class Teuchos::ParameterList & a0) -> void { return o.modifyParameterList(a0); }, "", pybind11::arg("validParamList"));
		cl.def("modifyParameterList", (void (Teuchos::ParameterList::*)(class Teuchos::ParameterList &, const int)) &Teuchos::ParameterList::modifyParameterList, "Modify the valid parameter list prior to validation.\n\n \n [in,out] The parameter list used as a template for validation.\n\n \n [in] Determines the number of levels of depth that the\n modification will recurse into.  A value of depth=0 means that\n only the top level parameters and sublists will be checked.  Default:\n depth = large number.\n\n We loop over the valid parameter list in this modification routine.  This routine\n adds and/or removes fields in the valid parameter list to match the structure of the\n parameter list about to be validated.  After completion, both parameter lists should\n have the same fields or else an error will be thrown during validation.\n\nC++: Teuchos::ParameterList::modifyParameterList(class Teuchos::ParameterList &, const int) --> void", pybind11::arg("validParamList"), pybind11::arg("depth"));
		cl.def("reconcileParameterList", [](Teuchos::ParameterList &o, class Teuchos::ParameterList & a0) -> void { return o.reconcileParameterList(a0); }, "", pybind11::arg("validParamList"));
		cl.def("reconcileParameterList", (void (Teuchos::ParameterList::*)(class Teuchos::ParameterList &, const bool)) &Teuchos::ParameterList::reconcileParameterList, "Reconcile a parameter list after validation\n\n \n [in,out] The parameter list used as a template for validation.\n\n \n [in] Sweep through the parameter list tree from left to right.\n\n We loop through the valid parameter list in reverse breadth-first order in this reconciliation\n routine.  This routine assumes that the reconciliation routine won't create new sublists as it\n traverses the parameter list.\n\nC++: Teuchos::ParameterList::reconcileParameterList(class Teuchos::ParameterList &, const bool) --> void", pybind11::arg("validParamList"), pybind11::arg("left_to_right"));

		cl.def("__str__", [](Teuchos::ParameterList const &o) -> std::string { std::ostringstream s; using namespace Teuchos; s << o; return s.str(); } );

		def_ParameterList_member_functions(cl);

		{ // Teuchos::ParameterList::PrintOptions file:Teuchos_ParameterList.hpp line:118
			auto & enclosing_class = cl;
			pybind11::class_<Teuchos::ParameterList::PrintOptions, Teuchos::RCP<Teuchos::ParameterList::PrintOptions>> cl(enclosing_class, "PrintOptions", "Utility class for setting and passing in print options. ", pybind11::module_local());
			cl.def( pybind11::init( [](){ return new Teuchos::ParameterList::PrintOptions(); } ) );
			cl.def( pybind11::init( [](Teuchos::ParameterList::PrintOptions const &o){ return new Teuchos::ParameterList::PrintOptions(o); } ) );
			cl.def("indent", (class Teuchos::ParameterList::PrintOptions & (Teuchos::ParameterList::PrintOptions::*)(int)) &Teuchos::ParameterList::PrintOptions::indent, "C++: Teuchos::ParameterList::PrintOptions::indent(int) --> class Teuchos::ParameterList::PrintOptions &", pybind11::return_value_policy::automatic, pybind11::arg("_indent"));
			cl.def("showTypes", (class Teuchos::ParameterList::PrintOptions & (Teuchos::ParameterList::PrintOptions::*)(bool)) &Teuchos::ParameterList::PrintOptions::showTypes, "C++: Teuchos::ParameterList::PrintOptions::showTypes(bool) --> class Teuchos::ParameterList::PrintOptions &", pybind11::return_value_policy::automatic, pybind11::arg("_showTypes"));
			cl.def("showFlags", (class Teuchos::ParameterList::PrintOptions & (Teuchos::ParameterList::PrintOptions::*)(bool)) &Teuchos::ParameterList::PrintOptions::showFlags, "C++: Teuchos::ParameterList::PrintOptions::showFlags(bool) --> class Teuchos::ParameterList::PrintOptions &", pybind11::return_value_policy::automatic, pybind11::arg("_showFlags"));
			cl.def("showDoc", (class Teuchos::ParameterList::PrintOptions & (Teuchos::ParameterList::PrintOptions::*)(bool)) &Teuchos::ParameterList::PrintOptions::showDoc, "C++: Teuchos::ParameterList::PrintOptions::showDoc(bool) --> class Teuchos::ParameterList::PrintOptions &", pybind11::return_value_policy::automatic, pybind11::arg("_showDoc"));
			cl.def("showDefault", (class Teuchos::ParameterList::PrintOptions & (Teuchos::ParameterList::PrintOptions::*)(bool)) &Teuchos::ParameterList::PrintOptions::showDefault, "C++: Teuchos::ParameterList::PrintOptions::showDefault(bool) --> class Teuchos::ParameterList::PrintOptions &", pybind11::return_value_policy::automatic, pybind11::arg("_showDefault"));
			cl.def("incrIndent", (class Teuchos::ParameterList::PrintOptions & (Teuchos::ParameterList::PrintOptions::*)(int)) &Teuchos::ParameterList::PrintOptions::incrIndent, "C++: Teuchos::ParameterList::PrintOptions::incrIndent(int) --> class Teuchos::ParameterList::PrintOptions &", pybind11::return_value_policy::automatic, pybind11::arg("indents"));
			cl.def("indent", (int (Teuchos::ParameterList::PrintOptions::*)() const) &Teuchos::ParameterList::PrintOptions::indent, "C++: Teuchos::ParameterList::PrintOptions::indent() const --> int");
			cl.def("showTypes", (bool (Teuchos::ParameterList::PrintOptions::*)() const) &Teuchos::ParameterList::PrintOptions::showTypes, "C++: Teuchos::ParameterList::PrintOptions::showTypes() const --> bool");
			cl.def("showFlags", (bool (Teuchos::ParameterList::PrintOptions::*)() const) &Teuchos::ParameterList::PrintOptions::showFlags, "C++: Teuchos::ParameterList::PrintOptions::showFlags() const --> bool");
			cl.def("showDoc", (bool (Teuchos::ParameterList::PrintOptions::*)() const) &Teuchos::ParameterList::PrintOptions::showDoc, "C++: Teuchos::ParameterList::PrintOptions::showDoc() const --> bool");
			cl.def("showDefault", (bool (Teuchos::ParameterList::PrintOptions::*)() const) &Teuchos::ParameterList::PrintOptions::showDefault, "C++: Teuchos::ParameterList::PrintOptions::showDefault() const --> bool");
			cl.def("copy", (class Teuchos::ParameterList::PrintOptions (Teuchos::ParameterList::PrintOptions::*)() const) &Teuchos::ParameterList::PrintOptions::copy, "C++: Teuchos::ParameterList::PrintOptions::copy() const --> class Teuchos::ParameterList::PrintOptions");
		}

	}
	// Teuchos::parameterList() file:Teuchos_ParameterList.hpp line:793
	M("Teuchos").def("parameterList", (class Teuchos::RCP<class Teuchos::ParameterList> (*)()) &Teuchos::parameterList, "Nonmember constructor.\n\n \n\n \n\nC++: Teuchos::parameterList() --> class Teuchos::RCP<class Teuchos::ParameterList>");

	// Teuchos::parameterList(const std::string &) file:Teuchos_ParameterList.hpp line:804
	M("Teuchos").def("parameterList", (class Teuchos::RCP<class Teuchos::ParameterList> (*)(const std::string &)) &Teuchos::parameterList, "Nonmember constructor.\n\n \n\n \n\nC++: Teuchos::parameterList(const std::string &) --> class Teuchos::RCP<class Teuchos::ParameterList>", pybind11::arg("name"));

	// Teuchos::parameterList(const class Teuchos::ParameterList &) file:Teuchos_ParameterList.hpp line:815
	M("Teuchos").def("parameterList", (class Teuchos::RCP<class Teuchos::ParameterList> (*)(const class Teuchos::ParameterList &)) &Teuchos::parameterList, "Nonmember constructor.\n\n \n\n \n\nC++: Teuchos::parameterList(const class Teuchos::ParameterList &) --> class Teuchos::RCP<class Teuchos::ParameterList>", pybind11::arg("source"));

	// Teuchos::createParameterList() file:Teuchos_ParameterList.hpp line:826
	M("Teuchos").def("createParameterList", (class Teuchos::RCP<class Teuchos::ParameterList> (*)()) &Teuchos::createParameterList, "Nonmember constructor.\n\n \n\n \n\nC++: Teuchos::createParameterList() --> class Teuchos::RCP<class Teuchos::ParameterList>");

	// Teuchos::createParameterList(const std::string &) file:Teuchos_ParameterList.hpp line:837
	M("Teuchos").def("createParameterList", (class Teuchos::RCP<class Teuchos::ParameterList> (*)(const std::string &)) &Teuchos::createParameterList, "Nonmember constructor.\n\n \n\n \n\nC++: Teuchos::createParameterList(const std::string &) --> class Teuchos::RCP<class Teuchos::ParameterList>", pybind11::arg("name"));

	// Teuchos::haveSameModifiers(const class Teuchos::ParameterList &, const class Teuchos::ParameterList &) file:Teuchos_ParameterList.hpp line:883
	M("Teuchos").def("haveSameModifiers", (bool (*)(const class Teuchos::ParameterList &, const class Teuchos::ParameterList &)) &Teuchos::haveSameModifiers, "Return true if a modified parameter list has the same modifiers as the modified parameter\n list being used as input.\n\nC++: Teuchos::haveSameModifiers(const class Teuchos::ParameterList &, const class Teuchos::ParameterList &) --> bool", pybind11::arg("list1"), pybind11::arg("list2"));

	// Teuchos::haveSameValues(const class Teuchos::ParameterList &, const class Teuchos::ParameterList &, bool) file:Teuchos_ParameterList.hpp line:898
	M("Teuchos").def("haveSameValues", [](const class Teuchos::ParameterList & a0, const class Teuchos::ParameterList & a1) -> bool { return Teuchos::haveSameValues(a0, a1); }, "", pybind11::arg("list1"), pybind11::arg("list2"));
	M("Teuchos").def("haveSameValues", (bool (*)(const class Teuchos::ParameterList &, const class Teuchos::ParameterList &, bool)) &Teuchos::haveSameValues, "Returns true if two parameter lists have the same values.\n\n Two parameter lists may have the same values but may not be identical.  For\n example, two parameters can have the same values but not have the same\n documentation strings or the same validators.\n\n \n This function respects ordering of the ParameterList entries; the same values in a different\n       order will result in \n\n \n\n \n\nC++: Teuchos::haveSameValues(const class Teuchos::ParameterList &, const class Teuchos::ParameterList &, bool) --> bool", pybind11::arg("list1"), pybind11::arg("list2"), pybind11::arg("verbose"));

	// Teuchos::haveSameValuesSorted(const class Teuchos::ParameterList &, const class Teuchos::ParameterList &, bool) file:Teuchos_ParameterList.hpp line:913
	M("Teuchos").def("haveSameValuesSorted", [](const class Teuchos::ParameterList & a0, const class Teuchos::ParameterList & a1) -> bool { return Teuchos::haveSameValuesSorted(a0, a1); }, "", pybind11::arg("list1"), pybind11::arg("list2"));
	M("Teuchos").def("haveSameValuesSorted", (bool (*)(const class Teuchos::ParameterList &, const class Teuchos::ParameterList &, bool)) &Teuchos::haveSameValuesSorted, "Returns true if two parameter lists have the same values independent of ordering.\n\n Two parameter lists may have the same values but may not be identical.  For\n example, two parameters can have the same values but not have the same\n documentation strings or the same validators.\n\n \n This function does not respect ordering of the ParameterList entries; the same values in a different\n       order will result in \n\n \n\n \n\nC++: Teuchos::haveSameValuesSorted(const class Teuchos::ParameterList &, const class Teuchos::ParameterList &, bool) --> bool", pybind11::arg("list1"), pybind11::arg("list2"), pybind11::arg("verbose"));

	// Teuchos::getParameter(const class Teuchos::ParameterList &, const std::string &) file:Teuchos_ParameterList.hpp line:1321
	M("Teuchos").def("getParameter", (const std::string & (*)(const class Teuchos::ParameterList &, const std::string &)) &Teuchos::getParameter<std::string>, "C++: Teuchos::getParameter(const class Teuchos::ParameterList &, const std::string &) --> const std::string &", pybind11::return_value_policy::automatic, pybind11::arg("l"), pybind11::arg("name"));

	// Teuchos::getParameterPtr(const class Teuchos::ParameterList &, const std::string &) file:Teuchos_ParameterList.hpp line:1351
	M("Teuchos").def("getParameterPtr", (const std::string * (*)(const class Teuchos::ParameterList &, const std::string &)) &Teuchos::getParameterPtr<std::string>, "C++: Teuchos::getParameterPtr(const class Teuchos::ParameterList &, const std::string &) --> const std::string *", pybind11::return_value_policy::automatic, pybind11::arg("l"), pybind11::arg("name"));

	// Teuchos::sublist(const class Teuchos::RCP<class Teuchos::ParameterList> &, const std::string &, bool, const std::string &) file:Teuchos_ParameterList.hpp line:1563
	M("Teuchos").def("sublist", [](const class Teuchos::RCP<class Teuchos::ParameterList> & a0, const std::string & a1) -> Teuchos::RCP<class Teuchos::ParameterList> { return Teuchos::sublist(a0, a1); }, "", pybind11::arg("paramList"), pybind11::arg("name"));
	M("Teuchos").def("sublist", [](const class Teuchos::RCP<class Teuchos::ParameterList> & a0, const std::string & a1, bool const & a2) -> Teuchos::RCP<class Teuchos::ParameterList> { return Teuchos::sublist(a0, a1, a2); }, "", pybind11::arg("paramList"), pybind11::arg("name"), pybind11::arg("mustAlreadyExist"));
	M("Teuchos").def("sublist", (class Teuchos::RCP<class Teuchos::ParameterList> (*)(const class Teuchos::RCP<class Teuchos::ParameterList> &, const std::string &, bool, const std::string &)) &Teuchos::sublist, "Return a RCP to a sublist in another RCP-ed parameter list.\n\nC++: Teuchos::sublist(const class Teuchos::RCP<class Teuchos::ParameterList> &, const std::string &, bool, const std::string &) --> class Teuchos::RCP<class Teuchos::ParameterList>", pybind11::arg("paramList"), pybind11::arg("name"), pybind11::arg("mustAlreadyExist"), pybind11::arg("docString"));

	// Teuchos::sublist(const class Teuchos::RCP<const class Teuchos::ParameterList> &, const std::string &) file:Teuchos_ParameterList.hpp line:1577
	M("Teuchos").def("sublist", (class Teuchos::RCP<const class Teuchos::ParameterList> (*)(const class Teuchos::RCP<const class Teuchos::ParameterList> &, const std::string &)) &Teuchos::sublist, "Return a RCP to a sublist in another RCP-ed parameter list.\n\nC++: Teuchos::sublist(const class Teuchos::RCP<const class Teuchos::ParameterList> &, const std::string &) --> class Teuchos::RCP<const class Teuchos::ParameterList>", pybind11::arg("paramList"), pybind11::arg("name"));

	{ // Teuchos::InvalidDependencyException file:Teuchos_InvalidDependencyException.hpp line:19
		pybind11::class_<Teuchos::InvalidDependencyException, Teuchos::RCP<Teuchos::InvalidDependencyException>, PyCallBack_Teuchos_InvalidDependencyException> cl(M("Teuchos"), "InvalidDependencyException", "Thrown when some aspect of a Dependency has been determined to be invalid.", pybind11::module_local());
		cl.def( pybind11::init<const std::string &>(), pybind11::arg("what_arg") );

		cl.def( pybind11::init( [](PyCallBack_Teuchos_InvalidDependencyException const &o){ return new PyCallBack_Teuchos_InvalidDependencyException(o); } ) );
		cl.def( pybind11::init( [](Teuchos::InvalidDependencyException const &o){ return new Teuchos::InvalidDependencyException(o); } ) );
		cl.def("assign", (class Teuchos::InvalidDependencyException & (Teuchos::InvalidDependencyException::*)(const class Teuchos::InvalidDependencyException &)) &Teuchos::InvalidDependencyException::operator=, "C++: Teuchos::InvalidDependencyException::operator=(const class Teuchos::InvalidDependencyException &) --> class Teuchos::InvalidDependencyException &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
}
