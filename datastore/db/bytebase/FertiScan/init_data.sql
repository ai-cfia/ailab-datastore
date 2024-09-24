DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM "fertiscan_0.0.6".sub_label WHERE type_fr = 'Instruction' AND type_en = 'Instruction') THEN
        INSERT INTO "fertiscan_0.0.6".sub_label(type_fr,type_en) VALUES
        ('Instruction','Instruction'),
        ('Mise en garde','Caution'),
        ('Premier soin','First aid'),
        ('Garantie','Warranty');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM "fertiscan_0.0.7".sub_type WHERE type_fr = 'Instruction' AND type_en = 'Instruction') THEN
        INSERT INTO "fertiscan_0.0.7".sub_type(type_fr,type_en) VALUES
        ('Instruction','Instruction'),
        ('Mise en garde','Caution'),
        ('Premier soin','First aid'),
        ('Garantie','Warranty');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM "fertiscan_0.0.9".sub_type WHERE type_fr = 'Instruction' AND type_en = 'Instruction') THEN
        INSERT INTO "fertiscan_0.0.9".sub_type(type_fr,type_en) VALUES
        ('Instruction','Instruction'),
        ('Mise en garde','Caution'),
        ('Premier soin','First aid'),
        ('Garantie','Warranty');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM "fertiscan_0.0.10".sub_type WHERE type_fr = 'Instruction' AND type_en = 'Instruction') THEN
        INSERT INTO "fertiscan_0.0.10".sub_type(type_fr,type_en) VALUES
        ('Instruction','Instruction'),
        ('Mise en garde','Caution'),
        ('Premier soin','First aid'),
        ('Garantie','Warranty');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM "fertiscan_0.0.11".sub_type WHERE type_fr = 'instructions' AND type_en = 'instructions') THEN
        INSERT INTO "fertiscan_0.0.11".sub_type(type_fr,type_en) VALUES
        ('instructions','instructions'),
        ('mises_en_garde','cautions'),
        ('premier_soin','first_aid'),
        ('garanties','warranties');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM "fertiscan_0.0.12".sub_type WHERE type_fr = 'instructions' AND type_en = 'instructions') THEN
        INSERT INTO "fertiscan_0.0.12".sub_type(type_fr,type_en) VALUES
        ('instructions','instructions'),
        ('mises_en_garde','cautions'),
        ('premier_soin','first_aid'),
        ('garanties','warranties');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM "fertiscan_0.0.14".sub_type WHERE type_fr = 'instructions' AND type_en = 'instructions') THEN
        INSERT INTO "fertiscan_0.0.14".sub_type(type_fr,type_en) VALUES
        ('instructions','instructions'),
        ('mises_en_garde','cautions'),
        ('premier_soin','first_aid'),
        ('garanties','warranties');
    END IF;
END $$;
