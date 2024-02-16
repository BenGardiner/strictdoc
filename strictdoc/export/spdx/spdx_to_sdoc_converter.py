from typing import Union

from spdx_tools.spdx3.model import RelationshipType, SpdxDocument
from spdx_tools.spdx3.model.software import File, Package, Snippet

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.node import (
    SDocNode,
    SDocNodeField,
)
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    FileReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc.models.type_system import (
    FileEntry,
    GrammarElementFieldString,
    GrammarElementRelationChild,
    GrammarElementRelationFile,
    GrammarElementRelationParent,
)
from strictdoc.export.spdx.spdx_sdoc_container import SPDXSDocContainer


class SPDXToSDocConverter:
    @staticmethod
    def convert(spdx_container: SPDXSDocContainer) -> Document:
        map_spdxref_to_sdoc = {}

        document = Document(
            mid=None,
            title=spdx_container.document.name,
            config=None,
            view=None,
            grammar=None,
            bibliography=None,
            free_texts=[],
            section_contents=[],
        )

        document.config.requirement_style = "Inline"

        document.grammar = SPDXToSDocConverter.create_grammar_for_spdx()
        document.grammar.parent = document

        """
        Document
        """
        document_requirement: SDocNode = SPDXToSDocConverter._convert_document(
            spdx_container.document,
            sdoc_document=document,
            sdoc_parent=document,
        )
        document_requirement.ng_level = document.ng_level + 1
        document.section_contents.append(document_requirement)

        """
        Package
        """
        package_requirement = SPDXToSDocConverter._convert_package(
            spdx_container.package,
            sdoc_document=document,
            sdoc_parent=document,
        )
        package_requirement.ng_level = document.ng_level + 1
        document.section_contents.append(package_requirement)

        """
        Files.
        """

        file_section = SDocSection(
            parent=document,
            mid=None,
            uid=None,
            custom_level=None,
            title="Files",
            requirement_prefix=None,
            free_texts=[],
            section_contents=[],
        )
        file_section.ng_level = document.ng_level + 1
        document.section_contents.append(file_section)

        for file_ in spdx_container.files:
            requirement = SPDXToSDocConverter._convert_file(
                file_, document, file_section
            )

            file_section.section_contents.append(requirement)
            map_spdxref_to_sdoc[file_.spdx_id] = requirement

        """
        Snippets.
        """

        snippets_section = SDocSection(
            parent=document,
            mid=None,
            uid=None,
            custom_level=None,
            title="Snippets",
            requirement_prefix=None,
            free_texts=[],
            section_contents=[],
        )
        snippets_section.ng_level = document.ng_level + 1
        document.section_contents.append(snippets_section)

        for snippet_ in spdx_container.snippets:
            requirement = SPDXToSDocConverter._convert_snippet(
                snippet_, document, file_section, spdx_container
            )

            snippets_section.section_contents.append(requirement)
            map_spdxref_to_sdoc[snippet_.spdx_id] = requirement

        for relationship_ in spdx_container.relationships:
            if (
                relationship_.from_element in map_spdxref_to_sdoc
                and relationship_.to[0] in map_spdxref_to_sdoc
            ):
                if relationship_.relationship_type == RelationshipType.CONTAINS:
                    from_element = spdx_container.map_spdx_ref_to_objects[
                        relationship_.from_element
                    ]
                    to_element = spdx_container.map_spdx_ref_to_objects[
                        relationship_.to[0]
                    ]

                    from_element_sdoc = map_spdxref_to_sdoc[
                        from_element.spdx_id
                    ]
                    to_element_sdoc = map_spdxref_to_sdoc[to_element.spdx_id]

                    assert (
                        to_element_sdoc.reserved_uid is not None
                    ), to_element_sdoc

                    from_element_sdoc.references.append(
                        ChildReqReference(
                            parent=from_element_sdoc,
                            ref_uid=to_element_sdoc.reserved_uid,
                            role="CONTAINS",
                        )
                    )
                    from_element_sdoc.ordered_fields_lookup["REFS"] = [
                        SDocNodeField(
                            parent=from_element_sdoc,
                            field_name="REFS",
                            field_value=None,
                            field_value_multiline=None,
                            field_value_references=from_element_sdoc.references,
                        )
                    ]
                if (
                    relationship_.relationship_type
                    == RelationshipType.REQUIREMENT_FOR
                ):
                    from_element = spdx_container.map_spdx_ref_to_objects[
                        relationship_.from_element
                    ]
                    to_element = spdx_container.map_spdx_ref_to_objects[
                        relationship_.to[0]
                    ]

                    from_element_sdoc = map_spdxref_to_sdoc[
                        from_element.spdx_id
                    ]
                    to_element_sdoc = map_spdxref_to_sdoc[to_element.spdx_id]

                    assert (
                        to_element_sdoc.reserved_uid is not None
                    ), to_element_sdoc

                    from_element_sdoc.references.append(
                        ParentReqReference(
                            parent=from_element_sdoc,
                            ref_uid=to_element_sdoc.reserved_uid,
                            role="REQUIREMENT_FOR",
                        )
                    )
                    from_element_sdoc.ordered_fields_lookup["REFS"] = [
                        SDocNodeField(
                            parent=from_element_sdoc,
                            field_name="REFS",
                            field_value=None,
                            field_value_multiline=None,
                            field_value_references=from_element_sdoc.references,
                        )
                    ]
        return document

    @staticmethod
    def _convert_document(document: SpdxDocument, sdoc_document, sdoc_parent):
        requirement = SDocNode(
            parent=sdoc_parent,
            requirement_type="SPDX_PACKAGE",
            mid=None,
            fields=[],
            requirements=None,
        )
        requirement.ng_document_reference = DocumentReference()
        requirement.ng_document_reference.set_document(sdoc_document)

        requirement.set_field_value(
            field_name="UID", form_field_index=0, value=document.spdx_id
        )
        requirement.set_field_value(
            field_name="SPDXID", form_field_index=0, value=document.spdx_id
        )
        requirement.set_field_value(
            field_name="TITLE", form_field_index=0, value=document.name
        )
        requirement.set_field_value(
            field_name="STATEMENT", form_field_index=0, value=document.summary
        )
        requirement.ng_level = sdoc_parent.ng_level + 1
        return requirement

    @staticmethod
    def _convert_package(
        package: Package,
        sdoc_document: Document,
        sdoc_parent: Union[SDocSection, Document],
    ) -> SDocNode:
        requirement = SDocNode(
            parent=sdoc_parent,
            requirement_type="SPDX_PACKAGE",
            mid=None,
            fields=[],
            requirements=None,
        )
        requirement.ng_document_reference = DocumentReference()
        requirement.ng_document_reference.set_document(sdoc_document)

        requirement.set_field_value(
            field_name="UID", form_field_index=0, value=package.spdx_id
        )
        requirement.set_field_value(
            field_name="SPDXID", form_field_index=0, value=package.spdx_id
        )
        requirement.set_field_value(
            field_name="PRIMARY_PURPOSE",
            form_field_index=0,
            value=package.primary_purpose.name,
        )
        requirement.set_field_value(
            field_name="TITLE", form_field_index=0, value=package.name
        )
        requirement.set_field_value(
            field_name="STATEMENT", form_field_index=0, value=package.summary
        )
        if package.summary is not None:
            requirement.set_field_value(
                field_name="SUMMARY", form_field_index=0, value=package.summary
            )
        requirement.ng_level = sdoc_parent.ng_level + 1
        return requirement

    @staticmethod
    def _convert_file(
        file: File,
        sdoc_document: Document,
        sdoc_parent: Union[SDocSection, Document],
    ) -> SDocNode:
        fields = []
        requirement = SDocNode(
            parent=sdoc_parent,
            requirement_type="SPDX_FILE",
            mid=None,
            fields=fields,
            requirements=None,
        )
        requirement.ng_document_reference = DocumentReference()
        requirement.ng_document_reference.set_document(sdoc_document)

        requirement.set_field_value(
            field_name="UID", form_field_index=0, value=file.spdx_id
        )
        requirement.set_field_value(
            field_name="SPDXID", form_field_index=0, value=file.spdx_id
        )
        requirement.set_field_value(
            field_name="PRIMARY_PURPOSE",
            form_field_index=0,
            value=file.primary_purpose.name,
        )
        requirement.set_field_value(
            field_name="SUMMARY", form_field_index=0, value=file.summary
        )
        requirement.set_field_value(
            field_name="TITLE", form_field_index=0, value=file.name
        )
        requirement.ng_level = sdoc_parent.ng_level + 1

        requirement.references = [
            FileReference(
                parent=requirement,
                g_file_entry=FileEntry(
                    parent=None,
                    g_file_format=None,
                    g_file_path=file.name,
                    g_line_range=None,
                ),
            )
        ]
        requirement.ordered_fields_lookup["REFS"] = [
            SDocNodeField(
                parent=requirement,
                field_name="REFS",
                field_value=None,
                field_value_multiline=None,
                field_value_references=requirement.references,
            )
        ]

        return requirement

    @staticmethod
    def _convert_snippet(
        snippet: Snippet,
        sdoc_document: Document,
        sdoc_parent: Union[SDocSection, Document],
        spdx_container: SPDXSDocContainer,
    ) -> SDocNode:
        fields = []
        requirement = SDocNode(
            parent=sdoc_parent,
            requirement_type="SPDX_SNIPPET",
            mid=None,
            fields=fields,
            requirements=None,
        )
        requirement.ng_document_reference = DocumentReference()
        requirement.ng_document_reference.set_document(sdoc_document)

        requirement.set_field_value(
            field_name="UID", form_field_index=0, value=snippet.spdx_id
        )
        requirement.set_field_value(
            field_name="SPDXID", form_field_index=0, value=snippet.spdx_id
        )
        requirement.set_field_value(
            field_name="PRIMARY_PURPOSE",
            form_field_index=0,
            value=snippet.primary_purpose.name,
        )
        requirement.set_field_value(
            field_name="SUMMARY", form_field_index=0, value=snippet.summary
        )
        requirement.set_field_value(
            field_name="TITLE", form_field_index=0, value=snippet.name
        )

        spdx_file_id = spdx_container.map_spdx_snippets_to_files[
            snippet.spdx_id
        ]
        spdx_file = spdx_container.map_spdx_ref_to_objects[spdx_file_id]

        requirement.references = [
            FileReference(
                parent=requirement,
                g_file_entry=FileEntry(
                    parent=None,
                    g_file_format=None,
                    g_file_path=spdx_file.name,
                    g_line_range=f"{snippet.line_range.begin}, {snippet.line_range.end - 1}",
                ),
            )
        ]
        requirement.ordered_fields_lookup["REFS"] = [
            SDocNodeField(
                parent=requirement,
                field_name="REFS",
                field_value=None,
                field_value_multiline=None,
                field_value_references=requirement.references,
            )
        ]

        requirement.ng_level = sdoc_parent.ng_level + 1
        return requirement

    @staticmethod
    def create_grammar_for_spdx():
        elements = []

        """
        SPDX Document
        """
        fields = [
            GrammarElementFieldString(
                parent=None,
                title="UID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SPDXID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="TITLE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="STATEMENT",
                human_title=None,
                required="False",
            ),
        ]

        document_element = GrammarElement(
            parent=None,
            tag="SPDX_DOCUMENT",
            fields=fields,
            relations=[
                GrammarElementRelationChild(
                    parent=None,
                    relation_type="Child",
                    relation_role="CONTAINS",
                ),
            ],
        )
        elements.append(document_element)

        """
        SPDX Package
        """
        fields = [
            GrammarElementFieldString(
                parent=None,
                title="UID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SPDXID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="PRIMARY_PURPOSE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="TITLE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="STATEMENT",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SUMMARY",
                human_title=None,
                required="False",
            ),
        ]

        package_element = GrammarElement(
            parent=None,
            tag="SPDX_PACKAGE",
            fields=fields,
            relations=[
                GrammarElementRelationChild(
                    parent=None,
                    relation_type="Child",
                    relation_role="CONTAINS",
                ),
            ],
        )
        elements.append(package_element)

        """
        SPDX File.
        """
        fields = [
            GrammarElementFieldString(
                parent=None,
                title="UID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SPDXID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="PRIMARY_PURPOSE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SUMMARY",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="TITLE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="STATEMENT",
                human_title=None,
                required="False",
            ),
        ]

        file_element = GrammarElement(
            parent=None,
            tag="SPDX_FILE",
            fields=fields,
            relations=[
                GrammarElementRelationChild(
                    parent=None,
                    relation_type="Child",
                    relation_role="CONTAINS",
                ),
                GrammarElementRelationFile(
                    parent=None,
                    relation_type="File",
                ),
            ],
        )
        elements.append(file_element)

        """
        SPDX Snippet
        """
        fields = [
            GrammarElementFieldString(
                parent=None,
                title="UID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SPDXID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="PRIMARY_PURPOSE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SUMMARY",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="TITLE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="STATEMENT",
                human_title=None,
                required="False",
            ),
        ]

        elements.append(
            GrammarElement(
                parent=None,
                tag="SPDX_SNIPPET",
                fields=fields,
                relations=[
                    GrammarElementRelationParent(
                        parent=None,
                        relation_type="Parent",
                        relation_role="REQUIREMENT_FOR",
                    ),
                    GrammarElementRelationFile(
                        parent=None,
                        relation_type="File",
                    ),
                ],
            )
        )

        """
        Create Grammar.
        """
        grammar = DocumentGrammar(None, elements=elements)
        return grammar
