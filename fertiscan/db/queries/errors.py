"""
Query exceptions hierarchy:

    Exception
    |__QueryError
       |__InspectionQueryError
       |__LabelInformationQueryError
       |__LabelDimensionQueryError
       |__MetricQueryError
       |__UnitQueryError
       |__ElementCompoundQueryError
       |__MicronutrientQueryError
       |__GuaranteedAnalysisQueryError
       |__OrganizationQueryError
       |__OrganizationInformationQueryError
       |__LocationQueryError
       |__RegionQueryError
       |__ProvinceQueryError
       |__SpecificationQueryError
       |__SubLabelQueryError
       |__SubTypeQueryError

Each QueryError sub type exception also has specific errors sub types related to creation, retrieval, updating, and deletion, as well as a 'not found' error.
"""

from functools import wraps

from psycopg import Error


class QueryError(Exception):
    """Base exception for all query errors."""

    pass


class InspectionQueryError(QueryError):
    """Base exception for all inspection-related query errors."""

    pass


class InspectionNotFoundError(InspectionQueryError):
    """Raised when an inspection is not found."""

    pass


class InspectionCreationError(InspectionQueryError):
    """Raised when an error occurs during the creation of an inspection."""

    pass


class InspectionUpdateError(InspectionQueryError):
    """Raised when an error occurs during the updating of an inspection."""

    pass


class InspectionRetrievalError(InspectionQueryError):
    """Raised when an error occurs during the retrieval of an inspection."""

    pass


class InspectionDeleteError(InspectionQueryError):
    """Raised when an error occurs during the deletion of an inspection."""

    pass


class LabelInformationQueryError(QueryError):
    """Base exception for all label information-related query errors."""

    pass


class LabelInformationNotFoundError(LabelInformationQueryError):
    """Raised when a label information is not found."""

    pass


class LabelInformationCreationError(LabelInformationQueryError):
    """Raised when an error occurs during the creation of a label information."""

    pass


class LabelInformationUpdateError(LabelInformationQueryError):
    """Raised when an error occurs during the updating of a label information."""

    pass


class LabelInformationRetrievalError(LabelInformationQueryError):
    """Raised when an error occurs during the retrieval of a label information."""

    pass


class LabelInformationDeleteError(LabelInformationQueryError):
    """Raised when an error occurs during the deletion of a label information."""

    pass


class LabelDimensionQueryError(QueryError):
    """Base exception for all label dimension-related query errors."""

    pass


class LabelDimensionNotFoundError(LabelDimensionQueryError):
    """Raised when a label dimension is not found."""

    pass


class MetricQueryError(QueryError):
    """Base exception for all metric-related query errors."""

    pass


class MetricNotFoundError(MetricQueryError):
    """Raised when a metric is not found."""

    pass


class MetricCreationError(MetricQueryError):
    """Raised when an error occurs during the creation of a metric."""

    pass


class MetricUpdateError(MetricQueryError):
    """Raised when an error occurs during the updating of a metric."""

    pass


class MetricRetrievalError(MetricQueryError):
    """Raised when an error occurs during the retrieval of a metric."""

    pass


class MetricDeleteError(MetricQueryError):
    """Raised when an error occurs during the deletion of a metric."""

    pass


class UnitQueryError(QueryError):
    """Base exception for all unit-related query errors."""

    pass


class UnitNotFoundError(UnitQueryError):
    """Raised when a unit is not found."""

    pass


class UnitCreationError(UnitQueryError):
    """Raised when an error occurs during the creation of a unit."""

    pass


class UnitUpdateError(UnitQueryError):
    """Raised when an error occurs during the updating of a unit."""

    pass


class UnitRetrievalError(UnitQueryError):
    """Raised when an error occurs during the retrieval of a unit."""

    pass


class UnitDeleteError(UnitQueryError):
    """Raised when an error occurs during the deletion of a unit."""

    pass


class ElementCompoundQueryError(QueryError):
    """Base exception for all element compound-related query errors."""

    pass


class ElementCompoundNotFoundError(ElementCompoundQueryError):
    """Raised when an element compound is not found."""

    pass


class ElementCompoundCreationError(ElementCompoundQueryError):
    """Raised when an error occurs during the creation of an element compound."""

    pass


class ElementCompoundUpdateError(ElementCompoundQueryError):
    """Raised when an error occurs during the updating of an element compound."""

    pass


class ElementCompoundRetrievalError(ElementCompoundQueryError):
    """Raised when an error occurs during the retrieval of an element compound."""

    pass


class ElementCompoundDeleteError(ElementCompoundQueryError):
    """Raised when an error occurs during the deletion of an element compound."""

    pass


class MicronutrientQueryError(QueryError):
    """Base exception for all micronutrient-related query errors."""

    pass


class MicronutrientNotFoundError(MicronutrientQueryError):
    """Raised when a micronutrient is not found."""

    pass


class MicronutrientCreationError(MicronutrientQueryError):
    """Raised when an error occurs during the creation of a micronutrient."""

    pass


class MicronutrientUpdateError(MicronutrientQueryError):
    """Raised when an error occurs during the updating of a micronutrient."""

    pass


class MicronutrientRetrievalError(MicronutrientQueryError):
    """Raised when an error occurs during the retrieval of a micronutrient."""

    pass


class MicronutrientDeleteError(MicronutrientQueryError):
    """Raised when an error occurs during the deletion of a micronutrient."""

    pass


class GuaranteedAnalysisQueryError(QueryError):
    """Base exception for all guaranteed analysis-related query errors."""

    pass


class GuaranteedAnalysisNotFoundError(GuaranteedAnalysisQueryError):
    """Raised when a guaranteed analysis is not found."""

    pass


class GuaranteedAnalysisCreationError(GuaranteedAnalysisQueryError):
    """Raised when an error occurs during the creation of a guaranteed analysis."""

    pass


class GuaranteedAnalysisUpdateError(GuaranteedAnalysisQueryError):
    """Raised when an error occurs during the updating of a guaranteed analysis."""

    pass


class GuaranteedAnalysisRetrievalError(GuaranteedAnalysisQueryError):
    """Raised when an error occurs during the retrieval of a guaranteed analysis."""

    pass


class GuaranteedAnalysisDeleteError(GuaranteedAnalysisQueryError):
    """Raised when an error occurs during the deletion of a guaranteed analysis."""

    pass


class OrganizationQueryError(QueryError):
    """Base exception for all organization-related query errors."""

    pass


class OrganizationNotFoundError(OrganizationQueryError):
    """Raised when an organization is not found."""

    pass


class OrganizationCreationError(OrganizationQueryError):
    """Raised when an error occurs during the creation of an organization."""

    pass


class OrganizationUpdateError(OrganizationQueryError):
    """Raised when an error occurs during the updating of an organization."""

    pass


class OrganizationRetrievalError(OrganizationQueryError):
    """Raised when an error occurs during the retrieval of an organization."""

    pass


class OrganizationDeleteError(OrganizationQueryError):
    """Raised when an error occurs during the deletion of an organization."""

    pass


class OrganizationInformationQueryError(QueryError):
    """Base exception for all organization information-related query errors."""

    pass


class OrganizationInformationNotFoundError(OrganizationInformationQueryError):
    """Raised when organization information is not found."""

    pass


class OrganizationInformationCreationError(OrganizationInformationQueryError):
    """Raised when an error occurs during the creation of organization information."""

    pass


class OrganizationInformationUpdateError(OrganizationInformationQueryError):
    """Raised when an error occurs during the updating of organization information."""

    pass


class OrganizationInformationRetrievalError(OrganizationInformationQueryError):
    """Raised when an error occurs during the retrieval of organization information."""

    pass


class OrganizationInformationDeleteError(OrganizationInformationQueryError):
    """Raised when an error occurs during the deletion of organization information."""

    pass


class LocationQueryError(QueryError):
    """Base exception for all location-related query errors."""

    pass


class LocationNotFoundError(LocationQueryError):
    """Raised when a location is not found."""

    pass


class LocationCreationError(LocationQueryError):
    """Raised when an error occurs during the creation of a location."""

    pass


class LocationUpdateError(LocationQueryError):
    """Raised when an error occurs during the updating of a location."""

    pass


class LocationRetrievalError(LocationQueryError):
    """Raised when an error occurs during the retrieval of a location."""

    pass


class LocationDeleteError(LocationQueryError):
    """Raised when an error occurs during the deletion of a location."""

    pass


class RegionQueryError(QueryError):
    """Base exception for all region-related query errors."""

    pass


class RegionNotFoundError(RegionQueryError):
    """Raised when a region is not found."""

    pass


class RegionCreationError(RegionQueryError):
    """Raised when an error occurs during the creation of a region."""

    pass


class RegionUpdateError(RegionQueryError):
    """Raised when an error occurs during the updating of a region."""

    pass


class RegionRetrievalError(RegionQueryError):
    """Raised when an error occurs during the retrieval of a region."""

    pass


class RegionDeleteError(RegionQueryError):
    """Raised when an error occurs during the deletion of a region."""

    pass


class ProvinceQueryError(QueryError):
    """Base exception for all province-related query errors."""

    pass


class ProvinceNotFoundError(ProvinceQueryError):
    """Raised when a province is not found."""

    pass


class ProvinceCreationError(ProvinceQueryError):
    """Raised when an error occurs during the creation of a province."""

    pass


class ProvinceUpdateError(ProvinceQueryError):
    """Raised when an error occurs during the updating of a province."""

    pass


class ProvinceRetrievalError(ProvinceQueryError):
    """Raised when an error occurs during the retrieval of a province."""

    pass


class ProvinceDeleteError(ProvinceQueryError):
    """Raised when an error occurs during the deletion of a province."""

    pass


class SpecificationQueryError(QueryError):
    """Base exception for all specification-related query errors."""

    pass


class SpecificationNotFoundError(SpecificationQueryError):
    """Raised when a specification is not found."""

    pass


class SpecificationCreationError(SpecificationQueryError):
    """Raised when an error occurs during the creation of a specification."""

    pass


class SpecificationUpdateError(SpecificationQueryError):
    """Raised when an error occurs during the updating of a specification."""

    pass


class SpecificationRetrievalError(SpecificationQueryError):
    """Raised when an error occurs during the retrieval of a specification."""

    pass


class SpecificationDeleteError(SpecificationQueryError):
    """Raised when an error occurs during the deletion of a specification."""

    pass


class SubLabelQueryError(QueryError):
    """Base exception for all sublabel-related query errors."""

    pass


class SubLabelNotFoundError(SubLabelQueryError):
    """Raised when a sublabel is not found."""

    pass


class SubLabelCreationError(SubLabelQueryError):
    """Raised when an error occurs during the creation of a sublabel."""

    pass


class SubLabelUpdateError(SubLabelQueryError):
    """Raised when an error occurs during the updating of a sublabel."""

    pass


class SubLabelRetrievalError(SubLabelQueryError):
    """Raised when an error occurs during the retrieval of a sublabel."""

    pass


class SubLabelDeleteError(SubLabelQueryError):
    """Raised when an error occurs during the deletion of a sublabel."""

    pass


class SubTypeQueryError(QueryError):
    """Base exception for all subtype-related query errors."""

    pass


class SubTypeNotFoundError(SubTypeQueryError):
    """Raised when a subtype is not found."""

    pass


class SubTypeCreationError(SubTypeQueryError):
    """Raised when an error occurs during the creation of a subtype."""

    pass


class SubTypeUpdateError(SubTypeQueryError):
    """Raised when an error occurs during the updating of a subtype."""

    pass


class SubTypeRetrievalError(SubTypeQueryError):
    """Raised when an error occurs during the retrieval of a subtype."""

    pass


class SubTypeDeleteError(SubTypeQueryError):
    """Raised when an error occurs during the deletion of a subtype."""

    pass


def handle_query_errors(error_cls=QueryError):
    """Decorator for handling query errors."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except QueryError:
                raise
            except Error as db_error:
                raise error_cls(f"Database error: {db_error}") from db_error
            except Exception as e:
                raise error_cls(f"Unexpected error: {e}") from e

        return wrapper

    return decorator
