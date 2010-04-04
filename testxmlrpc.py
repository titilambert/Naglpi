#!/usr/bin/python

import xmlrpclib
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-s", "--glpi-server", dest="glpi_server", default="localhost",
                  help="""GLPI address (default "localhost")""")
parser.add_option("-g", "--glpi-url", dest="glpi_url", default="glpi",
                  help="""GLPI url (default "glpi")""", type="string")
parser.add_option("-H", "--hostname", dest="hostname",
                  help="Hostname", type="string")
parser.add_option("-i", "--ip", dest="ipaddress",
                  help="Host IP address")
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
                  help="test glpi connection" )
parser.add_option("-v", "--verbose", dest="verbose", default=False,
                  help="Verbose mode" )
parser.add_option("-V", "--version", dest="versiontest", default=False,
                  help="Show naglpi version" )

# Get opt
(options, args) = parser.parse_args()
# Build URL
url = "/" + options.glpi_url + "/plugins/webservices/xmlrpc.php";
uri =  "http://" + options.glpi_server + url

# Create xmlrpc client
proxy = xmlrpclib.ServerProxy(uri)

# Launch test
if options.test:
    xmlret = proxy.glpi.test()
    for item in xmlret.items():
        print "%s: %s" % item
    exit(0)

# login
params = {
            "login_name": options.username,
            "login_password": options.password,
            }
try:
    xmlret = proxy.glpi.doLogin(params)
except xmlrpclib.Fault,e:
    print e.faultString
    exit(e.faultCode)
    
# Get Session
session = { "session":xmlret["session"]}

# get computer list
try:
    computer_list = proxy.glpi.listComputers(session)
except xmlrpclib.Fault,e:
    print e.faultString
    exit(e.faultCode)


# Search computer
computer_found = False
for computer in computer_list:
    if computer["name"] == options.hostname:
        computer_id = computer["id"]
        computer_found = True
        break;


if options.category != None:
    # Get category
    params = {  
                "dropdown" : "tracking_category",
                "name" : options.category,
                }
    params.update(session)
    try:
        categories = proxy.glpi.listDropdownValues(params)
    except xmlrpclib.Fault,e:
        print e.faultString
        exit(e.faultCode)
    category_id = None
    if len(categories) > 0:
        category_id = {"category" : categories[0]["id"]}
    else:
        print "No category found"



# Create ticket
# See glpi/config/define.php
# define("COMPUTER_TYPE",1);
# Then itemtype == 1
params = {  
            "item" : computer_id,
            "title" : options.title,
            "content" : options.message,
            "urgence" : options.urgence,
            "itemtype" : 1,
            }
params.update(session)
if category_id:
    params.update(category_id)
try:
    xmlret = proxy.glpi.createTicket(params)
except xmlrpclib.Fault,e:
    print e.faultString
    exit(e.faultCode)
