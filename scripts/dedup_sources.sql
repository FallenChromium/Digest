BEGIN;

-- Create a temporary table to store the source mappings (old ID -> new ID)
CREATE TEMP TABLE source_mapping AS
WITH ranked_sources AS (
    SELECT
        id,
        name,
        config,
        FIRST_VALUE(id) OVER (
            PARTITION BY name, config::text
            ORDER BY id ASC
        ) as canonical_id,
        ROW_NUMBER() OVER (
            PARTITION BY name, config::text
            ORDER BY id ASC
        ) as rn
    FROM source
)
SELECT
    id as old_id,
    canonical_id as new_id
FROM ranked_sources
WHERE rn > 1;

-- Update content_pieces to point to the surviving source
-- Do this BEFORE deleting any sources to maintain referential integrity
UPDATE content_piece
SET source_id = m.new_id
FROM source_mapping m
WHERE content_piece.source_id = m.old_id;

-- Delete duplicate sources AFTER updating content_pieces
DELETE FROM source s
USING source_mapping m
WHERE s.id = m.old_id;

DROP TABLE source_mapping;

COMMIT;
