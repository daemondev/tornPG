--psql -U termux -d termux -a -f db2.sql
--[\i | -i | -c | @db2.sql] db2.sql
CREATE OR REPLACE FUNCTION notify_trigger() RETURNS trigger AS $$
	DECLARE
		channel_name varchar DEFAULT (TG_TABLE_NAME || '_changes');
		dato record;
	BEGIN
		IF TG_OP = 'INSERT' THEN
			dato := NEW;
		END IF;
		IF TG_OP = 'DELETE' THEN
			dato := OLD;
		END IF;
		IF TG_OP = 'UPDATE' THEN
			dato := NEW;
		END IF;
		--PERFORM pg_notify(channel_name, '{"id": "' || NEW.id || '"}');
		PERFORM pg_notify(channel_name, json_build_object('table', TG_TABLE_NAME, 'id', dato.id, 'type', TG_OP)::text);
		return dato;
	END;
	$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS base_changes_trigger on base;
CREATE TRIGGER base_changes_trigger AFTER INSERT OR UPDATE OR DELETE ON base FOR EACH ROW EXECUTE PROCEDURE notify_trigger();
