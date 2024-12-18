CARD_KINDS=(
    'adventurers'
    'monsters'
    'items'
    'moves'
)

WORLD_FILE=$1

# if [ ! -z '$WORLD_FILE' ]; then
#     WORLD_FILE="./resources/worlds/test_world.json"
# fi

WORLD_NAME=$(basename "${WORLD_FILE}")
WORLD_NAME="${WORLD_NAME%.*}"

GENERATED_WORLD=generated/${WORLD_NAME}

mkdir generated -p
mkdir "${GENERATED_WORLD}" -p
mkdir "${GENERATED_WORLD}/sheets" -p

python world/visualizer.py --world "${WORLD_FILE}" --output "${GENERATED_WORLD}"

# don't need this yet
for card_kind in "${CARD_KINDS[@]}"; do
    python -m tts_utils.create_tts_deck \
        --input "${GENERATED_WORLD}/${card_kind}" \
        --output "${GENERATED_WORLD}/sheets" \
        --back "${GENERATED_WORLD}/card_back.png"
    mv "${GENERATED_WORLD}/sheets/deck0.png" "${GENERATED_WORLD}/sheets/${card_kind}.png"
done
