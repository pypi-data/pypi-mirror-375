import datetime
from django.http import Http404, HttpResponse, JsonResponse
from .xsams_generators import xsams, get_timestamp
from refs.serializers import RefSerializer

# XXX
from .xsams_settings import NODEID


def add_headers(headers, response):
    """
    Attach the headers in the dictionary headers to the response object
    and return it.

    """

    for header_name in headers:
        response["VAMDC-%s" % header_name] = headers[header_name]
    return response


def export_xsams(filtered_qs, **kwargs):
    response = HttpResponse(xsams(filtered_qs, **kwargs), "text/xml")
    # Windows doesn't like colons: replace them with hyphens in the filename.
    timestamp = get_timestamp().replace(":", "-")
    filename = "{}-{}.xsams".format(NODEID, timestamp)
    response["Content-Disposition"] = "attachment; filename={}".format(filename)

    headers = {}
    return add_headers(headers, response)


def export_json(filtered_qs):
    serializer = RefSerializer(filtered_qs, many=True)
    response = JsonResponse(serializer.data, safe=False)
    return response


def export_bibtex(filtered_qs):
    # XXX
    pass


_export_refs = {
    "xsams": export_xsams,
    "json": export_json,
}


def export_refs(filtered_qs, output_format, **kwargs):
    try:
        return _export_refs[output_format.lower()](filtered_qs, **kwargs)
    except KeyError:
        raise Http404
