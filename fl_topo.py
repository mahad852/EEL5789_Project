from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo

class MyTopo(Topo):
    def build(self):
        # create switches
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        switch3 = self.addSwitch('s3')

        # create hosts
        host11 = self.addHost('h11')
        host12 = self.addHost('h12')
        host13 = self.addHost('h13')
        host14 = self.addHost('h14')
        host15 = self.addHost('h15')
        host16 = self.addHost('h16')
        host17 = self.addHost('h17')
        
        host21 = self.addHost('h21')
        host22 = self.addHost('h22')
        host23 = self.addHost('h23')
        host24 = self.addHost('h24')
        host25 = self.addHost('h25')
        host26 = self.addHost('h26')
        host27 = self.addHost('h27')

        host31 = self.addHost('h31')
        host32 = self.addHost('h32')
        host33 = self.addHost('h33')
        host34 = self.addHost('h34')
        host35 = self.addHost('h35')
        host36 = self.addHost('h36')
        host37 = self.addHost('h37')

        # add links
        self.addLink(switch1, host11)
        self.addLink(switch1, host12)
        self.addLink(switch1, host13)
        self.addLink(switch1, host14)
        self.addLink(switch1, host15)
        self.addLink(switch1, host16)
        self.addLink(switch1, host17)

        self.addLink(switch1, host21)
        self.addLink(switch1, host22)
        self.addLink(switch1, host23)
        self.addLink(switch1, host24)
        self.addLink(switch1, host25)
        self.addLink(switch1, host26)
        self.addLink(switch1, host27)

        self.addLink(switch1, host31)
        self.addLink(switch1, host32)
        self.addLink(switch1, host33)
        self.addLink(switch1, host34)
        self.addLink(switch1, host35)
        self.addLink(switch1, host36)
        self.addLink(switch1, host37)

        self.addLink(switch1, switch2)
        self.addLink(switch2, switch3)

def run():
    topo = MyTopo()
    net = Mininet(topo=topo, controller=RemoteController, autoSetMacs=True)

    # start the controller
    net.addController('controller', controller=RemoteController,
                      ip='127.0.0.1', port=6633)

    # start the switches
    for switch in net.switches:
        switch.start([net.controllers[0]])

    # start the hosts
    for host in net.hosts:
        host.cmd('ifconfig lo up')

    net.start()

    # set up flow limit controller
    flow_controller = net.controllers[0].newCustomController(
        'flow_controller', 'flow_limit_controller.FlowLimitController')
    net.controllers.append(flow_controller)

    # wait for switches to connect to controller
    net.waitConnected()

    print("Network setup complete!")
    print("Run the command 'sudo mn -c' to clean up the network after testing.")

    net.interact()

    net.stop()

if __name__ == '__main__':
    run()
