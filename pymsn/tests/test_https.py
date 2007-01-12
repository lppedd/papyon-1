import sys, os
parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, parent_dir) 
del parent_dir
del sys
del os

import gnet
import gnet.protocol
import gobject

mainloop = gobject.MainLoop()

def response(http, resp):
    global mainloop
    print resp
    mainloop.quit()

def request(http, req):
    print req

data='<?xml version="1.0" encoding="UTF-8"?><Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsse="http://schemas.xmlsoap.org/ws/2003/06/secext" xmlns:saml="urn:oasis:names:tc:SAML:1.0:assertion" xmlns:wsp="http://schemas.xmlsoap.org/ws/2002/12/policy" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/03/addressing" xmlns:wssc="http://schemas.xmlsoap.org/ws/2004/04/sc" xmlns:wst="http://schemas.xmlsoap.org/ws/2004/04/trust"><Header><ps:AuthInfo xmlns:ps="http://schemas.microsoft.com/Passport/SoapServices/PPCRL" Id="PPAuthInfo"><ps:HostingApp>{7108E71A-9926-4FCB-BCC9-9A9D3F32E423}</ps:HostingApp><ps:BinaryVersion>4</ps:BinaryVersion><ps:UIVersion>1</ps:UIVersion><ps:Cookies></ps:Cookies><ps:RequestParams>AQAAAAIAAABsYwQAAAAxMDMz</ps:RequestParams></ps:AuthInfo><wsse:Security><wsse:UsernameToken Id="user"><wsse:Username>kimbix@hotmail.com</wsse:Username><wsse:Password>linox45</wsse:Password></wsse:UsernameToken></wsse:Security></Header><Body><ps:RequestMultipleSecurityTokens xmlns:ps="http://schemas.microsoft.com/Passport/SoapServices/PPCRL" Id="RSTS"><wst:RequestSecurityToken Id="RST0"><wst:RequestType>http://schemas.xmlsoap.org/ws/2004/04/security/trust/Issue</wst:RequestType><wsp:AppliesTo><wsa:EndpointReference><wsa:Address>http://Passport.NET/tb</wsa:Address></wsa:EndpointReference></wsp:AppliesTo></wst:RequestSecurityToken><wst:RequestSecurityToken Id="RST2"><wst:RequestType>http://schemas.xmlsoap.org/ws/2004/04/security/trust/Issue</wst:RequestType><wsp:AppliesTo><wsa:EndpointReference><wsa:Address>messenger.msn.com</wsa:Address></wsa:EndpointReference></wsp:AppliesTo><wsse:PolicyReference URI="?id=507"></wsse:PolicyReference></wst:RequestSecurityToken><wst:RequestSecurityToken Id="RST3"><wst:RequestType>http://schemas.xmlsoap.org/ws/2004/04/security/trust/Issue</wst:RequestType><wsp:AppliesTo><wsa:EndpointReference><wsa:Address>contacts.msn.com</wsa:Address></wsa:EndpointReference></wsp:AppliesTo><wsse:PolicyReference URI="MBI"></wsse:PolicyReference></wst:RequestSecurityToken><wst:RequestSecurityToken Id="RST4"><wst:RequestType>http://schemas.xmlsoap.org/ws/2004/04/security/trust/Issue</wst:RequestType><wsp:AppliesTo><wsa:EndpointReference><wsa:Address>messengersecure.live.com</wsa:Address></wsa:EndpointReference></wsp:AppliesTo><wsse:PolicyReference URI="MBI_SSL"></wsse:PolicyReference></wst:RequestSecurityToken><wst:RequestSecurityToken Id="RST5"><wst:RequestType>http://schemas.xmlsoap.org/ws/2004/04/security/trust/Issue</wst:RequestType><wsp:AppliesTo><wsa:EndpointReference><wsa:Address>spaces.live.com</wsa:Address></wsa:EndpointReference></wsp:AppliesTo><wsse:PolicyReference URI="MBI"></wsse:PolicyReference></wst:RequestSecurityToken><wst:RequestSecurityToken Id="RST6"><wst:RequestType>http://schemas.xmlsoap.org/ws/2004/04/security/trust/Issue</wst:RequestType><wsp:AppliesTo><wsa:EndpointReference><wsa:Address>storage.msn.com</wsa:Address></wsa:EndpointReference></wsp:AppliesTo><wsse:PolicyReference URI="MBI"></wsse:PolicyReference></wst:RequestSecurityToken></ps:RequestMultipleSecurityTokens></Body></Envelope>'

uagent = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; IDCRL 4.100.313.1; IDCRL-cfg 4.0.5633.0; App MsnMsgr.Exe, 8.1.168.0, {7108E71A-9926-4FCB-BCC9-9A9D3F32E423})"
c = gnet.protocol.HTTPS("login.live.com")
c.connect("response-received", response)
c.connect("request-sent", request)
c.request("/RST.srf", headers={'User-Agent':uagent, 'Cookie':"MUID=FF4FF37AE48E491E96862397A5FD9AC4"}, data=data, method="POST")

mainloop.run()