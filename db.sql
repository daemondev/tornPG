CREATE OR REPLACE FUNCTION table_update_notify() RETURNS trigger AS $$
DECLARE id bigint;
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        id = NEW.id;
    ELSE
        id = OLD.id;
    END IF;
    PERFORM pg_notify('table_update', json_build_object('table', TG_TABLE_NAME, 'id', id, 'type', TG_OP)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER users_notify_update ON users;
CREATE TRIGGER users_notify_update AFTER UPDATE ON users
FOR EACH ROW EXECUTE PROCEDURE table_update_notify();

DROP TRIGGER users_notify_insert ON users;
CREATE TRIGGER users_notify_insert AFTER INSERT ON users
FOR EACH ROW EXECUTE PROCEDURE table_update_notify();

DROP TRIGGER users_notify_delete ON users;
CREATE TRIGGER users_notify_delete AFTER DELETE ON users
FOR EACH ROW EXECUTE PROCEDURE table_update_notify();

#-------------------------------------------------- BEGIN [true base change feeds] - (22-06-2018 - 04:35:57) {{
CREATE OR REPLACE FUNCTION notify_trigger() RETURNS trigger AS $$
	DECLARE
		channel_name varchar DEFAULT (TG_TABLE_NAME || '_changes');
	BEGIN
		IF TG_OP = 'INSERT' THEN
			--PERFORM pg_notify(channel_name, '{"id": "' || NEW.id || '"}');
                        PERFORM pg_notify(channel_name, json_build_object('table', TG_TABLE_NAME, 'id', NEW.id, 'type', TG_OP)::text);
			RETURN NEW;
		END IF;
		IF TG_OP = 'DELETE' THEN
			PERFORM pg_notify(channel_name, '{"id": "' || OLD.id || '"}');
			RETURN OLD;
		END IF;
		IF TG_OP = 'UPDATE' THEN
			PERFORM pg_notify(channel_name, '{"id": "' || NEW.id || '"}');
			RETURN NEW;
		END IF;
	END;
	$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS base_changes_trigger on base;
CREATE TRIGGER base_changes_trigger AFTER INSERT OR UPDATE OR DELETE ON base FOR EACH ROW EXECUTE PROCEDURE notify_trigger();
#-------------------------------------------------- END   [true base change feeds] - (22-06-2018 - 04:35:57) }}
#-------------------------------------------------- BEGIN [true base change feeds version 2] - (22-06-2018 - 05:16:31) {{
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
#-------------------------------------------------- END   [true base change feeds version 2] - (22-06-2018 - 05:16:31) }}
#-------------------------------------------------- BEGIN [test trigger] - (22-06-2018 - 04:57:31) {{

CREATE OR REPLACE FUNCTION sync_marj() RETURNS TRIGGER AS $back$
DECLARE
	--argumentos
	idsyncxxx		 	character(9) 	= TG_ARGV[0];
	syncxxx			character(7) 	= TG_ARGV[1];
	tabla_evaluada		character(25) 	= TG_ARGV[2];

	--variables a usar dentro del bloque
	sync_on 			usparamweb.usanumrecibos%TYPE;
	last_idsync 		cxabonos.idsync008%TYPE = 0;
	new_idsync 			cxabonos.idsync008%TYPE = 0;
	new_sync 			cxabonos.sync008%TYPE 	= 0;
	new_codinst 		usinstituciones.codinst%TYPE;
	contador_registros 	bigint			= 0;
	query1			varchar;

BEGIN

	--Si el evento es un insert
	IF (TG_OP = 'INSERT') THEN
		--Determina si esta activa la sincronizacion en la empresadel registro a insertar
		new_codinst = NEW.codinst;
		SELECT usanumrecibos INTO sync_on FROM usparamweb where codinst = new_codinst;
		--indica que si esta activa la replicacion
		IF sync_on > 0 THEN
	--Trae el ultimo valor de IDSync para la tabla que se esta recorriendo
			query1 :=  'SELECT ' || TG_ARGV[0] || ' FROM '|| tabla_evaluada || ' WHERE codinst = ' || new_codinst || ' ORDER BY codinst, ' || TG_ARGV[0] || ' DESC LIMIT 1;';
			EXECUTE query1 INTO last_idsync;

	--Incremente en 1 el utimo valor encontrado de idsync008
			new_idsync = last_idsync + 1;

	--Actualiza los campos IDSync_ y Sync_ de la tabla que se esta afectando
        --NEW.idsync008 	= new_idsync;

        EXECUTE  'NEW.' || trim(both '' from idsyncxxx) || ' = ' || new_idsync || ';';

        --NEW.sync008 	= new_sync;
        EXECUTE 'NEW.' || trim(both '' from syncxxx) || ' = ' || new_sync || ';';

        --crea nuevo registro (si no existe) en USSyncTablas correspondiente a la tabla que aqui se esta evaluando
        --verifica si ya existe el registro correspondiente a la tabla evaluada
        SELECT count(*) INTO contador_registros FROM ussynctablas WHERE codinst = new_codinst AND tablasync = tabla_evaluada;
        --Si no existe el registro se hara un INSERT
        IF contador_registros = 0 THEN
	--nuevo registro que indica que la tabla evaluada debe ser sincronizada
	    INSERT INTO ussynctablas VALUES(new_codinst, tabla_evaluada, now());
	END IF;
	END IF;
	END IF;
	RETURN NEW;
END;
$back$ LANGUAGE plpgsql;

 DROP TRIGGER trigger_test ON cxabonos;

CREATE TRIGGER trigger_test BEFORE
 INSERT ON cxabonos
--Los primeros 2 argumentos son los campos a modificar; el tercero es el nombre de la tabla a afectar.
 FOR EACH ROW EXECUTE PROCEDURE sync_marj('idsync008','sync008','cxabonos');

#-------------------------------------------------- END   [test trigger] - (22-06-2018 - 04:57:31) }}
