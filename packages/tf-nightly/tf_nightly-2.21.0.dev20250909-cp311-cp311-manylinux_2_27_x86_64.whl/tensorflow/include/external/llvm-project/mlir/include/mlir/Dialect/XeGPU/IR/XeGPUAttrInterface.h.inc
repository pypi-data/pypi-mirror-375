/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Declarations                                                     *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace xegpu {
/// Common trait for all XeGPU layouts.
class DistributeLayoutAttr;
namespace detail {
struct DistributeLayoutAttrInterfaceTraits {
  struct Concept {
    /// The methods defined by the interface.
    bool (*isForWorkgroup)(const Concept *impl, ::mlir::Attribute );
    bool (*isForSubgroup)(const Concept *impl, ::mlir::Attribute );
    int64_t (*getRank)(const Concept *impl, ::mlir::Attribute );
    int64_t (*getNumSubgroups)(const Concept *impl, ::mlir::Attribute );
    SmallVector<int64_t> (*getSgLayoutAsInt)(const Concept *impl, ::mlir::Attribute );
    SmallVector<int64_t> (*getSgDataAsInt)(const Concept *impl, ::mlir::Attribute );
    SmallVector<int64_t> (*getInstDataAsInt)(const Concept *impl, ::mlir::Attribute );
    SmallVector<int64_t> (*getLaneLayoutAsInt)(const Concept *impl, ::mlir::Attribute );
    SmallVector<int64_t> (*getLaneDataAsInt)(const Concept *impl, ::mlir::Attribute );
    xegpu::DistributeLayoutAttr (*dropSgLayoutAndData)(const Concept *impl, ::mlir::Attribute );
    xegpu::DistributeLayoutAttr (*dropInstData)(const Concept *impl, ::mlir::Attribute );
    FailureOr<SmallVector<Value>> (*delinearizeSubgroupId)(const Concept *impl, ::mlir::Attribute , OpBuilder &, Location, Value);
    FailureOr<SmallVector<SmallVector<Value>>> (*getOffsets)(const Concept *impl, ::mlir::Attribute , OpBuilder &, Location, Value, ArrayRef<int64_t>);
  };
  template<typename ConcreteAttr>
  class Model : public Concept {
  public:
    using Interface = ::mlir::xegpu::DistributeLayoutAttr;
    Model() : Concept{isForWorkgroup, isForSubgroup, getRank, getNumSubgroups, getSgLayoutAsInt, getSgDataAsInt, getInstDataAsInt, getLaneLayoutAsInt, getLaneDataAsInt, dropSgLayoutAndData, dropInstData, delinearizeSubgroupId, getOffsets} {}

    static inline bool isForWorkgroup(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline bool isForSubgroup(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline int64_t getRank(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline int64_t getNumSubgroups(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline SmallVector<int64_t> getSgLayoutAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline SmallVector<int64_t> getSgDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline SmallVector<int64_t> getInstDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline SmallVector<int64_t> getLaneLayoutAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline SmallVector<int64_t> getLaneDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline xegpu::DistributeLayoutAttr dropSgLayoutAndData(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline xegpu::DistributeLayoutAttr dropInstData(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline FailureOr<SmallVector<Value>> delinearizeSubgroupId(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId);
    static inline FailureOr<SmallVector<SmallVector<Value>>> getOffsets(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId, ArrayRef<int64_t> shape);
  };
  template<typename ConcreteAttr>
  class FallbackModel : public Concept {
  public:
    using Interface = ::mlir::xegpu::DistributeLayoutAttr;
    FallbackModel() : Concept{isForWorkgroup, isForSubgroup, getRank, getNumSubgroups, getSgLayoutAsInt, getSgDataAsInt, getInstDataAsInt, getLaneLayoutAsInt, getLaneDataAsInt, dropSgLayoutAndData, dropInstData, delinearizeSubgroupId, getOffsets} {}

    static inline bool isForWorkgroup(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline bool isForSubgroup(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline int64_t getRank(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline int64_t getNumSubgroups(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline SmallVector<int64_t> getSgLayoutAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline SmallVector<int64_t> getSgDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline SmallVector<int64_t> getInstDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline SmallVector<int64_t> getLaneLayoutAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline SmallVector<int64_t> getLaneDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline xegpu::DistributeLayoutAttr dropSgLayoutAndData(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline xegpu::DistributeLayoutAttr dropInstData(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline FailureOr<SmallVector<Value>> delinearizeSubgroupId(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId);
    static inline FailureOr<SmallVector<SmallVector<Value>>> getOffsets(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId, ArrayRef<int64_t> shape);
  };
  template<typename ConcreteModel, typename ConcreteAttr>
  class ExternalModel : public FallbackModel<ConcreteModel> {
  public:
    using ConcreteEntity = ConcreteAttr;
  };
};
template <typename ConcreteAttr>
struct DistributeLayoutAttrTrait;

} // namespace detail
class DistributeLayoutAttr : public ::mlir::AttributeInterface<DistributeLayoutAttr, detail::DistributeLayoutAttrInterfaceTraits> {
public:
  using ::mlir::AttributeInterface<DistributeLayoutAttr, detail::DistributeLayoutAttrInterfaceTraits>::AttributeInterface;
  template <typename ConcreteAttr>
  struct Trait : public detail::DistributeLayoutAttrTrait<ConcreteAttr> {};

  /// Check the availability of workgroup level layouts
  bool isForWorkgroup() const;

  /// Check the availability of subgroup level layouts
  bool isForSubgroup() const;

  /// Get the rank of attribute
  int64_t getRank() const;

  /// Get the num of effective subgroups
  int64_t getNumSubgroups() const;

  /// Get the SgLayout field of the attribute as integer array
  SmallVector<int64_t> getSgLayoutAsInt() const;

  /// Get the SgData field of the attribute as integer array
  SmallVector<int64_t> getSgDataAsInt() const;

  /// Get the InstData field of the attribute as integer array
  SmallVector<int64_t> getInstDataAsInt() const;

  /// Get the LaneLayout field of the attribute as integer array
  SmallVector<int64_t> getLaneLayoutAsInt() const;

  /// Get the LaneData field of the attribute as integer array
  SmallVector<int64_t> getLaneDataAsInt() const;

  /// Derive a new layout by dropping sgLayout and sgData
  xegpu::DistributeLayoutAttr dropSgLayoutAndData() const;

  /// Derive a new layout by dropping InstData
  xegpu::DistributeLayoutAttr dropInstData() const;

  /// Delinearizes a linear subgroup ID into its multidimensional
  ///                       indices based on the effective subgroup layout.
  FailureOr<SmallVector<Value>> delinearizeSubgroupId(OpBuilder & builder, Location loc, Value linearId) const;

  /// Generates instructions to compute multidimensional offsets for blocks
  ///                       assigned to a subgroup identified by linearId. The shape parameter
  ///                       represents the workgroup-level problem size. Each subgroup may access
  ///                       multiple blocks according to round-robin distribution rules.
  FailureOr<SmallVector<SmallVector<Value>>> getOffsets(OpBuilder & builder, Location loc, Value linearId, ArrayRef<int64_t> shape) const;
};
namespace detail {
  template <typename ConcreteAttr>
  struct DistributeLayoutAttrTrait : public ::mlir::AttributeInterface<DistributeLayoutAttr, detail::DistributeLayoutAttrInterfaceTraits>::Trait<ConcreteAttr> {
  };
}// namespace detail
} // namespace xegpu
} // namespace mlir
namespace mlir {
namespace xegpu {
template<typename ConcreteAttr>
bool detail::DistributeLayoutAttrInterfaceTraits::Model<ConcreteAttr>::isForWorkgroup(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).isForWorkgroup();
}
template<typename ConcreteAttr>
bool detail::DistributeLayoutAttrInterfaceTraits::Model<ConcreteAttr>::isForSubgroup(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).isForSubgroup();
}
template<typename ConcreteAttr>
int64_t detail::DistributeLayoutAttrInterfaceTraits::Model<ConcreteAttr>::getRank(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).getRank();
}
template<typename ConcreteAttr>
int64_t detail::DistributeLayoutAttrInterfaceTraits::Model<ConcreteAttr>::getNumSubgroups(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  std::optional<SmallVector<int64_t>> sgLayout = llvm::cast<ConcreteAttr>(tablegen_opaque_val).getSgLayoutAsInt();
                        if (sgLayout.has_value())
                          return computeProduct(*sgLayout);
                        return 0;
}
template<typename ConcreteAttr>
SmallVector<int64_t> detail::DistributeLayoutAttrInterfaceTraits::Model<ConcreteAttr>::getSgLayoutAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).getSgLayoutAsInt();
}
template<typename ConcreteAttr>
SmallVector<int64_t> detail::DistributeLayoutAttrInterfaceTraits::Model<ConcreteAttr>::getSgDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).getSgDataAsInt();
}
template<typename ConcreteAttr>
SmallVector<int64_t> detail::DistributeLayoutAttrInterfaceTraits::Model<ConcreteAttr>::getInstDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).getInstDataAsInt();
}
template<typename ConcreteAttr>
SmallVector<int64_t> detail::DistributeLayoutAttrInterfaceTraits::Model<ConcreteAttr>::getLaneLayoutAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).getLaneLayoutAsInt();
}
template<typename ConcreteAttr>
SmallVector<int64_t> detail::DistributeLayoutAttrInterfaceTraits::Model<ConcreteAttr>::getLaneDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).getLaneDataAsInt();
}
template<typename ConcreteAttr>
xegpu::DistributeLayoutAttr detail::DistributeLayoutAttrInterfaceTraits::Model<ConcreteAttr>::dropSgLayoutAndData(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).dropSgLayoutAndData();
}
template<typename ConcreteAttr>
xegpu::DistributeLayoutAttr detail::DistributeLayoutAttrInterfaceTraits::Model<ConcreteAttr>::dropInstData(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).dropInstData();
}
template<typename ConcreteAttr>
FailureOr<SmallVector<Value>> detail::DistributeLayoutAttrInterfaceTraits::Model<ConcreteAttr>::delinearizeSubgroupId(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).delinearizeSubgroupId(builder, loc, linearId);
}
template<typename ConcreteAttr>
FailureOr<SmallVector<SmallVector<Value>>> detail::DistributeLayoutAttrInterfaceTraits::Model<ConcreteAttr>::getOffsets(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId, ArrayRef<int64_t> shape) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).getOffsets(builder, loc, linearId, shape);
}
template<typename ConcreteAttr>
bool detail::DistributeLayoutAttrInterfaceTraits::FallbackModel<ConcreteAttr>::isForWorkgroup(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->isForWorkgroup(tablegen_opaque_val);
}
template<typename ConcreteAttr>
bool detail::DistributeLayoutAttrInterfaceTraits::FallbackModel<ConcreteAttr>::isForSubgroup(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->isForSubgroup(tablegen_opaque_val);
}
template<typename ConcreteAttr>
int64_t detail::DistributeLayoutAttrInterfaceTraits::FallbackModel<ConcreteAttr>::getRank(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->getRank(tablegen_opaque_val);
}
template<typename ConcreteAttr>
int64_t detail::DistributeLayoutAttrInterfaceTraits::FallbackModel<ConcreteAttr>::getNumSubgroups(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->getNumSubgroups(tablegen_opaque_val);
}
template<typename ConcreteAttr>
SmallVector<int64_t> detail::DistributeLayoutAttrInterfaceTraits::FallbackModel<ConcreteAttr>::getSgLayoutAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->getSgLayoutAsInt(tablegen_opaque_val);
}
template<typename ConcreteAttr>
SmallVector<int64_t> detail::DistributeLayoutAttrInterfaceTraits::FallbackModel<ConcreteAttr>::getSgDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->getSgDataAsInt(tablegen_opaque_val);
}
template<typename ConcreteAttr>
SmallVector<int64_t> detail::DistributeLayoutAttrInterfaceTraits::FallbackModel<ConcreteAttr>::getInstDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->getInstDataAsInt(tablegen_opaque_val);
}
template<typename ConcreteAttr>
SmallVector<int64_t> detail::DistributeLayoutAttrInterfaceTraits::FallbackModel<ConcreteAttr>::getLaneLayoutAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->getLaneLayoutAsInt(tablegen_opaque_val);
}
template<typename ConcreteAttr>
SmallVector<int64_t> detail::DistributeLayoutAttrInterfaceTraits::FallbackModel<ConcreteAttr>::getLaneDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->getLaneDataAsInt(tablegen_opaque_val);
}
template<typename ConcreteAttr>
xegpu::DistributeLayoutAttr detail::DistributeLayoutAttrInterfaceTraits::FallbackModel<ConcreteAttr>::dropSgLayoutAndData(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->dropSgLayoutAndData(tablegen_opaque_val);
}
template<typename ConcreteAttr>
xegpu::DistributeLayoutAttr detail::DistributeLayoutAttrInterfaceTraits::FallbackModel<ConcreteAttr>::dropInstData(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->dropInstData(tablegen_opaque_val);
}
template<typename ConcreteAttr>
FailureOr<SmallVector<Value>> detail::DistributeLayoutAttrInterfaceTraits::FallbackModel<ConcreteAttr>::delinearizeSubgroupId(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId) {
  return static_cast<const ConcreteAttr *>(impl)->delinearizeSubgroupId(tablegen_opaque_val, builder, loc, linearId);
}
template<typename ConcreteAttr>
FailureOr<SmallVector<SmallVector<Value>>> detail::DistributeLayoutAttrInterfaceTraits::FallbackModel<ConcreteAttr>::getOffsets(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId, ArrayRef<int64_t> shape) {
  return static_cast<const ConcreteAttr *>(impl)->getOffsets(tablegen_opaque_val, builder, loc, linearId, shape);
}
} // namespace xegpu
} // namespace mlir
