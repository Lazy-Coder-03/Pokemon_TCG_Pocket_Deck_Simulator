const TCGdex = require('@tcgdex/sdk').default;
const tcgdex = new TCGdex('en');

(async () => {
    const card = await tcgdex.card.get('A1-002');

    // get set info separately (to access release_date etc.)
    const setInfo = await tcgdex.set.get(card.set.id);

    // const row = {
    //     set_name: setInfo.name,
    //     set_code: setInfo.id,
    //     set_release_date: setInfo.releaseDate || null,
    //     set_total_cards: setInfo.cardCount?.official || null,
    //     pack_name: card.boosters?.map(b => b.name).join(', ') || null,
    //     card_name: card.name,
    //     card_number: card.localId,
    //     card_rarity: card.rarity,
    //     card_type: card.category,
    //     pokemon_stage: card.stage || null,
    //     ex: card.suffixe === 'EX' || card.name.includes('EX') ? true : false,
    // };


    console.log(card)
})();
