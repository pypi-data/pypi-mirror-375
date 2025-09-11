#include <ROL_AugmentedLagrangianObjective.hpp>
#include <ROL_Constraint.hpp>
#include <ROL_ElasticLinearConstraint.hpp>
#include <ROL_ElasticObjective.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_Objective.hpp>
#include <ROL_UpdateType.hpp>
#include <ROL_Vector.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_FilteredIterator.hpp>
#include <Teuchos_ParameterEntry.hpp>
#include <Teuchos_ParameterList.hpp>
#include <Teuchos_ParameterListModifier.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <Teuchos_StringIndexedOrderedValueObjectContainer.hpp>
#include <deque>
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

// ROL::ElasticLinearConstraint file:ROL_ElasticLinearConstraint.hpp line:26
struct PyCallBack_ROL_ElasticLinearConstraint_double_t : public ROL::ElasticLinearConstraint<double> {
	using ROL::ElasticLinearConstraint<double>::ElasticLinearConstraint;

	void update(const class ROL::Vector<double> & a0, enum ROL::UpdateType a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ElasticLinearConstraint::update(a0, a1, a2);
	}
	void update(const class ROL::Vector<double> & a0, bool a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ElasticLinearConstraint::update(a0, a1, a2);
	}
	void value(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "value");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ElasticLinearConstraint::value(a0, a1, a2);
	}
	void applyJacobian(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "applyJacobian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ElasticLinearConstraint::applyJacobian(a0, a1, a2, a3);
	}
	void applyAdjointJacobian(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "applyAdjointJacobian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ElasticLinearConstraint::applyAdjointJacobian(a0, a1, a2, a3);
	}
	void applyAdjointJacobian(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, double & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "applyAdjointJacobian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ElasticLinearConstraint::applyAdjointJacobian(a0, a1, a2, a3, a4);
	}
	void applyAdjointHessian(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, double & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "applyAdjointHessian");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ElasticLinearConstraint::applyAdjointHessian(a0, a1, a2, a3, a4);
	}
	class std::vector<double> solveAugmentedSystem(class ROL::Vector<double> & a0, class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, double & a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "solveAugmentedSystem");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "applyPreconditioner");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "checkApplyJacobian");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "checkApplyJacobian");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "checkApplyAdjointJacobian");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "checkAdjointConsistencyJacobian");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "checkAdjointConsistencyJacobian");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "checkApplyAdjointHessian");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "checkApplyAdjointHessian");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticLinearConstraint<double> *>(this), "setParameter");
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

// ROL::ElasticObjective file:ROL_ElasticObjective.hpp line:49
struct PyCallBack_ROL_ElasticObjective_double_t : public ROL::ElasticObjective<double> {
	using ROL::ElasticObjective<double>::ElasticObjective;

	void update(const class ROL::Vector<double> & a0, enum ROL::UpdateType a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ElasticObjective::update(a0, a1, a2);
	}
	double value(const class ROL::Vector<double> & a0, double & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "value");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return ElasticObjective::value(a0, a1);
	}
	void gradient(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "gradient");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ElasticObjective::gradient(a0, a1, a2);
	}
	void hessVec(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "hessVec");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ElasticObjective::hessVec(a0, a1, a2, a3);
	}
	void update(const class ROL::Vector<double> & a0, bool a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Objective::update(a0, a1, a2);
	}
	double dirDeriv(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "dirDeriv");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return Objective::dirDeriv(a0, a1, a2);
	}
	void invHessVec(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "invHessVec");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Objective::invHessVec(a0, a1, a2, a3);
	}
	void precond(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "precond");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Objective::precond(a0, a1, a2, a3);
	}
	void prox(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "prox");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Objective::prox(a0, a1, a2, a3);
	}
	void proxJacVec(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double a3, double & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "proxJacVec");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Objective::proxJacVec(a0, a1, a2, a3, a4);
	}
	class std::vector<class std::vector<double> > checkGradient(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool a2, std::ostream & a3, const int a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "checkGradient");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Objective::checkGradient(a0, a1, a2, a3, a4, a5);
	}
	class std::vector<class std::vector<double> > checkGradient(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool a3, std::ostream & a4, const int a5, const int a6) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "checkGradient");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Objective::checkGradient(a0, a1, a2, a3, a4, a5, a6);
	}
	class std::vector<class std::vector<double> > checkGradient(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class std::vector<double> & a2, const bool a3, std::ostream & a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "checkGradient");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Objective::checkGradient(a0, a1, a2, a3, a4, a5);
	}
	class std::vector<class std::vector<double> > checkGradient(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class std::vector<double> & a3, const bool a4, std::ostream & a5, const int a6) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "checkGradient");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Objective::checkGradient(a0, a1, a2, a3, a4, a5, a6);
	}
	class std::vector<class std::vector<double> > checkHessVec(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool a2, std::ostream & a3, const int a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "checkHessVec");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Objective::checkHessVec(a0, a1, a2, a3, a4, a5);
	}
	class std::vector<class std::vector<double> > checkHessVec(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool a3, std::ostream & a4, const int a5, const int a6) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "checkHessVec");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Objective::checkHessVec(a0, a1, a2, a3, a4, a5, a6);
	}
	class std::vector<class std::vector<double> > checkHessVec(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class std::vector<double> & a2, const bool a3, std::ostream & a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "checkHessVec");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Objective::checkHessVec(a0, a1, a2, a3, a4, a5);
	}
	class std::vector<class std::vector<double> > checkHessVec(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class std::vector<double> & a3, const bool a4, std::ostream & a5, const int a6) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "checkHessVec");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Objective::checkHessVec(a0, a1, a2, a3, a4, a5, a6);
	}
	class std::vector<double> checkHessSym(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool a3, std::ostream & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "checkHessSym");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<double>>::value) {
				static pybind11::detail::override_caster_t<class std::vector<double>> caster;
				return pybind11::detail::cast_ref<class std::vector<double>>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<double>>(std::move(o));
		}
		return Objective::checkHessSym(a0, a1, a2, a3, a4);
	}
	class std::vector<double> checkHessSym(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const bool a4, std::ostream & a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "checkHessSym");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<double>>::value) {
				static pybind11::detail::override_caster_t<class std::vector<double>> caster;
				return pybind11::detail::cast_ref<class std::vector<double>>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<double>>(std::move(o));
		}
		return Objective::checkHessSym(a0, a1, a2, a3, a4, a5);
	}
	class std::vector<class std::vector<double> > checkProxJacVec(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double a2, bool a3, std::ostream & a4, int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "checkProxJacVec");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<class std::vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class std::vector<class std::vector<double> >> caster;
				return pybind11::detail::cast_ref<class std::vector<class std::vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<class std::vector<double> >>(std::move(o));
		}
		return Objective::checkProxJacVec(a0, a1, a2, a3, a4, a5);
	}
	void setParameter(const class std::vector<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::ElasticObjective<double> *>(this), "setParameter");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Objective::setParameter(a0);
	}
};

void bind_pyrol_71(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::ElasticLinearConstraint file:ROL_ElasticLinearConstraint.hpp line:26
		pybind11::class_<ROL::ElasticLinearConstraint<double>, Teuchos::RCP<ROL::ElasticLinearConstraint<double>>, PyCallBack_ROL_ElasticLinearConstraint_double_t, ROL::Constraint<double>> cl(M("ROL"), "ElasticLinearConstraint_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<const class Teuchos::RCP<const class ROL::Vector<double> > &, const class Teuchos::RCP<class ROL::Constraint<double> > &, const class Teuchos::RCP<const class ROL::Vector<double> > &>(), pybind11::arg("x"), pybind11::arg("con"), pybind11::arg("c") );

		cl.def( pybind11::init( [](PyCallBack_ROL_ElasticLinearConstraint_double_t const &o){ return new PyCallBack_ROL_ElasticLinearConstraint_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::ElasticLinearConstraint<double> const &o){ return new ROL::ElasticLinearConstraint<double>(o); } ) );
		cl.def("update", [](ROL::ElasticLinearConstraint<double> &o, const class ROL::Vector<double> & a0, enum ROL::UpdateType const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("type"));
		cl.def("update", (void (ROL::ElasticLinearConstraint<double>::*)(const class ROL::Vector<double> &, enum ROL::UpdateType, int)) &ROL::ElasticLinearConstraint<double>::update, "C++: ROL::ElasticLinearConstraint<double>::update(const class ROL::Vector<double> &, enum ROL::UpdateType, int) --> void", pybind11::arg("x"), pybind11::arg("type"), pybind11::arg("iter"));
		cl.def("update", [](ROL::ElasticLinearConstraint<double> &o, const class ROL::Vector<double> & a0) -> void { return o.update(a0); }, "", pybind11::arg("x"));
		cl.def("update", [](ROL::ElasticLinearConstraint<double> &o, const class ROL::Vector<double> & a0, bool const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("flag"));
		cl.def("update", (void (ROL::ElasticLinearConstraint<double>::*)(const class ROL::Vector<double> &, bool, int)) &ROL::ElasticLinearConstraint<double>::update, "C++: ROL::ElasticLinearConstraint<double>::update(const class ROL::Vector<double> &, bool, int) --> void", pybind11::arg("x"), pybind11::arg("flag"), pybind11::arg("iter"));
		cl.def("value", (void (ROL::ElasticLinearConstraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::ElasticLinearConstraint<double>::value, "C++: ROL::ElasticLinearConstraint<double>::value(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("c"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("applyJacobian", (void (ROL::ElasticLinearConstraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::ElasticLinearConstraint<double>::applyJacobian, "C++: ROL::ElasticLinearConstraint<double>::applyJacobian(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("jv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("applyAdjointJacobian", (void (ROL::ElasticLinearConstraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::ElasticLinearConstraint<double>::applyAdjointJacobian, "C++: ROL::ElasticLinearConstraint<double>::applyAdjointJacobian(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("ajv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("applyAdjointJacobian", (void (ROL::ElasticLinearConstraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::ElasticLinearConstraint<double>::applyAdjointJacobian, "C++: ROL::ElasticLinearConstraint<double>::applyAdjointJacobian(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("ajv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("dualv"), pybind11::arg("tol"));
		cl.def("applyAdjointHessian", (void (ROL::ElasticLinearConstraint<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::ElasticLinearConstraint<double>::applyAdjointHessian, "C++: ROL::ElasticLinearConstraint<double>::applyAdjointHessian(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("ahuv"), pybind11::arg("u"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("setAnchor", (void (ROL::ElasticLinearConstraint<double>::*)(const class Teuchos::RCP<const class ROL::Vector<double> > &)) &ROL::ElasticLinearConstraint<double>::setAnchor, "C++: ROL::ElasticLinearConstraint<double>::setAnchor(const class Teuchos::RCP<const class ROL::Vector<double> > &) --> void", pybind11::arg("x"));
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
	{ // ROL::ElasticObjective file:ROL_ElasticObjective.hpp line:49
		pybind11::class_<ROL::ElasticObjective<double>, Teuchos::RCP<ROL::ElasticObjective<double>>, PyCallBack_ROL_ElasticObjective_double_t, ROL::Objective<double>> cl(M("ROL"), "ElasticObjective_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<const class Teuchos::RCP<class ROL::Objective<double> > &, const class Teuchos::RCP<class ROL::Constraint<double> > &, const double, const double, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class Teuchos::ParameterList &>(), pybind11::arg("obj"), pybind11::arg("con"), pybind11::arg("penaltyParameter"), pybind11::arg("sigma"), pybind11::arg("dualOptVec"), pybind11::arg("primConVec"), pybind11::arg("dualConVec"), pybind11::arg("parlist") );

		cl.def( pybind11::init<const class Teuchos::RCP<class ROL::Objective<double> > &, const class Teuchos::RCP<class ROL::Constraint<double> > &, const double, const double, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, const int>(), pybind11::arg("obj"), pybind11::arg("con"), pybind11::arg("penaltyParameter"), pybind11::arg("sigma"), pybind11::arg("dualOptVec"), pybind11::arg("primConVec"), pybind11::arg("dualConVec"), pybind11::arg("scaleLagrangian"), pybind11::arg("HessianApprox") );

		cl.def( pybind11::init( [](PyCallBack_ROL_ElasticObjective_double_t const &o){ return new PyCallBack_ROL_ElasticObjective_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::ElasticObjective<double> const &o){ return new ROL::ElasticObjective<double>(o); } ) );
		cl.def("update", [](ROL::ElasticObjective<double> &o, const class ROL::Vector<double> & a0, enum ROL::UpdateType const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("type"));
		cl.def("update", (void (ROL::ElasticObjective<double>::*)(const class ROL::Vector<double> &, enum ROL::UpdateType, int)) &ROL::ElasticObjective<double>::update, "C++: ROL::ElasticObjective<double>::update(const class ROL::Vector<double> &, enum ROL::UpdateType, int) --> void", pybind11::arg("x"), pybind11::arg("type"), pybind11::arg("iter"));
		cl.def("value", (double (ROL::ElasticObjective<double>::*)(const class ROL::Vector<double> &, double &)) &ROL::ElasticObjective<double>::value, "C++: ROL::ElasticObjective<double>::value(const class ROL::Vector<double> &, double &) --> double", pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("gradient", (void (ROL::ElasticObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::ElasticObjective<double>::gradient, "C++: ROL::ElasticObjective<double>::gradient(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("g"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("hessVec", (void (ROL::ElasticObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::ElasticObjective<double>::hessVec, "C++: ROL::ElasticObjective<double>::hessVec(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("setScaling", [](ROL::ElasticObjective<double> &o) -> void { return o.setScaling(); }, "");
		cl.def("setScaling", [](ROL::ElasticObjective<double> &o, const double & a0) -> void { return o.setScaling(a0); }, "", pybind11::arg("fscale"));
		cl.def("setScaling", (void (ROL::ElasticObjective<double>::*)(const double, const double)) &ROL::ElasticObjective<double>::setScaling, "C++: ROL::ElasticObjective<double>::setScaling(const double, const double) --> void", pybind11::arg("fscale"), pybind11::arg("cscale"));
		cl.def("getObjectiveValue", (double (ROL::ElasticObjective<double>::*)(const class ROL::Vector<double> &, double &)) &ROL::ElasticObjective<double>::getObjectiveValue, "C++: ROL::ElasticObjective<double>::getObjectiveValue(const class ROL::Vector<double> &, double &) --> double", pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("getObjectiveGradient", (const class Teuchos::RCP<const class ROL::Vector<double> > (ROL::ElasticObjective<double>::*)(const class ROL::Vector<double> &, double &)) &ROL::ElasticObjective<double>::getObjectiveGradient, "C++: ROL::ElasticObjective<double>::getObjectiveGradient(const class ROL::Vector<double> &, double &) --> const class Teuchos::RCP<const class ROL::Vector<double> >", pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("getConstraintVec", (const class Teuchos::RCP<const class ROL::Vector<double> > (ROL::ElasticObjective<double>::*)(const class ROL::Vector<double> &, double &)) &ROL::ElasticObjective<double>::getConstraintVec, "C++: ROL::ElasticObjective<double>::getConstraintVec(const class ROL::Vector<double> &, double &) --> const class Teuchos::RCP<const class ROL::Vector<double> >", pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("getNumberConstraintEvaluations", (int (ROL::ElasticObjective<double>::*)() const) &ROL::ElasticObjective<double>::getNumberConstraintEvaluations, "C++: ROL::ElasticObjective<double>::getNumberConstraintEvaluations() const --> int");
		cl.def("getNumberFunctionEvaluations", (int (ROL::ElasticObjective<double>::*)() const) &ROL::ElasticObjective<double>::getNumberFunctionEvaluations, "C++: ROL::ElasticObjective<double>::getNumberFunctionEvaluations() const --> int");
		cl.def("getNumberGradientEvaluations", (int (ROL::ElasticObjective<double>::*)() const) &ROL::ElasticObjective<double>::getNumberGradientEvaluations, "C++: ROL::ElasticObjective<double>::getNumberGradientEvaluations() const --> int");
		cl.def("reset", (void (ROL::ElasticObjective<double>::*)(const class ROL::Vector<double> &, double, double)) &ROL::ElasticObjective<double>::reset, "C++: ROL::ElasticObjective<double>::reset(const class ROL::Vector<double> &, double, double) --> void", pybind11::arg("multiplier"), pybind11::arg("penaltyParameter"), pybind11::arg("sigma"));
		cl.def("getAugmentedLagrangian", (const class Teuchos::RCP<class ROL::AugmentedLagrangianObjective<double> > (ROL::ElasticObjective<double>::*)() const) &ROL::ElasticObjective<double>::getAugmentedLagrangian, "C++: ROL::ElasticObjective<double>::getAugmentedLagrangian() const --> const class Teuchos::RCP<class ROL::AugmentedLagrangianObjective<double> >");
		cl.def("assign", (class ROL::ElasticObjective<double> & (ROL::ElasticObjective<double>::*)(const class ROL::ElasticObjective<double> &)) &ROL::ElasticObjective<double>::operator=, "C++: ROL::ElasticObjective<double>::operator=(const class ROL::ElasticObjective<double> &) --> class ROL::ElasticObjective<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("update", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, enum ROL::UpdateType const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("type"));
		cl.def("update", (void (ROL::Objective<double>::*)(const class ROL::Vector<double> &, enum ROL::UpdateType, int)) &ROL::Objective<double>::update, "Update objective function. \n\n      This function updates the objective function at new iterations. \n      \n\n      is the new iterate. \n      \n\n   is the type of update requested.\n      \n\n   is the outer algorithm iterations count.\n\nC++: ROL::Objective<double>::update(const class ROL::Vector<double> &, enum ROL::UpdateType, int) --> void", pybind11::arg("x"), pybind11::arg("type"), pybind11::arg("iter"));
		cl.def("update", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0) -> void { return o.update(a0); }, "", pybind11::arg("x"));
		cl.def("update", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, bool const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("flag"));
		cl.def("update", (void (ROL::Objective<double>::*)(const class ROL::Vector<double> &, bool, int)) &ROL::Objective<double>::update, "Update objective function. \n\n      This function updates the objective function at new iterations. \n      \n\n      is the new iterate. \n      \n\n   is true if the iterate has changed.\n      \n\n   is the outer algorithm iterations count.\n\nC++: ROL::Objective<double>::update(const class ROL::Vector<double> &, bool, int) --> void", pybind11::arg("x"), pybind11::arg("flag"), pybind11::arg("iter"));
		cl.def("value", (double (ROL::Objective<double>::*)(const class ROL::Vector<double> &, double &)) &ROL::Objective<double>::value, "C++: ROL::Objective<double>::value(const class ROL::Vector<double> &, double &) --> double", pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("gradient", (void (ROL::Objective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::Objective<double>::gradient, "Compute gradient.\n\n      This function returns the objective function gradient.\n      \n\n   is the gradient.\n      \n\n   is the current iterate.\n      \n\n is a tolerance for inexact objective function computation.\n\n      The default implementation is a finite-difference approximation based on the function value.\n      This requires the definition of a basis \n\n for the optimization vectors x and\n      the definition of a basis \n\n for the dual optimization vectors (gradient vectors g).\n      The bases must be related through the Riesz map, i.e., \n\n,\n      and this must be reflected in the implementation of the ROL::Vector::dual() method.\n\nC++: ROL::Objective<double>::gradient(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("g"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("dirDeriv", (double (ROL::Objective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::Objective<double>::dirDeriv, "Compute directional derivative.\n\n      This function returns the directional derivative of the objective function in the \n direction.\n      \n\n   is the current iterate.\n      \n\n   is the direction.\n      \n\n is a tolerance for inexact objective function computation.\n\nC++: ROL::Objective<double>::dirDeriv(const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> double", pybind11::arg("x"), pybind11::arg("d"), pybind11::arg("tol"));
		cl.def("hessVec", (void (ROL::Objective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::Objective<double>::hessVec, "Apply Hessian approximation to vector.\n\n      This function applies the Hessian of the objective function to the vector \n.\n      \n\n  is the the action of the Hessian on \n.\n      \n\n   is the direction vector.\n      \n\n   is the current iterate.\n      \n\n is a tolerance for inexact objective function computation.\n\nC++: ROL::Objective<double>::hessVec(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("invHessVec", (void (ROL::Objective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::Objective<double>::invHessVec, "Apply inverse Hessian approximation to vector.\n\n      This function applies the inverse Hessian of the objective function to the vector \n.\n      \n\n  is the action of the inverse Hessian on \n.\n      \n\n   is the direction vector.\n      \n\n   is the current iterate.\n      \n\n is a tolerance for inexact objective function computation.\n\nC++: ROL::Objective<double>::invHessVec(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("precond", (void (ROL::Objective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::Objective<double>::precond, "Apply preconditioner to vector.\n\n      This function applies a preconditioner for the Hessian of the objective function to the vector \n.\n      \n\n  is the action of the Hessian preconditioner on \n.\n      \n\n   is the direction vector.\n      \n\n   is the current iterate.\n      \n\n is a tolerance for inexact objective function computation.\n\nC++: ROL::Objective<double>::precond(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("Pv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("prox", (void (ROL::Objective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double, double &)) &ROL::Objective<double>::prox, "Compute the proximity operator.\n\n      This function returns the proximity operator.\n      \n\n  is the proximity operator applied to \n (primal optimization vector).\n      \n\n   is the input to the proximity operator (primal optimization vector).\n      \n\n   is the proximity operator parameter (positive scalar).\n      \n\n is a tolerance for inexact objective function computation.\n\nC++: ROL::Objective<double>::prox(class ROL::Vector<double> &, const class ROL::Vector<double> &, double, double &) --> void", pybind11::arg("Pv"), pybind11::arg("v"), pybind11::arg("t"), pybind11::arg("tol"));
		cl.def("proxJacVec", (void (ROL::Objective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double, double &)) &ROL::Objective<double>::proxJacVec, "Apply the Jacobian of the proximity operator.\n\n      This function applies the Jacobian of the proximity operator.\n      \n\n  is the Jacobian of the proximity operator at \n applied to \n (primal optimization vector).\n      \n\n   is the direction vector (primal optimization vector).\n      \n\n   is the input to the proximity operator (primal optimization vector).\n      \n\n   is the proximity operator parameter (positive scalar).\n      \n\n is a tolerance for inexact objective function computation.\n\nC++: ROL::Objective<double>::proxJacVec(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double, double &) --> void", pybind11::arg("Jv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("t"), pybind11::arg("tol"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("d"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool & a2) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("d"), pybind11::arg("printToStream"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool & a2, std::ostream & a3) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("d"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool & a2, std::ostream & a3, const int & a4) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("d"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"));
		cl.def("checkGradient", (class std::vector<class std::vector<double> > (ROL::Objective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int, const int)) &ROL::Objective<double>::checkGradient, "Finite-difference gradient check.\n\n      This function computes a sequence of one-sided finite-difference checks for the gradient.  \n      At each step of the sequence, the finite difference step size is decreased.  The output \n      compares the error \n      \n\n\n\n      if the approximation is first order. More generally, difference approximation is\n      \n\n\n\n      where m = order+1, \n are the difference weights and \n are the difference steps\n      \n\n             is an optimization variable.\n      \n\n             is a direction vector.\n      \n\n is a flag that turns on/off output.\n      \n\n     is the output stream.\n      \n\n      is a parameter which dictates the number of finite difference steps.\n      \n\n         is the order of the finite difference approximation (1,2,3,4)\n\nC++: ROL::Objective<double>::checkGradient(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int, const int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("d"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"), pybind11::arg("order"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("d"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool & a3) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("d"), pybind11::arg("printToStream"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool & a3, std::ostream & a4) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("d"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool & a3, std::ostream & a4, const int & a5) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("d"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"));
		cl.def("checkGradient", (class std::vector<class std::vector<double> > (ROL::Objective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int, const int)) &ROL::Objective<double>::checkGradient, "Finite-difference gradient check.\n\n      This function computes a sequence of one-sided finite-difference checks for the gradient.  \n      At each step of the sequence, the finite difference step size is decreased.  The output \n      compares the error \n      \n\n\n\n      if the approximation is first order. More generally, difference approximation is\n      \n\n\n\n      where m = order+1, \n are the difference weights and \n are the difference steps\n\n      \n             is an optimization variable.\n      \n\n             is used to create a temporary gradient vector.\n      \n\n             is a direction vector.\n      \n\n is a flag that turns on/off output.\n      \n\n     is the output stream.\n      \n\n      is a parameter which dictates the number of finite difference steps.\n      \n\n         is the order of the finite difference approximation (1,2,3,4)\n\nC++: ROL::Objective<double>::checkGradient(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int, const int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("d"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"), pybind11::arg("order"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class std::vector<double> & a2) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("d"), pybind11::arg("steps"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class std::vector<double> & a2, const bool & a3) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("d"), pybind11::arg("steps"), pybind11::arg("printToStream"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class std::vector<double> & a2, const bool & a3, std::ostream & a4) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("d"), pybind11::arg("steps"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkGradient", (class std::vector<class std::vector<double> > (ROL::Objective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class std::vector<double> &, const bool, std::ostream &, const int)) &ROL::Objective<double>::checkGradient, "Finite-difference gradient check with specified step sizes.\n\n      This function computes a sequence of one-sided finite-difference checks for the gradient.  \n      At each step of the sequence, the finite difference step size is decreased.  The output \n      compares the error \n      \n\n\n\n      if the approximation is first order. More generally, difference approximation is\n      \n\n\n\n      where m = order+1, \n are the difference weights and \n are the difference steps\n      \n\n             is an optimization variable.\n      \n\n             is a direction vector.\n      \n\n         is vector of steps of user-specified size.\n      \n\n is a flag that turns on/off output.\n      \n\n     is the output stream.\n      \n\n         is the order of the finite difference approximation (1,2,3,4)\n\nC++: ROL::Objective<double>::checkGradient(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class std::vector<double> &, const bool, std::ostream &, const int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("d"), pybind11::arg("steps"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("order"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class std::vector<double> & a3) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("d"), pybind11::arg("steps"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class std::vector<double> & a3, const bool & a4) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("d"), pybind11::arg("steps"), pybind11::arg("printToStream"));
		cl.def("checkGradient", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class std::vector<double> & a3, const bool & a4, std::ostream & a5) -> std::vector<class std::vector<double> > { return o.checkGradient(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("d"), pybind11::arg("steps"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkGradient", (class std::vector<class std::vector<double> > (ROL::Objective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class std::vector<double> &, const bool, std::ostream &, const int)) &ROL::Objective<double>::checkGradient, "Finite-difference gradient check with specified step sizes.\n\n      This function computes a sequence of one-sided finite-difference checks for the gradient.  \n      At each step of the sequence, the finite difference step size is decreased.  The output \n      compares the error \n      \n\n\n\n      if the approximation is first order. More generally, difference approximation is\n      \n\n\n\n      where m = order+1, \n are the difference weights and \n are the difference steps\n\n      \n             is an optimization variable.\n      \n\n             is used to create a temporary gradient vector.\n      \n\n             is a direction vector.\n      \n\n         is vector of steps of user-specified size.\n      \n\n is a flag that turns on/off output.\n      \n\n     is the output stream.\n      \n\n         is the order of the finite difference approximation (1,2,3,4)\n\nC++: ROL::Objective<double>::checkGradient(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class std::vector<double> &, const bool, std::ostream &, const int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("d"), pybind11::arg("steps"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("order"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("v"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool & a2) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("printToStream"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool & a2, std::ostream & a3) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool & a2, std::ostream & a3, const int & a4) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"));
		cl.def("checkHessVec", (class std::vector<class std::vector<double> > (ROL::Objective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int, const int)) &ROL::Objective<double>::checkHessVec, "Finite-difference Hessian-applied-to-vector check.\n\n      This function computes a sequence of one-sided finite-difference checks for the Hessian.  \n      At each step of the sequence, the finite difference step size is decreased.  The output \n      compares the error \n      \n\n\n\n      if the approximation is first order. More generally, difference approximation is\n      \n\n\n\n      where m = order+1, \n are the difference weights and \n are the difference steps\n      \n\n             is an optimization variable.\n      \n\n             is a direction vector.\n      \n\n is a flag that turns on/off output.\n      \n\n     is the output stream.\n      \n\n      is a parameter which dictates the number of finite difference steps.\n      \n\n         is the order of the finite difference approximation (1,2,3,4)\n\nC++: ROL::Objective<double>::checkHessVec(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int, const int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"), pybind11::arg("order"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("hv"), pybind11::arg("v"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool & a3) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("printToStream"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool & a3, std::ostream & a4) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool & a3, std::ostream & a4, const int & a5) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"));
		cl.def("checkHessVec", (class std::vector<class std::vector<double> > (ROL::Objective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int, const int)) &ROL::Objective<double>::checkHessVec, "Finite-difference Hessian-applied-to-vector check.\n\n      This function computes a sequence of one-sided finite-difference checks for the Hessian.  \n      At each step of the sequence, the finite difference step size is decreased.  The output \n      compares the error \n      \n\n\n\n      if the approximation is first order. More generally, difference approximation is\n      \n\n\n\n      where m = order+1, \n are the difference weights and \n are the difference steps\n      \n\n             is an optimization variable.\n      \n\n            is used to create temporary gradient and Hessian-times-vector vectors.\n      \n\n             is a direction vector.\n      \n\n is a flag that turns on/off output.\n      \n\n     is the output stream.\n      \n\n      is a parameter which dictates the number of finite difference steps.\n      \n\n         is the order of the finite difference approximation (1,2,3,4)\n\nC++: ROL::Objective<double>::checkHessVec(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &, const int, const int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"), pybind11::arg("order"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class std::vector<double> & a2) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("steps"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class std::vector<double> & a2, const bool & a3) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("steps"), pybind11::arg("printToStream"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class std::vector<double> & a2, const bool & a3, std::ostream & a4) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("steps"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkHessVec", (class std::vector<class std::vector<double> > (ROL::Objective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class std::vector<double> &, const bool, std::ostream &, const int)) &ROL::Objective<double>::checkHessVec, "Finite-difference Hessian-applied-to-vector check with specified step sizes.\n\n      This function computes a sequence of one-sided finite-difference checks for the Hessian.  \n      At each step of the sequence, the finite difference step size is decreased.  The output \n      compares the error \n      \n\n\n\n      if the approximation is first order. More generally, difference approximation is\n      \n\n\n\n      where m = order+1, \n are the difference weights and \n are the difference steps\n      \n\n             is an optimization variable.\n      \n\n             is a direction vector.\n      \n\n         is vector of steps of user-specified size.\n      \n\n is a flag that turns on/off output.\n      \n\n     is the output stream.\n      \n\n         is the order of the finite difference approximation (1,2,3,4)\n\nC++: ROL::Objective<double>::checkHessVec(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class std::vector<double> &, const bool, std::ostream &, const int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("steps"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("order"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class std::vector<double> & a3) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("steps"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class std::vector<double> & a3, const bool & a4) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("steps"), pybind11::arg("printToStream"));
		cl.def("checkHessVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class std::vector<double> & a3, const bool & a4, std::ostream & a5) -> std::vector<class std::vector<double> > { return o.checkHessVec(a0, a1, a2, a3, a4, a5); }, "", pybind11::arg("x"), pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("steps"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkHessVec", (class std::vector<class std::vector<double> > (ROL::Objective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class std::vector<double> &, const bool, std::ostream &, const int)) &ROL::Objective<double>::checkHessVec, "Finite-difference Hessian-applied-to-vector check with specified step sizes.\n\n      This function computes a sequence of one-sided finite-difference checks for the Hessian.  \n      At each step of the sequence, the finite difference step size is decreased.  The output \n      compares the error \n      \n\n\n\n      if the approximation is first order. More generally, difference approximation is\n      \n\n\n\n      where m = order+1, \n are the difference weights and \n are the difference steps\n      \n\n             is an optimization variable.\n      \n\n            is used to create temporary gradient and Hessian-times-vector vectors.\n      \n\n             is a direction vector.\n      \n\n         is vector of steps of user-specified size.\n      \n\n is a flag that turns on/off output.\n      \n\n     is the output stream.\n      \n\n         is the order of the finite difference approximation (1,2,3,4)\n\nC++: ROL::Objective<double>::checkHessVec(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class std::vector<double> &, const bool, std::ostream &, const int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("steps"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("order"));
		cl.def("checkHessSym", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2) -> std::vector<double> { return o.checkHessSym(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("w"));
		cl.def("checkHessSym", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const bool & a3) -> std::vector<double> { return o.checkHessSym(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("w"), pybind11::arg("printToStream"));
		cl.def("checkHessSym", (class std::vector<double> (ROL::Objective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &)) &ROL::Objective<double>::checkHessSym, "Hessian symmetry check.\n\n      This function checks the symmetry of the Hessian by comparing \n      \n\n\n\n\n\n      \n             is an optimization variable.\n      \n\n             is a direction vector.\n      \n\n             is a direction vector.\n      \n\n is a flag that turns on/off output.\n      \n\n     is the output stream.\n\nC++: ROL::Objective<double>::checkHessSym(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &) --> class std::vector<double>", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("w"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkHessSym", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3) -> std::vector<double> { return o.checkHessSym(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("w"));
		cl.def("checkHessSym", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const bool & a4) -> std::vector<double> { return o.checkHessSym(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("w"), pybind11::arg("printToStream"));
		cl.def("checkHessSym", (class std::vector<double> (ROL::Objective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &)) &ROL::Objective<double>::checkHessSym, "Hessian symmetry check.\n\n      This function checks the symmetry of the Hessian by comparing \n      \n\n\n\n\n\n      \n             is an optimization variable.\n      \n\n            is used to create temporary Hessian-times-vector vectors.\n      \n\n             is a direction vector.\n      \n\n             is a direction vector.\n      \n\n is a flag that turns on/off output.\n      \n\n     is the output stream.\n\nC++: ROL::Objective<double>::checkHessSym(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &) --> class std::vector<double>", pybind11::arg("x"), pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("w"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkProxJacVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) -> std::vector<class std::vector<double> > { return o.checkProxJacVec(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("v"));
		cl.def("checkProxJacVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double const & a2) -> std::vector<class std::vector<double> > { return o.checkProxJacVec(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("t"));
		cl.def("checkProxJacVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double const & a2, bool const & a3) -> std::vector<class std::vector<double> > { return o.checkProxJacVec(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("t"), pybind11::arg("printToStream"));
		cl.def("checkProxJacVec", [](ROL::Objective<double> &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double const & a2, bool const & a3, std::ostream & a4) -> std::vector<class std::vector<double> > { return o.checkProxJacVec(a0, a1, a2, a3, a4); }, "", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("t"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("checkProxJacVec", (class std::vector<class std::vector<double> > (ROL::Objective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, double, bool, std::ostream &, int)) &ROL::Objective<double>::checkProxJacVec, "Finite-difference proximity operator Jacobian-applied-to-vector check.\n\n      This function computes a sequence of one-sided finite-difference checks for the proximity\n      operator Jacobian.  \n      At each step of the sequence, the finite difference step size is decreased.  The output \n      compares the error \n      \n\n\n\n      if the approximation is first order.  Note that in some cases the proximity operator\n      is semismooth, which motivates the evaluation of \n\n at \n.\n      \n\n             is an optimization vector.\n      \n\n             is a direction vector.\n      \n\n             is the proximity operator parameter.\n      \n\n is a flag that turns on/off output.\n      \n\n     is the output stream.\n      \n\n      is a parameter which dictates the number of finite difference steps.\n\nC++: ROL::Objective<double>::checkProxJacVec(const class ROL::Vector<double> &, const class ROL::Vector<double> &, double, bool, std::ostream &, int) --> class std::vector<class std::vector<double> >", pybind11::arg("x"), pybind11::arg("v"), pybind11::arg("t"), pybind11::arg("printToStream"), pybind11::arg("outStream"), pybind11::arg("numSteps"));
		cl.def("setParameter", (void (ROL::Objective<double>::*)(const class std::vector<double> &)) &ROL::Objective<double>::setParameter, "C++: ROL::Objective<double>::setParameter(const class std::vector<double> &) --> void", pybind11::arg("param"));
		cl.def("assign", (class ROL::Objective<double> & (ROL::Objective<double>::*)(const class ROL::Objective<double> &)) &ROL::Objective<double>::operator=, "C++: ROL::Objective<double>::operator=(const class ROL::Objective<double> &) --> class ROL::Objective<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
}
