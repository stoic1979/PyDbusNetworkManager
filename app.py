import dbus

class DBusNetworkManager:

    def __init__(self):
        pass

    def get_introspection(self):
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

        # getting Mode
        Mode = m("org.freedesktop.NetworkManager.AccessPoint", "Mode")

        return (Ssid, int(Strength), str(HwAddress), int(Mode))


    def activate_connection(self, con_path, dev_path, obj_path):
        bus = dbus.SystemBus()
        wifi = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')

        iface = dbus.Interface(wifi, dbus_interface='org.freedesktop.NetworkManager')

        # activating connection
        m = iface.get_dbus_method("ActivateConnection", dbus_interface=None)
        active_connection = m(con_path, dev_path, obj_path)

        # on success, active connection object/path is returned
        return active_connection

    def connect_to_wifi(self, ssid, passphrase):
        bus = dbus.SystemBus()

        # create dbus interfaces for NetworkManager and Dbus Properties
        obj = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
        iface = dbus.Interface(obj, "org.freedesktop.NetworkManager")
        iface_props = dbus.Interface(obj, "org.freedesktop.DBus.Properties")

        # wireless should be enabled in network manager
        self.enable_networking(True)

        # Get path to the 'wlan0' device. If you're uncertain whether your WiFi
        # device is wlan0 or something else, you may utilize iface.GetDevices()
        # method to obtain a list of all devices, and then iterate over these
        # devices to check if DeviceType property equals NM_DEVICE_TYPE_WIFI (2).
        device_path = dbus.ObjectPath("/org/freedesktop/NetworkManager/Devices/2")
        print "wireless device path: ", device_path

        # Connect to the device's Wireless interface and obtain list of access points.
        device = dbus.Interface(bus.get_object("org.freedesktop.NetworkManager",
                                            device_path),
                                "org.freedesktop.NetworkManager.Device.Wireless")
        accesspoints_paths_list = device.GetAccessPoints()

        # Identify our access point. We do this by comparing our desired SSID
        # to the SSID reported by the AP.
        our_ap_path = None
        for ap_path in accesspoints_paths_list:
            ap_props = dbus.Interface(
                bus.get_object("org.freedesktop.NetworkManager", ap_path),
                "org.freedesktop.DBus.Properties")
            ap_ssid = ap_props.Get("org.freedesktop.NetworkManager.AccessPoint", "Ssid")
            # Returned SSID is a list of ASCII values. Let's convert it to a proper string.
            str_ap_ssid = "".join(chr(i) for i in ap_ssid)
            print ap_path, ": SSID =", str_ap_ssid
            if str_ap_ssid == SSID:
                our_ap_path = ap_path
                break

        if not our_ap_path:
            print "AP not found" 
            exit(2)
        print "Our AP: ", our_ap_path

        # At this point we have all the data we need. Let's prepare our connection
        # parameters so that we can tell the NetworkManager what is the passphrase.
        connection_params = {
            "802-11-wireless": {
                "security": "802-11-wireless-security",
            },
            "802-11-wireless-security": {
                "key-mgmt": "wpa-psk",
                "psk": PASSPHRASE
            },
        }

        # Establish the connection.
        settings_path, connection_path = iface.AddAndActivateConnection(
            connection_params, device_path, our_ap_path)
        print "settings_path =", settings_path
        print "connection_path =", connection_path
    
        # Wait until connection is established. This may take a few seconds.
        NM_ACTIVE_CONNECTION_STATE_ACTIVATED = 2
        print """Waiting for connection to reach """ \
            """NM_ACTIVE_CONNECTION_STATE_ACTIVATED state ..."""
        connection_props = dbus.Interface(
            bus.get_object("org.freedesktop.NetworkManager", connection_path),
            "org.freedesktop.DBus.Properties")
        state = 0
        while True:
            # Loop forever until desired state is detected.
            #
            # A timeout should be implemented here, otherwise the program will
            # get stuck if connection fails.
            #
            # IF PASSWORD IS BAD, NETWORK MANAGER WILL DISPLAY A QUERY DIALOG!
            # This is something that should be avoided, but I don't know how, yet.
            #
            # Also, if connection is disconnected at this point, the Get()
            # method will raise an org.freedesktop.DBus.Error.UnknownMethod
            # exception. This should also be anticipated.
            state = connection_props.Get(
                "org.freedesktop.NetworkManager.Connection.Active", "State")
            if state == NM_ACTIVE_CONNECTION_STATE_ACTIVATED:
                break
            time.sleep(0.001)
            print "Connection established!"

    def get_wifi_device_path(self):
        for dev in self.get_devices():
            try:
                aps = self.get_wifi_access_points_by_dev(dev)
                return dev

            except:
                pass
