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

config.host = process.env.HOST || config.host;
config.port = Number(process.env.PORT || config.port);

for (const [key, value] of Object.entries(config.paths)) {
  config.paths[key] = path.resolve(ROOT_DIR, value);
}