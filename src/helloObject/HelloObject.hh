#ifndef __LEARNING_GEM5_HELLO_OBJECT_HH__
#define __LEARNING_GEM5_HELLO_OBJECT_HH__

#include "helloObject/GoodbyeObject.hh"
#include "params/HelloObject.hh"
#include "sim/sim_object.hh"

namespace gem5
{

class HelloObject : public SimObject
{
    private:
        void processEvent();
        const std::string myName;
        const Tick latency;
        int timesLeft;

        EventFunctionWrapper event;
        GoodbyeObject *goodbye;
    public:
        HelloObject(const HelloObjectParams &p);
        void startup() override;
};

} // namespace gem5

#endif // __LEARNING_GEM5_HELLO_OBJECT_HH__
