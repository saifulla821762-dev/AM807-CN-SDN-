from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet
from ryu.topology import event
from ryu.topology.api import get_switch, get_link


class TopologyDetector(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TopologyDetector, self).__init__(*args, **kwargs)
        self.mac_to_port = {}   # stores MAC -> port mapping
        self.topology_api_app = self

    # default rule: send unknown packets to controller
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        mod = parser.OFPFlowMod(datapath=datapath,
                               priority=0,
                               match=match,
                               instructions=inst)

        datapath.send_msg(mod)

    # handle packets sent to controller
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth is None:
            return

        dst = eth.dst
        src = eth.src
        in_port = msg.match['in_port']

        # learn source MAC
        self.mac_to_port[dpid][src] = in_port

        # decide output port
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install flow rule if destination known
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)

            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                                 actions)]

            mod = parser.OFPFlowMod(datapath=datapath,
                                   priority=1,
                                   match=match,
                                   instructions=inst)

            datapath.send_msg(mod)

        # send packet out
        out = parser.OFPPacketOut(datapath=datapath,
                                 buffer_id=msg.buffer_id,
                                 in_port=in_port,
                                 actions=actions,
                                 data=msg.data)

        datapath.send_msg(out)

    # switch joins network
    @set_ev_cls(event.EventSwitchEnter)
    def switch_enter_handler(self, ev):
        self.logger.info("Switch entered: %s", ev.switch.dp.id)
        self.print_topology()

    # link added
    @set_ev_cls(event.EventLinkAdd)
    def link_add_handler(self, ev):
        self.logger.info("Link added: %s", ev.link)
        self.print_topology()

    # link removed
    @set_ev_cls(event.EventLinkDelete)
    def link_delete_handler(self, ev):
        self.logger.info("Link removed: %s", ev.link)
        self.print_topology()

    # print current topology
    def print_topology(self):
        switch_list = get_switch(self.topology_api_app, None)
        switches = [s.dp.id for s in switch_list]

        links_list = get_link(self.topology_api_app, None)
        links = [(l.src.dpid, l.dst.dpid) for l in links_list]

        self.logger.info("Current Switches: %s", switches)
        self.logger.info("Current Links: %s", links)