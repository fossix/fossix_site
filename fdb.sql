CREATE TYPE CONTENT_CATEGORY as ENUM ('article', 'comment', 'book', 'news');
CREATE TYPE CONTENT_STATE as ENUM ('published', 'saved', 'suspended', 'rejected', 'deleted');
CREATE TYPE USER_ROLE as ENUM ('member', 'author', 'moderator', 'administrator', 'superuser');

CREATE TABLE keywords (
	id SERIAL NOT NULL,
	keyword VARCHAR(25) NOT NULL,
	description VARCHAR(128),
	PRIMARY KEY (id)
);

CREATE TABLE "users" (
	id SERIAL NOT NULL,
	username VARCHAR(32) NOT NULL,
	fullname VARCHAR(32),
	email VARCHAR(150) NOT NULL,
	date_joined TIMESTAMP WITHOUT TIME ZONE default NOW(),
	role USER_ROLE NOT NULL default 'member',
	karma INTEGER default 0,
	receive_email BOOLEAN default FALSE,
	email_alerts BOOLEAN default FALSE,
	suspended BOOLEAN default FALSE,
	PRIMARY KEY (id),
	UNIQUE (email)
);

CREATE TABLE "identity" (
	id SERIAL NOT NULL,
	url VARCHAR(512),
	user_id INTEGER NOT NULL,
	PRIMARY KEY(id),
	FOREIGN KEY(user_id) REFERENCES "users" (id)
);

CREATE TABLE content_meta (
	id SERIAL NOT NULL,
	author_id INTEGER NOT NULL,
	create_date TIMESTAMP WITHOUT TIME ZONE NOT NULL default NOW(),
	like_count INTEGER default 0,
	read_count INTEGER default 0,
	comment_count INTEGER default 0,
	category CONTENT_CATEGORY NOT NULL,
	refers_to INTEGER,
	teaser VARCHAR(200) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(author_id) REFERENCES "users" (id),
	FOREIGN KEY(refers_to) REFERENCES content_meta (id)
);

CREATE TABLE content_versions (
	id INTEGER,
	version INTEGER,
	edit_summary VARCHAR(128),
	modifier_id INTEGER NOT NULL,
	modified_date TIMESTAMP WITHOUT TIME ZONE NOT NULL default NOW(),
	title VARCHAR(128),
	content TEXT NOT NULL,
	state CONTENT_STATE NOT NULL,
	PRIMARY KEY (id, version),
	FOREIGN KEY(id) REFERENCES content_meta (id),
	FOREIGN KEY(modifier_id) REFERENCES "users" (id)
);

CREATE TABLE tags_assoc (
	content_id INTEGER NOT NULL,
	content_version INTEGER NOT NULL,
	keyword_id INTEGER,
	FOREIGN KEY(content_id, content_version) REFERENCES content_versions (id, version),
	FOREIGN KEY(keyword_id) REFERENCES keywords (id)
);

-- A view comprising of content meta and content versions, and
-- which only contains the last published version
CREATE OR REPLACE VIEW content AS
SELECT
    a.id,
    a.version,
    a.edit_summary,
    a.modifier_id,
    a.modified_date,
    a.title,
    a.content,
    a.state,
    b.teaser,
    b.author_id,
    b.create_date,
    b.like_count,
    b.read_count,
    b.comment_count,
    b.category,
    b.refers_to
FROM
    content_meta b,
    content_versions a
WHERE
    a.id=b.id
    AND
    (a.id, a.version) IN (
    SELECT
	content_versions.id,
	max(content_versions.version)
    FROM content_versions
    GROUP by content_versions.id);

CREATE OR REPLACE FUNCTION fn_on_content_update() RETURNS TRIGGER as $content_view$
    -- Inserts content to content_versions with a new version
    DECLARE
	declare new_version integer;
	updated_row content;
    BEGIN
	-- Check whether duplicate records are being added, or if its only a state change
	IF OLD.title = NEW.TITLE and OLD.content = NEW.content THEN
	    IF OLD.state = NEW.state or OLD.teaser = NEW.teaser THEN
		RAISE NOTICE 'Nothing has changed';
		RETURN OLD;
	    ELSE
		RAISE NOTICE 'Updating only the state or the teaser';
		UPDATE content_versions set state = NEW.state, teaser = NEW.teaser
		    where content_versions.id = OLD.id and content_versions.version = OLD.version;
		RETURN NEW;
	    END IF;
	END IF;

	RAISE NOTICE 'Creating new version for content';
	SELECT MAX(content_versions.version) + 1 into new_version FROM content_versions where content_versions.id=OLD.id;
	if new_version <= OLD.version THEN
	    RAISE EXCEPTION 'Cannot update old version, new version(%) already present', new_version;
	    RETURN NULL;
	END IF;

	INSERT INTO content_versions (id, version, modifier_id, modified_date, title, content, state, edit_summary)
	    VALUES (NEW.id, new_version, NEW.modifier_id, NOW(), NEW.title, NEW.content, NEW.state, NEW.edit_summary);

	EXECUTE 'select * from content where id = $1.id' into updated_row USING NEW;
	RETURN updated_row;
    END;
$content_view$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fn_on_content_insert() RETURNS trigger as
$$
    DECLARE
	create_date timestamp;
	new_id integer;
    BEGIN

	RAISE NOTICE 'Trying to insert into content_meta';
	INSERT INTO content_meta(author_id, category, refers_to, teaser)
	VALUES(NEW.modifier_id, NEW.category, NEW.refers_to, NEW.teaser)
	returning id into new_id;

	RAISE NOTICE 'Inserted. New id is %', new_id;
	INSERT INTO content_versions(id, version, modifier_id, modified_date, title, content, state)
	VALUES(new_id, 1, NEW.modifier_id, NOW(), NEW.title, NEW.content, NEW.state);

	NEW.id := new_id;
	NEW.version := 1;
	RETURN NEW;
    END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_on_content_insert
    INSTEAD OF INSERT ON content
    FOR EACH ROW EXECUTE PROCEDURE fn_on_content_insert();

CREATE TRIGGER tr_on_content_update
    INSTEAD OF UPDATE ON content
    FOR EACH ROW EXECUTE PROCEDURE fn_on_content_update();
