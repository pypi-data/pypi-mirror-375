// @HEADER
// *****************************************************************************
//               Rapid Optimization Library (ROL) Package
//
// Copyright 2014 NTESS and the ROL contributors.
// SPDX-License-Identifier: BSD-3-Clause
// *****************************************************************************
// @HEADER

#ifndef ROL_FletcherStatusTest_H
#define ROL_FletcherStatusTest_H

#include "ROL_StatusTest.hpp"

/** \class ROL::FletcherStatusTest
    \brief Provides an interface to check status of optimization algorithms
           for problems with equality constraints.
*/


namespace ROL {

template <class Real>
class FletcherStatusTest : public StatusTest<Real> {
private:

  Real gtol_;
  Real ctol_;
  Real stol_;
  int  max_iter_;

public:

  virtual ~FletcherStatusTest() {}

  FletcherStatusTest( ROL::ParameterList &parlist ) {
    Real em6(1e-6);
    gtol_     = parlist.sublist("Status Test").get("Gradient Tolerance", em6);
    ctol_     = parlist.sublist("Status Test").get("Constraint Tolerance", em6);
    stol_     = parlist.sublist("Status Test").get("Step Tolerance", em6*gtol_);
    max_iter_ = parlist.sublist("Status Test").get("Iteration Limit", 100);
  }

  FletcherStatusTest( Real gtol = 1e-6, Real ctol = 1e-6, Real stol = 1e-12, int max_iter = 100 ) :  
    gtol_(gtol), ctol_(ctol), stol_(stol), max_iter_(max_iter) {}

  /** \brief Check algorithm status.
  */
  virtual bool check( AlgorithmState<Real> &state ) {
    if ( ((state.gnorm > gtol_) || (state.cnorm > ctol_)) && 
          (state.snorm > stol_) && (state.aggregateGradientNorm > gtol_) &&
          (state.iter  < max_iter_) && (!state.flag)) {
      return true;
    }
    else {
      state.statusFlag = ((state.gnorm <= gtol_) && (state.cnorm <= ctol_) ? EXITSTATUS_CONVERGED
                          : state.snorm <= stol_ ? EXITSTATUS_STEPTOL
                          : state.aggregateGradientNorm <= gtol_ ? EXITSTATUS_CONVERGED
                          : state.iter  >= max_iter_ ? EXITSTATUS_MAXITER
                          : state.flag==true ? EXITSTATUS_CONVERGED
                          : EXITSTATUS_LAST);
      return false;
    }
  }

}; // class FletcherStatusTest

} // namespace ROL

#endif

