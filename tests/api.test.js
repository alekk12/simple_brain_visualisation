import { describe, it, expect } from 'vitest';
//node --experimental-vm-modules node_modules/.bin/jest test/api.test.js
import request from 'supertest';
import app from '../server/server.js';

describe('GET /api/files', () => {
  it('returns a list of files as a json', async () => {
    const res = await request(app).get('/api/files');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body.files)).toBe(true);
  });
});

describe('POST /generate', () => {
  it('blank selection is bad', async () => {
    const res = await request(app).post('/generate').send({ text: '   ' });
    expect(res.body.success).toBe(false);
  });

  it('good selection', async () => {
    const res = await request(app).post('/generate').send({ text: 'a glowing tree at dusk' });
    console.log(res)
    expect(res.body.success).toBe(true);
    expect(typeof res.body.imageUrl).toBe('string');
  });
});

describe('static pages', () => {
  it('show index page', async () => {
    const res = await request(app).get('/');
    expect(res.status).toBe(200);
    expect(res.text).toContain('visualiser');
  });

  it('serves the viewer for /view', async () => {
    const res = await request(app).get('/view?file=x.pdf');
    expect(res.status).toBe(200);
    expect(res.text).toContain('id="stage"');
  });
});