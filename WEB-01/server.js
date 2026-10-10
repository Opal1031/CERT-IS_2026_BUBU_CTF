const http = require('node:http');
const { readFile } = require('node:fs/promises');
const path = require('node:path');

const flag = process.env.FLAG;
if (!flag || !/^BUBU\{[^{}\r\n]+\}$/.test(flag)) {
  process.stderr.write('FLAG must be set to a value in BUBU{...} format.\n');
  process.exit(1);
}

const port = Number(process.env.PORT || '3000');
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  process.stderr.write('PORT must be an integer from 1 to 65535.\n');
  process.exit(1);
}

const bodyLimit = 4096;

function respond(res, status, contentType, body) {
  res.writeHead(status, {
    'Content-Type': contentType,
    'Cache-Control': 'no-store',
    Pragma: 'no-cache',
    'X-Content-Type-Options': 'nosniff',
  });
  res.end(body);
}

function json(res, status, value) {
  respond(res, status, 'application/json; charset=utf-8', JSON.stringify(value));
}

function readRequestBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let length = 0;
    let settled = false;

    req.on('data', (chunk) => {
      if (settled) return;
      length += chunk.length;
      if (length > bodyLimit) {
        settled = true;
        reject({ status: 413, message: 'Request body is too large.' });
        req.resume();
        return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => {
      if (!settled) resolve(Buffer.concat(chunks).toString('utf8'));
    });
    req.on('error', (error) => {
      if (!settled) reject(error);
    });
    req.on('aborted', () => {
      if (!settled) reject(new Error('Request aborted.'));
    });
  });
}

async function serveFile(res, filename, contentType) {
  try {
    const contents = await readFile(path.join(__dirname, filename));
    respond(res, 200, contentType, contents);
  } catch (error) {
    process.stderr.write(`Failed to read ${filename}: ${error.message}\n`);
    json(res, 500, { error: 'Internal server error.' });
  }
}

async function handleRequest(req, res) {
  try {
    const pathname = new URL(req.url, 'http://localhost').pathname;

    if (req.method === 'GET' && pathname === '/') {
      await serveFile(res, 'index.html', 'text/html; charset=utf-8');
      return;
    }
    if (req.method === 'GET' && pathname === '/flag.txt') {
      await serveFile(res, 'flag.txt', 'text/plain; charset=utf-8');
      return;
    }
    if (req.method === 'GET' && pathname === '/healthz') {
      respond(res, 200, 'text/plain; charset=utf-8', 'ok');
      return;
    }
    if (req.method === 'POST' && pathname === '/api/staff-notice') {
      if (!/^application\/json(?:\s*;|\s*$)/i.test(req.headers['content-type'] || '')) {
        json(res, 415, { error: 'Expected JSON.' });
        return;
      }

      const rawBody = await readRequestBody(req);
      let body;
      try {
        body = JSON.parse(rawBody);
      } catch {
        json(res, 400, { error: 'Invalid JSON.' });
        return;
      }

      if (body && typeof body === 'object' && !Array.isArray(body) && body.role === 'admin') {
        json(res, 200, { flag });
      } else {
        json(res, 403, { error: 'Staff access required.' });
      }
      return;
    }

    json(res, 404, { error: 'Not found.' });
  } catch (error) {
    if (res.headersSent || res.destroyed) return;
    if (error && error.status === 413) {
      json(res, 413, { error: error.message });
      return;
    }
    process.stderr.write(`Request failed: ${error.message}\n`);
    json(res, 500, { error: 'Internal server error.' });
  }
}

const server = http.createServer(handleRequest);
server.requestTimeout = 10000;
if (require.main === module) {
  server.listen(port, '0.0.0.0');
}

module.exports = { handleRequest };
