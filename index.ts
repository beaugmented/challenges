import { ArkErrors, type } from "arktype";

const concertSchema = type({
  artistName: "string",
  date: "string.date?",           // Optional ISO format like "2025-06-01"
  time: "string?",                // Optional time format like "7:30 PM"
  venue: "string?",
  city: "string?",
  ticketLink: "string?",
  priceRange: "string?",
  openingActs: "string[]?",
  description: "string?",
  ageRestriction: "string?",
  imageUrl: "string?"
});

const concertsArraySchema = type({
  concerts: concertSchema.array() 
});

async function fetchConcertData() {
  try {
    const res = await fetch("http://0.0.0.0:8000/monqui/events?headless=true");
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data: unknown = await res.json();

    const result = concertsArraySchema(data);
    if (result instanceof ArkErrors) {
      console.error("Validation failed:", result);
      return null;
    }

    console.log("✅ Validation passed!");
    return result;
  } catch (thrown) {
    console.error("❌ Error during API fetch:", thrown);
    return null;
  }
}

// Execute the fetch
fetchConcertData().then(data => {
  if (data) {
    console.log(JSON.stringify(data, null, 2));
  } else {
    process.exit(1);
  }
});
