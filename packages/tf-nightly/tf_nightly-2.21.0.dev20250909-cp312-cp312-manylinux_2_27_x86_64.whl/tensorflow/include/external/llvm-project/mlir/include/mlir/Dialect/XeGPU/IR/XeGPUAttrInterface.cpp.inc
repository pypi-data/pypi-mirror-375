/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Definitions                                                      *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/


/// Check the availability of workgroup level layouts
bool mlir::xegpu::DistributeLayoutAttr::isForWorkgroup() const {
      return getImpl()->isForWorkgroup(getImpl(), *this);
  }

/// Check the availability of subgroup level layouts
bool mlir::xegpu::DistributeLayoutAttr::isForSubgroup() const {
      return getImpl()->isForSubgroup(getImpl(), *this);
  }

/// Get the rank of attribute
int64_t mlir::xegpu::DistributeLayoutAttr::getRank() const {
      return getImpl()->getRank(getImpl(), *this);
  }

/// Get the num of effective subgroups
int64_t mlir::xegpu::DistributeLayoutAttr::getNumSubgroups() const {
      return getImpl()->getNumSubgroups(getImpl(), *this);
  }

/// Get the SgLayout field of the attribute as integer array
SmallVector<int64_t> mlir::xegpu::DistributeLayoutAttr::getSgLayoutAsInt() const {
      return getImpl()->getSgLayoutAsInt(getImpl(), *this);
  }

/// Get the SgData field of the attribute as integer array
SmallVector<int64_t> mlir::xegpu::DistributeLayoutAttr::getSgDataAsInt() const {
      return getImpl()->getSgDataAsInt(getImpl(), *this);
  }

/// Get the InstData field of the attribute as integer array
SmallVector<int64_t> mlir::xegpu::DistributeLayoutAttr::getInstDataAsInt() const {
      return getImpl()->getInstDataAsInt(getImpl(), *this);
  }

/// Get the LaneLayout field of the attribute as integer array
SmallVector<int64_t> mlir::xegpu::DistributeLayoutAttr::getLaneLayoutAsInt() const {
      return getImpl()->getLaneLayoutAsInt(getImpl(), *this);
  }

/// Get the LaneData field of the attribute as integer array
SmallVector<int64_t> mlir::xegpu::DistributeLayoutAttr::getLaneDataAsInt() const {
      return getImpl()->getLaneDataAsInt(getImpl(), *this);
  }

/// Derive a new layout by dropping sgLayout and sgData
xegpu::DistributeLayoutAttr mlir::xegpu::DistributeLayoutAttr::dropSgLayoutAndData() const {
      return getImpl()->dropSgLayoutAndData(getImpl(), *this);
  }

/// Derive a new layout by dropping InstData
xegpu::DistributeLayoutAttr mlir::xegpu::DistributeLayoutAttr::dropInstData() const {
      return getImpl()->dropInstData(getImpl(), *this);
  }

/// Delinearizes a linear subgroup ID into its multidimensional
///                       indices based on the effective subgroup layout.
FailureOr<SmallVector<Value>> mlir::xegpu::DistributeLayoutAttr::delinearizeSubgroupId(OpBuilder & builder, Location loc, Value linearId) const {
      return getImpl()->delinearizeSubgroupId(getImpl(), *this, builder, loc, linearId);
  }

/// Generates instructions to compute multidimensional offsets for blocks
///                       assigned to a subgroup identified by linearId. The shape parameter
///                       represents the workgroup-level problem size. Each subgroup may access
///                       multiple blocks according to round-robin distribution rules.
FailureOr<SmallVector<SmallVector<Value>>> mlir::xegpu::DistributeLayoutAttr::getOffsets(OpBuilder & builder, Location loc, Value linearId, ArrayRef<int64_t> shape) const {
      return getImpl()->getOffsets(getImpl(), *this, builder, loc, linearId, shape);
  }
