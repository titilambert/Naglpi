#!/usr/bin/python

#    naglpi.py

#    This file is part of naglpi

#    Copyright (C) 2010 Thibault Cohen

#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import xmlrpclib
from optparse import OptionParser
import sys

# Create option parse
parser = OptionParser()
parser.add_option("-s", "--glpi-server", dest="glpi_server", default="localhost",
                  help="""GLPI address (default "localhost")""")
parser.add_option("-g", "--glpi-url", dest="glpi_url", default="glpi",
                  help="""GLPI url (default "glpi")""", type="string")
parser.add_option("-H", "--hostname", dest="hostname",
                  help="Hostname", type="string")
parser.add_option("-i", "--ip", dest="ipaddress",
                  help="Host IP address (useless for now)")
parser.add_option("-c", "--category", dest="category", default=None,
                  help="GLPI Ticket category", type="string")
parser.add_option("-m", "--message", dest="message", default="",
                  help="Ticket content", type="string")
parser.add_option("-t", "--title", dest="title", default="",
                  help="Ticket title", type="string")
parser.add_option("-U", "--urgence", dest="urgence", default=3,
                  help="Ticket urgency level" )
parser.add_option("-u", "--username", dest="username", default="glpi",
                  help="""GLPI Username (default "glpi")""" )
parser.add_option("-p", "--password", dest="password", default="glpi",
                  help="""GLPI Password (default "glpi")""" )
parser.add_option("-T", "--test", dest="test", default=False,
                  help="Test glpi connection" )
parser.add_option("-v", "--verbose", dest="verbose", default=False,
                  help="Verbose mode (useless for now)" )
parser.add_option("-V", "--version", dest="versiontest", default=False,
                  help="Show naglpi version" )

# Get options
(options, args) = parser.parse_args()

# Build URL
url = "/" + options.glpi_url + "/plugins/webservices/xmlrpc.php";
uri =  "http://" + options.glpi_server + url

# Create xmlrpc client
proxy = xmlrpclib.ServerProxy(uri)

# Launch test
if options.test:
    try:
        xmlret = proxy.glpi.test()
    except xmlrpclib.Fault,e:
        print e.faultString
        sys.exit(e.faultCode)
    for item in xmlret.items():
        print "%s: %s" % item
    sys.exit(0)

# Check if title is present
if not options.title:
    print "Ticket title missing (-t option)"
    sys.exit(1)

# Check if content is present
if not options.message:
    print "Ticket content missing (-m option)"
    sys.exit(1)

# login
params = {
            "login_name": options.username,
            "login_password": options.password,
            }
try:
    xmlret = proxy.glpi.doLogin(params)
except xmlrpclib.Fault,e:
    print e.faultString
    sys.exit(e.faultCode)
    
# Get Session
session = { "session":xmlret["session"]}

# get computer list
try:
    computer_list = proxy.glpi.listComputers(session)
except xmlrpclib.Fault,e:
    print e.faultString
    sys.exit(e.faultCode)


# Create params for create ticket request

create_ticket_params = {  
            "title" : options.title,
            "content" : options.message,
            "urgence" : options.urgence,
            }

# Add session id
create_ticket_params.update(session)

# Search computer
computer_id = None
for computer in computer_list:
    if computer["name"] == options.hostname:
        # We found it in glpi database
        # TODO ? double - check with IP address ?
        computer_id = computer["id"]
        # See glpi/config/define.php
        # define("COMPUTER_TYPE",1);
        # Then itemtype == 1
        computer_dict = {
                            "item" : computer_id,
                            "itemtype" : 1,
                            }
        create_ticket_params.update(computer_dict)
        break;

# If not host found, we add a comment in ticket content
if not computer_id:
    create_ticket_params["content"] = "Nagios note : Host not found in GLPI database\n\n" + options.message

# Add category ticket
if options.category != None:
    # Get category
    params = {  
                "dropdown" : "ItilCategory",
                "name" : options.category,
                }
    params.update(session)
    try:
        categories = proxy.glpi.listDropdownValues(params)
    except xmlrpclib.Fault,e:
        print e.faultString
        sys.exit(e.faultCode)
    category_id = None
    # Get only first category
    if len(categories) > 0:
        category_id = {"category" : categories[0]["id"]}
        create_ticket_params.update(category_id)
    else:
        # No category found
        pass

# Create ticket request
try:
    xmlret = proxy.glpi.createTicket(create_ticket_params)
except xmlrpclib.Fault,e:
    print e.faultString
    sys.exit(e.faultCode)
