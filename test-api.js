require("dotenv").config();
const axios = require("axios");

async function testOpenAIAuth() {
  try {
    console.log(
      `Testing API key: ${
        process.env.LLM_API ? process.env.LLM_API : "UNDEFINED"
      }...`
    );

    const response = await axios.get("https://api.openai.com/v1/models", {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.LLM_API}`,
      },
    });

    console.log("✅ API key is valid");
    console.log(`Found ${response.data.data.length} models`);
  } catch (error) {
    console.error("❌ API key test failed:", error.message);
    if (error.response) {
      console.error("Status:", error.response.status);
      console.error("Data:", error.response.data);
    }
  }
}

testOpenAIAuth();
