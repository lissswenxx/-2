-- ============================================
-- ТРИГГЕР ВЕРСИОНИРОВАНИЯ
-- ============================================

CREATE OR REPLACE FUNCTION publication_version_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.version = OLD.version + 1;
    NEW.is_current = TRUE;
    UPDATE publications SET is_current = FALSE 
    WHERE id = OLD.id AND is_current = TRUE;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_publication_version ON publications;
CREATE TRIGGER trg_publication_version
    BEFORE UPDATE ON publications
    FOR EACH ROW
    EXECUTE FUNCTION publication_version_update();