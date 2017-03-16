import dbus

def get_network_manager_introspection():
    bus = dbus.SystemBus()
    obj = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')

    iface = dbus.Interface(obj, dbus_interface='org.freedesktop.DBus.Introspectable')

    # getting introspection xml
    m = iface.get_dbus_method("Introspect", dbus_interface=None)
    return m()

def enable_networking(val):
    """
    function enables/disables networking depending upon the 'val' argument
    if val is True, networking is enabled
    if val is False, networking is disabled
    """
    bus = dbus.SystemBus()
    wifi = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')

    iface = dbus.Interface(wifi, dbus_interface='org.freedesktop.NetworkManager')

    # enabling/disabling networking
    m = iface.get_dbus_method("Enable", dbus_interface=None)
    m(val)

def get_devices():
    bus = dbus.SystemBus()
    wifi = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')

    iface = dbus.Interface(wifi, dbus_interface='org.freedesktop.NetworkManager')

    # getting all devices
    m = iface.get_dbus_method("GetAllDevices", dbus_interface=None)
    devs = []
    for dev in m():
        devs.append("%s" % dev)
    return devs

def get_active_connections():
    bus = dbus.SystemBus()
    wifi = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')

    iface = dbus.Interface(wifi, dbus_interface='org.freedesktop.DBus.Properties')

    m = iface.get_dbus_method("Get", dbus_interface=None)
    return [ str(ac) for ac in m("org.freedesktop.NetworkManager", "ActiveConnections") ]

def get_wifi_access_points_by_dev(device_path):
    bus = dbus.SystemBus()
    obj = bus.get_object('org.freedesktop.NetworkManager', device_path)

    iface = dbus.Interface(obj, dbus_interface='org.freedesktop.NetworkManager.Device.Wireless')

    # getting all wireless access points
    m = iface.get_dbus_method("GetAccessPoints", dbus_interface=None)

    return [str(ap) for ap in m()]

def get_wifi_access_points():
    aps = None
    for dev in get_devices():
        try:
            aps = get_wifi_access_points_by_dev(dev)

            # we will get interface 'org.freedesktop.NetworkManager.Device.Wireless'
            # in one device only so once we get aps for one, no need to continue
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

    return props


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
    print get_active_connections()

    print get_devices()
    print get_wifi_access_points()

    # getting access points' Ssid, Strength, HwAddress
    for ap in get_wifi_access_points():
        print get_access_point_brief_info(ap)

