from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import MultiPartRenderer

class ApiFormDataMixin:
    parser_classes = [MultiPartParser, FormParser]
    # renderer_classes = [MultiPartRenderer]
