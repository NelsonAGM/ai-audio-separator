import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./routes.js";
import { log } from "./vite.js";

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }

      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "…";
      }

      log(logLine);
    }
  });

  next();
});

(async () => {
  try {
    const server = await registerRoutes(app);

    app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
      const status = err.status || err.statusCode || 500;
      const message = err.message || "Internal Server Error";

      res.status(status).json({ message });
      throw err;
    });

    // Importar dinámicamente setupVite y serveStatic desde vite.js
    if (app.get("env") === "development") {
      const viteModule = await import("./vite.js");
      await viteModule.setupVite(app, server);
    } else {
      const viteModule = await import("./vite.js");
      viteModule.serveStatic(app);
    }

    // ALWAYS serve the app on the port asignado por Railway o 5000 por defecto
    const port = process.env.PORT ? Number(process.env.PORT) : 5000;
    server.listen({
      port,
      host: "0.0.0.0"
      // reusePort: true, // Eliminado para compatibilidad con Windows
    }, () => {
      log(`serving on port ${port}`);
    });
  } catch (err) {
    console.error("Error global al arrancar el backend:", err);
    process.exit(1);
  }
})();
