__author__ = 'X'
BUCKET_NUM = 160
K = 5
a = 3
k = 5

class KBuckets:
    def __init__(self):
        self.bucket = []
        for i in range(BUCKET_NUM):
            self.bucket.append([])

    def __str__(self):
        for i in range(BUCKET_NUM):
            if len(self.bucket[i]) != 0:
                for each in self.bucket[i]:
                    print "bucket %d : %s." % (i, each)
        return ""

    def add_bucket(self, id, bucketNum):
        """
        :param id: (sid, port) tuple
        :param bucketNum: bucket number to add
        :return: no return
        """
        currentBucket = self.bucket[bucketNum]
        if id in currentBucket:
            print "refresh %s in bucket %d" % (id, bucketNum)
            self.bucket[bucketNum].remove(id)
            self.bucket[bucketNum].append(id)
        else:
            if len(currentBucket) < K:
                print "add %s in bucket %d" % (id, bucketNum)
                self.bucket[bucketNum].append(id)
            else:
                pass
                #send ping call

    def delete_bucket(self, id, bucketNum):
        """
        :param id: only need sid
        :param bucketNum:
        :return:
        """
        if id in self.bucket[bucketNum]:
            self.bucket[bucketNum].remove(id)
        #    print "delete %s" % id

    def find_closest_node(self, id, bucketNum):
        """
        find closest node in a particular bucket
        :param id:  sid for int
        :param bucketNum: int
        :return: (sid, port) tuple for (int, int)
        """
        result = self.bucket[bucketNum]
        for i in range(1,BUCKET_NUM):
            if len(result) < a:
                result += self.bucket[bucketNum-i] if bucketNum-i >= 0 else []
                result += self.bucket[bucketNum+i] if bucketNum+i < BUCKET_NUM else []
            else:
                break
#        print result
        sort_bucket = sorted(result, cmp=lambda x,y: cmp(x[0] ^id, y[0] ^id))
        return sort_bucket[:a]



