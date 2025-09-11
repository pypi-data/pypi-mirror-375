#include <ROL_BoundConstraint.hpp>
#include <ROL_Constraint.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_ReducedLinearConstraint.hpp>
#include <ROL_UpdateType.hpp>
#include <ROL_Vector.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <ios>
#include <iterator>
#include <locale>
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

// ROL::ReducedLinearConstraint file:ROL_ReducedLinearConstraint.hpp line:33
struct PyCallBack_ROL_ReducedLinearConstraint_double_t : public ROL::ReducedLinearConstraint<double> {
	using ROL::ReducedLinearConstraint<double>::ReducedLinearConstraint;

	void value(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "value");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ReducedLinearConstraint::value(a0, a1, a2);
	}
	void applyJacobian(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "applyJacobian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ReducedLinearConstraint::applyJacobian(a0, a1, a2, a3);
	}
	void applyAdjointJacobian(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "applyAdjointJacobian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ReducedLinearConstraint::applyAdjointJacobian(a0, a1, a2, a3);
	}
	void applyAdjointHessian(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, double & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "applyAdjointHessian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ReducedLinearConstraint::applyAdjointHessian(a0, a1, a2, a3, a4);
	}
	void update(const class ROL::Vector<double> & a0, enum ROL::UpdateType a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Constraint::update(a0, a1, a2);
	}
	void update(const class ROL::Vector<double> & a0, bool a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Constraint::update(a0, a1, a2);
	}
	void applyAdjointJacobian(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, double & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "applyAdjointJacobian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Constraint::applyAdjointJacobian(a0, a1, a2, a3, a4);
	}
	class std::vector<double> solveAugmentedSystem(class ROL::Vector<double> & a0, class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, double & a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "solveAugmentedSystem");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<double>>::value) {
				static pybind11::detail::override_caster_t<class std::vector<double>> caster;
				return pybind11::detail::cast_ref<class std::vector<double>>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<double>>(std::move(o));
		}
		return Constraint::solveAugmentedSystem(a0, a1, a2, a3, a4, a5);
	}
	void applyPreconditioner(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, double & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "applyPreconditioner");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Constraint::applyPreconditioner(a0, a1, a2, a3, a4);
	}
	class std::vector<class std::vector<double> > checkApplyJacobian(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class std::vector<double> & a3, const bool a4, std::ostream & a5, const int a6) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "checkApplyJacobian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Constraint::checkApplyJacobian(a0, a1, a2, a3, a4, a5, a6);
	}
	class std::vector<class std::vector<double> > checkApplyJacobian(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool a3, std::ostream & a4, const int a5, const int a6) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "checkApplyJacobian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Constraint::checkApplyJacobian(a0, a1, a2, a3, a4, a5, a6);
	}
	class std::vector<class std::vector<double> > checkApplyAdjointJacobian(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const bool a4, std::ostream & a5, const int a6) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "checkApplyAdjointJacobian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Constraint::checkApplyAdjointJacobian(a0, a1, a2, a3, a4, a5, a6);
	}
	double checkAdjointConsistencyJacobian(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool a3, std::ostream & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "checkAdjointConsistencyJacobian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return Constraint::checkAdjointConsistencyJacobian(a0, a1, a2, a3, a4);
	}
	double checkAdjointConsistencyJacobian(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const bool a5, std::ostream & a6) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "checkAdjointConsistencyJacobian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return Constraint::checkAdjointConsistencyJacobian(a0, a1, a2, a3, a4, a5, a6);
	}
	class std::vector<class std::vector<double> > checkApplyAdjointHessian(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class std::vector<double> & a4, const bool a5, std::ostream & a6, const int a7) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "checkApplyAdjointHessian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6, a7);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Constraint::checkApplyAdjointHessian(a0, a1, a2, a3, a4, a5, a6, a7);
	}
	class std::vector<class std::vector<double> > checkApplyAdjointHessian(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const bool a4, std::ostream & a5, const int a6, const int a7) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "checkApplyAdjointHessian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6, a7);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Constraint::checkApplyAdjointHessian(a0, a1, a2, a3, a4, a5, a6, a7);
	}
	void setParameter(const class std::vector<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ReducedLinearConstraint<double> *>(this), "setParameter");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Constraint::setParameter(a0);
	}
};

void bind_pyrol_61(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::ReducedLinearConstraint file:ROL_ReducedLinearConstraint.hpp line:33
		pybind11::class_<ROL::ReducedLinearConstraint<double>, Teuchos::RCP<ROL::ReducedLinearConstraint<double>>, PyCallBack_ROL_ReducedLinearConstraint_double_t, ROL::Constraint<double>> cl(M("ROL"), "ReducedLinearConstraint_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<const class Teuchos::RCP<class ROL::Constraint<double> > &, const class Teuchos::RCP<class ROL::BoundConstraint<double> > &, const class Teuchos::RCP<const class ROL::Vector<double> > &>(), pybind11::arg("con"), pybind11::arg("bnd"), pybind11::arg("x") );

		cl.def( pybind11::init( [](PyCallBack_ROL_ReducedLinearConstraint_double_t const &o){ return new PyCallBack_ROL_ReducedLinearConstraint_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::ReducedLinearConstraint<double> const &o){ return new ROL::ReducedLinearConstraint<double>(o); } ) );
		cl.def("setX", (void (ROL::ReducedLinearConstraint<double>::*)(const class Teuchos::RCP<const class ROL::Vector<double> > &)) &ROL::ReducedLinearConstraint<double>::setX, "C++: ROL::ReducedLinearConstraint<double>::setX(const class Teuchos::RCP<const class ROL::Vector<double> > &) --> void", pybind11::arg("x"));
		cl.def("value", (void (ROL::ReducedLinearConstraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::ReducedLinearConstraint<double>::value, "C++: ROL::ReducedLinearConstraint<double>::value(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("c"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("applyJacobian", (void (ROL::ReducedLinearConstraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::ReducedLinearConstraint<double>::applyJacobian, "C++: ROL::ReducedLinearConstraint<double>::applyJacobian(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("jv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("applyAdjointJacobian", (void (ROL::ReducedLinearConstraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::ReducedLinearConstraint<double>::applyAdjointJacobian, "C++: ROL::ReducedLinearConstraint<double>::applyAdjointJacobian(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("jv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("applyAdjointHessian", (void (ROL::ReducedLinearConstraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::ReducedLinearConstraint<double>::applyAdjointHessian, "C++: ROL::ReducedLinearConstraint<double>::applyAdjointHessian(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("ahuv"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("update", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, enum ROL::UpdateType const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("type"));
		cl.def("update", (void (ROL::Constraint<double>::*)(const class ROL::Vector<double> &, enum ROL::UpdateType, int)) &ROL::Constraint<double>::update, "Update constraint function. \n\n      This function updates the constraint function at new iterations. \n      \n\n      is the new iterate. \n      \n\n   is the type of update requested.\n      \n\n   is the outer algorithm iterations count.\n\nC++: ROL::Constraint<double>::update(const class ROL::Vector<double> &, enum ROL::UpdateType, int) --> void", pybind11::arg("x"), pybind11::arg("type"), pybind11::arg("iter"));
		cl.def("update", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0) -> void { return o.update(a0); }, "", pybind11::arg("x"));
		cl.def("update", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, bool const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("flag"));
		cl.def("update", (void (ROL::Constraint<double>::*)(const class ROL::Vector<double> &, bool, int)) &ROL::Constraint<double>::update, "Update constraint functions.  \n                x is the optimization variable, \n                flag = true if optimization variable is changed,\n                iter is the outer algorithm iterations count.\n\nC++: ROL::Constraint<double>::update(const class ROL::Vector<double> &, bool, int) --> void", pybind11::arg("x"), pybind11::arg("flag"), pybind11::arg("iter"));
		cl.def("value", (void (ROL::Constraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::Constraint<double>::value, "C++: ROL::Constraint<double>::value(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("c"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("applyJacobian", (void (ROL::Constraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::Constraint<double>::applyJacobian, "Apply the constraint Jacobian at \n, \n,\n             to vector \n\n.\n\n             \n  is the result of applying the constraint Jacobian to  at  a constraint-space vector\n             \n\n   is an optimization-space vector\n             \n\n   is the constraint argument; an optimization-space vector\n             \n\n is a tolerance for inexact evaluations; currently unused\n\n             On return, \n, where\n             \n\n, \n. \n             The default implementation is a finite-difference approximation.\n\n             ---\n\nC++: ROL::Constraint<double>::applyJacobian(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("jv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("applyAdjointJacobian", (void (ROL::Constraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::Constraint<double>::applyAdjointJacobian, "Apply the adjoint of the the constraint Jacobian at \n, \n,\n             to vector \n\n.\n\n             \n is the result of applying the adjoint of the constraint Jacobian to  at  a dual optimization-space vector\n             \n\n   is a dual constraint-space vector\n             \n\n   is the constraint argument; an optimization-space vector\n             \n\n is a tolerance for inexact evaluations; currently unused\n\n             On return, \n, where\n             \n\n, \n. \n             The default implementation is a finite-difference approximation.\n\n             ---\n\nC++: ROL::Constraint<double>::applyAdjointJacobian(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("ajv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("applyAdjointJacobian", (void (ROL::Constraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::Constraint<double>::applyAdjointJacobian, "Apply the adjoint of the the constraint Jacobian at \n, \n,\n             to vector \n\n.\n\n             \n is the result of applying the adjoint of the constraint Jacobian to  at  a dual optimization-space vector\n             \n\n   is a dual constraint-space vector\n             \n\n   is the constraint argument; an optimization-space vector\n             \n\n  is a vector used for temporary variables; a constraint-space vector\n             \n\n is a tolerance for inexact evaluations; currently unused\n\n             On return, \n, where\n             \n\n, \n. \n             The default implementation is a finite-difference approximation.\n\n             ---\n\nC++: ROL::Constraint<double>::applyAdjointJacobian(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("ajv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("dualv"), pybind11::arg("tol"));
		cl.def("applyAdjointHessian", (void (ROL::Constraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::Constraint<double>::applyAdjointHessian, "Apply the derivative of the adjoint of the constraint Jacobian at \n\n             to vector \n in direction \n,\n             according to \n\n.\n\n             \n is the result of applying the derivative of the adjoint of the constraint Jacobian at  to vector  in direction  a dual optimization-space vector\n             \n\n    is the direction vector; a dual constraint-space vector\n             \n\n    is an optimization-space vector\n             \n\n    is the constraint argument; an optimization-space vector\n             \n\n  is a tolerance for inexact evaluations; currently unused\n\n             On return, \n, where\n             \n\n, \n, and \n. \n             The default implementation is a finite-difference approximation based on the adjoint Jacobian.\n\n             ---\n\nC++: ROL::Constraint<double>::applyAdjointHessian(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("huv"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("solveAugmentedSystem", (class std::vector<double> (ROL::Constraint<double>::*)(class ROL::Vector<double> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::Constraint<double>::solveAugmentedSystem, "Approximately solves the  augmented system \n             \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n             where \n, \n,\n             \n\n, \n,\n             \n\n is an identity or Riesz\n             operator, and \n\n\n             is a zero operator.\n\n             \n  is the optimization-space component of the result\n             \n\n  is the dual constraint-space component of the result\n             \n\n  is the dual optimization-space component of the right-hand side\n             \n\n  is the constraint-space component of the right-hand side\n             \n\n   is the constraint argument; an optimization-space vector\n             \n\n is the nominal relative residual tolerance\n\n             On return, \n approximately\n             solves the augmented system, where the size of the residual is\n             governed by special stopping conditions. \n             The default implementation is the preconditioned generalized\n             minimal residual (GMRES) method, which enables the use of\n             nonsymmetric preconditioners.\n\n             ---\n\nC++: ROL::Constraint<double>::solveAugmentedSystem(class ROL::Vector<double> &, class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> class std::vector<double>", pybind11::arg("v1"), pybind11::arg("v2"), pybind11::arg("b1"), pybind11::arg("b2"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("applyPreconditioner", (void (ROL::Constraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::Constraint<double>::applyPreconditioner, "Apply a constraint preconditioner at \n, \n,\n             to vector \n\n.  Ideally, this preconditioner satisfies the following relationship:\n             \n\n\n\n             where R is the appropriate Riesz map in \n.  It is used by the #solveAugmentedSystem method.\n\n             \n  is the result of applying the constraint preconditioner to  at  a dual constraint-space vector\n             \n\n   is a constraint-space vector\n             \n\n   is the preconditioner argument; an optimization-space vector\n             \n\n   is the preconditioner argument; a dual optimization-space vector, unused\n             \n\n is a tolerance for inexact evaluations\n\n             On return, \n, where\n             \n\n, \n. \n             The default implementation is the Riesz map in \n\n.\n\n             ---\n\nC++: ROL::Constraint<double>::applyPreconditioner(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("pv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("tol"));
		cl.def("activate", (void (ROL::Constraint<double>::*)()) &ROL::Constraint<double>::activate, "Turn on constraints \n\nC++: ROL::Constraint<double>::activate() --> void");
		cl.def("deactivate", (void (ROL::Constraint<double>::*)()) &ROL::Constraint<double>::deactivate, "Turn off constraints\n\nC++: ROL::Constraint<double>::deactivate() --> void");
		cl.def("isActivated", (bool (ROL::Constraint<double>::*)()) &ROL::Constraint<double>::isActivated, "Check if constraints are on\n\nC++: ROL::Constraint<double>::isActivated() --> bool");
		cl.def("checkApplyJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class std::vector<double> & a3) -> std::vector<class std::vector<double> > { return o.checkApplyJacobian(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("jv"), pybind11::arg("steps"));
		cl.def("checkApplyJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class std::vector<double> & a3, const bool & a4) -> std::vector<class std::vector<double> > { return o.checkApplyJacobian(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("jv"), pybind11::arg("steps"), pybind11::arg("printToStream"));
		cl.def("checkApplyJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class std::vector<double> & a3, const bool & a4, std::ostream & a5) -> std::vector<class std::vector<double> > { return o.checkApplyJacobian(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("jv"), pybind11::arg("steps"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkApplyJacobian", (class std::vector<class std::vector<double> > (ROL::Constraint<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class std::vector<double> &, const bool, std::ostream &, const int)) &ROL::Constraint<double>::checkApplyJacobian, "Finite-difference check for the constraint Jacobian application.\n\n      Details here.\n\nC++: ROL::Constraint<double>::checkApplyJacobian(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class std::vector<double> &, const bool, std::ostream &, const int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("jv"), pybind11::arg("steps"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("order"));
		cl.def("checkApplyJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2) -> std::vector<class std::vector<double> > { return o.checkApplyJacobian(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("jv"));
		cl.def("checkApplyJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool & a3) -> std::vector<class std::vector<double> > { return o.checkApplyJacobian(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("jv"), pybind11::arg("printToStream"));
		cl.def("checkApplyJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool & a3, std::ostream & a4) -> std::vector<class std::vector<double> > { return o.checkApplyJacobian(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("jv"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkApplyJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool & a3, std::ostream & a4, const int & a5) -> std::vector<class std::vector<double> > { return o.checkApplyJacobian(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("jv"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"));
		cl.def("checkApplyJacobian", (class std::vector<class std::vector<double> > (ROL::Constraint<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int, const int)) &ROL::Constraint<double>::checkApplyJacobian, "Finite-difference check for the constraint Jacobian application.\n\n      Details here.\n\n  \n\nC++: ROL::Constraint<double>::checkApplyJacobian(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int, const int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("jv"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"), pybind11::arg("order"));
		cl.def("checkApplyAdjointJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3) -> std::vector<class std::vector<double> > { return o.checkApplyAdjointJacobian(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("c"), pybind11::arg("ajv"));
		cl.def("checkApplyAdjointJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const bool & a4) -> std::vector<class std::vector<double> > { return o.checkApplyAdjointJacobian(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("c"), pybind11::arg("ajv"), pybind11::arg("printToStream"));
		cl.def("checkApplyAdjointJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const bool & a4, std::ostream & a5) -> std::vector<class std::vector<double> > { return o.checkApplyAdjointJacobian(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("c"), pybind11::arg("ajv"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkApplyAdjointJacobian", (class std::vector<class std::vector<double> > (ROL::Constraint<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int)) &ROL::Constraint<double>::checkApplyAdjointJacobian, "Finite-difference check for the application of the adjoint of constraint Jacobian.\n\n      Details here. (This function should be deprecated)\n\n  \n\nC++: ROL::Constraint<double>::checkApplyAdjointJacobian(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("c"), pybind11::arg("ajv"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"));
		cl.def("checkAdjointConsistencyJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2) -> double { return o.checkAdjointConsistencyJacobian(a0, a1, a2); }, "", pybind11::arg("w"), pybind11::arg("v"), pybind11::arg("x"));
		cl.def("checkAdjointConsistencyJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool & a3) -> double { return o.checkAdjointConsistencyJacobian(a0, a1, a2, a3); }, "", pybind11::arg("w"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("printToStream"));
		cl.def("checkAdjointConsistencyJacobian", (double (ROL::Constraint<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &)) &ROL::Constraint<double>::checkAdjointConsistencyJacobian, "C++: ROL::Constraint<double>::checkAdjointConsistencyJacobian(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &) --> double", pybind11::arg("w"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkAdjointConsistencyJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4) -> double { return o.checkAdjointConsistencyJacobian(a0, a1, a2, a3, a4); }, "", pybind11::arg("w"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("dualw"), pybind11::arg("dualv"));
		cl.def("checkAdjointConsistencyJacobian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const bool & a5) -> double { return o.checkAdjointConsistencyJacobian(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("w"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("dualw"), pybind11::arg("dualv"), pybind11::arg("printToStream"));
		cl.def("checkAdjointConsistencyJacobian", (double (ROL::Constraint<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &)) &ROL::Constraint<double>::checkAdjointConsistencyJacobian, "C++: ROL::Constraint<double>::checkAdjointConsistencyJacobian(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &) --> double", pybind11::arg("w"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("dualw"), pybind11::arg("dualv"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkApplyAdjointHessian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class std::vector<double> & a4) -> std::vector<class std::vector<double> > { return o.checkApplyAdjointHessian(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("hv"), pybind11::arg("steps"));
		cl.def("checkApplyAdjointHessian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class std::vector<double> & a4, const bool & a5) -> std::vector<class std::vector<double> > { return o.checkApplyAdjointHessian(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("hv"), pybind11::arg("steps"), pybind11::arg("printToStream"));
		cl.def("checkApplyAdjointHessian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class std::vector<double> & a4, const bool & a5, std::ostream & a6) -> std::vector<class std::vector<double> > { return o.checkApplyAdjointHessian(a0, a1, a2, a3, a4, a5, a6); }, "", pybind11::arg("x"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("hv"), pybind11::arg("steps"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkApplyAdjointHessian", (class std::vector<class std::vector<double> > (ROL::Constraint<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class std::vector<double> &, const bool, std::ostream &, const int)) &ROL::Constraint<double>::checkApplyAdjointHessian, "Finite-difference check for the application of the adjoint of constraint Hessian.\n\n      Details here.\n\n  \n\nC++: ROL::Constraint<double>::checkApplyAdjointHessian(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class std::vector<double> &, const bool, std::ostream &, const int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("hv"), pybind11::arg("steps"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("order"));
		cl.def("checkApplyAdjointHessian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3) -> std::vector<class std::vector<double> > { return o.checkApplyAdjointHessian(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("hv"));
		cl.def("checkApplyAdjointHessian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const bool & a4) -> std::vector<class std::vector<double> > { return o.checkApplyAdjointHessian(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("hv"), pybind11::arg("printToStream"));
		cl.def("checkApplyAdjointHessian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const bool & a4, std::ostream & a5) -> std::vector<class std::vector<double> > { return o.checkApplyAdjointHessian(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("hv"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkApplyAdjointHessian", [](ROL::Constraint<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const bool & a4, std::ostream & a5, const int & a6) -> std::vector<class std::vector<double> > { return o.checkApplyAdjointHessian(a0, a1, a2, a3, a4, a5, a6); }, "", pybind11::arg("x"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("hv"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"));
		cl.def("checkApplyAdjointHessian", (class std::vector<class std::vector<double> > (ROL::Constraint<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int, const int)) &ROL::Constraint<double>::checkApplyAdjointHessian, "Finite-difference check for the application of the adjoint of constraint Hessian.\n\n      Details here.\n\n  \n\nC++: ROL::Constraint<double>::checkApplyAdjointHessian(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int, const int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("hv"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"), pybind11::arg("order"));
		cl.def("setParameter", (void (ROL::Constraint<double>::*)(const class std::vector<double> &)) &ROL::Constraint<double>::setParameter, "C++: ROL::Constraint<double>::setParameter(const class std::vector<double> &) --> void", pybind11::arg("param"));
		cl.def("assign", (class ROL::Constraint<double> & (ROL::Constraint<double>::*)(const class ROL::Constraint<double> &)) &ROL::Constraint<double>::operator=, "C++: ROL::Constraint<double>::operator=(const class ROL::Constraint<double> &) --> class ROL::Constraint<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
}
