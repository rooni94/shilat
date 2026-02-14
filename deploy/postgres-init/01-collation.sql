DO $$
BEGIN
  CREATE COLLATION IF NOT EXISTS "ar-SA-x-icu" (provider = icu, locale = 'ar-SA');
EXCEPTION WHEN others THEN
  NULL;
END $$;
