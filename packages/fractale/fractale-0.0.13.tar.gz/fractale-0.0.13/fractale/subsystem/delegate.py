# Save this file as, for example, /etc/flux/plugins/delegate.py

import flux
import flux.job
import json
import asyncio

async def depend_cb(p, topic, args):
    """
    Callback for the job.dependency.delegate topic.
    This function will be run by the Flux reactor's event loop.
    """
    jobid = None
    remote_h = None
    try:
        # CORRECT: Call arg_unpack as a method on the plugin context object 'p'
        unpacked_args = p.arg_unpack(
            args,
            "{s:I s:{s:s} s:o}",
            "id", "dependency", "value", "jobspec"
        )
        jobid = unpacked_args[0]
        uri = unpacked_args[1]
        jobspec = unpacked_args[2]

        p.log(f"Job {jobid}: Delegating to URI: {uri}")
        p.dependency_add(jobid, "delegated")
        remote_h = flux.Flux(uri=uri)

        if "attributes" in jobspec and \
           "system" in jobspec["attributes"] and \
           "dependencies" in jobspec["attributes"]["system"]:
            p.log(f"Job {jobid}: Removing dependencies from jobspec before delegation.")
            del jobspec["attributes"]["system"]["dependencies"]

        encoded_jobspec = json.dumps(jobspec)
        remote_jobid = await remote_h.job_submit(encoded_jobspec)
        p.log(f"Job {jobid}: Delegated successfully. Remote jobid is {remote_jobid}")
        p.event_post_pack(jobid, "delegated", "{s:I}", "jobid", int(remote_jobid))
        result = await remote_h.job_wait(remote_jobid, "result")
        
        if result['status'] == 0:
            p.log(f"Job {jobid}: Remote job {remote_jobid} succeeded. Completing local job.")
            p.raise_exception(jobid, "DelegationSuccess", 0, "Delegation successful")
        else:
            errstr = result.get('errstr', 'Unknown remote error')
            p.log_error(f"Job {jobid}: Remote job {remote_jobid} failed: {errstr}")
            p.raise_exception(jobid, "DelegationFailure", 0, f"Remote job failed: {errstr}")

    except Exception as e:
        p.log_error(f"Delegate plugin error for job {jobid}: {e}")
        if jobid:
            p.raise_exception(jobid, "DelegationFailure", 0, f"Plugin error: {e}")

    finally:
        if remote_h:
            remote_h.close()

def plugin_init(p):
    """
    Called by Flux when the plugin is loaded.
    The object 'p' is our handle to the plugin system.
    """
    def wrapper(topic, args, arg):
        asyncio.ensure_future(depend_cb(p, topic, args))
        return 0

    handlers = [
        {"topic": "job.dependency.delegate", "callback": wrapper, "arg": None}
    ]
    
    # CORRECT: Call register as a method on the plugin context object 'p'
    if p.register("py-delegate", handlers) < 0:
        p.log_error("Failed to register py-delegate plugin")
        return -1
    return 0
