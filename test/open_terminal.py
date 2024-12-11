import pyinstrument
with pyinstrument.profile():
    import pyapp_window
    pyapp_window.open_window(
        # size=(80, 24),
        size=(120, 40),
        # size=(160, 60),
        backend='terminal',
    )
