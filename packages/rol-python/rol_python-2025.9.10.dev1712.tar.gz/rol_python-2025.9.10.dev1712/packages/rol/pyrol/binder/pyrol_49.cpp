#include <ROL_BatchManager.hpp>
#include <ROL_DynamicObjective.hpp>
#include <ROL_DynamicObjective_CheckInterface.hpp>
#include <ROL_Elementwise_Function.hpp>
#include <ROL_Elementwise_Reduce.hpp>
#include <ROL_TimeStamp.hpp>
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

// ROL::BatchManager file:ROL_BatchManager.hpp line:19
struct PyCallBack_ROL_BatchManager_double_t : public ROL::BatchManager<double> {
	using ROL::BatchManager<double>::BatchManager;

	int batchID() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchManager<double> *>(this), "batchID");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return BatchManager::batchID();
	}
	int numBatches() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchManager<double> *>(this), "numBatches");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<int>::value) {
				static pybind11::detail::override_caster_t<int> caster;
				return pybind11::detail::cast_ref<int>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<int>(std::move(o));
		}
		return BatchManager::numBatches();
	}
	void sumAll(double * a0, double * a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchManager<double> *>(this), "sumAll");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return BatchManager::sumAll(a0, a1, a2);
	}
	void sumAll(class ROL::Vector<double> & a0, class ROL::Vector<double> & a1) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchManager<double> *>(this), "sumAll");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return BatchManager::sumAll(a0, a1);
	}
	void reduceAll(double * a0, double * a1, int a2, const class ROL::Elementwise::ReductionOp<double> & a3) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchManager<double> *>(this), "reduceAll");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return BatchManager::reduceAll(a0, a1, a2, a3);
	}
	void gatherAll(const double * a0, const int a1, double * a2, const int a3) const override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchManager<double> *>(this), "gatherAll");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2, a3);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return BatchManager::gatherAll(a0, a1, a2, a3);
	}
	void broadcast(double * a0, int a1, int a2) override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchManager<double> *>(this), "broadcast");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>(a0, a1, a2);
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return BatchManager::broadcast(a0, a1, a2);
	}
	void barrier() override {
		pybind11::gil_scoped_acquire gil;
		pybind11::function overload = pybind11::get_overload(static_cast<const ROL::BatchManager<double> *>(this), "barrier");
		if (overload) {
			auto o = overload.operator()<pybind11::return_value_policy::reference>();
			if (pybind11::detail::cast_is_temporary_value_reference<void>::value) {
				static pybind11::detail::override_caster_t<void> caster;
				return pybind11::detail::cast_ref<void>(std::move(o), caster);
			}
			return pybind11::detail::cast_safe<void>(std::move(o));
		}
		return BatchManager::barrier();
	}
};

void bind_pyrol_49(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	// ROL::make_check(class ROL::DynamicObjective<double> &) file:ROL_DynamicObjective_CheckInterface.hpp line:177
	M("ROL").def("make_check", (class ROL::details::DynamicObjective_CheckInterface<double> (*)(class ROL::DynamicObjective<double> &)) &ROL::make_check<double>, "C++: ROL::make_check(class ROL::DynamicObjective<double> &) --> class ROL::details::DynamicObjective_CheckInterface<double>", pybind11::arg("obj"));

	// ROL::make_check(class ROL::DynamicObjective<double> &, struct ROL::TimeStamp<double> &) file:ROL_DynamicObjective_CheckInterface.hpp line:182
	M("ROL").def("make_check", (class ROL::details::DynamicObjective_CheckInterface<double> (*)(class ROL::DynamicObjective<double> &, struct ROL::TimeStamp<double> &)) &ROL::make_check<double>, "C++: ROL::make_check(class ROL::DynamicObjective<double> &, struct ROL::TimeStamp<double> &) --> class ROL::details::DynamicObjective_CheckInterface<double>", pybind11::arg("obj"), pybind11::arg("ts"));

	{ // ROL::BatchManager file:ROL_BatchManager.hpp line:19
		pybind11::class_<ROL::BatchManager<double>, Teuchos::RCP<ROL::BatchManager<double>>, PyCallBack_ROL_BatchManager_double_t> cl(M("ROL"), "BatchManager_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new ROL::BatchManager<double>(); }, [](){ return new PyCallBack_ROL_BatchManager_double_t(); } ) );
		cl.def("batchID", (int (ROL::BatchManager<double>::*)()) &ROL::BatchManager<double>::batchID, "C++: ROL::BatchManager<double>::batchID() --> int");
		cl.def("numBatches", (int (ROL::BatchManager<double>::*)()) &ROL::BatchManager<double>::numBatches, "C++: ROL::BatchManager<double>::numBatches() --> int");
		cl.def("sumAll", (void (ROL::BatchManager<double>::*)(double *, double *, int)) &ROL::BatchManager<double>::sumAll, "C++: ROL::BatchManager<double>::sumAll(double *, double *, int) --> void", pybind11::arg("input"), pybind11::arg("output"), pybind11::arg("dim"));
		cl.def("sumAll", (void (ROL::BatchManager<double>::*)(class ROL::Vector<double> &, class ROL::Vector<double> &)) &ROL::BatchManager<double>::sumAll, "C++: ROL::BatchManager<double>::sumAll(class ROL::Vector<double> &, class ROL::Vector<double> &) --> void", pybind11::arg("input"), pybind11::arg("output"));
		cl.def("reduceAll", (void (ROL::BatchManager<double>::*)(double *, double *, int, const class ROL::Elementwise::ReductionOp<double> &)) &ROL::BatchManager<double>::reduceAll, "C++: ROL::BatchManager<double>::reduceAll(double *, double *, int, const class ROL::Elementwise::ReductionOp<double> &) --> void", pybind11::arg("input"), pybind11::arg("output"), pybind11::arg("dim"), pybind11::arg("r"));
		cl.def("gatherAll", (void (ROL::BatchManager<double>::*)(const double *, const int, double *, const int) const) &ROL::BatchManager<double>::gatherAll, "C++: ROL::BatchManager<double>::gatherAll(const double *, const int, double *, const int) const --> void", pybind11::arg("send"), pybind11::arg("ssize"), pybind11::arg("receive"), pybind11::arg("rsize"));
		cl.def("broadcast", (void (ROL::BatchManager<double>::*)(double *, int, int)) &ROL::BatchManager<double>::broadcast, "C++: ROL::BatchManager<double>::broadcast(double *, int, int) --> void", pybind11::arg("input"), pybind11::arg("cnt"), pybind11::arg("root"));
		cl.def("barrier", (void (ROL::BatchManager<double>::*)()) &ROL::BatchManager<double>::barrier, "C++: ROL::BatchManager<double>::barrier() --> void");
		cl.def("assign", (class ROL::BatchManager<double> & (ROL::BatchManager<double>::*)(const class ROL::BatchManager<double> &)) &ROL::BatchManager<double>::operator=, "C++: ROL::BatchManager<double>::operator=(const class ROL::BatchManager<double> &) --> class ROL::BatchManager<double> &", pybind11::return_value_policy::automatic, pybind11::arg(""));
	}
}
