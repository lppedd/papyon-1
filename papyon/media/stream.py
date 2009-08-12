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

from papyon.event import EventsDispatcher
from papyon.media.constants import *

import gobject
import logging

logger = logging.getLogger('Media:Stream')

__all__ = ['MediaStream']

class MediaStream(gobject.GObject, EventsDispatcher):
    """A stream used to transfer media data. It can be an audio or video
       stream and may have codecs and transport candidates associated with it.

       A stream handler implementing the L{papyon.event.MediaStreamEventInferface}
       might need to execute some actions when a stream receives remote codecs
       and candidates (e.g. codecs negotiation) or when closed. (e.g. UI
       notification). See L{papyon.media.conference.MediaStreamHandler} for a
       default implementation using Farsight 2.0."""

    __gsignals__ = {
        'prepared': (gobject.SIGNAL_RUN_FIRST,
            gobject.TYPE_NONE,
            ()),
        'ready': (gobject.SIGNAL_RUN_FIRST,
            gobject.TYPE_NONE,
            ())
    }

    def __init__(self, name, direction, created, encoder):
        """Initialize the media stream.

           @param name: Stream name
           @type name: string
           @param direction: Stream direction
           @type direction: L{papyon.media.constants.MediaStreamDirection}
           @param created: Whether or not the stream has been requested by the client
           @type created: bool
           @param encoder: Candidates encoder/decoder
           @type encoder: L{papyon.media.candidate.MediaCandidateEncoder}"""

        gobject.GObject.__init__(self)
        EventsDispatcher.__init__(self)
        self._name = name
        self._active = False
        self._created = created
        self._direction = direction
        self._encoder = encoder
        self._local_codecs = []
        self._local_codecs_prepared = False
        self._local_candidate_id = None
        self._local_candidates = []
        self._local_candidates_prepared = False
        self._remote_codecs = []
        self._remote_candidate_id = None
        self._remote_candidates = []
        self.relays = []

    @property
    def name(self):
        """Stream name"""
        return self._name

    @property
    def controlling(self):
        """Is the stream created locally (outgoing call)"""
        return self._created

    @property
    def direction(self):
        """Direction of the stream
           @rtype L{papyon.media.constants.MediaStreamDirection}"""
        return self._direction

    @property
    def prepared(self):
        """Are the stream local codecs and candidates received"""
        return (self._local_codecs_prepared and
                self._local_candidates_prepared)

    @property
    def ready(self):
        """Is the candidate pair selected"""
        return (self._local_candidate_id is not None and
                self._remote_candidate_id is not None)

    def close(self):
        """Close the stream"""
        self._dispatch("on_stream_closed")

    def build_description(self, desc):
        """Build the stream description from its infos. We also encode the
           candidates into it using the MediaCandidateEncoder. Descriptions
           are eventually sent to the other participants of the call using
           a L{papyon.media.message.MediaSessionMessage}.

           @param desc: Stream description to complete
           @type desc: L{papyon.media.message.MediaStreamDescription}"""

        desc._ip, desc._port, desc._rtcp = self.get_default_address()
        desc.set_codecs(self._local_codecs)
        self._encoder.encode_candidates(self, desc)
        return desc

    def parse_description(self, desc):
        """Parse the stream infos from a description (codecs and
           candidates).

           @param desc: Media stream description to parse
           @type desc: L{papyon.media.message.MediaStreamDescription}"""

        self._remote_codecs = desc.valid_codecs
        candidates = self._encoder.decode_candidates(desc)
        self._remote_candidates.extend(candidates)
        if not self._remote_candidates:
            self._remote_candidates = self._encoder.get_default_candidates(desc)

        # If the media description has a remote candidate, the active pair
        # has already been selected and the first candidate should be the
        # remote active one.
        if desc.has_active_remote():
            self._remote_candidate_id = candidates[0].foundation
        elif self._active:
            self.process()

    def process(self):
        """Function called once the stream handler is ready to handle the
           stream signals. Emit the signals if we have any pending ones."""

        self._active = True
        if self._remote_codecs:
            self._dispatch("on_remote_codecs_received", self._remote_codecs)
        if self._remote_candidates:
            self._dispatch("on_remote_candidates_received", self._remote_candidates)

    def get_active_local_candidates(self):
        """Returns the active local candidates or all the candidates if there
           isn't any active one. This list is meant to be sent to the other
           call participants."""

        active = self._local_candidate_id
        candidates = self._local_candidates
        if active:
            return filter(lambda x: (x.foundation == active), candidates)
        return candidates

    def get_active_remote_candidates(self):
        """Returns the active remote candidates."""

        active = self._remote_candidate_id
        candidates = self._remote_candidates
        if active is None:
            return []
        return filter(lambda x: (x.foundation == active), candidates)

    def get_default_address(self):
        """Returns the default address. We use the active local candidate if
           there is one selected, else we are using the default candidate."""

        ip = None
        port = None
        rtcp = None

        active = self._local_candidate_id
        default = self.search_default_candidate()
        if not active and default:
            active = default.foundation

        for candidate in self._local_candidates:
            if candidate.foundation == active and \
               candidate.component_id is COMPONENTS.RTP:
                ip = candidate.ip
                port = candidate.port
            if candidate.foundation == active and \
               candidate.component_id is COMPONENTS.RTCP:
                rtcp = candidate.port

        return ip, port, rtcp

    def search_default_candidate(self):
        """Returns the first relay found in the local candidates or the
           candidate with the lowest priority."""
        default = None
        for candidate in self._local_candidates:
            if candidate.transport != "UDP":
                continue
            if candidate.type == "relay":
                return candidate
            if not default or candidate.priority < default.priority:
                default = candidate
        return default

    # The following functions need to be called by some kind of media stream
    # handler. See L{papyon.media.conference.StreamHandler} for a default
    # implementation using Farsight.

    def new_local_candidate(self, candidate):
        """Called by the stream handler when it finds a new local candidate
           @param candidate: New local candidate
           @type candidate: L{papyon.media.candidate.MediaCandidate}"""

        self._local_candidates.append(candidate)

    def new_active_candidate_pair(self, local, remote):
        """Called by the stream handler once the active candidate pair is selected
           @param local: Local active candidate id
           @type local: string
           @param remote: Remote active candidate id
           @type remote: string"""

        logger.debug("New active candidate pair (%s, %s)" % (local, remote))
        if self.ready:
            return # ignore other candidate pairs
        self._local_candidate_id = local
        self._remote_candidate_id = remote
        self.emit("ready")

    def local_candidates_prepared(self):
        """Called by the stream handler once all the local candidates are found"""

        if self._local_candidates_prepared:
            return
        self._local_candidates_prepared = True
        if self.prepared:
            self.emit("prepared")

    def set_local_codecs(self, codecs):
        """Called by the stream handler to set the local codecs
           @param codecs: List of local codecs
           @type codecs: list of L{papyon.media.codec.MediaCodec}"""

        self._local_codecs = codecs
        if self._local_codecs_prepared:
            return
        self._local_codecs_prepared = True
        if self.prepared:
            self.emit("prepared")

