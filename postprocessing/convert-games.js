const fs = require('fs');

// Read the games.json file
const data = JSON.parse(fs.readFileSync('games.json', 'utf8'));

// Convert the data
const convertedData = {};

for (const [key, value] of Object.entries(data)) {
  if (Array.isArray(value)) {
    // Check if it's the first type (objects with name, genres, etc.)
    if (value.length > 0 && typeof value[0] === 'object' && value[0] !== null) {
      // Already in the preferred format
      convertedData[key] = value;
    } else {
      // Convert from second type (array of strings) to first type
      convertedData[key] = value.map(name => ({
        name: name,
        genres: [],
        image: null,
        link: null,
        instructions: null
      }));
    }
  } else {
    // Keep non-array values as is
    convertedData[key] = value;
  }
}

// Write the converted data back to a new file
fs.writeFileSync('games-converted.json', JSON.stringify(convertedData, null, 2));

console.log('Conversion complete. Output saved to games-converted.json');