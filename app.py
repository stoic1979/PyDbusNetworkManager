import dbus

def enable_networking(val):
    """
    function enables/disables networking depending upon the 'val' argument
    if val is True, networking is enabled
    if val is False, networking is disabled
    """
    bus = dbus.SystemBus()
    wifi = bus.get_object('org.freedesktop.NetworkManager',
                        '/org/freedesktop/NetworkManager')

    iface = dbus.Interface(wifi, dbus_interface='org.freedesktop.NetworkManager')

    # enabling/disabling networking
    m = iface.get_dbus_method("Enable", dbus_interface=None)
    m(val)

def get_devices():
    bus = dbus.SystemBus()
    wifi = bus.get_object('org.freedesktop.NetworkManager',
                        '/org/freedesktop/NetworkManager')

    iface = dbus.Interface(wifi, dbus_interface='org.freedesktop.NetworkManager')

    # getting all devices
    m = iface.get_dbus_method("GetAllDevices", dbus_interface=None)
    devs = []
    for dev in m():
        devs.append("%s" % dev)
    return devs

def get_wifi_access_points_by_dev(device_path):
    print "Checking:", device_path
    bus = dbus.SystemBus()
    obj = bus.get_object('org.freedesktop.NetworkManager', device_path)

    iface = dbus.Interface(obj, dbus_interface='org.freedesktop.NetworkManager.Device.Wireless')

    # getting all wireless access points
    m = iface.get_dbus_method("GetAccessPoints", dbus_interface=None)

    aps = []
    for ap in m():
        aps.append("%s" % ap)
    print aps
    return aps

def get_wifi_access_points():
    aps = None
    for dev in get_devices():
        try:
            aps = get_wifi_access_points_by_dev(dev)
            break
        except:
            pass
    return aps

def get_access_point_all_info(ap_path):

    bus = dbus.SystemBus()
    obj = bus.get_object('org.freedesktop.NetworkManager', ap_path)

    iface = dbus.Interface(obj, dbus_interface='org.freedesktop.DBus.Properties')

    m = iface.get_dbus_method("GetAll", dbus_interface=None)

    # getting all ppoperties like Ssid, Strength, HwAddress etc.
    props = m("org.freedesktop.NetworkManager.AccessPoint")
    for k,v in props.iteritems():
        print k,v


def get_access_point_brief_info(ap_path):

    bus = dbus.SystemBus()
    obj = bus.get_object('org.freedesktop.NetworkManager', ap_path)

    iface = dbus.Interface(obj, dbus_interface='org.freedesktop.DBus.Properties')

    m = iface.get_dbus_method("Get", dbus_interface=None)

    # getting Ssid
    dbusArray = m("org.freedesktop.NetworkManager.AccessPoint", "Ssid")
    Ssid = ''.join([chr(character) for character in dbusArray])

    # getting Strength
    Strength = m("org.freedesktop.NetworkManager.AccessPoint", "Strength")

    # getting HwAddress
    HwAddress = m("org.freedesktop.NetworkManager.AccessPoint", "HwAddress")

    return (Ssid, int(Strength), str(HwAddress))


if __name__ == "__main__":

    print get_devices()
    print get_wifi_access_points()

    # getting access points' Ssid, Strength, HwAddress
    for ap in get_wifi_access_points():
        print get_access_point_brief_info(ap)

