from hug.format import content_type
from multipart import MultipartParser


@content_type('multipart/form-data')
def multipart(body, **header_params):
    if header_params and 'boundary' in header_params:
        if type(header_params['boundary']) is str:
            header_params['boundary'] = header_params['boundary'].encode()
    parser = MultipartParser(
        stream=body, boundary=header_params['boundary'], disk_limit=17179869184)
    form = dict(zip([p.name for p in parser.parts()],
                    [(p.filename, p.file) if p.filename else p.file.read().decode() for p in parser.parts()]))
    return form
