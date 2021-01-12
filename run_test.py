import os
import requests
import json
import time
class Node:
    def __init__(self, external_port, ip, node_id):
        self.external_port = external_port
        self.ip = ip
        self.id = node_id
    def __str__(self):
        return "\n External Port: " + str(self.external_port) + "\n IP: " + self.ip + "\n ID: " + str(self.id)

def build_file(name):
    os.system("sudo docker build . -t " + name)

def build_view(count, ip = "10.0.0.", internal_port = 5000, external_port = 8080):
    nodes = []
    for x in range(2, count+2):
        node_ip = ip + str(x)
        node_external_port = external_port + x
        nodes.append(Node(node_external_port, node_ip, x-2))
    return nodes

def launch_instances(nodes, internal_port, net, name):
    for x in nodes:
        if len(nodes) == 1:
            launch_string = "sudo docker run"
        else:
            launch_string = "sudo docker run -d"
        view = [y.ip + ":" + str(internal_port) for y in nodes]
        view.remove(x.ip + ":" + str(internal_port))
        launch_string += " -p " + str(x.external_port) + ":" + str(internal_port)
        launch_string += " --ip=" + x.ip 
        launch_string += " --net=" + net
        launch_string += " -e VIEW="
        launch_string += ",".join(view)
        launch_string += " -e IPPORT=" + x.ip + ":" + str(internal_port)
        launch_string += " " + name
        os.system(launch_string)
    os.system("sudo docker ps")

def kill_all():
    os.system("sudo docker kill $(docker ps -q)")

def test_broadcast(nodes, local):
    node = nodes[0]
    address = local + ":" + str(node.external_port) + "/kv-store/test_POST"
    print("sending to ip: " + address)
    msg = {"key": "key", "val": "val"}
    response = requests.post(address, json = msg)
    print(response.json())

if __name__ == "__main__":

    local = "http://127.0.0.1"
    name = "paxos"
    internal_port = 5000
    external_port = 8080
    ip = "10.0.0."
    net = "mynet"

    kill_all()

    build_file(name)

    nodes = build_view(10, ip, internal_port, external_port)
    
    launch_instances(nodes, internal_port, net, name)

    time.sleep(1)

    test_broadcast(nodes, local)

# sudo docker run -p 8083:5000 --ip=10.0.0.20 --net=mynet  -e VIEW=10.0.0.20:5000,10.0.0.21:5000,10.0.0.22:5000,10.0.0.23:5000 -e IPPORT=10.0.0.20:8080 paxos

# sudo docker run -p 8082:5000 --ip=10.0.0.2 --net=mynet  -e VIEW=10.0.0.3:5000 -e IPPORT=10.0.0.2:5000 paxos
# sudo docker run -p 8083:5000 --ip=10.0.0.3 --net=mynet  -e VIEW=10.0.0.2:5000 -e IPPORT=10.0.0.3:5000 paxos