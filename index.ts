import { ArkErrors, type } from "arktype";

const concertSchema = type({
  artistName: "string",
  date: "string.date",            // Expect ISO format like "2025-06-01"
  time: "string",                 // Optional time format like "7:30 PM"
  venue: "string",
  city: "string",
  ticketLink: "string",
  priceRange: "string?",
  openingActs: "string[]?",
  description: "string?",
  ageRestriction: "string?",
  imageUrl: "string?"
});

const concertsArraySchema = type({
  concerts: concertSchema.array() 
});

try {
  const res = await fetch("http://localhost:7000");
  if (!res.ok) {
    throw new Error(`HTTP error! status: ${res.status}`);
  }

  const data: unknown = await res.json();

  const result = concertsArraySchema(data);
  if (result instanceof ArkErrors) {
    console.error("Validation failed:", result);
    process.exit(1);
  }

  console.log("✅ Validation passed!");
  console.log(result, null, 2);
} catch (thrown) {
  console.error("❌ Error during test:", thrown);
  process.exit(1);
}
