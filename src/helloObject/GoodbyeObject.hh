#ifndef __LEARNING_GEM5_GOODBYE_OBJECT_HH__
#define __LEARNING_GEM5_GOODBYE_OBJECT_HH__

#include <string>

#include "params/GoodbyeObject.hh"
#include "sim/sim_object.hh"

namespace gem5{
class GoodbyeObject : public SimObject
{
    private:
        void processEvent();


        void fillBuffer();

        EventFunctionWrapper event;

    /// The bytes processed per tick.
        float bandwidth;

    /// The size of the buffer we are going to fill.
        int bufferSize;

    /// The buffer we are putting our message in.
        char *buffer;

    /// The message to put into the buffer.
        std::string message;

    /// The amount of the buffer we've used so far.
        int bufferUsed;

    public:
        GoodbyeObject(const GoodbyeObjectParams& p);
        ~GoodbyeObject();


        void sayGoodbye(std::string name);
};
} // namespace gem5

#endif // __LEARNING_GEM5_GOODBYE_OBJECT_HH__
