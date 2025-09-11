#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_FiniteDifference.hpp>
#include <ROL_Vector.hpp>
#include <ROL_VectorWorkspace.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <functional>
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

// ROL::details::FiniteDifference file:ROL_FiniteDifference.hpp line:32
struct PyCallBack_ROL_details_FiniteDifference_double_t : public ROL::details::FiniteDifference<double> {
	using ROL::details::FiniteDifference<double>::FiniteDifference;

	double operator()(class std::function<double (const class ROL::Vector<double> &)> & a0, class std::function<void (const class ROL::Vector<double> &)> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const double a4) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::details::FiniteDifference<double> *>(this), "__call__");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return FiniteDifference::operator()(a0, a1, a2, a3, a4);
	}
	void operator()(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)> & a0, class std::function<void (const class ROL::Vector<double> &)> & a1, class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const double a5) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::details::FiniteDifference<double> *>(this), "__call__");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return FiniteDifference::operator()(a0, a1, a2, a3, a4, a5);
	}
};

void bind_pyrol_46(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::details::FiniteDifference file:ROL_FiniteDifference.hpp line:32
		pybind11::class_<ROL::details::FiniteDifference<double>, Teuchos::RCP<ROL::details::FiniteDifference<double>>, PyCallBack_ROL_details_FiniteDifference_double_t> cl(M("ROL::details"), "FiniteDifference_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::details::FiniteDifference<double>(); }, [](){ return new PyCallBack_ROL_details_FiniteDifference_double_t(); } ), "doc");
		cl.def( pybind11::init<const int>(), pybind11::arg("order") );

		cl.def( pybind11::init<const int, const class Teuchos::RCP<class ROL::details::VectorWorkspace<double> > &>(), pybind11::arg("order"), pybind11::arg("workspace") );

		cl.def( pybind11::init( [](PyCallBack_ROL_details_FiniteDifference_double_t const &o){ return new PyCallBack_ROL_details_FiniteDifference_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::details::FiniteDifference<double> const &o){ return new ROL::details::FiniteDifference<double>(o); } ) );
		cl.def("__call__", (double (ROL::details::FiniteDifference<double>::*)(class std::function<double (const class ROL::Vector<double> &)> &, class std::function<void (const class ROL::Vector<double> &)> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double) const) &ROL::details::FiniteDifference<double>::operator(), "C++: ROL::details::FiniteDifference<double>::operator()(class std::function<double (const class ROL::Vector<double> &)> &, class std::function<void (const class ROL::Vector<double> &)> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double) const --> double", pybind11::arg("f_value"), pybind11::arg("f_update"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("h"));
		cl.def("__call__", (void (ROL::details::FiniteDifference<double>::*)(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)> &, class std::function<void (const class ROL::Vector<double> &)> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double) const) &ROL::details::FiniteDifference<double>::operator(), "C++: ROL::details::FiniteDifference<double>::operator()(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)> &, class std::function<void (const class ROL::Vector<double> &)> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double) const --> void", pybind11::arg("f_value"), pybind11::arg("f_update"), pybind11::arg("Jv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("h"));
	}
}
