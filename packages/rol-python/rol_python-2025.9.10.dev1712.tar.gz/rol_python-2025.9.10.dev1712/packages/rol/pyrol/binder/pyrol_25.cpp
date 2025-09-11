#include <ROL_BarzilaiBorwein.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_LinearOperator.hpp>
#include <ROL_Objective.hpp>
#include <ROL_Secant.hpp>
#include <ROL_TrustRegionModel_U.hpp>
#include <ROL_TrustRegion_U.hpp>
#include <ROL_TrustRegion_U_Types.hpp>
#include <ROL_UpdateType.hpp>
#include <ROL_ValidParameters.hpp>
#include <ROL_Vector.hpp>
#include <ROL_lBFGS.hpp>
#include <ROL_lDFP.hpp>
#include <ROL_lSR1.hpp>
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

// ROL::Secant file:ROL_Secant.hpp line:45
struct PyCallBack_ROL_Secant_double_t : public ROL::Secant<double> {
	using ROL::Secant<double>::Secant;

	void updateStorage(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const double a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Secant<double> *>(this), "updateStorage");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::updateStorage(a0, a1, a2, a3, a4, a5);
	}
	void applyH(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Secant<double> *>(this), "applyH");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		pybind11::pybind11_fail("Tried to call pure virtual function \"Secant::applyH\"");
	}
	void applyH0(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Secant<double> *>(this), "applyH0");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::applyH0(a0, a1);
	}
	void applyB(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Secant<double> *>(this), "applyB");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		pybind11::pybind11_fail("Tried to call pure virtual function \"Secant::applyB\"");
	}
	void applyB0(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Secant<double> *>(this), "applyB0");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::applyB0(a0, a1);
	}
	void apply(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Secant<double> *>(this), "apply");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::apply(a0, a1, a2);
	}
	void applyInverse(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Secant<double> *>(this), "applyInverse");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::applyInverse(a0, a1, a2);
	}
	void update(const class ROL::Vector<double> & a0, bool a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Secant<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::update(a0, a1, a2);
	}
	void applyAdjoint(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Secant<double> *>(this), "applyAdjoint");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::applyAdjoint(a0, a1, a2);
	}
	void applyAdjointInverse(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Secant<double> *>(this), "applyAdjointInverse");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::applyAdjointInverse(a0, a1, a2);
	}
};

// ROL::lBFGS file:ROL_lBFGS.hpp line:22
struct PyCallBack_ROL_lBFGS_double_t : public ROL::lBFGS<double> {
	using ROL::lBFGS<double>::lBFGS;

	void applyH(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lBFGS<double> *>(this), "applyH");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return lBFGS::applyH(a0, a1);
	}
	void applyB(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lBFGS<double> *>(this), "applyB");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return lBFGS::applyB(a0, a1);
	}
	void updateStorage(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const double a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lBFGS<double> *>(this), "updateStorage");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::updateStorage(a0, a1, a2, a3, a4, a5);
	}
	void applyH0(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lBFGS<double> *>(this), "applyH0");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::applyH0(a0, a1);
	}
	void applyB0(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lBFGS<double> *>(this), "applyB0");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::applyB0(a0, a1);
	}
	void apply(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lBFGS<double> *>(this), "apply");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::apply(a0, a1, a2);
	}
	void applyInverse(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lBFGS<double> *>(this), "applyInverse");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::applyInverse(a0, a1, a2);
	}
	void update(const class ROL::Vector<double> & a0, bool a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lBFGS<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::update(a0, a1, a2);
	}
	void applyAdjoint(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lBFGS<double> *>(this), "applyAdjoint");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::applyAdjoint(a0, a1, a2);
	}
	void applyAdjointInverse(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lBFGS<double> *>(this), "applyAdjointInverse");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::applyAdjointInverse(a0, a1, a2);
	}
};

// ROL::lDFP file:ROL_lDFP.hpp line:22
struct PyCallBack_ROL_lDFP_double_t : public ROL::lDFP<double> {
	using ROL::lDFP<double>::lDFP;

	void applyH(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lDFP<double> *>(this), "applyH");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return lDFP::applyH(a0, a1);
	}
	void applyH0(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lDFP<double> *>(this), "applyH0");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return lDFP::applyH0(a0, a1);
	}
	void applyB(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lDFP<double> *>(this), "applyB");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return lDFP::applyB(a0, a1);
	}
	void applyB0(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lDFP<double> *>(this), "applyB0");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return lDFP::applyB0(a0, a1);
	}
	void updateStorage(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const double a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lDFP<double> *>(this), "updateStorage");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::updateStorage(a0, a1, a2, a3, a4, a5);
	}
	void apply(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lDFP<double> *>(this), "apply");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::apply(a0, a1, a2);
	}
	void applyInverse(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lDFP<double> *>(this), "applyInverse");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::applyInverse(a0, a1, a2);
	}
	void update(const class ROL::Vector<double> & a0, bool a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lDFP<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::update(a0, a1, a2);
	}
	void applyAdjoint(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lDFP<double> *>(this), "applyAdjoint");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::applyAdjoint(a0, a1, a2);
	}
	void applyAdjointInverse(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lDFP<double> *>(this), "applyAdjointInverse");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::applyAdjointInverse(a0, a1, a2);
	}
};

// ROL::lSR1 file:ROL_lSR1.hpp line:23
struct PyCallBack_ROL_lSR1_double_t : public ROL::lSR1<double> {
	using ROL::lSR1<double>::lSR1;

	void updateStorage(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const double a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lSR1<double> *>(this), "updateStorage");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return lSR1::updateStorage(a0, a1, a2, a3, a4, a5);
	}
	void applyH0(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lSR1<double> *>(this), "applyH0");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return lSR1::applyH0(a0, a1);
	}
	void applyH(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lSR1<double> *>(this), "applyH");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return lSR1::applyH(a0, a1);
	}
	void applyB0(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lSR1<double> *>(this), "applyB0");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return lSR1::applyB0(a0, a1);
	}
	void applyB(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lSR1<double> *>(this), "applyB");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return lSR1::applyB(a0, a1);
	}
	void apply(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lSR1<double> *>(this), "apply");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::apply(a0, a1, a2);
	}
	void applyInverse(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lSR1<double> *>(this), "applyInverse");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::applyInverse(a0, a1, a2);
	}
	void update(const class ROL::Vector<double> & a0, bool a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lSR1<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::update(a0, a1, a2);
	}
	void applyAdjoint(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lSR1<double> *>(this), "applyAdjoint");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::applyAdjoint(a0, a1, a2);
	}
	void applyAdjointInverse(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::lSR1<double> *>(this), "applyAdjointInverse");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::applyAdjointInverse(a0, a1, a2);
	}
};

// ROL::BarzilaiBorwein file:ROL_BarzilaiBorwein.hpp line:26
struct PyCallBack_ROL_BarzilaiBorwein_double_t : public ROL::BarzilaiBorwein<double> {
	using ROL::BarzilaiBorwein<double>::BarzilaiBorwein;

	void applyH(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BarzilaiBorwein<double> *>(this), "applyH");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return BarzilaiBorwein::applyH(a0, a1);
	}
	void applyB(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BarzilaiBorwein<double> *>(this), "applyB");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return BarzilaiBorwein::applyB(a0, a1);
	}
	void updateStorage(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const double a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BarzilaiBorwein<double> *>(this), "updateStorage");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::updateStorage(a0, a1, a2, a3, a4, a5);
	}
	void applyH0(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BarzilaiBorwein<double> *>(this), "applyH0");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::applyH0(a0, a1);
	}
	void applyB0(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BarzilaiBorwein<double> *>(this), "applyB0");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::applyB0(a0, a1);
	}
	void apply(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BarzilaiBorwein<double> *>(this), "apply");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::apply(a0, a1, a2);
	}
	void applyInverse(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BarzilaiBorwein<double> *>(this), "applyInverse");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Secant::applyInverse(a0, a1, a2);
	}
	void update(const class ROL::Vector<double> & a0, bool a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BarzilaiBorwein<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::update(a0, a1, a2);
	}
	void applyAdjoint(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BarzilaiBorwein<double> *>(this), "applyAdjoint");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::applyAdjoint(a0, a1, a2);
	}
	void applyAdjointInverse(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BarzilaiBorwein<double> *>(this), "applyAdjointInverse");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return LinearOperator::applyAdjointInverse(a0, a1, a2);
	}
};

// ROL::TrustRegionModel_U file:ROL_TrustRegionModel_U.hpp line:32
struct PyCallBack_ROL_TrustRegionModel_U_double_t : public ROL::TrustRegionModel_U<double> {
	using ROL::TrustRegionModel_U<double>::TrustRegionModel_U;

	void setData(class ROL::Objective<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "setData");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return TrustRegionModel_U::setData(a0, a1, a2, a3);
	}
	double value(const class ROL::Vector<double> & a0, double & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "value");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return TrustRegionModel_U::value(a0, a1);
	}
	void gradient(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "gradient");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return TrustRegionModel_U::gradient(a0, a1, a2);
	}
	void hessVec(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "hessVec");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return TrustRegionModel_U::hessVec(a0, a1, a2, a3);
	}
	void invHessVec(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "invHessVec");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return TrustRegionModel_U::invHessVec(a0, a1, a2, a3);
	}
	void precond(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "precond");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return TrustRegionModel_U::precond(a0, a1, a2, a3);
	}
	const class Teuchos::RCP<const class ROL::Vector<double> > getGradient() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "getGradient");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const class Teuchos::RCP<const class ROL::Vector<double> >>::value) {
				static pybind11::detail::override_caster_t<const class Teuchos::RCP<const class ROL::Vector<double> >> caster;
				return pybind11::detail::cast_ref<const class Teuchos::RCP<const class ROL::Vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const class Teuchos::RCP<const class ROL::Vector<double> >>(std::move(o));
		}
		return TrustRegionModel_U::getGradient();
	}
	const class Teuchos::RCP<const class ROL::Vector<double> > getIterate() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "getIterate");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const class Teuchos::RCP<const class ROL::Vector<double> >>::value) {
				static pybind11::detail::override_caster_t<const class Teuchos::RCP<const class ROL::Vector<double> >> caster;
				return pybind11::detail::cast_ref<const class Teuchos::RCP<const class ROL::Vector<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const class Teuchos::RCP<const class ROL::Vector<double> >>(std::move(o));
		}
		return TrustRegionModel_U::getIterate();
	}
	const class Teuchos::RCP<class ROL::Objective<double> > getObjective() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "getObjective");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<const class Teuchos::RCP<class ROL::Objective<double> >>::value) {
				static pybind11::detail::override_caster_t<const class Teuchos::RCP<class ROL::Objective<double> >> caster;
				return pybind11::detail::cast_ref<const class Teuchos::RCP<class ROL::Objective<double> >>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<const class Teuchos::RCP<class ROL::Objective<double> >>(std::move(o));
		}
		return TrustRegionModel_U::getObjective();
	}
	void update(const class ROL::Vector<double> & a0, enum ROL::UpdateType a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "update");
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
	void update(const class ROL::Vector<double> & a0, bool a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "update");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "dirDeriv");
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
	void prox(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "prox");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "proxJacVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "checkHessSym");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "checkHessSym");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "checkProxJacVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegionModel_U<double> *>(this), "setParameter");
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

// ROL::TrustRegion_U file:ROL_TrustRegion_U.hpp line:23
struct PyCallBack_ROL_TrustRegion_U_double_t : public ROL::TrustRegion_U<double> {
	using ROL::TrustRegion_U<double>::TrustRegion_U;

	void initialize(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegion_U<double> *>(this), "initialize");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return TrustRegion_U::initialize(a0, a1);
	}
	void solve(class ROL::Vector<double> & a0, double & a1, double & a2, int & a3, int & a4, const double a5, class ROL::TrustRegionModel_U<double> & a6) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TrustRegion_U<double> *>(this), "solve");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		pybind11::pybind11_fail("Tried to call pure virtual function \"TrustRegion_U::solve\"");
	}
};

void bind_pyrol_25(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	// ROL::getValidROLParameters() file:ROL_ValidParameters.hpp line:20
	M("ROL").def("getValidROLParameters", (class Teuchos::RCP<const class Teuchos::ParameterList> (*)()) &ROL::getValidROLParameters, "C++: ROL::getValidROLParameters() --> class Teuchos::RCP<const class Teuchos::ParameterList>");

	// ROL::getValidSOLParameters() file:ROL_ValidParameters.hpp line:255
	M("ROL").def("getValidSOLParameters", (class Teuchos::RCP<const class Teuchos::ParameterList> (*)()) &ROL::getValidSOLParameters, "C++: ROL::getValidSOLParameters() --> class Teuchos::RCP<const class Teuchos::ParameterList>");

	// ROL::ETrustRegionU file:ROL_TrustRegion_U_Types.hpp line:29
	pybind11::enum_<ROL::ETrustRegionU>(M("ROL"), "ETrustRegionU", pybind11::arithmetic(), "Enumeration of trust-region solver types.\n\n      \n    TRUSTREGION_U_CAUCHYPOINT     describe\n      \n\n    TRUSTREGION_U_TRUNCATEDCG     describe\n      \n\n    TRUSTREGION_U_SPG             describe\n      \n\n    TRUSTREGION_U_DOGLEG          describe\n      \n\n    TRUSTREGION_U_DOUBLEDOGLEG    describe", pybind11::module_local())
		.value("TRUSTREGION_U_CAUCHYPOINT", ROL::TRUSTREGION_U_CAUCHYPOINT)
		.value("TRUSTREGION_U_TRUNCATEDCG", ROL::TRUSTREGION_U_TRUNCATEDCG)
		.value("TRUSTREGION_U_SPG", ROL::TRUSTREGION_U_SPG)
		.value("TRUSTREGION_U_DOGLEG", ROL::TRUSTREGION_U_DOGLEG)
		.value("TRUSTREGION_U_DOUBLEDOGLEG", ROL::TRUSTREGION_U_DOUBLEDOGLEG)
		.value("TRUSTREGION_U_LAST", ROL::TRUSTREGION_U_LAST)
		.export_values();

;

	// ROL::ETrustRegionUToString(enum ROL::ETrustRegionU) file:ROL_TrustRegion_U_Types.hpp line:38
	M("ROL").def("ETrustRegionUToString", (std::string (*)(enum ROL::ETrustRegionU)) &ROL::ETrustRegionUToString, "C++: ROL::ETrustRegionUToString(enum ROL::ETrustRegionU) --> std::string", pybind11::arg("tr"));

	// ROL::isValidTrustRegionU(enum ROL::ETrustRegionU) file:ROL_TrustRegion_U_Types.hpp line:57
	M("ROL").def("isValidTrustRegionU", (int (*)(enum ROL::ETrustRegionU)) &ROL::isValidTrustRegionU, "Verifies validity of a TrustRegionU enum.\n\n      \n  [in]  - enum of the TrustRegionU\n      \n\n 1 if the argument is a valid TrustRegionU; 0 otherwise.\n\nC++: ROL::isValidTrustRegionU(enum ROL::ETrustRegionU) --> int", pybind11::arg("ls"));

	// ROL::StringToETrustRegionU(std::string) file:ROL_TrustRegion_U_Types.hpp line:86
	M("ROL").def("StringToETrustRegionU", (enum ROL::ETrustRegionU (*)(std::string)) &ROL::StringToETrustRegionU, "C++: ROL::StringToETrustRegionU(std::string) --> enum ROL::ETrustRegionU", pybind11::arg("s"));

	// ROL::ESecantMode file:ROL_Secant.hpp line:23
	pybind11::enum_<ROL::ESecantMode>(M("ROL"), "ESecantMode", pybind11::arithmetic(), "", pybind11::module_local())
		.value("SECANTMODE_FORWARD", ROL::SECANTMODE_FORWARD)
		.value("SECANTMODE_INVERSE", ROL::SECANTMODE_INVERSE)
		.value("SECANTMODE_BOTH", ROL::SECANTMODE_BOTH)
		.export_values();

;

	{ // ROL::SecantState file:ROL_Secant.hpp line:30
		pybind11::class_<ROL::SecantState<double>, Teuchos::RCP<ROL::SecantState<double>>> cl(M("ROL"), "SecantState_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<int, enum ROL::ESecantMode>(), pybind11::arg("M"), pybind11::arg("sm") );

		cl.def( pybind11::init( [](ROL::SecantState<double> const &o){ return new ROL::SecantState<double>(o); } ) );
		cl.def_readwrite("iterate", &ROL::SecantState<double>::iterate);
		cl.def_readwrite("iterDiff", &ROL::SecantState<double>::iterDiff);
		cl.def_readwrite("gradDiff", &ROL::SecantState<double>::gradDiff);
		cl.def_readwrite("product", &ROL::SecantState<double>::product);
		cl.def_readwrite("product2", &ROL::SecantState<double>::product2);
		cl.def_readwrite("storage", &ROL::SecantState<double>::storage);
		cl.def_readwrite("current", &ROL::SecantState<double>::current);
		cl.def_readwrite("iter", &ROL::SecantState<double>::iter);
		cl.def_readwrite("mode", &ROL::SecantState<double>::mode);
		cl.def("assign", (struct ROL::SecantState<double> & (ROL::SecantState<double>::*)(const struct ROL::SecantState<double> &)) &ROL::SecantState<double>::operator=, "C++: ROL::SecantState<double>::operator=(const struct ROL::SecantState<double> &) --> struct ROL::SecantState<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::Secant file:ROL_Secant.hpp line:45
		pybind11::class_<ROL::Secant<double>, Teuchos::RCP<ROL::Secant<double>>, PyCallBack_ROL_Secant_double_t, ROL::LinearOperator<double>> cl(M("ROL"), "Secant_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new PyCallBack_ROL_Secant_double_t(); } ), "doc");
		cl.def( pybind11::init( [](int const & a0){ return new PyCallBack_ROL_Secant_double_t(a0); } ), "doc");
		cl.def( pybind11::init( [](int const & a0, bool const & a1){ return new PyCallBack_ROL_Secant_double_t(a0, a1); } ), "doc");
		cl.def( pybind11::init( [](int const & a0, bool const & a1, double const & a2){ return new PyCallBack_ROL_Secant_double_t(a0, a1, a2); } ), "doc");
		cl.def( pybind11::init<int, bool, double, enum ROL::ESecantMode>(), pybind11::arg("M"), pybind11::arg("useDefaultScaling"), pybind11::arg("Bscaling"), pybind11::arg("mode") );

		cl.def(pybind11::init<PyCallBack_ROL_Secant_double_t const &>());
		cl.def("updateStorage", (void (ROL::Secant<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::Secant<double>::updateStorage, "C++: ROL::Secant<double>::updateStorage(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("grad"), pybind11::arg("gp"), pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("applyH", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyH, "C++: ROL::Secant<double>::applyH(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyH0", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyH0, "C++: ROL::Secant<double>::applyH0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyB", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyB, "C++: ROL::Secant<double>::applyB(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("applyB0", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyB0, "C++: ROL::Secant<double>::applyB0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("test", [](ROL::Secant<double> const &o) -> void { return o.test(); }, "");
		cl.def("test", (void (ROL::Secant<double>::*)(std::ostream &) const) &ROL::Secant<double>::test, "C++: ROL::Secant<double>::test(std::ostream &) const --> void", pybind11::arg("stream"));
		cl.def("apply", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::Secant<double>::apply, "C++: ROL::Secant<double>::apply(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyInverse", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::Secant<double>::applyInverse, "C++: ROL::Secant<double>::applyInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("update", [](ROL::LinearOperator<double> &o, const class ROL::Vector<double> & a0) -> void { return o.update(a0); }, "", pybind11::arg("x"));
		cl.def("update", [](ROL::LinearOperator<double> &o, const class ROL::Vector<double> & a0, bool const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("flag"));
		cl.def("update", (void (ROL::LinearOperator<double>::*)(const class ROL::Vector<double> &, bool, int)) &ROL::LinearOperator<double>::update, "C++: ROL::LinearOperator<double>::update(const class ROL::Vector<double> &, bool, int) --> void", pybind11::arg("x"), pybind11::arg("flag"), pybind11::arg("iter"));
		cl.def("apply", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::apply, "C++: ROL::LinearOperator<double>::apply(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyInverse", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyInverse, "C++: ROL::LinearOperator<double>::applyInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyAdjoint", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyAdjoint, "C++: ROL::LinearOperator<double>::applyAdjoint(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyAdjointInverse", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyAdjointInverse, "C++: ROL::LinearOperator<double>::applyAdjointInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("assign", (class ROL::LinearOperator<double> & (ROL::LinearOperator<double>::*)(const class ROL::LinearOperator<double> &)) &ROL::LinearOperator<double>::operator=, "C++: ROL::LinearOperator<double>::operator=(const class ROL::LinearOperator<double> &) --> class ROL::LinearOperator<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::lBFGS file:ROL_lBFGS.hpp line:22
		pybind11::class_<ROL::lBFGS<double>, Teuchos::RCP<ROL::lBFGS<double>>, PyCallBack_ROL_lBFGS_double_t, ROL::Secant<double>> cl(M("ROL"), "lBFGS_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](int const & a0){ return new ROL::lBFGS<double>(a0); }, [](int const & a0){ return new PyCallBack_ROL_lBFGS_double_t(a0); } ), "doc");
		cl.def( pybind11::init( [](int const & a0, bool const & a1){ return new ROL::lBFGS<double>(a0, a1); }, [](int const & a0, bool const & a1){ return new PyCallBack_ROL_lBFGS_double_t(a0, a1); } ), "doc");
		cl.def( pybind11::init<int, bool, double>(), pybind11::arg("M"), pybind11::arg("useDefaultScaling"), pybind11::arg("Bscaling") );

		cl.def( pybind11::init( [](PyCallBack_ROL_lBFGS_double_t const &o){ return new PyCallBack_ROL_lBFGS_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::lBFGS<double> const &o){ return new ROL::lBFGS<double>(o); } ) );
		cl.def("applyH", (void (ROL::lBFGS<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::lBFGS<double>::applyH, "C++: ROL::lBFGS<double>::applyH(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyB", (void (ROL::lBFGS<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::lBFGS<double>::applyB, "C++: ROL::lBFGS<double>::applyB(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("updateStorage", (void (ROL::Secant<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::Secant<double>::updateStorage, "C++: ROL::Secant<double>::updateStorage(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("grad"), pybind11::arg("gp"), pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("applyH", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyH, "C++: ROL::Secant<double>::applyH(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyH0", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyH0, "C++: ROL::Secant<double>::applyH0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyB", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyB, "C++: ROL::Secant<double>::applyB(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("applyB0", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyB0, "C++: ROL::Secant<double>::applyB0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("test", [](ROL::Secant<double> const &o) -> void { return o.test(); }, "");
		cl.def("test", (void (ROL::Secant<double>::*)(std::ostream &) const) &ROL::Secant<double>::test, "C++: ROL::Secant<double>::test(std::ostream &) const --> void", pybind11::arg("stream"));
		cl.def("apply", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::Secant<double>::apply, "C++: ROL::Secant<double>::apply(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyInverse", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::Secant<double>::applyInverse, "C++: ROL::Secant<double>::applyInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("update", [](ROL::LinearOperator<double> &o, const class ROL::Vector<double> & a0) -> void { return o.update(a0); }, "", pybind11::arg("x"));
		cl.def("update", [](ROL::LinearOperator<double> &o, const class ROL::Vector<double> & a0, bool const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("flag"));
		cl.def("update", (void (ROL::LinearOperator<double>::*)(const class ROL::Vector<double> &, bool, int)) &ROL::LinearOperator<double>::update, "C++: ROL::LinearOperator<double>::update(const class ROL::Vector<double> &, bool, int) --> void", pybind11::arg("x"), pybind11::arg("flag"), pybind11::arg("iter"));
		cl.def("apply", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::apply, "C++: ROL::LinearOperator<double>::apply(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyInverse", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyInverse, "C++: ROL::LinearOperator<double>::applyInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyAdjoint", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyAdjoint, "C++: ROL::LinearOperator<double>::applyAdjoint(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyAdjointInverse", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyAdjointInverse, "C++: ROL::LinearOperator<double>::applyAdjointInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("assign", (class ROL::LinearOperator<double> & (ROL::LinearOperator<double>::*)(const class ROL::LinearOperator<double> &)) &ROL::LinearOperator<double>::operator=, "C++: ROL::LinearOperator<double>::operator=(const class ROL::LinearOperator<double> &) --> class ROL::LinearOperator<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::lDFP file:ROL_lDFP.hpp line:22
		pybind11::class_<ROL::lDFP<double>, Teuchos::RCP<ROL::lDFP<double>>, PyCallBack_ROL_lDFP_double_t, ROL::Secant<double>> cl(M("ROL"), "lDFP_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](int const & a0){ return new ROL::lDFP<double>(a0); }, [](int const & a0){ return new PyCallBack_ROL_lDFP_double_t(a0); } ), "doc");
		cl.def( pybind11::init( [](int const & a0, bool const & a1){ return new ROL::lDFP<double>(a0, a1); }, [](int const & a0, bool const & a1){ return new PyCallBack_ROL_lDFP_double_t(a0, a1); } ), "doc");
		cl.def( pybind11::init<int, bool, double>(), pybind11::arg("M"), pybind11::arg("useDefaultScaling"), pybind11::arg("Bscaling") );

		cl.def( pybind11::init( [](PyCallBack_ROL_lDFP_double_t const &o){ return new PyCallBack_ROL_lDFP_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::lDFP<double> const &o){ return new ROL::lDFP<double>(o); } ) );
		cl.def("applyH", (void (ROL::lDFP<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::lDFP<double>::applyH, "C++: ROL::lDFP<double>::applyH(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyH0", (void (ROL::lDFP<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::lDFP<double>::applyH0, "C++: ROL::lDFP<double>::applyH0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyB", (void (ROL::lDFP<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::lDFP<double>::applyB, "C++: ROL::lDFP<double>::applyB(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("applyB0", (void (ROL::lDFP<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::lDFP<double>::applyB0, "C++: ROL::lDFP<double>::applyB0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("updateStorage", (void (ROL::Secant<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::Secant<double>::updateStorage, "C++: ROL::Secant<double>::updateStorage(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("grad"), pybind11::arg("gp"), pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("applyH", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyH, "C++: ROL::Secant<double>::applyH(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyH0", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyH0, "C++: ROL::Secant<double>::applyH0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyB", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyB, "C++: ROL::Secant<double>::applyB(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("applyB0", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyB0, "C++: ROL::Secant<double>::applyB0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("test", [](ROL::Secant<double> const &o) -> void { return o.test(); }, "");
		cl.def("test", (void (ROL::Secant<double>::*)(std::ostream &) const) &ROL::Secant<double>::test, "C++: ROL::Secant<double>::test(std::ostream &) const --> void", pybind11::arg("stream"));
		cl.def("apply", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::Secant<double>::apply, "C++: ROL::Secant<double>::apply(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyInverse", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::Secant<double>::applyInverse, "C++: ROL::Secant<double>::applyInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("update", [](ROL::LinearOperator<double> &o, const class ROL::Vector<double> & a0) -> void { return o.update(a0); }, "", pybind11::arg("x"));
		cl.def("update", [](ROL::LinearOperator<double> &o, const class ROL::Vector<double> & a0, bool const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("flag"));
		cl.def("update", (void (ROL::LinearOperator<double>::*)(const class ROL::Vector<double> &, bool, int)) &ROL::LinearOperator<double>::update, "C++: ROL::LinearOperator<double>::update(const class ROL::Vector<double> &, bool, int) --> void", pybind11::arg("x"), pybind11::arg("flag"), pybind11::arg("iter"));
		cl.def("apply", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::apply, "C++: ROL::LinearOperator<double>::apply(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyInverse", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyInverse, "C++: ROL::LinearOperator<double>::applyInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyAdjoint", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyAdjoint, "C++: ROL::LinearOperator<double>::applyAdjoint(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyAdjointInverse", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyAdjointInverse, "C++: ROL::LinearOperator<double>::applyAdjointInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("assign", (class ROL::LinearOperator<double> & (ROL::LinearOperator<double>::*)(const class ROL::LinearOperator<double> &)) &ROL::LinearOperator<double>::operator=, "C++: ROL::LinearOperator<double>::operator=(const class ROL::LinearOperator<double> &) --> class ROL::LinearOperator<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::lSR1 file:ROL_lSR1.hpp line:23
		pybind11::class_<ROL::lSR1<double>, Teuchos::RCP<ROL::lSR1<double>>, PyCallBack_ROL_lSR1_double_t, ROL::Secant<double>> cl(M("ROL"), "lSR1_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](int const & a0){ return new ROL::lSR1<double>(a0); }, [](int const & a0){ return new PyCallBack_ROL_lSR1_double_t(a0); } ), "doc");
		cl.def( pybind11::init( [](int const & a0, bool const & a1){ return new ROL::lSR1<double>(a0, a1); }, [](int const & a0, bool const & a1){ return new PyCallBack_ROL_lSR1_double_t(a0, a1); } ), "doc");
		cl.def( pybind11::init( [](int const & a0, bool const & a1, double const & a2){ return new ROL::lSR1<double>(a0, a1, a2); }, [](int const & a0, bool const & a1, double const & a2){ return new PyCallBack_ROL_lSR1_double_t(a0, a1, a2); } ), "doc");
		cl.def( pybind11::init<int, bool, double, enum ROL::ESecantMode>(), pybind11::arg("M"), pybind11::arg("useDefaultScaling"), pybind11::arg("Bscaling"), pybind11::arg("mode") );

		cl.def( pybind11::init( [](PyCallBack_ROL_lSR1_double_t const &o){ return new PyCallBack_ROL_lSR1_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::lSR1<double> const &o){ return new ROL::lSR1<double>(o); } ) );
		cl.def("updateStorage", (void (ROL::lSR1<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::lSR1<double>::updateStorage, "C++: ROL::lSR1<double>::updateStorage(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("grad"), pybind11::arg("gp"), pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("applyH0", (void (ROL::lSR1<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::lSR1<double>::applyH0, "C++: ROL::lSR1<double>::applyH0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyH", (void (ROL::lSR1<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::lSR1<double>::applyH, "C++: ROL::lSR1<double>::applyH(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyB0", (void (ROL::lSR1<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::lSR1<double>::applyB0, "C++: ROL::lSR1<double>::applyB0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("applyB", (void (ROL::lSR1<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::lSR1<double>::applyB, "C++: ROL::lSR1<double>::applyB(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("updateStorage", (void (ROL::Secant<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::Secant<double>::updateStorage, "C++: ROL::Secant<double>::updateStorage(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("grad"), pybind11::arg("gp"), pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("applyH", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyH, "C++: ROL::Secant<double>::applyH(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyH0", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyH0, "C++: ROL::Secant<double>::applyH0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyB", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyB, "C++: ROL::Secant<double>::applyB(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("applyB0", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyB0, "C++: ROL::Secant<double>::applyB0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("test", [](ROL::Secant<double> const &o) -> void { return o.test(); }, "");
		cl.def("test", (void (ROL::Secant<double>::*)(std::ostream &) const) &ROL::Secant<double>::test, "C++: ROL::Secant<double>::test(std::ostream &) const --> void", pybind11::arg("stream"));
		cl.def("apply", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::Secant<double>::apply, "C++: ROL::Secant<double>::apply(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyInverse", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::Secant<double>::applyInverse, "C++: ROL::Secant<double>::applyInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("update", [](ROL::LinearOperator<double> &o, const class ROL::Vector<double> & a0) -> void { return o.update(a0); }, "", pybind11::arg("x"));
		cl.def("update", [](ROL::LinearOperator<double> &o, const class ROL::Vector<double> & a0, bool const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("flag"));
		cl.def("update", (void (ROL::LinearOperator<double>::*)(const class ROL::Vector<double> &, bool, int)) &ROL::LinearOperator<double>::update, "C++: ROL::LinearOperator<double>::update(const class ROL::Vector<double> &, bool, int) --> void", pybind11::arg("x"), pybind11::arg("flag"), pybind11::arg("iter"));
		cl.def("apply", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::apply, "C++: ROL::LinearOperator<double>::apply(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyInverse", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyInverse, "C++: ROL::LinearOperator<double>::applyInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyAdjoint", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyAdjoint, "C++: ROL::LinearOperator<double>::applyAdjoint(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyAdjointInverse", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyAdjointInverse, "C++: ROL::LinearOperator<double>::applyAdjointInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("assign", (class ROL::LinearOperator<double> & (ROL::LinearOperator<double>::*)(const class ROL::LinearOperator<double> &)) &ROL::LinearOperator<double>::operator=, "C++: ROL::LinearOperator<double>::operator=(const class ROL::LinearOperator<double> &) --> class ROL::LinearOperator<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::BarzilaiBorwein file:ROL_BarzilaiBorwein.hpp line:26
		pybind11::class_<ROL::BarzilaiBorwein<double>, Teuchos::RCP<ROL::BarzilaiBorwein<double>>, PyCallBack_ROL_BarzilaiBorwein_double_t, ROL::Secant<double>> cl(M("ROL"), "BarzilaiBorwein_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::BarzilaiBorwein<double>(); }, [](){ return new PyCallBack_ROL_BarzilaiBorwein_double_t(); } ), "doc");
		cl.def( pybind11::init<int>(), pybind11::arg("type") );

		cl.def( pybind11::init( [](PyCallBack_ROL_BarzilaiBorwein_double_t const &o){ return new PyCallBack_ROL_BarzilaiBorwein_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::BarzilaiBorwein<double> const &o){ return new ROL::BarzilaiBorwein<double>(o); } ) );
		cl.def("applyH", (void (ROL::BarzilaiBorwein<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::BarzilaiBorwein<double>::applyH, "C++: ROL::BarzilaiBorwein<double>::applyH(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyB", (void (ROL::BarzilaiBorwein<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::BarzilaiBorwein<double>::applyB, "C++: ROL::BarzilaiBorwein<double>::applyB(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("updateStorage", (void (ROL::Secant<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::Secant<double>::updateStorage, "C++: ROL::Secant<double>::updateStorage(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("grad"), pybind11::arg("gp"), pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("applyH", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyH, "C++: ROL::Secant<double>::applyH(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyH0", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyH0, "C++: ROL::Secant<double>::applyH0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"));
		cl.def("applyB", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyB, "C++: ROL::Secant<double>::applyB(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("applyB0", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &) const) &ROL::Secant<double>::applyB0, "C++: ROL::Secant<double>::applyB0(class ROL::Vector<double> &, const class ROL::Vector<double> &) const --> void", pybind11::arg("Bv"), pybind11::arg("v"));
		cl.def("test", [](ROL::Secant<double> const &o) -> void { return o.test(); }, "");
		cl.def("test", (void (ROL::Secant<double>::*)(std::ostream &) const) &ROL::Secant<double>::test, "C++: ROL::Secant<double>::test(std::ostream &) const --> void", pybind11::arg("stream"));
		cl.def("apply", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::Secant<double>::apply, "C++: ROL::Secant<double>::apply(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyInverse", (void (ROL::Secant<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::Secant<double>::applyInverse, "C++: ROL::Secant<double>::applyInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("update", [](ROL::LinearOperator<double> &o, const class ROL::Vector<double> & a0) -> void { return o.update(a0); }, "", pybind11::arg("x"));
		cl.def("update", [](ROL::LinearOperator<double> &o, const class ROL::Vector<double> & a0, bool const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("flag"));
		cl.def("update", (void (ROL::LinearOperator<double>::*)(const class ROL::Vector<double> &, bool, int)) &ROL::LinearOperator<double>::update, "C++: ROL::LinearOperator<double>::update(const class ROL::Vector<double> &, bool, int) --> void", pybind11::arg("x"), pybind11::arg("flag"), pybind11::arg("iter"));
		cl.def("apply", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::apply, "C++: ROL::LinearOperator<double>::apply(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyInverse", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyInverse, "C++: ROL::LinearOperator<double>::applyInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyAdjoint", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyAdjoint, "C++: ROL::LinearOperator<double>::applyAdjoint(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("applyAdjointInverse", (void (ROL::LinearOperator<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const) &ROL::LinearOperator<double>::applyAdjointInverse, "C++: ROL::LinearOperator<double>::applyAdjointInverse(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) const --> void", pybind11::arg("Hv"), pybind11::arg("v"), pybind11::arg("tol"));
		cl.def("assign", (class ROL::LinearOperator<double> & (ROL::LinearOperator<double>::*)(const class ROL::LinearOperator<double> &)) &ROL::LinearOperator<double>::operator=, "C++: ROL::LinearOperator<double>::operator=(const class ROL::LinearOperator<double> &) --> class ROL::LinearOperator<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::TrustRegionModel_U file:ROL_TrustRegionModel_U.hpp line:32
		pybind11::class_<ROL::TrustRegionModel_U<double>, Teuchos::RCP<ROL::TrustRegionModel_U<double>>, PyCallBack_ROL_TrustRegionModel_U_double_t, ROL::Objective<double>> cl(M("ROL"), "TrustRegionModel_U_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](class Teuchos::ParameterList & a0){ return new ROL::TrustRegionModel_U<double>(a0); }, [](class Teuchos::ParameterList & a0){ return new PyCallBack_ROL_TrustRegionModel_U_double_t(a0); } ), "doc");
		cl.def( pybind11::init( [](class Teuchos::ParameterList & a0, const class Teuchos::RCP<class ROL::Secant<double> > & a1){ return new ROL::TrustRegionModel_U<double>(a0, a1); }, [](class Teuchos::ParameterList & a0, const class Teuchos::RCP<class ROL::Secant<double> > & a1){ return new PyCallBack_ROL_TrustRegionModel_U_double_t(a0, a1); } ), "doc");
		cl.def( pybind11::init<class Teuchos::ParameterList &, const class Teuchos::RCP<class ROL::Secant<double> > &, enum ROL::ESecantMode>(), pybind11::arg("list"), pybind11::arg("secant"), pybind11::arg("mode") );

		cl.def( pybind11::init( [](PyCallBack_ROL_TrustRegionModel_U_double_t const &o){ return new PyCallBack_ROL_TrustRegionModel_U_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::TrustRegionModel_U<double> const &o){ return new ROL::TrustRegionModel_U<double>(o); } ) );
		cl.def("update", [](ROL::TrustRegionModel_U<double> &o, const class ROL::Vector<double> & a0) -> void { return o.update(a0); }, "", pybind11::arg("x"));
		cl.def("update", [](ROL::TrustRegionModel_U<double> &o, const class ROL::Vector<double> & a0, bool const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("flag"));
		cl.def("update", [](ROL::TrustRegionModel_U<double> &o, const class ROL::Vector<double> & a0, bool const & a1, int const & a2) -> void { return o.update(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("flag"), pybind11::arg("iter"));
		cl.def("update", [](ROL::TrustRegionModel_U<double> &o, const class ROL::Vector<double> & a0, enum ROL::UpdateType const & a1) -> void { return o.update(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("type"));
		cl.def("update", [](ROL::TrustRegionModel_U<double> &o, const class ROL::Vector<double> & a0, enum ROL::UpdateType const & a1, int const & a2) -> void { return o.update(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("type"), pybind11::arg("iter"));
		cl.def("initialize", (void (ROL::TrustRegionModel_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &)) &ROL::TrustRegionModel_U<double>::initialize, "C++: ROL::TrustRegionModel_U<double>::initialize(const class ROL::Vector<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("x"), pybind11::arg("g"));
		cl.def("validate", (void (ROL::TrustRegionModel_U<double>::*)(class ROL::Objective<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, enum ROL::ETrustRegionU)) &ROL::TrustRegionModel_U<double>::validate, "C++: ROL::TrustRegionModel_U<double>::validate(class ROL::Objective<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, enum ROL::ETrustRegionU) --> void", pybind11::arg("obj"), pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("etr"));
		cl.def("setData", (void (ROL::TrustRegionModel_U<double>::*)(class ROL::Objective<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::TrustRegionModel_U<double>::setData, "C++: ROL::TrustRegionModel_U<double>::setData(class ROL::Objective<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("obj"), pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("tol"));
		cl.def("update", (void (ROL::TrustRegionModel_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::TrustRegionModel_U<double>::update, "C++: ROL::TrustRegionModel_U<double>::update(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("s"), pybind11::arg("gold"), pybind11::arg("gnew"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("value", (double (ROL::TrustRegionModel_U<double>::*)(const class ROL::Vector<double> &, double &)) &ROL::TrustRegionModel_U<double>::value, "C++: ROL::TrustRegionModel_U<double>::value(const class ROL::Vector<double> &, double &) --> double", pybind11::arg("s"), pybind11::arg("tol"));
		cl.def("gradient", (void (ROL::TrustRegionModel_U<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::TrustRegionModel_U<double>::gradient, "C++: ROL::TrustRegionModel_U<double>::gradient(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("g"), pybind11::arg("s"), pybind11::arg("tol"));
		cl.def("hessVec", (void (ROL::TrustRegionModel_U<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::TrustRegionModel_U<double>::hessVec, "C++: ROL::TrustRegionModel_U<double>::hessVec(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("s"), pybind11::arg("tol"));
		cl.def("invHessVec", (void (ROL::TrustRegionModel_U<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::TrustRegionModel_U<double>::invHessVec, "C++: ROL::TrustRegionModel_U<double>::invHessVec(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("s"), pybind11::arg("tol"));
		cl.def("precond", (void (ROL::TrustRegionModel_U<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::TrustRegionModel_U<double>::precond, "C++: ROL::TrustRegionModel_U<double>::precond(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("Pv"), pybind11::arg("v"), pybind11::arg("s"), pybind11::arg("tol"));
		cl.def("getGradient", (const class Teuchos::RCP<const class ROL::Vector<double> > (ROL::TrustRegionModel_U<double>::*)() const) &ROL::TrustRegionModel_U<double>::getGradient, "C++: ROL::TrustRegionModel_U<double>::getGradient() const --> const class Teuchos::RCP<const class ROL::Vector<double> >");
		cl.def("getIterate", (const class Teuchos::RCP<const class ROL::Vector<double> > (ROL::TrustRegionModel_U<double>::*)() const) &ROL::TrustRegionModel_U<double>::getIterate, "C++: ROL::TrustRegionModel_U<double>::getIterate() const --> const class Teuchos::RCP<const class ROL::Vector<double> >");
		cl.def("getObjective", (const class Teuchos::RCP<class ROL::Objective<double> > (ROL::TrustRegionModel_U<double>::*)() const) &ROL::TrustRegionModel_U<double>::getObjective, "C++: ROL::TrustRegionModel_U<double>::getObjective() const --> const class Teuchos::RCP<class ROL::Objective<double> >");
		cl.def("assign", (class ROL::TrustRegionModel_U<double> & (ROL::TrustRegionModel_U<double>::*)(const class ROL::TrustRegionModel_U<double> &)) &ROL::TrustRegionModel_U<double>::operator=, "C++: ROL::TrustRegionModel_U<double>::operator=(const class ROL::TrustRegionModel_U<double> &) --> class ROL::TrustRegionModel_U<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
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
	{ // ROL::TrustRegion_U file:ROL_TrustRegion_U.hpp line:23
		pybind11::class_<ROL::TrustRegion_U<double>, Teuchos::RCP<ROL::TrustRegion_U<double>>, PyCallBack_ROL_TrustRegion_U_double_t> cl(M("ROL"), "TrustRegion_U_double_t", "", pybind11::module_local());
		cl.def(pybind11::init<PyCallBack_ROL_TrustRegion_U_double_t const &>());
		cl.def( pybind11::init( [](){ return new PyCallBack_ROL_TrustRegion_U_double_t(); } ) );
		cl.def("initialize", (void (ROL::TrustRegion_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &)) &ROL::TrustRegion_U<double>::initialize, "C++: ROL::TrustRegion_U<double>::initialize(const class ROL::Vector<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("x"), pybind11::arg("g"));
		cl.def("solve", (void (ROL::TrustRegion_U<double>::*)(class ROL::Vector<double> &, double &, double &, int &, int &, const double, class ROL::TrustRegionModel_U<double> &)) &ROL::TrustRegion_U<double>::solve, "C++: ROL::TrustRegion_U<double>::solve(class ROL::Vector<double> &, double &, double &, int &, int &, const double, class ROL::TrustRegionModel_U<double> &) --> void", pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("pRed"), pybind11::arg("iflag"), pybind11::arg("iter"), pybind11::arg("del"), pybind11::arg("model"));
		cl.def("assign", (class ROL::TrustRegion_U<double> & (ROL::TrustRegion_U<double>::*)(const class ROL::TrustRegion_U<double> &)) &ROL::TrustRegion_U<double>::operator=, "C++: ROL::TrustRegion_U<double>::operator=(const class ROL::TrustRegion_U<double> &) --> class ROL::TrustRegion_U<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
}
