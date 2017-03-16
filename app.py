import dbus

def get_devices():
    bus = dbus.SystemBus()
    wifi = bus.get_object('org.freedesktop.NetworkManager',
                        '/org/freedesktop/NetworkManager')

    iface = dbus.Interface(wifi, dbus_interface='org.freedesktop.NetworkManager')

    # getting all devices
    m = iface.get_dbus_method("GetAllDevices", dbus_interface=None)
    for dev in m():
        print dev

if __name__ == "__main__":
    get_devices()

