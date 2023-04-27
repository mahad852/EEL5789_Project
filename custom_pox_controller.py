from pox.core import core
from pox.lib.util import dpid_to_str
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of

class MyController(object):
    def __init__(self):
        core.openflow.addListeners(self)
        self.max_flows = 5
        self.flow_count = {}

    def _handle_ConnectionUp(self, event):
        self.flow_count[event.dpid] = 0

    def _handle_FlowRemoved(self, event):
        if event.dpid in self.flow_count:
            self.flow_count[event.dpid] -= 1

    def _handle_PacketIn(self, event):
        if event.dpid not in self.flow_count:
            return
        if self.flow_count[event.dpid] >= self.max_flows:
            self._drop_flow(event)
        else:
            self._install_flow(event)

    def _install_flow(self, event):
        self.flow_count[event.dpid] += 1
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(event.parsed)
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(msg)

    def _drop_flow(self, event):
        self.flow_count[event.dpid] += 1
        msg = of.ofp_packet_out()
        msg.buffer_id = event.ofp.buffer_id
        event.connection.send(msg)

def launch():
    core.registerNew(MyController)