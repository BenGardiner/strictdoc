# mypy: disable-error-code="attr-defined,no-untyped-call,no-untyped-def,var-annotated"
from typing import Optional, Type, Union

from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.section import FreeText
from strictdoc.backend.sdoc.models.type_system import RequirementFieldName
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.html_fragment_writer import (
    HTMLFragmentWriter,
)
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.text_to_html_writer import TextToHtmlWriter
from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)


class MarkupRenderer:
    @staticmethod
    def create(
        markup,
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
        html_templates: HTMLTemplates,
        config: ProjectConfig,
        context_document: Optional[SDocDocument],
    ) -> "MarkupRenderer":
        assert isinstance(html_templates, HTMLTemplates)
        html_fragment_writer: Union[
            RstToHtmlFragmentWriter,
            Type[HTMLFragmentWriter],
            Type[TextToHtmlWriter],
        ]
        if not markup or markup == "RST":
            html_fragment_writer = RstToHtmlFragmentWriter(
                path_to_output_dir=config.export_output_dir,
                context_document=context_document,
            )
        elif markup == "HTML":
            html_fragment_writer = HTMLFragmentWriter
        else:
            html_fragment_writer = TextToHtmlWriter
        return MarkupRenderer(
            html_fragment_writer,
            traceability_index,
            link_renderer,
            html_templates,
            context_document,
        )

    def __init__(
        self,
        fragment_writer,
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
        html_templates: HTMLTemplates,
        context_document: Optional[SDocDocument],
    ):
        assert isinstance(traceability_index, TraceabilityIndex)
        assert isinstance(link_renderer, LinkRenderer)
        assert context_document is None or isinstance(
            context_document, SDocDocument
        ), context_document
        assert isinstance(html_templates, HTMLTemplates)

        self.fragment_writer = fragment_writer
        self.traceability_index = traceability_index
        self.link_renderer: LinkRenderer = link_renderer
        self.context_document: Optional[SDocDocument] = context_document

        # FIXME: Now that the underlying RST fragment caching is in place,
        # This caching could be removed. It is unlikely that it adds any serious
        # performance improvement.
        self.cache = {}
        self.rationale_cache = {}

        self.template_anchor = html_templates.jinja_environment().get_template(
            "rst/anchor.jinja"
        )

    def render_node_statement(self, document_type, node):
        assert isinstance(node, SDocNode)
        return self.render_node_field(document_type, node.get_content_field())

    def render_truncated_node_statement(self, document_type, node):
        assert isinstance(node, SDocNode)
        return self.render_node_field(
            document_type, node.get_content_field(), truncated=True
        )

    def render_node_rationale(self, document_type, node: SDocNode):
        assert isinstance(node, SDocNode)
        return self.render_node_field(
            document_type,
            node.get_field_by_name(RequirementFieldName.RATIONALE),
        )

    def render_node_field(
        self, document_type, node_field: SDocNodeField, truncated: bool = False
    ):
        assert isinstance(node_field, SDocNodeField), node_field

        if (document_type, node_field, truncated) in self.cache:
            return self.cache[(document_type, node_field, truncated)]

        parts_output = ""
        for part in node_field.parts:
            if isinstance(part, str):
                parts_output += part
            elif isinstance(part, InlineLink):
                linkable_node = (
                    self.traceability_index.get_linkable_node_by_uid(part.link)
                )
                href = self.link_renderer.render_node_link(
                    linkable_node, self.context_document, document_type
                )
                parts_output += self.fragment_writer.write_anchor_link(
                    linkable_node.get_display_title(), href
                )
            elif isinstance(part, Anchor):
                parts_output += self.template_anchor.render(
                    anchor=part,
                    traceability_index=self.traceability_index,
                    link_renderer=self.link_renderer,
                    document_type=DocumentType.document(),
                )
            else:
                raise NotImplementedError
        output = self.fragment_writer.write(parts_output)
        self.cache[(document_type, node_field, truncated)] = output

        return output

    def render_free_text(self, document_type, free_text):
        assert isinstance(free_text, FreeText)
        assert self.context_document is not None

        if (document_type, free_text) in self.cache:
            return self.cache[(document_type, free_text)]

        parts_output = ""
        for part in free_text.parts:
            if isinstance(part, str):
                parts_output += part
            elif isinstance(part, InlineLink):
                linkable_node = (
                    self.traceability_index.get_linkable_node_by_uid(part.link)
                )
                href = self.link_renderer.render_node_link(
                    linkable_node, self.context_document, document_type
                )
                parts_output += self.fragment_writer.write_anchor_link(
                    linkable_node.get_display_title(), href
                )
            elif isinstance(part, Anchor):
                parts_output += self.template_anchor.render(
                    anchor=part,
                    traceability_index=self.traceability_index,
                    link_renderer=self.link_renderer,
                    document_type=DocumentType.document(),
                )

        output = self.fragment_writer.write(parts_output)
        self.cache[(document_type, free_text)] = output

        return output
