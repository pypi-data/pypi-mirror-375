#include <ROL_BoundConstraint.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_Objective.hpp>
#include <ROL_PolyhedralProjection.hpp>
#include <ROL_Problem.hpp>
#include <ROL_Secant.hpp>
#include <ROL_StatusTest.hpp>
#include <ROL_TypeP_Algorithm.hpp>
#include <ROL_TypeP_AlgorithmFactory.hpp>
#include <ROL_TypeP_InexactNewtonAlgorithm.hpp>
#include <ROL_TypeP_ProxGradientAlgorithm.hpp>
#include <ROL_TypeP_QuasiNewtonAlgorithm.hpp>
#include <ROL_TypeP_SpectralGradientAlgorithm.hpp>
#include <ROL_TypeP_TrustRegionAlgorithm.hpp>
#include <ROL_TypeP_iPianoAlgorithm.hpp>
#include <ROL_Types.hpp>
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

// ROL::TypeP::Algorithm file:ROL_TypeP_Algorithm.hpp line:56
struct PyCallBack_ROL_TypeP_Algorithm_double_t : public ROL::TypeP::Algorithm<double> {
	using ROL::TypeP::Algorithm<double>::Algorithm;

	void run(class ROL::Problem<double> & a0, std::ostream & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::Algorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1);
	}
	void run(class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::Algorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1, a2, a3);
	}
	void run(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3, std::ostream & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::Algorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		pybind11::pybind11_fail("Tried to call pure virtual function \"Algorithm::run\"");
	}
	void writeHeader(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::Algorithm<double> *>(this), "writeHeader");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::writeHeader(a0);
	}
	void writeName(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::Algorithm<double> *>(this), "writeName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::writeName(a0);
	}
	void writeOutput(std::ostream & a0, bool a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::Algorithm<double> *>(this), "writeOutput");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::writeOutput(a0, a1);
	}
	void writeExitStatus(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::Algorithm<double> *>(this), "writeExitStatus");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::writeExitStatus(a0);
	}
};

// ROL::TypeP::ProxGradientAlgorithm file:ROL_TypeP_ProxGradientAlgorithm.hpp line:23
struct PyCallBack_ROL_TypeP_ProxGradientAlgorithm_double_t : public ROL::TypeP::ProxGradientAlgorithm<double> {
	using ROL::TypeP::ProxGradientAlgorithm<double>::ProxGradientAlgorithm;

	void run(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3, std::ostream & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::ProxGradientAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ProxGradientAlgorithm::run(a0, a1, a2, a3, a4);
	}
	void writeHeader(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::ProxGradientAlgorithm<double> *>(this), "writeHeader");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ProxGradientAlgorithm::writeHeader(a0);
	}
	void writeName(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::ProxGradientAlgorithm<double> *>(this), "writeName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ProxGradientAlgorithm::writeName(a0);
	}
	void writeOutput(std::ostream & a0, bool a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::ProxGradientAlgorithm<double> *>(this), "writeOutput");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ProxGradientAlgorithm::writeOutput(a0, a1);
	}
	void run(class ROL::Problem<double> & a0, std::ostream & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::ProxGradientAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1);
	}
	void run(class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::ProxGradientAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1, a2, a3);
	}
	void writeExitStatus(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::ProxGradientAlgorithm<double> *>(this), "writeExitStatus");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::writeExitStatus(a0);
	}
};

// ROL::TypeP::SpectralGradientAlgorithm file:ROL_TypeP_SpectralGradientAlgorithm.hpp line:23
struct PyCallBack_ROL_TypeP_SpectralGradientAlgorithm_double_t : public ROL::TypeP::SpectralGradientAlgorithm<double> {
	using ROL::TypeP::SpectralGradientAlgorithm<double>::SpectralGradientAlgorithm;

	void run(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3, std::ostream & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::SpectralGradientAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SpectralGradientAlgorithm::run(a0, a1, a2, a3, a4);
	}
	void writeHeader(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::SpectralGradientAlgorithm<double> *>(this), "writeHeader");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SpectralGradientAlgorithm::writeHeader(a0);
	}
	void writeName(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::SpectralGradientAlgorithm<double> *>(this), "writeName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SpectralGradientAlgorithm::writeName(a0);
	}
	void writeOutput(std::ostream & a0, bool a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::SpectralGradientAlgorithm<double> *>(this), "writeOutput");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return SpectralGradientAlgorithm::writeOutput(a0, a1);
	}
	void run(class ROL::Problem<double> & a0, std::ostream & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::SpectralGradientAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1);
	}
	void run(class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::SpectralGradientAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1, a2, a3);
	}
	void writeExitStatus(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::SpectralGradientAlgorithm<double> *>(this), "writeExitStatus");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::writeExitStatus(a0);
	}
};

// ROL::TypeP::iPianoAlgorithm file:ROL_TypeP_iPianoAlgorithm.hpp line:23
struct PyCallBack_ROL_TypeP_iPianoAlgorithm_double_t : public ROL::TypeP::iPianoAlgorithm<double> {
	using ROL::TypeP::iPianoAlgorithm<double>::iPianoAlgorithm;

	void run(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3, std::ostream & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::iPianoAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return iPianoAlgorithm::run(a0, a1, a2, a3, a4);
	}
	void writeHeader(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::iPianoAlgorithm<double> *>(this), "writeHeader");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return iPianoAlgorithm::writeHeader(a0);
	}
	void writeName(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::iPianoAlgorithm<double> *>(this), "writeName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return iPianoAlgorithm::writeName(a0);
	}
	void writeOutput(std::ostream & a0, bool a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::iPianoAlgorithm<double> *>(this), "writeOutput");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return iPianoAlgorithm::writeOutput(a0, a1);
	}
	void run(class ROL::Problem<double> & a0, std::ostream & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::iPianoAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1);
	}
	void run(class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::iPianoAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1, a2, a3);
	}
	void writeExitStatus(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::iPianoAlgorithm<double> *>(this), "writeExitStatus");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::writeExitStatus(a0);
	}
};

// ROL::TypeP::QuasiNewtonAlgorithm file:ROL_TypeP_QuasiNewtonAlgorithm.hpp line:24
struct PyCallBack_ROL_TypeP_QuasiNewtonAlgorithm_double_t : public ROL::TypeP::QuasiNewtonAlgorithm<double> {
	using ROL::TypeP::QuasiNewtonAlgorithm<double>::QuasiNewtonAlgorithm;

	void run(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3, std::ostream & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::QuasiNewtonAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return QuasiNewtonAlgorithm::run(a0, a1, a2, a3, a4);
	}
	void writeHeader(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::QuasiNewtonAlgorithm<double> *>(this), "writeHeader");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return QuasiNewtonAlgorithm::writeHeader(a0);
	}
	void writeName(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::QuasiNewtonAlgorithm<double> *>(this), "writeName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return QuasiNewtonAlgorithm::writeName(a0);
	}
	void writeOutput(std::ostream & a0, bool a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::QuasiNewtonAlgorithm<double> *>(this), "writeOutput");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return QuasiNewtonAlgorithm::writeOutput(a0, a1);
	}
	void run(class ROL::Problem<double> & a0, std::ostream & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::QuasiNewtonAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1);
	}
	void run(class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::QuasiNewtonAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1, a2, a3);
	}
	void writeExitStatus(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::QuasiNewtonAlgorithm<double> *>(this), "writeExitStatus");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::writeExitStatus(a0);
	}
};

// ROL::TypeP::TrustRegionAlgorithm file:ROL_TypeP_TrustRegionAlgorithm.hpp line:83
struct PyCallBack_ROL_TypeP_TrustRegionAlgorithm_double_t : public ROL::TypeP::TrustRegionAlgorithm<double> {
	using ROL::TypeP::TrustRegionAlgorithm<double>::TrustRegionAlgorithm;

	void run(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3, std::ostream & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::TrustRegionAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return TrustRegionAlgorithm::run(a0, a1, a2, a3, a4);
	}
	void writeHeader(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::TrustRegionAlgorithm<double> *>(this), "writeHeader");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return TrustRegionAlgorithm::writeHeader(a0);
	}
	void writeName(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::TrustRegionAlgorithm<double> *>(this), "writeName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return TrustRegionAlgorithm::writeName(a0);
	}
	void writeOutput(std::ostream & a0, bool a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::TrustRegionAlgorithm<double> *>(this), "writeOutput");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return TrustRegionAlgorithm::writeOutput(a0, a1);
	}
	void run(class ROL::Problem<double> & a0, std::ostream & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::TrustRegionAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1);
	}
	void run(class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::TrustRegionAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1, a2, a3);
	}
	void writeExitStatus(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::TrustRegionAlgorithm<double> *>(this), "writeExitStatus");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::writeExitStatus(a0);
	}
};

// ROL::TypeP::InexactNewtonAlgorithm file:ROL_TypeP_InexactNewtonAlgorithm.hpp line:23
struct PyCallBack_ROL_TypeP_InexactNewtonAlgorithm_double_t : public ROL::TypeP::InexactNewtonAlgorithm<double> {
	using ROL::TypeP::InexactNewtonAlgorithm<double>::InexactNewtonAlgorithm;

	void run(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3, std::ostream & a4) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::InexactNewtonAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return InexactNewtonAlgorithm::run(a0, a1, a2, a3, a4);
	}
	void writeHeader(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::InexactNewtonAlgorithm<double> *>(this), "writeHeader");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return InexactNewtonAlgorithm::writeHeader(a0);
	}
	void writeName(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::InexactNewtonAlgorithm<double> *>(this), "writeName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return InexactNewtonAlgorithm::writeName(a0);
	}
	void writeOutput(std::ostream & a0, bool a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::InexactNewtonAlgorithm<double> *>(this), "writeOutput");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return InexactNewtonAlgorithm::writeOutput(a0, a1);
	}
	void run(class ROL::Problem<double> & a0, std::ostream & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::InexactNewtonAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1);
	}
	void run(class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::InexactNewtonAlgorithm<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::run(a0, a1, a2, a3);
	}
	void writeExitStatus(std::ostream & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::TypeP::InexactNewtonAlgorithm<double> *>(this), "writeExitStatus");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Algorithm::writeExitStatus(a0);
	}
};

void bind_pyrol_74(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::TypeP::AlgorithmState file:ROL_TypeP_Algorithm.hpp line:25
		pybind11::class_<ROL::TypeP::AlgorithmState<double>, Teuchos::RCP<ROL::TypeP::AlgorithmState<double>>, ROL::AlgorithmState<double>> cl(M("ROL::TypeP"), "AlgorithmState_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::TypeP::AlgorithmState<double>(); } ) );
		cl.def( pybind11::init( [](ROL::TypeP::AlgorithmState<double> const &o){ return new ROL::TypeP::AlgorithmState<double>(o); } ) );
		cl.def_readwrite("searchSize", &ROL::TypeP::AlgorithmState<double>::searchSize);
		cl.def_readwrite("svalue", &ROL::TypeP::AlgorithmState<double>::svalue);
		cl.def_readwrite("nvalue", &ROL::TypeP::AlgorithmState<double>::nvalue);
		cl.def_readwrite("stepVec", &ROL::TypeP::AlgorithmState<double>::stepVec);
		cl.def_readwrite("gradientVec", &ROL::TypeP::AlgorithmState<double>::gradientVec);
		cl.def_readwrite("nprox", &ROL::TypeP::AlgorithmState<double>::nprox);
		cl.def_readwrite("nsval", &ROL::TypeP::AlgorithmState<double>::nsval);
		cl.def_readwrite("nnval", &ROL::TypeP::AlgorithmState<double>::nnval);
		cl.def("reset", (void (ROL::TypeP::AlgorithmState<double>::*)()) &ROL::TypeP::AlgorithmState<double>::reset, "C++: ROL::TypeP::AlgorithmState<double>::reset() --> void");
		cl.def("assign", (struct ROL::TypeP::AlgorithmState<double> & (ROL::TypeP::AlgorithmState<double>::*)(const struct ROL::TypeP::AlgorithmState<double> &)) &ROL::TypeP::AlgorithmState<double>::operator=, "C++: ROL::TypeP::AlgorithmState<double>::operator=(const struct ROL::TypeP::AlgorithmState<double> &) --> struct ROL::TypeP::AlgorithmState<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def_readwrite("iter", &ROL::AlgorithmState<double>::iter);
		cl.def_readwrite("minIter", &ROL::AlgorithmState<double>::minIter);
		cl.def_readwrite("nfval", &ROL::AlgorithmState<double>::nfval);
		cl.def_readwrite("ncval", &ROL::AlgorithmState<double>::ncval);
		cl.def_readwrite("ngrad", &ROL::AlgorithmState<double>::ngrad);
		cl.def_readwrite("value", &ROL::AlgorithmState<double>::value);
		cl.def_readwrite("minValue", &ROL::AlgorithmState<double>::minValue);
		cl.def_readwrite("gnorm", &ROL::AlgorithmState<double>::gnorm);
		cl.def_readwrite("cnorm", &ROL::AlgorithmState<double>::cnorm);
		cl.def_readwrite("snorm", &ROL::AlgorithmState<double>::snorm);
		cl.def_readwrite("aggregateGradientNorm", &ROL::AlgorithmState<double>::aggregateGradientNorm);
		cl.def_readwrite("aggregateModelError", &ROL::AlgorithmState<double>::aggregateModelError);
		cl.def_readwrite("flag", &ROL::AlgorithmState<double>::flag);
		cl.def_readwrite("iterateVec", &ROL::AlgorithmState<double>::iterateVec);
		cl.def_readwrite("lagmultVec", &ROL::AlgorithmState<double>::lagmultVec);
		cl.def_readwrite("minIterVec", &ROL::AlgorithmState<double>::minIterVec);
		cl.def_readwrite("statusFlag", &ROL::AlgorithmState<double>::statusFlag);
		cl.def("reset", (void (ROL::AlgorithmState<double>::*)()) &ROL::AlgorithmState<double>::reset, "C++: ROL::AlgorithmState<double>::reset() --> void");
		cl.def("assign", (struct ROL::AlgorithmState<double> & (ROL::AlgorithmState<double>::*)(const struct ROL::AlgorithmState<double> &)) &ROL::AlgorithmState<double>::operator=, "C++: ROL::AlgorithmState<double>::operator=(const struct ROL::AlgorithmState<double> &) --> struct ROL::AlgorithmState<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::TypeP::Algorithm file:ROL_TypeP_Algorithm.hpp line:56
		pybind11::class_<ROL::TypeP::Algorithm<double>, Teuchos::RCP<ROL::TypeP::Algorithm<double>>, PyCallBack_ROL_TypeP_Algorithm_double_t> cl(M("ROL::TypeP"), "Algorithm_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new PyCallBack_ROL_TypeP_Algorithm_double_t(); } ) );
		cl.def(pybind11::init<PyCallBack_ROL_TypeP_Algorithm_double_t const &>());
		cl.def("setStatusTest", [](ROL::TypeP::Algorithm<double> &o, const class Teuchos::RCP<class ROL::StatusTest<double> > & a0) -> void { return o.setStatusTest(a0); }, "", pybind11::arg("status"));
		cl.def("setStatusTest", (void (ROL::TypeP::Algorithm<double>::*)(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool)) &ROL::TypeP::Algorithm<double>::setStatusTest, "C++: ROL::TypeP::Algorithm<double>::setStatusTest(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool) --> void", pybind11::arg("status"), pybind11::arg("combineStatus"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Problem<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Problem<double> &, std::ostream &) --> void", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeHeader, "C++: ROL::TypeP::Algorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeName, "C++: ROL::TypeP::Algorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeP::Algorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &, bool) const) &ROL::TypeP::Algorithm<double>::writeOutput, "C++: ROL::TypeP::Algorithm<double>::writeOutput(std::ostream &, bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("writeExitStatus", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeExitStatus, "C++: ROL::TypeP::Algorithm<double>::writeExitStatus(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("getState", (class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > (ROL::TypeP::Algorithm<double>::*)() const) &ROL::TypeP::Algorithm<double>::getState, "C++: ROL::TypeP::Algorithm<double>::getState() const --> class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> >");
		cl.def("reset", (void (ROL::TypeP::Algorithm<double>::*)()) &ROL::TypeP::Algorithm<double>::reset, "C++: ROL::TypeP::Algorithm<double>::reset() --> void");
	}
	{ // ROL::TypeP::ProxGradientAlgorithm file:ROL_TypeP_ProxGradientAlgorithm.hpp line:23
		pybind11::class_<ROL::TypeP::ProxGradientAlgorithm<double>, Teuchos::RCP<ROL::TypeP::ProxGradientAlgorithm<double>>, PyCallBack_ROL_TypeP_ProxGradientAlgorithm_double_t, ROL::TypeP::Algorithm<double>> cl(M("ROL::TypeP"), "ProxGradientAlgorithm_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<class Teuchos::ParameterList &>(), pybind11::arg("list") );

		cl.def( pybind11::init( [](PyCallBack_ROL_TypeP_ProxGradientAlgorithm_double_t const &o){ return new PyCallBack_ROL_TypeP_ProxGradientAlgorithm_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::TypeP::ProxGradientAlgorithm<double> const &o){ return new ROL::TypeP::ProxGradientAlgorithm<double>(o); } ) );
		cl.def("run", [](ROL::TypeP::ProxGradientAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", [](ROL::TypeP::ProxGradientAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::ProxGradientAlgorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", [](ROL::TypeP::ProxGradientAlgorithm<double> &o, class ROL::Problem<double> & a0, std::ostream & a1) -> void { return o.run(a0, a1); }, "", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::ProxGradientAlgorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::ProxGradientAlgorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::ProxGradientAlgorithm<double>::run, "C++: ROL::TypeP::ProxGradientAlgorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeP::ProxGradientAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeP::ProxGradientAlgorithm<double>::writeHeader, "C++: ROL::TypeP::ProxGradientAlgorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeP::ProxGradientAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeP::ProxGradientAlgorithm<double>::writeName, "C++: ROL::TypeP::ProxGradientAlgorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeP::ProxGradientAlgorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeP::ProxGradientAlgorithm<double>::*)(std::ostream &, bool) const) &ROL::TypeP::ProxGradientAlgorithm<double>::writeOutput, "C++: ROL::TypeP::ProxGradientAlgorithm<double>::writeOutput(std::ostream &, bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("setStatusTest", [](ROL::TypeP::Algorithm<double> &o, const class Teuchos::RCP<class ROL::StatusTest<double> > & a0) -> void { return o.setStatusTest(a0); }, "", pybind11::arg("status"));
		cl.def("setStatusTest", (void (ROL::TypeP::Algorithm<double>::*)(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool)) &ROL::TypeP::Algorithm<double>::setStatusTest, "C++: ROL::TypeP::Algorithm<double>::setStatusTest(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool) --> void", pybind11::arg("status"), pybind11::arg("combineStatus"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Problem<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Problem<double> &, std::ostream &) --> void", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeHeader, "C++: ROL::TypeP::Algorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeName, "C++: ROL::TypeP::Algorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeP::Algorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &, bool) const) &ROL::TypeP::Algorithm<double>::writeOutput, "C++: ROL::TypeP::Algorithm<double>::writeOutput(std::ostream &, bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("writeExitStatus", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeExitStatus, "C++: ROL::TypeP::Algorithm<double>::writeExitStatus(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("getState", (class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > (ROL::TypeP::Algorithm<double>::*)() const) &ROL::TypeP::Algorithm<double>::getState, "C++: ROL::TypeP::Algorithm<double>::getState() const --> class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> >");
		cl.def("reset", (void (ROL::TypeP::Algorithm<double>::*)()) &ROL::TypeP::Algorithm<double>::reset, "C++: ROL::TypeP::Algorithm<double>::reset() --> void");
	}
	{ // ROL::TypeP::SpectralGradientAlgorithm file:ROL_TypeP_SpectralGradientAlgorithm.hpp line:23
		pybind11::class_<ROL::TypeP::SpectralGradientAlgorithm<double>, Teuchos::RCP<ROL::TypeP::SpectralGradientAlgorithm<double>>, PyCallBack_ROL_TypeP_SpectralGradientAlgorithm_double_t, ROL::TypeP::Algorithm<double>> cl(M("ROL::TypeP"), "SpectralGradientAlgorithm_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<class Teuchos::ParameterList &>(), pybind11::arg("list") );

		cl.def( pybind11::init( [](PyCallBack_ROL_TypeP_SpectralGradientAlgorithm_double_t const &o){ return new PyCallBack_ROL_TypeP_SpectralGradientAlgorithm_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::TypeP::SpectralGradientAlgorithm<double> const &o){ return new ROL::TypeP::SpectralGradientAlgorithm<double>(o); } ) );
		cl.def("run", [](ROL::TypeP::SpectralGradientAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", [](ROL::TypeP::SpectralGradientAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::SpectralGradientAlgorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", [](ROL::TypeP::SpectralGradientAlgorithm<double> &o, class ROL::Problem<double> & a0, std::ostream & a1) -> void { return o.run(a0, a1); }, "", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::SpectralGradientAlgorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::SpectralGradientAlgorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::SpectralGradientAlgorithm<double>::run, "C++: ROL::TypeP::SpectralGradientAlgorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeP::SpectralGradientAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeP::SpectralGradientAlgorithm<double>::writeHeader, "C++: ROL::TypeP::SpectralGradientAlgorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeP::SpectralGradientAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeP::SpectralGradientAlgorithm<double>::writeName, "C++: ROL::TypeP::SpectralGradientAlgorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeP::SpectralGradientAlgorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeP::SpectralGradientAlgorithm<double>::*)(std::ostream &, bool) const) &ROL::TypeP::SpectralGradientAlgorithm<double>::writeOutput, "C++: ROL::TypeP::SpectralGradientAlgorithm<double>::writeOutput(std::ostream &, bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("setStatusTest", [](ROL::TypeP::Algorithm<double> &o, const class Teuchos::RCP<class ROL::StatusTest<double> > & a0) -> void { return o.setStatusTest(a0); }, "", pybind11::arg("status"));
		cl.def("setStatusTest", (void (ROL::TypeP::Algorithm<double>::*)(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool)) &ROL::TypeP::Algorithm<double>::setStatusTest, "C++: ROL::TypeP::Algorithm<double>::setStatusTest(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool) --> void", pybind11::arg("status"), pybind11::arg("combineStatus"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Problem<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Problem<double> &, std::ostream &) --> void", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeHeader, "C++: ROL::TypeP::Algorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeName, "C++: ROL::TypeP::Algorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeP::Algorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &, bool) const) &ROL::TypeP::Algorithm<double>::writeOutput, "C++: ROL::TypeP::Algorithm<double>::writeOutput(std::ostream &, bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("writeExitStatus", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeExitStatus, "C++: ROL::TypeP::Algorithm<double>::writeExitStatus(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("getState", (class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > (ROL::TypeP::Algorithm<double>::*)() const) &ROL::TypeP::Algorithm<double>::getState, "C++: ROL::TypeP::Algorithm<double>::getState() const --> class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> >");
		cl.def("reset", (void (ROL::TypeP::Algorithm<double>::*)()) &ROL::TypeP::Algorithm<double>::reset, "C++: ROL::TypeP::Algorithm<double>::reset() --> void");
	}
	{ // ROL::TypeP::iPianoAlgorithm file:ROL_TypeP_iPianoAlgorithm.hpp line:23
		pybind11::class_<ROL::TypeP::iPianoAlgorithm<double>, Teuchos::RCP<ROL::TypeP::iPianoAlgorithm<double>>, PyCallBack_ROL_TypeP_iPianoAlgorithm_double_t, ROL::TypeP::Algorithm<double>> cl(M("ROL::TypeP"), "iPianoAlgorithm_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<class Teuchos::ParameterList &>(), pybind11::arg("list") );

		cl.def( pybind11::init( [](PyCallBack_ROL_TypeP_iPianoAlgorithm_double_t const &o){ return new PyCallBack_ROL_TypeP_iPianoAlgorithm_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::TypeP::iPianoAlgorithm<double> const &o){ return new ROL::TypeP::iPianoAlgorithm<double>(o); } ) );
		cl.def("run", [](ROL::TypeP::iPianoAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", [](ROL::TypeP::iPianoAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::iPianoAlgorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", [](ROL::TypeP::iPianoAlgorithm<double> &o, class ROL::Problem<double> & a0, std::ostream & a1) -> void { return o.run(a0, a1); }, "", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::iPianoAlgorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::iPianoAlgorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::iPianoAlgorithm<double>::run, "C++: ROL::TypeP::iPianoAlgorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeP::iPianoAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeP::iPianoAlgorithm<double>::writeHeader, "C++: ROL::TypeP::iPianoAlgorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeP::iPianoAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeP::iPianoAlgorithm<double>::writeName, "C++: ROL::TypeP::iPianoAlgorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeP::iPianoAlgorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeP::iPianoAlgorithm<double>::*)(std::ostream &, bool) const) &ROL::TypeP::iPianoAlgorithm<double>::writeOutput, "C++: ROL::TypeP::iPianoAlgorithm<double>::writeOutput(std::ostream &, bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("setStatusTest", [](ROL::TypeP::Algorithm<double> &o, const class Teuchos::RCP<class ROL::StatusTest<double> > & a0) -> void { return o.setStatusTest(a0); }, "", pybind11::arg("status"));
		cl.def("setStatusTest", (void (ROL::TypeP::Algorithm<double>::*)(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool)) &ROL::TypeP::Algorithm<double>::setStatusTest, "C++: ROL::TypeP::Algorithm<double>::setStatusTest(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool) --> void", pybind11::arg("status"), pybind11::arg("combineStatus"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Problem<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Problem<double> &, std::ostream &) --> void", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeHeader, "C++: ROL::TypeP::Algorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeName, "C++: ROL::TypeP::Algorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeP::Algorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &, bool) const) &ROL::TypeP::Algorithm<double>::writeOutput, "C++: ROL::TypeP::Algorithm<double>::writeOutput(std::ostream &, bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("writeExitStatus", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeExitStatus, "C++: ROL::TypeP::Algorithm<double>::writeExitStatus(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("getState", (class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > (ROL::TypeP::Algorithm<double>::*)() const) &ROL::TypeP::Algorithm<double>::getState, "C++: ROL::TypeP::Algorithm<double>::getState() const --> class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> >");
		cl.def("reset", (void (ROL::TypeP::Algorithm<double>::*)()) &ROL::TypeP::Algorithm<double>::reset, "C++: ROL::TypeP::Algorithm<double>::reset() --> void");
	}
	{ // ROL::TypeP::QuasiNewtonAlgorithm file:ROL_TypeP_QuasiNewtonAlgorithm.hpp line:24
		pybind11::class_<ROL::TypeP::QuasiNewtonAlgorithm<double>, Teuchos::RCP<ROL::TypeP::QuasiNewtonAlgorithm<double>>, PyCallBack_ROL_TypeP_QuasiNewtonAlgorithm_double_t, ROL::TypeP::Algorithm<double>> cl(M("ROL::TypeP"), "QuasiNewtonAlgorithm_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](class Teuchos::ParameterList & a0){ return new ROL::TypeP::QuasiNewtonAlgorithm<double>(a0); }, [](class Teuchos::ParameterList & a0){ return new PyCallBack_ROL_TypeP_QuasiNewtonAlgorithm_double_t(a0); } ), "doc");
		cl.def( pybind11::init<class Teuchos::ParameterList &, const class Teuchos::RCP<class ROL::Secant<double> > &>(), pybind11::arg("list"), pybind11::arg("secant") );

		cl.def( pybind11::init( [](PyCallBack_ROL_TypeP_QuasiNewtonAlgorithm_double_t const &o){ return new PyCallBack_ROL_TypeP_QuasiNewtonAlgorithm_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::TypeP::QuasiNewtonAlgorithm<double> const &o){ return new ROL::TypeP::QuasiNewtonAlgorithm<double>(o); } ) );
		cl.def("run", [](ROL::TypeP::QuasiNewtonAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", [](ROL::TypeP::QuasiNewtonAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::QuasiNewtonAlgorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", [](ROL::TypeP::QuasiNewtonAlgorithm<double> &o, class ROL::Problem<double> & a0, std::ostream & a1) -> void { return o.run(a0, a1); }, "", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::QuasiNewtonAlgorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::QuasiNewtonAlgorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::QuasiNewtonAlgorithm<double>::run, "C++: ROL::TypeP::QuasiNewtonAlgorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeP::QuasiNewtonAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeP::QuasiNewtonAlgorithm<double>::writeHeader, "C++: ROL::TypeP::QuasiNewtonAlgorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeP::QuasiNewtonAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeP::QuasiNewtonAlgorithm<double>::writeName, "C++: ROL::TypeP::QuasiNewtonAlgorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeP::QuasiNewtonAlgorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeP::QuasiNewtonAlgorithm<double>::*)(std::ostream &, bool) const) &ROL::TypeP::QuasiNewtonAlgorithm<double>::writeOutput, "C++: ROL::TypeP::QuasiNewtonAlgorithm<double>::writeOutput(std::ostream &, bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("setStatusTest", [](ROL::TypeP::Algorithm<double> &o, const class Teuchos::RCP<class ROL::StatusTest<double> > & a0) -> void { return o.setStatusTest(a0); }, "", pybind11::arg("status"));
		cl.def("setStatusTest", (void (ROL::TypeP::Algorithm<double>::*)(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool)) &ROL::TypeP::Algorithm<double>::setStatusTest, "C++: ROL::TypeP::Algorithm<double>::setStatusTest(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool) --> void", pybind11::arg("status"), pybind11::arg("combineStatus"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Problem<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Problem<double> &, std::ostream &) --> void", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeHeader, "C++: ROL::TypeP::Algorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeName, "C++: ROL::TypeP::Algorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeP::Algorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &, bool) const) &ROL::TypeP::Algorithm<double>::writeOutput, "C++: ROL::TypeP::Algorithm<double>::writeOutput(std::ostream &, bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("writeExitStatus", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeExitStatus, "C++: ROL::TypeP::Algorithm<double>::writeExitStatus(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("getState", (class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > (ROL::TypeP::Algorithm<double>::*)() const) &ROL::TypeP::Algorithm<double>::getState, "C++: ROL::TypeP::Algorithm<double>::getState() const --> class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> >");
		cl.def("reset", (void (ROL::TypeP::Algorithm<double>::*)()) &ROL::TypeP::Algorithm<double>::reset, "C++: ROL::TypeP::Algorithm<double>::reset() --> void");
	}
	// ROL::TypeP::ETrustRegionP file:ROL_TypeP_TrustRegionAlgorithm.hpp line:25
	pybind11::enum_<ROL::TypeP::ETrustRegionP>(M("ROL::TypeP"), "ETrustRegionP", pybind11::arithmetic(), "", pybind11::module_local())
		.value("TRUSTREGION_P_SPG", ROL::TypeP::TRUSTREGION_P_SPG)
		.value("TRUSTREGION_P_SPG2", ROL::TypeP::TRUSTREGION_P_SPG2)
		.value("TRUSTREGION_P_NCG", ROL::TypeP::TRUSTREGION_P_NCG)
		.value("TRUSTREGION_P_LAST", ROL::TypeP::TRUSTREGION_P_LAST)
		.export_values();

;

	// ROL::TypeP::ETrustRegionPToString(enum ROL::TypeP::ETrustRegionP) file:ROL_TypeP_TrustRegionAlgorithm.hpp line:32
	M("ROL::TypeP").def("ETrustRegionPToString", (std::string (*)(enum ROL::TypeP::ETrustRegionP)) &ROL::TypeP::ETrustRegionPToString, "C++: ROL::TypeP::ETrustRegionPToString(enum ROL::TypeP::ETrustRegionP) --> std::string", pybind11::arg("alg"));

	// ROL::TypeP::isValidTrustRegionP(enum ROL::TypeP::ETrustRegionP) file:ROL_TypeP_TrustRegionAlgorithm.hpp line:44
	M("ROL::TypeP").def("isValidTrustRegionP", (int (*)(enum ROL::TypeP::ETrustRegionP)) &ROL::TypeP::isValidTrustRegionP, "C++: ROL::TypeP::isValidTrustRegionP(enum ROL::TypeP::ETrustRegionP) --> int", pybind11::arg("alg"));

	// ROL::TypeP::StringToETrustRegionP(std::string) file:ROL_TypeP_TrustRegionAlgorithm.hpp line:72
	M("ROL::TypeP").def("StringToETrustRegionP", (enum ROL::TypeP::ETrustRegionP (*)(std::string)) &ROL::TypeP::StringToETrustRegionP, "C++: ROL::TypeP::StringToETrustRegionP(std::string) --> enum ROL::TypeP::ETrustRegionP", pybind11::arg("s"));

	{ // ROL::TypeP::TrustRegionAlgorithm file:ROL_TypeP_TrustRegionAlgorithm.hpp line:83
		pybind11::class_<ROL::TypeP::TrustRegionAlgorithm<double>, Teuchos::RCP<ROL::TypeP::TrustRegionAlgorithm<double>>, PyCallBack_ROL_TypeP_TrustRegionAlgorithm_double_t, ROL::TypeP::Algorithm<double>> cl(M("ROL::TypeP"), "TrustRegionAlgorithm_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](class Teuchos::ParameterList & a0){ return new ROL::TypeP::TrustRegionAlgorithm<double>(a0); }, [](class Teuchos::ParameterList & a0){ return new PyCallBack_ROL_TypeP_TrustRegionAlgorithm_double_t(a0); } ), "doc");
		cl.def( pybind11::init<class Teuchos::ParameterList &, const class Teuchos::RCP<class ROL::Secant<double> > &>(), pybind11::arg("list"), pybind11::arg("secant") );

		cl.def( pybind11::init( [](PyCallBack_ROL_TypeP_TrustRegionAlgorithm_double_t const &o){ return new PyCallBack_ROL_TypeP_TrustRegionAlgorithm_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::TypeP::TrustRegionAlgorithm<double> const &o){ return new ROL::TypeP::TrustRegionAlgorithm<double>(o); } ) );
		cl.def("run", [](ROL::TypeP::TrustRegionAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", [](ROL::TypeP::TrustRegionAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::TrustRegionAlgorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", [](ROL::TypeP::TrustRegionAlgorithm<double> &o, class ROL::Problem<double> & a0, std::ostream & a1) -> void { return o.run(a0, a1); }, "", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::TrustRegionAlgorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::TrustRegionAlgorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::TrustRegionAlgorithm<double>::run, "C++: ROL::TypeP::TrustRegionAlgorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeP::TrustRegionAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeP::TrustRegionAlgorithm<double>::writeHeader, "C++: ROL::TypeP::TrustRegionAlgorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeP::TrustRegionAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeP::TrustRegionAlgorithm<double>::writeName, "C++: ROL::TypeP::TrustRegionAlgorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeP::TrustRegionAlgorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeP::TrustRegionAlgorithm<double>::*)(std::ostream &, bool) const) &ROL::TypeP::TrustRegionAlgorithm<double>::writeOutput, "C++: ROL::TypeP::TrustRegionAlgorithm<double>::writeOutput(std::ostream &, bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("setStatusTest", [](ROL::TypeP::Algorithm<double> &o, const class Teuchos::RCP<class ROL::StatusTest<double> > & a0) -> void { return o.setStatusTest(a0); }, "", pybind11::arg("status"));
		cl.def("setStatusTest", (void (ROL::TypeP::Algorithm<double>::*)(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool)) &ROL::TypeP::Algorithm<double>::setStatusTest, "C++: ROL::TypeP::Algorithm<double>::setStatusTest(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool) --> void", pybind11::arg("status"), pybind11::arg("combineStatus"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Problem<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Problem<double> &, std::ostream &) --> void", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeHeader, "C++: ROL::TypeP::Algorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeName, "C++: ROL::TypeP::Algorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeP::Algorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &, bool) const) &ROL::TypeP::Algorithm<double>::writeOutput, "C++: ROL::TypeP::Algorithm<double>::writeOutput(std::ostream &, bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("writeExitStatus", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeExitStatus, "C++: ROL::TypeP::Algorithm<double>::writeExitStatus(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("getState", (class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > (ROL::TypeP::Algorithm<double>::*)() const) &ROL::TypeP::Algorithm<double>::getState, "C++: ROL::TypeP::Algorithm<double>::getState() const --> class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> >");
		cl.def("reset", (void (ROL::TypeP::Algorithm<double>::*)()) &ROL::TypeP::Algorithm<double>::reset, "C++: ROL::TypeP::Algorithm<double>::reset() --> void");
	}
	{ // ROL::TypeP::InexactNewtonAlgorithm file:ROL_TypeP_InexactNewtonAlgorithm.hpp line:23
		pybind11::class_<ROL::TypeP::InexactNewtonAlgorithm<double>, Teuchos::RCP<ROL::TypeP::InexactNewtonAlgorithm<double>>, PyCallBack_ROL_TypeP_InexactNewtonAlgorithm_double_t, ROL::TypeP::Algorithm<double>> cl(M("ROL::TypeP"), "InexactNewtonAlgorithm_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<class Teuchos::ParameterList &>(), pybind11::arg("list") );

		cl.def( pybind11::init( [](PyCallBack_ROL_TypeP_InexactNewtonAlgorithm_double_t const &o){ return new PyCallBack_ROL_TypeP_InexactNewtonAlgorithm_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::TypeP::InexactNewtonAlgorithm<double> const &o){ return new ROL::TypeP::InexactNewtonAlgorithm<double>(o); } ) );
		cl.def("run", [](ROL::TypeP::InexactNewtonAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", [](ROL::TypeP::InexactNewtonAlgorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2, std::ostream & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::InexactNewtonAlgorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", [](ROL::TypeP::InexactNewtonAlgorithm<double> &o, class ROL::Problem<double> & a0, std::ostream & a1) -> void { return o.run(a0, a1); }, "", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::InexactNewtonAlgorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::InexactNewtonAlgorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::InexactNewtonAlgorithm<double>::run, "C++: ROL::TypeP::InexactNewtonAlgorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeP::InexactNewtonAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeP::InexactNewtonAlgorithm<double>::writeHeader, "C++: ROL::TypeP::InexactNewtonAlgorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeP::InexactNewtonAlgorithm<double>::*)(std::ostream &) const) &ROL::TypeP::InexactNewtonAlgorithm<double>::writeName, "C++: ROL::TypeP::InexactNewtonAlgorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeP::InexactNewtonAlgorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeP::InexactNewtonAlgorithm<double>::*)(std::ostream &, bool) const) &ROL::TypeP::InexactNewtonAlgorithm<double>::writeOutput, "C++: ROL::TypeP::InexactNewtonAlgorithm<double>::writeOutput(std::ostream &, bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("setStatusTest", [](ROL::TypeP::Algorithm<double> &o, const class Teuchos::RCP<class ROL::StatusTest<double> > & a0) -> void { return o.setStatusTest(a0); }, "", pybind11::arg("status"));
		cl.def("setStatusTest", (void (ROL::TypeP::Algorithm<double>::*)(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool)) &ROL::TypeP::Algorithm<double>::setStatusTest, "C++: ROL::TypeP::Algorithm<double>::setStatusTest(const class Teuchos::RCP<class ROL::StatusTest<double> > &, bool) --> void", pybind11::arg("status"), pybind11::arg("combineStatus"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Problem<double> & a0) -> void { return o.run(a0); }, "", pybind11::arg("problem"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Problem<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Problem<double> &, std::ostream &) --> void", pybind11::arg("problem"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, class ROL::Objective<double> & a1, class ROL::Objective<double> & a2) -> void { return o.run(a0, a1, a2); }, "", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("run", [](ROL::TypeP::Algorithm<double> &o, class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, class ROL::Objective<double> & a2, class ROL::Objective<double> & a3) -> void { return o.run(a0, a1, a2, a3); }, "", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"));
		cl.def("run", (void (ROL::TypeP::Algorithm<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &)) &ROL::TypeP::Algorithm<double>::run, "C++: ROL::TypeP::Algorithm<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &, class ROL::Objective<double> &, std::ostream &) --> void", pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("sobj"), pybind11::arg("nobj"), pybind11::arg("outStream"));
		cl.def("writeHeader", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeHeader, "C++: ROL::TypeP::Algorithm<double>::writeHeader(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeName", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeName, "C++: ROL::TypeP::Algorithm<double>::writeName(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("writeOutput", [](ROL::TypeP::Algorithm<double> const &o, std::ostream & a0) -> void { return o.writeOutput(a0); }, "", pybind11::arg("os"));
		cl.def("writeOutput", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &, bool) const) &ROL::TypeP::Algorithm<double>::writeOutput, "C++: ROL::TypeP::Algorithm<double>::writeOutput(std::ostream &, bool) const --> void", pybind11::arg("os"), pybind11::arg("write_header"));
		cl.def("writeExitStatus", (void (ROL::TypeP::Algorithm<double>::*)(std::ostream &) const) &ROL::TypeP::Algorithm<double>::writeExitStatus, "C++: ROL::TypeP::Algorithm<double>::writeExitStatus(std::ostream &) const --> void", pybind11::arg("os"));
		cl.def("getState", (class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> > (ROL::TypeP::Algorithm<double>::*)() const) &ROL::TypeP::Algorithm<double>::getState, "C++: ROL::TypeP::Algorithm<double>::getState() const --> class Teuchos::RCP<const struct ROL::TypeP::AlgorithmState<double> >");
		cl.def("reset", (void (ROL::TypeP::Algorithm<double>::*)()) &ROL::TypeP::Algorithm<double>::reset, "C++: ROL::TypeP::Algorithm<double>::reset() --> void");
	}
	// ROL::TypeP::EAlgorithmP file:ROL_TypeP_AlgorithmFactory.hpp line:32
	pybind11::enum_<ROL::TypeP::EAlgorithmP>(M("ROL::TypeP"), "EAlgorithmP", pybind11::arithmetic(), "Enumeration of bound constrained algorithm types.\n\n    \n    ALGORITHM_P_LINESEARCH          describe\n    \n\n    ALGORITHM_P_TRUSTREGION         describe\n    \n\n    ALGORITHM_P_SPECTRALGRADIENT    describe\n    \n\n    ALGORITHM_P_IPIANO              describe", pybind11::module_local())
		.value("ALGORITHM_P_LINESEARCH", ROL::TypeP::ALGORITHM_P_LINESEARCH)
		.value("ALGORITHM_P_TRUSTREGION", ROL::TypeP::ALGORITHM_P_TRUSTREGION)
		.value("ALGORITHM_P_SPECTRALGRADIENT", ROL::TypeP::ALGORITHM_P_SPECTRALGRADIENT)
		.value("ALGORITHM_P_IPIANO", ROL::TypeP::ALGORITHM_P_IPIANO)
		.value("ALGORITHM_P_LAST", ROL::TypeP::ALGORITHM_P_LAST)
		.export_values();

;

	// ROL::TypeP::EAlgorithmPToString(enum ROL::TypeP::EAlgorithmP) file:ROL_TypeP_AlgorithmFactory.hpp line:40
	M("ROL::TypeP").def("EAlgorithmPToString", (std::string (*)(enum ROL::TypeP::EAlgorithmP)) &ROL::TypeP::EAlgorithmPToString, "C++: ROL::TypeP::EAlgorithmPToString(enum ROL::TypeP::EAlgorithmP) --> std::string", pybind11::arg("alg"));

	// ROL::TypeP::isValidAlgorithmP(enum ROL::TypeP::EAlgorithmP) file:ROL_TypeP_AlgorithmFactory.hpp line:58
	M("ROL::TypeP").def("isValidAlgorithmP", (int (*)(enum ROL::TypeP::EAlgorithmP)) &ROL::TypeP::isValidAlgorithmP, "Verifies validity of a AlgorithmP enum.\n\n    \n  [in]  - enum of the AlgorithmP\n    \n\n 1 if the argument is a valid AlgorithmP; 0 otherwise.\n\nC++: ROL::TypeP::isValidAlgorithmP(enum ROL::TypeP::EAlgorithmP) --> int", pybind11::arg("alg"));

	// ROL::TypeP::StringToEAlgorithmP(std::string) file:ROL_TypeP_AlgorithmFactory.hpp line:87
	M("ROL::TypeP").def("StringToEAlgorithmP", (enum ROL::TypeP::EAlgorithmP (*)(std::string)) &ROL::TypeP::StringToEAlgorithmP, "C++: ROL::TypeP::StringToEAlgorithmP(std::string) --> enum ROL::TypeP::EAlgorithmP", pybind11::arg("s"));

}
