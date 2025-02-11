from llama_index.core.vector_stores.types import MetadataFilter, MetadataFilters

def generate_filters(doc_ids=None):
    """
    Generate metadata filters for vector search.
    Filters out private documents and allows filtering by document IDs.
    """
    public_doc_filter = MetadataFilter(
        key="private",
        value="true",
        operator="!=",  # ✅ Exclude private documents
    )

    filters = [public_doc_filter]

    if doc_ids and len(doc_ids) > 0:
        selected_doc_filter = MetadataFilter(
            key="document_id",
            value=doc_ids,
            operator="in",
        )
        filters.append(selected_doc_filter)
        return MetadataFilters(filters=filters, condition="or")

    return MetadataFilters(filters=filters)
