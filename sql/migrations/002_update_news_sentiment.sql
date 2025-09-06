-- Update news_sentiment table schema
ALTER TABLE news_sentiment 
  DROP COLUMN sentiment_magnitude,
  ADD COLUMN IF NOT EXISTS sentiment_label VARCHAR(20),
  ADD COLUMN IF NOT EXISTS url TEXT NOT NULL UNIQUE DEFAULT '',
  ADD COLUMN IF NOT EXISTS source VARCHAR(255) NOT NULL DEFAULT '';

-- Remove the default constraint after adding the columns
ALTER TABLE news_sentiment 
  ALTER COLUMN url DROP DEFAULT,
  ALTER COLUMN source DROP DEFAULT;
