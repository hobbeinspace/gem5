#ifndef __LEARNING_GEM5_SIMPLE_DRAM_SIMPLE_DRAM_HH__
#define __LEARNING_GEM5_SIMPLE_DRAM_SIMPLE_DRAM_HH__

#include <unordered_map>

// #include "base/random.hh"
// #include "base/statistics.hh"

#include "mem/port.hh"
#include "params/SimpleDRAM.hh"
#include "mem/abstract_mem.hh"
namespace gem5
{
namespace memory
{
class SimpleDRAM : public AbstractMemory
{
    private:
        class CPUSidePort : public ResponsePort
        {
            private:
                SimpleDRAM *owner;
                bool needRetry;
                PacketPtr blockedPacket;

            public:
                CPUSidePort(const std::string& name, SimpleDRAM *owner) :
                    ResponsePort(name, owner), owner(owner), needRetry(false),
                    blockedPacket(nullptr)
                { }

                AddrRangeList getAddrRanges() const override;
                void trySendRetry();
                void sendPacket(PacketPtr pkt);

            protected:
                Tick recvAtomic(PacketPtr pkt) override {
                     panic("recvAtomic unimpl."); }
                void recvFunctional(PacketPtr pkt) override;
                bool recvTimingReq(PacketPtr pkt) override;
                void recvRespRetry() override;
        };
        CPUSidePort cpuPort;
        bool handleRequest(PacketPtr pkt,int port_id);
        void sendRangeChange() const;
        void handleFunctional(PacketPtr pkt);
        void handleTiming(PacketPtr pkt);
        AddrRangeList getAddrRanges() const;
        void sendResponse(PacketPtr pkt);

        void processEvent();
        void accessTiming(PacketPtr pkt);
        void accessFunctional(PacketPtr pkt);
        void insert(PacketPtr pkt);
        const Cycles latency;
        std::unordered_map<Addr, uint8_t*> DRAMStore;
        uint8_t* pmemAddr;
    protected:

        AddrRangeList ranges;
    public:
        SimpleDRAM(const SimpleDRAMParams& params);
        Port &getPort(const std::string &if_name,
                  PortID idx=InvalidPortID) override;
        DrainState drain() override;        
        void init() override;
};

}
}

#endif // __LEARNING_GEM5_SIMPLE_DRAM_SIMPLE_DRAM_HH__
