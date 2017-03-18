#
# quick test script to test wifi connect/disconnet
# for given ssid and passphrase
#

import dbus
import time

# change your ssid, and passphrase here
SSID = "p55"
PASSPHRASE = "987654321"

def ensure_wifi_is_enabled(iface_props):
    was_wifi_enabled = iface_props.Get("org.freedesktop.NetworkManager", "WirelessEnabled")

    if not was_wifi_enabled:
        print "Enabling WiFi and sleeping for 10 seconds ..."
        iface_props.Set("org.freedesktop.NetworkManager", "WirelessEnabled",
                          True)
        # Give the WiFi adapter some time to scan for APs. This is absolutely
        # the wrong way to do it, and the program should listen for
        # AccessPointAdded() signals, but it will do.
        time.sleep(10)

def wifi_connect_disconnect_test():
    bus = dbus.SystemBus()

    # create dbus interfaces for NetworkManager and Dbus Properties
    obj = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
    iface = dbus.Interface(obj, "org.freedesktop.NetworkManager")
    iface_props = dbus.Interface(obj, "org.freedesktop.DBus.Properties")

    # wireless should be enabled in network manager
    ensure_wifi_is_enabled(iface_props)

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
        ap_ssid = ap_props.Get("org.freedesktop.NetworkManager.AccessPoint",
                               "Ssid")
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

    #############################
    #                           #
    # Connection is established #
    #                           #
    #############################
    print "Sleeping for 5 seconds ..."
    time.sleep(5)
    print "Disconnecting ..."

    ##############################################################################
    #                                                                            #
    # Clean up: disconnect and delete connection settings. If program crashes    #
    # before this point is reached then connection settings will be stored       #
    # forever.                                                                   #
    # Some pre-init cleanup feature should be devised to deal with this problem, #
    # but this is an issue for another topic.                                    #
    #                                                                            #
    ##############################################################################
    iface.DeactivateConnection(connection_path)
    settings = dbus.Interface(
        bus.get_object("org.freedesktop.NetworkManager", settings_path),
        "org.freedesktop.NetworkManager.Settings.Connection")
    settings.Delete()

    # Disable Wireless (optional step)
    if not was_wifi_enabled:
        iface_props.Set("org.freedesktop.NetworkManager", "WirelessEnabled", False)

    print "------------------- finished -----------------------"

if __name__ == "__main__":
    wifi_connect_disconnect_test()
