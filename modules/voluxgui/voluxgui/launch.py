def launch(connection_preset=""):

    # builtins
    import os
    import sys
    import threading
    import logging
    import importlib

    # site
    import volux
    import colorama

    # package
    from voluxgui.gui import VoluxGui

    log = logging.getLogger("voluxgui launch")
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d"
    )
    ch.setFormatter(formatter)
    log.addHandler(ch)

    vlx = volux.VoluxOperator()

    shared_modules = []

    def add_volux_module(module_name, class_name, *args, **kwargs):

        try:
            module = importlib.import_module(module_name)
            module_UUID = vlx.add_module(
                getattr(module, class_name)(*args, **kwargs)
            )
            shared_modules.append(vlx.modules[module_UUID])
            return module_UUID
        except Exception as err:
            log.warning("failed to import {}... ({})".format(module_name, err))

    audio_UUID = add_volux_module("voluxaudio", "VoluxAudio")
    l_strip_UUID = add_volux_module(
        "voluxlight",
        "VoluxLight",
        instance_label="strip",
        init_mode="device",
        init_mode_args={"label": "Strip"},
    )
    add_volux_module(
        "voluxlight",
        "VoluxLight",
        instance_label="ceiling",
        init_mode="device",
        init_mode_args={"label": "Office Ceiling"},
    )
    add_volux_module(
        "voluxlight",
        "VoluxLight",
        instance_label="demo",
        init_mode="device",
        init_mode_args={"label": "Demo Bulb"},
    )
    vis_UUID = add_volux_module(
        "voluxlightvisualiser",
        "VoluxLightVisualiser",
        mode="intense",
        hueHz=120,
        hue_cycle_duration=5,
    )
    add_volux_module("voluxvolume", "VoluxVolume")

    gui_UUID = vlx.add_module(
        # VoluxGui(shared_modules=gui_shared_modules),
        VoluxGui(shared_modules=shared_modules),
        req_permissions=[
            volux.request.SyncState,
            volux.request.AddConnection,
            volux.request.RemoveConnection,
            volux.request.GetConnections,
            volux.request.StartSync,
            volux.request.StopSync,
            volux.request.GetSyncDeltas,
            volux.request.GetConnectionNicknames,
        ],
    )

    if connection_preset == "lightshow":

        connection_list = [
            volux.VoluxConnection(
                vlx.modules[audio_UUID], vlx.modules[gui_UUID], 120
            ),
            volux.VoluxConnection(
                vlx.modules[audio_UUID], vlx.modules[vis_UUID], 120
            ),
            volux.VoluxConnection(
                vlx.modules[vis_UUID], vlx.modules[l_strip_UUID], 120
            ),
        ]

        for connection in connection_list:
            vlx.add_connection(connection)

        vlx.gui.mainApp.LFconnections._refresh_connections()
        vlx.gui.mainApp.LFconnections._toggle_sync_externally()

    vlx.gui.init_window()
    vlx.stop_sync()


if __name__ == "__main__":
    launch()
