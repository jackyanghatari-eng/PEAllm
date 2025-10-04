// =============================================================
// AI SHORT FILM AGENCY — FOLEY SOUND DOWNLOADER (FREESOUND.ORG)
// =============================================================
// STEP 1: REPLACE 'YOUR_FREESOUND_API_KEY' WITH YOUR REAL KEY
// Get key at: https://freesound.org/apiv2/apply/
// =============================================================

const axios = require('axios');
const fs = require('fs');
const path = require('path');

// 🔑 YOUR FREESOUND API KEY — PASTE IT HERE
const API_KEY = 'JK8ZsODwX3UO1QoFaIaaxakk4Giznl06ytfi7ZBs';

// 📁 OUTPUT FOLDER — WILL AUTO-CREATE IF NOT EXISTS
const OUTPUT_DIR = 'D:\\AI Agency\\Foley-Sounds';

// 🌐 SEARCH LANGUAGE — THAI CONTEXT
const LANG = 'th';

// 📂 CREATE FOLDER IF NOT EXISTS
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// 🎧 SOUND SEARCH LIST — QUERY + FILENAME
const sounds = [
  { query: 'grass rustle', filename: 'grass-rustle.mp3' },
  { query: 'cup on table', filename: 'cup-table-soft.mp3' },
  { query: 'pen click', filename: 'pen-tap.wav' },
  { query: 'page turn', filename: 'page-turn-soft.mp3' },
  { query: 'chair creak', filename: 'chair-creak.wav' },
  { query: 'wind leaves', filename: 'wind-leaves.mp3' },
  { query: 'cafe background', filename: 'cafe-ambience.mp3' }
];

// 🔄 DOWNLOAD FUNCTION — SEARCH + FETCH + SAVE
// 🔍 SEARCH FREESOUND HELPER
async function searchFreesound(query) {
  return await axios.get('https://freesound.org/apiv2/search/text/', {
    params: {
      query: query,
      token: API_KEY,
      license: 'cc0',
      fields: 'id,name,previews,license',
      page_size: 1
    }
  });
}

// ♻️ FALLBACK QUERY MAPPER
function getFallbackQuery(primary) {
  const fallbacks = {
    'cup on table': 'mug on wood',
    'cafe background': 'restaurant ambience',
    'grass rustle': 'leaves rustle',
    'pen click': 'click pen',
    'page turn': 'book flip',
    'chair creak': 'wood creak',
    'wind leaves': 'breeze leaves'
  };
  return fallbacks[primary] || primary;
}

// 🔄 ENHANCED DOWNLOAD WITH FALLBACK
async function downloadSound(sound) {
  try {
    // Try primary query first
    let res = await searchFreesound(sound.query);
    
    // If no result, try fallback query
    if (!res.data.results || res.data.results.length === 0) {
      const fallbackQuery = getFallbackQuery(sound.query);
      console.log(`🔄 No result for "${sound.query}" → trying fallback: "${fallbackQuery}"`);
      res = await searchFreesound(fallbackQuery);
    }

    if (!res.data.results || res.data.results.length === 0) {
      console.log(`❌ No CC0 sound found for: ${sound.query}`);
      return;
    }

    const firstHit = res.data.results[0];
    const audioUrl = firstHit.previews['preview-lq-mp3'];
    const outputPath = path.join(OUTPUT_DIR, sound.filename);

    console.log(`⬇️ Downloading: ${firstHit.name} → ${sound.filename}`);
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
    console.error(`❌ Error downloading ${sound.filename}:`, err.message);
    if (err.response && err.response.status === 401) {
      console.error('🔑 Your API key may be invalid or not activated.');
    }
  }
}
// ▶️ MAIN EXECUTION
(async () => {
  console.log('🎬 Starting Freesound Foley Sound Downloader...');
  console.log('🌐 All sounds are CC0 — no attribution required.');

  for (let sound of sounds) {
    await downloadSound(sound);
  }

  console.log(`\n🎉 DONE! All sounds saved to: ${OUTPUT_DIR}`);
})();