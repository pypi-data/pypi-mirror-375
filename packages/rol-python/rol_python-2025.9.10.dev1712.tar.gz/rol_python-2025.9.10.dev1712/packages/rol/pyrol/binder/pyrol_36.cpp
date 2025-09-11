#include <ROL_DescentDirection_U.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_Gradient_U.hpp>
#include <ROL_Krylov.hpp>
#include <ROL_NewtonKrylov_U.hpp>
#include <ROL_Newton_U.hpp>
#include <ROL_NonlinearCG.hpp>
#include <ROL_NonlinearCG_U.hpp>
#include <ROL_Objective.hpp>
#include <ROL_QuasiNewton_U.hpp>
#include <ROL_Secant.hpp>
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

// ROL::Gradient_U file:ROL_Gradient_U.hpp line:26
struct PyCallBack_ROL_Gradient_U_double_t : public ROL::Gradient_U<double> {
	using ROL::Gradient_U<double>::Gradient_U;

	void compute(class ROL::Vector<double> & a0, double & a1, double & a2, int & a3, int & a4, const class ROL::Vector<double> & a5, const class ROL::Vector<double> & a6, class ROL::Objective<double> & a7) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Gradient_U<double> *>(this), "compute");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6, a7);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Gradient_U::compute(a0, a1, a2, a3, a4, a5, a6, a7);
	}
	std::string printName() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Gradient_U<double> *>(this), "printName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<std::string>::value) {
				static pybind11::detail::override_caster_t<std::string> caster;
				return pybind11::detail::cast_ref<std::string>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<std::string>(std::move(o));
		}
		return Gradient_U::printName();
	}
	void initialize(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Gradient_U<double> *>(this), "initialize");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DescentDirection_U::initialize(a0, a1);
	}
	void update(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const double a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Gradient_U<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DescentDirection_U::update(a0, a1, a2, a3, a4, a5);
	}
};

// ROL::QuasiNewton_U file:ROL_QuasiNewton_U.hpp line:27
struct PyCallBack_ROL_QuasiNewton_U_double_t : public ROL::QuasiNewton_U<double> {
	using ROL::QuasiNewton_U<double>::QuasiNewton_U;

	void compute(class ROL::Vector<double> & a0, double & a1, double & a2, int & a3, int & a4, const class ROL::Vector<double> & a5, const class ROL::Vector<double> & a6, class ROL::Objective<double> & a7) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::QuasiNewton_U<double> *>(this), "compute");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6, a7);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return QuasiNewton_U::compute(a0, a1, a2, a3, a4, a5, a6, a7);
	}
	void update(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const double a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::QuasiNewton_U<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return QuasiNewton_U::update(a0, a1, a2, a3, a4, a5);
	}
	std::string printName() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::QuasiNewton_U<double> *>(this), "printName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<std::string>::value) {
				static pybind11::detail::override_caster_t<std::string> caster;
				return pybind11::detail::cast_ref<std::string>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<std::string>(std::move(o));
		}
		return QuasiNewton_U::printName();
	}
	void initialize(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::QuasiNewton_U<double> *>(this), "initialize");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DescentDirection_U::initialize(a0, a1);
	}
};

// ROL::NonlinearCG file:ROL_NonlinearCG.hpp line:52
struct PyCallBack_ROL_NonlinearCG_double_t : public ROL::NonlinearCG<double> {
	using ROL::NonlinearCG<double>::NonlinearCG;

	void run(class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, class ROL::Objective<double> & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::NonlinearCG<double> *>(this), "run");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return NonlinearCG::run(a0, a1, a2, a3);
	}
};

// ROL::NonlinearCG_U file:ROL_NonlinearCG_U.hpp line:28
struct PyCallBack_ROL_NonlinearCG_U_double_t : public ROL::NonlinearCG_U<double> {
	using ROL::NonlinearCG_U<double>::NonlinearCG_U;

	void compute(class ROL::Vector<double> & a0, double & a1, double & a2, int & a3, int & a4, const class ROL::Vector<double> & a5, const class ROL::Vector<double> & a6, class ROL::Objective<double> & a7) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::NonlinearCG_U<double> *>(this), "compute");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6, a7);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return NonlinearCG_U::compute(a0, a1, a2, a3, a4, a5, a6, a7);
	}
	std::string printName() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::NonlinearCG_U<double> *>(this), "printName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<std::string>::value) {
				static pybind11::detail::override_caster_t<std::string> caster;
				return pybind11::detail::cast_ref<std::string>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<std::string>(std::move(o));
		}
		return NonlinearCG_U::printName();
	}
	void initialize(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::NonlinearCG_U<double> *>(this), "initialize");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DescentDirection_U::initialize(a0, a1);
	}
	void update(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const double a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::NonlinearCG_U<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DescentDirection_U::update(a0, a1, a2, a3, a4, a5);
	}
};

// ROL::Newton_U file:ROL_Newton_U.hpp line:25
struct PyCallBack_ROL_Newton_U_double_t : public ROL::Newton_U<double> {
	using ROL::Newton_U<double>::Newton_U;

	void compute(class ROL::Vector<double> & a0, double & a1, double & a2, int & a3, int & a4, const class ROL::Vector<double> & a5, const class ROL::Vector<double> & a6, class ROL::Objective<double> & a7) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Newton_U<double> *>(this), "compute");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6, a7);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return Newton_U::compute(a0, a1, a2, a3, a4, a5, a6, a7);
	}
	std::string printName() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Newton_U<double> *>(this), "printName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<std::string>::value) {
				static pybind11::detail::override_caster_t<std::string> caster;
				return pybind11::detail::cast_ref<std::string>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<std::string>(std::move(o));
		}
		return Newton_U::printName();
	}
	void initialize(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Newton_U<double> *>(this), "initialize");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DescentDirection_U::initialize(a0, a1);
	}
	void update(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const double a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::Newton_U<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DescentDirection_U::update(a0, a1, a2, a3, a4, a5);
	}
};

// ROL::NewtonKrylov_U file:ROL_NewtonKrylov_U.hpp line:29
struct PyCallBack_ROL_NewtonKrylov_U_double_t : public ROL::NewtonKrylov_U<double> {
	using ROL::NewtonKrylov_U<double>::NewtonKrylov_U;

	void compute(class ROL::Vector<double> & a0, double & a1, double & a2, int & a3, int & a4, const class ROL::Vector<double> & a5, const class ROL::Vector<double> & a6, class ROL::Objective<double> & a7) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::NewtonKrylov_U<double> *>(this), "compute");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5, a6, a7);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return NewtonKrylov_U::compute(a0, a1, a2, a3, a4, a5, a6, a7);
	}
	void update(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1, const class ROL::Vector<double> & a2, const class ROL::Vector<double> & a3, const double a4, const int a5) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::NewtonKrylov_U<double> *>(this), "update");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3, a4, a5);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return NewtonKrylov_U::update(a0, a1, a2, a3, a4, a5);
	}
	std::string printName() const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::NewtonKrylov_U<double> *>(this), "printName");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<std::string>::value) {
				static pybind11::detail::override_caster_t<std::string> caster;
				return pybind11::detail::cast_ref<std::string>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<std::string>(std::move(o));
		}
		return NewtonKrylov_U::printName();
	}
	void initialize(const class ROL::Vector<double> & a0, const class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::NewtonKrylov_U<double> *>(this), "initialize");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return DescentDirection_U::initialize(a0, a1);
	}
};

void bind_pyrol_36(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // ROL::Gradient_U file:ROL_Gradient_U.hpp line:26
		pybind11::class_<ROL::Gradient_U<double>, Teuchos::RCP<ROL::Gradient_U<double>>, PyCallBack_ROL_Gradient_U_double_t, ROL::DescentDirection_U<double>> cl(M("ROL"), "Gradient_U_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::Gradient_U<double>(); }, [](){ return new PyCallBack_ROL_Gradient_U_double_t(); } ) );
		cl.def( pybind11::init( [](PyCallBack_ROL_Gradient_U_double_t const &o){ return new PyCallBack_ROL_Gradient_U_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::Gradient_U<double> const &o){ return new ROL::Gradient_U<double>(o); } ) );
		cl.def("compute", (void (ROL::Gradient_U<double>::*)(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &)) &ROL::Gradient_U<double>::compute, "C++: ROL::Gradient_U<double>::compute(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &) --> void", pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("sdotg"), pybind11::arg("iter"), pybind11::arg("flag"), pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"));
		cl.def("printName", (std::string (ROL::Gradient_U<double>::*)() const) &ROL::Gradient_U<double>::printName, "C++: ROL::Gradient_U<double>::printName() const --> std::string");
		cl.def("assign", (class ROL::Gradient_U<double> & (ROL::Gradient_U<double>::*)(const class ROL::Gradient_U<double> &)) &ROL::Gradient_U<double>::operator=, "C++: ROL::Gradient_U<double>::operator=(const class ROL::Gradient_U<double> &) --> class ROL::Gradient_U<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("initialize", (void (ROL::DescentDirection_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &)) &ROL::DescentDirection_U<double>::initialize, "C++: ROL::DescentDirection_U<double>::initialize(const class ROL::Vector<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("x"), pybind11::arg("g"));
		cl.def("compute", (void (ROL::DescentDirection_U<double>::*)(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &)) &ROL::DescentDirection_U<double>::compute, "C++: ROL::DescentDirection_U<double>::compute(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &) --> void", pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("sdotg"), pybind11::arg("iter"), pybind11::arg("flag"), pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"));
		cl.def("update", (void (ROL::DescentDirection_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::DescentDirection_U<double>::update, "C++: ROL::DescentDirection_U<double>::update(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("s"), pybind11::arg("gold"), pybind11::arg("gnew"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("printName", (std::string (ROL::DescentDirection_U<double>::*)() const) &ROL::DescentDirection_U<double>::printName, "C++: ROL::DescentDirection_U<double>::printName() const --> std::string");
		cl.def("assign", (class ROL::DescentDirection_U<double> & (ROL::DescentDirection_U<double>::*)(const class ROL::DescentDirection_U<double> &)) &ROL::DescentDirection_U<double>::operator=, "C++: ROL::DescentDirection_U<double>::operator=(const class ROL::DescentDirection_U<double> &) --> class ROL::DescentDirection_U<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::QuasiNewton_U file:ROL_QuasiNewton_U.hpp line:27
		pybind11::class_<ROL::QuasiNewton_U<double>, Teuchos::RCP<ROL::QuasiNewton_U<double>>, PyCallBack_ROL_QuasiNewton_U_double_t, ROL::DescentDirection_U<double>> cl(M("ROL"), "QuasiNewton_U_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](class Teuchos::ParameterList & a0){ return new ROL::QuasiNewton_U<double>(a0); }, [](class Teuchos::ParameterList & a0){ return new PyCallBack_ROL_QuasiNewton_U_double_t(a0); } ), "doc");
		cl.def( pybind11::init<class Teuchos::ParameterList &, const class Teuchos::RCP<class ROL::Secant<double> > &>(), pybind11::arg("parlist"), pybind11::arg("secant") );

		cl.def( pybind11::init( [](PyCallBack_ROL_QuasiNewton_U_double_t const &o){ return new PyCallBack_ROL_QuasiNewton_U_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::QuasiNewton_U<double> const &o){ return new ROL::QuasiNewton_U<double>(o); } ) );
		cl.def("compute", (void (ROL::QuasiNewton_U<double>::*)(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &)) &ROL::QuasiNewton_U<double>::compute, "C++: ROL::QuasiNewton_U<double>::compute(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &) --> void", pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("sdotg"), pybind11::arg("iter"), pybind11::arg("flag"), pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"));
		cl.def("update", (void (ROL::QuasiNewton_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::QuasiNewton_U<double>::update, "C++: ROL::QuasiNewton_U<double>::update(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("s"), pybind11::arg("gold"), pybind11::arg("gnew"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("printName", (std::string (ROL::QuasiNewton_U<double>::*)() const) &ROL::QuasiNewton_U<double>::printName, "C++: ROL::QuasiNewton_U<double>::printName() const --> std::string");
		cl.def("assign", (class ROL::QuasiNewton_U<double> & (ROL::QuasiNewton_U<double>::*)(const class ROL::QuasiNewton_U<double> &)) &ROL::QuasiNewton_U<double>::operator=, "C++: ROL::QuasiNewton_U<double>::operator=(const class ROL::QuasiNewton_U<double> &) --> class ROL::QuasiNewton_U<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("initialize", (void (ROL::DescentDirection_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &)) &ROL::DescentDirection_U<double>::initialize, "C++: ROL::DescentDirection_U<double>::initialize(const class ROL::Vector<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("x"), pybind11::arg("g"));
		cl.def("compute", (void (ROL::DescentDirection_U<double>::*)(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &)) &ROL::DescentDirection_U<double>::compute, "C++: ROL::DescentDirection_U<double>::compute(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &) --> void", pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("sdotg"), pybind11::arg("iter"), pybind11::arg("flag"), pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"));
		cl.def("update", (void (ROL::DescentDirection_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::DescentDirection_U<double>::update, "C++: ROL::DescentDirection_U<double>::update(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("s"), pybind11::arg("gold"), pybind11::arg("gnew"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("printName", (std::string (ROL::DescentDirection_U<double>::*)() const) &ROL::DescentDirection_U<double>::printName, "C++: ROL::DescentDirection_U<double>::printName() const --> std::string");
		cl.def("assign", (class ROL::DescentDirection_U<double> & (ROL::DescentDirection_U<double>::*)(const class ROL::DescentDirection_U<double> &)) &ROL::DescentDirection_U<double>::operator=, "C++: ROL::DescentDirection_U<double>::operator=(const class ROL::DescentDirection_U<double> &) --> class ROL::DescentDirection_U<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::NonlinearCGState file:ROL_NonlinearCG.hpp line:43
		pybind11::class_<ROL::NonlinearCGState<double>, Teuchos::RCP<ROL::NonlinearCGState<double>>> cl(M("ROL"), "NonlinearCGState_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](ROL::NonlinearCGState<double> const &o){ return new ROL::NonlinearCGState<double>(o); } ) );
		cl.def( pybind11::init( [](){ return new ROL::NonlinearCGState<double>(); } ) );
		cl.def_readwrite("grad", &ROL::NonlinearCGState<double>::grad);
		cl.def_readwrite("pstep", &ROL::NonlinearCGState<double>::pstep);
		cl.def_readwrite("iter", &ROL::NonlinearCGState<double>::iter);
		cl.def_readwrite("restart", &ROL::NonlinearCGState<double>::restart);
		cl.def_readwrite("nlcg_type", &ROL::NonlinearCGState<double>::nlcg_type);
		cl.def("assign", (struct ROL::NonlinearCGState<double> & (ROL::NonlinearCGState<double>::*)(const struct ROL::NonlinearCGState<double> &)) &ROL::NonlinearCGState<double>::operator=, "C++: ROL::NonlinearCGState<double>::operator=(const struct ROL::NonlinearCGState<double> &) --> struct ROL::NonlinearCGState<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::NonlinearCG file:ROL_NonlinearCG.hpp line:52
		pybind11::class_<ROL::NonlinearCG<double>, Teuchos::RCP<ROL::NonlinearCG<double>>, PyCallBack_ROL_NonlinearCG_double_t> cl(M("ROL"), "NonlinearCG_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](enum ROL::ENonlinearCG const & a0){ return new ROL::NonlinearCG<double>(a0); }, [](enum ROL::ENonlinearCG const & a0){ return new PyCallBack_ROL_NonlinearCG_double_t(a0); } ), "doc");
		cl.def( pybind11::init<enum ROL::ENonlinearCG, int>(), pybind11::arg("type"), pybind11::arg("restart") );

		cl.def( pybind11::init( [](PyCallBack_ROL_NonlinearCG_double_t const &o){ return new PyCallBack_ROL_NonlinearCG_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::NonlinearCG<double> const &o){ return new ROL::NonlinearCG<double>(o); } ) );
		cl.def("run", (void (ROL::NonlinearCG<double>::*)(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &)) &ROL::NonlinearCG<double>::run, "C++: ROL::NonlinearCG<double>::run(class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &) --> void", pybind11::arg("s"), pybind11::arg("g"), pybind11::arg("x"), pybind11::arg("obj"));
		cl.def("assign", (class ROL::NonlinearCG<double> & (ROL::NonlinearCG<double>::*)(const class ROL::NonlinearCG<double> &)) &ROL::NonlinearCG<double>::operator=, "C++: ROL::NonlinearCG<double>::operator=(const class ROL::NonlinearCG<double> &) --> class ROL::NonlinearCG<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::NonlinearCG_U file:ROL_NonlinearCG_U.hpp line:28
		pybind11::class_<ROL::NonlinearCG_U<double>, Teuchos::RCP<ROL::NonlinearCG_U<double>>, PyCallBack_ROL_NonlinearCG_U_double_t, ROL::DescentDirection_U<double>> cl(M("ROL"), "NonlinearCG_U_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](class Teuchos::ParameterList & a0){ return new ROL::NonlinearCG_U<double>(a0); }, [](class Teuchos::ParameterList & a0){ return new PyCallBack_ROL_NonlinearCG_U_double_t(a0); } ), "doc");
		cl.def( pybind11::init<class Teuchos::ParameterList &, const class Teuchos::RCP<class ROL::NonlinearCG<double> > &>(), pybind11::arg("parlist"), pybind11::arg("nlcg") );

		cl.def( pybind11::init( [](PyCallBack_ROL_NonlinearCG_U_double_t const &o){ return new PyCallBack_ROL_NonlinearCG_U_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::NonlinearCG_U<double> const &o){ return new ROL::NonlinearCG_U<double>(o); } ) );
		cl.def("compute", (void (ROL::NonlinearCG_U<double>::*)(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &)) &ROL::NonlinearCG_U<double>::compute, "C++: ROL::NonlinearCG_U<double>::compute(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &) --> void", pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("sdotg"), pybind11::arg("iter"), pybind11::arg("flag"), pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"));
		cl.def("printName", (std::string (ROL::NonlinearCG_U<double>::*)() const) &ROL::NonlinearCG_U<double>::printName, "C++: ROL::NonlinearCG_U<double>::printName() const --> std::string");
		cl.def("assign", (class ROL::NonlinearCG_U<double> & (ROL::NonlinearCG_U<double>::*)(const class ROL::NonlinearCG_U<double> &)) &ROL::NonlinearCG_U<double>::operator=, "C++: ROL::NonlinearCG_U<double>::operator=(const class ROL::NonlinearCG_U<double> &) --> class ROL::NonlinearCG_U<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("initialize", (void (ROL::DescentDirection_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &)) &ROL::DescentDirection_U<double>::initialize, "C++: ROL::DescentDirection_U<double>::initialize(const class ROL::Vector<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("x"), pybind11::arg("g"));
		cl.def("compute", (void (ROL::DescentDirection_U<double>::*)(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &)) &ROL::DescentDirection_U<double>::compute, "C++: ROL::DescentDirection_U<double>::compute(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &) --> void", pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("sdotg"), pybind11::arg("iter"), pybind11::arg("flag"), pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"));
		cl.def("update", (void (ROL::DescentDirection_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::DescentDirection_U<double>::update, "C++: ROL::DescentDirection_U<double>::update(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("s"), pybind11::arg("gold"), pybind11::arg("gnew"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("printName", (std::string (ROL::DescentDirection_U<double>::*)() const) &ROL::DescentDirection_U<double>::printName, "C++: ROL::DescentDirection_U<double>::printName() const --> std::string");
		cl.def("assign", (class ROL::DescentDirection_U<double> & (ROL::DescentDirection_U<double>::*)(const class ROL::DescentDirection_U<double> &)) &ROL::DescentDirection_U<double>::operator=, "C++: ROL::DescentDirection_U<double>::operator=(const class ROL::DescentDirection_U<double> &) --> class ROL::DescentDirection_U<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::Newton_U file:ROL_Newton_U.hpp line:25
		pybind11::class_<ROL::Newton_U<double>, Teuchos::RCP<ROL::Newton_U<double>>, PyCallBack_ROL_Newton_U_double_t, ROL::DescentDirection_U<double>> cl(M("ROL"), "Newton_U_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::Newton_U<double>(); }, [](){ return new PyCallBack_ROL_Newton_U_double_t(); } ) );
		cl.def( pybind11::init( [](PyCallBack_ROL_Newton_U_double_t const &o){ return new PyCallBack_ROL_Newton_U_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::Newton_U<double> const &o){ return new ROL::Newton_U<double>(o); } ) );
		cl.def("compute", (void (ROL::Newton_U<double>::*)(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &)) &ROL::Newton_U<double>::compute, "C++: ROL::Newton_U<double>::compute(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &) --> void", pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("sdotg"), pybind11::arg("iter"), pybind11::arg("flag"), pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"));
		cl.def("printName", (std::string (ROL::Newton_U<double>::*)() const) &ROL::Newton_U<double>::printName, "C++: ROL::Newton_U<double>::printName() const --> std::string");
		cl.def("assign", (class ROL::Newton_U<double> & (ROL::Newton_U<double>::*)(const class ROL::Newton_U<double> &)) &ROL::Newton_U<double>::operator=, "C++: ROL::Newton_U<double>::operator=(const class ROL::Newton_U<double> &) --> class ROL::Newton_U<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("initialize", (void (ROL::DescentDirection_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &)) &ROL::DescentDirection_U<double>::initialize, "C++: ROL::DescentDirection_U<double>::initialize(const class ROL::Vector<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("x"), pybind11::arg("g"));
		cl.def("compute", (void (ROL::DescentDirection_U<double>::*)(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &)) &ROL::DescentDirection_U<double>::compute, "C++: ROL::DescentDirection_U<double>::compute(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &) --> void", pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("sdotg"), pybind11::arg("iter"), pybind11::arg("flag"), pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"));
		cl.def("update", (void (ROL::DescentDirection_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::DescentDirection_U<double>::update, "C++: ROL::DescentDirection_U<double>::update(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("s"), pybind11::arg("gold"), pybind11::arg("gnew"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("printName", (std::string (ROL::DescentDirection_U<double>::*)() const) &ROL::DescentDirection_U<double>::printName, "C++: ROL::DescentDirection_U<double>::printName() const --> std::string");
		cl.def("assign", (class ROL::DescentDirection_U<double> & (ROL::DescentDirection_U<double>::*)(const class ROL::DescentDirection_U<double> &)) &ROL::DescentDirection_U<double>::operator=, "C++: ROL::DescentDirection_U<double>::operator=(const class ROL::DescentDirection_U<double> &) --> class ROL::DescentDirection_U<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
	{ // ROL::NewtonKrylov_U file:ROL_NewtonKrylov_U.hpp line:29
		pybind11::class_<ROL::NewtonKrylov_U<double>, Teuchos::RCP<ROL::NewtonKrylov_U<double>>, PyCallBack_ROL_NewtonKrylov_U_double_t, ROL::DescentDirection_U<double>> cl(M("ROL"), "NewtonKrylov_U_double_t", "", pybind11::module_local());
		cl.def( pybind11::init<class Teuchos::ParameterList &>(), pybind11::arg("parlist") );

		cl.def( pybind11::init( [](class Teuchos::ParameterList & a0, const class Teuchos::RCP<class ROL::Krylov<double> > & a1, const class Teuchos::RCP<class ROL::Secant<double> > & a2){ return new ROL::NewtonKrylov_U<double>(a0, a1, a2); }, [](class Teuchos::ParameterList & a0, const class Teuchos::RCP<class ROL::Krylov<double> > & a1, const class Teuchos::RCP<class ROL::Secant<double> > & a2){ return new PyCallBack_ROL_NewtonKrylov_U_double_t(a0, a1, a2); } ), "doc");
		cl.def( pybind11::init<class Teuchos::ParameterList &, const class Teuchos::RCP<class ROL::Krylov<double> > &, const class Teuchos::RCP<class ROL::Secant<double> > &, const bool>(), pybind11::arg("parlist"), pybind11::arg("krylov"), pybind11::arg("secant"), pybind11::arg("computeObj") );

		cl.def( pybind11::init( [](PyCallBack_ROL_NewtonKrylov_U_double_t const &o){ return new PyCallBack_ROL_NewtonKrylov_U_double_t(o); } ) );
		cl.def( pybind11::init( [](ROL::NewtonKrylov_U<double> const &o){ return new ROL::NewtonKrylov_U<double>(o); } ) );
		cl.def("compute", (void (ROL::NewtonKrylov_U<double>::*)(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &)) &ROL::NewtonKrylov_U<double>::compute, "C++: ROL::NewtonKrylov_U<double>::compute(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &) --> void", pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("sdotg"), pybind11::arg("iter"), pybind11::arg("flag"), pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"));
		cl.def("update", (void (ROL::NewtonKrylov_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::NewtonKrylov_U<double>::update, "C++: ROL::NewtonKrylov_U<double>::update(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("s"), pybind11::arg("gold"), pybind11::arg("gnew"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("printName", (std::string (ROL::NewtonKrylov_U<double>::*)() const) &ROL::NewtonKrylov_U<double>::printName, "C++: ROL::NewtonKrylov_U<double>::printName() const --> std::string");
		cl.def("assign", (class ROL::NewtonKrylov_U<double> & (ROL::NewtonKrylov_U<double>::*)(const class ROL::NewtonKrylov_U<double> &)) &ROL::NewtonKrylov_U<double>::operator=, "C++: ROL::NewtonKrylov_U<double>::operator=(const class ROL::NewtonKrylov_U<double> &) --> class ROL::NewtonKrylov_U<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
		cl.def("initialize", (void (ROL::DescentDirection_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &)) &ROL::DescentDirection_U<double>::initialize, "C++: ROL::DescentDirection_U<double>::initialize(const class ROL::Vector<double> &, const class ROL::Vector<double> &) --> void", pybind11::arg("x"), pybind11::arg("g"));
		cl.def("compute", (void (ROL::DescentDirection_U<double>::*)(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &)) &ROL::DescentDirection_U<double>::compute, "C++: ROL::DescentDirection_U<double>::compute(class ROL::Vector<double> &, double &, double &, int &, int &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, class ROL::Objective<double> &) --> void", pybind11::arg("s"), pybind11::arg("snorm"), pybind11::arg("sdotg"), pybind11::arg("iter"), pybind11::arg("flag"), pybind11::arg("x"), pybind11::arg("g"), pybind11::arg("obj"));
		cl.def("update", (void (ROL::DescentDirection_U<double>::*)(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int)) &ROL::DescentDirection_U<double>::update, "C++: ROL::DescentDirection_U<double>::update(const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const class ROL::Vector<double> &, const double, const int) --> void", pybind11::arg("x"), pybind11::arg("s"), pybind11::arg("gold"), pybind11::arg("gnew"), pybind11::arg("snorm"), pybind11::arg("iter"));
		cl.def("printName", (std::string (ROL::DescentDirection_U<double>::*)() const) &ROL::DescentDirection_U<double>::printName, "C++: ROL::DescentDirection_U<double>::printName() const --> std::string");
		cl.def("assign", (class ROL::DescentDirection_U<double> & (ROL::DescentDirection_U<double>::*)(const class ROL::DescentDirection_U<double> &)) &ROL::DescentDirection_U<double>::operator=, "C++: ROL::DescentDirection_U<double>::operator=(const class ROL::DescentDirection_U<double> &) --> class ROL::DescentDirection_U<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
}
