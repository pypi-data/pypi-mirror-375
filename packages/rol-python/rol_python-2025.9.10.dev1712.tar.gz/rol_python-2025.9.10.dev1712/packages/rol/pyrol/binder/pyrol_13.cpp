#include <random>
#include <sstream> // __str__

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

void bind_pyrol_13(std::function< pybind11::module &(std::string const &namespace_) > &M)
{
	{ // std::mersenne_twister_engine file:bits/random.h line:588
		pybind11::class_<std::mersenne_twister_engine<unsigned long,64UL,312UL,156UL,31UL,13043109905998158313UL,29UL,6148914691236517205UL,17UL,8202884508482404352UL,37UL,18444473444759240704UL,43UL,6364136223846793005UL>, Teuchos::RCP<std::mersenne_twister_engine<unsigned long,64UL,312UL,156UL,31UL,13043109905998158313UL,29UL,6148914691236517205UL,17UL,8202884508482404352UL,37UL,18444473444759240704UL,43UL,6364136223846793005UL>>> cl(M("std"), "mersenne_twister_engine_unsigned_long_64UL_312UL_156UL_31UL_13043109905998158313UL_29UL_6148914691236517205UL_17UL_8202884508482404352UL_37UL_18444473444759240704UL_43UL_6364136223846793005UL_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new std::mersenne_twister_engine<unsigned long,64UL,312UL,156UL,31UL,13043109905998158313UL,29UL,6148914691236517205UL,17UL,8202884508482404352UL,37UL,18444473444759240704UL,43UL,6364136223846793005UL>(); } ) );
		cl.def( pybind11::init<unsigned long>(), pybind11::arg("__sd") );

		cl.def( pybind11::init( [](std::mersenne_twister_engine<unsigned long,64UL,312UL,156UL,31UL,13043109905998158313UL,29UL,6148914691236517205UL,17UL,8202884508482404352UL,37UL,18444473444759240704UL,43UL,6364136223846793005UL> const &o){ return new std::mersenne_twister_engine<unsigned long,64UL,312UL,156UL,31UL,13043109905998158313UL,29UL,6148914691236517205UL,17UL,8202884508482404352UL,37UL,18444473444759240704UL,43UL,6364136223846793005UL>(o); } ) );
		cl.def("seed", [](std::mersenne_twister_engine<unsigned long,64UL,312UL,156UL,31UL,13043109905998158313UL,29UL,6148914691236517205UL,17UL,8202884508482404352UL,37UL,18444473444759240704UL,43UL,6364136223846793005UL> &o) -> void { return o.seed(); }, "");
		cl.def("seed", (void (std::mersenne_twister_engine<unsigned long,64UL,312UL,156UL,31UL,13043109905998158313UL,29UL,6148914691236517205UL,17UL,8202884508482404352UL,37UL,18444473444759240704UL,43UL,6364136223846793005UL>::*)(unsigned long)) &std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005>::seed, "C++: std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005>::seed(unsigned long) --> void", pybind11::arg("__sd"));
		cl.def_static("min", (unsigned long (*)()) &std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005>::min, "C++: std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005>::min() --> unsigned long");
		cl.def_static("max", (unsigned long (*)()) &std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005>::max, "C++: std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005>::max() --> unsigned long");
		cl.def("discard", (void (std::mersenne_twister_engine<unsigned long,64UL,312UL,156UL,31UL,13043109905998158313UL,29UL,6148914691236517205UL,17UL,8202884508482404352UL,37UL,18444473444759240704UL,43UL,6364136223846793005UL>::*)(unsigned long long)) &std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005>::discard, "C++: std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005>::discard(unsigned long long) --> void", pybind11::arg("__z"));
		cl.def("__call__", (unsigned long (std::mersenne_twister_engine<unsigned long,64UL,312UL,156UL,31UL,13043109905998158313UL,29UL,6148914691236517205UL,17UL,8202884508482404352UL,37UL,18444473444759240704UL,43UL,6364136223846793005UL>::*)()) &std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005>::operator(), "C++: std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005>::operator()() --> unsigned long");
	}
	{ // std::normal_distribution file:bits/random.h line:2118
		pybind11::class_<std::normal_distribution<double>, Teuchos::RCP<std::normal_distribution<double>>> cl(M("std"), "normal_distribution_double_t", "", pybind11::module_local());
		cl.def( pybind11::init( [](){ return new std::normal_distribution<double>(); } ) );
		cl.def( pybind11::init( [](double const & a0){ return new std::normal_distribution<double>(a0); } ), "doc" , pybind11::arg("__mean"));
		cl.def( pybind11::init<double, double>(), pybind11::arg("__mean"), pybind11::arg("__stddev") );

		cl.def( pybind11::init<const struct std::normal_distribution<>::param_type &>(), pybind11::arg("__p") );

		cl.def( pybind11::init( [](std::normal_distribution<double> const &o){ return new std::normal_distribution<double>(o); } ) );
		cl.def("__call__", (double (std::normal_distribution<double>::*)(class std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005> &)) &std::normal_distribution<>::operator()<std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005>>, "C++: std::normal_distribution<>::operator()(class std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005> &) --> double", pybind11::arg("__urng"));
		cl.def("__call__", (double (std::normal_distribution<double>::*)(class std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005> &, const struct std::normal_distribution<>::param_type &)) &std::normal_distribution<>::operator()<std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005>>, "C++: std::normal_distribution<>::operator()(class std::mersenne_twister_engine<unsigned long, 64, 312, 156, 31, 13043109905998158313, 29, 6148914691236517205, 17, 8202884508482404352, 37, 18444473444759240704, 43, 6364136223846793005> &, const struct std::normal_distribution<>::param_type &) --> double", pybind11::arg("__urng"), pybind11::arg("__param"));
		cl.def("reset", (void (std::normal_distribution<double>::*)()) &std::normal_distribution<>::reset, "C++: std::normal_distribution<>::reset() --> void");
		cl.def("mean", (double (std::normal_distribution<double>::*)() const) &std::normal_distribution<>::mean, "C++: std::normal_distribution<>::mean() const --> double");
		cl.def("stddev", (double (std::normal_distribution<double>::*)() const) &std::normal_distribution<>::stddev, "C++: std::normal_distribution<>::stddev() const --> double");
		cl.def("param", (struct std::normal_distribution<>::param_type (std::normal_distribution<double>::*)() const) &std::normal_distribution<>::param, "C++: std::normal_distribution<>::param() const --> struct std::normal_distribution<>::param_type");
		cl.def("param", (void (std::normal_distribution<double>::*)(const struct std::normal_distribution<>::param_type &)) &std::normal_distribution<>::param, "C++: std::normal_distribution<>::param(const struct std::normal_distribution<>::param_type &) --> void", pybind11::arg("__param"));
		cl.def("min", (double (std::normal_distribution<double>::*)() const) &std::normal_distribution<>::min, "C++: std::normal_distribution<>::min() const --> double");
		cl.def("max", (double (std::normal_distribution<double>::*)() const) &std::normal_distribution<>::max, "C++: std::normal_distribution<>::max() const --> double");

		{ // std::normal_distribution<>::param_type file:bits/random.h line:2128
			auto & enclosing_class = cl;
			pybind11::class_<std::normal_distribution<>::param_type, Teuchos::RCP<std::normal_distribution<>::param_type>> cl(enclosing_class, "param_type", "", pybind11::module_local());
			cl.def( pybind11::init( [](){ return new std::normal_distribution<>::param_type(); } ) );
			cl.def( pybind11::init( [](double const & a0){ return new std::normal_distribution<>::param_type(a0); } ), "doc" , pybind11::arg("__mean"));
			cl.def( pybind11::init<double, double>(), pybind11::arg("__mean"), pybind11::arg("__stddev") );

			cl.def( pybind11::init( [](std::normal_distribution<>::param_type const &o){ return new std::normal_distribution<>::param_type(o); } ) );
			cl.def("mean", (double (std::normal_distribution<>::param_type::*)() const) &std::normal_distribution<>::param_type::mean, "C++: std::normal_distribution<>::param_type::mean() const --> double");
			cl.def("stddev", (double (std::normal_distribution<>::param_type::*)() const) &std::normal_distribution<>::param_type::stddev, "C++: std::normal_distribution<>::param_type::stddev() const --> double");
		}

	}
}
