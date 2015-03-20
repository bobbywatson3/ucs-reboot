from UcsSdk import *
from UcsSdk.MoMeta.LsPower import LsPower
import re
import argparse
import getpass


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--service-profile-wildcard', required=True, help="Wildcard match for any service profile names that contain this string")
parser.add_argument('-l', '--login', default='admin', help="Login for UCS Manager. Default is 'admin'.")
parser.add_argument('-p', '--password', help="Password for UCS Manager.")
parser.add_argument('-u', '--ucs', required=True, help="Hostname or IP address of UCS Manager") # TODO make this work with multiple UCS IP's

args = parser.parse_args()

service_profile_wildcard = args.service_profile_wildcard

try:
    handle = UcsHandle()
    if not args.password:
        args.password = getpass.getpass(prompt='UCS Password: ')
    handle.Login(args.ucs, args.login, args.password)

    service_profiles = []
    mo_dn_array = {}
    getRsp = handle.GetManagedObject(None, None,{"Dn":"org-root/"})
    moArr = handle.GetManagedObject(getRsp, "lsServer")
    for mo in moArr:
        origDn = str(mo.Dn)
        if service_profile_wildcard in origDn:
            cleanDn = re.search(r'(?<=ls-)(\S*)',origDn)
            cleanDn = cleanDn.group()
            service_profiles.append(cleanDn)
            mo_dn_array[mo] = origDn
    
    print "The following service profiles will be rebooted:"
    for server in service_profiles:
        print server 
    while True:
        sys.stdout.write('Hard reboot servers? [y/n] ')
        choice = raw_input().lower()
        if choice == 'y':
            print "Rebooting servers."
            for mo,dn in mo_dn_array.items():
                powerclass = dn + "/power"
                handle.SetManagedObject(mo, LsPower.ClassId(), {LsPower.DN:dn + "/power", LsPower.STATE:"cycle-immediate"}, False)
            print "Servers rebooted."
            break
        elif choice == 'n':
            quit()
        else: 
            sys.stdout.write("Please enter 'y' or 'n'")

    handle.Logout()
except Exception, err:
        print "Exception:", str(err)
        import traceback, sys
        print '-' * 60
        traceback.print_exc(file=sys.stdout)
        print '-' * 60

