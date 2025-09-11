// @HEADER
// *****************************************************************************
//               Rapid Optimization Library (ROL) Package
//
// Copyright 2014 NTESS and the ROL contributors.
// SPDX-License-Identifier: BSD-3-Clause
// *****************************************************************************
// @HEADER

#ifndef ROL_PEBBL_TPETRAINTEGERTRANSFORMATION_H
#define ROL_PEBBL_TPETRAINTEGERTRANSFORMATION_H

#include "ROL_PEBBL_IntegerTransformation.hpp"
#include "ROL_TpetraMultiVector.hpp"

/** @ingroup func_group
    \class ROL::PEBBL::TpetraIntegerTransformation
    \brief Defines the pebbl transform operator interface for TpetraMultiVectors.

    ROL's pebbl constraint interface is designed to set individual components
    of a vector to a fixed value.  The range space is the same as the domain.

    ---
*/


namespace ROL {
namespace PEBBL {

template <class Real>
class TpetraIntegerTransformation : public IntegerTransformation<Real> {
private:
  Ptr<Tpetra::MultiVector<>> getData(Vector<Real> &x) const {
    return dynamic_cast<TpetraMultiVector<Real>&>(x).getVector();
  }

 using IntegerTransformation<Real>::map_; 

public:
  TpetraIntegerTransformation(void)
    : IntegerTransformation<Real>() {}

  TpetraIntegerTransformation(const TpetraIntegerTransformation &T)
    : IntegerTransformation<Real>(T) {}

  void fixValues(Vector<Real> &c, bool zero = false) const {
    Teuchos::ArrayView<Real> cview = (getData(c)->getDataNonConst(0))();
    for (auto it=map_.begin(); it!=map_.end(); ++it) {
      cview[it->first] = (zero ? static_cast<Real>(0) : it->second);
    }
  }

}; // class TpetraIntegerTransformation

} // namespace PEBBL
} // namespace ROL

#endif
