type MessageHandler = (data: any) => void;

export class PortfolioWebSocket {
  private url: string;
  private ws: WebSocket | null = null;
  private listeners: Map<string, Set<MessageHandler>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  private pingInterval: any = null;
  private isExplicitlyClosed = false;

  constructor(portfolioId: string) {
    if (typeof import.meta !== "undefined" && import.meta.env?.VITE_WS_URL) {
      this.url = `${import.meta.env.VITE_WS_URL}/ws/portfolio/${portfolioId}/`;
    } else {
      const proto = typeof window !== "undefined" && window.location?.protocol === "https:" ? "wss:" : "ws:";
      const hostname = typeof window !== "undefined" && window.location?.hostname ? window.location.hostname : "localhost";
      this.url = `${proto}//${hostname}:8000/ws/portfolio/${portfolioId}/`;
    }
  }


  connect() {
    this.isExplicitlyClosed = false;
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this.startHeartbeat();
        this.notifyListeners("status", { connected: true });
      };

      this.ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const eventType = payload.type || "message";
          this.notifyListeners(eventType, payload.data || payload);
        } catch (err) {
          console.error("WS message parse error:", err);
        }
      };

      this.ws.onclose = () => {
        this.stopHeartbeat();
        this.notifyListeners("status", { connected: false });
        if (!this.isExplicitlyClosed) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = () => {
        this.ws?.close();
      };
    } catch (err) {
      console.error("WS connection failure:", err);
      this.scheduleReconnect();
    }
  }

  on(type: string, handler: MessageHandler) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type)!.add(handler);
    return () => {
      this.listeners.get(type)?.delete(handler);
    };
  }

  private notifyListeners(type: string, data: any) {
    this.listeners.get(type)?.forEach((h) => h(data));
  }

  private startHeartbeat() {
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ action: "PING" }));
      }
    }, 30000);
  }

  private stopHeartbeat() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts), 15000);
      setTimeout(() => this.connect(), delay);
    }
  }

  disconnect() {
    this.isExplicitlyClosed = true;
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners.clear();
  }
}
