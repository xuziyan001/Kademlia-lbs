__author__ = 'X'
from twisted.internet import reactor
from msg import Msg
from node import Node


nodeCollection = []
ip = '127.0.0.1'
def main():
    seed = []
    for i in range(100):
        seed.append(ip+':'+str(i+10000))
    for each in seed:
        node = Node(each)
        nodeCollection.append(node)
        reactor.listenTCP(int(each.split(':')[1]), node)

def test_ping():
    node = Node('127.0.0.1:20000')
    reactor.listenTCP(20000, node)
    print node
    testMessage = Msg(0, 32812248528126350900072321242296281633, 10009, 293268701940054034179163628332357508988, 20000, -1, -1, True, {})
    node.send(testMessage, (32812248528126350900072321242296281633, 10009))
    node.send(testMessage, (32812248528126350900072321242296281633, 10009))

def test_find_node():
    node = Node('127.0.0.1:20000')
    reactor.listenTCP(20000, node)
    for each in nodeCollection[:50]:
        node.add_bucket((each.nodeId, node.port))
    testMessage = Msg(2, 0, 0, 293268701940054034179163628332357508988, 20000, 1, -1, True, {})
    node.find_node_cache[1] = [(32812248528126350900072321242296281633, 10009)]
    node.send(testMessage, (32812248528126350900072321242296281633, 10009))

def test_find_value():
    node = Node('127.0.0.1:20000')
    reactor.listenTCP(20000, node)
    for each in nodeCollection[:50]:
        node.add_bucket((each.nodeId, each.port))
    nodeCollection[99].store[2632163086015756094940243123419199943] = "yesIt'sMe!"

    node.active_key.append(2632163086015756094940243123419199943)
    testMessage = Msg(3, 0, 0, 293268701940054034179163628332357508988, 20000, 2632163086015756094940243123419199943, -1, True, {})
    node.find_node_cache[2632163086015756094940243123419199943] = [(32812248528126350900072321242296281633, 10009)]
    node.send(testMessage, (32812248528126350900072321242296281633, 10009))

def test_register():
    node = Node('127.0.0.1:20000')
    reactor.listenTCP(20000, node)
    for each in nodeCollection[:50]:
        node.add_bucket((each.nodeId, each.port))
    node.find_node_cache[2632163086015756094940243123419199943] = [(293268701940054034179163628332357508988, 20000)]
    testMessage = Msg(4, 0, 0, 293268701940054034179163628332357508988, 20000, 2632163086015756094940243123419199943, 'rsssssp', True, {})
    node.send(testMessage, (293268701940054034179163628332357508988, 20000))


if __name__ == "__main__":
    main()
    sid_port_collection = []
    for each in nodeCollection:
        sid_port_collection.append((each.nodeId,each.port))
    for each in nodeCollection:
        map(each.add_bucket,sid_port_collection)
    #test_ping()
    #test_find_node()
    #test_find_value()
    test_register()
    reactor.run()