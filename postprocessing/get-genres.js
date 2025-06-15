const fs = require('fs');

// Read from stdin
let inputData = '';
process.stdin.on('data', chunk => {
  inputData += chunk;
});

process.stdin.on('end', () => {
  const data = JSON.parse(inputData);

const uniqueGenres = new Set();

// Iterate through all months/bundles
for (const [key, value] of Object.entries(data)) {
  if (Array.isArray(value)) {
    value.forEach(game => {
      // Check if it's an object with genres property
      if (typeof game === 'object' && game !== null && game.genres && Array.isArray(game.genres)) {
        game.genres.forEach(genre => {
          if (genre && typeof genre === 'string') {
            uniqueGenres.add(genre);
          }
        });
      }
    });
  }
}

// Convert Set to sorted array
const sortedGenres = Array.from(uniqueGenres).sort();

  console.log(JSON.stringify(sortedGenres, null, 2));
});