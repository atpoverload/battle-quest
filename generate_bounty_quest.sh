WORLD=bounty_quest

mkdir -p generated
OUTPUT_DIR="generated/${WORLD}"

rm -rf "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}"

SCRATCH_DIR="${OUTPUT_DIR}/scratch"
mkdir -p "${SCRATCH_DIR}"

# generate and randomize the world
python3 world/generator.py \
    --world "resources/templates/${WORLD}_template.yaml" \
    --output "${SCRATCH_DIR}/generated_world.yaml"
python3 world/randomizer.py \
    --world "${SCRATCH_DIR}/generated_world.yaml" \
    --output "${SCRATCH_DIR}/randomized_world.yaml"

# generate the sprites
mkdir -p "${SCRATCH_DIR}/sprites"
mkdir -p "${SCRATCH_DIR}/sprites"
python3 visualizer/sprite_generator.py \
    --world "${SCRATCH_DIR}/randomized_world.yaml" \
    --output "${SCRATCH_DIR}/sprites"
cp ./resources/sprites/${WORLD}/* "${SCRATCH_DIR}/sprites/."

# create the cards
CARD_DIR=${OUTPUT_DIR}/tts_card
mkdir -p "${CARD_DIR}"
mkdir -p "${CARD_DIR}/cards"
python draw_world_cards.py \
    --world "${SCRATCH_DIR}/randomized_world.yaml" \
    --resources "${SCRATCH_DIR}/sprites" \
    --output "${CARD_DIR}/cards"

# make sheets for the different types of cards for convenience
mkdir -p "${CARD_DIR}/sheets"
mv "${CARD_DIR}/cards/cardback.png" "${CARD_DIR}/sheets/cardback.png"

for cards in ${CARD_DIR}/cards/**; do
    card_kind=$(basename ${cards})
    python -m tts_utils.create_tts_deck \
        --input "${cards}" \
        --output "${CARD_DIR}/sheets" \
        --back "${CARD_DIR}/sheets/cardback.png"
    for deck in ${CARD_DIR}/sheets/deck*.png; do
        deck_name=$(basename ${deck})
        mv "${deck}" "${CARD_DIR}/sheets/${card_kind}_${deck_name}"
    done
done
