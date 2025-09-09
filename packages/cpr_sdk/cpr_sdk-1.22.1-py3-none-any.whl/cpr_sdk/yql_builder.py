from string import Template
from typing import Optional

from rich import print as rprint

from cpr_sdk.models.search import Filters, SearchParameters


class YQLBuilder:
    """Used to assemble yql queries"""

    yql_base = Template(
        """
        select * from sources $SOURCES
            where $WHERE_CLAUSE
        limit 0
        |
            $CONTINUATION
        all(
            group(family_import_id)
            output(count())
            max($LIMIT)
            $SORT
            each(
                output(count())
                max($MAX_HITS_PER_FAMILY)
                each(
                    output(
                        summary(search_summary)
                    )
                )
            )
        )
    """
    )

    def __init__(self, params: SearchParameters, sensitive: bool = False) -> None:
        self.params = params
        self.sensitive = sensitive

    def build_sources(self) -> str:
        """Creates the part of the query that determines which sources to search"""
        if self.params.documents_only:
            return "family_document"
        else:
            return "family_document, document_passage"

    def build_search_term(self) -> str:
        """Create the part of the query that matches a users search text"""
        if self.params.all_results:
            return "( true )"
        if self.params.exact_match:
            return """
                (
                    (family_name_not_stemmed contains({stem: false}@query_string)) or
                    (family_description_not_stemmed contains({stem: false}@query_string)) or
                    (text_block_not_stemmed contains ({stem: false}@query_string))
                )
            """
        elif self.sensitive:
            return """
                (
                    (userInput(@query_string)) 
                )
            """
        elif self.params.by_document_title:
            return """
                (
                    (document_title_index contains(@query_string))
                )
            """
        else:
            # if specified in the search parameters, add a threshold for the distance
            # between the query and the text_embedding
            distance_threshold_clause = (
                f', "distanceThreshold": {self.params.distance_threshold}'
                if self.params.distance_threshold is not None
                else ""
            )

            return f"""
                (
                    (userInput(@query_string)) 
                    or (
                        [{{\"targetNumHits\": 1000{distance_threshold_clause}}}]
                        nearestNeighbor(text_embedding,query_embedding)
                    )
                )
            """

    def build_metadata_filter(self) -> Optional[str]:
        """Create the part of the query that limits to specific metadata"""
        metadata_filters = []
        if self.params.metadata:
            [
                metadata_filters.append(
                    f"""
                    (
                        metadata contains sameElement(
                            name contains '{metadata.name}',
                            value contains '{metadata.value}'
                        )
                    )
                    """
                )
                for metadata in self.params.metadata
            ]
            return f"({' and '.join(metadata_filters)})"
        return None

    def build_concepts_filter(self) -> Optional[str]:
        """
        Create the part of the query that limits to specific concepts.

        e.g:
        - `concepts.name contains 'floods' and concepts.name contains 'environment'`
        - `concepts.parent_concept_ids_flat matches 'Q123' and concepts.name contains 'environment'`
        """
        if self.params.concept_filters:
            concepts_query = []
            for concept in self.params.concept_filters:
                if concept.name == "parent_concept_ids_flat":
                    concepts_query.append(
                        f"concepts.{concept.name} matches '{concept.value}'"
                    )
                else:
                    concepts_query.append(
                        f"concepts.{concept.name} contains '{concept.value}'"
                    )
            return f"({' and '.join(concepts_query)})"
        return None

    def build_corpus_type_name_filter(self) -> Optional[str]:
        """Create the part of the query that limits to specific corpora"""
        if self.params.corpus_type_names:
            corpora = ", ".join([f"'{c}'" for c in self.params.corpus_type_names])
            return f"(corpus_type_name in({corpora}))"

    def build_corpus_import_ids_filter(self) -> Optional[str]:
        """Create the part of the query that limits to specific corpora import id"""
        if self.params.corpus_import_ids:
            corpora = ", ".join([f"'{c}'" for c in self.params.corpus_import_ids])
            return f"(corpus_import_id in({corpora}))"

    def build_family_filter(self) -> Optional[str]:
        """Create the part of the query that limits to specific families"""
        if self.params.family_ids:
            families = ", ".join([f"'{f}'" for f in self.params.family_ids])
            return f"(family_import_id in({families}))"
        return None

    def build_document_filter(self) -> Optional[str]:
        """Create the part of the query that limits to specific documents"""
        if self.params.document_ids:
            documents = ", ".join([f"'{d}'" for d in self.params.document_ids])
            return f"(document_import_id in({documents}))"
        return None

    def _inclusive_filters(self, filters: Filters, field_name: str) -> Optional[str]:
        values = getattr(filters, field_name)
        query_filters = []
        for value in values:
            query_filters.append(f'({field_name} contains "{value}")')
        if query_filters:
            return f"({' or '.join(query_filters)})"

    def build_year_start_filter(self) -> Optional[str]:
        """Create the part of the query that filters on a year range"""
        if self.params.year_range:
            start, _ = self.params.year_range
            if start:
                return f"(family_publication_year >= {start})"
        return None

    def build_year_end_filter(self) -> Optional[str]:
        """Create the part of the query that filters on a year range"""
        if self.params.year_range:
            _, end = self.params.year_range
            if end:
                return f"(family_publication_year <= {end})"
        return None

    def build_concept_count_filter(self) -> Optional[str]:
        """Create the part of the query that filters on concept counts"""
        concept_count_filters_subqueries = []
        if self.params.concept_count_filters:
            for concept_count_filter in self.params.concept_count_filters:
                concept_count_filters_subqueries.append(
                    f"""
                    {"!" if concept_count_filter.negate else ""}
                    (
                        concept_counts contains sameElement(
                            {
                        (
                            f'key contains "{concept_count_filter.concept_id}", '
                            if concept_count_filter.concept_id is not None
                            else ""
                        )
                    }
                            value {concept_count_filter.operand.value} {
                        concept_count_filter.count
                    }
                        )
                    )
                    """
                )

            return f"({' and '.join(concept_count_filters_subqueries)})"
        return None

    def build_where_clause(self) -> str:
        """Create the part of the query that adds filters"""
        filters = []
        filters.append(self.build_search_term())
        filters.append(self.build_family_filter())
        filters.append(self.build_document_filter())
        filters.append(self.build_corpus_type_name_filter())
        filters.append(self.build_corpus_import_ids_filter())
        filters.append(self.build_metadata_filter())
        filters.append(self.build_concepts_filter())
        if f := self.params.filters:
            filters.append(self._inclusive_filters(f, "family_geographies"))
            filters.append(self._inclusive_filters(f, "family_geography"))
            filters.append(self._inclusive_filters(f, "family_category"))
            filters.append(self._inclusive_filters(f, "document_languages"))
            filters.append(self._inclusive_filters(f, "family_source"))
        filters.append(self.build_year_start_filter())
        filters.append(self.build_year_end_filter())
        filters.append(self.build_concept_count_filter())
        return " and ".join([f for f in filters if f])  # Remove empty

    def build_continuation(self) -> str:
        """Create the part of the query that adds continuation tokens"""
        if self.params.continuation_tokens:
            continuations = ", ".join(f"'{c}'" for c in self.params.continuation_tokens)
            return f"{{ 'continuations': [{continuations}] }}"
        else:
            return ""

    def build_limit(self) -> int:
        """Create the part of the query limiting the number of families returned"""
        return self.params.limit

    def build_sort(self) -> str:
        """Creates the part of the query used for sorting by different fields"""
        sort_by = self.params.vespa_sort_by
        sort_order = self.params.vespa_sort_order

        if not sort_by or not sort_order:
            return ""
        return f"order({sort_order}max({sort_by}))"

    def build_max_hits_per_family(self) -> int:
        """Create the part of the query limiting passages within a family returned"""
        return self.params.max_hits_per_family

    def to_str(self) -> str:
        """Assemble the yql from parts using the template"""
        yql = self.yql_base.substitute(
            SOURCES=self.build_sources(),
            WHERE_CLAUSE=self.build_where_clause(),
            CONTINUATION=self.build_continuation(),
            LIMIT=self.build_limit(),
            SORT=self.build_sort(),
            MAX_HITS_PER_FAMILY=self.build_max_hits_per_family(),
        )
        return " ".join(yql.split())


if __name__ == "__main__":
    # YQL example
    params = SearchParameters(
        query_string="climate",
        exact_match=False,
        limit=10,
        max_hits_per_family=10,
        filters=Filters(
            **{"document_languages": ["value"], "family_source": ["value"]}
        ),
        year_range=(2000, 2020),
        continuation_tokens=None,
    )

    yql_new = YQLBuilder(
        params=params,
        sensitive=False,
    ).to_str()

    rprint(yql_new)
