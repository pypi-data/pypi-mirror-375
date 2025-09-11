"""Startup script run when the VCE launches."""

import asyncio
import os
import re
from asyncio import subprocess

import tornado
import tornado.websocket

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Your VCE is starting</title>
  <style>
    html { font-family: Arial, Helvetica, sans-serif; }
    #status { position: absolute; left: 50%; top: 50%; max-width: 30rem; transform: translate(-50%,-50%); border-top-right-radius: 1rem; box-shadow: 0 0 #0000,var(--tw-ring-shadow, 0 0 #0000),0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1); }
    h1 { font-size: 1rem; font-weight: bold; padding: 0.5rem 1rem; margin: 0; background-color: rgb(205 207 234); border-top-right-radius: 1rem; color: rgb(39 38 87); }
    #messages { max-height: 12rem; margin: 0; padding: 0.5rem 1rem; overflow: auto; border-left: 1px solid; border-bottom: 1px solid; border-right: 1px solid; border-color: rgb(214 214 214); }
    #messages > li { list-style-type: none; display: flex; flex-direction: row; align-items: center; margin-bottom: 0.5rem; }
    .msg { flex: 1 1 auto; padding-right: 1rem; }
    .icon { flex: 0 0 auto; display: block; width: 1.5rem; height: 1.5rem; color: rgb(39 38 87); }
    .icon svg { display: block; width: 100%; height: 100%; fill: currentColor; }
    .icon.busy svg { animation: spin 1s linear infinite; }
    .icon.failure { color: rgb(168 12 12); }

    @keyframes spin {
      from {
        transform: rotate(0deg);
      }
      to {
        transform: rotate(360deg);
      }
    }
  </style>
</head>
<body>
  <div id="status" role="status">
    <h1 id="header" tabindex="-1">Your VCE is starting</h1>
    <ul id="messages" aria-live="true">
    </ul>
  </div>
  <script>
    const header = document.querySelector("#header");
    header.focus();

    const messages = document.querySelector("#messages");
    const ws = new WebSocket(((window.location.protocol === "https:") ? "wss://" : "ws://") + window.location.host + "{JUPYTERHUB_SERVICE_PREFIX}ocl-status");
    addNewProgress({text: "Preparing startup"});

    /**
     * Handle websocket messages.
     */
    ws.addEventListener("message", (msg) => {
      const data = JSON.parse(msg.data);
      if (data.type === "start") {
        completeProgress({status: "success"});
        addNewProgress(data);
      } else {
        completeProgress(data);
      }
    });

    /**
     * Handle closing the websocket connection.
     */
    ws.addEventListener("close", () => {
      completeProgress({status: "success"});
      addNewProgress({text: "Waiting for the interface to be ready..."});
      setTimeout(checkReady, 5000);
    });

    /**
     * Add a new active progress element
     */
    function addNewProgress(progress) {
      const item = document.createElement("li");
      item.innerHTML = '<span class="msg">' + progress.text + '</span><span class="icon busy"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>working</title><path d="M12,6V9L16,5L12,1V4A8,8 0 0,0 4,12C4,13.57 4.46,15.03 5.24,16.26L6.7,14.8C6.25,13.97 6,13 6,12A6,6 0 0,1 12,6M18.76,7.74L17.3,9.2C17.74,10.04 18,11 18,12A6,6 0 0,1 12,18V15L8,19L12,23V20A8,8 0 0,0 20,12C20,10.43 19.54,8.97 18.76,7.74Z" /></svg></span>';
      messages.appendChild(item);
      setTimeout(() => {
        item.scrollIntoView();
      }, 0);
    }

    /**
     * Update the active progress to either success or failure.
     */
    function completeProgress(progress) {
      const current = document.querySelector(".busy");
      if (current !== null) {
        current.classList.remove("busy");
        if (progress.status === "success") {
          current.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>Completed successfully</title><path d="M9,20.42L2.79,14.21L5.62,11.38L9,14.77L18.88,4.88L21.71,7.71L9,20.42Z" /></svg>';
          current.classList.add("success");
        } else {
          current.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>close-thick</title><path d="M20 6.91L17.09 4L12 9.09L6.91 4L4 6.91L9.09 12L4 17.09L6.91 20L12 14.91L17.09 20L20 17.09L14.91 12L20 6.91Z" /></svg>';
          current.classList.add("failure");
        }
      }
    }

    /**
     * Check whether the UI is ready and reload if it is.
     */
    async function checkReady() {
      try {
        const response = await window.fetch(window.location.href);
        if (Math.floor(response.status / 100) === 4 || Math.floor(response.status / 100) === 5) {
          setTimeout(checkReady, 5000);
        } else {
          window.location.reload();
        }
      } catch(e) {
        setTimeout(() => {
          window.location.reload();
        }, 5000);
      }
    }
  </script>
</body>
</html>
"""


class IndexRequestHandler(tornado.web.RequestHandler):
    """Handler for any URL to return the HTML."""

    def get(self: "IndexRequestHandler") -> None:
        """Send the HTML template to the user."""
        self.set_header("Content-Type", "text/html")
        self.set_header("Cache-Control", "no-cache, no-store")
        prefix = os.environ["JUPYTERHUB_SERVICE_PREFIX"] if "JUPYTERHUB_SERVICE_PREFIX" in os.environ else "/"
        self.write(HTML_TEMPLATE.replace("{JUPYTERHUB_SERVICE_PREFIX}", prefix))


class ProgressHandler(tornado.websocket.WebSocketHandler):
    """Handler for the progress Websocket."""

    def initialize(self: "ProgressHandler", queue: asyncio.queues.Queue) -> None:
        """Initialise the handler with the queue to use."""
        self._queue = queue

    def open(self: "ProgressHandler"):
        """Open the Websocket connection and start the queue tracking."""
        self._track_progress = asyncio.create_task(self.track_progress())

    async def track_progress(self: "ProgressHandler"):
        """Track the progress queue and send it on to the websocket."""
        while True:
            msg = await self._queue.get()
            self.write_message(msg)


async def main():
    """Run the progress server and the startup scripts."""
    done_event = asyncio.Event()
    queue = asyncio.queues.Queue()

    async def run_startup_scripts():
        """Task to run the individual startup scripts."""
        print("Preparing startup")  # noqa: T201
        await asyncio.sleep(1)
        if os.path.isdir("/usr/share/ou/startup.d"):
            filenames = os.listdir("/usr/share/ou/startup.d")
            filenames.sort()
            print("Preparing startup complete")  # noqa: T201
            for filename in filenames:
                tokens = filename.split("-")
                if len(tokens) > 0:
                    if re.match("^[0-9]+$", tokens[0]):
                        tokens = tokens[1:]
                if len(tokens) > 0:
                    tokens[0] = tokens[0].title()
                    message = " ".join(tokens)
                else:
                    message = "Unknown activity"
                print(message, flush=True)  # noqa: T201
                await queue.put({"type": "start", "text": message})
                process = await subprocess.create_subprocess_exec("bash", f"/usr/share/ou/startup.d/{filename}")
                await process.wait()
                if process.returncode != 0:
                    await queue.put({"type": "done", "status": "failure"})
                else:
                    await queue.put({"type": "done", "status": "success"})
                    print(f"{message} complete", flush=True)  # noqa: T201
                await asyncio.sleep(0.5)
        done_event.set()

    if "OCL_NO_STARTUP_WEB_SERVER" not in os.environ:
      prefix = os.environ["JUPYTERHUB_SERVICE_PREFIX"] if "JUPYTERHUB_SERVICE_PREFIX" in os.environ else "/"
      application = tornado.web.Application(
          [(f"{prefix}ocl-status", ProgressHandler, {"queue": queue}), ("/.*", IndexRequestHandler)],
          websocket_ping_interval=10,
      )
      application.listen(8888)
    asyncio.get_event_loop().create_task(run_startup_scripts())
    await done_event.wait()


if __name__ == "__main__":
    asyncio.run(main())
