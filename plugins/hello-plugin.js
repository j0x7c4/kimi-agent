// Example UI plugin — serves as a smoke test for local plugin loading.
export default {
  id: "local:hello",
  name: "Hello Plugin",
  description: "A minimal test plugin that shows a greeting when thinking starts.",
  version: "0.1.0",
  author: "local",
  events: ["thinking:start", "thinking:end"],
  overlayConfig: { position: "top-right", zIndex: 9500 },
  render({ event, dismiss }) {
    if (event.type === "thinking:start") {
      const el = document.createElement("div");
      el.textContent = "Thinking...";
      Object.assign(el.style, {
        background: "#1e40af",
        color: "white",
        padding: "8px 16px",
        borderRadius: "9999px",
        fontSize: "13px",
        fontWeight: "500",
        boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
      });
      return el;
    }
    if (event.type === "thinking:end") {
      dismiss();
    }
    return null;
  },
};
