#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_ValidateFunction.hpp>
#include <ROL_Vector.hpp>
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

// ROL::details::ValidateFunction file: line:66
struct PyCallBack_ROL_details_ValidateFunction_double_t : public ROL::details::ValidateFunction<double> {
	using ROL::details::ValidateFunction<double>::ValidateFunction;

	class std::vector<class std::vector<double> > derivative_check(class std::function<double (const class ROL::Vector<double> &)> a0, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)> a1, class std::function<void (const class ROL::Vector<double> &)> a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5, const std::string & a6) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::details::ValidateFunction<double> *>(this), "derivative_check");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return ValidateFunction::derivative_check(a0, a1, a2, a3, a4, a5, a6);
	}
	class std::vector<class std::vector<double> > derivative_check(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)> a0, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> a1, class std::function<void (const class ROL::Vector<double> &)> a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5, const std::string & a6) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::details::ValidateFunction<double> *>(this), "derivative_check");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return ValidateFunction::derivative_check(a0, a1, a2, a3, a4, a5, a6);
	}
	class std::vector<double> symmetry_check(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> a0, class std::function<void (const class ROL::Vector<double> &)> a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const std::string & a5, const std::string & a6) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::details::ValidateFunction<double> *>(this), "symmetry_check");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<double>>::value) {
				static pybind11::detail::override_caster_t<class std::vector<double>> caster;
				return pybind11::detail::cast_ref<class std::vector<double>>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<double>>(std::move(o));
		}
		return ValidateFunction::symmetry_check(a0, a1, a2, a3, a4, a5, a6);
	}
	class std::vector<double> adjoint_consistency_check(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> a0, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> a1, class std::function<void (const class ROL::Vector<double> &)> a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5, const std::string & a6, const std::string & a7) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::details::ValidateFunction<double> *>(this), "adjoint_consistency_check");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6, a7);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<double>>::value) {
				static pybind11::detail::override_caster_t<class std::vector<double>> caster;
				return pybind11::detail::cast_ref<class std::vector<double>>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<double>>(std::move(o));
		}
		return ValidateFunction::adjoint_consistency_check(a0, a1, a2, a3, a4, a5, a6, a7);
	}
	class std::vector<double> inverse_check(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> a0, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> a1, class std::function<void (const class ROL::Vector<double> &)> a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const std::string & a5, const std::string & a6) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::details::ValidateFunction<double> *>(this), "inverse_check");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<double>>::value) {
				static pybind11::detail::override_caster_t<class std::vector<double>> caster;
				return pybind11::detail::cast_ref<class std::vector<double>>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<double>>(std::move(o));
		}
		return ValidateFunction::inverse_check(a0, a1, a2, a3, a4, a5, a6);
	}
	class std::vector<double> solve_check(class std::function<void (class ROL::Vector<double> &, class ROL::Vector<double> &)> a0, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)> a1, class std::function<void (const class ROL::Vector<double> &)> a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const std::string & a5) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::details::ValidateFunction<double> *>(this), "solve_check");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<double>>::value) {
				static pybind11::detail::override_caster_t<class std::vector<double>> caster;
				return pybind11::detail::cast_ref<class std::vector<double>>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<double>>(std::move(o));
		}
		return ValidateFunction::solve_check(a0, a1, a2, a3, a4, a5);
	}
};

void bind_pyrol_76(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::details::ValidateFunction file: line:66
		pybind11::class_<ROL::details::ValidateFunction<double>, Teuchos::RCP<ROL::details::ValidateFunction<double>>, PyCallBack_ROL_details_ValidateFunction_double_t> cl(M("ROL::details"), "ValidateFunction_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::details::ValidateFunction<double>(); }, [](){ return new PyCallBack_ROL_details_ValidateFunction_double_t(); } ), "doc");
		cl.def( pybind11::init( [](const int & a0){ return new ROL::details::ValidateFunction<double>(a0); }, [](const int & a0){ return new PyCallBack_ROL_details_ValidateFunction_double_t(a0); } ), "doc");
		cl.def( pybind11::init( [](const int & a0, const int & a1){ return new ROL::details::ValidateFunction<double>(a0, a1); }, [](const int & a0, const int & a1){ return new PyCallBack_ROL_details_ValidateFunction_double_t(a0, a1); } ), "doc");
		cl.def( pybind11::init( [](const int & a0, const int & a1, const int & a2){ return new ROL::details::ValidateFunction<double>(a0, a1, a2); }, [](const int & a0, const int & a1, const int & a2){ return new PyCallBack_ROL_details_ValidateFunction_double_t(a0, a1, a2); } ), "doc");
		cl.def( pybind11::init( [](const int & a0, const int & a1, const int & a2, const int & a3){ return new ROL::details::ValidateFunction<double>(a0, a1, a2, a3); }, [](const int & a0, const int & a1, const int & a2, const int & a3){ return new PyCallBack_ROL_details_ValidateFunction_double_t(a0, a1, a2, a3); } ), "doc");
		cl.def( pybind11::init( [](const int & a0, const int & a1, const int & a2, const int & a3, const bool & a4){ return new ROL::details::ValidateFunction<double>(a0, a1, a2, a3, a4); }, [](const int & a0, const int & a1, const int & a2, const int & a3, const bool & a4){ return new PyCallBack_ROL_details_ValidateFunction_double_t(a0, a1, a2, a3, a4); } ), "doc");
		cl.def( pybind11::init<const int, const int, const int, const int, const bool, std::ostream &>(), pybind11::arg("order"), pybind11::arg("numSteps"), pybind11::arg("width"), pybind11::arg("precision"), pybind11::arg("printToStream"), pybind11::arg("os") );

		cl.def( pybind11::init( [](PyCallBack_ROL_details_ValidateFunction_double_t const &o){ return new PyCallBack_ROL_details_ValidateFunction_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::details::ValidateFunction<double> const &o){ return new ROL::details::ValidateFunction<double>(o); } ) );
		cl.def("derivative_check", (class std::vector<class std::vector<double> > (ROL::details::ValidateFunction<double>::*)(class std::function<double (const class ROL::Vector<double> &)>, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (const class ROL::Vector<double> &)>, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const std::string &) const) &ROL::details::ValidateFunction<double>::derivative_check, "C++: ROL::details::ValidateFunction<double>::derivative_check(class std::function<double (const class ROL::Vector<double> &)>, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (const class ROL::Vector<double> &)>, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const std::string &) const --> class std::vector<class std::vector<double> >", pybind11::arg("f_value"), pybind11::arg("f_derivative"), pybind11::arg("f_update"), pybind11::arg("g"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("label"));
		cl.def("derivative_check", (class std::vector<class std::vector<double> > (ROL::details::ValidateFunction<double>::*)(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (const class ROL::Vector<double> &)>, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const std::string &) const) &ROL::details::ValidateFunction<double>::derivative_check, "C++: ROL::details::ValidateFunction<double>::derivative_check(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (const class ROL::Vector<double> &)>, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const std::string &) const --> class std::vector<class std::vector<double> >", pybind11::arg("f_value"), pybind11::arg("f_derivative"), pybind11::arg("f_update"), pybind11::arg("c"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("label"));
		cl.def("symmetry_check", [](ROL::details::ValidateFunction<double> const &o, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> const & a0, class std::function<void (const class ROL::Vector<double> &)> const & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4) -> std::vector<double> { return o.symmetry_check(a0, a1, a2, a3, a4); }, "", pybind11::arg("A"), pybind11::arg("A_update"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("x"));
		cl.def("symmetry_check", [](ROL::details::ValidateFunction<double> const &o, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> const & a0, class std::function<void (const class ROL::Vector<double> &)> const & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const std::string & a5) -> std::vector<double> { return o.symmetry_check(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("A"), pybind11::arg("A_update"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("name"));
		cl.def("symmetry_check", (class std::vector<double> (ROL::details::ValidateFunction<double>::*)(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (const class ROL::Vector<double> &)>, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const std::string &, const std::string &) const) &ROL::details::ValidateFunction<double>::symmetry_check, "C++: ROL::details::ValidateFunction<double>::symmetry_check(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (const class ROL::Vector<double> &)>, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const std::string &, const std::string &) const --> class std::vector<double>", pybind11::arg("A"), pybind11::arg("A_update"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("name"), pybind11::arg("symbol"));
		cl.def("adjoint_consistency_check", [](ROL::details::ValidateFunction<double> const &o, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> const & a0, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> const & a1, class std::function<void (const class ROL::Vector<double> &)> const & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5) -> std::vector<double> { return o.adjoint_consistency_check(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("A"), pybind11::arg("A_adj"), pybind11::arg("A_update"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("x"));
		cl.def("adjoint_consistency_check", [](ROL::details::ValidateFunction<double> const &o, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> const & a0, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> const & a1, class std::function<void (const class ROL::Vector<double> &)> const & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const class ROL::Vector<double> & a5, const std::string & a6) -> std::vector<double> { return o.adjoint_consistency_check(a0, a1, a2, a3, a4, a5, a6); }, "", pybind11::arg("A"), pybind11::arg("A_adj"), pybind11::arg("A_update"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("name"));
		cl.def("adjoint_consistency_check", (class std::vector<double> (ROL::details::ValidateFunction<double>::*)(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (const class ROL::Vector<double> &)>, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const std::string &, const std::string &) const) &ROL::details::ValidateFunction<double>::adjoint_consistency_check, "C++: ROL::details::ValidateFunction<double>::adjoint_consistency_check(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (const class ROL::Vector<double> &)>, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const std::string &, const std::string &) const --> class std::vector<double>", pybind11::arg("A"), pybind11::arg("A_adj"), pybind11::arg("A_update"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("name"), pybind11::arg("symbol"));
		cl.def("inverse_check", [](ROL::details::ValidateFunction<double> const &o, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> const & a0, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> const & a1, class std::function<void (const class ROL::Vector<double> &)> const & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4) -> std::vector<double> { return o.inverse_check(a0, a1, a2, a3, a4); }, "", pybind11::arg("A"), pybind11::arg("A_inv"), pybind11::arg("A_update"), pybind11::arg("v"), pybind11::arg("x"));
		cl.def("inverse_check", [](ROL::details::ValidateFunction<double> const &o, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> const & a0, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)> const & a1, class std::function<void (const class ROL::Vector<double> &)> const & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const std::string & a5) -> std::vector<double> { return o.inverse_check(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("A"), pybind11::arg("A_inv"), pybind11::arg("A_update"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("name"));
		cl.def("inverse_check", (class std::vector<double> (ROL::details::ValidateFunction<double>::*)(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (const class ROL::Vector<double> &)>, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const std::string &, const std::string &) const) &ROL::details::ValidateFunction<double>::inverse_check, "C++: ROL::details::ValidateFunction<double>::inverse_check(class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (const class ROL::Vector<double> &)>, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const std::string &, const std::string &) const --> class std::vector<double>", pybind11::arg("A"), pybind11::arg("A_inv"), pybind11::arg("A_update"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("name"), pybind11::arg("symbol"));
		cl.def("solve_check", [](ROL::details::ValidateFunction<double> const &o, class std::function<void (class ROL::Vector<double> &, class ROL::Vector<double> &)> const & a0, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)> const & a1, class std::function<void (const class ROL::Vector<double> &)> const & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4) -> std::vector<double> { return o.solve_check(a0, a1, a2, a3, a4); }, "", pybind11::arg("solve"), pybind11::arg("value"), pybind11::arg("update"), pybind11::arg("c"), pybind11::arg("x"));
		cl.def("solve_check", (class std::vector<double> (ROL::details::ValidateFunction<double>::*)(class std::function<void (class ROL::Vector<double> &, class ROL::Vector<double> &)>, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (const class ROL::Vector<double> &)>, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const std::string &) const) &ROL::details::ValidateFunction<double>::solve_check, "C++: ROL::details::ValidateFunction<double>::solve_check(class std::function<void (class ROL::Vector<double> &, class ROL::Vector<double> &)>, class std::function<void (class ROL::Vector<double> &, const class ROL::Vector<double> &)>, class std::function<void (const class ROL::Vector<double> &)>, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const std::string &) const --> class std::vector<double>", pybind11::arg("solve"), pybind11::arg("value"), pybind11::arg("update"), pybind11::arg("c"), pybind11::arg("x"), pybind11::arg("name"));
		cl.def("getStream", (std::ostream & (ROL::details::ValidateFunction<double>::*)() const) &ROL::details::ValidateFunction<double>::getStream, "C++: ROL::details::ValidateFunction<double>::getStream() const --> std::ostream &", pybind11::return_value_policy::automatic);
	}
}
