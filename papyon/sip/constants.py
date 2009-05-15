# -*- coding: utf-8 -*-
#
# papyon - a python client library for Msn
#
# Copyright (C) 2009 Collabora Ltd.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

SHORT_HEADERS = {
    "call-id": "i",
    "contact": "m",
    "content-encoding": "e",
    "content-length": "l",
    "content-type": "c",
    "from": "f",
    "subject": "s",
    "to": "t",
    "via": "v",
}

MESSAGE_TYPES = {
    100: "Trying",
    180: "Ringing",
    181: "Call Is Being Forwarded",
    182: "Queued",
    183: "Session Progress",

    200: "OK",

    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Moved Temporarily",
    305: "Use Proxy",
    380: "Alternative Service",

    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    410: "Gone",
    413: "Request Entity Too Large",
    414: "Request-URI Too Long",
    415: "Unsupported Media Type",
    416: "Unsupported URI Scheme",
    420: "Bad Extension",
    421: "Extension Required",
    423: "Interval Too Brief",
    480: "Temporarily Unavailable",
    481: "Call/Transaction Does Not Exist",
    482: "Loop Detected",
    483: "Too Many Hops",
    484: "Address Incomplete",
    485: "Ambiguous",
    486: "Busy Here",
    487: "Request Terminated",
    488: "Not Acceptable Here",
    491: "Request Pending",
    493: "Undecipherable",

    500: "Server Internal Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Server Time-out",
    505: "Version Not Supported",
    513: "Message Too Large",

    600: "Busy Everywhere",
    603: "Decline",
    604: "Does Not Exist Anywhere",
    606: "Not Acceptable"
}

VID_XCAPS = "34 65537:352:288:15.0:256000:1;131074:176:144:15.0:180000:1"

class COMPONENTS:
    RTP = 1
    RTCP = 2