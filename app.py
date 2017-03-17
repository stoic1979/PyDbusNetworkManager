import dbus

class DBusNetworkManager:

    def __init__(self):
        pass

    def get_network_manager_introspection(self):
        bus = dbus.SystemBus()
        obj = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')

        iface = dbus.Interface(obj, dbus_interface='org.freedesktop.DBus.Introspectable')
    
        # getting introspection xml
        m = iface.get_dbus_method("Introspect", dbus_interface=None)
        return m()


    def enable_networking(self, val):
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


    def get_devices(self):
        bus = dbus.SystemBus()
        wifi = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')

        iface = dbus.Interface(wifi, dbus_interface='org.freedesktop.NetworkManager')

        # getting all devices
        m = iface.get_dbus_method("GetAllDevices", dbus_interface=None)
        devs = []
        for dev in m():
            devs.append("%s" % dev)
        return devs


    def get_active_connections(self):
        bus = dbus.SystemBus()
        wifi = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')

        iface = dbus.Interface(wifi, dbus_interface='org.freedesktop.DBus.Properties')

        m = iface.get_dbus_method("Get", dbus_interface=None)
        return [ str(ac) for ac in m("org.freedesktop.NetworkManager", "ActiveConnections") ]


    def get_active_connection_info(self, ac_path):
        bus = dbus.SystemBus()
        wifi = bus.get_object('org.freedesktop.NetworkManager', ac_path)

        iface = dbus.Interface(wifi, dbus_interface='org.freedesktop.DBus.Properties')

        # creating proxy 'Get' method
        m = iface.get_dbus_method("Get", dbus_interface=None)

        # getting Id of active connection
        Id = m("org.freedesktop.NetworkManager.Connection.Active", "Id")

        # getting Type of active connection
        Type = m("org.freedesktop.NetworkManager.Connection.Active", "Type")

        # getting Uuid of active connection
        Uuid = m("org.freedesktop.NetworkManager.Connection.Active", "Uuid")

        # getting State of active connection
        State = m("org.freedesktop.NetworkManager.Connection.Active", "State")

        # NOTE:
        # this function only returns properties like Id, Type, Uuid, State of an active connection
        # However, other properties like Dhcp4Config, Dhcp6Config, Ip4Config, Ip6Config etc. can also be obtained
        return (str(Id), str(Type), str(Uuid), int(State))


    def deactivate_connection(self, ac_path):
        bus = dbus.SystemBus()
        wifi = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')

        iface = dbus.Interface(wifi, dbus_interface='org.freedesktop.NetworkManager')

        # getting all devices
        m = iface.get_dbus_method("DeactivateConnection", dbus_interface=None)

        try:
            m(ac_path)
            return True
        except Exception as exp:
            print "deactivate_connection() exception :: %s" % exp

        return False


    def get_wifi_access_points_by_dev(self, device_path):
        bus = dbus.SystemBus()
        obj = bus.get_object('org.freedesktop.NetworkManager', device_path)

        iface = dbus.Interface(obj, dbus_interface='org.freedesktop.NetworkManager.Device.Wireless')

        # getting all wireless access points
        m = iface.get_dbus_method("GetAccessPoints", dbus_interface=None)

        return [str(ap) for ap in m()]


    def get_wifi_access_points(self):
        aps = None
        for dev in self.get_devices():
            try:
                aps = self.get_wifi_access_points_by_dev(dev)

                # we will get interface 'org.freedesktop.NetworkManager.Device.Wireless'
                # in one device only so once we get aps for one, no need to continue
                break
            except:
                pass
        return aps


    def get_access_point_all_info(self, ap_path):

        bus = dbus.SystemBus()
        obj = bus.get_object('org.freedesktop.NetworkManager', ap_path)

        iface = dbus.Interface(obj, dbus_interface='org.freedesktop.DBus.Properties')

        m = iface.get_dbus_method("GetAll", dbus_interface=None)

        # getting all ppoperties like Ssid, Strength, HwAddress etc.
        props = m("org.freedesktop.NetworkManager.AccessPoint")
        for k,v in props.iteritems():
            print k,v

        return props


    def get_access_point_brief_info(self, ap_path):

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

    dnm = DBusNetworkManager()

    print "\n------------[ Devices ]----------------"
    print dnm.get_devices()

    print "\n------------[ Access Points ]----------------"
    print dnm.get_wifi_access_points()

    # getting access points' Ssid, Strength, HwAddress
    for ap in dnm.get_wifi_access_points():
        print dnm.get_access_point_brief_info(ap)

    # getting active connection info
    print "\n------------[ Active Connections ]----------------"
    print dnm.get_active_connections()
    for ac in dnm.get_active_connections():
        print dnm.get_active_connection_info(ac)

    print "\n------------[ Deactivate Connection ]----------------"
    for ac in dnm.get_active_connections():
        if dnm.deactivate_connection(ac):
            print "Successfully deactivated: %s" % ac
        else:
            print "Failed to deactivate: %s" % ac
