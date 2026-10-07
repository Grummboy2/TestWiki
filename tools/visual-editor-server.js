"use strict";

const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const host = "127.0.0.1";
const port = Number(process.env.DM2_EDITOR_PORT || 8765);
const contentTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".txt": "text/plain; charset=utf-8"
};

const rootPages = new Set([
  "404.html", "PAGE-TEMPLATE.html", "breeding.html", "changelog.html", "dragons.html",
  "faq.html", "flight.html", "index.html", "install.html", "items.html", "wiki-editor.html"
]);

function allowedFile(relativePath) {
  if (typeof relativePath !== "string") return false;
  const normalizedPath = relativePath.replace(/\\/g, "/");
  const parts = normalizedPath.split("/");
  if (normalizedPath.startsWith("/") || /^[a-z]:/i.test(normalizedPath) ||
      parts.some((part) => !part || part === "." || part === "..")) return false;

  if (normalizedPath === "assets/config.js" || normalizedPath === "assets/data.js") return true;
  if (parts[0] === "assets" || parts[0] === "textures") {
    return parts.every((part) => !part.startsWith("."));
  }

  return parts.length === 1 &&
    (rootPages.has(parts[0]) || /^[a-z0-9][a-z0-9-]*\.html$/i.test(parts[0]));
}

function writeFile(relativePath, contents, createOnly) {
  return new Promise((resolve, reject) => {
    const destination = path.resolve(root, relativePath);
    if (!destination.startsWith(root + path.sep)) {
      reject(Object.assign(new Error("Invalid file path"), { statusCode: 400 }));
      return;
    }

    fs.access(destination, fs.constants.F_OK, (accessError) => {
      if (!accessError && createOnly) {
        reject(Object.assign(new Error("A page with this filename already exists"), { statusCode: 409 }));
        return;
      }
      if (accessError && accessError.code !== "ENOENT") {
        reject(accessError);
        return;
      }

      const temporary = path.join(path.dirname(destination), `.dm2-editor-${process.pid}-${Date.now()}-${Math.random().toString(16).slice(2)}.tmp`);
      fs.writeFile(temporary, contents, { encoding: "utf8", flag: "wx" }, (writeError) => {
        if (writeError) {
          reject(writeError);
          return;
        }
        fs.rename(temporary, destination, (renameError) => {
          if (renameError) {
            fs.unlink(temporary, () => reject(renameError));
            return;
          }
          resolve();
        });
      });
    });
  });
}

function sendJson(response, statusCode, payload) {
  const contents = Buffer.from(JSON.stringify(payload));
  response.writeHead(statusCode, {
    "Cache-Control": "no-store",
    "Content-Length": contents.length,
    "Content-Type": "application/json; charset=utf-8",
    "X-Content-Type-Options": "nosniff"
  });
  response.end(contents);
}

const server = http.createServer((request, response) => {
  if (request.headers.host !== `${host}:${port}`) {
    response.writeHead(403).end("This local editor accepts requests only from 127.0.0.1");
    return;
  }

  let pathname;
  try {
    pathname = decodeURIComponent(new URL(request.url, `http://${host}:${port}`).pathname);
  } catch {
    response.writeHead(400).end("Invalid URL");
    return;
  }

  if (pathname === "/__editor/status") {
    if (request.method !== "GET") {
      response.writeHead(405, { Allow: "GET" }).end("Method not allowed");
      return;
    }
    sendJson(response, 200, { ready: true, project: "TestWiki" });
    return;
  }

  if (pathname === "/__editor/save") {
    if (request.method !== "POST") {
      response.writeHead(405, { Allow: "POST" }).end("Method not allowed");
      return;
    }
    if (request.headers.origin !== `http://${host}:${port}` ||
        request.headers["content-type"] !== "application/json") {
      response.writeHead(403).end("Editor writes are allowed only from this local Wiki editor");
      return;
    }

    let size = 0;
    const chunks = [];
    request.on("data", (chunk) => {
      size += chunk.length;
      if (size > 5 * 1024 * 1024) {
        response.writeHead(413).end("Editor save is too large");
        request.destroy();
        return;
      }
      chunks.push(chunk);
    });
    request.on("end", async () => {
      if (response.writableEnded) return;
      try {
        const payload = JSON.parse(Buffer.concat(chunks).toString("utf8"));
        if (!Array.isArray(payload.files) || payload.files.length < 1 || payload.files.length > 2) {
          sendJson(response, 400, { error: "Save one page and its search index, or save the Wiki settings." });
          return;
        }

        let totalBytes = 0;
        for (const file of payload.files) {
          if (!file || typeof file.path !== "string" || typeof file.contents !== "string" ||
              !allowedFile(file.path) || typeof file.createOnly !== "undefined" && typeof file.createOnly !== "boolean") {
            sendJson(response, 400, { error: "The requested save contains an unsupported file." });
            return;
          }
          totalBytes += Buffer.byteLength(file.contents, "utf8");
        }
        if (totalBytes > 4 * 1024 * 1024) {
          sendJson(response, 413, { error: "Editor save is too large" });
          return;
        }

        for (const file of payload.files) {
          await writeFile(file.path, file.contents, file.createOnly === true);
        }
        sendJson(response, 200, { saved: payload.files.map((file) => file.path) });
      } catch (error) {
        if (error instanceof SyntaxError) {
          sendJson(response, 400, { error: "Invalid JSON in editor save" });
          return;
        }
        sendJson(response, error.statusCode || 500, { error: error.statusCode ? error.message : "Unable to save Wiki files" });
      }
    });
    request.on("error", () => {
      if (!response.writableEnded) sendJson(response, 400, { error: "Editor save request failed" });
    });
    return;
  }

  if (request.method !== "GET" && request.method !== "HEAD") {
    response.writeHead(405, { Allow: "GET, HEAD" }).end("Method not allowed");
    return;
  }

  if (pathname === "/") pathname = "/index.html";
  else if (pathname.endsWith("/")) pathname += "index.html";

  const filePath = path.resolve(root, `.${pathname}`);
  if (!filePath.startsWith(root + path.sep)) {
    response.writeHead(403).end("Forbidden");
    return;
  }

  const relativePath = path.relative(root, filePath).split(path.sep);
  if (!allowedFile(relativePath.join(path.sep)) &&
      relativePath.join("/") !== "tools/visual-editor/index.html") {
    response.writeHead(404).end("Not found");
    return;
  }

  fs.readFile(filePath, (error, contents) => {
    if (error) {
      response.writeHead(error.code === "ENOENT" ? 404 : 500).end("Unable to read this site file");
      return;
    }

    response.writeHead(200, {
      "Cache-Control": "no-store",
      "Content-Length": contents.length,
      "Content-Type": contentTypes[path.extname(filePath).toLowerCase()] || "application/octet-stream",
      "X-Content-Type-Options": "nosniff"
    });
    response.end(request.method === "HEAD" ? undefined : contents);
  });
});

server.on("error", (error) => {
  console.error(`Unable to start the local Wiki editor server: ${error.message}`);
  process.exitCode = 1;
});

server.listen(port, host, () => {
  const url = `http://${host}:${port}/tools/visual-editor/`;
  console.log(`Local Wiki editor: ${url}`);
  console.log("This server listens only on this computer. Press Ctrl+C to stop it.");

  if (process.argv.includes("--no-browser")) return;

  const { execFile } = require("node:child_process");
  execFile("cmd.exe", ["/c", "start", "", url], (error) => {
    if (error) console.log(`Open this address in your browser: ${url}`);
  });
});
