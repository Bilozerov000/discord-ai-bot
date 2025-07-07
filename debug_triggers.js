#!/usr/bin/env node
/**
 * Debug script to test trigger word matching
 */

require('dotenv').config();

const botnames = process.env.BOT_TRIGGERS.split(',');
const testTranscription = "Голова, как дела?";

console.log('🔍 Debugging trigger word matching...');
console.log('');
console.log('Environment BOT_TRIGGERS:', process.env.BOT_TRIGGERS);
console.log('Parsed botnames array:', botnames);
console.log('Test transcription:', testTranscription);
console.log('');

// Test each trigger word
for (const name of botnames) {
    console.log(`Testing trigger: "${name}"`);
    
    // Original regex from bot.js
    const regex = new RegExp(`\\b${name}\\b`, 'i');
    const matches = regex.test(testTranscription);
    
    console.log(`  Regex: ${regex}`);
    console.log(`  Matches: ${matches}`);
    
    // Test case-insensitive simple includes
    const simpleMatch = testTranscription.toLowerCase().includes(name.toLowerCase());
    console.log(`  Simple includes: ${simpleMatch}`);
    
    // Test with trim
    const trimmedName = name.trim();
    const trimmedRegex = new RegExp(`\\b${trimmedName}\\b`, 'i');
    const trimmedMatches = trimmedRegex.test(testTranscription);
    console.log(`  Trimmed name: "${trimmedName}"`);
    console.log(`  Trimmed regex matches: ${trimmedMatches}`);
    
    console.log('');
}

// Test the overall condition from bot.js
const overallMatch = botnames.some(name => {
    const regex = new RegExp(`\\b${name}\\b`, 'i');
    return regex.test(testTranscription);
});

console.log('Overall match result:', overallMatch);

// Additional debug info
console.log('');
console.log('Character codes for first trigger:');
if (botnames[0]) {
    for (let i = 0; i < botnames[0].length; i++) {
        console.log(`  "${botnames[0][i]}" = ${botnames[0].charCodeAt(i)}`);
    }
}

console.log('');
console.log('Character codes for "Голова" in transcription:');
const transcriptionWord = "Голова";
for (let i = 0; i < transcriptionWord.length; i++) {
    console.log(`  "${transcriptionWord[i]}" = ${transcriptionWord.charCodeAt(i)}`);
}
