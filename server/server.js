const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { createCanvas } = require("canvas");
const { spawn } = require("child_process");

const ROOT_DIR = process.env.ROOT_DIR || path.resolve(__dirname, "..");

const config = JSON.parse(
  fs.readFileSync(path.join(ROOT_DIR, "config.json"), "utf8")
);

const localConfigPath = path.join(ROOT_DIR, "local.config.json");
if (fs.existsSync(localConfigPath)) {
  Object.assign(
    config,
    JSON.parse(fs.readFileSync(localConfigPath, "utf8"))
  );
}

config.host = process.env.HOST || config.host;
config.port = Number(process.env.PORT || config.port);

for (const [key, value] of Object.entries(config.paths)) {
  config.paths[key] = path.resolve(ROOT_DIR, value);
}

const app = express();
app.use(cors());
app.use(express.json());

const py = spawn(config.conda_model, [config.paths.model_loader],
{ cwd: __dirname });

for (const d of [config.paths.uploads_dir, config.paths.output_dir]) fs.mkdirSync(d, { recursive: true });

// py.stdout.on("data", (d) => console.log("[py]", d.toString()));
// py.stderr.on("data", (d) => console.error("[py err]", d.toString()));

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, config.paths.uploads_dir),
  filename: (req, file, cb) => {
    const safe = path.basename(file.originalname).replace(/[^\w.\-]+/g, '_');
    cb(null, safe);
  },
});
const upload = multer({ storage });

app.use('/', express.static(config.paths.public_dir));
app.use('/files', express.static(config.paths.uploads_dir));
app.use('/output', express.static(config.paths.output_dir, { etag: false, maxAge: 0 }));

app.use('/vendor/pdfjs', express.static(config.paths.pdf_disp_dir, {
  setHeaders: (res, p) => {
    if (p.endsWith('.mjs')) res.setHeader('Content-Type', 'text/javascript');
  },
}));

app.get('/api/files', (req, res) => {
  const files = fs.readdirSync(config.paths.uploads_dir).filter(f => /\.(pdf|html?)$/i.test(f));
  res.json({ files });
});

app.post('/api/upload', upload.array('files'), (req, res) => {
  res.json({ success: true, files: (req.files || []).map(f => f.filename) });
});

app.get('/view', (req, res) => res.sendFile(path.join(config.paths.public_dir, 'viewer.html')));

app.get('/config', (req, res) => res.json({ host: config.host, port: config.port }));

app.post('/generate', async (req, res) => {
  try {
    const text = ((req.body && req.body.text) || '').trim();
    if (!text) {
      return res.status(400).json({ success: false, error: 'No text provided' });
    }

    const url = await generateImage(text);

    res.json({
      success: true,
      imageUrl: `${url}?t=${Date.now()}`
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, error: err.message });
  }
});

app.listen(config.port, config.host, () => {
  console.log(`Server ready at http://${config.host}:${config.port}`);
});