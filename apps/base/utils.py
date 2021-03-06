import base64
import os
import uuid

from django.utils.deconstruct import deconstructible

from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination


class StandardResultSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


def paginated_queryset(queryset, request, pagination_class=StandardResultSetPagination()):
    '''
        Return a paginated result for a queryset
    '''
    paginator = pagination_class
    result_page = paginator.paginate_queryset(queryset, request)
    return (paginator, result_page)


@deconstructible
class RandomFileName(object):
    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        extension = os.path.splitext(filename)[1]
        path = self.path
        if 'id' in self.path and instance.pk:
            path = self.path.format(id=instance.pk)
        filename = '{}{}'.format(uuid.uuid4(), extension)
        filename = os.path.join(path, filename)
        return filename


def get_model_object(model_name):
    def get_model_by_pk(pk):
        try:
            model_object = model_name.objects.get(pk=pk)
            return model_object
        except model_name.DoesNotExist:
            raise NotFound('{} {} does not exist'.format(model_name.__name__, pk))
    get_model_by_pk.__name__ = 'get_{}_object'.format(model_name.__name__.lower())
    return get_model_by_pk


def encode_data(data):
    """
    Turn `data` into a hash and an encoded string, suitable for use with `decode_data`.
    Assume `data` is an iterable consists of byte-like objects.
    """
    encoded = []
    for i in data:
        encoded.append(base64.encodebytes(i).decode().split("=")[0])
    return encoded


def decode_data(data):
    """
    The inverse of `encode_data`.
    Assume `data` is an iterable consists of strings (from function `encode_data`).
    """
    decoded = []
    for i in data:
        s = i + "=="
        decoded.append(base64.decodebytes(s.encode()))
    return decoded
