__author__ = 'X'
import hashlib
from kbuckets import KBuckets
from msg import Msg
import msg
import time
import kbuckets


from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer
from twisted.protocols  import  basic


class KademliaServer(basic.LineReceiver):

    def lineReceived(self, message):
        d = self.factory.handle_message(message)

        def onError(err):
            return 'internal error in server'
        d.addErrback(onError)

        def writeResponse(message):
            #self.transport.write('server callback writeResponse writes:'+message+'\r\n')
            self.transport.write('\r\n')
            self.transport.loseConnection()
        d.addCallback(writeResponse)


class KademliaClient(protocol.Protocol):
    """Once connected, send a message, then print the result."""

    def connectionMade(self):
        self.transport.write(self.factory.get_message()+"\r\n")
        #print "client write msg: %s" % self.factory.get_message()

    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        #print "Server said:", data
        self.transport.loseConnection()

    def connectionLost(self, reason):
        print "\r\n"

class KademliaClientFactory(protocol.ClientFactory):
    protocol = KademliaClient
    def __init__(self, message):
        self.message = message

    def get_message(self):
        return  self.message

    def clientConnectionFailed(self, connector, reason):
        print "\r\n"
#        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "\r\n"
 #       reactor.stop()

class Node(protocol.ServerFactory):

    protocol = KademliaServer
    def __init__(self, ip):
        self.nodeId = int(hashlib.md5(ip).hexdigest(), 16)
        self.kBuckets = KBuckets()
        self.port = int(ip.split(':')[1])
        self.append_to_add = []
        self.store = {}
        self.find_node_cache = {}
        self.find_node_already = {}
        self.active_key = []

    def __str__(self):
        return str(self.nodeId)+" "+str(self.port)

    def parse_info(self, info):
        """
        :param info: info for str
        :return: dict for {'str':'str'}
        """
        if info == '':
            return {}
        info_res = {}
        list_info = info.split('&')
#        print 'list_info: %s' % list_info
        for each in list_info:
            each_list = each.split('=')
            info_res[each_list[0].strip()] = each_list[1].strip()
        return info_res

    def dic_to_str(self, dic):
        res = ''
        if dic == {}:
            return res
        for each in dic.keys():
            res += str(each)+'='+str(dic[each])+'&'
        return res[:-1]


    def handle_message(self, message):
        print str(self.nodeId)+' '+str(self.port) + ' recv msg: %s' % message
        time.sleep(1)
        mesg = message.split(' ')
        rpc_type = int(mesg[0])
        target_id = long(mesg[1])
        target_port = int(mesg[2])
        source_id = long(mesg[3])
        source_port = int(mesg[4])
        key = long(mesg[5])
        value = mesg[6]
        status = True if mesg[7]=="True" else False
        info = self.parse_info(mesg[8])
        res = Msg(rpc_type, target_id, target_port, source_id, source_port, key, value, status, info)
        if rpc_type == msg.PING:
            self.handle_ping(res)
            return defer.succeed("handle_ping")
        elif rpc_type == msg.PONG:
            self.handle_pong(res)
            return defer.succeed("handle_pong")
        elif rpc_type == msg.STORE:
            self.handle_store(res)
            return  defer.succeed("handle_store")
        elif rpc_type == msg.FIND_NODE:
            self.handle_find_node(res)
            return  defer.succeed("handle_find_node")
        elif rpc_type == msg.FIND_NODE_RETURN:
            self.handle_find_node_return(res)
            return  defer.succeed("handle_find_node_return")
        elif rpc_type == msg.FIND_VALUE:
            self.handle_find_value(res)
            return  defer.succeed("handle_find_value")
        elif rpc_type == msg.FIND_VALUE_RETURN:
            self.handle_find_value_return(res)
            return  defer.succeed("handle_find_value_return")
        elif rpc_type == msg.REGISTER:
            self.handle_register(res)
            return  defer.succeed("handle_register")

    def find_closest_node(self, id):
        """
        find closest node in k buckets
        :param id: sid to search k buckets
        :return: (sid, port) tuple
        """
        bucketNum = self.find_bucket_num(id)
        return self.kBuckets.find_closest_node(id, bucketNum)

    def add_bucket(self, id):
        """
        :param id: (sid,port) tuple to add
        :return: nothing
        """
        bucketNum = self.find_bucket_num(id[0])
        if bucketNum == -1: #self pass
            pass
        else:
            self.kBuckets.add_bucket(id, bucketNum)
        """
        current_bucket = self.kBuckets.bucket[bucketNum]
        if len(current_bucket) == kbuckets.K:
            if id in current_bucket:
                print "%s refresh %s." % (self.nodeId, id[0])
                self.kBuckets.bucket[bucketNum].remove(id)
                self.kBuckets.bucket[bucketNum].append(id)
                self.append_to_add = []
            else:
                self.append_to_add.append(id)
                info = {}
                info['pre_sid'] = self.nodeId
                info['pre_port'] = self.port
                testping =  Msg(msg.PING, current_bucket[0][0], self.nodeId, self.port, current_bucket[0][0], True, info, 'forward')
                self.send(testping, (current_bucket[0][0], current_bucket[0][1]))
        else:
            self.kBuckets.add_bucket(id, bucketNum)
            print "%s add %s." % (self.nodeId, id[0])
        """

    def delete_bucket(self, id):
        """
        :param id: sid to delete
        :return: nothing
        """
        bucketNum = self.find_bucket_num(id)
        self.kBuckets.delete_bucket(id, bucketNum)

    def find_bucket_num(self, id):
        """
        :param id: sid to locate k-bucket
        :return: bucket number
        """
        sid = id
        num = 0
        distance = sid ^ self.nodeId
        if distance == 0:
            return -1 #that is myself
        while distance >>  1 != 0:
            distance = distance >> 1
            num += 1
        return num

    def handle_ping(self, message):
        rpc_type = msg.PONG
        target_id = message.source_id
        target_port = message.source_port
        source_id = self.nodeId
        source_port = self.port
        key = -1
        value = -1
        status = True
        info = {}
        result = Msg(rpc_type, target_id, target_port, source_id, source_port, key, value, status, info)
        self.send(result, (target_id, target_port))

    def handle_pong(self, message):
        id = (message.source_id, message.source_port)
        self.add_bucket(id)

    def handle_store(self, message):
        self.store[message.key] = message.value
        print "%s %s store %s for key %s." % (self.nodeId, self.port, message.value, message.key)

    def handle_find_node(self, message):
        key = message.key
        target_node = self.find_closest_node(key)
        print "%s find closest node %s for key %s." % (self.port, target_node, key)
        info = {}
        for each in target_node:
            info[each[0]] = each[1]
        rpc_type = msg.FIND_NODE_RETURN
        target_id = message.source_id
        target_port = message.source_port
        source_id = self.nodeId
        source_port = self.port
        value = message.value
        status = True
        result = Msg(rpc_type, target_id, target_port, source_id, source_port, key, value, status, info)
        self.send(result, (target_id, target_port))

    def handle_find_node_return(self, message):
        key = message.key
        value = message.value
        info = message.info
        print "key: %s" % key
        #if key not in self.find_node_cache:
        #    self.find_node_cache[key] = []
        if key not in self.find_node_already:
            self.find_node_already[key] = []
        source_id = message.source_id
        source_port = message.source_port
        self.find_node_already[key].append((source_id, source_port))
        info_list = []
        for each in info:
            sid_port = (long(each), int(info[each]))
            info_list.append(sid_port)
        if len(set(info_list).difference(set(self.find_node_cache[key]))) == 0 and set(self.find_node_cache[key]) == set(self.find_node_already[key]):
            result = sorted(self.find_node_already[key], cmp=lambda x,y: cmp(x[0] ^key, y[0] ^key))
            result = result if len(result) < kbuckets.k else result[:kbuckets.k]
            print "find node finish, result is %s."  % result
            self.find_node_already[key] = []
            self.find_node_cache[key] = []
            if value != '-1':
                for each in result:
                    store_query = Msg(1, each[0], each[1], self.nodeId, self.port, key, value, True, {})
                    self.send(store_query, (each[0], each[1]))
            return result
        for sid_port in info_list:
            if sid_port not in self.find_node_cache[key]:
                self.find_node_cache[key].append(sid_port)
                rpc_type = msg.FIND_NODE
                target_id = sid_port[0]
                target_port = sid_port[1]
                source_id = self.nodeId
                source_port = self.port
                value = message.value
                status = True
                info = {}
                result = Msg(rpc_type, target_id, target_port, source_id, source_port, key, value, status, info)
                self.send(result, (target_id, target_port))
        print "cache: %s" % self.find_node_cache[key]
        print "already: %s" % self.find_node_already[key]

    def handle_find_value(self, message):
        key = message.key
        if key in self.store:
            print "%s %s find value %s for key %s." % (self.nodeId, self.port, self.store[key], key)
            rpc_type = msg.FIND_VALUE_RETURN
            target_id = message.source_id
            target_port = message.source_port
            source_id = self.nodeId
            source_port = self.port
            value = self.store[key]
            status = True
            info = {}
            result = Msg(rpc_type, target_id, target_port, source_id, source_port, key, value, status, info)
            self.send(result, (target_id, target_port))
            return
        target_node = self.find_closest_node(key)
        print "%s find closest node %s for key %s." % (self.port, target_node, key)
        info = {}
        for each in target_node:
            info[each[0]] = each[1]
        rpc_type = msg.FIND_VALUE_RETURN
        target_id = message.source_id
        target_port = message.source_port
        source_id = self.nodeId
        source_port = self.port
        value = -1
        status = False
        result = Msg(rpc_type, target_id, target_port, source_id, source_port, key, value, status, info)
        self.send(result, (target_id, target_port))

    def handle_find_value_return(self, message):
        key = message.key
        if key not in self.active_key:
            return "already found value for key %s." % key
        if message.status == False:
            info = message.info
            print "key: %s" % key
            if key not in self.find_node_already:
                self.find_node_already[key] = []
            source_id = message.source_id
            source_port = message.source_port
            self.find_node_already[key].append((source_id, source_port))
            print "cache: %s" % self.find_node_cache[key]
            print "already: %s" % self.find_node_already[key]
            info_list = []
            for each in info:
                sid_port = (long(each), int(info[each]))
                info_list.append(sid_port)
            if len(set(info_list).difference(set(self.find_node_cache[key]))) == 0 and set(self.find_node_cache[key]) == set(self.find_node_already[key]): #find all nodes
                print "cannot find value for key."  % key
                self.find_node_already[key] = []
                self.find_node_cache[key] = []
                self.active_key.remove(key)
                return "no found key %s." % key
            for sid_port in info_list:
                if sid_port not in self.find_node_cache[key]:
                    self.find_node_cache[key].append(sid_port)
                    rpc_type = msg.FIND_VALUE
                    target_id = sid_port[0]
                    target_port = sid_port[1]
                    source_id = self.nodeId
                    source_port = self.port
                    value = -1
                    status = True
                    info = {}
                    result = Msg(rpc_type, target_id, target_port, source_id, source_port, key, value, status, info)
                    self.send(result, (target_id, target_port))
        else:
            self.active_key.remove(key)
            self.find_node_already[key] = []
            self.find_node_cache[key] = []
            print "%s %s find value %s for key %s." % (self.nodeId, self.port, message.value, key)
            return message.value

    def handle_register(self, message):
        key = message.key
        value = message.value
        query_message = Msg(2, 0, 0, self.nodeId, self.port, key, value, True, {})
        self.send(query_message, (self.nodeId, self.port))

    def send(self, message, id):
        port = id[1]
        #print "now port is %s" % port
        msg = str(message.rpc)+' '+str(message.target_id)+' '+str(message.target_port)+' '+str(message.source_id)+' '+str(message.source_port) \
             +' '+str(message.key)+' '+str(message.value)+' '+str(message.status)+' '+self.dic_to_str(message.info)
        f = KademliaClientFactory(msg)
        reactor.connectTCP("localhost", port, f)
        print str(self.nodeId)+' '+str(self.port)+" send message: %s to port %s." % (msg, port)