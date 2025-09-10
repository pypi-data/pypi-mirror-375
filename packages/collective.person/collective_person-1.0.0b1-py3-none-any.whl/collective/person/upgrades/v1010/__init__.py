from collective.person.utils import reindex_all_person_content
from Products.GenericSetup.tool import SetupTool


def reindex_persons(context: SetupTool):
    """Reindex all Person objects to update the index."""
    idxs = ["sortable_title", "Title", "SearchableText", "object_provides"]
    reindex_all_person_content(idxs)
