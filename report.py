# Copyright (c) 2014 Martin Abente - tch@sugarlabs.org

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA

import os
from tempfile import NamedTemporaryFile

from backend.logcollect import LogCollect
from backend.zendesk import FieldHelper, Ticket, Attachment


def send_report(data):
    """
    data: dict
        subject: str
        body: str
        name: str
        email: str
        school: str
        phone: str
        serial: str
        build: str
        files: list
            file: dict
                path: str
                name: str
                type: str
    """
    tempfile = NamedTemporaryFile(delete=False)
    tempfile.close()

    collector = LogCollect()
    collector.write_logs(archive=tempfile.name, logbytes=0)

    data['files'].append({'path': tempfile.name,
                          'name': 'logs.zip',
                          'type': 'application/zip'})

    uploads = []
    for file in data['files']:
        attachment = Attachment()
        attachment.create(file['path'],
                          file['name'],
                          file['type'])
        uploads.append(attachment.token())

    os.remove(tempfile.name)

    helper = FieldHelper()
    fields = []
    fields.append(helper.get_field(data['school'], 2))
    fields.append(helper.get_field(data['phone'], 4))
    fields.append(helper.get_field(data['serial'], 5))
    fields.append(helper.get_field(data['build'], 6))

    ticket = Ticket()
    ticket.create(data['subject'],
                  data['body'],
                  uploads,
                  data['name'],
                  data['email'],
                  fields)
