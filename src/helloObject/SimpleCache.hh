#ifndef __LEARNING_GEM5_SIMPLE_CACHE_SIMPLE_CACHE_HH__
#define __LEARNING_GEM5_SIMPLE_CACHE_SIMPLE_CACHE_HH__

#include <unordered_map>

#include "base/random.hh"
#include "base/statistics.hh"
#include "mem/port.hh"
#include "params/SimpleCache.hh"
#include "sim/clocked_object.hh"

namespace gem5
{
class SimpleCache : public ClockedObject
{
    private:
        class AccessEvent : public Event
        {
            private:
                SimpleCache *cache;
                PacketPtr pkt;
            public:
                AccessEvent(SimpleCache *cache, PacketPtr pkt) :
                    Event(Default_Pri, AutoDelete), cache(cache), pkt(pkt)
                { }
                void process() override {
                    cache->accessTiming(pkt);
                }
        };
        class CPUSidePort : public ResponsePort
        {
            private:
                SimpleCache *owner;
                bool needRetry;
                PacketPtr blockedPacket;
                int id;

            public:
                CPUSidePort(const std::string& name, int id,
                    SimpleCache *owner) :
                    ResponsePort(name, owner),
                    owner(owner),needRetry(false),id(id),
                    blockedPacket(nullptr)
                { }

                AddrRangeList getAddrRanges() const override;
                void trySendRetry();
                void sendPacket(PacketPtr pkt);

            protected:
                Tick recvAtomic(PacketPtr pkt) override {
                     panic("recvAtomic unimpl.");
                    }
                void recvFunctional(PacketPtr pkt) override;
                bool recvTimingReq(PacketPtr pkt) override;
                void recvRespRetry() override;
        };

        class MemSidePort : public RequestPort
        {
            private:
                SimpleCache *owner;
                PacketPtr blockedPacket;

            public:
                MemSidePort(const std::string& name, SimpleCache *owner) :
                RequestPort(name, owner), owner(owner),
                blockedPacket(nullptr)
                { }
                void sendPacket(PacketPtr pkt);

            protected:
                bool recvTimingResp(PacketPtr pkt) override;
                void recvReqRetry() override;
                void recvRangeChange() override;
        };
        std::vector<CPUSidePort> cpuPorts;
        MemSidePort memPort;
        bool blocked;
        bool handleRequest(PacketPtr pkt,int port_id);
        bool handleResponse(PacketPtr pkt);
        void sendRangeChange() const;
        void handleFunctional(PacketPtr pkt);
        AddrRangeList getAddrRanges() const;
        void sendResponse(PacketPtr pkt);

        void processEvent();
        void accessTiming(PacketPtr pkt);
        bool accessFunctional(PacketPtr pkt);
        void insert(PacketPtr pkt);

        const Cycles latency;
        const Addr blockSize;
        const unsigned capacity;
        PacketPtr originalPacket;
        PacketPtr outstandingPacket;
        int waitingPortId;
        Tick missTime;
        std::unordered_map<Addr, uint8_t*> cacheStore;
        Random::RandomPtr rng = Random::genRandom();

    protected:
        struct SimpleCacheStats : public statistics::Group
        {
            SimpleCacheStats(statistics::Group *parent);
            statistics::Scalar hits;
            statistics::Scalar misses;
            statistics::Histogram missLatency;
            statistics::Formula hitRatio;
        } stats;
    public:
        SimpleCache(const SimpleCacheParams& params);
        Port &getPort(const std::string &if_name,
                  PortID idx=InvalidPortID) override;
};

}

#endif // __LEARNING_GEM5_SIMPLE_CACHE_SIMPLE_CACHE_HH__
