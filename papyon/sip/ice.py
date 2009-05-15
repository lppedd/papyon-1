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

from papyon.sip.constants import *
from papyon.sip.sdp import *
from papyon.util.decorator import rw_property

class Session(object):

    def __init__(self, draft=0):
        self.draft = draft
        self._local_codecs = {}
        self._remote_codecs = {}
        self._local_candidates = {}
        self._remote_candidates = {}
        self._local_active = {}
        self._remote_active = {}

    def get_remote_codecs(self, name):
        return self._remote_codecs.get(name)

    def get_remote_candidates(self, name):
        return self._remote_candidates.get(name)

    def set_local_codecs(self, name, codecs):
        self._local_codecs[name] = codecs

    def set_local_candidates(self, name, candidates):
        self._local_candidates[name] = candidates

    def set_active_candidates(self, name, local, remote):
        self._local_active[name] = local
        self._remote_active[name] = remote

    def build_sdp(self):
        sdp = Message()
        for name, codecs in self._local_codecs.iteritems():
            media = self.build_media(name, codecs)
            sdp.medias[media.name] = media
        return sdp.build()

    def build_media(self, name, codecs):
        ip, port, rtcp = self.get_default_address(name)
        media = Media(name, ip, port, rtcp)
        media.codecs = codecs

        candidates = self.get_active_local_candidates(name)
        if candidates:
            if self.draft is 19:
                media.add_attribute("ice-ufrag", candidates[0].username)
                media.add_attribute("ice-pwd", candidates[0].password)
            for candidate in candidates:
                media.add_attribute("candidate", candidate.build_local())

        candidates = self.get_active_remote_candidates(name)
        if candidates:
            list = map(lambda c: c.build_remote(), candidates)
            media.add_attribute("remote-candidate", " ".join(list))

        return media

    def parse_sdp(self, message):
        sdp = Message()
        sdp.parse(message)
        for media in sdp.medias.values():
            self.parse_media(media)

    def parse_media(self, media):
        self._remote_codecs[media.name] = media.codecs
        self._remote_candidates[media.name] = self.parse_candidates(media)

    def parse_candidates(self, media):
        candidates = []

        if not media.get_attribute("candidate"):
            self.draft = 0
            candidates.append(Candidate(component_id=COMPONENTS.RTP, ip=media.ip,
                port=media.port, transport="UDP", priority=1, type="host"))
            candidates.append(Candidate(component_id=COMPONENTS.RTCP, ip=media.ip,
                port=media.rtcp, transport="UDP", priority=1, type="host"))
        else:
            ufrag = media.get_attribute("ice-ufrag")
            pwd = media.get_attribute("ice-pwd")
            if ufrag and pwd:
                self.draft = 19
            else:
                self.draft = 6

            for attribute in media.get_attributes("candidate"):
                candidate = Candidate(draft=self.draft, username=ufrag,
                                      password=pwd)
                candidate.parse(attribute)
                candidates.append(candidate)

        return candidates

    def get_active_local_candidates(self, name):
        active = self._local_active.get(name)
        candidates = self._local_candidates.get(name)
        if active:
            return reduce(lambda x: (x.foundation == active.foundation), candidates)
        return candidates

    def get_active_remote_candidates(self, name):
        candidates = []
        components = []
        active = self._remote_active.get(name)
        if active is None:
            return candidates
        for candidate in self._remote_candidates.get(name):
            if candidate.foundation == active.foundation:
                if self.draft is 6:
                    candidates.append(candidate)
                    break
                elif self.draft is 19:
                    if candidate.component_id in components:
                        continue
                    candidates.append(candidate)
                    components.append(candidate.component_id)
        return candidates

    def get_default_address(self, name):
        ip = None
        port = None
        rtcp = None

        active = self._local_active.get(name)
        if not active:
            active = self.search_relay(name)

        for candidate in self._local_candidates.get(name):
            if candidate.foundation == active.foundation and \
               candidate.component_id is COMPONENTS.RTP:
                ip = candidate.ip
                port = candidate.port
            if candidate.foundation == active.foundation and \
               candidate.component_id is COMPONENTS.RTCP:
                rtcp = candidate.port

        return ip, port, rtcp

    def search_relay(self, name):
        relay = None
        for candidate in self._local_candidates.get(name):
            if candidate.transport != "UDP":
                continue
            if candidate.is_relay():
                return candidate
            if not relay or candidate.priority < relay.priority:
                relay = candidate
        return relay


class Candidate(object):

    def __init__(self, draft=0, foundation=None, component_id=None,
                 transport=None, priority=None, username=None, password=None,
                 type=None, ip=None, port=None, base_ip=None, base_port=None):
        self._extensions = {}

        self.draft = draft
        self.foundation = foundation
        self.component_id = component_id
        self.transport = transport
        self.priority = priority
        self.username = username
        self.password = password
        self.type = type
        self.ip = ip
        self.port = port
        self.base_ip = base_ip
        self.base_port = base_port

    @rw_property
    def type():
        def fget(self):
            return self._extensions.get("typ")
        def fset(self, value):
            self._extensions["typ"] = value
        return locals()

    @rw_property
    def base_ip():
        def fget(self):
            return self._extensions.get("raddr")
        def fset(self, value):
            self._extensions["raddr"] = value
        return locals()

    @rw_property
    def base_port():
        def fget(self):
            return self._extensions.get("rport")
        def fset(self, value):
            self._extensions["rport"] = value
        return locals()

    def is_relay(self):
        if self.draft is 6:
            return (self.priority < 0.5)
        elif self.draft is 19:
            return (self.type == "relay")

    def build_local(self):
        if self.draft is 6:
            return "%s %i %s %s %.3f %s %i" % (self.username, self.component_id,
                self.password, self.transport, self.priority, self.ip, self.port)
        elif self.draft is 19:
            ext = []
            for k, v in self._extensions.iteritems():
                if v is not None:
                    ext.append("%s %s" % (k, str(v)))
            return "%i %i %s %i %s %i %s" % (self.foundation, self.component_id,
                self.transport, self.priority, self.ip, self.port, " ".join(ext))

    def build_remote(self):
        if self.draft is 6:
            return self.username
        elif self.draft is 19:
            return "%i %s %i" % (self.component_id, self.ip, self.port)

    def parse(self, line):
        parts = line.split()
        parts = map(lambda x: ((x.isdigit() and int(x)) or x), parts)

        if self.draft is 19:
            (self.foundation, self.component_id, self.transport,
                self.priority, self.ip, self.port) = parts[0:6]
            for i in range(6, len(parts), 2):
                self._extensions[parts[i]] = parts[i + 1]
        elif self.draft is 6:
            (self.username, self.component_id, self.password, self.transport,
                self.priority, self.ip, self.port) = parts[0:7]
            self.foundation = self.username[0:31]
            self.priority = float(self.priority)

    def __eq__(self, other):
        return (self.draft == other.draft and
                self.foundation == other.foundation and
                self.component_id == other.component_id and
                self.transport == other.transport and
                self.priority == other.priority and
                self.username == other.username and
                self.password == other.password and
                self.type == other.type and
                self.ip == other.ip and
                self.port == other.port and
                self.base_ip == other.base_ip and
                self.base_port == other.base_port)

    def __repr__(self):
        return "<ICE Candidate: %s>" % self.build_local()