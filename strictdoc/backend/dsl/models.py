import collections


class Document(object):
    def __init__(self, name, section_contents=[]):
        self.name = name
        self.section_contents = section_contents
        self.path = "<No document path>"

        self.ng_sections = []
        self.ng_level = 0

    def __str__(self):
        return "Document: <name: {}, section_contents: {}>".format(
            self.name, self.section_contents
        )

    def __repr__(self):
        return self.__str__()

    def assign_path(self, path):
        assert isinstance(path, str)
        self.path = path

    def ng_toc_section_iterator(self):
        task_list = collections.deque([self])

        while True:
            current = task_list.popleft()

            task_list.extendleft(reversed(current.ng_sections))

            if not task_list:
                break

            yield task_list[0]

    def ng_section_iterator(self):
        task_list = collections.deque([self])

        while True:
            current = task_list.popleft()

            if isinstance(current, Section) or isinstance(current, Document):
                task_list.extendleft(reversed(current.section_contents))

            if isinstance(current, CompositeRequirement):
                task_list.extendleft(reversed(current.requirements))

            if not task_list:
                break

            yield task_list[0]


class ReqComment(object):
    def __init__(self, parent, comment):
        self.parent = parent
        self.comment = comment

    def __str__(self):
        return "Comment: <{}>".format(
            self.comment
        )

    def __repr__(self):
        return self.__str__()

    def comment_by_paragraphs(self):
        paragraphs = self.comment.split('\n\n')
        return paragraphs


class Section(object):
    def __init__(self, parent, level, title, section_contents):
        self.parent = parent
        self.level = int(level)
        self.title = title
        self.section_contents = section_contents

        self.ng_level = self.level
        self.ng_sections = []

    def __str__(self):
        return "Section: <level: {}, title: {}, section_contents: {}>".format(
            self.level, self.title, self.section_contents
        )

    def __repr__(self):
        return self.__str__()

    @property
    def is_requirement(self):
        return False

    @property
    def is_section(self):
        return True


class Requirement(object):
    def __init__(self,
                 parent,
                 statement,
                 statement_multiline,
                 uid,
                 status,
                 tags,
                 references,
                 title,
                 body,
                 comments,
                 requirements=None):
        assert parent

        self.parent = parent
        self.uid = uid.strip()
        self.status = status
        self.tags = tags
        self.references: [Reference] = references
        self.title = title
        self.statement = statement
        self.statement_multiline = statement_multiline
        self.body = body
        self.comments = comments
        self.requirements = requirements

        self.ng_level = None

    def __str__(self):
        return "{}: <uid: {}, title_or_none: {}, statement: {}, comments: {}>".format(
            self.__class__.__name__,
            self.uid, self.title, self.statement, self.comments
        )

    def __repr__(self):
        return self.__str__()

    @property
    def is_requirement(self):
        return True

    @property
    def is_section(self):
        return False

    def statement_as_html_blocks(self):
        if self.statement:
            return [self.statement]
        elif self.statement_multiline:
            return self.statement_multiline.split('\n\n')


class CompositeRequirement(Requirement):
    def __init__(self, parent, **fields):
        super(CompositeRequirement, self).__init__(parent, **fields)


# class Body(object):
#     def __init__(self, parent, body_content=[]):
#         self.parent = parent
#         self.body_content = body_content
#
#     def __str__(self):
#         return "Body: <{}>".format(
#             self.body_content
#         )
#
#     def __repr__(self):
#         return self.__str__()


class Body(object):
    def __init__(self, parent, content):
        self.parent = parent
        self.content = content.strip()

    def __str__(self):
        return "Body: <{}>".format(
            self.content
        )

    def __repr__(self):
        return self.__str__()


class Reference(object):
    def __init__(self, parent, ref_type, path):
        self.parent = parent
        self.ref_type = ref_type
        self.path = path.strip()

    def __str__(self):
        return "Reference: <ref_type = {}, path = {}>".format(
            self.ref_type, self.path
        )

    def __repr__(self):
        return self.__str__()


class FreeText:
    def __init__(self, parent, text):
        self.parent = parent
        self.text = text

    @property
    def is_requirement(self):
        return False

    @property
    def is_section(self):
        return False

    @property
    def is_free_text(self):
        return True
