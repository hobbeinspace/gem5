#include "mem/port.hh"
#include "params/SimpleMemobj.hh"
#include "sim/sim_object.hh"

namespace gem5
{
class SimpleMemobj : public SimObject
{
    private:
        class CPUSidePort : public ResponsePort
        {
            private:
                SimpleMemobj *owner;
                bool needRetry;
                PacketPtr blockedPacket;

            public:
                CPUSidePort(const std::string& name, SimpleMemobj *owner) :
                    ResponsePort(name, owner), owner(owner),needRetry(false),
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

        class MemSidePort : public RequestPort
        {
            private:
                SimpleMemobj *owner;
                PacketPtr blockedPacket;

            public:
                MemSidePort(const std::string& name, SimpleMemobj *owner) :
                RequestPort(name, owner), owner(owner),
                blockedPacket(nullptr)
                { }
                void sendPacket(PacketPtr pkt);

            protected:
                bool recvTimingResp(PacketPtr pkt) override;
                void recvReqRetry() override;
                void recvRangeChange() override;
        };
        CPUSidePort instPort;
        CPUSidePort dataPort;
        MemSidePort memPort;
        bool blocked;
        bool handleRequest(PacketPtr pkt);
        bool handleResponse(PacketPtr pkt);
        void sendRangeChange();
        void handleFunctional(PacketPtr pkt);
        AddrRangeList getAddrRanges() const;
        EventFunctionWrapper event;
        PacketPtr scheduledPacket;
        void processEvent();

    public:
        SimpleMemobj(const SimpleMemobjParams& params);
        Port &getPort(const std::string &if_name,
                  PortID idx=InvalidPortID) override;
};


} // namespace gem5
