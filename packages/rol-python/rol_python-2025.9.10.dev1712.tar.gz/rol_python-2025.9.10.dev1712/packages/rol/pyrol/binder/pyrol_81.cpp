#include <ROL_BatchManager.hpp>
#include <ROL_Distribution.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_MonteCarloGenerator.hpp>
#include <ROL_Objective.hpp>
#include <ROL_PrimalDualRisk.hpp>
#include <ROL_RiskNeutralObjective.hpp>
#include <ROL_SampleGenerator.hpp>
#include <ROL_SimulatedVector.hpp>
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
#include <Teuchos_any.hpp>
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

// ROL::PrimalSimulatedVector file:ROL_SimulatedVector.hpp line:267
struct PyCallBack_ROL_PrimalSimulatedVector_double_t : public ROL::PrimalSimulatedVector<double> {
	using ROL::PrimalSimulatedVector<double>::PrimalSimulatedVector;

	double dot(const class ROL::Vector<double> & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "dot");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return PrimalSimulatedVector::dot(a0);
	}
	class Teuchos::RCP<class ROL::Vector<double> > clone() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "clone");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<class Teuchos::RCP<class ROL::Vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class Teuchos::RCP<class ROL::Vector<double> >> caster;
				return pybind11::detail::cast_ref<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o));
		}
		return PrimalSimulatedVector::clone();
	}
	const class ROL::Vector<double> & dual() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "dual");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const class ROL::Vector<double> &>::value) {
				static pybind11::detail::override_caster_t<const class ROL::Vector<double> &> caster;
				return pybind11::detail::cast_ref<const class ROL::Vector<double> &>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const class ROL::Vector<double> &>(std::move(o));
		}
		return PrimalSimulatedVector::dual();
	}
	void set(const class ROL::Vector<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "set");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::set(a0);
	}
	void plus(const class ROL::Vector<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "plus");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::plus(a0);
	}
	void scale(const double a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "scale");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::scale(a0);
	}
	void axpy(const double a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "axpy");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::axpy(a0, a1);
	}
	double norm() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "norm");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return SimulatedVector::norm();
	}
	class Teuchos::RCP<class ROL::Vector<double> > basis(const int a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "basis");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<class Teuchos::RCP<class ROL::Vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class Teuchos::RCP<class ROL::Vector<double> >> caster;
				return pybind11::detail::cast_ref<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o));
		}
		return SimulatedVector::basis(a0);
	}
	int dimension() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "dimension");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return SimulatedVector::dimension();
	}
	void zero() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "zero");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::zero();
	}
	void applyUnary(const class ROL::Elementwise::UnaryFunction<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "applyUnary");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::applyUnary(a0);
	}
	void applyBinary(const class ROL::Elementwise::BinaryFunction<double> & a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "applyBinary");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::applyBinary(a0, a1);
	}
	double reduce(const class ROL::Elementwise::ReductionOp<double> & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "reduce");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return SimulatedVector::reduce(a0);
	}
	void setScalar(const double a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "setScalar");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::setScalar(a0);
	}
	void randomize(const double a0, const double a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "randomize");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::randomize(a0, a1);
	}
	double apply(const class ROL::Vector<double> & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "apply");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return Vector::apply(a0);
	}
	void print(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "print");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Vector::print(a0);
	}
	class std::vector<double> checkVector(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool a2, std::ostream & a3) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::PrimalSimulatedVector<double> *>(this), "checkVector");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<double>>::value) {
				static pybind11::detail::override_caster_t<class std::vector<double>> caster;
				return pybind11::detail::cast_ref<class std::vector<double>>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<double>>(std::move(o));
		}
		return Vector::checkVector(a0, a1, a2, a3);
	}
};

// ROL::DualSimulatedVector file:ROL_SimulatedVector.hpp line:334
struct PyCallBack_ROL_DualSimulatedVector_double_t : public ROL::DualSimulatedVector<double> {
	using ROL::DualSimulatedVector<double>::DualSimulatedVector;

	double dot(const class ROL::Vector<double> & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "dot");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return DualSimulatedVector::dot(a0);
	}
	class Teuchos::RCP<class ROL::Vector<double> > clone() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "clone");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<class Teuchos::RCP<class ROL::Vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class Teuchos::RCP<class ROL::Vector<double> >> caster;
				return pybind11::detail::cast_ref<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o));
		}
		return DualSimulatedVector::clone();
	}
	const class ROL::Vector<double> & dual() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "dual");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const class ROL::Vector<double> &>::value) {
				static pybind11::detail::override_caster_t<const class ROL::Vector<double> &> caster;
				return pybind11::detail::cast_ref<const class ROL::Vector<double> &>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const class ROL::Vector<double> &>(std::move(o));
		}
		return DualSimulatedVector::dual();
	}
	void set(const class ROL::Vector<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "set");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::set(a0);
	}
	void plus(const class ROL::Vector<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "plus");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::plus(a0);
	}
	void scale(const double a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "scale");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::scale(a0);
	}
	void axpy(const double a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "axpy");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::axpy(a0, a1);
	}
	double norm() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "norm");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return SimulatedVector::norm();
	}
	class Teuchos::RCP<class ROL::Vector<double> > basis(const int a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "basis");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<class Teuchos::RCP<class ROL::Vector<double> >>::value) {
				static pybind11::detail::override_caster_t<class Teuchos::RCP<class ROL::Vector<double> >> caster;
				return pybind11::detail::cast_ref<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class Teuchos::RCP<class ROL::Vector<double> >>(std::move(o));
		}
		return SimulatedVector::basis(a0);
	}
	int dimension() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "dimension");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return SimulatedVector::dimension();
	}
	void zero() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "zero");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::zero();
	}
	void applyUnary(const class ROL::Elementwise::UnaryFunction<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "applyUnary");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::applyUnary(a0);
	}
	void applyBinary(const class ROL::Elementwise::BinaryFunction<double> & a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "applyBinary");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::applyBinary(a0, a1);
	}
	double reduce(const class ROL::Elementwise::ReductionOp<double> & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "reduce");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return SimulatedVector::reduce(a0);
	}
	void setScalar(const double a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "setScalar");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::setScalar(a0);
	}
	void randomize(const double a0, const double a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "randomize");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SimulatedVector::randomize(a0, a1);
	}
	double apply(const class ROL::Vector<double> & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "apply");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return Vector::apply(a0);
	}
	void print(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "print");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Vector::print(a0);
	}
	class std::vector<double> checkVector(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool a2, std::ostream & a3) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DualSimulatedVector<double> *>(this), "checkVector");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<double>>::value) {
				static pybind11::detail::override_caster_t<class std::vector<double>> caster;
				return pybind11::detail::cast_ref<class std::vector<double>>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<double>>(std::move(o));
		}
		return Vector::checkVector(a0, a1, a2, a3);
	}
};

// ROL::MonteCarloGenerator file: line:69
struct PyCallBack_ROL_MonteCarloGenerator_double_t : public ROL::MonteCarloGenerator<double> {
	using ROL::MonteCarloGenerator<double>::MonteCarloGenerator;

	void update(const class ROL::Vector<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::MonteCarloGenerator<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return MonteCarloGenerator::update(a0);
	}
	double computeError(class std::vector<double> & a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::MonteCarloGenerator<double> *>(this), "computeError");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return MonteCarloGenerator::computeError(a0);
	}
	void refine() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::MonteCarloGenerator<double> *>(this), "refine");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return MonteCarloGenerator::refine();
	}
	int numGlobalSamples() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::MonteCarloGenerator<double> *>(this), "numGlobalSamples");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return MonteCarloGenerator::numGlobalSamples();
	}
	int start() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::MonteCarloGenerator<double> *>(this), "start");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return SampleGenerator::start();
	}
	void setSamples(bool a0) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::MonteCarloGenerator<double> *>(this), "setSamples");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SampleGenerator::setSamples(a0);
	}
	int numMySamples() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::MonteCarloGenerator<double> *>(this), "numMySamples");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return SampleGenerator::numMySamples();
	}
	class std::vector<double> getMyPoint(const int a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::MonteCarloGenerator<double> *>(this), "getMyPoint");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<class std::vector<double>>::value) {
				static pybind11::detail::override_caster_t<class std::vector<double>> caster;
				return pybind11::detail::cast_ref<class std::vector<double>>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<class std::vector<double>>(std::move(o));
		}
		return SampleGenerator::getMyPoint(a0);
	}
	double getMyWeight(const int a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::MonteCarloGenerator<double> *>(this), "getMyWeight");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return SampleGenerator::getMyWeight(a0);
	}
};

// ROL::RiskNeutralObjective file: line:71
struct PyCallBack_ROL_RiskNeutralObjective_double_t : public ROL::RiskNeutralObjective<double> {
	using ROL::RiskNeutralObjective<double>::RiskNeutralObjective;

	void update(const class ROL::Vector<double> & a0, enum ROL::UpdateType a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return RiskNeutralObjective::update(a0, a1, a2);
	}
	void update(const class ROL::Vector<double> & a0, bool a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return RiskNeutralObjective::update(a0, a1, a2);
	}
	double value(const class ROL::Vector<double> & a0, double & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "value");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return RiskNeutralObjective::value(a0, a1);
	}
	void gradient(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "gradient");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return RiskNeutralObjective::gradient(a0, a1, a2);
	}
	void hessVec(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "hessVec");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return RiskNeutralObjective::hessVec(a0, a1, a2, a3);
	}
	void precond(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "precond");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return RiskNeutralObjective::precond(a0, a1, a2, a3);
	}
	double dirDeriv(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "dirDeriv");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "invHessVec");
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
	void prox(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "prox");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "proxJacVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "checkHessSym");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "checkHessSym");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "checkProxJacVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::RiskNeutralObjective<double> *>(this), "setParameter");
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

void bind_pyrol_81(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::PrimalSimulatedVector file:ROL_SimulatedVector.hpp line:267
		pybind11::class_<ROL::PrimalSimulatedVector<double>, Teuchos::RCP<ROL::PrimalSimulatedVector<double>>, PyCallBack_ROL_PrimalSimulatedVector_double_t, ROL::SimulatedVector<double>> cl(M("ROL"), "PrimalSimulatedVector_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](PyCallBack_ROL_PrimalSimulatedVector_double_t const &o){ return new PyCallBack_ROL_PrimalSimulatedVector_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::PrimalSimulatedVector<double> const &o){ return new ROL::PrimalSimulatedVector<double>(o); } ) );
		cl.def("dot", (double (ROL::PrimalSimulatedVector<double>::*)(const class ROL::Vector<double> &) const) &ROL::PrimalSimulatedVector<double>::dot, "C++: ROL::PrimalSimulatedVector<double>::dot(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::PrimalSimulatedVector<double>::*)() const) &ROL::PrimalSimulatedVector<double>::clone, "C++: ROL::PrimalSimulatedVector<double>::clone() const --> class Teuchos::RCP<class ROL::Vector<double> >");
		cl.def("dual", (const class ROL::Vector<double> & (ROL::PrimalSimulatedVector<double>::*)() const) &ROL::PrimalSimulatedVector<double>::dual, "C++: ROL::PrimalSimulatedVector<double>::dual() const --> const class ROL::Vector<double> &", pybind11::return_value_policy::automatic);
		cl.def("set", (void (ROL::SimulatedVector<double>::*)(const class ROL::Vector<double> &)) &ROL::SimulatedVector<double>::set, "C++: ROL::SimulatedVector<double>::set(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("plus", (void (ROL::SimulatedVector<double>::*)(const class ROL::Vector<double> &)) &ROL::SimulatedVector<double>::plus, "C++: ROL::SimulatedVector<double>::plus(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("scale", (void (ROL::SimulatedVector<double>::*)(const double)) &ROL::SimulatedVector<double>::scale, "C++: ROL::SimulatedVector<double>::scale(const double) --> void", pybind11::arg("alpha"));
		cl.def("axpy", (void (ROL::SimulatedVector<double>::*)(const double, const class ROL::Vector<double> &)) &ROL::SimulatedVector<double>::axpy, "C++: ROL::SimulatedVector<double>::axpy(const double, const class ROL::Vector<double> &) --> void", pybind11::arg("alpha"), pybind11::arg("x"));
		cl.def("dot", (double (ROL::SimulatedVector<double>::*)(const class ROL::Vector<double> &) const) &ROL::SimulatedVector<double>::dot, "C++: ROL::SimulatedVector<double>::dot(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("norm", (double (ROL::SimulatedVector<double>::*)() const) &ROL::SimulatedVector<double>::norm, "C++: ROL::SimulatedVector<double>::norm() const --> double");
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::SimulatedVector<double>::*)() const) &ROL::SimulatedVector<double>::clone, "C++: ROL::SimulatedVector<double>::clone() const --> class Teuchos::RCP<class ROL::Vector<double> >");
		cl.def("dual", (const class ROL::Vector<double> & (ROL::SimulatedVector<double>::*)() const) &ROL::SimulatedVector<double>::dual, "C++: ROL::SimulatedVector<double>::dual() const --> const class ROL::Vector<double> &", pybind11::return_value_policy::automatic);
		cl.def("basis", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::SimulatedVector<double>::*)(const int) const) &ROL::SimulatedVector<double>::basis, "C++: ROL::SimulatedVector<double>::basis(const int) const --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("i"));
		cl.def("dimension", (int (ROL::SimulatedVector<double>::*)() const) &ROL::SimulatedVector<double>::dimension, "C++: ROL::SimulatedVector<double>::dimension() const --> int");
		cl.def("zero", (void (ROL::SimulatedVector<double>::*)()) &ROL::SimulatedVector<double>::zero, "C++: ROL::SimulatedVector<double>::zero() --> void");
		cl.def("applyUnary", (void (ROL::SimulatedVector<double>::*)(const class ROL::Elementwise::UnaryFunction<double> &)) &ROL::SimulatedVector<double>::applyUnary, "C++: ROL::SimulatedVector<double>::applyUnary(const class ROL::Elementwise::UnaryFunction<double> &) --> void", pybind11::arg("f"));
		cl.def("applyBinary", (void (ROL::SimulatedVector<double>::*)(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &)) &ROL::SimulatedVector<double>::applyBinary, "C++: ROL::SimulatedVector<double>::applyBinary(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("f"), pybind11::arg("x"));
		cl.def("reduce", (double (ROL::SimulatedVector<double>::*)(const class ROL::Elementwise::ReductionOp<double> &) const) &ROL::SimulatedVector<double>::reduce, "C++: ROL::SimulatedVector<double>::reduce(const class ROL::Elementwise::ReductionOp<double> &) const --> double", pybind11::arg("r"));
		cl.def("setScalar", (void (ROL::SimulatedVector<double>::*)(const double)) &ROL::SimulatedVector<double>::setScalar, "C++: ROL::SimulatedVector<double>::setScalar(const double) --> void", pybind11::arg("C"));
		cl.def("randomize", [](ROL::SimulatedVector<double> &o) -> void { return o.randomize(); }, "");
		cl.def("randomize", [](ROL::SimulatedVector<double> &o, const double & a0) -> void { return o.randomize(a0); }, "", pybind11::arg("l"));
		cl.def("randomize", (void (ROL::SimulatedVector<double>::*)(const double, const double)) &ROL::SimulatedVector<double>::randomize, "C++: ROL::SimulatedVector<double>::randomize(const double, const double) --> void", pybind11::arg("l"), pybind11::arg("u"));
		cl.def("get", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::SimulatedVector<double>::*)(unsigned long)) &ROL::SimulatedVector<double>::get, "C++: ROL::SimulatedVector<double>::get(unsigned long) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("i"));
		cl.def("set", (void (ROL::SimulatedVector<double>::*)(unsigned long, const class ROL::Vector<double> &)) &ROL::SimulatedVector<double>::set, "C++: ROL::SimulatedVector<double>::set(unsigned long, const class ROL::Vector<double> &) --> void", pybind11::arg("i"), pybind11::arg("x"));
		cl.def("zero", (void (ROL::SimulatedVector<double>::*)(unsigned long)) &ROL::SimulatedVector<double>::zero, "C++: ROL::SimulatedVector<double>::zero(unsigned long) --> void", pybind11::arg("i"));
		cl.def("numVectors", (unsigned long (ROL::SimulatedVector<double>::*)() const) &ROL::SimulatedVector<double>::numVectors, "C++: ROL::SimulatedVector<double>::numVectors() const --> unsigned long");
		cl.def("plus", (void (ROL::Vector<double>::*)(const class ROL::Vector<double> &)) &ROL::Vector<double>::plus, "C++: ROL::Vector<double>::plus(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("scale", (void (ROL::Vector<double>::*)(const double)) &ROL::Vector<double>::scale, "C++: ROL::Vector<double>::scale(const double) --> void", pybind11::arg("alpha"));
		cl.def("dot", (double (ROL::Vector<double>::*)(const class ROL::Vector<double> &) const) &ROL::Vector<double>::dot, "C++: ROL::Vector<double>::dot(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("norm", (double (ROL::Vector<double>::*)() const) &ROL::Vector<double>::norm, "C++: ROL::Vector<double>::norm() const --> double");
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::Vector<double>::*)() const) &ROL::Vector<double>::clone, "C++: ROL::Vector<double>::clone() const --> class Teuchos::RCP<class ROL::Vector<double> >");
		cl.def("axpy", (void (ROL::Vector<double>::*)(const double, const class ROL::Vector<double> &)) &ROL::Vector<double>::axpy, "Compute \n where \n.\n\n             \n is the scaling of \n             \n\n     is a vector.\n\n             On return \n.\n             Uses #clone, #set, #scale and #plus for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::axpy(const double, const class ROL::Vector<double> &) --> void", pybind11::arg("alpha"), pybind11::arg("x"));
		cl.def("zero", (void (ROL::Vector<double>::*)()) &ROL::Vector<double>::zero, "Set to zero vector.\n\n             Uses #scale by zero for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::zero() --> void");
		cl.def("basis", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::Vector<double>::*)(const int) const) &ROL::Vector<double>::basis, "Return i-th basis vector.\n\n             \n is the index of the basis function.\n             \n\n A reference-counted pointer to the basis vector with index \n\n             Overloading the basis is only required if the default gradient implementation\n             is used, which computes a finite-difference approximation.\n\n             ---\n\nC++: ROL::Vector<double>::basis(const int) const --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("i"));
		cl.def("dimension", (int (ROL::Vector<double>::*)() const) &ROL::Vector<double>::dimension, "Return dimension of the vector space.\n\n             \n The dimension of the vector space, i.e., the total number of basis vectors.\n\n             Overload if the basis is overloaded.\n\n             ---\n\nC++: ROL::Vector<double>::dimension() const --> int");
		cl.def("set", (void (ROL::Vector<double>::*)(const class ROL::Vector<double> &)) &ROL::Vector<double>::set, "Set \n where \n.\n\n             \n     is a vector.\n\n             On return \n.\n             Uses #zero and #plus methods for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::set(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("dual", (const class ROL::Vector<double> & (ROL::Vector<double>::*)() const) &ROL::Vector<double>::dual, "Return dual representation of \n, for example,\n             the result of applying a Riesz map, or change of basis, or\n             change of memory layout.\n\n             \n         A const reference to dual representation.\n\n             By default, returns the current object.\n             Please overload if you need a dual representation.\n\n             ---\n\nC++: ROL::Vector<double>::dual() const --> const class ROL::Vector<double> &", pybind11::return_value_policy::automatic);
		cl.def("apply", (double (ROL::Vector<double>::*)(const class ROL::Vector<double> &) const) &ROL::Vector<double>::apply, "Apply \n to a dual vector.  This is equivalent\n             to the call \n\n.\n\n             \n      is a vector\n             \n\n         The number equal to \n.\n\n             ---\n\nC++: ROL::Vector<double>::apply(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("applyUnary", (void (ROL::Vector<double>::*)(const class ROL::Elementwise::UnaryFunction<double> &)) &ROL::Vector<double>::applyUnary, "C++: ROL::Vector<double>::applyUnary(const class ROL::Elementwise::UnaryFunction<double> &) --> void", pybind11::arg("f"));
		cl.def("applyBinary", (void (ROL::Vector<double>::*)(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &)) &ROL::Vector<double>::applyBinary, "C++: ROL::Vector<double>::applyBinary(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("f"), pybind11::arg("x"));
		cl.def("reduce", (double (ROL::Vector<double>::*)(const class ROL::Elementwise::ReductionOp<double> &) const) &ROL::Vector<double>::reduce, "C++: ROL::Vector<double>::reduce(const class ROL::Elementwise::ReductionOp<double> &) const --> double", pybind11::arg("r"));
		cl.def("print", (void (ROL::Vector<double>::*)(std::ostream &) const) &ROL::Vector<double>::print, "C++: ROL::Vector<double>::print(std::ostream &) const --> void", pybind11::arg("outStream"));
		cl.def("setScalar", (void (ROL::Vector<double>::*)(const double)) &ROL::Vector<double>::setScalar, "Set \n where \n.\n\n             \n     is a scalar.\n\n             On return \n.\n             Uses #applyUnary methods for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::setScalar(const double) --> void", pybind11::arg("C"));
		cl.def("randomize", [](ROL::Vector<double> &o) -> void { return o.randomize(); }, "");
		cl.def("randomize", [](ROL::Vector<double> &o, const double & a0) -> void { return o.randomize(a0); }, "", pybind11::arg("l"));
		cl.def("randomize", (void (ROL::Vector<double>::*)(const double, const double)) &ROL::Vector<double>::randomize, "Set vector to be uniform random between [l,u].\n\n             \n     is a the lower bound.\n             \n\n     is a the upper bound.\n\n             On return the components of \n are uniform\n             random numbers on the interval \n\n.\n       	     The default implementation uses #applyUnary methods for the\n       	     computation. Please overload if a more efficient implementation is\n             needed.\n\n             ---\n\nC++: ROL::Vector<double>::randomize(const double, const double) --> void", pybind11::arg("l"), pybind11::arg("u"));
		cl.def("checkVector", [](ROL::Vector<double> const &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) -> std::vector<double> { return o.checkVector(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("y"));
		cl.def("checkVector", [](ROL::Vector<double> const &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool & a2) -> std::vector<double> { return o.checkVector(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("y"), pybind11::arg("printToStream"));
		cl.def("checkVector", (class std::vector<double> (ROL::Vector<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &) const) &ROL::Vector<double>::checkVector, "Verify vector-space methods.\n\n             \n     is a vector.\n             \n\n     is a vector.\n\n             Returns a vector of Reals, all of which should be close to zero.\n             They represent consistency errors in the vector space properties,\n             as follows:\n\n             - Commutativity of addition: \n.\n             - Associativity of addition: \n\n.\n             - Identity element of addition: \n\n.\n             - Inverse elements of addition: \n\n.\n             - Identity element of scalar multiplication: \n\n.\n             - Consistency of scalar multiplication with field multiplication: \n\n.\n             - Distributivity of scalar multiplication with respect to field addition: \n\n.\n             - Distributivity of scalar multiplication with respect to vector addition: \n\n.\n             - Commutativity of dot (inner) product over the field of reals: \n\n.\n             - Additivity of dot (inner) product: \n\n.\n             - Consistency of scalar multiplication and norm: \n\n.\n             - Reflexivity: \n\n .\n             - Consistency of apply and dual: \n\n.\n\n             The consistency errors are defined as the norms or absolute values of the differences between the left-hand\n             side and the right-hand side terms in the above equalities.\n\n             ---\n\nC++: ROL::Vector<double>::checkVector(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &) const --> class std::vector<double>", pybind11::arg("x"), pybind11::arg("y"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("assign", (class ROL::Vector<double> & (ROL::Vector<double>::*)(const class ROL::Vector<double> &)) &ROL::Vector<double>::operator=, "C++: ROL::Vector<double>::operator=(const class ROL::Vector<double> &) --> class ROL::Vector<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::DualSimulatedVector file:ROL_SimulatedVector.hpp line:334
		pybind11::class_<ROL::DualSimulatedVector<double>, Teuchos::RCP<ROL::DualSimulatedVector<double>>, PyCallBack_ROL_DualSimulatedVector_double_t, ROL::SimulatedVector<double>> cl(M("ROL"), "DualSimulatedVector_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](PyCallBack_ROL_DualSimulatedVector_double_t const &o){ return new PyCallBack_ROL_DualSimulatedVector_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::DualSimulatedVector<double> const &o){ return new ROL::DualSimulatedVector<double>(o); } ) );
		cl.def("dot", (double (ROL::DualSimulatedVector<double>::*)(const class ROL::Vector<double> &) const) &ROL::DualSimulatedVector<double>::dot, "C++: ROL::DualSimulatedVector<double>::dot(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::DualSimulatedVector<double>::*)() const) &ROL::DualSimulatedVector<double>::clone, "C++: ROL::DualSimulatedVector<double>::clone() const --> class Teuchos::RCP<class ROL::Vector<double> >");
		cl.def("dual", (const class ROL::Vector<double> & (ROL::DualSimulatedVector<double>::*)() const) &ROL::DualSimulatedVector<double>::dual, "C++: ROL::DualSimulatedVector<double>::dual() const --> const class ROL::Vector<double> &", pybind11::return_value_policy::automatic);
		cl.def("set", (void (ROL::SimulatedVector<double>::*)(const class ROL::Vector<double> &)) &ROL::SimulatedVector<double>::set, "C++: ROL::SimulatedVector<double>::set(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("plus", (void (ROL::SimulatedVector<double>::*)(const class ROL::Vector<double> &)) &ROL::SimulatedVector<double>::plus, "C++: ROL::SimulatedVector<double>::plus(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("scale", (void (ROL::SimulatedVector<double>::*)(const double)) &ROL::SimulatedVector<double>::scale, "C++: ROL::SimulatedVector<double>::scale(const double) --> void", pybind11::arg("alpha"));
		cl.def("axpy", (void (ROL::SimulatedVector<double>::*)(const double, const class ROL::Vector<double> &)) &ROL::SimulatedVector<double>::axpy, "C++: ROL::SimulatedVector<double>::axpy(const double, const class ROL::Vector<double> &) --> void", pybind11::arg("alpha"), pybind11::arg("x"));
		cl.def("dot", (double (ROL::SimulatedVector<double>::*)(const class ROL::Vector<double> &) const) &ROL::SimulatedVector<double>::dot, "C++: ROL::SimulatedVector<double>::dot(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("norm", (double (ROL::SimulatedVector<double>::*)() const) &ROL::SimulatedVector<double>::norm, "C++: ROL::SimulatedVector<double>::norm() const --> double");
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::SimulatedVector<double>::*)() const) &ROL::SimulatedVector<double>::clone, "C++: ROL::SimulatedVector<double>::clone() const --> class Teuchos::RCP<class ROL::Vector<double> >");
		cl.def("dual", (const class ROL::Vector<double> & (ROL::SimulatedVector<double>::*)() const) &ROL::SimulatedVector<double>::dual, "C++: ROL::SimulatedVector<double>::dual() const --> const class ROL::Vector<double> &", pybind11::return_value_policy::automatic);
		cl.def("basis", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::SimulatedVector<double>::*)(const int) const) &ROL::SimulatedVector<double>::basis, "C++: ROL::SimulatedVector<double>::basis(const int) const --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("i"));
		cl.def("dimension", (int (ROL::SimulatedVector<double>::*)() const) &ROL::SimulatedVector<double>::dimension, "C++: ROL::SimulatedVector<double>::dimension() const --> int");
		cl.def("zero", (void (ROL::SimulatedVector<double>::*)()) &ROL::SimulatedVector<double>::zero, "C++: ROL::SimulatedVector<double>::zero() --> void");
		cl.def("applyUnary", (void (ROL::SimulatedVector<double>::*)(const class ROL::Elementwise::UnaryFunction<double> &)) &ROL::SimulatedVector<double>::applyUnary, "C++: ROL::SimulatedVector<double>::applyUnary(const class ROL::Elementwise::UnaryFunction<double> &) --> void", pybind11::arg("f"));
		cl.def("applyBinary", (void (ROL::SimulatedVector<double>::*)(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &)) &ROL::SimulatedVector<double>::applyBinary, "C++: ROL::SimulatedVector<double>::applyBinary(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("f"), pybind11::arg("x"));
		cl.def("reduce", (double (ROL::SimulatedVector<double>::*)(const class ROL::Elementwise::ReductionOp<double> &) const) &ROL::SimulatedVector<double>::reduce, "C++: ROL::SimulatedVector<double>::reduce(const class ROL::Elementwise::ReductionOp<double> &) const --> double", pybind11::arg("r"));
		cl.def("setScalar", (void (ROL::SimulatedVector<double>::*)(const double)) &ROL::SimulatedVector<double>::setScalar, "C++: ROL::SimulatedVector<double>::setScalar(const double) --> void", pybind11::arg("C"));
		cl.def("randomize", [](ROL::SimulatedVector<double> &o) -> void { return o.randomize(); }, "");
		cl.def("randomize", [](ROL::SimulatedVector<double> &o, const double & a0) -> void { return o.randomize(a0); }, "", pybind11::arg("l"));
		cl.def("randomize", (void (ROL::SimulatedVector<double>::*)(const double, const double)) &ROL::SimulatedVector<double>::randomize, "C++: ROL::SimulatedVector<double>::randomize(const double, const double) --> void", pybind11::arg("l"), pybind11::arg("u"));
		cl.def("get", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::SimulatedVector<double>::*)(unsigned long)) &ROL::SimulatedVector<double>::get, "C++: ROL::SimulatedVector<double>::get(unsigned long) --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("i"));
		cl.def("set", (void (ROL::SimulatedVector<double>::*)(unsigned long, const class ROL::Vector<double> &)) &ROL::SimulatedVector<double>::set, "C++: ROL::SimulatedVector<double>::set(unsigned long, const class ROL::Vector<double> &) --> void", pybind11::arg("i"), pybind11::arg("x"));
		cl.def("zero", (void (ROL::SimulatedVector<double>::*)(unsigned long)) &ROL::SimulatedVector<double>::zero, "C++: ROL::SimulatedVector<double>::zero(unsigned long) --> void", pybind11::arg("i"));
		cl.def("numVectors", (unsigned long (ROL::SimulatedVector<double>::*)() const) &ROL::SimulatedVector<double>::numVectors, "C++: ROL::SimulatedVector<double>::numVectors() const --> unsigned long");
		cl.def("plus", (void (ROL::Vector<double>::*)(const class ROL::Vector<double> &)) &ROL::Vector<double>::plus, "C++: ROL::Vector<double>::plus(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("scale", (void (ROL::Vector<double>::*)(const double)) &ROL::Vector<double>::scale, "C++: ROL::Vector<double>::scale(const double) --> void", pybind11::arg("alpha"));
		cl.def("dot", (double (ROL::Vector<double>::*)(const class ROL::Vector<double> &) const) &ROL::Vector<double>::dot, "C++: ROL::Vector<double>::dot(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("norm", (double (ROL::Vector<double>::*)() const) &ROL::Vector<double>::norm, "C++: ROL::Vector<double>::norm() const --> double");
		cl.def("clone", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::Vector<double>::*)() const) &ROL::Vector<double>::clone, "C++: ROL::Vector<double>::clone() const --> class Teuchos::RCP<class ROL::Vector<double> >");
		cl.def("axpy", (void (ROL::Vector<double>::*)(const double, const class ROL::Vector<double> &)) &ROL::Vector<double>::axpy, "Compute \n where \n.\n\n             \n is the scaling of \n             \n\n     is a vector.\n\n             On return \n.\n             Uses #clone, #set, #scale and #plus for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::axpy(const double, const class ROL::Vector<double> &) --> void", pybind11::arg("alpha"), pybind11::arg("x"));
		cl.def("zero", (void (ROL::Vector<double>::*)()) &ROL::Vector<double>::zero, "Set to zero vector.\n\n             Uses #scale by zero for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::zero() --> void");
		cl.def("basis", (class Teuchos::RCP<class ROL::Vector<double> > (ROL::Vector<double>::*)(const int) const) &ROL::Vector<double>::basis, "Return i-th basis vector.\n\n             \n is the index of the basis function.\n             \n\n A reference-counted pointer to the basis vector with index \n\n             Overloading the basis is only required if the default gradient implementation\n             is used, which computes a finite-difference approximation.\n\n             ---\n\nC++: ROL::Vector<double>::basis(const int) const --> class Teuchos::RCP<class ROL::Vector<double> >", pybind11::arg("i"));
		cl.def("dimension", (int (ROL::Vector<double>::*)() const) &ROL::Vector<double>::dimension, "Return dimension of the vector space.\n\n             \n The dimension of the vector space, i.e., the total number of basis vectors.\n\n             Overload if the basis is overloaded.\n\n             ---\n\nC++: ROL::Vector<double>::dimension() const --> int");
		cl.def("set", (void (ROL::Vector<double>::*)(const class ROL::Vector<double> &)) &ROL::Vector<double>::set, "Set \n where \n.\n\n             \n     is a vector.\n\n             On return \n.\n             Uses #zero and #plus methods for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::set(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("dual", (const class ROL::Vector<double> & (ROL::Vector<double>::*)() const) &ROL::Vector<double>::dual, "Return dual representation of \n, for example,\n             the result of applying a Riesz map, or change of basis, or\n             change of memory layout.\n\n             \n         A const reference to dual representation.\n\n             By default, returns the current object.\n             Please overload if you need a dual representation.\n\n             ---\n\nC++: ROL::Vector<double>::dual() const --> const class ROL::Vector<double> &", pybind11::return_value_policy::automatic);
		cl.def("apply", (double (ROL::Vector<double>::*)(const class ROL::Vector<double> &) const) &ROL::Vector<double>::apply, "Apply \n to a dual vector.  This is equivalent\n             to the call \n\n.\n\n             \n      is a vector\n             \n\n         The number equal to \n.\n\n             ---\n\nC++: ROL::Vector<double>::apply(const class ROL::Vector<double> &) const --> double", pybind11::arg("x"));
		cl.def("applyUnary", (void (ROL::Vector<double>::*)(const class ROL::Elementwise::UnaryFunction<double> &)) &ROL::Vector<double>::applyUnary, "C++: ROL::Vector<double>::applyUnary(const class ROL::Elementwise::UnaryFunction<double> &) --> void", pybind11::arg("f"));
		cl.def("applyBinary", (void (ROL::Vector<double>::*)(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &)) &ROL::Vector<double>::applyBinary, "C++: ROL::Vector<double>::applyBinary(const class ROL::Elementwise::BinaryFunction<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("f"), pybind11::arg("x"));
		cl.def("reduce", (double (ROL::Vector<double>::*)(const class ROL::Elementwise::ReductionOp<double> &) const) &ROL::Vector<double>::reduce, "C++: ROL::Vector<double>::reduce(const class ROL::Elementwise::ReductionOp<double> &) const --> double", pybind11::arg("r"));
		cl.def("print", (void (ROL::Vector<double>::*)(std::ostream &) const) &ROL::Vector<double>::print, "C++: ROL::Vector<double>::print(std::ostream &) const --> void", pybind11::arg("outStream"));
		cl.def("setScalar", (void (ROL::Vector<double>::*)(const double)) &ROL::Vector<double>::setScalar, "Set \n where \n.\n\n             \n     is a scalar.\n\n             On return \n.\n             Uses #applyUnary methods for the computation.\n             Please overload if a more efficient implementation is needed.\n\n             ---\n\nC++: ROL::Vector<double>::setScalar(const double) --> void", pybind11::arg("C"));
		cl.def("randomize", [](ROL::Vector<double> &o) -> void { return o.randomize(); }, "");
		cl.def("randomize", [](ROL::Vector<double> &o, const double & a0) -> void { return o.randomize(a0); }, "", pybind11::arg("l"));
		cl.def("randomize", (void (ROL::Vector<double>::*)(const double, const double)) &ROL::Vector<double>::randomize, "Set vector to be uniform random between [l,u].\n\n             \n     is a the lower bound.\n             \n\n     is a the upper bound.\n\n             On return the components of \n are uniform\n             random numbers on the interval \n\n.\n       	     The default implementation uses #applyUnary methods for the\n       	     computation. Please overload if a more efficient implementation is\n             needed.\n\n             ---\n\nC++: ROL::Vector<double>::randomize(const double, const double) --> void", pybind11::arg("l"), pybind11::arg("u"));
		cl.def("checkVector", [](ROL::Vector<double> const &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) -> std::vector<double> { return o.checkVector(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("y"));
		cl.def("checkVector", [](ROL::Vector<double> const &o, const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const bool & a2) -> std::vector<double> { return o.checkVector(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("y"), pybind11::arg("printToStream"));
		cl.def("checkVector", (class std::vector<double> (ROL::Vector<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &) const) &ROL::Vector<double>::checkVector, "Verify vector-space methods.\n\n             \n     is a vector.\n             \n\n     is a vector.\n\n             Returns a vector of Reals, all of which should be close to zero.\n             They represent consistency errors in the vector space properties,\n             as follows:\n\n             - Commutativity of addition: \n.\n             - Associativity of addition: \n\n.\n             - Identity element of addition: \n\n.\n             - Inverse elements of addition: \n\n.\n             - Identity element of scalar multiplication: \n\n.\n             - Consistency of scalar multiplication with field multiplication: \n\n.\n             - Distributivity of scalar multiplication with respect to field addition: \n\n.\n             - Distributivity of scalar multiplication with respect to vector addition: \n\n.\n             - Commutativity of dot (inner) product over the field of reals: \n\n.\n             - Additivity of dot (inner) product: \n\n.\n             - Consistency of scalar multiplication and norm: \n\n.\n             - Reflexivity: \n\n .\n             - Consistency of apply and dual: \n\n.\n\n             The consistency errors are defined as the norms or absolute values of the differences between the left-hand\n             side and the right-hand side terms in the above equalities.\n\n             ---\n\nC++: ROL::Vector<double>::checkVector(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const bool, std::ostream &) const --> class std::vector<double>", pybind11::arg("x"), pybind11::arg("y"), pybind11::arg("printToStream"), pybind11::arg("outStream"));
		cl.def("assign", (class ROL::Vector<double> & (ROL::Vector<double>::*)(const class ROL::Vector<double> &)) &ROL::Vector<double>::operator=, "C++: ROL::Vector<double>::operator=(const class ROL::Vector<double> &) --> class ROL::Vector<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::MonteCarloGenerator file: line:69
		pybind11::class_<ROL::MonteCarloGenerator<double>, Teuchos::RCP<ROL::MonteCarloGenerator<double>>, PyCallBack_ROL_MonteCarloGenerator_double_t, ROL::SampleGenerator<double>> cl(M("ROL"), "MonteCarloGenerator_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](int const & a0, class std::vector<class std::vector<double> > & a1, const class Teuchos::RCP<class ROL::BatchManager<double> > & a2){ return new ROL::MonteCarloGenerator<double>(a0, a1, a2); }, [](int const & a0, class std::vector<class std::vector<double> > & a1, const class Teuchos::RCP<class ROL::BatchManager<double> > & a2){ return new PyCallBack_ROL_MonteCarloGenerator_double_t(a0, a1, a2); } ), "doc");
		cl.def( pybind11::init( [](int const & a0, class std::vector<class std::vector<double> > & a1, const class Teuchos::RCP<class ROL::BatchManager<double> > & a2, bool const & a3){ return new ROL::MonteCarloGenerator<double>(a0, a1, a2, a3); }, [](int const & a0, class std::vector<class std::vector<double> > & a1, const class Teuchos::RCP<class ROL::BatchManager<double> > & a2, bool const & a3){ return new PyCallBack_ROL_MonteCarloGenerator_double_t(a0, a1, a2, a3); } ), "doc");
		cl.def( pybind11::init( [](int const & a0, class std::vector<class std::vector<double> > & a1, const class Teuchos::RCP<class ROL::BatchManager<double> > & a2, bool const & a3, bool const & a4){ return new ROL::MonteCarloGenerator<double>(a0, a1, a2, a3, a4); }, [](int const & a0, class std::vector<class std::vector<double> > & a1, const class Teuchos::RCP<class ROL::BatchManager<double> > & a2, bool const & a3, bool const & a4){ return new PyCallBack_ROL_MonteCarloGenerator_double_t(a0, a1, a2, a3, a4); } ), "doc");
		cl.def( pybind11::init( [](int const & a0, class std::vector<class std::vector<double> > & a1, const class Teuchos::RCP<class ROL::BatchManager<double> > & a2, bool const & a3, bool const & a4, int const & a5){ return new ROL::MonteCarloGenerator<double>(a0, a1, a2, a3, a4, a5); }, [](int const & a0, class std::vector<class std::vector<double> > & a1, const class Teuchos::RCP<class ROL::BatchManager<double> > & a2, bool const & a3, bool const & a4, int const & a5){ return new PyCallBack_ROL_MonteCarloGenerator_double_t(a0, a1, a2, a3, a4, a5); } ), "doc");
		cl.def( pybind11::init<int, class std::vector<class std::vector<double> > &, const class Teuchos::RCP<class ROL::BatchManager<double> > &, bool, bool, int, int>(), pybind11::arg("nSamp"), pybind11::arg("bounds"), pybind11::arg("bman"), pybind11::arg("use_SA"), pybind11::arg("adaptive"), pybind11::arg("numNewSamps"), pybind11::arg("seed") );

		cl.def( pybind11::init( [](int const & a0, const class std::vector<double> & a1, const class std::vector<double> & a2, const class Teuchos::RCP<class ROL::BatchManager<double> > & a3){ return new ROL::MonteCarloGenerator<double>(a0, a1, a2, a3); }, [](int const & a0, const class std::vector<double> & a1, const class std::vector<double> & a2, const class Teuchos::RCP<class ROL::BatchManager<double> > & a3){ return new PyCallBack_ROL_MonteCarloGenerator_double_t(a0, a1, a2, a3); } ), "doc");
		cl.def( pybind11::init( [](int const & a0, const class std::vector<double> & a1, const class std::vector<double> & a2, const class Teuchos::RCP<class ROL::BatchManager<double> > & a3, bool const & a4){ return new ROL::MonteCarloGenerator<double>(a0, a1, a2, a3, a4); }, [](int const & a0, const class std::vector<double> & a1, const class std::vector<double> & a2, const class Teuchos::RCP<class ROL::BatchManager<double> > & a3, bool const & a4){ return new PyCallBack_ROL_MonteCarloGenerator_double_t(a0, a1, a2, a3, a4); } ), "doc");
		cl.def( pybind11::init( [](int const & a0, const class std::vector<double> & a1, const class std::vector<double> & a2, const class Teuchos::RCP<class ROL::BatchManager<double> > & a3, bool const & a4, bool const & a5){ return new ROL::MonteCarloGenerator<double>(a0, a1, a2, a3, a4, a5); }, [](int const & a0, const class std::vector<double> & a1, const class std::vector<double> & a2, const class Teuchos::RCP<class ROL::BatchManager<double> > & a3, bool const & a4, bool const & a5){ return new PyCallBack_ROL_MonteCarloGenerator_double_t(a0, a1, a2, a3, a4, a5); } ), "doc");
		cl.def( pybind11::init( [](int const & a0, const class std::vector<double> & a1, const class std::vector<double> & a2, const class Teuchos::RCP<class ROL::BatchManager<double> > & a3, bool const & a4, bool const & a5, int const & a6){ return new ROL::MonteCarloGenerator<double>(a0, a1, a2, a3, a4, a5, a6); }, [](int const & a0, const class std::vector<double> & a1, const class std::vector<double> & a2, const class Teuchos::RCP<class ROL::BatchManager<double> > & a3, bool const & a4, bool const & a5, int const & a6){ return new PyCallBack_ROL_MonteCarloGenerator_double_t(a0, a1, a2, a3, a4, a5, a6); } ), "doc");
		cl.def( pybind11::init<int, const class std::vector<double> &, const class std::vector<double> &, const class Teuchos::RCP<class ROL::BatchManager<double> > &, bool, bool, int, int>(), pybind11::arg("nSamp"), pybind11::arg("mean"), pybind11::arg("std"), pybind11::arg("bman"), pybind11::arg("use_SA"), pybind11::arg("adaptive"), pybind11::arg("numNewSamps"), pybind11::arg("seed") );

		cl.def( pybind11::init( [](PyCallBack_ROL_MonteCarloGenerator_double_t const &o){ return new PyCallBack_ROL_MonteCarloGenerator_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::MonteCarloGenerator<double> const &o){ return new ROL::MonteCarloGenerator<double>(o); } ) );
		cl.def("update", (void (ROL::MonteCarloGenerator<double>::*)(const class ROL::Vector<double> &)) &ROL::MonteCarloGenerator<double>::update, "C++: ROL::MonteCarloGenerator<double>::update(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("computeError", (double (ROL::MonteCarloGenerator<double>::*)(class std::vector<double> &)) &ROL::MonteCarloGenerator<double>::computeError, "C++: ROL::MonteCarloGenerator<double>::computeError(class std::vector<double> &) --> double", pybind11::arg("vals"));
		cl.def("refine", (void (ROL::MonteCarloGenerator<double>::*)()) &ROL::MonteCarloGenerator<double>::refine, "C++: ROL::MonteCarloGenerator<double>::refine() --> void");
		cl.def("numGlobalSamples", (int (ROL::MonteCarloGenerator<double>::*)() const) &ROL::MonteCarloGenerator<double>::numGlobalSamples, "C++: ROL::MonteCarloGenerator<double>::numGlobalSamples() const --> int");
		cl.def("update", (void (ROL::SampleGenerator<double>::*)(const class ROL::Vector<double> &)) &ROL::SampleGenerator<double>::update, "C++: ROL::SampleGenerator<double>::update(const class ROL::Vector<double> &) --> void", pybind11::arg("x"));
		cl.def("start", (int (ROL::SampleGenerator<double>::*)()) &ROL::SampleGenerator<double>::start, "C++: ROL::SampleGenerator<double>::start() --> int");
		cl.def("computeError", (double (ROL::SampleGenerator<double>::*)(class std::vector<double> &)) &ROL::SampleGenerator<double>::computeError, "C++: ROL::SampleGenerator<double>::computeError(class std::vector<double> &) --> double", pybind11::arg("vals"));
		cl.def("refine", (void (ROL::SampleGenerator<double>::*)()) &ROL::SampleGenerator<double>::refine, "C++: ROL::SampleGenerator<double>::refine() --> void");
		cl.def("setSamples", [](ROL::SampleGenerator<double> &o) -> void { return o.setSamples(); }, "");
		cl.def("setSamples", (void (ROL::SampleGenerator<double>::*)(bool)) &ROL::SampleGenerator<double>::setSamples, "C++: ROL::SampleGenerator<double>::setSamples(bool) --> void", pybind11::arg("inConstructor"));
		cl.def("numGlobalSamples", (int (ROL::SampleGenerator<double>::*)() const) &ROL::SampleGenerator<double>::numGlobalSamples, "C++: ROL::SampleGenerator<double>::numGlobalSamples() const --> int");
		cl.def("numMySamples", (int (ROL::SampleGenerator<double>::*)() const) &ROL::SampleGenerator<double>::numMySamples, "C++: ROL::SampleGenerator<double>::numMySamples() const --> int");
		cl.def("getMyPoint", (class std::vector<double> (ROL::SampleGenerator<double>::*)(const int) const) &ROL::SampleGenerator<double>::getMyPoint, "C++: ROL::SampleGenerator<double>::getMyPoint(const int) const --> class std::vector<double>", pybind11::arg("i"));
		cl.def("getMyWeight", (double (ROL::SampleGenerator<double>::*)(const int) const) &ROL::SampleGenerator<double>::getMyWeight, "C++: ROL::SampleGenerator<double>::getMyWeight(const int) const --> double", pybind11::arg("i"));
		cl.def("batchID", (int (ROL::SampleGenerator<double>::*)() const) &ROL::SampleGenerator<double>::batchID, "C++: ROL::SampleGenerator<double>::batchID() const --> int");
		cl.def("numBatches", (int (ROL::SampleGenerator<double>::*)() const) &ROL::SampleGenerator<double>::numBatches, "C++: ROL::SampleGenerator<double>::numBatches() const --> int");
		cl.def("sumAll", (void (ROL::SampleGenerator<double>::*)(double *, double *, int) const) &ROL::SampleGenerator<double>::sumAll, "C++: ROL::SampleGenerator<double>::sumAll(double *, double *, int) const --> void", pybind11::arg("input"), pybind11::arg("output"), pybind11::arg("dim"));
		cl.def("sumAll", (void (ROL::SampleGenerator<double>::*)(class ROL::Vector<double> &, class ROL::Vector<double> &) const) &ROL::SampleGenerator<double>::sumAll, "C++: ROL::SampleGenerator<double>::sumAll(class ROL::Vector<double> &, class ROL::Vector<double> &) const --> void", pybind11::arg("input"), pybind11::arg("output"));
		cl.def("broadcast", (void (ROL::SampleGenerator<double>::*)(double *, int, int) const) &ROL::SampleGenerator<double>::broadcast, "C++: ROL::SampleGenerator<double>::broadcast(double *, int, int) const --> void", pybind11::arg("input"), pybind11::arg("cnt"), pybind11::arg("root"));
		cl.def("barrier", (void (ROL::SampleGenerator<double>::*)() const) &ROL::SampleGenerator<double>::barrier, "C++: ROL::SampleGenerator<double>::barrier() const --> void");
		cl.def("getBatchManager", (const class Teuchos::RCP<class ROL::BatchManager<double> > (ROL::SampleGenerator<double>::*)() const) &ROL::SampleGenerator<double>::getBatchManager, "C++: ROL::SampleGenerator<double>::getBatchManager() const --> const class Teuchos::RCP<class ROL::BatchManager<double> >");
		cl.def("print", [](ROL::SampleGenerator<double> const &o) -> void { return o.print(); }, "");
		cl.def("print", [](ROL::SampleGenerator<double> const &o, const std::string & a0) -> void { return o.print(a0); }, "", pybind11::arg("filename"));
		cl.def("print", (void (ROL::SampleGenerator<double>::*)(const std::string &, const int) const) &ROL::SampleGenerator<double>::print, "C++: ROL::SampleGenerator<double>::print(const std::string &, const int) const --> void", pybind11::arg("filename"), pybind11::arg("prec"));
		cl.def("assign", (class ROL::SampleGenerator<double> & (ROL::SampleGenerator<double>::*)(const class ROL::SampleGenerator<double> &)) &ROL::SampleGenerator<double>::operator=, "C++: ROL::SampleGenerator<double>::operator=(const class ROL::SampleGenerator<double> &) --> class ROL::SampleGenerator<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::PrimalDualRisk file: line:70
		pybind11::class_<ROL::PrimalDualRisk<double>, Teuchos::RCP<ROL::PrimalDualRisk<double>>> cl(M("ROL"), "PrimalDualRisk_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<const class Teuchos::RCP<class ROL::Problem<double> > &, const class Teuchos::RCP<class ROL::SampleGenerator<double> > &, class Teuchos::ParameterList &>(), pybind11::arg("input"), pybind11::arg("sampler"), pybind11::arg("parlist") );

		cl.def( pybind11::init( [](ROL::PrimalDualRisk<double> const &o){ return new ROL::PrimalDualRisk<double>(o); } ) );
		cl.def("check", [](ROL::PrimalDualRisk<double> &o) -> void { return o.check(); }, "");
		cl.def("check", (void (ROL::PrimalDualRisk<double>::*)(std::ostream &)) &ROL::PrimalDualRisk<double>::check, "C++: ROL::PrimalDualRisk<double>::check(std::ostream &) --> void", pybind11::arg("outStream"));
		cl.def("run", [](ROL::PrimalDualRisk<double> &o) -> void { return o.run(); }, "");
		cl.def("run", (void (ROL::PrimalDualRisk<double>::*)(std::ostream &)) &ROL::PrimalDualRisk<double>::run, "C++: ROL::PrimalDualRisk<double>::run(std::ostream &) --> void", pybind11::arg("outStream"));
	}
	{ // ROL::RiskNeutralObjective file: line:71
		pybind11::class_<ROL::RiskNeutralObjective<double>, Teuchos::RCP<ROL::RiskNeutralObjective<double>>, PyCallBack_ROL_RiskNeutralObjective_double_t, ROL::Objective<double>> cl(M("ROL"), "RiskNeutralObjective_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](const class Teuchos::RCP<class ROL::Objective<double> > & a0, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a1, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a2, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a3){ return new ROL::RiskNeutralObjective<double>(a0, a1, a2, a3); }, [](const class Teuchos::RCP<class ROL::Objective<double> > & a0, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a1, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a2, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a3){ return new PyCallBack_ROL_RiskNeutralObjective_double_t(a0, a1, a2, a3); } ), "doc");
		cl.def( pybind11::init<const class Teuchos::RCP<class ROL::Objective<double> > &, const class Teuchos::RCP<class ROL::SampleGenerator<double> > &, const class Teuchos::RCP<class ROL::SampleGenerator<double> > &, const class Teuchos::RCP<class ROL::SampleGenerator<double> > &, const bool>(), pybind11::arg("pObj"), pybind11::arg("vsampler"), pybind11::arg("gsampler"), pybind11::arg("hsampler"), pybind11::arg("storage") );

		cl.def( pybind11::init( [](const class Teuchos::RCP<class ROL::Objective<double> > & a0, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a1, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a2){ return new ROL::RiskNeutralObjective<double>(a0, a1, a2); }, [](const class Teuchos::RCP<class ROL::Objective<double> > & a0, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a1, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a2){ return new PyCallBack_ROL_RiskNeutralObjective_double_t(a0, a1, a2); } ), "doc");
		cl.def( pybind11::init<const class Teuchos::RCP<class ROL::Objective<double> > &, const class Teuchos::RCP<class ROL::SampleGenerator<double> > &, const class Teuchos::RCP<class ROL::SampleGenerator<double> > &, const bool>(), pybind11::arg("pObj"), pybind11::arg("vsampler"), pybind11::arg("gsampler"), pybind11::arg("storage") );

		cl.def( pybind11::init( [](const class Teuchos::RCP<class ROL::Objective<double> > & a0, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a1){ return new ROL::RiskNeutralObjective<double>(a0, a1); }, [](const class Teuchos::RCP<class ROL::Objective<double> > & a0, const class Teuchos::RCP<class ROL::SampleGenerator<double> > & a1){ return new PyCallBack_ROL_RiskNeutralObjective_double_t(a0, a1); } ), "doc");
		cl.def( pybind11::init<const class Teuchos::RCP<class ROL::Objective<double> > &, const class Teuchos::RCP<class ROL::SampleGenerator<double> > &, const bool>(), pybind11::arg("pObj"), pybind11::arg("sampler"), pybind11::arg("storage") );

		cl.def( pybind11::init( [](PyCallBack_ROL_RiskNeutralObjective_double_t const &o){ return new PyCallBack_ROL_RiskNeutralObjective_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::RiskNeutralObjective<double> const &o){ return new ROL::RiskNeutralObjective<double>(o); } ) );
		cl.def("update", [](ROL::RiskNeutralObjective<double> &o, const class ROL::Vector<double> & a0, enum ROL::UpdateType const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("type"));
		cl.def("update", (void (ROL::RiskNeutralObjective<double>::*)(const class ROL::Vector<double> &, enum ROL::UpdateType, int)) &ROL::RiskNeutralObjective<double>::update, "C++: ROL::RiskNeutralObjective<double>::update(const class ROL::Vector<double> &, enum ROL::UpdateType, int) --> void", pybind11::arg("x"), pybind11::arg("type"), pybind11::arg("iter"));
		cl.def("update", [](ROL::RiskNeutralObjective<double> &o, const class ROL::Vector<double> & a0) -> void { return o.update(a0); }, "", pybind11::arg("x"));
		cl.def("update", [](ROL::RiskNeutralObjective<double> &o, const class ROL::Vector<double> & a0, bool const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("flag"));
		cl.def("update", (void (ROL::RiskNeutralObjective<double>::*)(const class ROL::Vector<double> &, bool, int)) &ROL::RiskNeutralObjective<double>::update, "C++: ROL::RiskNeutralObjective<double>::update(const class ROL::Vector<double> &, bool, int) --> void", pybind11::arg("x"), pybind11::arg("flag"), pybind11::arg("iter"));
		cl.def("value", (double (ROL::RiskNeutralObjective<double>::*)(const class ROL::Vector<double> &, double &)) &ROL::RiskNeutralObjective<double>::value, "C++: ROL::RiskNeutralObjective<double>::value(const class ROL::Vector<double> &, double &) --> double", pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("gradient", (void (ROL::RiskNeutralObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::RiskNeutralObjective<double>::gradient, "C++: ROL::RiskNeutralObjective<double>::gradient(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("g"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("hessVec", (void (ROL::RiskNeutralObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::RiskNeutralObjective<double>::hessVec, "C++: ROL::RiskNeutralObjective<double>::hessVec(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("precond", (void (ROL::RiskNeutralObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::RiskNeutralObjective<double>::precond, "C++: ROL::RiskNeutralObjective<double>::precond(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("Pv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("assign", (class ROL::RiskNeutralObjective<double> & (ROL::RiskNeutralObjective<double>::*)(const class ROL::RiskNeutralObjective<double> &)) &ROL::RiskNeutralObjective<double>::operator=, "C++: ROL::RiskNeutralObjective<double>::operator=(const class ROL::RiskNeutralObjective<double> &) --> class ROL::RiskNeutralObjective<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
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
