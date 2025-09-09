"""
gpframe: A general-purpose framework for routine execution with concurrency and event handling.
------------

Note
---------------
This library is in an early stage of development.
It is generally unstable: documentation and tests are incomplete,
and the API may undergo breaking changes without notice.

Core Components
---------------
- FrameBuilder (from .api.builder):
  Factory function to obtain a FrameBuilderType.  
  Accepts a routine to be executed inside a Frame.  
  The routine can be synchronous or asynchronous.

- FrameBuilderType (from .api.builder):
  API to configure the Frame name, logger, and handlers.  
  Calling FrameBuilderType.start() launches the Frame and returns a Frame object.

- Frame (from .api.frame):
  Represents the entire lifecycle of a Frame.  
  Provides Frame.task for accessing the Frame's execution task.  
  Allows writing to the request message map via Frame.request.update().

- EventContext (from .api.contexts):
  Allows writing to the event_message map through EventContext.event_message.update().

- RoutineContext (from .api.contexts):
  Allows writing to the routine_message map through RoutineContext.routine_message.update().

- Outcome (from .api.outcome):
  Passed to the terminated_callback after the Frame has finished (after on_close).  
  Provides read-only access to all message maps.  
  Each message map is a snapshot of its state at termination.


Message Maps
------------
gpframe defines four synchronized message maps and one result container.  
These maps are the core mechanism for communication between the Frame,
the routine, and event handlers.

1. environment
   - Purpose: Immutable configuration or contextual information.
   - Access:
       Read: Frame, EventContext, RoutineContext
       Write: Frame (setup stage only)
   - Example: constants, system configuration, resource identifiers.

2. request
   - Purpose: Incoming requests or instructions that affect routine behavior.
   - Access:
       Read: Frame, EventContext, RoutineContext
       Write: Frame (via Frame.request.update())
   - Example: runtime parameters, control flags.

3. event_message
   - Purpose: Event-driven updates produced by event handlers.
   - Access:
       Read: Frame, RoutineContext
       Write: EventContext (via EventContext.event_message.update())
   - Example: status events, log signals, external notifications.

4. routine_message
   - Purpose: Communication channel from the routine to other components.
   - Access:
       Read: Frame, EventContext
       Write: RoutineContext (via RoutineContext.routine_message.update())
   - Example: progress reports, intermediate results.

5. routine_result
   - Purpose: Result value of the routine execution.
   - Access:
       Read: EventContext.routine_result
       Write: set internally by each routine execution
   - Behavior:
       Updated every time the routine finishes (success, error, or cancellation).  
       After the Frame terminates, the last value represents the final outcome.
   - Special values:
       NO_VALUE = not yet executed or failed

Lifecycle and Access Rules
--------------------------
- All maps are thread-safe (backed by SynchronizedMapReader/SynchronizedMapUpdater).
- During Frame execution, access is restricted according to context type.
- After Frame termination, direct access is invalid and raises TerminatedError.
  To inspect final state, use Outcome which contains a snapshot of all maps.


Error Handling
--------------
- NO_VALUE (from .impl.routine.result):
  Initial value of EventContext.routine_result.value.  
  Indicates that no routine result exists (not yet executed, exception raised, etc.).

- TerminatedError (from .impl.builder):
  Raised when attempting to access message maps after a Frame has terminated.  
  In such cases, maps must be accessed via Outcome.

- FutureTimeoutError, ThreadCleanupTimeoutError (from .impl.routine.asynchronous):
  Timeout-related errors for asynchronous routines and thread cleanup.

- SubprocessTimeoutError (from .impl.routine.subprocess):
  Timeout error for subprocess routines.

- Throw (from .impl.handler.exception):
  Exception wrapper for re-throwing errors without being wrapped as HandlerError.  
  Useful when propagating exceptions such as asyncio.CancelledError directly.

"""

from .api.builder import FrameBuilder

from .api.builder import FrameBuilderType

from .api.frame import Frame

from .api.contexts import EventContext
from .api.contexts import RoutineContext

from .api.outcome import Outcome

from .impl.routine.result import NO_VALUE

from .impl.builder import TerminatedError

from .impl.routine.asynchronous import FutureTimeoutError, ThreadCleanupTimeoutError
from .impl.routine.subprocess import SubprocessTimeoutError

from .impl.handler.exception import Throw

__all__ = ("FrameBuilder", "FrameBuilderType",
           "Frame",
           "EventContext", "RoutineContext",
           "Outcome",
           "NO_VALUE",
           "TerminatedError", 
           "FutureTimeoutError", "ThreadCleanupTimeoutError",
           "SubprocessTimeoutError",
           "Throw")
