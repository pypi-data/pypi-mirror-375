#include <ROL_DynamicFunction.hpp>
#include <ROL_DynamicObjective.hpp>
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

// ROL::DynamicObjective file:ROL_DynamicObjective.hpp line:38
struct PyCallBack_ROL_DynamicObjective_double_t : public ROL::DynamicObjective<double> {
	using ROL::DynamicObjective<double>::DynamicObjective;

	void update(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const struct ROL::TimeStamp<double> & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicObjective::update(a0, a1, a2, a3);
	}
	double value(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const struct ROL::TimeStamp<double> & a3) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "value");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<double>::value) {
				static pybind11::detail::override_caster_t<double> caster;
				return pybind11::detail::cast_ref<double>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<double>(std::move(o));
		}
		pybind11::pybind11_fail("Tried to call pure virtual function \"DynamicObjective::value\"");
	}
	void gradient_uo(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const struct ROL::TimeStamp<double> & a4) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "gradient_uo");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicObjective::gradient_uo(a0, a1, a2, a3, a4);
	}
	void gradient_un(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const struct ROL::TimeStamp<double> & a4) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "gradient_un");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicObjective::gradient_un(a0, a1, a2, a3, a4);
	}
	void gradient_z(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const struct ROL::TimeStamp<double> & a4) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "gradient_z");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicObjective::gradient_z(a0, a1, a2, a3, a4);
	}
	void hessVec_uo_uo(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const struct ROL::TimeStamp<double> & a5) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "hessVec_uo_uo");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicObjective::hessVec_uo_uo(a0, a1, a2, a3, a4, a5);
	}
	void hessVec_uo_un(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const struct ROL::TimeStamp<double> & a5) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "hessVec_uo_un");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicObjective::hessVec_uo_un(a0, a1, a2, a3, a4, a5);
	}
	void hessVec_uo_z(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const struct ROL::TimeStamp<double> & a5) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "hessVec_uo_z");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicObjective::hessVec_uo_z(a0, a1, a2, a3, a4, a5);
	}
	void hessVec_un_uo(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const struct ROL::TimeStamp<double> & a5) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "hessVec_un_uo");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicObjective::hessVec_un_uo(a0, a1, a2, a3, a4, a5);
	}
	void hessVec_un_un(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const struct ROL::TimeStamp<double> & a5) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "hessVec_un_un");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicObjective::hessVec_un_un(a0, a1, a2, a3, a4, a5);
	}
	void hessVec_un_z(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const struct ROL::TimeStamp<double> & a5) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "hessVec_un_z");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicObjective::hessVec_un_z(a0, a1, a2, a3, a4, a5);
	}
	void hessVec_z_uo(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const struct ROL::TimeStamp<double> & a5) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "hessVec_z_uo");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicObjective::hessVec_z_uo(a0, a1, a2, a3, a4, a5);
	}
	void hessVec_z_un(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const struct ROL::TimeStamp<double> & a5) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "hessVec_z_un");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicObjective::hessVec_z_un(a0, a1, a2, a3, a4, a5);
	}
	void hessVec_z_z(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const class ROL::Vector<double> & a4, const struct ROL::TimeStamp<double> & a5) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "hessVec_z_z");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DynamicObjective::hessVec_z_z(a0, a1, a2, a3, a4, a5);
	}
	void update_uo(const class ROL::Vector<double> & a0, const struct ROL::TimeStamp<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "update_uo");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "update_un");
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
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::DynamicObjective<double> *>(this), "update_z");
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

void bind_pyrol_47(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::DynamicObjective file:ROL_DynamicObjective.hpp line:38
		PYBIND11_TYPE_CASTER_BASE_HOLDER(ROL::DynamicObjective<double> , Teuchos::RCP<ROL::DynamicObjective<double>>)
		pybind11::class_<ROL::DynamicObjective<double>, Teuchos::RCP<ROL::DynamicObjective<double>>, PyCallBack_ROL_DynamicObjective_double_t, ROL::DynamicFunction<double>> cl(M("ROL"), "DynamicObjective_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new PyCallBack_ROL_DynamicObjective_double_t(); } ) );
		cl.def(pybind11::init<PyCallBack_ROL_DynamicObjective_double_t const &>());
		cl.def("update_uo", [](ROL::DynamicObjective<double> &o, const class ROL::Vector<double> & a0, const struct ROL::TimeStamp<double> & a1) -> void { return o.update_uo(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("ts"));
		cl.def("update_un", [](ROL::DynamicObjective<double> &o, const class ROL::Vector<double> & a0, const struct ROL::TimeStamp<double> & a1) -> void { return o.update_un(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("ts"));
		cl.def("update_z", [](ROL::DynamicObjective<double> &o, const class ROL::Vector<double> & a0, const struct ROL::TimeStamp<double> & a1) -> void { return o.update_z(a0, a1); }, "", pybind11::arg("x"), pybind11::arg("ts"));
		cl.def("update", (void (ROL::DynamicObjective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &)) &ROL::DynamicObjective<double>::update, "C++: ROL::DynamicObjective<double>::update(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) --> void", pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("value", (double (ROL::DynamicObjective<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const) &ROL::DynamicObjective<double>::value, "C++: ROL::DynamicObjective<double>::value(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const --> double", pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("gradient_uo", (void (ROL::DynamicObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const) &ROL::DynamicObjective<double>::gradient_uo, "C++: ROL::DynamicObjective<double>::gradient_uo(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const --> void", pybind11::arg("g"), pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("gradient_un", (void (ROL::DynamicObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const) &ROL::DynamicObjective<double>::gradient_un, "C++: ROL::DynamicObjective<double>::gradient_un(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const --> void", pybind11::arg("g"), pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("gradient_z", (void (ROL::DynamicObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const) &ROL::DynamicObjective<double>::gradient_z, "C++: ROL::DynamicObjective<double>::gradient_z(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const --> void", pybind11::arg("g"), pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("hessVec_uo_uo", (void (ROL::DynamicObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const) &ROL::DynamicObjective<double>::hessVec_uo_uo, "C++: ROL::DynamicObjective<double>::hessVec_uo_uo(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("hessVec_uo_un", (void (ROL::DynamicObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const) &ROL::DynamicObjective<double>::hessVec_uo_un, "C++: ROL::DynamicObjective<double>::hessVec_uo_un(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("hessVec_uo_z", (void (ROL::DynamicObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const) &ROL::DynamicObjective<double>::hessVec_uo_z, "C++: ROL::DynamicObjective<double>::hessVec_uo_z(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("hessVec_un_uo", (void (ROL::DynamicObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const) &ROL::DynamicObjective<double>::hessVec_un_uo, "C++: ROL::DynamicObjective<double>::hessVec_un_uo(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("hessVec_un_un", (void (ROL::DynamicObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const) &ROL::DynamicObjective<double>::hessVec_un_un, "C++: ROL::DynamicObjective<double>::hessVec_un_un(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("hessVec_un_z", (void (ROL::DynamicObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const) &ROL::DynamicObjective<double>::hessVec_un_z, "C++: ROL::DynamicObjective<double>::hessVec_un_z(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("hessVec_z_uo", (void (ROL::DynamicObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const) &ROL::DynamicObjective<double>::hessVec_z_uo, "C++: ROL::DynamicObjective<double>::hessVec_z_uo(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("hessVec_z_un", (void (ROL::DynamicObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const) &ROL::DynamicObjective<double>::hessVec_z_un, "C++: ROL::DynamicObjective<double>::hessVec_z_un(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("hessVec_z_z", (void (ROL::DynamicObjective<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const) &ROL::DynamicObjective<double>::hessVec_z_z, "C++: ROL::DynamicObjective<double>::hessVec_z_z(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) const --> void", pybind11::arg("hv"), pybind11::arg("v"), pybind11::arg("uo"), pybind11::arg("un"), pybind11::arg("z"), pybind11::arg("timeStamp"));
		cl.def("assign", (class ROL::DynamicObjective<double> & (ROL::DynamicObjective<double>::*)(const class ROL::DynamicObjective<double> &)) &ROL::DynamicObjective<double>::operator=, "C++: ROL::DynamicObjective<double>::operator=(const class ROL::DynamicObjective<double> &) --> class ROL::DynamicObjective<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("update_uo", (void (ROL::DynamicFunction<double>::*)(const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &)) &ROL::DynamicFunction<double>::update_uo, "C++: ROL::DynamicFunction<double>::update_uo(const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) --> void", pybind11::arg("x"), pybind11::arg("ts"));
		cl.def("update_un", (void (ROL::DynamicFunction<double>::*)(const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &)) &ROL::DynamicFunction<double>::update_un, "C++: ROL::DynamicFunction<double>::update_un(const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) --> void", pybind11::arg("x"), pybind11::arg("ts"));
		cl.def("update_z", (void (ROL::DynamicFunction<double>::*)(const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &)) &ROL::DynamicFunction<double>::update_z, "C++: ROL::DynamicFunction<double>::update_z(const class ROL::Vector<double> &, const struct ROL::TimeStamp<double> &) --> void", pybind11::arg("x"), pybind11::arg("ts"));
		cl.def("is_zero_derivative", (bool (ROL::DynamicFunction<double>::*)(const std::string &)) &ROL::DynamicFunction<double>::is_zero_derivative, "C++: ROL::DynamicFunction<double>::is_zero_derivative(const std::string &) --> bool", pybind11::arg("key"));
		cl.def("assign", (class ROL::DynamicFunction<double> & (ROL::DynamicFunction<double>::*)(const class ROL::DynamicFunction<double> &)) &ROL::DynamicFunction<double>::operator=, "C++: ROL::DynamicFunction<double>::operator=(const class ROL::DynamicFunction<double> &) --> class ROL::DynamicFunction<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
}
