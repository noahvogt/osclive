from .raw import *
from .studiolive1602 import *

SL2442Status_raw1394 = {
    # Leave empty for now, we just need the length to be correct so it doesn't leave bytes in the buffer!
}

SL2442Channels_raw1394 = {
    **{
        "ch%d" % (i + 1): RawInputChannel(i, SL1602CtrlsIn_raw1394, 1)
        for i in range(24)
    },
    **{
        "sub%d" % (i + 1): RawInputChannel(i + 24, SL1602CtrlsIn_raw1394, 2)
        for i in range(4)
    },
    **{
        "aux%d" % (i + 1): RawInputChannel(i + 28, SL1602CtrlsIn_raw1394, 1)
        for i in range(10)
    },
    "fxa": RawInputChannel(38, SL1602CtrlsIn_raw1394),
    "fxb": RawInputChannel(39, SL1602CtrlsIn_raw1394),
    "main": RawInputChannel(40, SL1602CtrlsIn_raw1394, 2),
    "geq0": RawGeq(0, SL1602CtrlsGeq_raw1394, length=200),
    "fx0": RawFx(0, SL1602CtrlsFx_raw1394, length=200),
    "fx1": RawFx(1, SL1602CtrlsFx_raw1394, length=200),
    "masters": RawMasters(0, SL1602CtrlsMasters_raw1394, length=200),
    "_status": RawStatus(0, SL2442Status_raw1394, length=69),
    "_faders": RawFaders(0, {}, length=200),
}


class StudioLive2442(RawStudioLiveDevice):
    name = "StudioLive 24.4.2"
    channels = SL2442Channels_raw1394
