#include <ROL_DynamicFunction.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_TimeStamp.hpp>
#include <ROL_Vector.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <ios>
#include <iterator>
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

// ROL::DynamicFunction file:ROL_DynamicFunction.hpp line:33
struct PyCallBack_ROL_DynamicFunction_double_t : public ROL::DynamicFunction<double> {
	using ROL::DynamicFunction<double>::DynamicFunction;

	void update_uo(const class ROL::Vector<double> & a0, const struct ROL::TimeStamp<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicFunction<double> *>(this), "update_uo");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicFunction::update_uo(a0, a1);
	}
	void update_un(const class ROL::Vector<double> & a0, const struct ROL::TimeStamp<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicFunction<double> *>(this), "update_un");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicFunction::update_un(a0, a1);
	}
	void update_z(const class ROL::Vector<double> & a0, const struct ROL::TimeStamp<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicFunction<double> *>(this), "update_z");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicFunction::update_z(a0, a1);
	}
};

void bind_pyrol_38(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::DynamicFunction file:ROL_DynamicFunction.hpp line:33
		PYBIND11_TYPE_CASTER_BASE_HOLDER(ROL::DynamicFunction<double> , Teuchos::RCP<ROL::DynamicFunction<double>>)
		pybind11::class_<ROL::DynamicFunction<double>, Teuchos::RCP<ROL::DynamicFunction<double>>, PyCallBack_ROL_DynamicFunction_double_t> cl(M("ROL"), "DynamicFunction_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](PyCallBack_ROL_DynamicFunction_double_t const &o){ return new PyCallBack_ROL_DynamicFunction_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::DynamicFunction<double> const &o){ return new ROL::DynamicFunction<double>(o); } ) );
		cl.def("update_uo", (void (ROL::DynamicFunction<double>::*)(const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &)) &ROL::DynamicFunction<double>::update_uo, "C++: ROL::DynamicFunction<double>::update_uo(const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) --> void", pybind11::arg("x"), pybind11::arg("ts"));
		cl.def("update_un", (void (ROL::DynamicFunction<double>::*)(const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &)) &ROL::DynamicFunction<double>::update_un, "C++: ROL::DynamicFunction<double>::update_un(const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) --> void", pybind11::arg("x"), pybind11::arg("ts"));
		cl.def("update_z", (void (ROL::DynamicFunction<double>::*)(const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &)) &ROL::DynamicFunction<double>::update_z, "C++: ROL::DynamicFunction<double>::update_z(const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) --> void", pybind11::arg("x"), pybind11::arg("ts"));
		cl.def("is_zero_derivative", (bool (ROL::DynamicFunction<double>::*)(const std::string &)) &ROL::DynamicFunction<double>::is_zero_derivative, "C++: ROL::DynamicFunction<double>::is_zero_derivative(const std::string &) --> bool", pybind11::arg("key"));
		cl.def("assign", (class ROL::DynamicFunction<double> & (ROL::DynamicFunction<double>::*)(const class ROL::DynamicFunction<double> &)) &ROL::DynamicFunction<double>::operator=, "C++: ROL::DynamicFunction<double>::operator=(const class ROL::DynamicFunction<double> &) --> class ROL::DynamicFunction<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
}
