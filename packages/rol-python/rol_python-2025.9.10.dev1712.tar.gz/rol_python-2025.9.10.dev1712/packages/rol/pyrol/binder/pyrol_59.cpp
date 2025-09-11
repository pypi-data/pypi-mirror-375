#include <ROL_BatchManager.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_OED_DoubleWellPenalty.hpp>
#include <ROL_OED_L1Penalty.hpp>
#include <ROL_OED_ProfiledClass.hpp>
#include <ROL_OED_Radamacher.hpp>
#include <ROL_Objective.hpp>
#include <ROL_UpdateType.hpp>
#include <ROL_Vector.hpp>
#include <Teuchos_ENull.hpp>
#include <Teuchos_RCPDecl.hpp>
#include <Teuchos_RCPNode.hpp>
#include <Teuchos_any.hpp>
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

// ROL::OED::Radamacher file:ROL_OED_Radamacher.hpp line:19
struct PyCallBack_ROL_OED_Radamacher_double_t : public ROL::OED::Radamacher<double> {
	using ROL::OED::Radamacher<double>::Radamacher;

	void generate(class ROL::Vector<double> & a0) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::Radamacher<double> *>(this), "generate");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Radamacher::generate(a0);
	}
	void get(class ROL::Vector<double> & a0, const class std::vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::Radamacher<double> *>(this), "get");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Radamacher::get(a0, a1);
	}
	void reset() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::Radamacher<double> *>(this), "reset");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ProfiledClass::reset();
	}
	void summarize(std::ostream & a0, const class Teuchos::RCP<class ROL::BatchManager<double> > & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::Radamacher<double> *>(this), "summarize");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ProfiledClass::summarize(a0, a1);
	}
};

// ROL::OED::L1Penalty file:ROL_OED_L1Penalty.hpp line:21
struct PyCallBack_ROL_OED_L1Penalty_double_t : public ROL::OED::L1Penalty<double> {
	using ROL::OED::L1Penalty<double>::L1Penalty;

	double value(const class ROL::Vector<double> & a0, double & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "value");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return L1Penalty::value(a0, a1);
	}
	void gradient(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "gradient");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return L1Penalty::gradient(a0, a1, a2);
	}
	void hessVec(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "hessVec");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return L1Penalty::hessVec(a0, a1, a2, a3);
	}
	void update(const class ROL::Vector<double> & a0, enum ROL::UpdateType a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "update");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "update");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "dirDeriv");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "invHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "precond");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "prox");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "proxJacVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "checkHessSym");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "checkHessSym");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "checkProxJacVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "setParameter");
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
	void reset() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "reset");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ProfiledClass::reset();
	}
	void summarize(std::ostream & a0, const class Teuchos::RCP<class ROL::BatchManager<double> > & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::L1Penalty<double> *>(this), "summarize");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ProfiledClass::summarize(a0, a1);
	}
};

// ROL::OED::DoubleWellPenalty file:ROL_OED_DoubleWellPenalty.hpp line:21
struct PyCallBack_ROL_OED_DoubleWellPenalty_double_t : public ROL::OED::DoubleWellPenalty<double> {
	using ROL::OED::DoubleWellPenalty<double>::DoubleWellPenalty;

	double value(const class ROL::Vector<double> & a0, double & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "value");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		return DoubleWellPenalty::value(a0, a1);
	}
	void gradient(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, double & a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "gradient");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DoubleWellPenalty::gradient(a0, a1, a2);
	}
	void hessVec(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, double & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "hessVec");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DoubleWellPenalty::hessVec(a0, a1, a2, a3);
	}
	void update(const class ROL::Vector<double> & a0, enum ROL::UpdateType a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "update");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "update");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "dirDeriv");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "invHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "precond");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "prox");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "proxJacVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "checkGradient");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "checkHessVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "checkHessSym");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "checkHessSym");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "checkProxJacVec");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "setParameter");
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
	void reset() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "reset");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ProfiledClass::reset();
	}
	void summarize(std::ostream & a0, const class Teuchos::RCP<class ROL::BatchManager<double> > & a1) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::OED::DoubleWellPenalty<double> *>(this), "summarize");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return ProfiledClass::summarize(a0, a1);
	}
};

void bind_pyrol_59(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::OED::Radamacher file:ROL_OED_Radamacher.hpp line:19
		pybind11::class_<ROL::OED::Radamacher<double>, Teuchos::RCP<ROL::OED::Radamacher<double>>, PyCallBack_ROL_OED_Radamacher_double_t, ROL::OED::TraceSampler<double>> cl(M("ROL::OED"), "Radamacher_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<const class Teuchos::RCP<class ROL::Vector<double> > &, int>(), pybind11::arg("theta"), pybind11::arg("size") );

		cl.def( pybind11::init( [](PyCallBack_ROL_OED_Radamacher_double_t const &o){ return new PyCallBack_ROL_OED_Radamacher_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::OED::Radamacher<double> const &o){ return new ROL::OED::Radamacher<double>(o); } ) );
		cl.def("generate", (void (ROL::OED::Radamacher<double>::*)(class ROL::Vector<double> &) const) &ROL::OED::Radamacher<double>::generate, "C++: ROL::OED::Radamacher<double>::generate(class ROL::Vector<double> &) const --> void", pybind11::arg("g"));
		cl.def("get", (void (ROL::OED::Radamacher<double>::*)(class ROL::Vector<double> &, const class std::vector<double> &)) &ROL::OED::Radamacher<double>::get, "C++: ROL::OED::Radamacher<double>::get(class ROL::Vector<double> &, const class std::vector<double> &) --> void", pybind11::arg("F"), pybind11::arg("param"));
		cl.def("generate", (void (ROL::OED::TraceSampler<double>::*)(class ROL::Vector<double> &) const) &ROL::OED::TraceSampler<double>::generate, "C++: ROL::OED::TraceSampler<double>::generate(class ROL::Vector<double> &) const --> void", pybind11::arg("g"));
		cl.def("get", (void (ROL::OED::TraceSampler<double>::*)(class ROL::Vector<double> &, const class std::vector<double> &)) &ROL::OED::TraceSampler<double>::get, "C++: ROL::OED::TraceSampler<double>::get(class ROL::Vector<double> &, const class std::vector<double> &) --> void", pybind11::arg("F"), pybind11::arg("param"));
		cl.def("startTimer", (void (ROL::OED::ProfiledClass<double,std::string>::*)(std::string) const) &ROL::OED::ProfiledClass<double, std::string>::startTimer, "C++: ROL::OED::ProfiledClass<double, std::string>::startTimer(std::string) const --> void", pybind11::arg("name"));
		cl.def("stopTimer", (void (ROL::OED::ProfiledClass<double,std::string>::*)(std::string) const) &ROL::OED::ProfiledClass<double, std::string>::stopTimer, "C++: ROL::OED::ProfiledClass<double, std::string>::stopTimer(std::string) const --> void", pybind11::arg("name"));
		cl.def("rename", (void (ROL::OED::ProfiledClass<double,std::string>::*)(std::string) const) &ROL::OED::ProfiledClass<double, std::string>::rename, "C++: ROL::OED::ProfiledClass<double, std::string>::rename(std::string) const --> void", pybind11::arg("name"));
		cl.def("reset", (void (ROL::OED::ProfiledClass<double,std::string>::*)()) &ROL::OED::ProfiledClass<double, std::string>::reset, "C++: ROL::OED::ProfiledClass<double, std::string>::reset() --> void");
		cl.def("summarize", [](ROL::OED::ProfiledClass<double,std::string> const &o, std::ostream & a0) -> void { return o.summarize(a0); }, "", pybind11::arg("stream"));
		cl.def("summarize", (void (ROL::OED::ProfiledClass<double,std::string>::*)(std::ostream &, const class Teuchos::RCP<class ROL::BatchManager<double> > &) const) &ROL::OED::ProfiledClass<double, std::string>::summarize, "C++: ROL::OED::ProfiledClass<double, std::string>::summarize(std::ostream &, const class Teuchos::RCP<class ROL::BatchManager<double> > &) const --> void", pybind11::arg("stream"), pybind11::arg("bman"));
	}
	{ // ROL::OED::L1Penalty file:ROL_OED_L1Penalty.hpp line:21
		pybind11::class_<ROL::OED::L1Penalty<double>, Teuchos::RCP<ROL::OED::L1Penalty<double>>, PyCallBack_ROL_OED_L1Penalty_double_t, ROL::Objective<double>, ROL::OED::ProfiledClass<double,std::string>> cl(M("ROL::OED"), "L1Penalty_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::OED::L1Penalty<double>(); }, [](){ return new PyCallBack_ROL_OED_L1Penalty_double_t(); } ) );
		cl.def( pybind11::init( [](PyCallBack_ROL_OED_L1Penalty_double_t const &o){ return new PyCallBack_ROL_OED_L1Penalty_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::OED::L1Penalty<double> const &o){ return new ROL::OED::L1Penalty<double>(o); } ) );
		cl.def("value", (double (ROL::OED::L1Penalty<double>::*)(const class ROL::Vector<double> &, double &)) &ROL::OED::L1Penalty<double>::value, "C++: ROL::OED::L1Penalty<double>::value(const class ROL::Vector<double> &, double &) --> double", pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("gradient", (void (ROL::OED::L1Penalty<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::OED::L1Penalty<double>::gradient, "C++: ROL::OED::L1Penalty<double>::gradient(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("g"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("hessVec", (void (ROL::OED::L1Penalty<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::OED::L1Penalty<double>::hessVec, "C++: ROL::OED::L1Penalty<double>::hessVec(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
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
		cl.def("startTimer", (void (ROL::OED::ProfiledClass<double,std::string>::*)(std::string) const) &ROL::OED::ProfiledClass<double, std::string>::startTimer, "C++: ROL::OED::ProfiledClass<double, std::string>::startTimer(std::string) const --> void", pybind11::arg("name"));
		cl.def("stopTimer", (void (ROL::OED::ProfiledClass<double,std::string>::*)(std::string) const) &ROL::OED::ProfiledClass<double, std::string>::stopTimer, "C++: ROL::OED::ProfiledClass<double, std::string>::stopTimer(std::string) const --> void", pybind11::arg("name"));
		cl.def("rename", (void (ROL::OED::ProfiledClass<double,std::string>::*)(std::string) const) &ROL::OED::ProfiledClass<double, std::string>::rename, "C++: ROL::OED::ProfiledClass<double, std::string>::rename(std::string) const --> void", pybind11::arg("name"));
		cl.def("reset", (void (ROL::OED::ProfiledClass<double,std::string>::*)()) &ROL::OED::ProfiledClass<double, std::string>::reset, "C++: ROL::OED::ProfiledClass<double, std::string>::reset() --> void");
		cl.def("summarize", [](ROL::OED::ProfiledClass<double,std::string> const &o, std::ostream & a0) -> void { return o.summarize(a0); }, "", pybind11::arg("stream"));
		cl.def("summarize", (void (ROL::OED::ProfiledClass<double,std::string>::*)(std::ostream &, const class Teuchos::RCP<class ROL::BatchManager<double> > &) const) &ROL::OED::ProfiledClass<double, std::string>::summarize, "C++: ROL::OED::ProfiledClass<double, std::string>::summarize(std::ostream &, const class Teuchos::RCP<class ROL::BatchManager<double> > &) const --> void", pybind11::arg("stream"), pybind11::arg("bman"));
	}
	{ // ROL::OED::DoubleWellPenalty file:ROL_OED_DoubleWellPenalty.hpp line:21
		pybind11::class_<ROL::OED::DoubleWellPenalty<double>, Teuchos::RCP<ROL::OED::DoubleWellPenalty<double>>, PyCallBack_ROL_OED_DoubleWellPenalty_double_t, ROL::Objective<double>, ROL::OED::ProfiledClass<double,std::string>> cl(M("ROL::OED"), "DoubleWellPenalty_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::OED::DoubleWellPenalty<double>(); }, [](){ return new PyCallBack_ROL_OED_DoubleWellPenalty_double_t(); } ) );
		cl.def( pybind11::init( [](PyCallBack_ROL_OED_DoubleWellPenalty_double_t const &o){ return new PyCallBack_ROL_OED_DoubleWellPenalty_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::OED::DoubleWellPenalty<double> const &o){ return new ROL::OED::DoubleWellPenalty<double>(o); } ) );
		cl.def("value", (double (ROL::OED::DoubleWellPenalty<double>::*)(const class ROL::Vector<double> &, double &)) &ROL::OED::DoubleWellPenalty<double>::value, "C++: ROL::OED::DoubleWellPenalty<double>::value(const class ROL::Vector<double> &, double &) --> double", pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("gradient", (void (ROL::OED::DoubleWellPenalty<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::OED::DoubleWellPenalty<double>::gradient, "C++: ROL::OED::DoubleWellPenalty<double>::gradient(class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("g"), pybind11::arg("x"), pybind11::arg("tol"));
		cl.def("hessVec", (void (ROL::OED::DoubleWellPenalty<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &)) &ROL::OED::DoubleWellPenalty<double>::hessVec, "C++: ROL::OED::DoubleWellPenalty<double>::hessVec(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, double &) --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("x"), pybind11::arg("tol"));
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
		cl.def("startTimer", (void (ROL::OED::ProfiledClass<double,std::string>::*)(std::string) const) &ROL::OED::ProfiledClass<double, std::string>::startTimer, "C++: ROL::OED::ProfiledClass<double, std::string>::startTimer(std::string) const --> void", pybind11::arg("name"));
		cl.def("stopTimer", (void (ROL::OED::ProfiledClass<double,std::string>::*)(std::string) const) &ROL::OED::ProfiledClass<double, std::string>::stopTimer, "C++: ROL::OED::ProfiledClass<double, std::string>::stopTimer(std::string) const --> void", pybind11::arg("name"));
		cl.def("rename", (void (ROL::OED::ProfiledClass<double,std::string>::*)(std::string) const) &ROL::OED::ProfiledClass<double, std::string>::rename, "C++: ROL::OED::ProfiledClass<double, std::string>::rename(std::string) const --> void", pybind11::arg("name"));
		cl.def("reset", (void (ROL::OED::ProfiledClass<double,std::string>::*)()) &ROL::OED::ProfiledClass<double, std::string>::reset, "C++: ROL::OED::ProfiledClass<double, std::string>::reset() --> void");
		cl.def("summarize", [](ROL::OED::ProfiledClass<double,std::string> const &o, std::ostream & a0) -> void { return o.summarize(a0); }, "", pybind11::arg("stream"));
		cl.def("summarize", (void (ROL::OED::ProfiledClass<double,std::string>::*)(std::ostream &, const class Teuchos::RCP<class ROL::BatchManager<double> > &) const) &ROL::OED::ProfiledClass<double, std::string>::summarize, "C++: ROL::OED::ProfiledClass<double, std::string>::summarize(std::ostream &, const class Teuchos::RCP<class ROL::BatchManager<double> > &) const --> void", pybind11::arg("stream"), pybind11::arg("bman"));
	}
}
