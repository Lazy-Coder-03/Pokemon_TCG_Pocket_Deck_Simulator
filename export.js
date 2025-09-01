const fs = require("fs");
const path = require("path");
const TCGdex = require("@tcgdex/sdk").default;
const { createObjectCsvWriter } = require("csv-writer");

const tcgdex = new TCGdex("en");
const saveDir = "data";

// list of sets to export
const sets = [
    "A1",   // Genetic Apex (Oct 30, 2024)
    "A1a",
    "A2",
    "A2a",
    "A2b",
    "A3",
    "A3a",
    "A3b",
    "A4",
    "A4a",
    "P-A"
];

    // "A1a",
    // "A2",   // Cosmic Eclipse (Nov 15, 2024)
    // "A2a",
    // "A2b",
    // "A3",
    // "A3a",
    // "A3b",
    // "A4",
    // "A4a",
    // "A4b",
    // "P-A"
    // add other sets here


(async () => {
    try {
        if (!fs.existsSync(saveDir)) fs.mkdirSync(saveDir, { recursive: true });

        for (const setId of sets) {
            const set = await tcgdex.set.get(setId);
            console.log(`📦 Processing set: ${set.name} (${set.id})`);

            // fetch full card objects individually to ensure evolveFrom is present
            const fullCards = await Promise.all(
                set.cards.map(cardResume => tcgdex.card.get(cardResume.id))
            );

            // set-level boosters for fallback
            const setBoosterNames = set.boosters?.map(b => b.name).join(", ") || set.name;

            const csvWriter = createObjectCsvWriter({
                path: path.join(saveDir, `${setId}-${set.name.replace(/[\/\\?%*:|"<> ]/g, "-")}.csv`),
                header: [
                    { id: "set_name", title: "set_name" },
                    { id: "set_code", title: "set_code" },
                    { id: "set_release_date", title: "set_release_date" },
                    { id: "set_total_cards", title: "set_total_cards" },
                    { id: "pack_name", title: "pack_name" },
                    { id: "card_name", title: "card_name" },
                    { id: "card_number", title: "card_number" },
                    { id: "card_rarity", title: "card_rarity" },
                    { id: "card_type", title: "card_type" },
                    { id: "pokemon_stage", title: "pokemon_stage" },
                    { id: "evolves_from", title: "evolves_from" },
                    { id: "ex", title: "ex" }
                ]
            });

            const records = fullCards.map(card => {
                const rarity = typeof card.rarity === "object" ? card.rarity.name : card.rarity || "N/A";
                const stage = typeof card.stage === "object" ? card.stage.name : card.stage || "N/A";
                const types = (card.types || []).join(", ") || (card.category || "N/A");

                const packName = (card.boosters && card.boosters.length > 0)
                    ? card.boosters.map(b => b.name).join(", ")
                    : setBoosterNames;

                const isEx = (
                    (card.name && /(^|\s)ex(\b|$)/i.test(card.name)) ||
                    (Array.isArray(card.subtypes) && card.subtypes.includes("EX")) ||
                    (card.suffixe && String(card.suffixe).toLowerCase() === "ex")
                );

                return {
                    set_name: set.name,
                    set_code: set.id,
                    set_release_date: set.releaseDate || "N/A",
                    set_total_cards: set.cardCount?.official || set.cardCount?.total || "N/A",
                    pack_name: packName,
                    card_name: card.name,
                    card_number: card.localId || card.id,
                    card_rarity: rarity,
                    card_type: types,
                    pokemon_stage: stage,
                    evolves_from: card.evolveFrom ?? "N/A",  // fixed casing & safe fallback
                    ex: isEx ? "Yes" : "No"
                };
            });

            await csvWriter.writeRecords(records);
            console.log(`✅ Exported ${records.length} cards → ${path.join(saveDir, `${set.name.replace(/[\/\\?%*:|"<> ]/g, "-")}.csv`)}`);
        }

    } catch (err) {
        console.error("❌ Error exporting:", err);
    }
})();
