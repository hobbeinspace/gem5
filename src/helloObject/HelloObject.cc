#include "helloObject/HelloObject.hh"

#include <iostream>

#include "base/trace.hh"
#include "debug/HelloObject.hh"

namespace gem5
{

HelloObject::HelloObject(const HelloObjectParams &params) :
    SimObject(params),event([this] { processEvent();},name()),
    myName(params.name),
    latency(params.time_to_wait),
    timesLeft(params.number_of_fires)
    ,goodbye(params.goodbye_object)
{
    DPRINTF(HelloObject, "Hello World! From a SimObject!\n");
    panic_if(!goodbye, "HelloObject must have
        a GoodbyeObject to say goodbye to!\n");
}

void
HelloObject::processEvent()
{
    timesLeft--;
    DPRINTF(HelloObject, "Hello world! Processing the event!\n");
    if (timesLeft==0){
        DPRINTF(HelloObject,"DONE FIRING!!\n");
        goodbye->sayGoodbye(myName);
    }
    else{
        schedule(event,curTick()+latency);
    }
}

void
HelloObject::startup()
{
    schedule(event, latency);
}


} // namespace gem5
