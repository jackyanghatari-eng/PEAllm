// =============================================================
// STEP 1: REPLACE THIS WITH YOUR PIXABAY API KEY
// =============================================================
const API_KEY = '52411045-912ffdcfe9ef54dd742df832a'; // ← YOUR KEY

// =============================================================
// STEP 2: This script will auto-create folder and download 7 Foley sounds
// =============================================================

const axios = require('axios');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = 'D:\\AI Agency\\Foley-Sounds'; // ← Fixed path for your setup
const LANG = 'th'; // Thai context for search

// Create folder if not exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

const sounds = [
  { query: 'grass rustle close', filename: 'grass-rustle.mp3' },
  { query: 'ceramic cup on wood table', filename: 'cup-table-soft.mp3' },
  { query: 'pen click plastic', filename: 'pen-tap.wav' },
  { query: 'book page turn soft', filename: 'page-turn-soft.mp3' },
  { query: 'wooden chair creak gentle', filename: 'chair-creak.wav' },
  { query: 'light wind through leaves', filename: 'wind-leaves.mp3' },
  { query: 'cafe ambience no music', filename: 'cafe-ambience.mp3' }
];

async function downloadSound(sound) {
  try {
    console.log(`\n🔍 Searching: "${sound.query}"`);

    // ✅ FIXED: NO TRAILING SPACES + AUDIO ENDPOINT
    const res = await axios.get('https://pixabay.com/api/audio/', {
      params: {
        key: API_KEY,
        q: encodeURIComponent(sound.query),
        lang: LANG,
        per_page: 1
      }
    });

    if (!res.data.hits || res.data.hits.length === 0) {
      console.log(`❌ No result found for: ${sound.query}`);
      return;
    }

    const audioUrl = res.data.hits[0].full_audio_url;
    const outputPath = path.join(OUTPUT_DIR, sound.filename);

    console.log(`⬇️ Downloading → ${sound.filename}`);
    const writer = fs.createWriteStream(outputPath);
    const audioRes = await axios({
      url: audioUrl,
      method: 'GET',
      responseType: 'stream'
    });

    audioRes.data.pipe(writer);

    await new Promise((resolve, reject) => {
      writer.on('finish', resolve);
      writer.on('error', reject);
    });

    console.log(`✅ Saved: ${sound.filename}`);
  } catch (err) {
    console.error(`❌ Error with ${sound.filename}:`, err.message);
  }
}

(async () => {
  console.log('🎬 Starting Auto Foley Sound Downloader...');
  for (let sound of sounds) {
    await downloadSound(sound);
  }
  console.log(`\n🎉 All sounds saved to: ${OUTPUT_DIR}`);
})();