
#include "helloObject/SimpleDRAM.hh"

#include "base/compiler.hh"
#include "debug/SimpleDRAM.hh"
#include "sim/system.hh"

namespace gem5{
namespace memory
{
SimpleDRAM::SimpleDRAM(const SimpleDRAMParams &params) :
    AbstractMemory(params),
    latency(params.latency),
    cpuPort(params.name + ".cpu_side", this)
{
    auto it=params.ranges.begin();
    for (; it != params.ranges.end(); ++it) {
        ranges.push_back(*it);
    }
    DPRINTF(SimpleDRAM,"constructing SimpleDRAM\n");
}
DrainState
SimpleDRAM::drain()
{
    panic("DRAIN UNIMPL");
    return DrainState::Drained;
}


void 
SimpleDRAM::init(){
    DPRINTF(SimpleDRAM, "Initializing SimpleDRAM\n");
    ClockedObject::init();
    if (cpuPort.isConnected()) {
        cpuPort.sendRangeChange();
    }
}
Port & SimpleDRAM::getPort(const std::string &if_name, PortID idx)
{
    DPRINTF(SimpleDRAM, "getPort called with if_name %s and idx %d\n", if_name, idx);
    if (if_name == "cpu_side") {
        return cpuPort;
    }
    else {
        return ClockedObject::getPort(if_name, idx);
    }
}
AddrRangeList SimpleDRAM::CPUSidePort::getAddrRanges() const
{
    DPRINTF(SimpleDRAM, "CPUSidePort getAddrRanges\n");
    return owner->getAddrRanges();
}
AddrRangeList SimpleDRAM::getAddrRanges() const
{
    DPRINTF(SimpleDRAM, "Sending new ranges\n");
    return ranges;
}

void SimpleDRAM::CPUSidePort::recvFunctional(PacketPtr pkt)
{
    // Just forward to the cache.
    return owner->handleFunctional(pkt);
}

bool SimpleDRAM::CPUSidePort::recvTimingReq(PacketPtr pkt)
{
    DPRINTF(SimpleDRAM, "Got request %s\n", pkt->print());
    owner->handleTiming(pkt);
    return true;
}

void SimpleDRAM::CPUSidePort::recvRespRetry()
{
    assert(blockedPacket != nullptr);
    PacketPtr pkt = blockedPacket;
    blockedPacket = nullptr;

    DPRINTF(SimpleDRAM, "Retrying response pkt %s\n", pkt->print());
    sendPacket(pkt);
}
void SimpleDRAM::CPUSidePort::sendPacket(PacketPtr pkt)
{
    // If we can't send the packet across the port, store it for later.
    DPRINTF(SimpleDRAM, "Sending %s to CPU\n", pkt->print());
    if (!sendTimingResp(pkt)) {
        DPRINTF(SimpleDRAM, "failed!\n");
        blockedPacket = pkt;
    }
}
void SimpleDRAM::handleFunctional(PacketPtr pkt)
{
    panic("handleFunctional UNIMPL");
}
void SimpleDRAM::handleTiming(PacketPtr pkt)
{
    panic("handleTiming UNIMPL");
}
}//namespace gem5
}
