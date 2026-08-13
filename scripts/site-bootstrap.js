(() => {
  const NativeWorker = window.Worker;
  if (!NativeWorker) {
    return;
  }

  function handleWorkerMessage(event) {
    const rpcMessage = event.data?.data ?? event.data;
    if (rpcMessage?.id !== "kernelMessage") {
      return;
    }

    let kernelMessage = rpcMessage.payload?.message;
    if (typeof kernelMessage === "string") {
      try {
        kernelMessage = JSON.parse(kernelMessage);
      } catch {
        return;
      }
    }

    if (kernelMessage?.op !== "completed-run") {
      return;
    }

    window.__noteRuntimeReady = true;
    window.dispatchEvent(new CustomEvent("note:runtime-ready"));
  }

  window.Worker = class NoteWorker extends NativeWorker {
    constructor(...args) {
      super(...args);
      this.addEventListener("message", handleWorkerMessage);
    }
  };
})();
