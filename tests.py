from app import DBusNetworkManager

def test_deactivate_connection(dnm):
    print "\n------------[ Deactivate Connection ]----------------"
    for ac in dnm.get_active_connections():
        if dnm.deactivate_connection(ac):
            print "Successfully deactivated: %s" % ac
        else:
            print "Failed to deactivate: %s" % ac


def test_activate_connection(dnm):
    # hard coded obj paths for testing
    con_path = dbus.ObjectPath("/org/freedesktop/NetworkManager/Settings/2")
    dev_path = dbus.ObjectPath("/org/freedesktop/NetworkManager/Devices/2")
    obj_path = dbus.ObjectPath("/org/freedesktop/NetworkManager/Settings/Connection")
    print "Current Active Connection: ", dnm.activate_connection(con_path, dev_path, obj_path)

def test_get_active_connections(dnm):
    # getting active connection info
    print "\n------------[ Active Connections ]----------------"
    print dnm.get_active_connections()
    for ac in dnm.get_active_connections():
        print dnm.get_active_connection_info(ac)

def test_introspection(dnm):
    print dnm.get_introspection()

def test_get_devices(dnm):
    print "\n------------[ Devices ]----------------"
    print dnm.get_devices()

def test_get_access_points(dnm):
    print "\n------------[ Access Points ]----------------"
    print dnm.get_wifi_access_points()

    # getting access points' Ssid, Strength, HwAddress
    for ap in dnm.get_wifi_access_points():
        print dnm.get_access_point_brief_info(ap)

def test_wifi_connect():
    status, msg = dnm.connect_to_wifi("p55", "987654321")
    if status:
        print "Connection made"
        print msg
    else:
        print "Connection not made"
        print msg

if __name__ == "__main__":

    dnm = DBusNetworkManager()
    test_get_devices(dnm)
    test_get_access_points(dnm)
